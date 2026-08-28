# operators — one integral-transform framework, many named operators

Every member of this package is a **neural operator**: a learned map from a function to a
function — a whole field in, a whole field out, evaluable at any point. The neural-operator
literature defines the entire class as one shape (Kovachki, Li, Liu, Azizzadenesheli,
Bhattacharya, Stuart, Anandkumar — *Neural Operator: Learning Maps Between Function Spaces*,
JMLR 24, 2023):

    encode the input into a channel space,
    repeat:  v(x)  ←  activation( W·v(x)  +  ∫ κ(x, y) · v(y) · dν(y) ),
    read the channels out as the output function.

The named architectures differ **only** in how the kernel integral ∫κ·v·dν is parametrized and
evaluated. This package is that observation made literal: a small framework holds the shared
anatomy, and each named operator is a thin assembly of framework parts.

**This document holds the design rationale. The code does not** — by house style, docstrings and
comments in this project explain what code does and never why it exists. When you want to know
why something is shaped the way it is, it is written here or in the operator's
`IMPLEMENTATION.md`, never in the module.

---

## The four contracts

| Class | Role | Implementations |
|---|---|---|
| `Operator` | root interface: input representation → output representation on a requested discretization, with an optional conditioning vector | the `NeuralOperator` template; every encoder and readout; every wrapper |
| `Representation` | a typed function object, **carrying its quadrature** (the measure dν as data) | `GridFunction`, `PointSet`, `Coefficients` |
| `Kernel` | the learned κ plus its **fused** integration against the measures it declares support for | spectral · compact-support · low-rank · codomain-attention · dense |
| `Composition` | how layers chain — each implementation owns its topology and its backward strategy | explicit stack · weight-tied · fixed point · multi-scale |

Concrete, deliberately not abstract: `Domain` (the periodic cell), `Discretization` (a grid shape
or explicit query points), `Quadrature` (uniform-grid or counting), `Layer` (kernel + local linear
term + activation mode + residual flag), the wrappers, and the conformal calibrator.

### Why these four, and not more

The design began at seven contracts and lost three, each for a stated reason:

- **Activation** became a *mode* on `Layer` (`pointwise` or `alias_free`) rather than a class.
  Only one operator needs the alias-free form, and it needs it as a property of the layer, not as
  a polymorphic object.
- **Encoder and Readout** dissolved into `Operator`. Anything that maps a function to a function
  already satisfies the root interface; a lift, a branch, a trunk, and a nonlinear decoder are all
  just operators used in a particular position. This is also what lets the nonlinear manifold
  decoder — whose output is *not* an integral — sit in the framework without a special case.
- **A separate Integral class** was considered and rejected for the forward path. See below.

### Why the integral is not its own class

The integral has three ingredients, and they were given three different fates.

**The measure became data.** The dν of ∫κ(x,y)·v(y)·dν(y) is genuinely independent of the kernel:
it says where a function lives and how a sum over its points approximates an integral. Every
`Representation` therefore carries a `Quadrature`. A grid function integrates with uniform weights
(cell volume ÷ point count — which is exactly the ÷V_cell normalization the data pipeline already
performs); an atomic structure integrates by counting over delta functions; a coefficient vector
sums over a finite index set.

That choice pays in four independent places: zero-mean projection of a correction field,
renormalization of a predicted density to the electron count, the inner products of a low-rank
kernel, and the attention scores of the codomain-attention operator — all read weights off the
representation rather than re-deriving them.

It also **unified two kernel families**: with the measure separated, the stencil kernel and the
graph kernel are the same object — a compact-support κ(x−y) integrated against a uniform grid
(→ convolution) or against a point set (→ message passing). Five families were hiding four.

**The dense evaluation became the correctness oracle.** `framework/integral.py` holds the
definition evaluated literally: loop over sources, evaluate κ, weigh by the quadrature, sum. It is
O(sources × targets) and unusable at size, and every fused kernel must reproduce it on small
problems (8³ grids, a few atoms) before it is trusted at full size. A fast kernel that has never
been checked against the definition is not an implementation of the definition.

**The production integral stayed fused inside each kernel.** The fast algorithm exists only for a
specific *pairing* of kernel structure with measure: the Fourier path exists because the kernel is
translation-invariant *and* the measure is a uniform grid; message passing exists because the
kernel has compact support *and* the sources are points. An abstract `Integral.apply(kernel,
measure)` would either dispatch on pairs straight back to those same fused routines — pure
bookkeeping — or genuinely permit arbitrary pairs at O(N·M). The pairing *is* the architecture, so
each kernel declares which representations it accepts and owns its own `Integrate`.

### Conditioning is in the root signature

`Operator.__call__` takes `condition` alongside the input and the output discretization. Per-sample
covariates — the exchange-correlation functional, the exact-exchange fraction, strain parameters
when they modulate rather than drive — reach encoders, layers, and wrappers through it. Two of the
eight operators need it in two different ways (per-layer modulation for the correction operator,
concatenated channels for the parametric Fourier operator); without it in the root signature every
implementer rediscovers the same hole.

### Why three representations, not four

`PointMeasure` (atoms as an input structure) and `PointSamples` (values carried on query points)
were separate until DeepDFT was walked through: its probe points join the message graph and
receive messages at every layer, so the layer state is atoms and probes *together*. One `PointSet`
with optional values and a `roles` field expresses that; two classes could not.

### Representation fields

| Class | Field | Meaning |
|---|---|---|
| `GridFunction` | `values` | shape (channels, n₁, n₂, n₃) |
| | `channel_labels` | one physical name per channel — `charge_density`, `magnetization`, `electron_localization_up`, … |
| | `quadrature` | uniform grid: weight = cell volume ÷ point count |
| `PointSet` | `positions` | shape (n, 3), fractional coordinates |
| | `values` | shape (n, channels) when features ride on the points; absent for a bare structure |
| | `species` | per-point element identity when the points are atoms |
| | `roles` | message-passing asymmetries — receive-only probe points |
| `Coefficients` | `vector` | shape (k,) — sensor readings, basis coefficients, or parameters |

Channel labels are not decoration: the multiple-input and codomain-attention operators must know
which field is which, and the corpus's spin-block law makes channel sets vary from run to run
(under spin polarization every field file doubles — density and magnetization, localization up and
down, potential up and down).

### Why compositions own their topology

`Composition` is a class rather than a `for` loop because two of its four implementations carry
state the chain rule cannot see. The fixed-point scheme applies one layer until the output stops
changing, and needs a solver (Anderson acceleration) plus its own differentiation rule (phantom
gradients, or the implicit-function adjoint). The multi-scale scheme is a directed graph with skip
connections and filtered resampling between scales, not a chain, and must designate which scale
the output leaves at.

---

## The operators

| Package | Mapping, in words | Parts |
|---|---|---|
| `factorized_fourier` | charge density → electron localization field (and → local potential) | pointwise lift · spectral kernel (factorized) · explicit stack · pointwise projection |
| `alias_free_convolutional` | charge density → electron localization field | pointwise lift · compact-support kernel · alias-free activation · multi-scale |
| `deep_operator_network` | strain or lattice parameters → charge density field | sensor encoder · dense layers · basis-expansion readout |
| `multiple_input_operator_network` | (charge density, local potential) → electron localization field | two sensor encoders · low-rank product · basis expansion |
| `nonlinear_manifold_decoder` | strain or lattice parameters → charge density field | sensor encoder · dense layers · nonlinear decoder |
| `deep_dft` | atomic structure → charge density field (+ magnetization) | atom embedding · compact-support kernel over atoms ∪ probes · pointwise projection |
| `residual_correction` | cheap-functional (PBE) charge density → accurate-functional (HSE) charge density | wrappers over a backbone; conformal calibrator |
| `codomain_attention` | any subset of the fields → the missing fields | variable encoding · codomain-attention kernel over spectral kernels · pointwise projection |

Each package's own rationale, data, floors, and kill thresholds live in its `IMPLEMENTATION.md`.

Two consequences of the framework worth stating plainly. The **deep-equilibrium variant is not a
package**: it is `factorized_fourier` with `composition = FixedPoint`, which is what makes the
planned explicit → weight-tied → implicit comparison a change of one component rather than three
codebases. And **conservation attaches to task heads, not to operators**: a density output is
renormalized to the electron count, a potential output has its uniform mode pinned, and an
electron-localization output has neither — so the wrapper reads the task card.

### Zero kernel layers is legitimate

The branch–trunk operators map parameters to a field: sensor encoder → dense layers → basis
readout, with no kernel integral anywhere. The framework permits a composition holding no layers
rather than inventing a fake integral to satisfy the template.

---

## What goes where

| Directory | Contents |
|---|---|
| `framework/` | the four contracts, the `NeuralOperator` template, `Layer`, the dense reference integral, and the discretization-invariance harness |
| `kernels/spectral/` | translation-invariant kernels: full and factorized per-axis mode weights, mode truncation, physical-wavevector features from the reciprocal lattice, spectral resampling (truncation and zero-padding), and the batched three-dimensional real Fourier transform with autodiff through complex tensors |
| `kernels/compact_support/` | small-support kernels in two parametrizations — tabulated at integer offsets on a grid (convolution) and continuous in the displacement (message passing) — plus periodic neighbor finding and the alias-free activation machinery |
| `kernels/low_rank/` | separable kernels φ(x)·ψ(y) evaluated as inner products, and the dense kernel over a finite index set |
| `kernels/codomain_attention/` | attention over the channel index, with weights shared across channel tokens |
| `encoders/` | pointwise lift · sensor encoder · basis-projection encoder · atom embedding · variable encoding |
| `compositions/` | explicit stack · weight-tied · fixed point · multi-scale |
| `readouts/` | pointwise projection (bounded heads live here) · basis expansion (the trunk) · nonlinear decoder |
| `wrappers/` | residual · conditioned · conserving · the conformal calibrator |
| `data/` | corpus parsers, the derived tensor store, the split engine, the exclusion registry, the orbit map, spectral derivations, the floors, and the Stage-0 report generator |
| `metrics/` | comparison metrics — field errors, curve distances, and unit-level aggregates |
| `tasks/` | task cards — inputs, targets, loss, metrics, conservation law, covariates, split |

### Notes that the code deliberately does not carry

These are corpus and numerical facts that constrain implementations. They are recorded here
because they are reasons, and reasons do not belong in the modules.

- **Periodic images must be enumerated by cell height** (nᵢ = ⌈cutoff / heightᵢ⌉ with an exact
  distance filter). The minimum-image shortcut is wrong in the alloy campaign's strongly skewed
  monoclinic cell.
- **The alias-free activation must be fused** — upsample ×2, apply the nonlinearity, downsample
  ×2, tile-streamed with a custom gradient rule. Naive autodiff materializes the doubled grid and
  exhausts the resident card's memory. This is a correctness-of-scale requirement, not an
  optimization.
- **The atom embedding is keyed by element *and* pseudopotential title.** Twelve elements ship
  with two pseudopotential variants across campaigns, and conflating them mixes incompatible
  references.
- **The Fourier-transform substrate is an open decision** (vendor-wrapped versus written in
  house); both cost figures are carried until it is made.
- **Probe sampling is importance-weighted and de-biased**, because error mass concentrates in
  atom-centered volumes.
- **Density-of-states curves are rebuilt from eigenvalues**, never read from the pre-computed
  file; smearing is set per campaign.
- **The conformal calibrator is not an operator.** It takes a trained predictor and a calibration
  set at the symmetry-orbit level (roughly 299 exchangeable units on the strain campaign, not
  1,291 points) and returns interval-valued predictions.

### The invariance harness

Discretization invariance is the operator claim, so it is tested once at framework level rather
than privately per architecture. The axes, each with its null, follow `test-suite.md` §9.5:
resolution (train coarse via Fourier truncation — never strided subsampling, which aliases —
evaluate fine, against trigonometric upsampling of the coarse truth); supercell (the 2-atom ↔
64-atom twin shear grid, against the measured block gap between the campaigns' own truths); size
(the held-out alloy cells, scored as skill against the superposed-atomic-densities floor); and
symmetry (the 48 exact grid operations of the diamond group, reporting median equivariance error).

---

## The type discipline

Adopted 2026-08-26, before any implementation code exists, so every line that follows is written
against a modern contract rather than retrofitted to one. The package floor is **Python 3.14**
(annotations are natively lazy, so no `from __future__ import annotations` anywhere), and
**pyright in strict mode is a test gate**: `Test_The_Package_Type_Checks_Strictly` runs it over
the whole package, so a type error fails `pytest`. This is distinct from the standing "no style
checker" decision — naming, docstring, and spacing rules remain enforced by review only.

**The behavioral contracts are generic Protocols that implementations still inherit by name.**
`Operator`, `Kernel`, and `Composition` are `Protocol` classes with `@abstractmethod` members,
and `NeuralOperator` plus every assembly explicitly subclasses what it implements. Each half
buys something real: the protocol half means conformance is checked structurally by pyright
against full signatures, and the inheritance half keeps intent named in the class line and keeps
runtime safety — Protocol's metaclass derives from ABCMeta, so instantiating a class with an
unimplemented abstract member still raises.

**The generic parameters carry the anatomy.** `Operator[In, Out]` states what a map eats and
produces; `NeuralOperator[In, Hidden, Out]` types its parts as `encoder: Operator[In, Hidden]`,
`composition: Composition[Hidden]`, `readout: Operator[Hidden, Out]`, so the checker proves the
chain agrees before anything runs. Every assembly pins concrete forms in its class line —
`DeepDft(NeuralOperator[PointSet, PointSet, GridFunction | PointSet])` — which makes the class
line itself a statement of the operator's shape. Where `Out` is `GridFunction | PointSet` the
output form is correlated with the requested discretization (`GridSpec` → `GridFunction`,
`PointSpec` → `PointSet`); the `@overload` pairs that teach the checker this correlation are
written with each operator's implementation, not before. `Kernel` keeps its
`supported_representations` class attribute even though `Kernel[In, Out]` states the same thing
statically — the generics inform the checker, the attribute informs runtime dispatch.

**Aliases use the `type` statement** (`Array`, `Discretization`, `Quadrature`, `Activation`).
These are lazy `TypeAliasType` objects and cannot be used with `isinstance` — runtime checks go
against the concrete classes, or through `match`.

**`Representation` declares `domain` but not `quadrature`, on purpose.** Mutable attributes are
invariant to the checker, so a base-level `quadrature: Quadrature` would forbid the forms from
narrowing it — and the narrowing is load-bearing: `GridFunction` pins `UniformGridQuadrature`
(the spectral kernel's fast path exists only on a uniform grid) and `Coefficients` pins
`CountingQuadrature`. The measure is therefore read off concrete- or union-typed values, where
its type is exact, never off the base.

**`Array` stays `type Array = Any`** until the substrate decision (array library + autodiff) is
made. An Array protocol's member list *is* the substrate contract, so writing one now would
prejudge that decision; it becomes a real `Protocol` the day the substrate lands, its members
grown from what the framework actually uses.

Value-like dataclasses are `frozen=True, slots=True`; `Layer` is `slots=True` and generic in the
representation its kernel is endomorphic over.

---

## The inspection doctrine

A standing requirement from the project's original specification, restored to canon 2026-08-28
after an audit found it had not survived the restructure, and now **equal in rank to the house
style and the pyright gate**: everything the code computes, learns, or stores must be reachable
through a deliberate inspection API — weights, per-layer intermediate fields, kernel internals
(spectral mode weights, attention scores, message-passing edges), training curves, floors,
split maps, metrics. The convention is the one the tensor store already uses on disk: **named,
plain-word-keyed arrays** (scalars as zero-dimensional arrays), never anonymous tensors, never
state locked inside an engine object.

Why named arrays: a name is what makes a quantity findable, comparable across models, and
storable beside the corpus's own fields without translation. Why the renderer may consume only
the inspection API: if a plot needs something the API does not expose, the API is incomplete,
and that is the bug — the renderer is the completeness test. Why a part lands **in the same
commit** as its inspection surface: a surface added later is a surface shaped by what was
convenient, not by what the part knows.

- `framework/inspectable.py` holds the contract: `Inspect() -> dict[str, Array]`. `Operator`,
  `Kernel`, and `Composition` inherit it; `NeuralOperator.Inspect` aggregates its parts under
  prefixed keys (`encoder.<name>`, `composition.<name>`, `readout.<name>`) so an assembled
  operator is one flat, browsable namespace. The import tests gate the contract.
- `inspection/` is the data-layer surface: the catalog (campaigns, runs, shapes, units,
  provenance, field loading), the summary tables (orbit map, fold balance, exclusions), and
  `plots.py` — the one module allowed to import the plotting library (a seam test enforces
  it), rendering axis slices and curves from inspection arrays alone.
- The engine seam (Phase B) carries the obligation onward: parameters as named arrays at any
  time, a capture mode for declared forward intermediates, training loops emitting loss and
  metric curves as stored artifacts. Engine-native objects never cross the seam outward —
  named arrays do.
- Each operator's implementation specification must contain an "Inspection" section naming
  what that operator exposes; a specification without one does not launch its build.
- Plots and metric tables are exactly the artifacts `test-suite.md` §9.7 permits off `/Pool`;
  volumetric arrays themselves still never leave.

---

## Rules of the package

1. **One folder = one importable object named after the folder.** Spelled-out English names;
   literature names and citations live in each folder's `manifest.toml` and `IMPLEMENTATION.md`.
2. **Every fused kernel must match the dense reference integral** on small problems before it is
   trusted at size.
3. **The interface is falsifiable, not decreed:** the first build wave (the branch–trunk family
   and the correction operator) is the designated shakedown and may amend the contracts with a
   recorded reason.
4. **Backend-agnostic until dictated:** arrays are an opaque `Array` alias; the array and autodiff
   substrate is specified in the implementation documents, not here.
5. **Code style:** variables `with_underscores_between`, functions `Start_With_A_Capital`,
   datatypes `HaveNoSpaces`; docstrings and comments explain code only, never motivation, never
   inline, never longer than one line; two blank lines between every function and class. Rationale
   belongs in this file and in the `IMPLEMENTATION.md` documents.
6. Data discipline is inherited from `test-suite.md` at the repository root: spin-block-aware
   parsing, densities divided by cell volume, orbit-aware splits, the exclusion registry, and
   nothing volumetric or license-derived ever leaving `/Pool`.
7. **Everything is inspectable:** weights, outputs, and intermediates are reachable as named
   plain-word arrays through `Inspect()` on every part, and renderable through `inspection/`;
   a part lands in the same commit as its inspection surface. See "The inspection doctrine".

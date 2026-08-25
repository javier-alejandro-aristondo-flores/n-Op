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

## The four abstract classes

| Class | Role | Implementations |
|---|---|---|
| `Operator` | root interface: input representation → output representation on a requested discretization, with an optional conditioning vector | the `NeuralOperator` template; every encoder and readout; every wrapper |
| `Representation` | a typed function object, **carrying its quadrature** (the measure dν as data) | `GridFunction` (labeled channels), `PointSet` (positions + optional values / species / roles), `Coefficients` |
| `Kernel` | the learned κ plus its **fused** integration against the measures it declares support for | spectral · compact-support (stencil ≡ message passing, two parametrizations) · low-rank (the universal one) · codomain-attention · dense |
| `Composition` | how layers chain — each implementation owns its topology and its backward strategy | explicit stack · weight-tied · fixed point · multi-scale |

Concrete, deliberately not abstract: `Domain` (the periodic cell), `Discretization` (grid spec or
query points), `Quadrature` (uniform-grid / counting), `Layer` (kernel + local linear term +
activation mode ∈ {pointwise, alias-free} + residual flag), the wrappers (`Residual`,
`Conditioned`, `Conserving`), and the `ConformalCalibrator` — which is **not** an Operator: it
takes a calibration set and returns prediction intervals.

**Why the integral is not its own class in the forward path:** the fast algorithm exists only for
a specific pairing of kernel structure with measure (translation-invariant × uniform grid → FFT;
compact support × points → message passing). An abstract integral there would be bookkeeping or an
O(N·M) footgun. Instead, the measure is explicit **data** on every representation, and
`framework/integral.py` holds the dense O(N·M) reference — the correctness oracle every fused
kernel must match on small problems before any full-size run.

## The operators (thin assemblies)

| Package | Mapping, in words | Parts |
|---|---|---|
| `factorized_fourier` | charge density → electron localization field (and → local potential) | pointwise lift · spectral kernel (factorized) · explicit stack · pointwise projection |
| `alias_free_convolutional` | charge density → electron localization field | pointwise lift · compact-support kernel (tabulated) · alias-free activation · multi-scale |
| `deep_operator_network` | strain or lattice parameters → charge density field | sensor encoder · dense layers · basis-expansion readout (zero kernel layers — legitimate) |
| `multiple_input_operator_network` | (charge density, local potential) → electron localization field | two sensor encoders · low-rank product · basis expansion |
| `nonlinear_manifold_decoder` | strain or lattice parameters → charge density field | sensor encoder · dense layers · nonlinear decoder |
| `deep_dft` | atomic structure → charge density field (+ magnetization) | atom embedding · compact-support kernel over atoms ∪ receive-only probes · pointwise projection |
| `residual_correction` | cheap-functional (PBE) charge density → accurate-functional (HSE) charge density | wrappers (residual, conditioned, conserving) over a backbone; conformal calibrator |
| `codomain_attention` | any subset of the fields → the missing fields | variable encoding · codomain-attention kernel over spectral kernels · pointwise projection |

The deep-equilibrium variant is not a package: it is `factorized_fourier` with
`composition = FixedPoint`. Conservation wrappers attach to **task heads** (a density output is
renormalized to the electron count; a potential output has its uniform mode pinned), never to
operators as such — see `tasks/`.

## Rules of the package

1. **One folder = one importable object named after the folder.** Spelled-out English names;
   literature names and citations live in each folder's `manifest.toml` and docstring.
2. **Every fused kernel must match the dense reference integral** on small problems before it is
   trusted at size.
3. **The interface is falsifiable, not decreed:** the first build wave (the branch–trunk family
   and the correction operator) is the designated shakedown and may amend the abstract classes
   with a recorded reason.
4. **Backend-agnostic until dictated:** arrays are an opaque `Array` alias; the array/autodiff
   substrate is specified in the implementation documents, not here.
5. Data discipline is inherited from `test-suite.md` at the repository root: spin-block-aware
   parsing, densities divided by cell volume, orbit-aware splits, the exclusion registry, and
   nothing volumetric or license-derived ever leaving `/Pool`.

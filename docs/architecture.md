<!-- GENERATED FILE — do not edit. Source files under docs/{architecture,implementation,mvp}/. Regenerate with `python docs/meta/assemble.py`. -->

# n-Op Architecture

## Contents

- [Purpose and scope](#arch-01-purpose)
- [Library landscape](#arch-02-libraries)
- [Inputs](#arch-03-inputs)
- [The unified state](#arch-04-state)
- [Dynamics — GENERIC](#arch-05-generic)
- [The PhysicsGraph](#arch-06-physics-graph)
- [The compose-time pipeline](#arch-07-pipeline)
- [The 4-level Born–Oppenheimer hierarchy](#arch-08-bo-levels)
- [Canonical vocabularies and counts](#arch-09-vocabularies)
- [Layer-0 typeclass alphabet](#arch-10-typeclasses)
- [Residuals](#arch-11-residuals)
- [Cert obligations](#arch-12-cert)
- [Applicability classifiers](#arch-13-applicability)
- [Topology atlas](#arch-14-topology)
- [γ̂ as a Stage-4 lowering choice](#arch-15-gamma-hat)
- [The pino-bridge exports](#arch-16-pino-bridge)
- [Out of scope](#arch-17-out-of-scope)
- [Open decisions](#arch-18-open-decisions)
- [Coupling structure](#arch-19-coupling-structure)
- [Representation substrate](#arch-20-representations)
- [Multiscale state — slow and macro tiers](#arch-21-multiscale-state)


<a id="arch-01-purpose"></a>

# Purpose and scope

`n-Op` ("neural operator") trains a **physically-informed neural operator
(PINO)** that predicts the time evolution of the state of a crystalline material
under operating conditions. The downstream target is the design of **durable
high-performance ultra-wide-bandgap (UWBG) semiconductor chips for harsh
environments** — chips that must function inside, for instance, a jet turbine:
high temperature (>500 °C), thermal cycling, mechanical vibration, high field,
high current density, possibly radiation.

`/physics` does not represent the *state values* of a system; it is the way to
**instantiate a physical system** (a crystal) and define the laws through which
something else (the PINO) is evolved. It defines what a state *is*, what laws
govern its evolution, and how to evaluate whether a candidate state satisfies
those laws. Properties of the crystal may themselves have to be predicted, and
some perturbations alter what those properties do to the lattice — so the
properties are derived from state, never hard-coded.

**Minimum viable demonstration (MVP):** model **diamond**, with three target
capabilities:

1. Crystal-structure prediction (including diamond-compatible heterostructures).
2. Electron-cloud diffusion through the lattice.
3. Heat diffusion through the lattice.

The MVP discipline is **"as much closed-form / computationally feasible
expressions as possible"** and **purpose-built tools**. The MVP is
diamond-centric; the broader material scope includes anything that forms a
semiconductor with diamond: c-BN, AlN, GaN, β-Ga₂O₃, AlGaN; refractory contact
metals (W, Mo, Pt, Ti, Ni, Ta, TiN, WSi₂); substrates (SiC, Si, sapphire); gate
dielectrics (Al₂O₃, HfO₂, AlN-as-dielectric).

**The comprehensiveness of the spec is the point**, even though implementation
is diamond-first. That distinction — comprehensive spec, diamond-first build —
runs through everything below. The concrete diamond-first build target — the
minimal slice of this spec the three capabilities require — is carved out in
the `docs/mvp/` tree (`mvp-01-system` through `mvp-06-build-order`).

## What `/physics` is not

`/physics` is a pure oracle. It does not own training control flow,
sample selection beyond the per-generator `sampling-policy`, or any
loop that consumes loss values to decide what to evaluate next.
**Active-learning loops** — residual-adaptive sampling beyond the
declared policy, query-by-committee, importance reweighting against
running loss statistics — live in `/interface`, not in `/physics` and
not in `/informed-operator`. Both `/physics` and `/informed-operator`
expose the signals (granular residuals, gradients, cert evidence)
that an external active-learning policy in `/interface` consumes.

---


<a id="arch-02-libraries"></a>

# Library landscape

`n-Op` is partitioned into three sibling libraries.

- **`/physics`** — a substrate-agnostic reference oracle. It encodes the laws of
  the system: state structure, dynamics, observable definitions, residual
  definitions, and certification obligations. It does **not** hold time-varying
  state values, train neural networks, integrate trajectories, or wrap external
  DFT codes at runtime. This document is primarily about `/physics`.
- **`/informed-operator`** — the PINO itself. It consumes `/physics` and learns
  the time-evolution operator. Design notes live under
  `informed-operator/design/`.
- **`/interface`** — the user-facing surface. Out of scope for the current
  design pass.

Engineering aspects (defects, dopants, surfaces, interfaces, operating-condition
effects) live **inside** `/physics`, not in a separate library.

---


<a id="arch-03-inputs"></a>

# Inputs

Three physically orthogonal inputs fully specify "what crystal, in what
conditions":

1. **`PeriodicityStructure`** — the spatial skeleton: dimensionality
   `d ∈ {0,1,2,3}`, lattice vectors `{a_i}`, periodicity flags. The geometry of
   repetition (Bravais lattice, space group, cell vectors `h`).
2. **`SiteDecoration`** — the per-position content: which species sit at which
   Wyckoff positions; orbital basis; optional spin, charge state, occupancy, and
   a tag (`host` / `defect` / `adsorbate` / `substrate` / `impurity`). Defects,
   surfaces, adsorbates, magnetic configurations, charged systems, and alloys
   are **special cases of `SiteDecoration`**, not new top-level types.
3. **`Environment`** — external conditions: temperature, pressure (or volume),
   chemical potentials, applied electric/magnetic fields, applied stress,
   temperature gradient, carrier-injection conditions; plus the
   harsh-environment fields the slow-tier kinetics read — `radiation_flux`,
   `radiation_dose`, per-host displacement threshold `E_d`, mechanical-vibration
   spectrum, and oxygen partial pressure `p_O2` (`arch-21-multiscale-state §21.11`).

`Reference` (a bag of `(Crystal, Environment, weight)` baselines) and `Property`
(the requested observable) are **not** top-level inputs: `Reference` composes
from the three above and belongs to the cert layer; `Property` is an output
request, a parameter of `predict`/`residual`.

---


<a id="arch-04-state"></a>

# The unified state

The instantaneous state is the 7-tuple

```
x(t) = ( h,      cell vectors                       ∈ GL⁺(3, ℝ)   (3×3 real)
         R_I,    ion positions                      ∈ ℝ^{3N}
         P_I,    ion momenta                        ∈ ℝ^{3N}
         Π_h,    cell momentum (Parrinello–Rahman)  ∈ ℝ^{3×3}
         Z_I,    species labels (immutable)         discrete
         γ̂,      one-body density matrix            2×2 Pauli-spinor operator
                 (Pauli-spinor for magnetism)       on (r, r'; t)
         A )     external EM vector potential        ∈ ℝ³ field A(r,t)
```

(`A` is carried in the Weyl gauge `A₀ ≡ 0`, transverse `∇·A = 0`; the
electrostatic sector lives in the matter functionals — normative gauge/partition
paragraph in `arch-05-generic`.)

These are the **irreducible degrees of freedom of the micro tier**. Quantities
recoverable from the 7-tuple by coarse-graining **on the micro timescale and
scale** — phonon distributions `n_{q,s}`, the carrier distribution `f_n(k,r)`,
surface coverages `θ_i`, electron/lattice temperatures, current density, internal
fields — are **emergent** and stay out of the micro state: adding such a
*same-timescale* coarse-graining would create a constraint manifold tying it
back to the irreducible DOFs and reintroduce the integration pathology the
formulation avoids.

Quantities that are **not** recoverable on the micro timescale or scale are
**first-class state in their own tier**, not emergent: slow, history-dependent
**defect populations** and **composition vectors** (hours–years), and
**homogenized device-scale fields** (lattice-temperature, potential, and
carrier-density profiles on a device mesh). They couple to the micro tier only
parametrically — adiabatic driving (slow) or homogenization (macro) — so they
introduce *no* constraint manifold. See `arch-21-multiscale-state` for the
refined emergence axiom and the slow / macro tiers. (This is also the
reconciliation of the earlier "distributions are emergent" wording with
`arch-08-bo-levels`, which correctly states L4 introduces its own irreducible
distribution state.)

`x(t)` is a **type** that the PINO's predictions instantiate at each time step.
`/physics` does not hold values of `x(t)`; it defines what `x(t)` is and how to
test a candidate against the laws.

The seven slot labels above are the elements of the closed C1 vocabulary
`StateComponent`, realized as a `Universe[StateComponent]` instance per
`arch-20-representations §20.3`. Downstream files address state slots by
that universe's dense ordinal handle rather than by raw symbol.

---


<a id="arch-05-generic"></a>

# Dynamics — GENERIC

Time evolution uses the **GENERIC** form (General Equation for the
Non-Equilibrium Reversible–Irreversible Coupling):

```
dx/dt = L · δE/δx + M · δS/δx
```

- `E[x]` — total energy functional.
- `S[x]` — total entropy functional.
- `L` — Poisson operator: antisymmetric; reversible dynamics.
- `M` — friction operator: symmetric, positive semidefinite; irreversible
  dynamics.
- Degeneracy conditions: `L · δS/δx = 0` (reversible part conserves entropy) and
  `M · δE/δx = 0` (dissipative part conserves energy).

Each traditional regime of multiphysics is recovered as an **extraction** of
this single equation. Static observables are equilibrium readouts (fixed points
where `dx/dt = 0`); time-evolving observables are trajectory readouts. The
structural residual that grounds every other is the **EOM-violation residual**
`‖dx/dt − (L δE/δx + M δS/δx)‖²`. Every other residual category in
`arch-11-residuals` is either a refinement of it (per state component, per
axis) or an algebraic identity the dynamics must satisfy. `/physics` emits the
full granular residual vector; aggregation into a scalar training objective
lives in `/informed-operator`.

### Canonical functionals and operators

The two functionals decompose as:

```
E[x] = E_kin(ions)      Σ_I |P_I|²/2M_I + tr(Π_hᵀΠ_h)/2W
     + E_BO(R, h)       min_γ̂ ⟨Ĥ_electronic⟩[γ̂; R, h]
     + E_KS[γ̂]          kinetic + Hartree + exchange-correlation on γ̂
     + E_EM[A]          (1/8π) ∫ (|E|² + |B|²) dr
     + E_coupling       Σ_{c ∈ CouplingSpec, v ∈ realize(c) | v.target = Scalar} v
                        — channels declared per arch-19-coupling-structure;
                          MVP set: electron-phonon, minimal coupling,
                          ion-ion electrostatic.

S[x] = S_vib           vibrational entropy from the phonon spectrum
     + S_electronic     Fermi–Dirac entropy of the γ̂ spectrum
     + S_config         configurational entropy of coarse-grained DOFs
```

The two operators decompose as:

```
L (antisymmetric Poisson):
  · symplectic on (R, P)         canonical ion phase space
  · symplectic on (h, Π_h)       Parrinello–Rahman cell phase space
  · Liouville–von Neumann on γ̂   (1/iℏ) [Ĥ_KS, ·]
  · Maxwell on A                 Hamiltonian form of the EM field
  · semiclassical streaming      on emergent distributions
  · cross-blocks                 Σ_c Σ_{v ∈ realize(c) | v.target = AntisymmForm} v
                                 (arch-19-coupling-structure)

M (symmetric, positive semidefinite):
  · diagonal kernels             per-component dissipation (intra-block)
  · cross-kernels                Σ_c Σ_{v ∈ realize(c) | v.target = PSDSymmForm} v
                                 (arch-19-coupling-structure;
                                  MVP set: phonon-phonon and electron-phonon
                                  scattering kernels)
```

These pieces are assembled across the four levels of §6; each level contributes
the `E`, `S`, `L`, and `M` terms that act on its irreducible state.

### The nine regimes as extractions

| Regime | Extraction |
|--------|-----------|
| Structural | Critical points of `E` at `T = 0` (or `F` at `T > 0`); 1st derivatives |
| Mechanical | 2nd strain-derivatives of `F` at equilibrium |
| Thermal | Eigendecomposition of `∂²E_BO/∂u²` (phonons); BTE for phonon distribution |
| Electronic | SCF as gradient flow on `E_KS`; TDKS as Liouville on `γ̂` (pure `L`) |
| Magnetic | spin-doubled `γ̂`; spin EOM = `L` (precession) + `M` (orientation-preserving relaxation `S × (S × H_eff)`) |
| Optical | Response of `γ̂` to `A(t)` via `L`; absorption via `M` (radiative damping) |
| Transport | BTE on emergent carrier distribution: `L` (streaming) + `M` (collisions) |
| Thermodynamic | min `F` at fixed `(T, V, N)`; convex hull of `{F_φ}` |
| Chemical/surface | Master equation on configurations (`M` = rate matrix); minimum-energy-path search on `E_BO` |

The per-regime derivations of each extraction from the unified structure are in
the `docs/implementation/` tree (especially `impl-06-compositions`) and grounded
in `physics/research/group-{A,B,C}-*.md`.

### Generator structure is per-tier (degeneracy / Jacobi normalization)

The two-generator form and its degeneracy conditions `L·δS/δx = 0`, `M·δE/δx = 0`
hold **per tier / per BO level with the generators active at that tier**, not as a
single global bracket over all variables simultaneously. This is what reconciles
the written functionals with the degeneracy conditions and the `impl-10` Phase-8
"degeneracy verified" artifact. (The tiers are defined in
`arch-21-multiscale-state`; the standard GENERIC mechanical-vs-thermal split.)

- **The `γ̂`-block of `L` is the Lie–Poisson bracket** — `{A,B}(γ̂) = Tr( γ̂ ·
  [δA/δγ̂, δB/δγ̂] )`, giving `∂γ̂/∂t = −(i/ℏ)[Ĥ_KS, γ̂]` with `Ĥ_KS = δE/δγ̂`,
  written `[·, γ̂]` **not** the bare `[Ĥ_KS, ·]`. The Lie–Poisson form satisfies the
  **Jacobi identity by construction** and **degeneracy**: the Fermi–Dirac
  electronic entropy is a spectral functional of `γ̂`, so `δS_el/δγ̂` commutes with
  `γ̂` and `L_γ̂·δS_el/δγ̂ = [δS_el/δγ̂, γ̂] = 0`.
- **L2 (the mechanical surface) is single-generator (Hamiltonian) at fixed
  entropy.** The symplectic and Parrinello–Rahman blocks generate the `E_BO`-flow;
  `S_vib(R,h)` is a slow / parametric functional whose `(R,h)`-dependence drives the
  dissipative dynamics of the slow and macro tiers, not the L2 bracket. The apparent
  `L·δS_vib/δR ≠ 0` is therefore not a degeneracy violation: at L2 the active
  generator is `E` alone (an isothermal single-generator contraction); entropy
  production lives with the distribution / configurational variables.

**Jacobi status per `L`-block.** Canonical blocks (symplectic `(R,P)`, `(h,Π_h)`;
Lie–Poisson `γ̂`; Maxwell `A`) satisfy Jacobi **exactly**. Generated `AntisymmForm`
cross-blocks (`arch-19-coupling-structure`) conserve energy by antisymmetry but do
**not** automatically satisfy Jacobi (an additional condition); V1 restricts them to
the semidirect-product / Lie–Poisson class (Jacobi by construction) or flags them.
`impl-10` Phase-8 "Jacobi verified" is exact for canonical blocks and a cert-side
numerical check for generated cross-blocks — not a global symbolic proof.

**`Degeneracy` is cert-only, not a training residual.** Under the per-tier generator
structure the `Degeneracy` category (`arch-11-residuals §11.1`) is **identically zero
by construction**; it is a cert obligation — a generator-construction-bug tripwire —
not a PINO loss term (removed from the `arch-11 §11.4.1` training gate).

**`E`-functional activation is level-conditional.** `E[x]` is not a flat simultaneous
sum: at L1 the active electronic energy is `E_KS[γ̂; R₀, h₀]` — **parametric in the
frozen geometry** (it carries `∫ v_ext(R)·n + V_II(R,h)` even though `γ̂` is the
active variable); at L2, `E_BO(R,h) = min_γ̂ E_KS[γ̂; R,h]` *replaces* `E_KS` with `γ̂`
resolved (no double-count). The e-ph coupling channel contributes the linear-order
cross-term for the `L`/`M` blocks and the beyond-reference part of `E_coupling`, not
the full electron–ion energy.

**Gauge fixing and the electrostatic partition (normative).** The state's `A`
(`arch-04-state`) is carried in the **Weyl gauge** `A₀ ≡ 0` with the residual
time-independent gauge freedom fixed by transversality `∇·A = 0` — i.e. the
Coulomb-gauge radiation field. Under this split, `E_EM[A] = (1/8π)∫(|E_⊥|² + |B|²)`
counts the **transverse (radiation) sector only**; the **longitudinal /
electrostatic sector is owned by the matter functionals** — the Hartree term inside
`E_KS[γ̂]` and the ion–ion electrostatic channel — and appears nowhere in `E_EM`, so
no electrostatic energy is double-counted between the field and matter terms. This
is the standard nonrelativistic-QED partition (transverse field dynamical; Coulomb
interaction instantaneous in the matter sector). Consequences: the `EOM/A` residual
(`arch-11-residuals §11.1`) is evaluated on the transverse `A` in this gauge and is
therefore gauge-unambiguous; the minimal-coupling channel (`arch-19`) reads the
transverse `A`; gauge invariance of observables remains architectural (the
equivariance marker, registry row 104). (2026-07 gap-audit A2.)

---


<a id="arch-06-physics-graph"></a>


# The PhysicsGraph

Given the inputs (`arch-03-inputs`), the unified state (`arch-04-state`),
and the GENERIC dynamics (`arch-05-generic`), there is one data structure
that everything else in `/physics` is a view of:

> **The `PhysicsGraph`.**

A typed, hash-consed, content-addressed directed acyclic graph. It is what
the compose-time pipeline (`arch-07-pipeline`) produces, what the runtime
kernel evaluates, what the cert obligations (`arch-12-cert`) traverse, and
what `/informed-operator` trains against. Every other "thing" in
`/physics` — formulas, methods, templates, observables, residuals, bundles,
applicability classifiers, the topology atlas — is a kind of node, a
labeled subset, or a per-stage sidecar indexed by node id.

## 6.1 Anatomy of a node

```
Node =
  ( id   : ContentAddress    -- hash-cons identity (substrate identity rule
                             --   of arch-20-representations §20.1; the typed
                             --   family is Address[GraphNode])
  , type : Layer0Type        -- arch-10-typeclasses
  , kind : NodeKind          -- §6.2
  , role : OutputRole        -- §6.3
  )
```

Four fields. Two (`kind`, `role`) are named sum types whose names earn
their keep; one (`type`) reuses the existing Layer-0 typeclass alphabet;
one (`id`) is the hash-cons identity. Per-node decorations —
applicability predicates, symmetry annotations, compression plans,
adjoint strategies, cert hooks, provenance tags — live instead in
per-stage sidecars (§6.4), produced by one stage and consumed by the
next, never carried into the runtime kernel.

`NodeKind` (§6.2) is the closed C1 vocabulary that discriminates the
typed payload sum; this is the substrate's primary closed-polymorphism
mechanism (`arch-20-representations §20.6`). Sidecars (§6.4) are typed
`PersistentMap` fibers in the substrate's sense (`arch-20 §20.3`,
cluster C3). Graph identity is the closure of the multiset of output
`Address[GraphNode]` values under children-pointers
(`arch-20 §20.3` row for `PhysicsGraph`); the graph has no separate
identifier independent of its outputs.

## 6.2 The three node kinds

```
NodeKind =
  | Input(InputKind)
  | FormulaApply(formula : NamedFormula, args : List<NodeId>)
  | MethodInvoke(method  : NamedMethod,  args : List<NodeId>)

InputKind = StateSlot(StateComponent) | EnvScalar(EnvField)
```

Every operation in `/physics` is one of these three:

1. **`Input`** — a slot for a state component (`h`, `R_I`, `P_I`, `Π_h`,
   `Z_I`, `γ̂`, `A`) or an environmental scalar (`T`, `μ`, `E_field`, …).
2. **`FormulaApply`** — application of one of the 132 named formulas
   (`arch-09-vocabularies §9.3`) to typed argument nodes.
3. **`MethodInvoke`** — application of one of the 12 computational
   methods (`arch-09-vocabularies §9.1`) to typed argument nodes.

What about constructs that look like they might be additional node kinds?

- **Symmetry projection** is `MethodInvoke(symmetry-projection, …)` —
  one of the existing 12 methods. Stage 2 (`arch-07-pipeline §7.2`)
  inserts these as `MethodInvoke` nodes, not as a new species.
- **Fixed-point solves** (SCF, BTE-RTA, Liouville steady state) are
  `MethodInvoke` of the methods that have fixed-point semantics
  (`variational-minimization`, `kinetic-evolution`'s SCF/BTE-RTA modes).
  The fixed-point property is a fact about the named method, looked up
  at Stage 4 when adjoints are synthesized.
- **Observables and residuals** are *roles* (§6.3), not kinds. The same
  computation can be `Internal` in one composition and an `Observable`
  in another.

## 6.3 Output role

```
OutputRole =
  | Internal
  | Observable(bundle : 1..11)
  | ResidualLeaf(key : ResidualKey)
```

The role tells the runtime kernel which nodes are *exposed* in the
output. `Internal` nodes are evaluated but never returned. `Observable`
nodes feed the `pino-bridge` outputs (`arch-16-pino-bridge`) and are
bundle-tagged. `ResidualLeaf` nodes produce the entries of the
granularity-keyed `ResidualVector` defined in `arch-11-residuals`.

## 6.4 Per-stage sidecars

Information that stages decide *about* nodes lives in maps keyed by
`NodeId`. Each map is produced by one stage and consumed by the next;
sidecars are not part of the node's identity, are not hash-consed, and
do not survive past their consumer.

```
Stage1Sidecar.applicability  : Map<NodeId, Predicate>      -- consumed and discarded
Stage2Sidecar.symmetry       : Map<NodeId, IrrepBlock>     -- consumed by Stage 4
Stage4Sidecar.compression    : Map<NodeId, CompressionPlan>
Stage4Sidecar.adjoint        : Map<FixedPointNodeId, AdjointSolver>

CompressionPlan =
  | Dense
  | Sparse(sparsity-pattern)
  | LowRank(rank)
  | HODLR(params)
  | TT(ranks)
  | …
```

The PINO never sees these sidecars. The runtime kernel doesn't carry
them either — they are codegen inputs, consumed at Stage 4 and erased.

## 6.5 The graph *is* every other vocabulary

| Vocabulary item | Realized as |
|---|---|
| 132 formulas (`arch-09-vocabularies §9.3`) | typing rules for `FormulaApply` nodes |
| 12 methods (`arch-09-vocabularies §9.1`) | typing rules for `MethodInvoke` nodes |
| 20 templates (`arch-09-vocabularies §9.2`) | graph-construction macros that emit subgraphs |
| 11 bundles (`arch-09-vocabularies §9.4`) | the `bundle` payload of `Observable` roles |
| 19 residual categories (`arch-11-residuals`) | facet on `ResidualLeaf`, in `ContributionFacets.category` (a `CategoryTag` enum) |
| 4 BO levels (`arch-08-bo-levels`) | a layer label derivable from a node's transitive inputs; not stored |
| 4 Layer-0 typeclasses (`arch-10-typeclasses`) | the `type` field on every node |
| Applicability classifier (`arch-13-applicability`) | a Stage 1 sidecar that *prunes* the graph; not retained |
| Topology atlas (`arch-14-topology`) | a precomputed table consumed by Stage 2 |
| 10 cert obligations (`arch-12-cert`) | global traversals over the graph, indexed by `NodeKind` and `OutputRole` |
| γ̂ hybrid representation (`arch-15-gamma-hat`) | a Stage 4 `CompressionPlan` for nodes whose `type` is the density-matrix typeclass |
| `pino-bridge.Validate` (`arch-16-pino-bridge`) | the differentiated projection to `Observable` + `ResidualLeaf` outputs |
| `pino-bridge.Import` (`arch-16-pino-bridge`) | Stage 1 insertion of `Input` nodes pinned to external values, plus cert-only `ResidualLeaf` nodes |

## 6.6 Why it is *the* data structure

- **Closure.** Every closed vocabulary in `arch-09-vocabularies` is
  either a typing rule for a node kind, a labeled subset of nodes, or
  an annotation field on a node. Nothing in `/physics` lives outside
  the graph.
- **Composition.** Composing observables literally is composing
  subgraphs. The 20 templates (`arch-09-vocabularies §9.2`) are
  graph-construction macros.
- **Correctness.** The cert layer (`arch-12-cert`) is a graph traversal;
  the granularity discipline (`arch-11-residuals`) is "leaves are
  addressable"; the symmetry discipline is a Stage 2 rewrite; the
  adjoint discipline is a per-node Stage 4 strategy.
- **Performance.** The pipeline (`arch-07-pipeline`) is graph rewrites
  and lowering; performance work has no other surface.
- **Substrate-agnosticism.** The graph is language-neutral typed
  pseudocode; whether it lives in Julia Symbolics, JAX traced jaxpr,
  or MLIR is the implementation-language decision
  (`arch-18-open-decisions`). The *concept* is invariant.

> The `PhysicsGraph` is to `/physics` what the relational schema is
> to a database: every other notion is a view, a query, or an
> annotation over it. Picking a language is picking a host for
> *this* graph.


<a id="arch-07-pipeline"></a>


# The compose-time pipeline

`/physics` exposes one residual surface, evaluated through one stack, at one
fidelity. Runtime cost is bounded by compose-time specialization, symmetry
quotienting, compression, and structural sharing — every kernel emerging from
the pipeline below is fast by construction.

The pipeline runs in five stages. The first four execute **once per
`(PeriodicityStructure, SiteDecoration, Environment)` tuple**, producing
a compiled kernel. The fifth applies that kernel to dense state vectors
millions of times per training run.

## 7.1 Stage 1 — Symbolic lift

**Inputs.** The user's request — which observable bundles
(`arch-09-vocabularies §9.4`) and which residual categories
(`arch-11-residuals`) the composition must cover — plus the three
descriptors and the applicability classifiers (`arch-13-applicability`).

**Action.** Construct the initial `PhysicsGraph` (`arch-06-physics-graph`):
each requested template (`arch-09-vocabularies §9.2`) is instantiated as
a subgraph of `Input`, `FormulaApply`, and `MethodInvoke` nodes.

**Sidecar produced.** `Stage1Sidecar.applicability : Map<NodeId,
Predicate>`. The classifiers prune the graph: any subgraph whose
applicability is false for this `(Crystal, Environment)` tuple is
deleted. After Stage 1, every remaining node is meaningful for this
composition; the sidecar is discarded.

## 7.2 Stage 2 — Symmetry quotient

**Inputs.** The pruned graph from Stage 1; the topology atlas
(`arch-14-topology`) entry for this composition's space group, Wyckoff
orbits, and orbital basis.

**Action.** Two rewrites:

- **Operator block-diagonalization.** Every operator that commutes with
  the space-group action is rewritten into its irrep / isotypic
  decomposition. Schur's lemma collapses dense
  `MethodInvoke(eigendecomposition, …)` nodes into per-irrep blocks of
  size `Σ_λ d_λ m_λ`.
- **IBZ orbit collapse.** Nodes ranging over the full Brillouin zone
  are rewritten to range over the irreducible BZ with orbit weights.
  In cubic systems (the diamond MVP) this is up to **48× fewer**
  k-points.

`MethodInvoke(symmetry-projection, …)` nodes — using the existing
twelfth method — are inserted at the boundaries.

**Sidecar produced.** `Stage2Sidecar.symmetry : Map<NodeId,
IrrepBlock>`. Consumed by Stage 4 when choosing operator
representations.

## 7.2.5 Stage 2.5 — Invariant synthesis

**Inputs.** The `Stage1Sidecar.coupling-channels : List<CouplingChannel>`
declared by the composition (`arch-19-coupling-structure`); the
`CrystalSymmetryGroup` constructed in Stages 1+2.

**Action.** For each channel `c` whose `c.applicability` holds, run
the invariant generator (`arch-19-coupling-structure §19.3`) and
return the finite basis `List<InvariantTerm>` of `c.target`-shaped
symmetry-invariant terms of order `c.order` and derivative depth
`c.derivative`. Each `InvariantTerm` is the constructive dual of an
irrep-block decomposition: same machinery as §7.2, used to *build*
invariants rather than *decompose* operators.

**Sidecar produced.** `Stage2_5Sidecar.invariants : Map<CouplingChannel,
List<InvariantTerm>>`. Consumed by Stage 3 when the invariants are
lowered into `FormulaApply` nodes attached to the `E_coupling`,
`L_assembly`, and `M_assembly` aggregator methods.

## 7.3 Stage 3 — Algebraic simplification

**Action.** Three rewrites, all exact and AD-safe:

- **Hash-consing.** Pure subexpressions that appear in multiple
  residuals (a band structure, a charge density, a force field, a
  dynamical matrix) collapse to a single node referenced by all
  consumers.
- **Cross-formula CSE.** The 132 named formulas often share
  intermediate quantities; CSE pulls these out.
- **Tearing and alias elimination.** Algebraic dependencies are
  resolved at compose-time (ModelingToolkit-style); sparsity patterns
  are inferred for the next stage.

**Sidecar produced.** No new sidecar; the graph itself is the output.
The granularity discipline (`arch-11-residuals`) is preserved: every
`ResidualLeaf` retains its content-addressed `ResidualKey`; sharing of
upstream nodes does not collapse the leaves.

## 7.4 Stage 4 — Lowering and adjoint synthesis

**Action.** Three concurrent decisions:

- **Compression-plan selection.** Each operator-typed node is assigned
  a `CompressionPlan` (`arch-06-physics-graph §6.4`): `Dense`,
  `Sparse`, `LowRank(rank)`, `HODLR(params)`, `TT(ranks)`, …
  `MethodInvoke(spectral-decomposition, …)` may be lowered to
  randomized SVD or Davidson; the BTE collision kernel
  (`MethodInvoke(kinetic-evolution, …)`) may be lowered to TT-cross.
  **Each compression plan carries a per-plan error target** — the truncation
  tolerance for the `LowRank`/`HODLR`/`TT` ranks — and the rank is chosen to *meet
  that target*, not merely by structure. The target enters the per-residual error
  budget via `Quantity.combineTol` (`arch-11-residuals §11.7`).
- **Adjoint synthesis.** For every `MethodInvoke` whose method has
  fixed-point semantics, the **implicit-differentiation adjoint** is
  synthesized: gradient cost becomes one extra linear solve,
  independent of forward iteration count. This is what makes
  residuals with fixed-point semantics tractable as gradients.
- **Codegen.** The whole graph is lowered to a compiled kernel with
  one entry point (the `Input` slots), one `Map<ResidualKey, Scalar>`
  exit (the `ResidualLeaf` outputs), one `Map<ObservableRef, Value>`
  exit (the `Observable` outputs), and one `CertEvidence` exit (the
  cert traversal results).

**Sidecars produced.** `Stage4Sidecar.compression`, `Stage4Sidecar.adjoint`.
Both are codegen inputs; both are erased after codegen completes. The
runtime kernel does not carry them.

## 7.5 Stage 5 — Runtime kernel application

**Inputs.** A dense state vector `x = (h, R_I, P_I, Π_h, Z_I, γ̂, A)`
(`arch-04-state`) and an `Environment` (`arch-03-inputs`).

**Action.** Apply the compiled kernel. No symbols. No interpretation.
No path selection.

**Outputs.**

```
evaluate : (State, Environment) → ( ResidualVector  : Map<ResidualKey, Scalar>
                                  , Gradient        : Map<ResidualKey, Cotangent>
                                  , ObservableMap   : Map<ObservableRef, Value>
                                  , CertEvidence    : CertEvidence )
```

The PINO sees the graph through `ResidualKey` content hashes; it never
touches a node directly. Loss aggregation lives in `/informed-operator`,
not `/physics` — the kernel emits the granular vector, the PINO chooses
how to reduce it.

## 7.6 The compose-time / runtime boundary

| Stage | Runs | Cost | Output |
|---|---|---|---|
| 1 Symbolic lift | once per composition | seconds | pruned graph |
| 2 Symmetry quotient | once per composition | seconds | reduced graph + symmetry sidecar |
| 3 Algebraic simplification | once per composition | seconds | shared, sparse graph |
| 4 Lower + adjoint synthesis | once per composition | seconds–minutes | compiled kernel |
| 5 Runtime kernel application | per state sample | microseconds–milliseconds | residual + gradient |

A composition fingerprint (a content hash of `(Periodicity, Decoration,
Environment-structural)`) keys a kernel cache. Scalar environment
parameters that vary at training time (e.g. `T` sweeps) are passed as
runtime inputs, not baked into the kernel; only structural changes
trigger recompile.

**Runtime cost is three-class, not one** (the "µs–ms" row above is only the
per-sample core). Per the cadence policy (`impl-07-residual-factory §7.8`):

| Class | What | Cost | Cadence |
|---|---|---|---|
| per-sample core | EOM-residual evaluation (T0/T1) | µs–ms | every SGD step / RAD-subsampled |
| on-request spectral | BZ-resolved observables, full PDE residuals (T2) | 0.1–10 s | per-epoch, cached per composition |
| per-composition reference | `E_BO`/DFPT/G₀W₀ property + reference solves (T3) | seconds–minutes | once per composition / calibration-only |

The "compile seconds–minutes" figure above is the symbolic Stages 1–4; the
per-composition *reference* solves the property observables require sit in the third
class and are scheduled off the per-sample hot path by the cadence policy.


<a id="arch-08-bo-levels"></a>


# The 4-level Born–Oppenheimer hierarchy

The 7-tuple state (`arch-04-state`) partitions into four levels whose
dependencies flow strictly upward (Level 4 → 3 → 2 → 1). The hierarchy
is a partition of the **state-component space**, complementary to
(not competing with) the `PhysicsGraph` (`arch-06-physics-graph`),
which partitions the *computation*.

- **L1 — Quantum electronic substrate.** Operates on `γ̂(r,r';t)` and
  `A(r,t)` at fixed `(R, h)`. Regimes: electronic, optical, magnetic.
  Math: Kohn–Sham / TDKS / TDCSDFT, Hohenberg–Kohn, Runge–Gross,
  Liouville–von Neumann.
- **L2 — Born–Oppenheimer surface.** Operates on `(R, P, h, Π_h)` with
  immutable `Z`. Uses `E_BO(R, h) = min_γ̂ E[γ̂; R, h]`, Hellmann–Feynman
  forces, DFT stress. Regimes: structural, mechanical. Math: variational
  on `(R, h)`, strain expansion, Parrinello–Rahman dynamics.
- **L3 — Equilibrium statistics on the BO surface.** Bose–Einstein,
  Fermi–Dirac, Maxwell–Boltzmann over L1/L2 spectra. Regimes: thermal,
  thermodynamic. Math: partition functions, free energies,
  quasi-harmonic approximation, convex hull.
- **L4 — Non-equilibrium kinetics.** Distributions over phase space;
  full GENERIC `L + M`. Regimes: transport, chemical/surface. Math:
  Boltzmann transport, Kubo / Green–Kubo, master equation, Marcus
  theory, transition-state theory, minimum-energy-path search.

Each level uses lower levels as inputs but introduces its own
irreducible state. A regime is a navigational *view* across the levels
that contribute to it (thermal spans L3 statistics and L4 phonon
transport).

**L4's "own irreducible state" is the macro continuum tier.** L4 introduces
distributions over phase space, which are not recoverable from a single micro
7-tuple. That irreducible state is made concrete as the **macro continuum-field
tier** (homogenized `T_L(r), φ(r), n(r), p(r), j(r)` on a device mesh), with the
full distribution kept emergent by moment closure; in parallel, slow
history-dependent **defect populations** form a first-class **slow /
configurational tier** on an hours–years timescale. Both are specified in
`arch-21-multiscale-state`. The micro 7-tuple (`arch-04-state`) is the L1/L2 tier;
this resolves the apparent tension with `arch-04`'s emergence wording (see
`arch-04-state` and `arch-21-multiscale-state §21.0`).

In the `PhysicsGraph`, BO level is **derivable** from the transitive
inputs of a node — it is not a stored field on `Node`
(`arch-06-physics-graph §6.5`). Stage 1 ordering follows the level
discipline: L1 nodes are constructed first; L2/L3/L4 nodes depend on
their L1/L2/L3 ancestors.

## 8.1 Dressing tiers (V1 vs V2 scope)

Within L1, corrections that "dress" the bare substrate are organized
into deferred-implementation tiers. **These are V1-vs-V2 implementation
scope, not a runtime hierarchy.** Dressing is a Stage-4 codegen choice
for specific `MethodInvoke` nodes; the `dressing` tag on
`ContributionFacets` is a provenance label, not a loss-weighting axis.

```
Layer 1      Bare substrate.
Layer 1.25   One-shot closed-form dressing — pure functions, no iteration.
             V1 members: G₀W₀ quasi-particle energies; first-order
             self-consistent phonons (SCP); the linear-response
             sub-stage producing Z*, ε∞, χ∞; the LO/TO non-analytic
             correction; one-shot diagonalization; one-shot topological
             invariants.
             Cert: OneShotCert (impl-07-residual-factory §7.7).
Layer 1.75   Iterative fixed-point dressing — DEFERRED to V2 in code,
             SPECIFIED for forward compatibility. Members: self-
             consistent GW, full SCPH/SSCHA, DMFT, BSE iterative
             variants, self-consistent polaron.
             Cert: IterativeResult (impl-07-residual-factory §7.7).
             Each member gets a bespoke Stage-4 lowering, NOT a shared
             primitive.
Layer 2      Property machinery — the rest of the PhysicsGraph.
Layer 3      PINO — lives in /informed-operator.
```

The diamond MVP runs entirely against Layer 1.25, preserving the
closed-form discipline. Diamond needs only two dressings:

- **G₀W₀** — Kohn–Sham underestimates the diamond gap by ~30%; G₀W₀
  corrects to ~5.5 eV vs measured 5.47 eV.
- **First-order SCP** — marginal at 773 K, growing above 1500 K.

Comprehensiveness is preserved via the V1 specification of Layer 1.75
even though no V1 code implements it.


<a id="arch-09-vocabularies"></a>

# Canonical vocabularies and counts

Every other document references these numbers rather than restating them.

| Vocabulary | Count | Closed? |
|---|---|---|
| Top-level inputs | 3 | yes |
| State DOFs | 7-tuple | yes |
| BO hierarchy levels | 4 | yes |
| Dressing layers | 1 / 1.25 / 1.75 / 2 / 3 | yes |
| Computational methods | 12 (+3 sub-methods) | yes |
| Abstract-property templates | 20 | yes |
| Named formulas | 132 substantive (+2 rejected markers) | yes — see `formula-registry.md` |
| Observable bundles | 11 (B1–B11) | yes |
| Residual categories | 19 | yes |
| Cert obligations | 10 | yes |
| Layer-0 typeclasses | 4 | yes |
| Crystal symmetry group | first-class (space group × time-reversal × U(1) × SU(2)) | yes |
| State sub-DOF tags | `orbital, spin, sublattice, valley, strain, gauge, charge, none` | yes |
| Theory-context vocabularies | 10 (`XCFunctionalTag`, `PPType`, `PPSourceTag`, `ManyBodyLevel`, `GWScheme`, `DoubleCountingTag`, `ImpuritySolverTag`, `OrbitalBasisTag`, `RelativisticTreatment`, `SOCScheme`) — see §9.7 | yes (versioned) |

### 9.1 Twelve computational methods

Closed vocabulary; instances are programs in this vocabulary:

`state-readout`, `algebraic-combination`, `functional-differentiation`,
`variational-minimization`, `spectral-decomposition`, `spectral-aggregation`,
`linear-response`, `path-search`, `convex-optimization`, `kinetic-evolution`,
`statistical-sampling`, `symmetry-projection`.

Plus three registered sub-methods: `field-line-integral` (under `path-search`),
`interface-tunneling` (under `linear-response`), and `mesh-interpolation` (under
`kinetic-evolution`) — the compile-time band/e-ph interpolator (Fourier for gauge-free band
energies/velocities, Wannier–EPW for gauge-sensitive e-ph matrix elements, with mandatory
dipole/quadrupole polar corrections; runtime reads the interpolated grid only, C1-clean). The
closed 12-method alphabet is preserved; interpolation is a sub-method, not a new top-level method.

### 9.2 Twenty abstract-property templates

Parametric method-chain templates; concrete observables are instantiations. The
discipline: collapse "N observables with the same shape" into "1 template × N
argument tuples." Detailed signatures in `impl-03-templates`.

*General (12):*

| Template | Produces |
|---|---|
| `StateReadoutOf` | lattice parameters, bond lengths, charge density, magnetic moments |
| `AlgebraicOf` | any named-formula combination (formation energy, surface energy, hardness, …) |
| `SecondDerivativeOf` | elastic constants, force constants, polar susceptibility |
| `SpectrumOf` | band structure, phonon dispersion |
| `SpectralAggregateOf` | DOS, phonon DOS, heat capacity, vibrational/electronic free energy |
| `ResponseOfTo` | dielectric function, conductivity(ω), exchange interactions |
| `PathStationaryOf` | migration barrier, reaction pathway |
| `KineticEvolutionOf` | electronic/thermal conductivity, ionic diffusivity |
| `ClassifyOf` | space group, Wyckoff orbit, crystal-structure class |
| `ComparisonOf` | defect characterization, surface-region comparison |
| `RadiativeEmissionOf` | photoluminescence |
| `MicrokineticSteadyStateOf` | catalytic activity, turnover frequency (driven steady state) |

*Renormalization / configurational / symmetry (3):*

| Template | Produces / notes |
|---|---|
| `SelfConsistentRenormalizationOf` | fixed-point dressing; method selector ∈ {SCP, SSCHA, GW, BSE-iterated, polaron}; emits `IterativeResult` |
| `ConfigurationalFreeEnergyOf` | composition-dependent free energy; parameterizations {ClusterExpansion (discrete, T=0), Redlich–Kister (continuous, finite-T excess Gibbs), Bragg–Williams} — **distinct, not instances of each other** |
| `SymmetryAdaptedHamiltonianOf` | constructive emission of the most general symmetry-allowed `H(k)` from (space group, Wyckoff orbits, orbital basis, neighbor shells); the substrate every composed material is classified against (§14) |

*Domain interface / defect / thermo (5):*

| Template | Produces / notes |
|---|---|
| `InterfaceEquilibriumOf` | bicrystal equilibrium with charge transfer + band alignment (Schottky barrier, band offset, interface dipole) |
| `SelfConsistentChargeBalanceOf` | charge-neutral Fermi level + defect populations; closes the L3↔non-equilibrium dependency cycle via a same-pass fixed point |
| `HarmonicStiffnessHessianOf` | mass-weighted dynamical matrix with acoustic-sum-rule enforcement and Born-effective-charge correction (a specialization of `SecondDerivativeOf` whose symmetrization is a template-level concern) |
| `BiSlabGrandPotentialOf` | grand potential of a two-slab system (adhesion, interface formation energy, debonding) |
| `MassActionEquilibriumOf` | equilibrium composition of a reaction set (point-defect / gas-exchange / adsorbate equilibria) — an equilibrium readout, distinct from `MicrokineticSteadyStateOf`'s driven steady state |

Bulk-boundary correspondence is **not** a template; it is handled at the cert
layer (obligation-7, a `DiscreteStructure` morphism over the topology atlas,
§14).

### 9.3 132 named formulas

Closed registry of typed, fully-parameterized algebraic formulas, named by
behavior (person-attribution names appear only as parenthetical literature
pointers). The canonical machine-readable list is
`physics/library/formulas/registry-manifest.csv` (132 substantive rows + 2
markers for relations that are enforced architecturally and therefore *not*
residualized: force = −∇energy, and equivariance). Rows 1–87 are grounded in the
domain research (`physics/research/`); rows 88–102 are the linear-response and
topology-atlas extensions; rows 105–112 are the slow-tier degradation / radiation
extensions (`arch-21-multiscale-state §21.13`); rows 113–119 are the
polarization / piezoelectric / 2DEG package (`is-noncentrosymmetric`-gated —
see the two-predicate split in `arch-13-applicability`; GaN/AlN/AlGaN
HEMTs); rows 120–127 are the per-material accuracy package (AHC gap(T) renormalization,
the 4-phonon / iterative-LBTE κ(T) siblings, the breakdown-field T-slope, the T,P-aware
metastability hull, the Wegscheider and rotational sum-rule consistency residuals, and
alloy-disorder scattering); rows 128–134 are the 2026-07 gap-audit package
(pyroelectric n_s(T), the gate-dielectric aging trio — Poole–Frenkel, TDDB,
JMAK crystallization — the XRD / Raman experimental-structure channels, and the
radiative-recombination detailed-balance rate). Each formula carries a typed
signature, a cost tier `T0..T3`, a differentiability tag `D0..D4`, and an
applicability classifier (§13). See `formula-registry.md` for the narrative index.

### 9.4 Eleven observable bundles

Organized by physics domain (the `B1..B11` labels used in the registry):

| ID | Bundle | Primary level |
|---|---|---|
| B1 | electronic-structure | L1 |
| B2 | phonon | L2 |
| B3 | transport | L4 |
| B4 | defect-resolved | L2/L3/L4 |
| B5 | surface-resolved | L2 |
| B6 | interface-resolved | L2 |
| B7 | mechanics | L2 |
| B8 | thermodynamics | L3 |
| B9 | non-equilibrium-operating | L4 |
| B10 | static-validity | L2 |
| B11 | degradation | L4 |

(A file tree may additionally group observable *modules* by output data-shape —
BZ-resolved, energy-resolved, real-space, tensor-indexed, etc. — but the
canonical, residual-driving grouping is the eleven physics-domain bundles above.)

### 9.5 `CrystalSymmetryGroup` and `IrrepLabel`

The crystal symmetry group is a first-class entity assembled at Stage 1+2
from `PeriodicityStructure × SiteDecoration` (`arch-07-pipeline §7.2`):

```
CrystalSymmetryGroup = SpaceGroup
                     ⋊ TimeReversal             -- Z₂-graded antiunitary twist
                     ⋊ U(1)Gauge?               -- present where applicable
                     ⋊ SU(2)Spin?               -- present where applicable
```

It is the input to the Stage-2 IBZ block-diagonalization rewrite and to
the Stage-2.5 invariant generator (`arch-19-coupling-structure §19.3`).
Its identity is an `Address[GroupAtlas]` over the canonical serialization
of its finite presentation, factor descriptors, and action homomorphisms
(`arch-20-representations §20.4`). Derived outputs — character tables,
irrep decompositions, projectors, BZ stalks, Fourier caches — are
ordinary substrate fibers stored through Stage 2 / 2.5 sidecars
(`arch-20-representations §20.3`).

An **`IrrepLabel`** names one irreducible representation of a
`CrystalSymmetryGroup`. Identity is the pair

```
IrrepLabel = (group : Address[GroupAtlas-context], local-name : Symbol)
```

— the local name (`Γ₁`, `X₃⁺`, …) is unique only inside its group
context. `IrrepLabel`s are the output discriminators of Stage-2
block-diagonalization and the input discriminators selecting which
trivial-irrep basis the Stage-2.5 generator projects onto.

### 9.6 Allowed `(StateComponent, SubDofTag)` pairs

`SubDofTag` is the closed vocabulary of internal-DOF labels
(`arch-19-coupling-structure`). Not every state component carries every
sub-DOF; the allowed pairs are:

| Component | Allowed `SubDofTag`s |
|---|---|
| `γ̂` | `orbital`, `spin`, `sublattice` *(when applicable)*, `valley` *(when applicable)* |
| `A`  | `gauge` |
| `R_I` | `none` |
| `P_I` | `none` |
| `h`  | `strain` |
| `Π_h` | `strain` |
| `Z_I` | `charge` |

`StatePiece` constructors (`arch-19-coupling-structure §19.2`) reject
pairs not listed here at registration time.

### 9.7 Theory-context vocabularies

The four axes of `TheoryContext` (`arch-19-coupling-structure §19.11`) —
the global theory frame a `CouplingSpec` is interpreted in — are built
from ten closed C1 vocabularies. They are genuinely new (no existing
arch-09 vocabulary covers them; the closest neighbour, the
`{SCP, SSCHA, GW, BSE-iterated, polaron}` selector inside the §9.2
`SelfConsistentRenormalizationOf` template, is a *per-observable dressing
method*, a different axis from the composition-global theory frame). Each
is a `Universe[T]` instance with `carrier_kind = Closed` and dense `u32`
ordinals (`arch-20-representations §20.1, §20.3`); adding a member is a
versioned `schema_version` bump (`arch-20 §20.9`), not an open-registry
append, because it changes the meaning of every recorded coefficient.

| Vocabulary | Members (MVP) | Notes |
|---|---|---|
| `XCFunctionalTag` | `LDA(·) \| GGA(·) \| MetaGGA(·) \| Hybrid(flavour, exx_fraction, screening_omega?)` | exchange-correlation functional; hybrid carries float exact-exchange fraction in payload |
| `PPType` | `NormConserving \| Ultrasoft \| PAW` | pseudopotential construction kind |
| `PPSourceTag` | `PseudoDojo(version) \| SSSP(version, accuracy) \| GBRV(version) \| VASP_PAW(set) \| Custom(DOI?)` | the table version string is an open key, content-pinned by an optional `Address[PPFile]` digest |
| `ManyBodyLevel` | `KohnSham \| KohnShamPlusU(HubbardParams) \| GW(GWScheme) \| DMFT(DMFTParams) \| HybridAsManyBody(·)*` | discriminator closed; `+U`/DMFT carry sub-records with `PersistentMap` fields |
| `GWScheme` | `G0W0 \| GW0 \| scGW \| QSGW` | |
| `DoubleCountingTag` | `FLL \| AMF \| Dudarev` | DFT+U / DMFT double-counting |
| `ImpuritySolverTag` | `CTQMC \| ED \| NRG \| IPT` | DMFT impurity solver |
| `OrbitalBasisTag` | `Wannier \| PAW \| Lowdin` | the +U projection basis (also closes the gauge-choice ambiguity for downfolded channels) |
| `RelativisticTreatment` | `NonRelativistic \| ScalarRelativistic \| FullRelativistic(SOCScheme)` | |
| `SOCScheme` | `DiracPAW \| TwoComponentZORA \| SecondVariational \| PerturbativeSOC` | |

`AtomicSpecies` (the key universe of `pseudopotential_set`) is the
ordinary closed vocabulary of the elements; for V1 it is `{C, B, N, Al,
Ga, O, H}` — O and H are required by the committed content, not future
scope: β-Ga₂O₃ is an arch-01 host (and a `DefectSpecies` host,
`arch-21 §21.2.1`), the O-bearing defects (`O_N`, `V_Al–O`, `V_Ga–O_N`,
`V_O–H`) decorate III-N/oxide hosts, and the seeded slow-tier rows read H
(rows 106, 110) and O via `p_O2` (row 109). Si and the contact-metal
species enter with their waves (schema_version bump per `arch-20 §20.9`).
`* HybridAsManyBody` is reserved/deprecated for V1 — a hybrid
is always recorded as `XCFunctionalTag.Hybrid` with `ManyBodyLevel.KohnSham`,
normalized by `make-theory-context` (`arch-19 §19.8`) so the
`Address[TheoryContext]` is canonical.

These vocabularies condition the *interpretation and verification* of
coefficients, never the *enumeration* of the symmetry-invariant basis;
accordingly they touch the reference-battery, named-formula-consistency,
reference-versioning, and surrogate-validity cert obligations
(`arch-12-cert`), and none of the others.

---


<a id="arch-10-typeclasses"></a>

# Layer-0 typeclass alphabet

Every observable output is typed by three orthogonal axes plus a discrete
bucket, captured as four typeclasses. (Presented here as language-neutral typed
pseudocode; the implementation language is undecided — see §17.)

- **`Quantity` (Value axis).** Units, equality-with-tolerance, behavior under
  change of units/basis. Every numeric output is a `Quantity`. Carries
  `unitsOf`, `approxEq(tol)`, `rescale`, and `combineTol` (how tolerances
  compose under arithmetic — e.g. `κ = κ_el + κ_ph`; associative, commutative,
  monotone; per-instance choice of max-absolute or root-sum-square).
- **`Sampleable` (Shape axis).** Whether the output is a function on a domain,
  with `evaluate : f → Domain → Codomain` total on its claimed domain. Optional
  à-la-carte capabilities:
  - `Integrable` — `integrate(measure)`; linear, change-of-variables.
  - `Differentiable` — `derivative : f → Domain → Maybe Tangent`, total on
    `Domain \ exceptionSet` (phase transitions, band crossings,
    charge-transition levels live in the exception set); carries a `chart` tag so
    derivatives only compare across instances with matching charts.
  - `Restrictable` — `restrict(subdomain)`.
- **`HasAnalyticStructure` (Constraint axis).** Global analytic laws as
  witnesses — causality/Kramers–Kronig, hermiticity, convexity, Onsager
  involution, sum rules. A `Witness` is a list of `(Local | Global)`-tagged
  witnesses (one output can carry several simultaneously); `certifyAnalytic`
  returns the witnesses or a typed failure.
- **`DiscreteStructure` (Combinatorial axis).** Integer invariants,
  classification groups, holonomy spectra, polyhedra, convex hulls — objects in a
  discrete category with `identity`, `compose`, and `isoEq`. Not `Quantity` (no
  units), not `Sampleable` (no domain). The topology-atlas outputs live here.

The old names `Scalar / FieldOnGrid / Tensor / Response` survive only as
aliases over common parameterizations (`Response = Sampleable + Integrable +
Differentiable + HasAnalyticStructure(KramersKronig)` over a frequency domain,
etc.). Cert obligations (§12) map onto these axes mechanically.

---


<a id="arch-11-residuals"></a>


# Residuals

Residuals are the physics-informed loss terms `/informed-operator`
trains against. In the `PhysicsGraph` (`arch-06-physics-graph`) they
are realized as nodes with `OutputRole = ResidualLeaf(key)`. The
emission discipline is **granular**: every independent component is
its own scalar with its own content-addressed key, and `/physics`
never preaggregates.

## 11.1 The nineteen categories (a taxonomy facet)

Residuals fall into nineteen categories (the seventeen primary categories below,
plus the two cross-tier EOM-violation siblings of `arch-21-multiscale-state`),
identified by symbolic tags rather than ordinals. The categories are a *facet* on
each contribution, not a granularity floor or a unit of weighting.

**EOM-violation — 9 categories.** Seven per micro state-component DOF
(`arch-04-state`), plus two cross-tier siblings (slow and macro,
`arch-21-multiscale-state`):

  1. `EOM/γ̂` — `‖∂γ̂/∂t − …‖²` on the density-matrix DOF.
  2. `EOM/A` — same form on the EM gauge potential.
  3. `EOM/R` — same form on ion positions.
  4. `EOM/P` — same form on ion momenta.
  5. `EOM/h` — same form on the cell metric.
  6. `EOM/Π_h` — same form on the cell-metric conjugate.
  7. `EOM/Z` — same form on atomic-number labels (only non-trivial
     under chemistry-active dynamics; otherwise structurally null).

  Aggregate form: `‖dx_i/dt − (L δE/δx_i + M δS/δx_i)‖²` for each
  state-component `x_i`. The axis structure of each EOM residual
  (the set of axis tuples emitted per `arch-11-residuals §11.2`) is
  the union of axes contributed by `(a)` the diagonal kinematic /
  symplectic operators and `(b)` the `InvariantTerm`s of every active
  `CouplingChannel` whose `pieces` include component `x_i`
  (`arch-19-coupling-structure`). Each generated invariant adds its
  own axis tuple; there is no per-coupling residual category.

  Two **cross-tier** EOM-violation siblings extend the family
  (`arch-21-multiscale-state`), sharing the same
  `‖∂_t x − (L δE/δx + M δS/δx)‖²` shape with `x` ranging over a non-micro tier:

  - `EOM/DefectPopulation` — slow-tier defect-population kinetics,
    `‖d[D]^q/dt − (G − [D]^q·k_ann)‖²` (`arch-21 §21.4`).
  - `EOM/Continuum` — macro-tier continuum-field balance,
    `‖∂_t field − RHS(fields; homogenized coeffs)‖²`, generalizing the
    device-PDE residual (`arch-21 §21.9`).

**Structural axes of GENERIC — 3 categories.**

  8. `Degeneracy` — `‖L δS/δx‖² + ‖M δE/δx‖²`. **Cert-only**: identically
     zero by construction under the per-tier GENERIC generators
     (`arch-05-generic`), so it is a generator-construction-bug tripwire, not a
     PINO training-loss term.
  9. `Conservation` — energy, particle-number / charge, momentum /
     crystal-momentum, spin. Particle number includes the **static γ̂-trace
     admissibility** `‖Tr γ̂ − N_e‖²` (N_e fixed by `SiteDecoration`) checked per
     snapshot — a candidate state must carry the right electron count, not merely
     conserve whatever count it has along a trajectory. Structural on the state;
     no new formula row.
 10. `Positivity` — `M ⪰ 0`, `f ∈ [0,1]`, `ρ ≥ 0`, `ω² ≥ 0`,
     `σ ⪰ 0`, `|S_i| = 1`. `ω² ≥ 0` is **applicability-gated** to phases claimed
     dynamically stable, so it does not penalize legitimate saddle / transition
     configurations the trajectories must traverse (e.g. along an NEB path). Also the
     electron-temperature bound `T_e ≥ T_L` (reads registry row 72) and the
     avalanche breakdown-integral guard `max(0, ∫α dx − 1)²` (reads registry row 75) —
     both reference existing rows, no new formula row.
     Also **γ̂ admissibility** (ensemble N-representability, the state-level
     analogue of `f ∈ [0,1]`): `γ̂† = γ̂` and `0 ⪯ γ̂ ⪯ 1`, evaluated as per-k-block
     spectral bounds on the `(Reciprocal, BlockDiag)` encoding (`arch-15-gamma-hat`
     §15.5 — extreme eigenvalues per block are cheap); the T=0 idempotency
     `‖γ̂² − γ̂‖²` is applicability-gated to claimed-zero-temperature states exactly
     as `ω² ≥ 0` is gated to claimed-stable phases. A candidate γ̂ outside these
     bounds can zero every EOM residual while being unphysical — these are the
     admissibility gates that make the oracle sound as a *verifier* of the state
     itself, not only of its dynamics (2026-07 gap-audit A1). Structural on the
     state; no new formula row.

**Algebraic identities — 5 categories** (the former umbrella, now
split by analytic kind):

 11. `Algebraic/Kramers-Kronig` — causality dispersion identities on
     response functions.
 12. `Algebraic/SumRules` — f-sum `(2/π)∫ω·Im ε dω = ω_p²`; acoustic
     sum `Σ_J Σ_R Φ_{IαJβ}(R) = 0`; the **rotational** sum rule
     `(Σ_J [Φ R_γ − Φ R_β])²` (Born–Huang / Gazis–Wallis, registry row 126);
     oscillator strengths.
 13. `Algebraic/BalanceLaws` — detailed balance; Einstein relation
     between mobility and diffusion; the **Wegscheider reaction-cycle**
     closure `(Σ_r σ_r ln K_r)²` (registry row 125).
 14. `Algebraic/Symmetries` — Onsager reciprocity; Maxwell relations;
     space-group equivariance of response tensors.
 15. `Algebraic/MethodEquivalence` — different formulas claiming the
     same observable agree on their shared domain (BTE-σ ≡ Kubo-σ in
     linear response, etc.). Two sub-kinds (an annotation, not a new tag): an
     **equivalence pair** binds two formulas that share an *agreement theorem* and
     trips on any disagreement beyond `δ_sym`/`τ_adj` (BTE-σ ≡ Kubo-σ); a
     **consistency pair** binds a cheap model to a microscopic reference that have
     **no** agreement theorem — Callaway/Slack κ vs iterative-LBTE κ, cheap-Chynoweth
     vs BTE/MC α — and trips only on *excess beyond a declared model-gap tolerance*
     `τ_method` (`arch-12 §12.0.2`), so a legitimate model gap is not scored as a bug.
     The κ 4-phonon / iterative-LBTE siblings (registry rows 121–122) bind to row 25
     as a **consistency pair**.

**Constraint violations (by input-domain type) — 2 categories.**
Disjoint by the *type* of input the constraint reads:

 16. `Static/Snapshot` — depends only on the geometric + electronic
     snapshot, no environment field. Valence-bond-sum charge balance;
     Born stability; dynamical stability; space-group equivariance of
     the snapshot.
 17. `Static/Thermodynamic` — depends on snapshot + environment
     (temperature, chemical potentials, partial pressures).
     Hull-distance — including the **T,P-aware metastability** form
     `max(0, ΔG_form(T,P) − ΔG_hull(T,P) − δ_meta)²` with a metastability band so
     diamond (+25 meV/atom at T=0) reads `R=0` (registry row 124) —
     formation-energy-from-references, solubility,
     mass-action, carbide-formation. Also the three slow-tier
     thermodynamic-consistency identities — Gibbs adsorption `dγ/dμ = −Γ`,
     charge–Fermi Maxwell `dE_form/dE_F = q`, and the Clausius–Clapeyron analog
     `d ln[D]/d(1/T)` vs `S_form` (`arch-21-multiscale-state §21.12`).

Categories 16 and 17 stay disjoint because they consume
type-distinct inputs (snapshot vs snapshot+environment), and the
PINO curriculum schedules them differently for that reason.

The `CategoryTag` enum is the closed set of **19** symbols: the 17 above plus the
two cross-tier EOM-violation siblings `EOM/DefectPopulation` and `EOM/Continuum`
(`arch-21-multiscale-state §21.4, §21.9`). It appears in
`ContributionFacets.category` and nowhere else carries semantic weight.

## 11.2 The atomic unit: residual contribution

A **residual contribution** is the smallest scalar (or scalar-valued
field-norm) the loss aggregator can multiply by an independent weight.
Every contribution is a `ResidualLeaf` node carrying a content-addressed
key:

```
ResidualKey = (producer : Producer, axes : Tuple<AxisLabel>)
Producer    = Formula(NamedFormula) | Method(NamedMethod)

ContributionFacets =                         -- sidecar; not part of identity
  ( category : CategoryTag                   -- one of 19 symbolic tags (§11.1)
  , bundle   : BundleId                      -- B1..B11
  , dressing : bare | dressed(scheme)        -- provenance label
  )
```

Two evaluations with identical inputs produce the identical key. The
PINO holds `Map<ResidualKey, Weight>` independent of `/physics`'s
internals; weights persist across compose-time recompiles. Facets are
exposed via a parallel `Map<ResidualKey, ContributionFacets>` that the
PINO consults for category- or bundle-level aggregation.

`ResidualKey` is a typed `ContentAddress` instance in the substrate's
sense (`arch-20-representations §20.3` row for cluster C5);
`CategoryTag`, `BundleId`, and `AxisLabel` are `Universe[T]` instances
(cluster C1); `ContributionFacets` is the value type of a typed sidecar
fiber and never participates in `ResidualKey` identity (cluster C3).

## 11.3 Examples of what becomes a separately-weightable contribution

Not "the algebraic-identities category" but each of:

- One Kramers–Kronig identity on one component of `ε(ω)` at one
  frequency band.
- The acoustic sum rule per Cartesian pair `(α, β)` and per shell `R`.
- The conservation residual for one charge species in one slab
  subdomain.
- The Born stability eigenvalue penalty per failing eigenmode of `C_ij`.
- The EOM violation per state-component
  `i ∈ {h, R_I, P_I, Π_h, γ̂, A}`, optionally per spatial / momentum bin.

Not "EOM violation"; not "Born stability"; not "conservation."

## 11.4 Output type

The runtime kernel emits a vector, not a scalar:

```
evaluate : (State, Environment) → ( residuals : Map<ResidualKey, Scalar>
                                  , gradient  : Map<ResidualKey, Cotangent>
                                  , …  )
```

Aggregation (per-category sums, GradNorm balancing, residual-adaptive
sampling, per-bundle weight schedules, curriculum gating) lives in
`/informed-operator`, not in `/physics`. `/physics` is an oracle that
reports per-component values; the consumer chooses how to reduce them.

### 11.4.1 Curriculum gating defaults

`/physics` specifies the **default** curriculum schedule that
`/informed-operator` uses to gate which residual categories
(`CategoryTag`, §11.1) participate at each training fraction.
`/informed-operator` may override.

```
fraction ∈ [0, 1] of total training budget
[0.00, 0.10)  Warmup    — Conservation + Positivity only
[0.10, 0.60)  Refine    — add all EOM/* + all Algebraic/* except MethodEquivalence
[0.60, 0.90)  Polish    — add Algebraic/MethodEquivalence + Static/Snapshot + Static/Thermodynamic
                          (Degeneracy is cert-only, §11.1 item 8 — never a training residual)
[0.90, 1.00]  Cooldown  — no new categories; weights frozen for final evaluation
```

Rationale: Warmup keeps the network on hard physical constraints
before the EOM surface (which dominates the loss landscape) turns on;
Refine carries the bulk of dynamics learning; Polish tightens the
cross-formula equivalence and thermodynamic-consistency residuals once
the dynamical residuals are quiet; Cooldown freezes the schedule for
deterministic final-cert evaluation.

The schedule is a normative default, not a contract: `/informed-operator`
declares its own `Map<CategoryTag, GateSchedule>` if it overrides any
fraction or category.

## 11.5 Granularity composes with hash-consing

Two contributions sharing 99% of their DAG ancestry — for example, all
Kramers–Kronig identities sharing the dielectric-function computation
— is the common case. Stage 3 (`arch-07-pipeline §7.3`) hash-consing
already gives the upstream sharing for free. The granularity directive
adds only that the *leaves* of the DAG — the per-contribution scalars
— are individually addressable. The single compose-time pipeline
produces a kernel that emits the full `Map<ResidualKey, Scalar>` in
one forward pass with no extra cost over emitting a single aggregated
scalar; reverse-mode produces the per-key gradient by structural
projection of the same pullback.

## 11.6 Closure (vocabulary count)

Residual contributions are **unbounded** (they unfold along the
generator's `axes`), but residual *generators* (`impl-07-residual-factory
§7.1`) remain countable: one per `(formula, applicability cell)` plus
the cert-only and ground-truth-bridge subtypes. The closed-vocabulary
discipline (`arch-09-vocabularies`) holds at the generator level.

## 11.7 Per-residual error composition (the accuracy ledger)

Every `ResidualGenerator` (`impl-07-residual-factory §7.1`) carries a
`characteristic-scale : σ` — the target accuracy of its observable, seeded from the
**per-observable accuracy ledger** (`docs/accuracy-ledger.md`, restored from the
research catalog). `σ` is a *declared scale*, not a fitted weight: it is the
error-model input that `arch-10-typeclasses` `Quantity.combineTol` composes along the
DAG (per-instance max-abs or RSS) into a per-`ResidualKey` error budget. The budget
sums the contributing terms — input `σ`, **model-form error** (RTA/3-ph, compact
models, QHA), **Stage-4 compression truncation** (the per-plan error target,
`arch-07-pipeline §7.4`), **dressing staleness** (frozen Layer-1.25 one-shots), and
**coefficient-provenance `σ`** (`arch-19-coupling-structure §19.8`) — so "is this
closed-form choice accurate enough?" is answerable *by the system*, not only by
external judgment.

The MVP headline design-grade targets (gap ±0.15 eV post-G₀W₀, C_ij ±5%, κ(300 K)
±20%, E_form ±0.2 eV, μ factor-2) and the full 52-observable ledger live in
`docs/accuracy-ledger.md`; the reference battery (cert obligation 4, `arch-12 §12.1`)
checks them at the MVP anchors. Every numeric tolerance named across `/physics`
(`τ_adj`, `δ_sym`, `δ_PSD`, `τ_SCF,*`, `τ_method`, `δ_surrogate`) is valued once in the
**tolerance ledger** (`arch-12 §12.0.2`).


<a id="arch-12-cert"></a>

# Cert obligations

Cert is a first-class deliverable: schema, deterministic text renderer, freeze
fixture + tamper tripwire, and a high-precision oracle cross-check. The
certificate emitted for any prediction is an inert s-expression carrying scalar
verdicts plus numeric witnesses for failures.

1. Symmetry equivariance.
2. Bounds (physical positivity).
3. Analytic limits (where closed-form answers exist).
4. Reference battery (frozen reference data on a held-out crystal battery).
5. Conservation laws.
6. GENERIC degeneracy + named-formula consistency across equivalent
   compositions.
7. Bulk-boundary correspondence (a `DiscreteStructure` morphism: for a bulk
   classified as `X_BS = k`, the slab must carry boundary states with
   multiplicities given by a lookup table indexed on
   `(k_generator, boundary_orientation)`).
8. Reference-battery-versioned (versioning discipline on obligation 4; reads
   `physics/library/cert/reference-data/`, looks up rows by
   `(Property, Material, Environment)`, trips at `|predicted − reference|/σ > 3`
   with the row's provenance).
9. Surrogate-net validity (for D4 surrogate formulas).
10. Adjoint-existence at registration (the gate of §11).

Each obligation maps onto a Layer-0 axis (§10), making the cert checkers generic
functions over the typeclasses.

The cert evidence produced by the ten obligations is one
`MerkleDAG[EvidenceOps, EvidencePayload]` per composition, in the
substrate's sense (`arch-20-representations §20.2`, §20.3 row for
cluster C4). Each obligation's output is a typed leaf attached as an
`EvidenceOps.attestation` node; aggregation across obligations is the
semilattice meet of `EvidenceOps`, so a composition's overall verdict
is `Failed` if any obligation leaf is `Failed`, `Pending` if any leaf
is `Pending` and none is `Failed`, and `Passed` otherwise. The
attestation DAG's root `Address` is the cert artifact `/informed-
operator` consumes.

## 12.0.1 Coupling-derived simplifications (obligations 1, 2, 5)

When a formula node originates from the invariant generator
(`arch-19-coupling-structure §19.3`), obligations 1, 2, and 5 collapse to
projection-residual checks (tolerances named in §12.0.2):

- **Obligation 1 (symmetry equivariance).** Invariants are
  trivial-irrep basis vectors by construction. Cert verifies the
  emitted `InvariantTerm.symbolic-form` lies in the claimed subspace:
  `||v − π_trivial v|| / ||v|| < δ_sym` on a sampled evaluation. Failure
  is a generator bug, not a physics bug.
- **Obligation 5 (antisymmetry of `L` — a conservation property).**
  `AntisymmForm` invariants project onto the antisymmetric component; cert
  verifies the emitted form equals its projection within `δ_sym`. (Antisymmetry
  conserves energy; Jacobi status per `arch-05-generic`.)
- **Obligation 2 (PSD of `M` — a bounds/positivity property).** For
  `PSDSymmForm` targets the projector is the **congruence-action Reynolds
  operator** (averaging `ρ(g)ᵀ M ρ(g)`) — only the congruence action preserves
  positive-semidefiniteness; a bare orthogonal subspace projection does not. The
  PSD condition is stated on the **assembled dissipative super-block per
  mechanism** (the diagonal kernels together with their off-diagonal
  cross-kernels), via a Schur-complement / Gram condition — **not** per
  off-diagonal kernel in isolation (an off-diagonal cross-kernel alone is not
  sign-definite). Cert checks `λ_min(M_block) ≥ −δ_PSD` on that assembled
  super-block. PSD *existence* is the structural theorem of `arch-19 §19.12`;
  this is its runtime guard.

These checks are `O(1)`–`O(block)` per invariant and run alongside the generator
at Stage 2.5.

## 12.0.2 Tolerance ledger

Canonical names and default values for every tolerance / error bound in `/physics`.
The symbol `δ` / `τ` denotes a *tolerance* throughout; `ε` is reserved for
permittivity in the physics formulas (this ends the `ε` collision noted in
`arch-19`). These values are the inputs `arch-10-typeclasses` `Quantity.combineTol`
composes into the per-observable error budget (`arch-11-residuals §11.7`).

| Name | Meaning | Default |
|---|---|---|
| `δ_sym` | symmetry / antisymmetry projection residual (obligations 1, 5) | `1e-6` relative |
| `δ_PSD` | assembled-super-block negative-eigenvalue guard (obligation 2) | `1e-9` absolute |
| `τ_SCF,strict` | SCF / minimization gradient-norm convergence (reference / compile side) | `1e-8` Ha |
| `τ_SCF,train` | SCF convergence on the runtime / training path (looser) | `1e-4` Ha |
| `τ_L3L4` | L3↔non-equilibrium same-pass fixed-point residual (≤ 5 iters) | `1e-4` |
| `τ_method` | `Algebraic/MethodEquivalence` relative-error envelope (obligation 6) | `10–20%`, declared per formula pair |
| `τ_adj` | registration adjoint vJp-vs-JvP gate (`impl-07-residual-factory §7.5`) | `1e-4` relative |
| `δ_surrogate` | D4 surrogate / relaxation validity (obligation 9), measured on a dev set | per-formula |

## 12.0.3 Composition-validity refusals (machine-checkable, not reviewer caveats)

Three compose-time refusals are decided by tag/field comparison on the active `CouplingSpec` +
`ProvenanceLedger`, emitted as obligation leaves rather than left to documentation. Each is a
`Failed` verdict with a witness (the offending coefficient / row pair).

- **Unprovenanced-coefficient refusal** (obligation 4/9 family, `arch-19-coupling-structure §19.8`).
  Any active channel carrying a coefficient with no `ProvenanceLedger` entry refuses the
  composition — an unprovenanced coefficient is a silent accuracy hole.
- **AHC `slope-kind` double-count refusal** (obligation 6, named-formula consistency).
  `ahc-gap-renormalization` (row 120) slopes carry `slope-kind ∈ {isochoric, total}`
  (`arch-19 §19.8`). A composition in which a `total`-tagged AHC slope and row 63's
  thermal-expansion (`Ξ·strain`) T-path are both active on the same observable is refused — the
  two paths would double-count the lattice-expansion part of `dE_g/dT`. Witness: the
  `(row 120 coeff, row 63 instance, observable)` triple. An `isochoric`-tagged slope passes.
- **Learned-correction-without-anchor refusal** (obligation 9, surrogate validity). A PINO-learned
  correction coefficient (V1: the EDF-tail `Δα`, `arch-19 §19.8`) is admissible only if external
  anchor data back its declared validity domain; with no anchors it ships as identity and any query
  inside the unanchored high-E×high-T corner trips obligation 9 with a domain witness (the
  ">500 °C breakdown = cert-refused, not met" stance).
- **Polarization-convention pairing refusal** (obligation 6, named-formula consistency;
  `arch-19 §19.8`). Each spontaneous-polarization (`P_sp`, row 113) and piezoelectric (`e₃₁`,
  rows 114/117) coefficient carries `polarization-reference ∈ {ZB-proper, H-improper}`. A
  composition whose active `P_sp` and `e₃₁` carry **mismatched** tags is refused — mixing a
  ZB-reference `P_sp` with an improper `e₃₁` (or vice versa) breaks the Dreyer accidental
  cancellation (PRX 6 021038 (2016)) and corrupts the 2DEG `n_s` (improper `e₃₁ ≈ 3.4× proper`).
  Witness: the `(P_sp coeff, e₃₁ coeff)` tag pair. The ±5%-ΔP target is additionally scoped
  `is-AlGaN-GaN`; a high-In InGaN/GaN composition (where the cancellation is incomplete) is
  σ-degraded or refused. The curated III-N coefficients are `ZB-proper` (`docs/accuracy-ledger.md`).

## 12.1 `SqliteReferenceCache` — backend for obligations 4 + 8

The reference battery (obligation 4) and its versioning discipline
(obligation 8) read from a single content-addressed store, the
**`SqliteReferenceCache`**: a process-local SQLite file at
`physics/library/cert/reference-data/cache.sqlite`, opened in WAL mode
for concurrent reads from the training process and the cert evaluator.

```
table entries (
  key             TEXT  PRIMARY KEY,   -- ContentAddress over (observable, value, sigma, provenance, coverage-mask)
  observable      TEXT  NOT NULL,      -- ObservableRef serialization
  value           BLOB  NOT NULL,      -- typed payload (scalar, tensor, curve)
  sigma           REAL  NOT NULL,
  provenance      TEXT  NOT NULL,      -- JSON: { source, doi?, fetched-at, version }
  coverage_mask   BLOB  NOT NULL,      -- RoaringCoverageMask serialization (arch-16-pino-bridge §16.2.1)
  schema_version  INT   NOT NULL
)
```

- **Key construction.** `ContentAddress` over the canonical serialization
  of `(observable, value, sigma, provenance, coverage_mask)` (SHA-256
  backed, per `arch-20-representations §20.4`). Identical payloads
  collapse to one row; tampered payloads change the key and trip the
  obligation-8 freeze comparison.
- **Schema versioning.** `schema_version` bumps on any column add;
  readers refuse rows whose `schema_version` exceeds the linked-in
  schema, forcing an explicit migration step rather than silent drift.
- **Write discipline.** Write-once per key; updates produce a new row
  with a new key. Deletes are disallowed in the cert path; obsolete
  rows are tombstoned via `provenance.version`.
- **Why SQLite.** Single-file, ACID, no daemon, ubiquitous; WAL mode
  serves the read-heavy cert workload; scales from the MVP's
  ~10-row diamond battery to the long-tail target of ~10⁴ rows
  without infrastructure changes.

The cache is the only persistent component of `/physics`; everything
else is recomputed from the graph.

---


<a id="arch-13-applicability"></a>

# Applicability classifiers

Every property, observable, and residual carries a typed predicate
`applicability : (Crystal, Environment) → Bool`. The PINO loss masks out
non-applicable properties per-sample, so the model is neither falsely supervised
(e.g. predicting a band gap for a metal) nor penalized for an undefined quantity.
This is what makes the architecture **compositional across crystal types**: the
same interface accepts diamond, GaN, AlN, c-BN, refractory metals — each
property's classifier decides whether it is a meaningful question for that
crystal (band gap iff insulator/semiconductor; Schottky barrier iff
metal-semiconductor interface; polar-optical scattering iff polar — false for
diamond; carbide-formation iff the interface includes a carbide former — false
for Pt/diamond, true for Ti/diamond).

**Two distinct "polar" predicates (normative; 2026-07 gap-audit / Wave-2).**
"Polar" conflates two independent crystal properties and the registry gates on
each separately:

- `is-polar-material` — nonzero Born effective charges / LO–TO splitting.
  Gates the **Fröhlich / polar-optical-phonon** paths (the `LongRangeStatic`
  e-ph channels, POP-limited v_sat, LST-derived ε_r). A property of the
  *bonds*, not the point group.
- `is-noncentrosymmetric` — piezoelectric crystal classes (no inversion
  center). Gates the **polarization package**: P_sp, piezoelectric tensors,
  2DEG n_s, pyroelectricity (rows 113–119, 128).

The two coincide on the corpus anchors that made the conflation invisible —
diamond (both false), wurtzite III-N (both true) — and **split on β-Ga₂O₃
(C2/m: centrosymmetric, so no P_sp/piezo/pyro — yet strongly polar-phonon,
with a massive multi-mode Fröhlich interaction that is its dominant mobility
limiter).** Gating rows 113–119/128 on the Fröhlich-sense predicate would
wrongly activate spontaneous polarization for β-Ga₂O₃; gating Fröhlich on the
piezo-sense predicate would wrongly *deactivate* its dominant scattering
channel.

V1 commitment: every registry entry gets an explicit `applicability` field;
always-true stubs are acceptable for V1.0 and refined incrementally. Open
questions (deferred): soft `[0,1]` classifiers, and classifier composition under
perturbation.

**Swept-Environment validity windows (committed, V1).** A predicate or formula
*validity window* that depends on a **runtime-swept** `Environment` scalar — temperature
(QHA window, the regime windows of `arch-21-multiscale-state §21.7.1`, the `ω²≥0`
claimed-stable gate, the Chynoweth field domain, the 4-phonon `T ≳ 0.4 Θ_D` window) — is
**re-evaluated per training sample** in the PINO loss mask, *not* once against the
composition's nominal `(Crystal, Environment)`. The per-sample mask path already exists
(`arch-16-pino-bridge`); compose-time `Stage-2.5` structure decisions are frozen, but the
*mask* over them is a runtime read of the swept scalar. To make this checkable, each emitted
kernel is **tagged with the `Environment` box** (the scalar ranges) on which its Stage-2.5
structure is valid; a sample whose swept scalar leaves that box is masked out (and, for a
cert query, trips the relevant obligation) rather than silently scored against a stale kernel.
This is the resolution of the former "current-vs-initial-state evaluation for trajectory
training" question.

`CouplingChannel.applicability` (`arch-19-coupling-structure §19.2`) uses
the same predicate contract: a first-order decidable function on typeclass
tags. A channel whose `applicability` returns `false` is skipped at Stage 2.5
and contributes no invariants to the composition.

The storage shape for an applicability predicate is a
`MerkleDAG[PredicateOps, C1Atom]` root in the substrate's sense
(`arch-20-representations §20.2`, §20.3 row for the applicability
cluster): a reduced ordered Boolean DAG over typed parameterized atoms
drawn from the C1 typeclass-tag vocabularies (`arch-10-typeclasses`).
The atom order is part of the predicate-vocabulary version
(`arch-20 §20.9`); adding a new atom creates a new order id and forces
explicit re-canonicalization of stored predicate roots rather than
silent reinterpretation. Cert obligation checkers (`arch-12-cert`) are
**not** ROBDDs over typeclass-tag atoms — they are typed registered
morphisms from GENERIC artifacts to evidence, registered through the
C2 generator-registry machinery (`arch-20 §20.7`). The split is
preserved.

---


<a id="arch-14-topology"></a>

# Topology atlas

The architecture treats a *material* as a composition
`(Lattice + SiteDecoration + Laws) → Material` whose properties are derived,
never hardcoded. The **topology atlas** makes that derivation navigable. At
compose-time it computes, for each composition:

```
TopologyAtlasEntry =
  ( space-group   : 1..230 (+ magnetic)
  , AZ-class      : ten-element symmetry-class label
  , X_BS          : finite abelian symmetry-indicator group
  , EBRs          : elementary band representations
  , compatibility : compatibility-relation matrix )
```

`X_BS` is computed in polynomial time via Smith Normal Form on the integer
matrix of orbit-induced representations. (117 of 230 space groups have
non-trivial `X_BS` under time-reversal in the spin-doubled setting; max
`|X_BS| = 72`.) Cheap parts — `X_BS` class, orbit-representation decomposition,
compatibility check, boundary-mode multiplicity via the indicator lookup — are
always-on at compose-time. Expensive global integrals over the dual-space grid
(Wilson loops, Chern integrals, Z₂ via Pfaffian) are opt-in per observable.

The atlas gives the PINO a navigational signal: `X_BS` tells the model which
compositions are topologically equivalent, so gradients in one inform the other.
Topology is the map, not a feature. Atlas outputs are `DiscreteStructure`
instances (§10), and cert obligation-7 is literally a morphism over them.

---


<a id="arch-15-gamma-hat"></a>


# γ̂ as a Stage-4 lowering choice

The one-body density matrix `γ̂` (one of the seven state DOFs in
`arch-04-state`) is the most demanding object in the state vector: a
single logical entity with multiple inequivalent encodings, where
different operations have different runtime cost on different
encodings.

Under the `PhysicsGraph` framing (`arch-06-physics-graph`) and the
compose-time pipeline (`arch-07-pipeline`), `γ̂` is one node-type
whose Stage-4 `CompressionPlan` ranges over a structured `Basis ×
Form` product. This file documents that product and the residual
open questions about it.

## 15.1 The encoding vocabulary

An encoding factors into two orthogonal axes:

```
Basis ∈ { Real, Reciprocal, Wannier, NaturalOrbital, SymmetryAdapted }
Form  ∈ { Dense, Sparse, BlockDiag, LowRank }
```

First-class V1 pairs:

- `(Reciprocal, BlockDiag)` for periodic substrates (the diamond MVP
  default).
- `(Real, Sparse)` for defects, surfaces, amorphous regions.
- `(Wannier, Sparse)` for interface layers and dangling bonds.
- `(NaturalOrbital, LowRank)` for low-rank substrates.
- `(SymmetryAdapted, BlockDiag)` for the output of
  `SymmetryAdaptedHamiltonianOf` (`arch-09-vocabularies §9.2`).

Stage 4 selects one slot per density-matrix-typed node based on the
`(PeriodicityStructure, SiteDecoration)` tuple. Transcoders convert
on demand for operations whose runtime cost is lower in a different
encoding.

## 15.2 Read path vs write path

Most `γ̂` traffic during PINO training is **reads** — apply `Ĥ`,
extract density, take a trace, take an eigendecomposition. A small
minority is **writes** — construction, self-consistent step,
time-stepping. The two paths differ:

```
READ PATH (dominates trajectory evaluation):
    interface ──destructor──▶ tensor-network substrate
    (lazy materialization; no term staging, no bundle sync)

WRITE PATH (construction, self-consistent step, time-stepping):
    interface ▶ term-algebra ▶ planner ▶ (encoding) ▶ substrate
```

Under the always-cheap pipeline, the read path is what the runtime
kernel does; the write path is absorbed by Stage 4 codegen.

Self-consistency (when `Ĥ[γ̂]` depends on `γ̂`) is *structured* by the
coalgebraic fixed-point form but **solved by the implicit-diff adjoint**
synthesized at Stage 4 (`arch-07-pipeline §7.4`); convergence work
happens via explicit iteration above the substrate.

## 15.3 Strategies as Stage-4 internals

Several representation strategies that might naively look like
architectural peers are, under the always-cheap framing, Stage-4
codegen tactics applied to nodes whose `type` is the density-matrix
typeclass:

| Strategy | Realization |
|---|---|
| Codata / coalgebraic interface | The `Node` interface itself (`arch-06-physics-graph §6.1`); destructors are method invocations |
| Typed term algebra (staging) | Stage 1 / Stage 3 internal — the symbolic IR for compose-time |
| E-graph with equality saturation | Optional offline rewrite oracle; not on the runtime path |
| Pullback bundle of synchronized encodings | Single-slot V1 (one canonical encoding per node); the bundle is a multi-slot V2 generalization |
| Tensor network with cost-aware contraction | Stage-4 codegen primitive for `Form ∈ {LowRank, BlockDiag}` |

## 15.4 Open questions

Genuinely open, deferred to V2 unless the diamond MVP forces them
sooner:

- **Approximate vs exact equality (ε-equivalence).** If the node
  identity contract is bisimulation-up-to-ε rather than exact equality,
  the e-graph layer needs error tracking; this is unsolved and is the
  main reason e-graphs stay an offline tool in V1.
- **Materialization policy.** When to force vs defer materialization
  on the read path is workload-dependent with no principled default.
- **Long-trajectory drift and rank growth.** Encodings degrade over
  many steps (low-rank densifies, sparsity fills in); a refresh /
  rebalance policy is undefined.
- **Rank-dependent applicability.** The `(NaturalOrbital, LowRank)`
  slot's value rests on low-cost consistency checks, which become
  prohibitive for higher-rank objects (four-index BSE, BTE collision
  matrices). Those objects use TT compression directly
  (`arch-07-pipeline §7.4`) and stay out of the bundle.

## 15.5 Diamond MVP commitment

The diamond MVP runs on `(Reciprocal, BlockDiag)` with each k-block
stored as orbitals (low-rank in the band index). At MVP scale this
sizes at ~18 MB total; densifying would cost ~460 MB at the same mesh,
which is exactly why the encoding forbids it (`mvp-02-gamma-budget`).


<a id="arch-16-pino-bridge"></a>


# The pino-bridge exports

`pino-bridge` is the only surface `/informed-operator` (and other
downstream consumers) sees. Two exports.

## 16.1 `Validate` — the differentiated residual surface

```
Validate(state    : UnifiedState,           -- the 7-tuple of arch-04-state
         env      : Environment,
         request  : all | {ResidualKey} | {ObservableRef},
         gradient : Skip | Compute)
       → ( residuals : Map<ResidualKey, Scalar>           -- granular per arch-11-residuals
         , values    : Map<ObservableRef, Value>          -- bundled observable outputs
         , cograds   : Optional<Map<ResidualKey, Cotangent>>
         , cert      : CertEvidence )
```

Single entry point. The `request` parameter selects which subgraph of
the compiled kernel to evaluate (full graph, a subset of residual leaves
keyed by `ResidualKey`, or a subset of observables). The `gradient`
parameter toggles the adjoint — when `Skip`, the kernel runs
forward-only, emitting residual values and observables without their
cotangents.

The output is **granular by construction** (`arch-11-residuals`): each
contribution is its own scalar with its own key. The PINO chooses
aggregation; `/physics` does not pre-sum.

## 16.2 `Import` — external ground truth

```
Import(named-target : ObservableRef,
       value        : Value,
       sigma        : Scalar,
       provenance   : Provenance,
       coverage-mask : CoverageMask)
     → GroundTruthBridgeGenerator
```

Per-target ingestion. Each call wraps one external datum (a VASP
energy, an experimental mobility curve, a curated battery row) as a
`GroundTruthBridgeGenerator` — the dataset analogue of
`ResidualGenerator` (`impl-07-residual-factory §7.1`). At Stage 1
(`arch-07-pipeline §7.1`) the generator inserts a pinned `Input`
node carrying `(value, sigma)` and a cert-only `ResidualLeaf` node
keyed by the named target's `ResidualKey`. `Import` is not
differentiated through; its `ResidualLeaf` outputs serve obligation
4 (reference battery, `arch-12-cert`) and feed `/informed-operator`'s
target-vs-prediction comparison.

### 16.2.1 `CoverageMask = RoaringCoverageMask`

`CoverageMask` declares which axis tuples of the named target the
imported datum actually constrains. The wire format is a serialized
**Roaring bitmap** over a flat index built from the generator's `axes`
(`impl-07-residual-factory §7.2`):

```
flat-index(axes) = enumerate(product(axes))   -- lexicographic over axis values
RoaringCoverageMask = serialized Roaring bitmap of selected flat-index positions
```

- **Sparse-from-start.** Coverage is overwhelmingly sparse: a battery
  row touches one `(k-point, band)`; an experimental σ(T) curve touches
  one axis; a phonon-dispersion datum touches one branch over a
  one-dimensional `k`-path. Dense-with-compression buys nothing and
  forces a full decode before lookup.
- **Why Roaring.** O(1) membership, fast intersection/union/cardinality
  for set ops the cert evaluator needs (e.g., "which (k, n) pairs are
  covered by *some* battery row?"), industry-standard format with
  bindings in every candidate language.
- **Persisted form.** The serialized Roaring bytes go into the
  `coverage_mask` column of `SqliteReferenceCache.entries`
  (`arch-12-cert §12.1`).

## 16.3 What is not exported

`Predict`, `Certify`, and `EnumerateObservables` remain available as
internal `/physics` API for non-PINO consumers (the future
`/interface`, debugging tools, the cert-only batch validator). They are
not part of the pino-bridge contract.


<a id="arch-17-out-of-scope"></a>

# Out of scope

Stated and held, so the architecture is honest about what it does not cover:

- Strongly-correlated systems (frustrated Wigner crystals, spin liquids, Mott
  physics) — `γ̂` is mean-field by construction; UWBG materials are large-gap and
  far from Mott physics.
- Flexoelectricity in centrosymmetric materials — below the numerical-noise
  floor; order-of-magnitude only.
- Magneto-thermal coupling in heavy contact metals — formally in `S`, not
  modeled.
- Deep-defect non-Markovian dynamics — Markov master-equation closure assumed.
- Polaron localization beyond Fröhlich.
- Full NEGF tunneling, full SCPH/SSCHA, and the **live** iterative-LBTE / full
  4-phonon BTE solve — deferred to Layer-1.75 V2 scaffolding. The **closed-form
  high-T 4-phonon correction** (Slack-like multiplicative κ-factor, valid `T ≳ 0.4 Θ_D`,
  registry row 121) and the **iterative-LBTE κ sibling anchored to published `κ_iter`**
  (row 122, dormant `MethodEquivalence` binding — no live solve) **do** ship in V1 as the
  Layer-1.25 / closed-form path; only the live BTE solve is V2. Where a cheap proxy is
  needed during training it is a registered D4 surrogate with an obligation-9 validity
  domain; **no such surrogate ships in V1**, with the accuracy regime declared in the
  ledger (`arch-11-residuals §11.7`, `docs/accuracy-ledger.md`).
- **AHC e-ph gap renormalization beyond the adiabatic one-shot** — the faithful
  `A_qν` Brillouin-zone sum and **non-adiabatic AHC** (Layer-1.75; ~25% on polar ZPR)
  are deferred to V2. V1 ships the adiabatic one-shot dressing `ΔE_g=ZPR·coth(Θ/2T)`
  (registry row 120) with per-material ZPR/slope coefficients (`docs/accuracy-ledger.md`).
- **EDF-tail / hot-carrier breakdown above ~500 °C** — the BTE-full / full-band-MC
  high-E×high-T tail correction needs per-material BTE/MC anchor data that **do not exist
  in the V1 corpus**; until they do, the learned `Δα` correction ships as identity and the
  corner is **cert-refused** (`arch-19-coupling-structure §19.8`, `arch-12-cert §12.0.3`),
  not claimed as a met target.
- **Plasmon–phonon coupling / LST-relation breakdown at degenerate doping** — above
  `n ≳ 10²⁰ cm⁻³` (reached by p⁺ B-doped diamond contact layers), the
  Lyddane–Sachs–Teller-derived static `ε_r` and Fröhlich screening lose validity. V1
  **applicability-gates** the LST `ε_r` path and Fröhlich screening on `n < n_degenerate(host)`;
  outside the gate the quantity is masked, not silently extrapolated. (Same gate carries the
  degenerate-Einstein refinement, `arch-21-multiscale-state §21.7.2`.)
- **III-N high-temperature thermal expansion** — QHA breaks above ~Θ_D/2 (GaN fails by
  ~500 °C); V1 has **no design-grade path**, only per-material σ-widening in the ledger
  (`accuracy-ledger §14`). This propagates into gap(T) (row-63 strain), `G(T)`, and the
  T,P-hull for the flagship polar materials. V2 = a first-order self-consistent-phonon
  correction as a second Layer-1.25 dressing (one-shot, same amortization shape as AHC).
- **Alloy-disorder mobility in AlGaN beyond the closed-form Harrison term** — the
  `is-alloy`-gated row 127 (`τ_alloy⁻¹∝x(1−x)ΔU²g(E)`) ships in V1; a full
  configurationally-averaged disorder treatment is V2.
- **Pure-AlN avalanche & p-type transport, and measurement-grade AlN high-T `κ`** — AlN has no
  measured impact-ionization coefficients (only Bulutay's full-band-MC *electron* values, SST 17
  L59 (2002); no hole), no measured bulk hole mobility (deep Mg acceptor, holes `< 10¹⁰ cm⁻³`), and
  no single-crystal `κ` measurement above ~500 K. V1 **cert-refuses** measured-AlN avalanche and
  p-AlN transport claims, and flags AlN high-T `κ` as theory-only (`docs/accuracy-ledger.md`;
  `docs/specs/2026-06-10-wave1-iii-n-seeding.md`). The AlN electron Caughey–Thomas
  mobility quartet exists but is paywalled (Farahmand IEEE TED 48 535 (2001) Tbl II / Wang arXiv
  2506.09240 (2025) Tbl SIII) — a targeted acquisition follow-up, not a V2 deferral.
- Absolute Berry-phase / Wannier-center polarization (the λ-path `P_sp` evaluator) —
  deferred to V2. V1 uses the Z*-composition path (`arch-19`/registry rows 113–114, ±5%,
  `accuracy-ledger` #35); the absolute modern-theory integral needs a
  `berry-phase-polarization` sub-stage not in the closed 12-method alphabet, analogous to
  the G₀W₀ gap upgrade over PBE.
- Plasma-process surface damage; grain-boundary statistics; continuum creep /
  dislocation climb; quantum-tunneling-corrected reaction rates (classical
  Eyring TST adequate at T_op ≥ 600 K).
- **Total-ionizing-dose (TID) radiation effects** — oxide trapped charge and
  D_it buildup in gate dielectrics under ionizing flux. Displacement damage
  (rows 111–112) is in scope; TID is predominantly amorphous-oxide physics and
  is deferred with the dielectric wave (couples to the amorphous-ALD entry
  below). (2026-07 gap-audit B5.)
- **Single-event effects (SEE/SEU)** — transient upsets from single-particle
  strikes; belongs to a digital-circuit layer above `/physics`
  (`non-equilibrium-high-field.md` H.3 disposition, now registered here).
- **h-BN as a host material** — appears in research anchor sets only; the
  layered-material machinery it needs (direction-dependent moduli — the
  bulk-modulus classifier already special-cases it — borderline-polar in-plane
  response, van-der-Waals interlayer channel) is not in the V1 scope list
  (arch-01). Decide in only if a 2D-substrate use case materializes.
- **Amorphous ALD gate films** — `/physics` models the *crystalline* polymorphs
  (α-Al₂O₃, monoclinic HfO₂, AlN-as-dielectric); as-deposited amorphous films
  have no `PeriodicityStructure` and are out of scope as hosts. Their
  *crystallization* — the >700 °C leakage-spike driver — **is** in scope as the
  slow-tier JMAK row (registry row 131), and the dielectric compact-model rows
  (Poole–Frenkel 129, TDDB 130) apply to the film as a parameterized layer, not
  as a resolved crystal. (2026-07 gap-audit B2/B5.)
- **General dopant redistribution** — row 106's drift–diffusion shape
  instantiates per species; V1 carries H (the corpus's named "silent killer");
  other dopants (Mg in GaN, …) are per-material wave instantiations of the same
  row, not new physics.
- True renormalization-group flow; inverse design / minimal-model search (would
  live in `/informed-operator` as a PINO head, not a `/physics` primitive);
  fragile topology.

`predict` raises `out-of-scope` with a witness for any of these; cert
obligation-3 flags suspect cases.

---


<a id="arch-18-open-decisions"></a>

# Open decisions

The architecture above is committed. These remain to be decided.

1. Surrogate-net build vs adopt, for the D4 surrogate formulas.
2. PDE-mesh **adjoint scheme** (discrete- vs continuous-adjoint of the
   finite-volume operator) for the macro continuum tier. The mesh **format** is no
   longer open — it is committed as a `DeviceMesh` finite-volume `Universe` with
   fields as fibers (`arch-21-multiscale-state §21.6`); only the adjoint binding
   remains, reusing the Stage-4→Stage-5 AD seam.
3. The `γ̂` open questions of `arch-15-gamma-hat §15.4` (ε-equality,
   materialization policy, long-trajectory drift / rank-refresh, rank-dependent
   applicability of the LowRank slot).
4. Layer-1.75 minimum spec sufficient for a V2 contributor to implement
   self-consistent GW / DMFT.
5. The integrator interface — the exact signature `dynamics` exposes to
   `/informed-operator` for handing off the assembled GENERIC right-hand side.
## Closed decisions

- **Multiscale state (slow + macro tiers) & the device scale-bridge** =
  the state is stratified into three tiers (`arch-21-multiscale-state`): the micro
  7-tuple (unchanged), a **slow / configurational tier** (defect populations,
  H content, oxidation/carbide fronts) evolving by Arrhenius generation–annihilation
  kinetics — **aging is core `/physics`** state the PINO predicts and `/physics`
  scores — and a **macro continuum tier** (homogenized `T_L(r), φ(r), n(r), p(r),
  j(r)` on a `DeviceMesh`) bridged to the micro tier by an explicit homogenization
  map. The emergence axiom is refined to *same-timescale/scale* coarse-graining
  (resolving the `arch-04`↔`arch-08` tension); the full distribution stays emergent
  by moment closure (no DAE); two EOM-family residual categories
  (`EOM/DefectPopulation`, `EOM/Continuum`) are added. No new computational method is
  introduced (the slow tier reuses `kinetic-evolution`). Residue: the PDE-mesh
  adjoint scheme (open item 2 above).
- **Implementation language** = a **polyglot of domain-specific DSLs** joined at
  the pipeline's Stage-4→Stage-5 codegen seam, not a single language
  (`physics/research/implementation-language.md`). This was the single blocking
  decision; closing it unblocks the first implementation phase.
  - **Haskell** hosts Stages 1–4 + the `arch-20` substrate (the symbolic-IR
    compiler): GADTs / `DataKinds` / type families type the op-indexed Merkle DAG
    and the `SymbolicTensorOps` operad at compile time; `hegg` provides the
    Stage-3 e-graph; `GHC.Generics` derives the §20.4 canonical serializer; our
    own AD drives Stage-4 adjoint synthesis. (OCaml is the documented fallback
    host.)
  - **Julia** is the Stage-5 runtime: Stage 4 **emits Julia source**, JIT-compiled
    once per composition, so the hot loop is native Julia with no per-sample FFI;
    Julia owns the optional GPU codegen.
  - **GAP** (offline) generates/validates the Stage-2/2.5 character tables and
    Reynolds projectors (`|G|≤192`), baked into the compiler.
  - **Lean 4** (offline) proves §20.4 pre-hash canonical-encoding injectivity and
    the `EvidenceOps` / `GroupOps` / ROBDD algebraic laws.

  Hardware: a **CPU-dominant compiler**; GPU is a Stage-5-only optional accelerator
  chosen per-composition (the symmetry quotient yields small irrep blocks — a GPU
  anti-pattern — so the diamond MVP often runs fastest on CPU). The polyglot split
  is a net win **conditional on** a Stage-4→Stage-5 differential golden test; the
  single-host fallback is Julia-only or Haskell-only. Rust (the single-language
  winner) is excluded by preference; Python+JAX is disqualified — its tracer owns
  differentiation, which conflicts with bring-your-own adjoint synthesis.
- **ReferenceCache backend** = `SqliteReferenceCache` (`arch-12-cert §12.1`).
- **Coverage-mask format** = `RoaringCoverageMask` (`arch-16-pino-bridge §16.2.1`).
- **Curriculum schedule** = `0.10 / 0.60 / 0.90` cumulative fractions, last
  `0.10` cooldown (`arch-11-residuals §11.4.1`); overridable by
  `/informed-operator`.
- **Active-learning loop placement** = `/interface`
  (`arch-01-purpose` "What `/physics` is not").
- **Applicability decidability** = first-order decidable on typeclass tags;
  enforced at registration (`impl-04-formulas`,
  `impl-10-build-sequence` Phase 7).
- **Coupling structure** = generic `CouplingChannel` record with three
  parameter axes (`pieces`, `target ∈ {Scalar, AntisymmForm, PSDSymmForm}`,
  `order × derivative`) plus a Stage-2.5 invariant generator that constructs
  the explicit terms from the crystal's symmetry group
  (`arch-19-coupling-structure`). The nine named cross-regime strings of
  `arch-05-generic` collapse to a handful of channel declarations; the
  per-coupling terms are generated, not registered.
- **Coupling-channel coverage policy** = a bounded `CoverageBound`
  (global cap `(order ≤ 4, Gradient(1))` + a per-mechanism inner table)
  plus the runtime rule "active channels are those whose `applicability`
  holds and whose invariant basis is non-empty," **not** a hand-curated
  registry (`arch-19-coupling-structure §19.9`). Each channel carries a
  `mechanism_range` tag whose derived `polynomial_sufficient` flag decides
  whether the symmetry-generated basis is the whole coupling; long-range
  channels carry a typed `KernelExt` for the non-polynomial part
  (§19.10–§19.11). The composition's theory frame is a `TheoryContext` on
  `CouplingSpec` (XC functional / pseudopotentials / many-body level /
  relativistic treatment), and `PSDSymmForm` channels carry documented PSD
  assumptions rather than a runtime SDP search (§19.11–§19.12). MVP default
  theory context: `PBE / PseudoDojo-v0.4.1-NC / KohnSham / ScalarRelativistic`.
- **Representation substrate** = one substrate contract (typed indexed
  universes, content-addressed Merkle DAGs, sparse-set backends,
  persistent stage-visible maps) plus a small parametric op-signature
  family (`PredicateOps`, `SymbolicTensorOps`, `EvidenceOps`,
  `GroupOps`) and specialized algebraic fibers per cluster
  (`arch-20-representations`). Every `/physics` representational object
  is a fiber over this substrate; identity, canonical serialization,
  and attachment are unified, while each cluster keeps the backend that
  wins on its hot path.
- **PhysicsGraph identity** = closure of output `Address[GraphNode]`
  set under children-pointers; edges are the children addresses inside
  each node payload, not separately identified.
- **Sidecar / evidence relationship** = sidecars carry `EvidenceId`
  attachments via the `EvidenceBearing` wrapper; materialized evidence
  lives in a persistent `EvidenceDAG`. Sidecars remain ephemeral or
  cache-eligible per domain; evidence persists across composition
  boundaries.
- **No solver-call hot paths.** Every hot operation in the
  `/physics` substrate is `O(log n)` or better with documented
  constant factors (`arch-20-representations §20.5`); no equivalence
  or subsumption op requires SAT or a runtime rewrite engine.


<a id="arch-19-coupling-structure"></a>

# Coupling structure

Cross-regime physics — electron-phonon, spin-orbit, magneto-elastic,
minimal coupling, phonon-phonon scattering, radiative damping, … —
is one kind of object with a small parameter space, not a hand-rolled
list of named terms.

## 19.1 The object

A **coupling** is a symmetry-respecting function from a tensor product
of pieces of the state vector (`arch-04-state`) into one of three
target shapes:

- **`Scalar`** — a real-valued function; lands in `E_coupling`
  (`arch-05-generic §5`).
- **`AntisymmForm`** — an antisymmetric 2-form on the tangent bundle;
  lands as an off-diagonal block of `L` (`arch-05-generic §5`).
- **`PSDSymmForm`** — a positive-semidefinite symmetric 2-form on the
  cotangent bundle; lands as an off-diagonal kernel of `M`
  (`arch-05-generic §5`).

Every cross-regime term in `arch-05-generic` is one instance of this
object.

## 19.2 The parameter axes

```
record CouplingChannel {
  pieces        : List<StatePiece>            -- ordered tensor factors
  target        : Scalar | AntisymmForm | PSDSymmForm
  order         : Nat                         -- # tensor factors (typically 2..4)
  derivative    : Ultralocal | Gradient(Nat)  -- spatial-derivative depth
  applicability : (Crystal, Environment) → Bool
  -- coverage-policy fields (§19.9–§19.10):
  mechanism_range  : MechanismRange               -- curated; source of truth for the next flag
  kernel_extension : Optional<KernelExt>          -- the non-polynomial part; present iff ¬polynomial_sufficient
  gauge_rule       : Optional<GaugeRule>          -- basis/gauge fixing (e.g. Wannier gauge); usually None
  provenance       : Optional<ProvenanceLedger>   -- where the coefficients came from; the normal annotation
}

record StatePiece {
  component : StateComponent                  -- one of γ̂, A, R, P, h, Π_h, Z
  sub-dof   : SubDofTag                       -- orbital | spin | sublattice | valley
                                              -- | strain | gauge | charge | none
}
```

`StateComponent` is the existing 7-tuple alphabet (`arch-04-state`).
`SubDofTag` enumerates the internal labels a component carries:
γ̂ carries `orbital`, `spin`, and (when applicable) `sublattice`,
`valley`; `h` carries `strain`; `A` carries `gauge`; etc. The
allowed `(component, sub-dof)` pairs are tabulated alongside the
state-component definition.

`order` and `derivative` declare the truncation. They are not part of
the underlying physical structure; they are the compose-time choice of
how high in the multipole / multi-tensor expansion to go.

The last four fields carry the coverage policy. `mechanism_range`
(§19.10) records whether the channel's mediating interaction is
short-range or long-range; from it the derived flag
`polynomial_sufficient` decides whether the symmetry-generated
polynomial basis is the *whole* coupling or only its short-range part.
When it is only a part, `kernel_extension` (§19.11) carries the
non-polynomial remainder. `gauge_rule` fixes a residual basis ambiguity
for the rare channels that have one; `provenance` records where the
numeric coefficients came from and is the ordinary annotation every
channel may carry. All four are `make-coupling-channel`-validated
(§19.8).

## 19.3 The invariant generator

```
generate-invariants : CrystalSymmetryGroup × CouplingChannel
                    → GeneratorOutput
```

Standard representation theory. Given the crystal's symmetry group
(`arch-09-vocabularies` lifts `CrystalSymmetryGroup` to a first-class
typeclass entity; Stage 2 already builds it from
`PeriodicityStructure × SiteDecoration`) and a channel specification,
this routine returns the finite basis of `target`-shaped
symmetry-invariant terms of the requested `order` and `derivative`.

Each `InvariantTerm` is a symbolic tensor expression carrying:

```
record InvariantTerm {
  channel         : CouplingChannel
  irrep-coefficients : IrrepCoefficientTable   -- the trivial-irrep coefficients
                                               -- of the underlying tensor product
  symbolic-form   : SymbolicTensor             -- the explicit term; stored as the
                                               -- root of a MerkleDAG[SymbolicTensorOps,
                                               -- TypedLeaf] per arch-20 §20.2
  generator-hash  : Address[InvariantTerm]     -- domain-separated content address
}
```

The generator returns a `GeneratorOutput`, not a bare list, because a
channel's full coupling may be the polynomial basis *plus* a
non-polynomial kernel (§19.10–§19.11):

```
record GeneratorOutput {
  polynomial_invariants : List<InvariantTerm>     -- the symmetry-generated basis
  polynomial_sufficient : Bool                     -- echoed certificate (derived, §19.10)
  kernel_extension      : Optional<KernelExt>      -- the non-polynomial remainder, if any (§19.11)
  gauge_rule            : Optional<GaugeRule>       -- a basis-fixing rule, if any
  output_hash           : Address[GeneratorOutput]  -- domain-separated; folds in all three above
}
```

The `polynomial_sufficient` flag is echoed into the output so that a
downstream stage holding only `polynomial_invariants` can never silently
treat a partial (short-range) basis as the complete coupling.

The generator is the *constructive* direction of the irrep machinery
that Stage 2 already uses *decompositionally* (`arch-07-pipeline §7.2`
block-diagonalizes operators by irrep). Same module; same primitives;
new direction.

**Contract.** The routine runs three integrity guards, a free O(1)
spinor-parity pre-prune, then the projector:

```
generate-invariants(G, c) :
  -- (0) well-formedness (§19.10): the flag and the kernel must agree
  if ¬polynomial_sufficient(c) ∧ c.kernel_extension = None: error "partial coverage, no kernel"
  if  polynomial_sufficient(c) ∧ c.kernel_extension ≠ None: error "sufficient channel carries a kernel"
  if ¬polynomial_sufficient(c) ∧ ¬kernel_tag_matches_range(c): error "kernel tag ≠ mechanism_range"
  -- (1) spinor-parity pre-prune: an odd total spinor count cannot form a Scalar / PSDSymmForm /
  --     AntisymmForm invariant, so the basis is empty before any character is computed
  if odd_spinor_count(c.pieces) ∧ c.target ∈ {Scalar, PSDSymmForm, AntisymmForm}: poly = []
  else: poly = trivial_irrep_projector(G, c.pieces, c.target, c.order, c.derivative)
  -- (2) return both parts; the kernel rides through untouched by the symmetry projector
  return GeneratorOutput{ poly, polynomial_sufficient(c), c.kernel_extension, c.gauge_rule, … }
```

**Emptiness and complexity.** Emptiness of `poly` is decided by the
character inner product `⟨χ_T, χ_trivial⟩_G = (1/|G|) Σ_g χ_T(g)`, a
single trace per group element — never forming `ρ(g)` explicitly. For
the MVP worst case (`|G| ≤ 192` with the double cover and time reversal,
`dim(T) ≤ ~250` at `order = 4, Gradient(1)`): the character pre-prune is
O(|G|) ≤ ~200 ops; the full Reynolds projection `P = (1/|G|) Σ_g ρ(g)`,
run only when the basis is non-empty, is O(|G|·dim(T)²) ≤ ~12M ops. The
result is cached on `Address[CrystalSymmetryGroup] × Address[CouplingChannel]`
(`arch-20-representations §20.4`), so per-composition cost is one-shot.
The cache key does **not** include the theory context (§19.11): the
polynomial basis is symmetry-determined and theory-independent.

> **Emptiness ≠ correctness.** A non-empty `poly` is *correct as far as
> it goes* but may still be only the short-range part of a long-range
> coupling. Whether `poly` is the *whole* coupling is the separate
> `polynomial_sufficient` question (§19.10), not the emptiness question.

## 19.4 Worked example — diamond electron-phonon

The library author declares one channel:

```
electron-phonon = CouplingChannel {
  pieces        = [ StatePiece(γ̂, orbital), StatePiece(R, none) ]
  target        = Scalar
  order         = 2
  derivative    = Ultralocal
  applicability = is-crystalline                     -- always true for diamond
}
```

At compose time:

1. **Stage 1** records the channel in `Stage1Sidecar.coupling-channels`.
2. **Stage 2** has already constructed the diamond symmetry group
   (Fd-3m + time-reversal).
3. **Stage 2.5** (new sub-stage, §19.5) runs
   `generate-invariants(Fd-3m+TR, electron-phonon)` and returns one
   `InvariantTerm`: the canonical `g_{nm,ν}(k,q)` matrix element
   written as a symmetry-respecting tensor.
4. **Stages 3–4** lower that `InvariantTerm` into a `FormulaApply`
   node attached to the `E_coupling` aggregator (a
   `MethodInvoke(hamiltonian-assemble, …)` node).

The symmetry group generates the admissible **form** of `g_{nm,ν}(k,q)` — which
invariants exist and their index structure. The **numerical values** (deformation
potentials, Fröhlich and anharmonic parameters) are supplied by the
`ProvenanceLedger` (DFPT / finite-difference / fits), outside the generative
structure: symmetry generates the form, provenance supplies the values.

Spin-orbit, magneto-elastic, minimal coupling (γ̂ ↔ A), Stark, Zeeman,
phonon-phonon, radiative damping — each one is a `CouplingChannel`
record with a different parameter assignment. None of those strings
appears as a value in any enum.

## 19.5 Stage 2.5 — invariant synthesis

A new sub-stage in `arch-07-pipeline §7.2`, executed between Stage 2's
block-diagonalization rewrite and Stage 3's algebraic simplification.

```
Inputs  : Stage1Sidecar.coupling-channels  : List<CouplingChannel>
          CrystalSymmetryGroup             (constructed in Stage 1+2)
Action  : For each channel c whose c.applicability holds, compute
          generate-invariants(group, c); attach the returned
          GeneratorOutput to the channel.
Outputs : Stage2_5Sidecar.invariants : Map<CouplingChannel, GeneratorOutput>
```

Consumed by Stages 3–4 when lowering invariants into `FormulaApply`
nodes targeted at the existing `E_coupling`, `L_assembly`,
`M_assembly` aggregator methods.

## 19.6 Composition

- **Within a single `target`.** Invariants compose by direct sum:
  `E_coupling = Σ_{c} Σ_{v ∈ invariants[c] | v.target = Scalar} v.symbolic-form`,
  and analogously for the L and M target shapes.
- **Across `target` shapes.** Composition is the existing E / L / M
  assembly in `arch-05-generic`.
- **Order truncation is monotone.** Order-`(n+1)` includes order-`n`
  as a prefix; the spec author chooses the cutoff per channel.
- **No channel-correlation primitive in V1.** If two physical
  mechanisms genuinely correlate (a cross-term in `M` between two
  scattering processes that are not independent), they are modeled as
  *one* `CouplingChannel` with a larger tensor product (more `pieces`),
  not two channels with an extra correlation parameter. This keeps the
  V1 algebra additive.
- **Kernel extensions add as one more summand.** When a channel carries
  a `kernel_extension` (§19.11), its lowered kernel node adds into the
  same aggregator as its polynomial invariants:
  `full_coupling = Σ poly_invariants + kernel_extension(q, ω)`. No new
  aggregator and no new composition primitive — the kernel is one summand
  in the existing direct sum. A long-range mechanism is therefore split
  into **two channels** — a short-range polynomial channel and a
  long-range kernel channel — rather than one channel that is partly
  polynomial and partly not (e.g. electron-phonon = a deformation-potential
  channel + a Fröhlich channel, the standard Verdi–Giustino SR/LR split,
  `arch-19 §19.10`).

## 19.7 Cert hooks

The invariant-generator structure simplifies two cert obligations
(`arch-12-cert`):

- **The symmetry-equivariance obligation.** Polynomial invariants are
  trivial-irrep basis vectors *by construction*; equivariance is
  automatic. Cert reduces to a numerical projection-residual check:
  `||v.symbolic-form − π_trivial v.symbolic-form|| < δ_sym` on a sampled
  evaluation. Failure indicates a generator bug, not a physics bug. A
  `kernel_extension` is **not** exempt: it is "scalar under the
  little-group of q" (`KernelExt.symmetry_law`, §19.11), so cert checks
  `‖K(Rq,ω) − D(R) K(q,ω) D(R)†‖ < δ_sym` over little-group elements `R` —
  a checkable equivariance, just not a polynomial one.
- **The positivity obligation** (antisymmetry of `L` / PSD of `M`).
  The `target` tag determines a projection rule applied at the
  generator step: `AntisymmForm` invariants are projected onto the
  antisymmetric component of the candidate tensor; `PSDSymmForm`
  invariants are projected onto the PSD cone. The projection is part
  of the generator's contract; cert numerically verifies the projected
  output matches the emitted `symbolic-form` within `δ_sym` (`arch-12 §12.0.2`).
  For `PSDSymmForm` channels, PSD *existence* is a structural theorem rather
  than a runtime search — see the documented assumptions in §19.12 — and the
  runtime PSD guard is checked on the **assembled dissipative super-block per
  mechanism** (diagonal + off-diagonal kernels together), not per off-diagonal
  kernel, via `arch-12 §12.0.1` obligation 2.

The polynomial checks are O(1) per invariant; both are integrated with
`SymmetryAdaptedHamiltonianOf` (`arch-09-vocabularies §9.2`) which
already lives in the symmetry machinery. The cert-obligation indices are now
fixed in `arch-12 §12.0.1`: equivariance = obligation 1, antisymmetry of `L` =
obligation 5 (conservation), PSD of `M` = obligation 2 (positivity).

## 19.8 Registration discipline

Channels register through the same factory pattern as residual
generators (`impl-07-residual-factory §7.3`):

```
make-coupling-channel(channel : CouplingChannel) → CouplingChannel
```

Returns the channel with its `applicability` validated as first-order
decidable on typeclass tags (the registration-time invariant from
`impl-04-formulas`). The channel's identity is `Address[CouplingChannel]`
under the canonical-serialization rule of `arch-20-representations §20.4`
(domain-separated, schema-versioned); identical channels collapse to one
address.

**Coefficient-provenance contract.** Symmetry generates the *form* of a channel's
invariants; the *values* (deformation potentials, Fröhlich and anharmonic
parameters, compact-model coefficients) enter through the channel's
`ProvenanceLedger` (§19.4 caveat). Each provenanced coefficient must carry:
`(value, σ, source, cost-class)` — where `cost-class ∈ {curated, per-material-DFPT,
fit}` declares its acquisition pipeline and `σ` its uncertainty (reusing the
reference-battery `σ` machinery, `arch-12 §12.1`). A **cert obligation refuses any
composition whose active channels carry coefficients without a `ProvenanceLedger`
entry** (an unprovenanced coefficient is a silent accuracy hole). For the MVP the
diamond coefficients are `curated`; other materials are `per-material-DFPT` and their
provenance is the gating data-acquisition task before that material is claimed.

**`slope-kind` tag — machine-checkable double-count guard for `dE_g/dT` (AHC).** Any
temperature-slope coefficient feeding `ahc-gap-renormalization` (registry row 120) additionally
carries `slope-kind ∈ {isochoric, total}`. The quoted experimental `dE_g/dT` slopes are mostly
*total* (they already fold in the lattice-expansion part that registry row 63 — `Ξ·strain` —
carries separately, ~30–40% of the shift). A **cert obligation refuses any composition in which a
`total`-tagged AHC slope and row-63's thermal-expansion T-path are both active on the same
observable** (double-counting the expansion contribution); an `isochoric`-tagged slope composes
with row 63 freely. The tag is a first-class field on the coefficient, so the check is a tag
comparison at compose time, not a reviewer caveat. The curated ZPR amplitudes feeding the `coth`
path (`docs/accuracy-ledger.md §1/§15`) are the **isochoric** electron-phonon values (Engel PRB 106
094316 (2022) / Miglio npj CM 6 167 (2020) AHC: GaN −189, AlN −399, diamond −345 meV), tagged
`isochoric`; the zero-point lattice-expansion part (Miglio: GaN −49, AlN −85 meV) is row 63's job —
so seeding a `total` magnitude into the e-ph `coth` path while row 63 is active is exactly the
double-count this guard refuses. (Wave-1 III-N audit: `docs/audits/2026-06-10-wave1-iii-n-audit.md`;
the prior `total` tag on isochoric Engel magnitudes was corrected there.)

**Polarization reference / proper-improper `e₃₁` self-consistency — machine-checkable pairing
guard.** Spontaneous polarization is reference-dependent; the 2DEG density `n_s` (registry row 115)
consumes an interface *difference* `ΔP` whose ±5% accuracy for AlGaN/GaN rests on an **accidental
cancellation** (Dreyer et al. PRX 6 021038 (2016) §V.D–E) between the spurious zinc-blende(ZB)-
reference term in `P_sp` and the proper-vs-improper `e₃₁` error — two large, opposite-sign
quantities — **not** generic reference-cancellation. The cancellation holds only under a
**self-consistent pairing**: either (a) ZB-reference `P_sp` + **proper** `e₃₁` + no ZB-correction
(the spec's path), or (b) layered-hexagonal-reference `P_sp` + `ΔP_corr` + **improper** `e₃₁`.
Because improper `e₃₁ ≈ 3.4× proper` for GaN/AlN, mixing conventions silently corrupts `n_s`. Each
polarization coefficient (`P_sp` row 113, `e₃₁` rows 114/117) therefore carries
`polarization-reference ∈ {ZB-proper, H-improper}`; a **cert obligation refuses any composition
whose active `P_sp` and `e₃₁` carry mismatched tags** (`arch-12 §12.0.3`). The ±5%-ΔP target also
carries an `is-AlGaN-GaN` validity scope — the cancellation **fails for high-In InGaN/GaN** and is
σ-degraded / cert-refused there. The spec's curated III-N coefficients (`docs/accuracy-ledger.md`)
are all `ZB-proper`.

**Learned-correction training contract (`Δα` EDF-tail and any PINO-fit residual coefficient).** A
coefficient whose `source` is a PINO-learned correction — the high-field EDF-tail correction
`Δα(E,T_L,T_e)` of the avalanche channel is the only V1 instance — is constrained two ways so it
cannot launder away its own supervision signal: (1) it is fit **only against external anchors**
(measurements or future BTE / full-band-MC points) and is **frozen with respect to the PINO
training loss** — gradients of the physics loss do not flow into it — because a correction trained
on the same residual it modifies can co-adapt to zero that residual and silently destroy the
obligation-9 domain it is meant to protect; (2) until such external anchors exist (the V1 corpus
has none — `docs/accuracy-ledger.md §49`), `Δα` **ships as the identity** (zero correction) and the
high-E×high-T corner stays **cert-refused** (`obligation 9`), making the ">500 °C breakdown =
cert-refused" stance load-bearing rather than decorative.

The active channels in a composition, **together with the theory frame
they are interpreted in**, are the **`CouplingSpec`**:

```
record CouplingSpec {
  channels       : SparseSet[CouplingRegistry]   -- the active channels (arch-20 §20.3)
  theory_context : TheoryContext                  -- the global theory frame (§19.11)
}
```

`CouplingSpec` was previously a bare `SparseSet[CouplingRegistry]`; it is
now a two-field record. Its `Address` is computed by the
`arch-20-representations §20.4` record rule, so two specs with identical
channel sets but different `theory_context` are guaranteed distinct
addresses — the theory frame is part of identity, automatically. The
`CouplingSpec` schema version is **bumped** (`arch-20 §20.9`) so old
bare-set addresses cannot collide with new record addresses. The spec is
carried alongside the composition request (`arch-07-pipeline §7.1`). The
diamond MVP's `CouplingSpec` is short: electron-phonon (short-range) +
minimal coupling + ion-ion electrostatic + phonon-phonon scattering
(in `M`), under the MVP default theory context (§19.11).

`theory_context` is **definitional input**: it is set at Stage 1, and it
must exist before Stage 2 builds the (possibly double-cover) symmetry
group, because the relativistic treatment determines whether the group
carries the spin SU(2) factor. A `make-theory-context(raw) → TheoryContext`
smart constructor (mirroring `make-coupling-channel`) **must** normalize
and validate before any `Address[TheoryContext]` is taken — this is
load-bearing for content addressing, not optional: it normalizes the
hybrid-functional double representation (a hybrid is always
`XCFunctionalTag.Hybrid` with `ManyBodyLevel.KohnSham`, never
`HybridAsManyBody`) and enforces relativistic PP/run consistency, so two
byte-distinct encodings of the same physics can never produce two
addresses.

## 19.9 Coverage policy (not a hand-curated registry)

The "coupling-channel template registry" is **not** an enumerated list of
coupling terms. A channel is a tuple in the parameter space
`(pieces, target, order, derivative, mechanism_range, applicability)`; the
registry is a **coverage policy** — a bounded subset of that space — plus
the runtime rule:

> the active channels for crystal `C` are those whose `applicability`
> holds and whose invariant basis is non-empty under the crystal's
> symmetry group `G_C`.

The invariant generator (§19.3) is the filter that culls structurally
empty tuples; the spec author never enumerates terms, only declares
bounds wide enough that generator + applicability prune to the right
active set automatically. The bound is the `CoverageBound`:

```
record CoverageBound {
  global_cap         : (max_order : Nat, max_derivative : Derivative)  -- (4, Gradient(1)) for the MVP
  per_mechanism_caps : PersistentMap<MechanismClass, (Nat, Derivative)> -- tighter inner pruning table
}
```

The MVP global cap is `(max_order = 4, max_derivative = Gradient(1))`.
The single driver of `order = 4` is lattice anharmonicity (4-phonon
scattering, significant for diamond/GaN above room temperature); every
other mechanism class fits inside `(2, Gradient(1))`, with a few reaching
`order = 3`. The per-mechanism inner table prunes tuples *before* the
character test so the generator never spends cycles on orders physics
never visits for that mechanism. Both are coverage-policy parameters, not
physical claims.

The principled template set (~15 rows) is the `mechanism_range` table of
§19.10 — which now includes the **piezoelectric acoustic** channel
(`LongRangeStatic(1)`, `1/q` pole) alongside the Fröhlich (`1/q²`) one, the second
long-range e-ph mechanism the polar III-N members carry (`is-polar-material`-gated;
inert for diamond). This **closes `arch-18-open-decisions §7`**.

## 19.10 Mechanism range and polynomial sufficiency

Some couplings are not polynomials of any finite degree in the state
variables: they are functions of the wavevector `q` and/or frequency `ω`
with an *essential* non-polynomial structure — a pole at `q = 0` (the
Fröhlich `1/|q|²` polar-optical coupling) or poles in `ω` (dynamical
screening: the screened Coulomb interaction `W(q,ω)`, the GW self-energy
`Σ(k,ω)`, the TDDFT kernel `f_xc(q,ω)`). For these, the generator's
polynomial basis is correct but **incomplete** — it captures the
short-range part and misses the long-range/dynamical part.

Whether a channel is complete is **not** decidable from
`(pieces, target, order, derivative)` and the symmetry group alone: the
short-range deformation-potential e-ph channel and the long-range
Fröhlich e-ph channel have *identical* signatures. Long-range-ness is a
property of the physical mechanism, so it is carried explicitly:

```
record MechanismRange =
  | ShortRange                          -- analytic / exponentially-localized mediator
  | LongRangeStatic(pole_order : Nat)   -- 1/|q|^p, ω-independent (Fröhlich p = 2, van der Waals, bare-Coulomb head)
  | LongRangeDynamical                  -- frequency-dependent screening: poles in ω (W, Σ, f_xc)
```

`mechanism_range` is curated once per template (the table below). The
flag `polynomial_sufficient` is then a total, O(1) **derived projection**:

```
polynomial_sufficient(c) =
  match c.mechanism_range with
  | ShortRange         => true
  | LongRangeStatic(0) => true            -- a constant "pole" is just a coefficient
  | LongRangeStatic(_) => false
  | LongRangeDynamical => false
```

with the well-formedness invariant enforced by `make-coupling-channel`:
`polynomial_sufficient(c) ⟺ (c.kernel_extension = None)`, and a non-sufficient
channel's `kernel_extension.tag` must match its `mechanism_range`.

`mechanism_range` says "this mechanism is long-range *when active*";
`applicability` (§19.2) independently says "this mechanism is active for
this crystal." They are orthogonal: a Fröhlich channel is long-range by
mechanism yet inert in a non-polar crystal (diamond, zero Born charges)
via `applicability`.

The coverage-policy template table (the ~14 principled channels;
all `ShortRange`/polynomial-sufficient except where noted):

| Channel template | `mechanism_range` | `polynomial_sufficient` |
|---|---|---|
| electron-phonon (deformation-potential, SR) | `ShortRange` | true |
| electron-phonon (Fröhlich polar-optical, LR) | `LongRangeStatic(2)` | **false** |
| electron-phonon (piezoelectric acoustic, LR) | `LongRangeStatic(1)` | **false** |
| spin-orbit | `ShortRange` | true |
| magneto-elastic | `ShortRange` | true |
| minimal coupling / light-matter | `ShortRange` | true |
| phonon-phonon (anharmonic) | `ShortRange` | true |
| radiative damping | `ShortRange` | true |
| exchange / Heisenberg | `ShortRange` | true |
| Zeeman | `ShortRange` | true |
| Stark / electric-dipole | `ShortRange` | true |
| strain-electronic (Bir-Pikus) | `ShortRange` | true |
| screened Coulomb / RPA `W(q,ω)` | `LongRangeDynamical` | **false** |
| GW self-energy `Σ(k,ω)` | `LongRangeDynamical` | **false** |
| TDDFT `f_xc(q,ω)` | `LongRangeDynamical` | **false** |

The frequency-dependent screening channels are not in the diamond MVP
`CouplingSpec`; they are the forcing function for the schema. ALDA
`f_xc` is the degenerate corner of `LongRangeDynamical` (a constant
kernel): tag a channel by its *general* mechanism, not by the cheapest
approximation of it, so swapping ALDA → a tabulated kernel needs no
re-tag.

## 19.11 Extension types — `KernelExt`, `GaugeRule`, `TheoryContext`

**`KernelExt`** carries the non-polynomial part of a long-range coupling.
All four variants share one backbone: a section of a `BZ × ℝ_ω` fiber
bundle valued in a bounded-rank tensor — they differ only in tensor rank,
real-vs-complex value, and whether they are given parametrically or as a
tabulated grid. No new substrate primitive is needed; every field maps
onto the `arch-20-representations §20.1` primitives.

```
record KernelExt {
  tag           : FroehlichLongRange | ScreenedCoulombRPA | GWQuasiparticleSelfEnergy | TDDFTXCKernel
  domain        : MomentumOnly | MomentumFrequency | KpointFrequency | RealSpaceRadial
  value_rank    : Rank0 | Rank2_GG | Rank2_bands | Rank2_cart
  value_field   : RealField | ComplexField
  symmetry_law  : QSymmetryLaw                    -- "K is scalar under the little-group of q" — the bridge to symmetry
  representation : Parametric(KernelParams) | Tabulated(KernelGrid) | Hybrid(KernelParams, KernelGrid)
  provenance    : Optional<ProvenanceLedger>
}
```

`Parametric` kernels (Fröhlich: `ε_∞`, `ε_static`, Born charges `Z*`,
`ω_LO`; LRC `f_xc`: a single `α`) are tiny (< 1 KB). `Tabulated` kernels
(the RPA dielectric matrix, the GW self-energy) can be large: the
full-frequency dense dielectric matrix for diamond (`12³` q-mesh × 64
frequencies × 500 G-vectors, complex) is ≈ **440 GB** worst case,
dropping to ≈ 0.5 GB after a plasmon-pole model + irreducible-BZ
reduction. The grid is a `CacheEligible` sidecar attached by
`Address[TabulatedField]` (`arch-20 §20.6`) — folded into the channel's
identity by address, never by value, so content-addressing stays O(1).
**No MVP channel is tabulated** (the active set is all-polynomial;
Fröhlich for the polar members is `Parametric`); tabulated storage is a
V2 concern, and the 440 GB figure is the number the persistent-storage
tier must be designed against before those channels turn on.

**`GaugeRule`** resolves a residual continuous basis ambiguity (e.g. the
Wannier-gauge / orbital-projection choice for a downfolded channel). It is
`None` for every MVP channel and is recorded only when a P3 gauge-fixing
rule is genuinely attached.

**`TheoryContext`** is the global theory frame on `CouplingSpec` (§19.8).
A coupling constant is meaningful only relative to the simulation that
produced it — a `J_ij` under PBE is a different number than under HSE06 —
so the frame is part of the spec's identity:

```
record TheoryContext {
  xc_functional          : XCFunctionalTag                         -- closed C1 vocabulary (arch-09 §9.7)
  pseudopotential_set    : PersistentMap<AtomicSpecies, PPRecord>  -- closed discriminators; open file id (content-pinned)
  many_body_level        : ManyBodyLevel                            -- closed C1; sub-records for +U / GW / DMFT
  relativistic_treatment : RelativisticTreatment                    -- closed C1
}
```

The four vocabularies are defined in `arch-09-vocabularies §9.7`. The
theory context does **not** enter the `generate-invariants` cache key
(the polynomial basis is symmetry-only; the relativistic treatment's
one effect — spin-orbit — enters through the symmetry group's double
cover, captured by `Address[CrystalSymmetryGroup]`, not here). It does
**not** enter the runtime kernel either: by Stage 4 the theory choice has
already selected the symmetry group and conditioned the coefficient
values, so the lowered kernel is theory-agnostic. `theory_context` is
therefore solely metadata for the cert + provenance layer (§19.7).

The **MVP default theory context** is `GGA(PBE)` / PseudoDojo v0.4.1
norm-conserving (Ga with the `3d` semicore shell promoted to valence) /
`KohnSham` (plain DFT) / `ScalarRelativistic` (no explicit SOC; the MVP
set is non-magnetic with no SOC-dependent observable). PBE's known
underestimate of UWBG band gaps is handled by theory-conditioning the
reference-battery obligation (§19.7), not by upgrading the default;
`Hybrid(HSE06)` is the documented accuracy upgrade for gap-sensitive work.

## 19.12 PSD closure for `PSDSymmForm` channels

A `PSDSymmForm` channel lands as an off-diagonal block of the GENERIC
friction operator `M`, which must be positive-semidefinite so that
entropy production stays non-negative. The invariant generator returns a
basis of `G`-invariant *symmetric* tensors, but membership in that linear
subspace does not by itself guarantee any combination is PSD (a linear
condition vs. a convex-cone condition).

For all three MVP `PSDSymmForm` channels, PSD is **structurally
guaranteed by physics** — it is a documented assumption, not a runtime
search:

```
Assumption [PSD-e-ph]   — electron-phonon dissipation kernel M_{e-ph}
  Origin:    GENERIC M-block axiom + fluctuation-dissipation theorem
             + Fermi-golden-rule Gram structure (sum of squared coupling matrix elements)
  Reference: Öttinger 2005 §5.3 (DOI 10.1002/0471727903); Callen–Welton 1951
             (DOI 10.1103/PhysRev.83.34); Giustino 2017 (DOI 10.1103/RevModPhys.89.015003)
  Closure:   tight (a PSD G-invariant representative provably exists) / loose (learned coefficients not pinned)

Assumption [PSD-ph-ph] — phonon-phonon scattering kernel M_{ph-ph}
  Origin:    GENERIC axiom + Onsager/detailed-balance + FDT
  Reference: Öttinger 2005 §5.3; De Groot & Mazur Ch. IV (ISBN 978-0-486-64741-8);
             Maradudin & Fein 1962 (DOI 10.1103/PhysRev.128.2589)
  Closure:   tight / loose

Assumption [PSD-rad]    — radiative damping kernel M_{rad}
  Origin:    GENERIC axiom + Lindblad/GKSL completely-positive structure (rate Γ ≥ 0); FDT root
  Reference: Öttinger 2005 §5.3; Breuer & Petruccione 2002 Ch. 3 (ISBN 978-0-19-852063-4);
             Jackson 1998 §17.2
  Closure:   tight / loose (trivial sign check when the invariant basis has dimension 1)
```

The closure is **tight at the operator level** — a PSD `G`-invariant
representative provably exists (the Reynolds image of a PSD seed is PSD),
so the positivity obligation (§19.7) never runs a semidefinite-feasibility
search for these channels; feasibility is a theorem, recorded as the
assumption above. The closure is **loose at the coefficient level** — the
PINO learns the basis coefficients and could transiently leave the PSD
cone during training — so the positivity obligation **keeps** a cheap
per-evaluation guard `λ_min(M_block) ≥ −δ_PSD` on the assembled per-mechanism
super-block (`arch-12 §12.0.1` obligation 2; tolerances valued in `arch-12 §12.0.2`).

**Dormant SDP fallback (V2).** A future `PSDSymmForm` channel with no
structural PSD guarantee would, at registration, solve the semidefinite
feasibility program "find `c` with `Σ c_i B_i ⪰ 0`" (interior-point,
`O(dim^{3.5})`, microseconds-to-milliseconds at registration only;
block-diagonalizable along the irrep decomposition per Gatermann–Parrilo
2004, DOI 10.1016/j.jpaa.2003.12.011); infeasibility rejects the channel.
No MVP channel needs it; it is specified for forward-compatibility only.

---


<a id="arch-20-representations"></a>

# Representation substrate

Every load-bearing object in `/physics` — vocabularies, registered
generators, selected subsets, sparse coverage masks, sidecars, evidence,
symbolic forms, applicability predicates, the physics graph itself — is
expressed as a fiber of **one substrate** parameterized by typed indexed
universes, content-addressed Merkle DAGs, and a small family of op
signatures. This file is the keystone for that substrate.

The substrate is **a contract, not a single dynamic container**. Each
cluster keeps the backend that wins on its hot path; the substrate
unifies their identity, serialization, and attachment disciplines.

## 20.1 Substrate primitives

Five primitives. Every other representation is a fiber over them.

```
Address[D] = Hash(domain_separator(D), schema_version(D), canonical_node_bytes)

Universe[U] = {
  id              : Address[Universe],
  carrier_kind    : Closed | Open | Derived,
  element_type    : TypeId,
  enumerator?     : (Universe[U]) → Iterator<Element[U]>,
  ordinal_policy  : DenseU32 | DenseU64 | None,
  schema_version  : Nat,
  backend_policy  : (density_estimate) → BackendChoice
}

SparseSet[U] = {
  universe : Universe[U],
  backend  : Tuple | Bitset | Roaring | HAMT | RankSelect,
  root     : Address[Set[U]],
  members  : (backend-specific canonical layout)
}

PersistentMap[K, V] = {
  key_universe?  : Universe[K],
  value_domain   : DomainId,
  backend        : HAMT(branching=32) | MerkleTrie,
  root           : Address[Map[K, V]]
}

MerkleDAG[S, L] = {
  domain         : DomainId,
  signature      : S,                       -- op-signature parameter
  leaf_type      : L,
  node_store     : Map<Address, Node[S, L]>,
  root           : Address[DAG[S, L]]
}

Node[S, L] = Leaf(L) | Op(op : S.Op, attrs : S.Attrs[op], children : S.Arities[op])
```

`Address[D]` is **domain-separated**. Two values from different domains
never collide even with identical canonical bytes. Default digest is
SHA-256 truncated nowhere in storage; truncation is allowed only in log
output.

## 20.2 The parametric op-signature family

Four op signatures parameterize the Merkle DAG instances in `/physics` (a fourth,
`GroupOps`, is added below). Three cover the general expression DAGs:

- **`PredicateOps`** — ROBDD reduced ordered Boolean ops over typed
  parameterized atoms drawn from a C1 vocabulary. Atom order is part of
  the predicate-vocabulary version. Used by `arch-13-applicability`.
- **`SymbolicTensorOps`** — colored-operad / free symmetric monoidal
  category generated by the target shapes of `arch-19-coupling-structure
  §19.1` (`Scalar`, `AntisymmForm`, `PSDSymmForm`) plus tensor product,
  contraction, derivative, group action, projection, and binding.
  Composition is operadic substitution. Used by `InvariantTerm` and
  `FormulaApply`.
- **`EvidenceOps`** — attestation, aggregation (semilattice meet),
  reference linkage, trajectory chunk. Used by `arch-12-cert`.

A fourth signature, **`GroupOps`** (multiplication, inversion,
restriction, antipode/TR-twist, character, projector), describes the
finite-quotient algebra of `CrystalSymmetryGroup`. Its derived outputs
(irrep tables, Fourier projectors, BZ stalks) are stored as ordinary
substrate fibers.

## 20.3 Per-cluster representation table

| Cluster | Shape | Backend / signature |
|---|---|---|
| C1 vocabularies (`StateComponent`, `SubDofTag`, `IrrepLabel`, `OutputRole`, `NodeKind`, `InputKind`, `CategoryTag`, `AxisLabel`, `BundleId`, `RegimeTag`) | `Universe[T]` instances with dense ordinals | Closed = `DenseU32`; Open = `DenseU64` with append-only registry |
| C2 registered generators (`FormulaRecord`, `ResidualGenerator`, `CouplingChannel`) | `Element[RegistryUniverse[k]]` | Kind-indexed dispatch; payload canonicalized by C5 rule |
| C5 content addressing (`ContentAddress`, `ResidualKey`, `generator-hash`, cache keys, sidecar fingerprints) | `Address[D]` | SHA-256, domain-separated |
| C6 selected subsets (`CouplingSpec`, active-residual / formula / bundle subsets) | `SparseSet[RegistryUniverse]` in Boolean lattice | HAMT / Roaring; subset identity = root |
| C7 sparse masks (`RoaringCoverageMask`, axis sets, subgraph node sets, irrep-block indices) | `SparseSet[Universe]` | Density-derived per universe |
| C3 sidecars (Stage 1 / 2 / 2.5 / 4 sidecars) | `PersistentMap[TypedKey, EvidenceBearing[V]]` | HAMT, branching 32; stage-visible |
| C4 evidence (`Witness`, `OneShotCert`, `IterativeResult`, ten obligation outputs) | `MerkleDAG[EvidenceOps, EvidencePayload]` | Persistent attestation DAG |
| `InvariantTerm` / `FormulaApply` symbolic form | `MerkleDAG[SymbolicTensorOps, TypedLeaf]` | Hash-consed tensor-algebra DAG |
| Applicability predicates | `MerkleDAG[PredicateOps, C1Atom]` | Versioned ROBDD over C1 atoms |
| `CrystalSymmetryGroup` | Graded composite atlas (sui generis) + `MerkleDAG[GroupOps, …]` derived caches | See `arch-09-vocabularies §9.5` |
| `PhysicsGraph` | Closure of output `Address[Node]` set under children-pointers | Identity is the multiset of output-root addresses |

## 20.4 Canonical serialization rule

One rule, used everywhere `Address[D]` is computed:

1. **Domain separator first.** `domain_separator(D)` is a fixed 16-byte
   tag for `D ∈ {Element, Set, Map, DAG.Predicate, DAG.SymbolicTensor,
   DAG.Evidence, GraphNode, ReferenceRow, GroupAtlas, …}`.
2. **Schema version next.** A `u32` declared in the universe descriptor
   for `D`; bumped on incompatible changes.
3. **Records.** Named fields lexicographically sorted by field name;
   each field serialized as `name_bytes ‖ length-prefixed value bytes`.
4. **Sequences.** Length-prefixed by `u64` element count; elements in
   declared order.
5. **Sets.** Elements canonicalized individually, sorted by address
   bytes, then length-prefixed and concatenated.
6. **Maps.** Entries canonicalized as `(key_bytes, value_bytes)`,
   sorted by key bytes, length-prefixed.
7. **Sum types.** Discriminator drawn from the C1 vocabulary indexing
   the sum; serialized as `u32 ordinal ‖ length-prefixed payload`.
8. **Continuous-factor data.** U(1) charge sectors serialize as signed
   integer lattice weights with a basis-id tag. SU(2) sectors serialize
   as doubled spin labels (`2j : Nat`) plus the Clebsch–Gordan
   table-version `Address`.
9. **Group action laws.** Normalized homomorphism / twist generators
   over layer ids; relation rows sorted by `(domain, codomain, action_label)`.
10. **Optional values.** `None` serializes as a single `0x00` byte; `Some(v)`
    as `0x01 ‖ length-prefixed value bytes`. The two are never confusable with
    an empty-but-present value, so a present-with-no-data field and an absent
    field hash distinctly. (Used by `kernel_extension`, `gauge_rule`,
    `provenance`, and every `T?` field in `arch-19-coupling-structure`.)
11. **Scalar leaves.** `Nat` / `Int` serialize as fixed-width big-endian
    (`u64` / `i64`); `Float` as IEEE-754 `binary64` big-endian with two
    normalizations applied first — every `NaN` maps to one canonical
    quiet-NaN bit pattern, and `-0.0` maps to `+0.0` — so numerically equal
    values always share an address. (Rule 8 covers only U(1)/SU(2) sector
    weights; arbitrary model floats such as `pole_order`, `exx_fraction`,
    `alpha`, `g_cutoff` use this rule.)

`SqliteReferenceCache` (`arch-12-cert §12.1`) and the residual cache
(`impl-07-residual-factory`) both consume this rule unchanged.

## 20.5 Hot-path commitments

No hot path is worse than `O(log n)`. No hot path requires a solver
call. No hot path requires duplicate serialization.

| Op | Asymptotic | Constant factor |
|---|---|---|
| `Address` equality | `O(1)` | one 32-byte compare |
| `Universe` member equality | `O(1)` | one machine-word compare on dense handle |
| `SparseSet` membership (Roaring) | `O(log n)` | container probe |
| `SparseSet` membership (HAMT) | `O(log₃₂ n)` | path walk |
| `SparseSet` membership (tuple, n ≤ 8) | `O(n)` | linear scan, no indirection |
| `PersistentMap` lookup | `O(log₃₂ n)` | one HAMT walk |
| `PersistentMap` insert at stage exit | `O(log₃₂ n)` | path copy |
| `MerkleDAG` root equality | `O(1)` | one address compare |
| `MerkleDAG` diff | `O(changed frontier)` | skip equal subtrees on address compare |
| ROBDD evaluate | `O(decision-path length)` | three-pointer fetch per node |
| ROBDD equivalence / subsumption | `O(1)` after canonicalization | memoized apply |
| `EvidenceOps` aggregate verdict | `O(children)` | semilattice meet, early exit on `Failed` |
| Group element multiplication | `O(1)` average | Schreier–Sims product table |
| Symmetry projector evaluation | `O(|G|/|H| · tensor rank)` | cached as `Address` after first eval |

Backend selection thresholds for `SparseSet`:

- `n ≤ 8` → sorted tuple (free-monoid backend, no allocation cost).
- Dense `n ≤ 256` of a small closed universe → bitset.
- Sparse over a large universe → Roaring.
- Persistent + diffable → HAMT or Merkle trie.

Universe descriptors carry the threshold ladder; the choice is a
property of the universe, not of an individual sparse set.

## 20.6 What the substrate replaces

- **Per-cluster identity disciplines.** `ContentAddress`, `ResidualKey`,
  `generator-hash`, residual cache keys, sidecar fingerprints, and
  reference-row keys are all `Address[D]`. There is one canonical
  serialization rule (§20.4), not per-cluster conventions.
- **Ad-hoc sidecar storage.** Sidecars are typed `PersistentMap`
  fibers; cross-stage visibility is the stage poset
  `1 < 2 < 2.5 < 3 < 4 < 5`; cache eligibility is a per-domain flag
  (`Ephemeral | AuditOnly | CacheEligible`). Evidence is **attached** by
  `EvidenceId`, never duplicated into a sidecar payload.
- **Three separate Merkle infrastructures.** `InvariantTerm` symbolic
  forms, applicability ROBDDs, and the evidence attestation DAG share
  one `MerkleDAG[S, L]` substrate, each with its own op signature (three of the
  four of §20.2; `GroupOps` is the group-algebra fourth).
- **PhysicsGraph as a special object.** The graph is the closure of its
  output addresses under children-pointers. Edges are not separately
  identified; argument-list addresses inside the node payload are the
  edges. `NodeKind` is a closed C1 vocabulary that indexes the typed
  payload sum — this is the substrate's primary closed-polymorphism
  mechanism.

## 20.7 What the substrate does not replace

- `CrystalSymmetryGroup` remains sui generis at the algebra layer.
  Its **identity** is an `Address[GroupAtlas]`; its **derived outputs**
  are substrate fibers; its **multiplication / projector / restriction
  semantics** are not reduced to the substrate. Hopf-algebra and
  Fourier views are derived view layers over the
  `CrystalSymmetryGroup` defined in `arch-09-vocabularies §9.5`.
- Cert checkers are typed registered morphisms from artifacts to
  evidence; they are **not** ROBDDs over typeclass-tag atoms.
  Applicability predicates are first-order decidable; cert checkers
  evaluate full GENERIC artifacts. Both register through C2; the split
  is preserved.
- The colored-operad / free-symmetric-monoidal-category structure on
  `SymbolicTensorOps` is the algebraic explanation of the op signature;
  the storage carrier is the hash-consed Merkle DAG.

## 20.8 Relationship to existing files

Each of the following retains its canonical authority over its own
concept; arch-20 only specifies the **shape** the concept inhabits.

- `arch-04-state` — `StateComponent` is a closed C1 vocabulary.
- `arch-06-physics-graph` — node identity is `Address[GraphNode]`;
  `NodeKind` is the closed C1 discriminator for the typed payload sum.
- `arch-07-pipeline` — pipeline stages form the visibility poset for
  sidecars; Stage 2.5 outputs are `MerkleDAG[SymbolicTensorOps, …]`
  roots.
- `arch-09-vocabularies` — vocabularies (`IrrepLabel`, `BundleId`,
  `CategoryTag`, …) are `Universe[T]` instances; `IrrepLabel` identity
  is `(Address[GroupAtlas-context], local-irrep-name)`.
- `arch-10-typeclasses` — typeclass-tag atoms used by predicates are
  parameterized C1 atoms registered through the same vocabulary
  machinery.
- `arch-11-residuals` — `ResidualKey`, `CategoryTag`, `BundleId`,
  `AxisLabel` are substrate-typed; `ContributionFacets` is a sidecar
  value, not part of identity.
- `arch-12-cert` — evidence is `MerkleDAG[EvidenceOps, …]`;
  `SqliteReferenceCache` consumes the canonical-serialization rule of
  §20.4.
- `arch-13-applicability` — applicability is
  `MerkleDAG[PredicateOps, C1Atom]` with versioned atom order.
- `arch-19-coupling-structure` — `CouplingChannel` is a registered
  generator (C2 element); `CouplingSpec` is `SparseSet[CouplingRegistry]`;
  `InvariantTerm.symbolic-form` is the hash-consed
  `MerkleDAG[SymbolicTensorOps, …]` root.
- `impl-07-residual-factory` — residual cache keys, dressing-cert
  schemas, and trajectory storage all use the substrate primitives.

## 20.9 Versioning discipline

Every universe and every domain carries a `schema_version : Nat`.
Incompatible changes bump the version. Old `Address` values remain
valid identifiers of the old schema; they are not silently reinterpreted.
Migration between schema versions is an explicit registered morphism,
never an implicit decode-with-new-rules.

ROBDD predicate atom orders are likewise versioned per predicate
vocabulary. Adding a new atom creates a new order id; old predicate
roots remain comparable only under their original order, with explicit
re-canonicalization at migration boundaries.

---


<a id="arch-21-multiscale-state"></a>

# Multiscale state — slow and macro tiers

## 21.0 The emergence-axiom correction

`arch-04-state` lists *defect populations* and *distributions* among quantities that are
"emergent — coarse-grainings of `x(t)`" and therefore forbidden from the state, justified by a
constraint-manifold / integration pathology. That classification is too strong: it
contradicts `arch-08-bo-levels:47` ("each level introduces its own irreducible state; L4 =
distributions over phase space"), and it forbids exactly the physics the project exists to
predict — aging and device-scale operation.

**Refined emergence axiom.** A quantity `y` is *emergent* (excluded from a tier's state) **iff**
it is recoverable from that tier's state by coarse-graining **on the same timescale and the
same scale**. Phonon occupations `n_{q,s}`, the carrier distribution `f_n(k,r)`, and
electron/lattice temperatures are emergent at the micro timescale — they fast-equilibrate to a
function of the micro 7-tuple within the micro relaxation time. Two classes of quantity are
**not** so recoverable and are therefore first-class state in their own tier:

- **Slow / history-dependent** (different *timescale*): defect-population concentrations,
  charge-state distributions, H content, oxidation/carbide fronts — at the micro timescale they
  are *frozen* (they evolve over hours–years, set by Arrhenius barriers of 2–7 eV) and carry the
  integrated thermal/irradiation history (`defects-surfaces-interfaces.md:54`:
  "treat `[V_C]` as a state variable … evolving by generation–annihilation kinetics, not an
  equilibrium quantity"; `csp-heterostructure.md:206` E.1 requires distinguishing equilibrium
  from frozen-in populations — meaningful only if frozen-in is stored).
- **Homogenized / device-scale** (different *scale*): the continuum fields `T_L(r), φ(r),
  n(r), p(r), j(r)` on a device mesh — not derivable from a single unit cell.

Because the added tiers are independent **by timescale or by scale**, they create **no algebraic
constraint** with the micro 7-tuple — they evolve on their own clean flow, coupled only
parametrically (adiabatic driving / homogenization). The constraint-manifold pathology
`arch-04` feared arises only for quantities redundant on the *same* timescale and scale, which
stay emergent (the full distribution is never promoted). The micro axiom holds verbatim; this
document adds the two tiers and reconciles `arch-04` ⊥ `arch-08`.

## 21.1 The three tiers

| Tier | Members | Equilibration timescale / scale | Index geometry | Dynamics |
|---|---|---|---|---|
| **Micro** | the 7-tuple `(h, R_I, P_I, Π_h, Z_I, γ̂, A)` (`arch-04-state`), **unchanged** | fs–ns, unit cell | continuous BZ × cell | full GENERIC `L+M` |
| **Slow / configurational** | defect concentrations `[D]^q`, `[H]`, `x_ox`, `x_carbide`, `ρ_dis` | hours–years, unit cell→mesh | discrete species × sites | ODE / master-equation |
| **Macro / continuum** | `T_L(r), φ(r), n(r), p(r), j(r)` on a device mesh | device scale | fields on real-space cells | parabolic + constraint PDEs |

The slow and macro tiers are **adiabatic parameters** of the micro tier: the micro 7-tuple
fast-equilibrates at fixed slow/macro state under `Environment`; the slow/macro state then
drifts under *time-averaged* micro quantities `⟨micro⟩_τ` (slow, §21.5) or under
*homogenized coefficients* the micro tier supplies (macro, §21.8). In `arch-08-bo-levels`
terms: the slow tier is a configurational layer above L4; the macro tier is **L4's spatial
fluid-limit reduction** (the drift-diffusion / Poisson system as the BTE fluid limit,
`group-C…md:92-104`) lifted from one cell to a device mesh — which is the "irreducible state"
`arch-08:47` already attributes to L4. `/physics` **scores** each tier's law-violation; the PINO
supplies each tier's trajectory (score-not-solve, `arch-16-pino-bridge`, preserved at every
scale). No new computational *method* is introduced: the slow tier reuses `kinetic-evolution`
(`arch-09 §9.1`); the macro tier reuses the device-PDE residual pattern (row 71).

---

## 21.2 The slow / configurational tier — state schema

### 21.2.1 The `DefectSpecies` universe (C1)

A closed C1 vocabulary `DefectSpecies` as a `Universe[T]` instance (`arch-20 §20.1, §20.3`;
`carrier_kind = Closed`, `ordinal_policy = DenseU32`). Its enumerator is the per-host native
defect inventory of `defects-surfaces-interfaces.md:9–18` (Part A.1):

| Host | `DefectSpecies` members | charge states `q` |
|---|---|---|
| Diamond (C) | `V_C`(GR1), `C_i`(split-⟨100⟩), `V2`, `N_s`, `NV`, `NVN`(H3), `N3V`, `N2A`, `platelet` | `V_C∈{+,0,−}`, `NV∈{+,0,−}` |
| c-BN | `V_B`, `V_N`, `B_i`, `N_i`, `B_N`, `N_B`, `V_B–O` | `V_N` donor-like |
| AlN | `V_Al`, `V_N`, `O_N`, `Al_i`, `V_Al–O`, `V_Al–nC_N` | `V_Al∈{0,−,2−,3−}`, `V_N∈{0,+}` |
| GaN | `V_Ga`, `V_N`, `N_i`, `Ga_i`, `V_Ga–O_N`, `V_Ga–nH` | `V_Ga∈{0,−,2−,3−}`, `V_N∈{0,+}` |
| β-Ga₂O₃ | `V_O(I/II/III)`, `V_Ga(1/2)`, `Ga_i`, `V_Ga–Ga_i–V_Ga`, `V_O–H`, `V_Ga–nH` | `V_O` deep |

Element type carries the Part-A.2 record `{name, site : LatticeSite, charge_states : List[Int],
spin}` (`defects…md:24–27`). Adding a member is a versioned `schema_version` bump
(`arch-20 §20.9`), exactly like the theory-context vocabularies (`arch-09 §9.7`).

### 21.2.2 The slow-state value (fiber over `DefectSpecies`)

The slow-state `s` is a typed fiber — cluster **C3** (`PersistentMap[TypedKey, V]`, HAMT
branching 32, stage-visible; `arch-20 §20.3`), **not** part of `ResidualKey` identity:

| Field | Type / units | Index | Source |
|---|---|---|---|
| `conc[D,q]` ≔ `[D]^q` | `Concentration` (cm⁻³) ≥ 0 | `DefectSpecies × ChargeState` | A.3 `defects…md:38–48` |
| `charge_dist[D]` ≔ `{f_q}` | `Simplex` over `q`, `Σ_q f_q = 1` | `DefectSpecies → Simplex` | A.3 `defects…md:44–48` |
| `H_content` ≔ `[H]` | `Concentration` (cm⁻³) ≥ 0 | scalar / region | G.2 `defects…md:408–421` |
| `oxide_front` ≔ `x_ox` | `Length` (nm) ≥ 0 | scalar / facet | #46 `catalog…md:147` |
| `carbide_thickness` ≔ `x_carbide` | `Length` (nm) ≥ 0 | `MetalContact` | F.5 `defects…md:364–376` |
| `dislocation_density` ≔ `ρ_dis` | `Length⁻²` (cm⁻²) ≥ 0 | scalar / region | G.7 `defects…md:460–468` |

`ChargeState` reuses the existing `SubDofTag = charge` already allowed on `Z_I`
(`arch-09 §9.6`); `charge_dist[D]` is its dynamic refinement.

**Relation to `SiteDecoration.occupancy` and `Z_I` (decision).** The slow fiber is a **new C3
fiber that is the dynamic promotion of `SiteDecoration.occupancy`**, **not** a mutation of `Z_I`:
(1) `Z_I` stays immutable (`arch-04-state:26`); atomic-number identity does not change as a
vacancy forms. (2) `occupancy` is the right physical quantity (a vacancy is `occupancy→0`); the
static `SiteDecoration.occupancy` becomes the **initial condition** `s(t=0)` (the as-synthesized
/ frozen-in population). (3) Tier hygiene: as a separate adiabatic-parameter fiber at a different
timescale, it ties **no** constraint manifold back to `(h, R_I, …)` — the condition the original
no-emergent-state rule was protecting, now satisfied honestly. The slow fiber drives bundle
**B11 (degradation)** residuals with defect-resolved sub-outputs in **B4**.

## 21.3 Slow-kinetic formulas (Part-G / Part-H → registry)

Every process is a new `FormulaRecord`; all Arrhenius rates use `rate = ν₀·exp(−E_a/kT)`
(`defects…md:392`); each names the `kinetic-evolution` sub-method it instantiates. CSV rows in
§21.13. **No new method or sub-method is introduced.**

- **F-G1 `vacancy-generation-arrhenius`** — `([V]^q,T,μ,j,x_ox',ρ_dis,k_ann) → d[V]^q/dt`
  (cm⁻³s⁻¹), `defects…md:399–406`:
  `d[V]/dt = G_total − [V]·k_ann`, `G_total = G_thermal + G_irradiation + G_interface`;
  `G_thermal = ν₀ exp(−E_form^V/kT)·N_site`; `G_interface = ξ_int·(dx_ox/dt + dx_carbide/dt)·N_site,int`;
  `G_irradiation` from F-H2; `k_ann = ν₀ exp(−E_migr^V/kT)`. Diamond `V_C`: `E_form≈7.2 eV`
  (HSE06), so `G_thermal(773 K)` is negligible — **the 500 °C generation budget is dominated by
  `G_interface` + `G_irradiation`**. Annihilation barriers (`defects…md:58–66`): `V_C^0` 2.3 eV,
  `V_C^−` 2.8 eV, `C_i` 1.6–1.7 eV, `V_N(GaN)` 2.6 eV, `V_Ga(GaN)` 1.9 eV, `V_O(Ga₂O₃)` 1.9–2.4 eV,
  `V_Al(AlN)` 3.4 eV. T0/D1; sub-method `master-equation`; B11/B4.
- **F-G2 `hydrogen-redistribution-drift-diffusion`** — `([H](r),T,E,μ_drift) → ∂[H]/∂t`,
  `defects…md:410–412`: `∂C/∂t = ∇·(D(T)∇C) − ∇·(μ_drift C E)`, `D(T)=D₀exp(−E_diff/kT)`. Diamond
  H interstitial `E_diff=1.7 eV`, `D(500 °C)≈1e−13 cm²/s` (~1 mm profile shift in 1000 h). T3/D3;
  `drift-diffusion`; B11/B5.
- **F-G3 `platelet-nucleation-allen-cahn`** — `([platelet],[N_s],T) → d[platelet]/dt`,
  `defects…md:425–428`: `k_nuc[N_s]² − k_dis[platelet]`, `k_nuc=ν₀exp(−E_nuc/kT)`, `E_nuc≈3.5 eV`.
  Half-life `N_s→N₂A` ≈ years@500 °C, hours@1000 °C. T1/D2; `Allen-Cahn`; B11/B4.
- **F-G4 `vibration-induced-vacancy-generation`** — `(ρ_dis,σ_stress,f_vib,v_dis,b) →
  (dρ_dis/dt, G_V)`, `defects…md:462–468`: `dρ_dis/dt = κ_vib(σ_stress/σ_yield)^m f_vib`, `m≈4–6`;
  `G_V = ξ·ρ_dis·v_dis·b`. T1/D1; `master-equation`; B11; `G_V` feeds F-G1's source.
- **F-F5 `carbide-growth-parabolic`** — **exists (row 81)**; re-tagged so its output `x_carbide`
  is a slow-state field. `x_carbide=√(2 k_carb(T) t)`, `k_carb=k₀exp(−E_carb/kT)`
  (`defects…md:367–369`): Ti 1.4 eV (~600 nm/1000 h@500 °C, severe), W 2.4 eV (~3 nm), Mo 2.1 eV
  (~15 nm), Pt none. `master-equation` front-advance `dx/dt = k_carb/x`. B11/B6.
- **F-46 `air-oxidation-rate-eyring`** — `(T,p_O2,ΔG‡,ν) → dx_ox/dt`, `catalog…md:147` (#46):
  `r_ox = ν·exp(−ΔG‡/kT)` (Eyring; cheap = Arrhenius). Diamond onset **>600 °C, "the lifetime
  limiter"**; accuracy factor ~3. T0/D1; `master-equation`; B11/B5. *(Research-flagged: #46 marked
  "OUTSIDE registry unless reaction-rate template present"; satisfied by `kinetic-evolution`.)*
- **F-47 `hydrogen-desorption-rate-eyring`** — `(T,E_des,ν) → r_H`, `catalog…md:148` (#47):
  `r_H = ν·exp(−E_des/kT)`, `E_des≈3.8 eV` (H–C bond). Drives the irreversible χ shift
  (NEA→PEA); desorbs 700–900 °C; accuracy factor ~2. T0/D1; `master-equation`; B11/B5.
- **F-H1 `nrt-displacements`** — `(T_dam,E_d) → N_d`, `non-eq…md:367` (H.1):
  `N_d = 0.8·T_dam/(2·E_d)`. `E_d`: diamond ~37–50 eV, GaN ~20 eV, Ga₂O₃ ~25 eV, AlN ~35 eV.
  T0/D1; `algebraic-of`; B11/B4; feeds F-H2.
- **F-H2 `frenkel-pair-yield`** — `(N_d,Σ_d,Φ_dose,η_recomb) → DefectDensity`, `non-eq…md:371`:
  `[V]_irr = Φ_dose·Σ_d·N_d·(1−η_recomb)` (cm⁻³), where the **macroscopic displacement cross-section**
  `Σ_d = N_atom·σ_d` (cm⁻¹) supplies the missing length⁻¹ so the product of `N_d` (displacements
  per PKA, dimensionless), `Σ_d` (cm⁻¹) and the fluence `Φ_dose` (cm⁻²) is a `Concentration`
  (cm⁻³) — without `Σ_d` the bare `N_d·(1−η)·Φ_dose` is cm⁻² (a fluence), not a density. `σ_d` is
  the per-`(host, particle-type, energy)` NIEL-derived displacement cross-section, one curated
  `ProvenanceLedger` coefficient (`arch-19-coupling-structure §19.8`). T0/D1; `master-equation`;
  B11/B4; this is `G_irradiation` of F-G1. *(Research-flagged: `non-eq…md:361`/`catalog…md:232`
  mark full cascade dynamics out-of-scope; `η_recomb(T_L)` and `σ_d` have **no closed form in the
  corpus** — only the coupling structure + the curated-coefficient slot are specified, not
  invented.)*

---

## 21.4 The `EOM/DefectPopulation` residual

The slow tier earns an EOM-violation residual category, `EOM/DefectPopulation` — the slow-tier
sibling of the seven micro `EOM/x_i` (`arch-11 §11.1`):

```
EOM/DefectPopulation[D,q,site] = ‖ d[D]^q/dt|_predicted − ( G^q_total[D] − [D]^q·k_ann^q[D] ) ‖²
```

the slow-tier specialization of `‖dx_i/dt − (L δE/δx_i + M δS/δx_i)‖²` (generation = dissipative
`M δS` branch; annihilation = restoring `L δE` branch toward `[D]_eq`). Each slow field
substitutes its §21.3 RHS (`[H]`→F-G2; `x_ox`→F-46; `x_carbide`→F-F5; `ρ_dis`→F-G4). **Axes**
`(DefectSpecies, ChargeState, SiteClass)` (+ spatial bin for field-valued `[H]`/`x_ox`); one
weightable `ResidualLeaf` per `(species, charge, site)` (`arch-11 §11.2–§11.3`), no
preaggregation. `ResidualKey = (Method(kinetic-evolution), axes)`; facets `(EOM/DefectPopulation,
B11, bare)`. The PINO predicts the aging trajectory `{s(t_0),s(t_1),…}`; `/physics` scores the
finite-difference `ds/dt` against the §21.3 RHS at each step — a consistent aging curve drives
the residual → 0. This is `csp…md:195` `R_ThermalCycleStability`'s population-drift residual
promoted to first-class. Curriculum: **Refine** `[0.10, 0.60)` with the other `EOM/*`.

## 21.5 The adiabatic driving contract (slow ← ⟨micro⟩)

Each slow rate is parameterized by **time-averaged** micro quantities `⟨·⟩_τ`:

| Slow rate | Driven by `⟨micro⟩_τ` | Cite |
|---|---|---|
| `G_irradiation` (F-G1, F-H2) | carrier/ion flux `⟨j⟩` | `defects…md:403–406` |
| all Arrhenius rates | lattice temperature `⟨T_L⟩` in every `exp(−E_a/kT)` | `defects…md:392`; self-heating from micro |
| `G_interface` (F-G1) | oxidation/carbide front velocity `dx_ox/dt`, `dx_carbide/dt` | `defects…md:404` |
| `G_V` (F-G4)→F-G1 | dislocation density/velocity `⟨ρ_dis⟩`, `v_dis` | `defects…md:467` |
| `[H]` drift (F-G2) | internal field `⟨E⟩` | `defects…md:412` |

```
d s/dt = Φ_kinetic( s ; ⟨T_L⟩_τ, ⟨j⟩_τ, ⟨E⟩_τ, ⟨ρ_dis⟩_τ, dx_ox/dt, dx_carbide/dt ; Environment )
```

The reverse coupling (slow → micro) is the adiabatic-parameter dependence: micro
`E_form^q(E_F(T))`, trap density `N_T = [D]`, χ(T,t), and gap/mobility read the *current* `s` as
a fixed parameter — the `SelfConsistentChargeBalanceOf` closure (`arch-09 §9.2`) consuming the
slow defect list (SRH `τ_n = 1/(σ_n v_th N_T)`, `defects…md:201,248`).

---

## 21.6 The macro / continuum tier — state schema

### 21.6.1 The device-mesh `Universe`

`DeviceMesh : Universe[MeshCell]` — a closed C7 universe over real-space cells (`arch-20 §20.3`):
`carrier_kind = Closed`, `ordinal_policy = DenseU32`, `enumerator = enumerate(product(mesh-axes))`
(`arch-16 §16.2.1` form), `backend_policy = Roaring | Bitset`. Each `MeshCell` carries
`(centroid r_c, volume V_c, face-list)`. Macro fields are fibers over it —
`PersistentMap[MeshCell, FieldValue]` (C3, HAMT-32) — so snapshots differing in one subdomain
share unchanged cells by address (`MerkleDAG diff = O(changed frontier)`).

**Discretization (finite-volume).** Each balance PDE is read in integral conservation form
`∂_t ∫_c φ dV + Σ_f Flux_f·A_f = ∫_c Source dV`, with face fluxes from the homogenized
coefficients (§21.8). The mesh is **conservative** (face flux out of `c` = flux into its
neighbor) so the `Conservation` residual (`arch-11 §11.1` cat. 9) holds discretely.

**Relation to `arch-18 §2`.** The macro tier **subsumes and narrows** the deferred "PDE-mesh
format + adjoint library": the *mesh format* is now committed (a `DeviceMesh` finite-volume
universe, fields as fibers, conservative fluxes — a substrate fiber, not a new container). What
remains open is only the *mesh-adjoint scheme* (discrete- vs continuous-adjoint of the
finite-volume operator), which reuses the Stage-4→Stage-5 AD seam — flagged in §21.15.

### 21.6.2 The field set (inclusions / exclusions)

```
MacroState = ( T_L : Field[DeviceMesh → ℝ₊]   [K],   φ : Field[DeviceMesh → ℝ]   [V],
               n,p : Field[DeviceMesh → ℝ₊]   [m⁻³], j : Field[DeviceMesh → ℝ³] [A·m⁻²] )
```

- `T_L(r)` — macro state (the spatial coarse-graining of the micro `S_vib` per-cell value onto
  the device profile; `non-eq…md:517,194`).
- `φ(r)` — macro state, **Poisson-constrained** `∇·(ε∇φ)=−ρ` (carried so the constraint is
  *scored*, not free; `group-C…md:116`).
- `n(r), p(r)` — macro state; the **0th moments** of `f_n` over a device cell (densities, not the
  distribution; `group-C…md:96–100,161`).
- `j(r)` — macro state via a **closed-form 1st-moment closure** (§21.7.2); carried so
  current-continuity `∇·j + ∂ρ/∂t = 0` is a scorable balance.

**Kept emergent (never promoted):** `f_n(k,r)` (promotion double-counts its moments → DAE);
`T_e(r)` (2nd moment, closed form §21.7.1); `E(r) = −∇φ` (quasi-static); all transport
coefficients `κ,σ,μ,α` (supplied by §21.8). The load-bearing distinction: `(T_L,φ,n,p,j)` are a
new **scale** (device-mesh fibers), **not** a new **distribution**.

## 21.7 Moment closures (keeping the distribution emergent)

### 21.7.1 Energy closure — `T_e` (2nd moment)

Two-temperature energy balance (`non-eq…md:258–273`): steady state `T_e − T_L =
(2/3)(j·E)τ_E/(n k_B)`; transient `(3/2)n k_B ∂_t T_e = j·E − (3/2)n k_B (T_e−T_L)/τ_E`. `τ_E`
per-composition: `tau-energy-pop(ℏω_LO,T_L)` (polar) / `tau-energy-acoustic(v_s,m*,T_L)`
(diamond). `T_e` is **never state** — reconstructed from `(n,j,T_L)` + supplied `τ_E`
(`non-eq…md:295–296`). Validity: Ohmic `≲10⁴ V/cm` (`T_e≈T_L`); warm `10⁴–10⁵`; hot `10⁵–10⁶`
(needs §21.7.2 for `μ(E)` collapse); saturated `≳ few×10⁵` (`j≈qnv_sat`). Positivity bound
`T_e ≥ T_L` scored as a `Positivity` residual (`non-eq…md:491`).

### 21.7.2 Momentum closure — `j` (1st moment)

Drift-diffusion `j = qμ(E,T)nE − qD∇n` (holes: sign-flip), Einstein `D = μk_BT/q`
(`group-C…md:98,103`); field-dependent mobility Caughey–Thomas `μ(E)=μ₀[1+(μ₀E/v_sat)^β]^(−1/β)`
(`non-eq…md:47`). Saturated regime collapses to `j≈qnv_sat`. No `f` required; `μ₀(T,N_D), v_sat,
β` are micro-supplied (§21.8). Faithful tier verifies vs BTE-`j(E)` as an
`Algebraic/MethodEquivalence` residual.

**Degenerate-statistics caveat (declared model-form error).** The Einstein relation `D = μk_BT/q`
is the **nondegenerate** form. p⁺ B-doped diamond contact layers (and n⁺ degenerate III-N) run at
`10²⁰–10²¹ cm⁻³`, where Fermi–Dirac statistics make the generalized relation
`D/μ = (k_BT/q)·F_{1/2}(η)/F_{−1/2}(η)` (`η = (E_F−E_C)/k_BT`) the correct one. V1 carries the
nondegenerate form with this discrepancy entered as a **declared model-form-error term** in the
`combineTol` budget (`arch-11-residuals §11.7`) on any composition whose carrier density crosses
`n_degenerate(host)`; the generalized `F_{1/2}/F_{−1/2}` variant is a gated refinement (it shares
the §21.7.2 closed form, no new method). The same `n < n_degenerate(host)` gate carries the
plasmon–phonon / LST exclusion (`arch-17-out-of-scope`).

## 21.8 THE HOMOGENIZATION MAP (the micro→device coefficient bridge)

The three macro balance PDEs (`non-eq…md:230–232`, `group-C…md:96–100`):
```
(P)  ∇·(ε∇φ) = −ρ,  ρ = q(p − n + N_D⁺ − N_A⁻)
(DD) ∂_t n + ∇·j = G − R,   j = qμnE − qD∇n
(H)  C_p ρ_m ∂_t T_L − ∇·(κ(T)∇T_L) = j·E
```

Each row maps a **micro per-composition output** to a **macro PDE coefficient** by an explicit
relation evaluated at the local cell state:

| # | Micro output (formula) | Homogenization relation | Macro coeff / term | Eq |
|---|---|---|---|---|
| HM-1 | `κ(T)` (`phonon-kappa-T`, Slack) | `D_thermal(r) = κ(T_L(r))/(C_p ρ_m)`; face flux `q_f = −κ(T_L,f)(∇T_L)_f` | heat diffusion `κ(T_L(r))` | (H) |
| HM-2 | `σ(T)`/`μ₀(T,N_D)` (`mobility-impurity-phonon`) | `σ(r)=qn μ₀(T_L(r),N_D)`; drift `μ(E,T)=μ₀[1+(μ₀|E|/v_sat)^β]^(−1/β)` at `E(r)=−∇φ`; face flux via Scharfetter–Gummel (§21.9); Einstein `D=μk_BT/q` nondegenerate (degenerate caveat §21.7.2) | drift `qμn`, diffusion `qD` | (DD) |
| HM-3 | `v_sat` (`v-sat-*`) | saturated regime: `j_drift = q n v_sat` (decouples `j` from `E`) | saturated drift | (DD) |
| HM-4 | `α_ii(E)` (`chynoweth`, `a·exp(−b/E)`) | `G_av(r)=α_n(|E|)n v_n + α_p(|E|)p v_p` at `|E(r)|`; breakdown `M=1/(1−∫α dx)` (row 75) | avalanche source | (DD) |
| HM-5 | SRH + G–R rates | `S_carrier = G_av + G_opt − R_SRH(n,p; defect-density(r))`; `R_SRH` reads the **slow tier** per-cell defect density | `G − R` source | (DD) |
| HM-6 | `Q = j·E` (Joule) | `Q(r) = j(r)·E(r) = −j·∇φ` (the energy-conserving `δS/δx` cross-coupling) | heat source | (H) |
| HM-7 | `ε(T)` | `ε(r)=ε(material,T_L(r))` | Poisson operator | (P) |
| HM-8 | `TBR` (`*-mismatch-tbr`) | interface faces: Robin BC `q_f=(T_L⁺−T_L⁻)/TBR` | (H) interface BC | (H) |

**Supply contract.** *Per-composition* (coefficients are closed-form evaluables of local
`(T_L,E,n,p)`, applied per-cell); *error-tagged* (cheap closed-form + faithful BTE binding tied
by an `Algebraic/MethodEquivalence` residual; the tag is the `dressing` facet); *cached*
(content-addressed `PersistentMap` lookup, `O(log₃₂ n)`, never a re-solve — honors "no
solver-call hot paths"); *compile/runtime split* (Stage 1–4 fix the coefficient *form* hash-consed
into the kernel; Stage 5 evaluates the cached closed form at the PINO-supplied per-cell fields).

## 21.9 The `EOM/Continuum` residual

Generalizing row 71 (`coupled-em-thermal-pde-residual`), for each macro field and cell:
```
EOM/Continuum[field, c] = ‖ ∂_t field(c) − RHS_field({fields(c')}_{c'∈stencil(c)}; homog-coeffs) ‖²
```
with `RHS_field` the finite-volume discretization (§21.6.1):

| Field | `RHS_field` (per cell `c`) | Coeffs |
|---|---|---|
| `T_L` | `(1/C_pρ_m)[ Σ_f κ(T_L,f)(∇T_L)_f A_f + Q(c)V_c ]/V_c` | HM-1,6,8 |
| `φ` | algebraic constraint: `‖Σ_f ε_f(∇φ)_f A_f + ρ(c)V_c‖²` | HM-7 |
| `n` | `(1/V_c)[ −Σ_f j_f A_f/q + (G−R)(c)V_c ]` | HM-2/3,4,5 |
| `p` | same, hole sign | HM-2/3,4,5 |
| `j` | algebraic closure: `‖j(c) − (qμnE − qD∇n)(c)‖²` | HM-2/3 |

**Drift-diffusion face flux — Scharfetter–Gummel (required, not central differencing).** The
inter-cell carrier flux `j_f` in the `n`/`p` rows **must** use the Scharfetter–Gummel
exponentially-fitted form, not naive/central finite-volume differencing:
```
j_f = (qD/Δx)·[ n_{c⁺}·B(Δψ) − n_{c⁻}·B(−Δψ) ],   Δψ = q(φ_{c⁺}−φ_{c⁻})/k_BT,   B(t)=t/(e^t−1)
```
(`B` the Bernoulli function). At the UWBG operating point the cell Péclet number
`Pe = qEΔx/k_BT ≈ 40` (1 MV/cm × ~10 nm cell ÷ 25 mV), where a centrally-differenced `j_f` makes
the **residual operator itself wrong at the operating point** — the PINO would then be scored
against a discretization artifact rather than the physics. Scharfetter–Gummel is closed-form and
differentiable (one removable singularity at `Δψ→0`, guarded by the series `B(t)≈1−t/2`),
preserving C1 / no-runtime-solver. The interface heat flux (HM-8) and the Poisson/`j` constraints
are unaffected; only the convection-dominated carrier flux needs the exponential fitting.

`φ`,`j` are **algebraic/constraint** balances (no `∂_t`). Axes `(MeshCell, MacroField)`; the
per-cell-per-field scalar is the atomic contribution (`arch-11 §11.3`, spatial bin = mesh cell);
`RoaringCoverageMask` over `enumerate(product(MeshCell, MacroField))` selects the constrained
subdomain. `EOM/Continuum` is the **macro instance of the EOM-violation family**, not a new
top-level category (`MacroField` plays `StateComponent`'s role); row 71 is one `(T_L,φ,j)`-coupled
instance. Scoring is score-not-solve: the PINO supplies the `MacroState` trajectory on the mesh
(`arch-16 §16.1`), `/physics` evaluates the per-cell residual + cotangent — it never solves the PDE.

---

## 21.10 The unified three-tier residual contract

Resolving `group-C…md:608–614` ("three distinct state schemas + a *common* residual contract")
into concrete types. The three schemas are **not unifiable into one tensor** (three distinct
discretizations) — hence *stratified*, not flattened:

| Tier | `x` | index | EOM category | reversible `L δE/δx` | dissipative `M δS/δx` |
|---|---|---|---|---|---|
| Micro | 7 components | BZ × cell | `EOM/{γ̂,A,R,P,h,Π_h,Z}` (cats 1–7) | streaming + force | collision |
| Slow | `{[D]^q}` | (species, site) | `EOM/DefectPopulation` | — (`E` in state energies) | master-eq generator |
| Macro | `(T_L,φ,n,p,j)` | (MeshCell, MacroField) | `EOM/Continuum` | quasi-static (constraints `φ`,`j`) | parabolic diffusion + sources |

All three share **one residual shape** `‖∂_t x − (L δE/δx + M δS/δx)‖²` (`arch-11 §11.1`,
`group-C…md:543,664–668`), instantiated three ways, plus the common Conservation / Positivity /
Algebraic-identity residuals. The macro `L` is quasi-static (no reversible bracket between
continuum fields), so its EOM is dominantly the dissipative branch — exactly `group-C…md:567`'s
"pure dissipative `M δS/δx`" fluid limit, consistent with the macro tier being the
spatial-L4 reduction. One `ResidualKey = (producer, axes)` space spans all tiers over tier-typed
axis universes; `CategoryTag` gains the two EOM-family siblings `EOM/DefectPopulation`,
`EOM/Continuum` (the closed set grows from 17 to 19); the PINO holds one `Map<ResidualKey,
Weight>` and aggregates per `CategoryTag` / `StateTier` facet — `/physics` never pre-sums across
tiers (`arch-11 §11.4`).

## 21.11 Required `Environment` field additions

The driving tier (`Environment`, `arch-03-inputs`) gains the harsh-env fields the slow kinetics
read:

| New field | Type / units | Read by |
|---|---|---|
| `radiation_flux` | `ParticleFlux` (cm⁻²s⁻¹) | F-H1, F-H2 |
| `radiation_dose` `Φ_dose` | `Fluence` (cm⁻²) | F-H2 |
| `displacement_threshold E_d` | `Energy` (eV), per host | F-H1 |
| `vibration_spectrum` | `PSD` (amplitude vs freq, 100 Hz–10 kHz) | F-G4 |
| `p_O2` | `Pressure` (Pa) | F-46 |

(`p_O2` is a specialization of the existing partial-pressure slot; `μ_env` chemical potentials
already present.) Presence of these fields fires the §21.3 applicability predicates (first-order
decidable on field presence, `impl-04`).

## 21.12 New consistency residuals (thermodynamic identities)

`Static/Thermodynamic` residuals (`arch-11 §11.1` item 17), from `defects…md:574` (I.4):

- **R-T1 Gibbs adsorption** — `‖dγ/dμ + Γ‖²` (`dγ/dμ = −Γ`): ties surface free energy `γ(term,μ)`
  (row 44) to slow `[H]`/`x_ox`. T0/D1.
- **R-T2 charge–Fermi Maxwell** — `‖dE_form/dE_F − q‖²`: Zhang–Northrup slope (row 30) vs `E_F`
  must equal `q`; ties `charge_dist[D]` to `E_F(T)`. T0/D1.
- **R-T3 Clausius–Clapeyron analog** — `‖d ln[D]^q/d(1/T) + (E_form^q − T S_form^q)/k‖²`:
  population temperature-dependence consistent with `S_form`. T1/D2.

Curriculum: **Polish** `[0.60, 0.90)` with the other `Static/Thermodynamic` residuals.

## 21.13 New registry rows (`registry-manifest.csv` format)

Rows 105–112 (rows 103–104 are the existing rejected markers; F-F5 =
`carbide-growth-parabolic`, existing row 81, not re-added):

```csv
105,vacancy-generation-arrhenius,"`(c_V^q, T, μ, j, x_ox', ρ_dis, k_ann) → dc_V/dt`",B11/B4,T0,D1,cheap,S3 (defects G.1),"E_form, T, k_ann"
106,hydrogen-redistribution-drift-diffusion,"`(c_H(r), T, E, μ_drift) → ∂c_H/∂t`",B11/B5,T3,D3,cheap,S3 (defects G.2),"D_0, E_diff, E-field"
107,platelet-nucleation-allen-cahn,"`(c_platelet, c_Ns, T) → dc_platelet/dt`",B11/B4,T1,D2,cheap,S3 (defects G.3),"c_Ns, k_nuc(E_nuc=3.5eV)"
108,vibration-induced-vacancy-generation,"`(ρ_dis, σ_stress, f_vib, v_dis, b) → (dρ_dis/dt, G_V)`",B11,T1,D1,cheap,S3 (defects G.7),"ρ_dis, σ_stress"
109,air-oxidation-rate-eyring,"`(T, p_O2, ΔG‡, ν) → dx_ox/dt`",B11/B5,T0,D1,cheap,"S3 (catalog #46, Eyring)","T, p_O2"
110,hydrogen-desorption-rate-eyring,"`(T, E_des, ν) → r_H`",B11/B5,T0,D1,cheap,"S3 (catalog #47, E_des=3.8eV)","T, surface c_H"
111,nrt-displacements,"`(T_dam, E_d) → N_d`",B11/B4,T0,D1,cheap,"S4 (non-eq H.1)","T_dam, E_d(host)"
112,frenkel-pair-yield,"`(N_d, Σ_d, Φ_dose, η_recomb) → DefectDensity`",B11/B4,T0,D1,cheap,"S4 (non-eq H.2; [V]_irr=Φ·Σ_d·N_d·(1−η_recomb), Σ_d=N_atom·σ_d NIEL)","nrt-displacements, σ_d(host,particle)"
```

## 21.14 Open sub-decisions (flagged, not silent)

The corpus was genuinely insufficient on five bounded points; each is a tracked sub-decision,
not a silent gap:

1. **Mesh-adjoint scheme** — the mesh *format* is committed; the discrete- vs continuous-adjoint
   choice for differentiating `EOM/Continuum` through the finite-volume operator is the live
   residue of `arch-18 §2` (inherits the Stage-4→Stage-5 AD seam).
2. **Mesh generation/refinement policy** — committed as structured-tensor for V1
   (`enumerate(product(axes))`); adaptive hot-spot refinement deferred to V2.
3. **Hole-transport coefficients** — `μ_p, α_p, v_sat,p` are anchored for few materials; the `p`
   schema is committed but bipolar coefficient anchors are a per-composition data gap.
4. **Bidirectional slow↔macro coupling** — HM-5 reads slow defect density (macro←slow); the
   back-reaction (carrier-driven defect generation, F-G1's `G_irradiation`) is macro→slow; the
   rate law is the slow tier's (§21.3/§21.5), the contract is noted here.
5. **`η_recomb(T_L)`, `σ_d(host,particle)`, and per-material regime thresholds** — no closed form
   in the corpus (only the coupling structure); the NIEL displacement cross-section `σ_d` (F-H2)
   and recombination efficiency are curated `ProvenanceLedger` coefficients, and regime-switch
   field windows are order-of-magnitude — flagged as calibration / data-acquisition tasks, not
   invented.

## 21.15 Landing edits to existing docs

`arch-04` emergence axiom refined (§21.0); `arch-05` per-tier generators (`arch-05 §5.x–§5.z`);
`arch-08` L4 = macro tier (contradiction removed); `arch-11` adds `EOM/DefectPopulation` +
`EOM/Continuum` (17→19) and R-T1/R-T2/R-T3; `arch-03` adds the §21.11 `Environment` fields;
`arch-09` notes `DefectSpecies` (no new method); `arch-18` Closed-decision entry + §2 narrowed;
`registry-manifest.csv` rows 105–112. No new computational method or sub-method is introduced.

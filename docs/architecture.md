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
   temperature gradient, carrier-injection conditions.

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

These are the **irreducible degrees of freedom**. Phonon distributions
`n_{q,s}`, carrier distributions `f_n(k,r)`, surface coverages `θ_i`, electron
and lattice temperatures, current density, internal fields, defect populations,
and composition vectors are all **emergent** — coarse-grainings, Bloch
transforms, or semiclassical limits of `x(t)`. Adding any of them to the state
would create a constraint manifold tying it back to the irreducible DOFs and
reintroduce the integration pathology the formulation avoids.

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
2. **`FormulaApply`** — application of one of the 102 named formulas
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
| 102 formulas (`arch-09-vocabularies §9.3`) | typing rules for `FormulaApply` nodes |
| 12 methods (`arch-09-vocabularies §9.1`) | typing rules for `MethodInvoke` nodes |
| 20 templates (`arch-09-vocabularies §9.2`) | graph-construction macros that emit subgraphs |
| 11 bundles (`arch-09-vocabularies §9.4`) | the `bundle` payload of `Observable` roles |
| 17 residual categories (`arch-11-residuals`) | facet on `ResidualLeaf`, in `ContributionFacets.category` (a `CategoryTag` enum) |
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
- **Cross-formula CSE.** The 102 named formulas often share
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
| Computational methods | 12 (+2 sub-methods) | yes |
| Abstract-property templates | 20 | yes |
| Named formulas | 102 substantive (+2 rejected markers) | yes — see `formula-registry.md` |
| Observable bundles | 11 (B1–B11) | yes |
| Residual categories | 17 | yes |
| Cert obligations | 10 | yes |
| Layer-0 typeclasses | 4 | yes |
| Crystal symmetry group | first-class (space group × time-reversal × U(1) × SU(2)) | yes |
| State sub-DOF tags | `orbital, spin, sublattice, valley, strain, gauge, charge, none` | yes |

### 9.1 Twelve computational methods

Closed vocabulary; instances are programs in this vocabulary:

`state-readout`, `algebraic-combination`, `functional-differentiation`,
`variational-minimization`, `spectral-decomposition`, `spectral-aggregation`,
`linear-response`, `path-search`, `convex-optimization`, `kinetic-evolution`,
`statistical-sampling`, `symmetry-projection`.

Plus two registered sub-methods: `field-line-integral` (under `path-search`) and
`interface-tunneling` (under `linear-response`).

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

### 9.3 102 named formulas

Closed registry of typed, fully-parameterized algebraic formulas, named by
behavior (person-attribution names appear only as parenthetical literature
pointers). The canonical machine-readable list is
`physics/library/formulas/registry-manifest.csv` (102 substantive rows + 2
markers for relations that are enforced architecturally and therefore *not*
residualized: force = −∇energy, and equivariance). Rows 1–87 are grounded in the
domain research (`physics/research/`); rows 88–102 are the linear-response and
topology-atlas extensions. Each formula carries a typed signature, a cost tier
`T0..T3`, a differentiability tag `D0..D4`, and an applicability classifier
(§13). See `formula-registry.md` for the narrative index.

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

## 11.1 The seventeen categories (a taxonomy facet)

Residuals fall into seventeen categories, identified by symbolic
tags rather than ordinals. The categories are a *facet* on each
contribution, not a granularity floor or a unit of weighting.

**EOM-violation (per state component) — 7 categories.** One per
DOF of the unified state (`arch-04-state`):

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

**Structural axes of GENERIC — 3 categories.**

  8. `Degeneracy` — `‖L δS/δx‖² + ‖M δE/δx‖²`.
  9. `Conservation` — energy, particle-number / charge, momentum /
     crystal-momentum, spin.
 10. `Positivity` — `M ⪰ 0`, `f ∈ [0,1]`, `ρ ≥ 0`, `ω² ≥ 0`,
     `σ ⪰ 0`, `|S_i| = 1`.

**Algebraic identities — 5 categories** (the former umbrella, now
split by analytic kind):

 11. `Algebraic/Kramers-Kronig` — causality dispersion identities on
     response functions.
 12. `Algebraic/SumRules` — f-sum `(2/π)∫ω·Im ε dω = ω_p²`; acoustic
     sum `Σ_J Σ_R Φ_{IαJβ}(R) = 0`; oscillator strengths.
 13. `Algebraic/BalanceLaws` — detailed balance; Einstein relation
     between mobility and diffusion.
 14. `Algebraic/Symmetries` — Onsager reciprocity; Maxwell relations;
     space-group equivariance of response tensors.
 15. `Algebraic/MethodEquivalence` — different formulas claiming the
     same observable agree on their shared domain (BTE-σ ≡ Kubo-σ in
     linear response, etc.).

**Constraint violations (by input-domain type) — 2 categories.**
Disjoint by the *type* of input the constraint reads:

 16. `Static/Snapshot` — depends only on the geometric + electronic
     snapshot, no environment field. Valence-bond-sum charge balance;
     Born stability; dynamical stability; space-group equivariance of
     the snapshot.
 17. `Static/Thermodynamic` — depends on snapshot + environment
     (temperature, chemical potentials, partial pressures).
     Hull-distance, formation-energy-from-references, solubility,
     mass-action, carbide-formation.

Categories 16 and 17 stay disjoint because they consume
type-distinct inputs (snapshot vs snapshot+environment), and the
PINO curriculum schedules them differently for that reason.

The `CategoryTag` enum is the closed set of 17 symbols above. It
appears in `ContributionFacets.category` and nowhere else carries
semantic weight.

## 11.2 The atomic unit: residual contribution

A **residual contribution** is the smallest scalar (or scalar-valued
field-norm) the loss aggregator can multiply by an independent weight.
Every contribution is a `ResidualLeaf` node carrying a content-addressed
key:

```
ResidualKey = (producer : Producer, axes : Tuple<AxisLabel>)
Producer    = Formula(NamedFormula) | Method(NamedMethod)

ContributionFacets =                         -- sidecar; not part of identity
  ( category : CategoryTag                   -- one of 17 symbolic tags (§11.1)
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
[0.60, 0.90)  Polish    — add Algebraic/MethodEquivalence + Static/Snapshot + Static/Thermodynamic + Degeneracy
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

## 12.0.1 Coupling-derived simplifications (obligations 1, 5)

When a formula node originates from the invariant generator
(`arch-19-coupling-structure §19.3`), obligations 1 and 5 collapse to
projection-residual checks:

- **Obligation 1 (symmetry equivariance).** Invariants are
  trivial-irrep basis vectors by construction. Cert verifies the
  emitted `InvariantTerm.symbolic-form` lies in the claimed subspace:
  `||v − π_trivial v|| / ||v|| < ε` on a sampled evaluation. Failure
  is a generator bug, not a physics bug.
- **Obligation 5 (antisymmetry of L, PSD of M).** The
  `InvariantTerm.channel.target` tag determines the projection rule:
  `AntisymmForm` invariants project onto the antisymmetric component;
  `PSDSymmForm` invariants project onto the PSD cone. Cert verifies
  the emitted form equals its projection within `ε`.

Both checks are O(1) per invariant and run alongside the generator at
Stage 2.5.

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

V1 commitment: every registry entry gets an explicit `applicability` field;
always-true stubs are acceptable for V1.0 and refined incrementally. Open
questions (deferred): soft `[0,1]` classifiers, classifier composition under
perturbation, and current-vs-initial-state evaluation for trajectory training.

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
- 4-phonon scattering, full NEGF tunneling, full SCPH/SSCHA — replaced by D4
  surrogates or Layer-1.75 V2 scaffolding.
- Plasma-process surface damage; grain-boundary statistics; continuum creep /
  dislocation climb; quantum-tunneling-corrected reaction rates (classical
  Eyring TST adequate at T_op ≥ 600 K).
- True renormalization-group flow; inverse design / minimal-model search (would
  live in `/informed-operator` as a PINO head, not a `/physics` primitive);
  fragile topology.

`predict` raises `out-of-scope` with a witness for any of these; cert
obligation-3 flags suspect cases.

---


<a id="arch-18-open-decisions"></a>

# Open decisions

The architecture above is committed. These remain to be decided.

1. **Implementation language — the single blocking decision.** No language is
   chosen. The always-cheap pipeline (`arch-07-pipeline`) narrows the candidates
   to those with first-class staging + AD + sparse linear algebra:
   - **Julia** — Symbolics.jl + ModelingToolkit.jl + Enzyme/Diffractor; closest
     analogue to the symbolic-IR + Stage-4-codegen design.
   - **Python + JAX** — `jax.jit` for staging, JAXopt for implicit-diff,
     Pennylane-style symbolic frontends for the IR; strongest ML/GPU ecosystem.
   - **Custom MLIR stack** — most control over Stage-4 codegen at highest cost.

   Haskell/TTH and Scala 3 are technically viable for the staging story but
   lack the numerical ecosystem (compressed-ops, IBZ tooling, GPU codegen) the
   pipeline depends on; demoted from candidates.

   This blocks the first implementation phase.
2. Surrogate-net build vs adopt, for the D4 surrogate formulas.
3. PDE-mesh format + adjoint library, for `KineticEvolutionOf` instances needing
   an explicit mesh.
4. The `γ̂` open questions of `arch-15-gamma-hat §15.4` (ε-equality,
   materialization policy, long-trajectory drift / rank-refresh, rank-dependent
   applicability of the LowRank slot).
5. Layer-1.75 minimum spec sufficient for a V2 contributor to implement
   self-consistent GW / DMFT.
6. The integrator interface — the exact signature `dynamics` exposes to
   `/informed-operator` for handing off the assembled GENERIC right-hand side.
7. **Coupling-channel template registry.** Enumerate the principled
   set of `CouplingChannel` templates (sector-pair × target shape × default
   order) covering the physics regimes we care about — expected ~10 entries
   spanning orbital-phonon, spin-orbit, spin-strain, gauge-matter
   (minimal coupling), multipole-external-field (Zeeman / Stark), ion-ion
   electrostatic, plus sub-DOF variants. Each entry: one `CouplingChannel`
   record + `Active(MVP) | V2-deferred | Excluded(rationale)` flag +
   applicability predicate. The actual coupling terms are *generated* by
   the Stage-2.5 invariant synthesizer (`arch-19-coupling-structure`); the
   registry only lists which channels to instantiate.

## Closed decisions

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

## 19.3 The invariant generator

```
generate-invariants : CrystalSymmetryGroup × CouplingChannel
                    → List<InvariantTerm>
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

The generator is the *constructive* direction of the irrep machinery
that Stage 2 already uses *decompositionally* (`arch-07-pipeline §7.2`
block-diagonalizes operators by irrep). Same module; same primitives;
new direction.

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

The author never wrote `g_{nm,ν}(k,q)`. The symmetry group did.

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
          List<InvariantTerm> to the channel.
Outputs : Stage2_5Sidecar.invariants : Map<CouplingChannel, List<InvariantTerm>>
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

## 19.7 Cert hooks

The invariant-generator structure simplifies two cert obligations
(`arch-12-cert`):

- **Obligation 1 (symmetry equivariance).** Invariants are
  trivial-irrep basis vectors *by construction*; equivariance is
  automatic. Cert reduces to a numerical projection-residual check:
  `||v.symbolic-form − π_trivial v.symbolic-form|| < ε` on a sampled
  evaluation. Failure indicates a generator bug, not a physics bug.
- **Obligation 5 (conservation / antisymmetry of L / PSD of M).**
  The `target` tag determines a projection rule applied at the
  generator step: `AntisymmForm` invariants are projected onto the
  antisymmetric component of the candidate tensor; `PSDSymmForm`
  invariants are projected onto the PSD cone. The projection is part
  of the generator's contract; cert numerically verifies the projected
  output matches the emitted `symbolic-form` within `ε`.

Both checks are O(1) per invariant; both are integrated with
`SymmetryAdaptedHamiltonianOf` (`arch-09-vocabularies §8.2`) which
already lives in the symmetry machinery.

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

The set of *active* channels in a composition is the **`CouplingSpec`** —
a `SparseSet[CouplingRegistry]` (`arch-20-representations §20.3`) whose
identity is its Merkle root, carried alongside the existing composition
request (`arch-07-pipeline §7.1`). The diamond MVP's `CouplingSpec` is
short: electron-phonon + minimal coupling + ion-ion electrostatic +
phonon-phonon scattering (in M).

## 19.9 Open — coupling-channel template registry

The principled set of `CouplingChannel` *templates* covering the
physics regimes (~10 entries) — orbital-phonon, spin-orbit, spin-strain,
gauge-matter (minimal coupling), multipole-external-field
(Zeeman / Stark), ion-ion electrostatic, plus sub-DOF variants — is not
enumerated here. Tracked as an open decision in
`arch-18-open-decisions §7`. The actual `InvariantTerm`s are generated
by the Stage-2.5 synthesizer; the registry only lists which channels
to instantiate.

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

Three op signatures cover every Merkle DAG instance in `/physics`:

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
  one `MerkleDAG[S, L]` substrate with three op signatures.
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

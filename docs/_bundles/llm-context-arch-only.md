<!-- GENERATED FILE — do not edit. Source files under docs/{architecture,implementation,mvp}/. Regenerate with `python docs/meta/assemble.py`. -->

# n-Op Architecture (LLM context bundle)

## Contents

- [The PhysicsGraph](#arch-06-physics-graph)
- [The compose-time pipeline](#arch-07-pipeline)
- [The unified state](#arch-04-state)
- [Dynamics — GENERIC](#arch-05-generic)
- [Canonical vocabularies and counts](#arch-09-vocabularies)
- [Residuals](#arch-11-residuals)
- [The pino-bridge exports](#arch-16-pino-bridge)


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

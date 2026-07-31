---
id: gamma-hat
title: "The one-body density matrix as a lowering choice"
owns:
  - density-matrix encoding vocabulary
  - density-matrix compression plan space
  - density-matrix scorer-only boundary
  - density-matrix read and write paths
  - density-matrix node identity
  - density-matrix memory budget at MVP scale
anchors:
  encoding-vocabulary: "The encoding vocabulary"
  scorer-only: "Scorer-only — the density matrix never evolves here"
  read-write-paths: "Read path and write path"
  lowering-internals: "Strategies that are lowering internals"
  identity-is-exact: "Node identity is exact"
  mvp-budget: "The memory budget at MVP scale"
depends-on:
  - unified-state
  - crystal-inputs
  - library-landscape
  - property-templates
  - generic-dynamics
  - physics-graph
  - compose-time-pipeline
  - representation-substrate
  - residual-definitions
  - forced-decisions
open-questions:
  - id: supercell-memory-budget
    anchor: mvp-budget
    summary: "The density-matrix memory budget when leaving the primitive cell. Orbital storage stays linear in atom count and band count, but no supercell budget is written down, and the page states that revisiting it is the first obligation on leaving the primitive cell."
---
# The one-body density matrix as a lowering choice

The one-body density matrix — one of the seven state slots ([unified-state#slots]) — is the most
demanding object in the state vector: a single logical entity with multiple inequivalent
encodings, where different operations have different runtime cost on different encodings.

Under the physics-graph framing ([physics-graph#the-graph]) and the compose-time pipeline
([compose-time-pipeline]) it is one node type whose `CompressionPlan` ranges over a structured
`Basis × Form` product. This page owns that product, the scorer-only boundary that bounds it, and
the memory budget the encoding buys.

## The encoding vocabulary

An encoding factors into two orthogonal axes:

```
Basis ∈ { Real, Reciprocal, Wannier, NaturalOrbital, SymmetryAdapted }
Form  ∈ { Dense, Sparse, BlockDiag, LowRank }
```

The first-class pairs for version 1, and what each is for:

| Pair | For |
|---|---|
| `(Reciprocal, BlockDiag)` | periodic substrates — the diamond MVP default |
| `(Real, Sparse)` | defects, surfaces, amorphous regions |
| `(Wannier, Sparse)` | interface layers and dangling bonds |
| `(NaturalOrbital, LowRank)` | low-rank substrates |
| `(SymmetryAdapted, BlockDiag)` | the output of `SymmetryAdaptedHamiltonianOf` ([property-templates#what-each-produces]) |

Lowering selects one slot per density-matrix-typed node from the
`(PeriodicityStructure, SiteDecoration)` pair ([crystal-inputs#top-level-inputs]). Transcoders
convert on demand for operations whose runtime cost is lower in a different encoding.

**Rank-dependent applicability is a compile-time predicate, not a runtime check.** Whether the
`(NaturalOrbital, LowRank)` slot applies is decided at lowering from the same pair, alongside
every other slot choice above. There is nothing accumulating that would need monitoring, so the
runtime check whose cost was the original objection is not needed. Four-index objects — the
Bethe–Salpeter kernel, Boltzmann collision matrices — go directly to tensor-train compression.

## Scorer-only — the density matrix never evolves here

**The oracle library is scorer-only: the density matrix never evolves inside it.** States arrive
complete, are scored, and are discarded. There is no trajectory in here and therefore no density
matrix carrying a history. The library holds no time-varying state values and integrates no
trajectories ([library-landscape#oracle-exclusions]); the write path is construction and self-consistency only.

An equation-of-motion violation residual over the density matrix ([residual-definitions#eom-categories]) is
consistent with this and is not an exception: it *scores* a supplied `∂_t γ̂` against the
reversible and dissipative generators `L·δE/δx + M·δS/δx` of [generic-dynamics#operators]. **Scoring a
proposed rate is not taking a step.**

Trajectory ownership sits with the consumer. The oracle emits a per-tier tangent map and a
steppable-form manifest — a pure function, not an integrator — and the manifest declares what a
consumer needs in order to integrate the micro tier and to own the density matrix's
representation health across its own steps. **The drift problem is exported, not dissolved**, and
saying so is the point.

## Read path and write path

Most density-matrix traffic during operator training is **reads** — apply the Hamiltonian,
extract the density, take a trace, take an eigendecomposition. A small minority is **writes** —
construction and the self-consistent step. The two paths differ:

```
READ PATH (dominates evaluation)
    interface ──destructor──▶ tensor-network substrate
    lazy materialisation; no term staging, no bundle sync

WRITE PATH (construction, self-consistent step)
    interface ▶ term algebra ▶ planner ▶ encoding ▶ substrate
```

The asymmetry is what the encoding is optimised for, and the costs say why. On the read path,
applying the operator is a matrix-matrix product against the `N_PW × N_b` factors; extracting the
density is a set of outer products; the trace is a set of inner products. **Every one of those
costs is set by the rank `N_b`, not by `N_PW²`** — which is the same fact the memory budget
below states in bytes. On the write path, construction is staged through the planner, and the
self-consistency gradient is handled by the implicit-differentiation adjoint synthesised at
lowering rather than by unrolling the iteration.

Under the always-cheap pipeline the read path is what the runtime kernel does, and the write path
is absorbed into lowering.

Self-consistency — the case where the Hamiltonian depends on the density matrix — is *structured*
by the coalgebraic fixed-point form but **solved by the implicit-differentiation adjoint**
synthesised at lowering ([compose-time-pipeline#lowering-and-adjoint-synthesis]). Convergence iteration happens by explicit
iteration above the substrate, never inside it.

## Strategies that are lowering internals

Several representation strategies that might look like architectural peers are, under the
always-cheap framing, lowering tactics applied to nodes whose type is the density-matrix
typeclass:

| Strategy | Realisation |
|---|---|
| Codata / coalgebraic interface | the `Node` interface itself ([physics-graph#node]); destructors are method invocations |
| Typed term algebra (staging) | an internal of symbolic lift and algebraic simplification — the compose-time symbolic intermediate representation |
| E-graph with equality saturation | an optional offline rewrite oracle; not on the runtime path |
| Pullback bundle of synchronised encodings | single-slot for version 1, one canonical encoding per node; the bundle is the multi-slot version 2 generalisation |
| Tensor network with cost-aware contraction | a lowering primitive for the low-rank and block-diagonal forms |

## Node identity is exact

The node identity contract is **not** bisimulation-up-to-ε, and must not be: `≈_ε` is not
transitive, so it yields no quotient, no canonical representative, and nothing to hash. The
general rule — identity stays exact, and the error estimate is carried beside it rather than
folded into it — is [representation-substrate#identity-exact]'s.

For the density matrix the consequence is the rewrite-admission rule: a rewrite is admitted when
it is exact over ℝ *and* its floating-point side conditions are discharged by an e-class analysis
carrying interval and not-equals facts ([compose-time-pipeline#rewrite-admission]). E-graphs stay offline, and they
stay offline for that stated reason rather than as a hedge.

## The memory budget at MVP scale

The dense one-body density matrix is `O(N_r²)`. At MVP scale that is a non-issue, because the
density matrix is **never densified**.

**Encoding.** `(Reciprocal, BlockDiag)` — one block per k-point — with each block stored as
**orbitals**, low-rank in the band index at `N_PW × N_b`, rather than as a dense `N_PW × N_PW`
matrix.

**Sizing, primitive cell, basis capable of supporting a quasi-particle correction.** A plane-wave
cutoff near 400 eV gives `N_PW ≈ 1000`; the band count is `N_b ≈ 40`, four occupied plus the
unoccupied manifold the quasi-particle correction needs; an 8×8×8 Monkhorst–Pack mesh gives
**~29 irreducible k-points**. Orbital storage is then

```
N_PW × N_b × 16 B × N_k  ≈  1000 × 40 × 16 × 29  ≈  18 MB
```

against a densified

```
N_PW² × 16 B × N_k  ≈  1000² × 16 × 29  ≈  460 MB
```

on the same mesh — which is exactly why the encoding forbids densifying. The factor of 16 bytes
is one complex double per element. **The slot choice is a feasibility boundary, not an
optimisation.**

The k-blocks are **mutually independent**: embarrassingly parallel, and independently
addressable. The block-diagonal form is therefore a parallelism decision as much as a storage
one.

**Warm-start initialiser.** A three-nearest-neighbour sp³d⁵ tight-binding model for carbon gives
a `~18 × 18` Hamiltonian per k-point — kilobytes — which seeds the self-consistent-field inner
loop ([forced-decisions#tb-warm-start]). It is **not a separate residual path**.

**Beyond the primitive cell.** Defect and interface supercells grow `N_PW` linearly, while
orbital storage stays roughly linear in `N_atoms × N_b`. The dense-storage concern returns only
if a large supercell is densified, which the encoding forbids. **A supercell memory budget is the
first thing to revisit when leaving the primitive cell**, and nothing carries one yet.

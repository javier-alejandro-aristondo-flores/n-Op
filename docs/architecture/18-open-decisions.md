---
id: arch-18-open-decisions
title: Open decisions
status: draft
revision: 1
canonical-for:
  - open decisions
depends-on: []
referenced-by: []
research-sources: []
---
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

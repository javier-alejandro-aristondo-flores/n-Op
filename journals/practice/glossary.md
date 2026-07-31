---
id: glossary
title: "Glossary"
owns:
  - implementation-vocabulary index
  - overloaded-token register
anchors:
  what-this-is: "An index, not a second definition"
  vocabulary: "Where a name is specified"
  overloaded: "Tokens that need a qualifier"
depends-on:
  - agent-contract
  - traps
  - physics-graph
  - residual-definitions
  - residual-machinery
  - multiscale-state
  - cert-obligations
  - pino-bridge
  - compose-time-pipeline
  - applicability-classifiers
  - topology-atlas
  - born-oppenheimer-levels
  - unified-state
  - canonical-vocabularies
  - observable-bundles
  - named-formulas
  - coupling-structure
  - representation-substrate
  - generic-dynamics
  - accuracy-ledger
open-questions: []
---
# Glossary

## An index, not a second definition

**No term is defined here.** Every row below names a page, and that page is where the
term is specified. A glossary that carries its own one-line definition carries a second
copy of something another page owns, and the two drift the moment either is edited —
which is the failure [agent-contract#placement] exists to make impossible. A pointer
cannot drift.

There are two keys into the corpus, and they answer different questions.

- **By topic.** `generated/corpus.json` maps every owned topic to the page that owns it.
  If you know what the *subject* is called, that map answers in one hop and it is
  emitted, so it is never wrong.
- **By name.** This page maps the names that appear in code, in typed pseudocode and in
  the reference data — record names, enum names, field names — onto the pages that
  specify them. Those names are not the same strings as the topics, which is why the
  topic map does not answer here.

If a name is missing from both, no page claims it. That is a finding, not a lookup
failure: decide which page should own it and add the topic there
([agent-contract#placement]).

## Where a name is specified

| Name | Specified in |
|---|---|
| `PhysicsGraph` | [physics-graph] |
| `Node` | [physics-graph] |
| `NodeKind` | [physics-graph] |
| `InputKind` | [physics-graph] |
| `OutputRole` | [physics-graph] |
| `FormulaApply` | [physics-graph] |
| `ResidualLeaf` | [physics-graph] |
| `CompressionPlan` | [physics-graph] |
| `ResidualKey` | [residual-definitions] |
| `ContributionFacets` | [residual-definitions] |
| `CategoryTag` | [residual-definitions] |
| `ResidualVector` | [residual-definitions] |
| curriculum gating defaults | [residual-definitions] |
| `AxisLabel` | [residual-machinery] |
| `ResidualGenerator` | [residual-machinery] |
| `IterationSnapshot` | [residual-machinery] |
| `OneShotCert` | [residual-machinery] |
| `IterativeResult` | [residual-machinery] |
| `StateTier` | [multiscale-state] |
| `DefectSpecies` | [multiscale-state] |
| defect population, the slow-tier fiber | [multiscale-state] |
| `DeviceMesh` and `MacroState` | [multiscale-state] |
| homogenization map | [multiscale-state] |
| the slow- and macro-tier equation-of-motion residual families | [multiscale-state] |
| `CertEvidence` | [cert-obligations] |
| `SqliteReferenceCache` | [cert-obligations] |
| `GroundTruthBridgeGenerator` | [pino-bridge] |
| `RoaringCoverageMask` | [pino-bridge] |
| `UnifiedState`, the bridge-surface name for the micro state | [pino-bridge] |
| the operator seam itself | [pino-bridge] |
| symbolic lift | [compose-time-pipeline] |
| symmetry quotient | [compose-time-pipeline] |
| invariant synthesis | [compose-time-pipeline] |
| algebraic simplification | [compose-time-pipeline] |
| lowering and adjoint synthesis | [compose-time-pipeline] |
| runtime kernel application | [compose-time-pipeline] |
| the always-cheap discipline | [compose-time-pipeline] |
| applicability classifier | [applicability-classifiers] |
| topology atlas | [topology-atlas] |
| Born-Oppenheimer levels | [born-oppenheimer-levels] |
| state component | [unified-state] |
| observable bundle | [observable-bundles] |
| `CrystalSymmetryGroup` | [canonical-vocabularies] |
| `IrrepLabel` | [canonical-vocabularies] |
| cost tier | [named-formulas] |
| differentiability tag | [named-formulas] |
| `CouplingChannel` | [coupling-structure] |
| `StatePiece` | [coupling-structure] |
| `InvariantTerm` | [coupling-structure] |
| `generate-invariants` | [coupling-structure] |
| `GeneratorOutput` | [coupling-structure] |
| `CouplingSpec` | [coupling-structure] |
| `MechanismRange` | [coupling-structure] |
| `polynomial_sufficient` | [coupling-structure] |
| `KernelExt` | [coupling-structure] |
| `GaugeRule` | [coupling-structure] |
| `CoverageBound` | [coupling-structure] |
| `TheoryContext` | [coupling-structure] |
| `SubDofTag` | [coupling-structure] |
| `ContentAddress` | [representation-substrate] |
| `Universe` | [representation-substrate] |
| `SparseSet` | [representation-substrate] |
| `PersistentMap` | [representation-substrate] |
| `MerkleDAG` | [representation-substrate] |
| `EvidenceBearing` | [representation-substrate] |
| `EvidenceDAG` | [representation-substrate] |
| `SymbolicTensorOps` | [representation-substrate] |
| `PredicateOps` | [representation-substrate] |
| `GroupOps` | [representation-substrate] |
| the two-generator dynamics form | [generic-dynamics] |
| ledger-tracked observables, and the ledger count | [accuracy-ledger] |

## Tokens that need a qualifier

[agent-contract#vocabulary] states the rule: when the corpus owns a word for something,
no synonym is admissible, and no token may name two things. This is the register of
tokens that already name two things, because the second sense belongs to physics, to an
external tool, or to a file format, and cannot be renamed away.

**One sense is reserved. Every other sense carries a qualifier, always** — including in
a heading, a field name and a commit message, since a qualifier that is dropped when
convenient is not a qualifier.

| Token | Reserved sense | Every other sense |
|---|---|---|
| `graph` | the physics graph, which is acyclic and whose topological order is its evaluation order | the dependency relation among pages is **cyclic** and must never be closed over; it is the **page index**, and it is emitted rather than authored |
| `tier` | the state tier — micro, slow, macro | evaluation cost uses its magnitude names; dressing tiers and build stages use theirs |
| `layer` | the physical or epitaxial layer, which is real physics | the graph's depth field is `depth`; the dressing tiers have their own names; the typeclass alphabet needs no number |
| `slot` | a slot of the unified state | a residual output is a `residual-key`; an encoding decision is an `encoding-choice` |
| `cell` | the crystallographic unit cell | a mesh cell is always `mesh-cell`; a field of a data row is a `field`, never a cell |
| `kernel` | the compiled artifact, which carries a file hash | physics kernels stay qualified — collision kernel, response kernel, `KernelExt` |
| `source` | nothing — the token names two different fields on two records the same factory reads together | a citation is `provenance`; the closed enum a generator compares against is `compared-against` |
| `path` | a file path | the registry column that classified anchors is `anchor-class`, which is what every denial of the old name already called it |
| `coverage-mask` | nothing — three unrelated masks multiply into one loss | `axis-coverage` for axis-tuple coverage, `applicability-mask` for per-sample applicability, `label-presence` for label presence per source |
| `GAP` | nothing — the missing-data marker is **`UNSEEDED`** | the computer-algebra system and the Gaussian Approximation Potential are external proper nouns and are always written under their full names; lowercase `gap` is the band gap. [traps#missing-data-marker] is the hazard |

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
  - accuracy-ledger
  - applicability-classifiers
  - born-oppenheimer-levels
  - cert-obligations
  - compose-time-pipeline
  - computational-methods
  - coupling-structure
  - crystal-inputs
  - generic-dynamics
  - multiscale-state
  - named-formulas
  - observable-bundles
  - physics-graph
  - pino-bridge
  - property-templates
  - representation-substrate
  - residual-definitions
  - residual-machinery
  - topology-atlas
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

- **By topic.** [corpus-index] maps every owned topic to the page that owns it.
  If you know what the *subject* is called, that map answers in one hop and it is
  emitted, so it is never wrong.
- **By name.** This page maps the names that appear in code, in typed pseudocode and in
  the reference data — record names, enum names, field names — onto the pages that
  specify them. Those names are not the same strings as the topics, which is why the
  topic map does not answer here.

**Every row asserts one thing: the name in the left cell appears on the page in the
right cell.** That is a claim about the target's *contents*, not about whether the
citation resolves — a row can satisfy every rule in the schema and still be false, which
is how this index drifted before anything checked it. The left cell is therefore the name
**as its own page writes it**, including that page's spelling and capitalization; where
this page's own style would spell it differently, the page it points at wins, because a
name not written the way a reader will search for it is not an index entry.

If a name is missing from both, no page claims it. That is a finding, not a lookup
failure: decide which page should own it and add the topic there
([agent-contract#placement]).

## Where a name is specified

| Name | Specified in |
|---|---|
| `PhysicsGraph` | [physics-graph#the-graph] |
| `Node` | [physics-graph#node] |
| `NodeKind` | [physics-graph#node-kinds] |
| `InputKind` | [physics-graph#node-kinds] |
| `MethodInvoke` | [physics-graph#node-kinds] |
| `FormulaApply` | [physics-graph#node-kinds] |
| `OutputRole` | [physics-graph#output-role] |
| `ResidualLeaf` | [physics-graph#output-role] |
| `CompressionPlan` | [physics-graph#sidecars] |
| `ResidualKey` | [residual-definitions#residualkey] |
| `ContributionFacets` | [residual-definitions#facets] |
| `CategoryTag` | [residual-definitions#categorytag] |
| the curriculum category gate | [residual-definitions#curriculum-gate] |
| `ResidualVector` | [compose-time-pipeline#runtime-kernel-application] |
| `CertEvidence` | [compose-time-pipeline#runtime-kernel-application] |
| `AxisLabel` | [residual-machinery#generator-record] |
| `ResidualGenerator` | [residual-machinery#generator-record] |
| `IterationSnapshot` | [residual-machinery#dressing-certs] |
| `OneShotCert` | [residual-machinery#dressing-certs] |
| `IterativeResult` | [residual-machinery#dressing-certs] |
| `DefectSpecies` | [multiscale-state#defect-species] |
| the slow-state schema | [multiscale-state#slow-state-schema] |
| `EOM/DefectPopulation` | [multiscale-state#eom-defect-population] |
| `EOM/Continuum` | [multiscale-state#eom-continuum] |
| `DeviceMesh` | [multiscale-state#device-mesh] |
| `MacroState` | [multiscale-state#macro-state-schema] |
| the homogenization map | [multiscale-state#homogenization-map] |
| `SqliteReferenceCache` | [cert-obligations#reference-cache] |
| `RoaringCoverageMask` | [cert-obligations#reference-cache] |
| `GroundTruthBridgeGenerator` | [pino-bridge#import] |
| `UnifiedState` | [pino-bridge#validate] |
| symbolic lift | [compose-time-pipeline#symbolic-lift] |
| symmetry quotient | [compose-time-pipeline#symmetry-quotient] |
| invariant synthesis | [compose-time-pipeline#invariant-synthesis] |
| algebraic simplification | [compose-time-pipeline#algebraic-simplification] |
| lowering and adjoint synthesis | [compose-time-pipeline#lowering-and-adjoint-synthesis] |
| runtime kernel application | [compose-time-pipeline#runtime-kernel-application] |
| the always-cheap discipline | [compose-time-pipeline#always-cheap] |
| applicability classifier | [applicability-classifiers] |
| topology atlas | [topology-atlas] |
| `DiscreteStructure` | [topology-atlas#entry] |
| the four Born–Oppenheimer levels | [born-oppenheimer-levels] |
| observable bundle | [observable-bundles] |
| `CrystalSymmetryGroup` | [coupling-structure] |
| `IrrepLabel` | [representation-substrate#clusters] |
| evaluation cost | [named-formulas#cost-tiers] |
| differentiability | [named-formulas#diff-tags] |
| `CouplingChannel` | [coupling-structure#channel-record] |
| `StatePiece` | [coupling-structure#channel-record] |
| `StateComponent` | [coupling-structure#channel-record] |
| `SubDofTag` | [coupling-structure#channel-record] |
| `InvariantTerm` | [coupling-structure#invariant-generator] |
| `generate-invariants` | [coupling-structure#invariant-generator] |
| `GeneratorOutput` | [coupling-structure#generator-contract] |
| `CouplingSpec` | [coupling-structure#couplingspec] |
| `MechanismRange` | [coupling-structure#mechanism-range-table] |
| `polynomial_sufficient` | [coupling-structure#mechanism-range-table] |
| `KernelExt` | [coupling-structure#kernel-ext] |
| `GaugeRule` | [coupling-structure] |
| `CoverageBound` | [coupling-structure#coverage-policy] |
| `TheoryContext` | [coupling-structure#theory-context-placement] |
| `ProvenanceLedger` | [coupling-structure#provenance-contract] |
| `AntisymmForm` | [coupling-structure#target-shapes] |
| `PSDSymmForm` | [coupling-structure#target-shapes] |
| `ContentAddress` | [representation-substrate] |
| `Universe` | [representation-substrate#primitives] |
| `SparseSet` | [representation-substrate#primitives] |
| `PersistentMap` | [representation-substrate#primitives] |
| `MerkleDAG` | [representation-substrate#primitives] |
| `EvidenceBearing` | [representation-substrate#clusters] |
| `SymbolicTensorOps` | [representation-substrate#op-signatures] |
| `PredicateOps` | [representation-substrate#op-signatures] |
| `GroupOps` | [representation-substrate#op-signatures] |
| `EvidenceOps` | [representation-substrate#op-signatures] |
| `PeriodicityStructure` | [crystal-inputs#periodicity-structure] |
| `SiteDecoration` | [crystal-inputs#site-decoration] |
| `ResponseKernel` | [computational-methods] |
| the two-generator form | [generic-dynamics#generic-form] |
| ledger-tracked observables | [accuracy-ledger#observable-counts] |
| `AlgebraicOf` | [property-templates#signatures] |
| `ClassifyOf` | [property-templates#signatures] |
| `HarmonicStiffnessHessianOf` | [property-templates#signatures] |
| `KineticEvolutionOf` | [property-templates#signatures] |
| `PathStationaryOf` | [property-templates#signatures] |
| `ResponseOfTo` | [property-templates#signatures] |
| `SecondDerivativeOf` | [property-templates#signatures] |
| `SelfConsistentChargeBalanceOf` | [property-templates#signatures] |
| `SelfConsistentRenormalizationOf` | [property-templates#signatures] |
| `SpectralAggregateOf` | [property-templates#signatures] |
| `SpectrumOf` | [property-templates#signatures] |
| `StateReadoutOf` | [property-templates#signatures] |
| `SymmetryAdaptedHamiltonianOf` | [property-templates#signatures] |

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

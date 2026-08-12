---
id: topology-atlas
title: "The topology atlas"
owns:
  - topology atlas entry
  - symmetry indicator group
  - topology cost split
  - topological equivalence signal
anchors:
  entry: "The atlas entry"
  x-bs: "The symmetry-indicator group"
  cost-split: "What is always on and what is opt-in"
  pino-signal: "Why the atlas exists"
depends-on:
  - typeclass-alphabet
  - cert-obligations
  - compose-time-pipeline
  - pino-bridge
open-questions: []
---
# The topology atlas

## The atlas entry

At compose time the atlas computes, for each composition:

```
TopologyAtlasEntry =
  ( space-group   : 1..230 (+ magnetic)
  , AZ-class      : ten-element symmetry-class label
  , X_BS          : finite abelian symmetry-indicator group
  , EBRs          : elementary band representations
  , compatibility : compatibility-relation matrix )
```

Every field is combinatorial, and atlas outputs are `DiscreteStructure`
instances ([typeclass-alphabet#discrete-structure]) — no units, no domain, no
tolerance. Obligation-7 is literally a morphism over them
([cert-obligations#the-ten-obligations]): bulk-boundary correspondence relates
two discrete objects, so checking it is composition in a discrete category
rather than a numerical comparison.

## The symmetry-indicator group

`X_BS` is computed in polynomial time, by Smith Normal Form on the integer
matrix of orbit-induced representations. That it is polynomial is what makes the
atlas affordable at compose time for every composition rather than for a chosen
few.

117 of the 230 space groups have a non-trivial symmetry-indicator group under
time reversal in the spin-doubled setting, and the largest such group has order
72.

## What is always on and what is opt-in

The cheap parts run at compose time for every composition: the
symmetry-indicator class, the orbit-representation decomposition, the
compatibility check, and boundary-mode multiplicity by indicator lookup. All four
are lookups or integer linear algebra over the entry above.

The expensive parts are global integrals over the dual-space grid — Wilson loops,
Chern integrals, the Pfaffian route to the Z₂ invariant — and those are opt-in
per observable. They cost a mesh integration each, which is the cost of an
observable rather than the cost of a classification, so charging every
composition for them would make the atlas the most expensive thing in the
pipeline ([compose-time-pipeline#always-cheap]).

## Why the atlas exists

The atlas gives the operator a navigational signal. The symmetry-indicator group
tells the model which compositions are topologically equivalent, so a gradient
taken in one informs the other ([pino-bridge#validate]).

**Topology is the map, not a feature.** The distinction decides how the atlas is
consumed: a feature is one more input concatenated onto a vector, and the model
must learn what to do with it; a map is a statement about which regions of the
composition space are the same region, and the model gets that structure for
free.

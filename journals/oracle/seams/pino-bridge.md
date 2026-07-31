---
id: pino-bridge
title: "The pino-bridge exports"
owns:
  - the exported surface contract
  - Validate signature
  - Import signature
  - axis coverage of an imported datum
anchors:
  surface: "The only surface"
  validate: "Validate — the differentiated residual surface"
  import: "Import — external ground truth"
  axis-coverage: "Axis coverage"
  not-exported: "What is not exported"
depends-on:
  - unified-state
  - physics-graph
  - compose-time-pipeline
  - residual-definitions
  - cert-obligations
  - residual-machinery
  - crystal-inputs
open-questions: []
---
# The pino-bridge exports

## The only surface

`pino-bridge` is the only surface the operator library — and any other
downstream consumer — sees of the oracle. It has two exports.

## Validate — the differentiated residual surface

```
Validate(state    : UnifiedState,           -- the seven-tuple of unified-state
         env      : Environment,
         request  : all | {ResidualKey} | {ObservableRef},
         gradient : Skip | Compute)
       → ( residuals : Map<ResidualKey, Scalar>
         , values    : Map<ObservableRef, Value>              -- bundled observable outputs
         , cograds   : Optional<Map<ResidualKey, Cotangent>>  -- the kernel's gradient map
         , cert      : CertEvidence )
```

A single entry point. `state` is [unified-state#slots] and `env` is
[crystal-inputs].

The `request` parameter selects which subgraph of the compiled kernel to
evaluate: the full graph, a subset of residual leaves keyed by `ResidualKey`, or
a subset of observables.

The `gradient` parameter toggles the adjoint. On `Skip` the kernel runs
forward-only, emitting residual values and observables without their cotangents.

The residual and cotangent maps are keyed and granular by construction
([residual-definitions#granularity]).

## Import — external ground truth

```
Import(named-target  : ObservableRef,
       value         : Value,
       standard-deviation : Scalar,
       provenance    : Provenance,
       axis-coverage : AxisCoverage)
     → GroundTruthBridgeGenerator
```

Per-target ingestion. Each call wraps **one** external datum — a VASP energy, an
experimental mobility curve, a curated battery row — as a
`GroundTruthBridgeGenerator`, the dataset analogue of the residual generator
([residual-machinery#generator-record]).

At the graph-construction stage ([compose-time-pipeline]) the generator inserts
a pinned `Input` node carrying `(value, standard-deviation)` and a **cert-only**
`ResidualLeaf` node keyed by the named target's `ResidualKey`
([physics-graph]).

`Import` is **not differentiated through**. Its residual-leaf outputs serve the
reference-battery obligation ([cert-obligations]) and feed the operator's
target-versus-prediction comparison.

## Axis coverage

`AxisCoverage` declares **which axis tuples of the named target the imported
datum actually constrains**. That is the only thing it means here.

It is not a per-sample applicability mask over a training batch, and it is not a
record of which labels are present from which source. Those are two different
objects, they live in the operator library, and they carry their own names. All
three multiply into the same loss term, so one name shared across them yields a
loss that is wrong and reports clean.

The wire format is a serialised **Roaring bitmap** over a flat index built from
the generator's `axes` ([residual-definitions#residualkey]):

```
flat-index(axes) = enumerate(product(axes))   -- lexicographic over axis values
RoaringAxisCoverage = serialised Roaring bitmap of selected flat-index positions
```

- **Sparse from the start.** Coverage is overwhelmingly sparse: a battery row
  touches one `(k-point, band)`; an experimental `σ(T)` curve touches one axis;
  a phonon-dispersion datum touches one branch over a one-dimensional `k`-path.
  Dense-with-compression buys nothing and forces a full decode before lookup.
- **Why Roaring.** O(1) membership; fast intersection, union and cardinality for
  the set operations the cert evaluator needs — *"which `(k, n)` pairs are
  covered by some battery row?"* — and an industry-standard format with bindings
  in every candidate language.
- **Persisted form.** The serialised bytes are stored in the axis-coverage
  column of the reference cache's entry table, and are part of the content
  address of a cache entry ([cert-obligations]).

## What is not exported

`Predict`, `Certify` and `EnumerateObservables` remain available as the oracle's
internal interface for non-operator consumers — the loops library, debugging
tools, the cert-only batch validator. They are not part of the pino-bridge
contract.

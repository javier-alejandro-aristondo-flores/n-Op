---
id: pino-bridge
title: "The pino-bridge exports"
owns:
  - the exported surface contract
  - Validate signature
  - Import signature
  - axis coverage of an imported datum
  - the evolver hand-off
  - steppable-form manifest fields
  - encoding validity domain
  - residual obligation map
anchors:
  surface: "The only surface"
  validate: "Validate — the differentiated residual surface"
  import: "Import — external ground truth"
  axis-coverage: "Axis coverage"
  steppable-form-manifest: "The evolver hand-off"
  encoding-validity-domain: "The encoding validity domain"
  obligation-map: "What the obligation map is for"
  not-exported: "What is not exported"
depends-on:
  - unified-state
  - physics-graph
  - compose-time-pipeline
  - residual-definitions
  - cert-obligations
  - residual-machinery
  - crystal-inputs
  - multiscale-state
  - gamma-hat
  - generic-dynamics
  - product
open-questions:
  - id: evolver-lowering-spec
    anchor: steppable-form-manifest
    summary: "The full lowering specification — the manifest record, the refusal enum, and the scorer-versus-evolver exactness obligation — is not written. No time-evolution product verb is claimed until it is."
---
# The pino-bridge exports

## The only surface

`pino-bridge` is the only surface the operator library — and any other
downstream consumer — sees of the oracle. It has three exports: `Validate` and
`Import` for a consumer that scores, and `dynamics` for a consumer that
integrates.

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
[crystal-inputs#environment].

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
`GroundTruthBridgeGenerator`, the dataset analog of the residual generator
([residual-machinery#generator-record]).

At the symbolic-lift stage ([compose-time-pipeline#symbolic-lift]) the generator
inserts a pinned `Input` node carrying `(value, standard-deviation)` and a
**cert-only** `ResidualLeaf` node keyed by the named target's `ResidualKey`
([physics-graph#node-kinds]).

`Import` is **not differentiated through**. Its residual-leaf outputs serve the
reference-battery obligation ([cert-obligations#the-ten-obligations]) and feed
the operator's target-versus-prediction comparison.

## Axis coverage

`AxisCoverage` declares **which axis tuples of the named target the imported
datum actually constrains**. That is the only thing it means here.

It is not a per-sample applicability mask over a training batch, and it is not a
record of which labels are present from which source. Those are two different
objects, they live in the operator library, and they carry their own names. All
three multiply into the same loss term, so one name shared across them yields a
loss that is wrong and reports clean.

The wire format is a serialized **Roaring bitmap** over a flat index built from
the generator's `axes` ([residual-definitions#residualkey]):

```
flat-index(axes) = enumerate(product(axes))   -- lexicographic over axis values
RoaringAxisCoverage = serialized Roaring bitmap of selected flat-index positions
```

- **Sparse from the start.** Coverage is overwhelmingly sparse: a battery row
  touches one `(k-point, band)`; an experimental `σ(T)` curve touches one axis;
  a phonon-dispersion datum touches one branch over a one-dimensional `k`-path.
  Dense-with-compression buys nothing and forces a full decode before lookup.
- **Why Roaring.** O(1) membership; fast intersection, union and cardinality for
  the set operations the cert evaluator needs — *"which `(k, n)` pairs are
  covered by some battery row?"* — and an industry-standard format with bindings
  in every candidate language.
- **Persisted form.** The serialized bytes are stored in the axis-coverage
  column of the reference cache's entry table, and are part of the content
  address of a cache entry ([cert-obligations#reference-cache]).

## The evolver hand-off

The oracle scores; it does not step. A consumer that *integrates* a tier
([multiscale-state#three-tiers]) calls `dynamics(tier)`, which hands back a
**causalized tangent kernel and a steppable-form manifest — not an
integrator**. Scheme choice, step-size control and the loop stay with the
caller.

```
dynamics(tier) exposes:
  tangent map           (state_tier, env, adiabatic-params) → tangent_tier;
                        a pure function
  generator sub-entries E, S, δE/δx, δS/δx and the L· / M· contraction blocks,
                        separately addressable — required by
                        degeneracy-respecting and discrete-gradient integrators
  algebraic subsystem   per-step solve plans, with an index-≤1 witness
  preservation grades   per-block generator tags
  obligation map        ResidualKey → conserve | bound | monotone
  cadence contract      the tier's cadence and its coupling to the others
  per-step cost         declared
  encoding validity domain
  sibling fingerprint   and the certificate reference
```

It is a flag-gated sibling emission at the lowering stage
([compose-time-pipeline#lowering-and-adjoint-synthesis]) sharing the scorer's
content-addressed right-hand-side forests: one extraction, two lowerings.
Score-not-solve survives it, because the hand-off is a per-call readout of the
instantaneous lawful tendency and never a trajectory
([product#score-not-solve]).

### The encoding validity domain

The oracle is scorer-only ([gamma-hat#scorer-only]), so nothing accumulates
here — and a consumer that integrates a tier inherits the representation-health
problem along with the tangent map. The manifest therefore declares the encoding
each block was compiled against, and the conditions under which that encoding
stops being a fair approximation: the `CompressionPlan` slot, its rank, and its
truncation target.

**Exporting the problem is legitimate; exporting it silently is not.**

### What the obligation map is for

`conserve | bound | monotone` is not an arbitrary vocabulary. It is the
vocabulary the robust dynamical-low-rank literature states its guarantees in, so
a consumer can match an integrator to the obligations term for term.

The named family is the **rank-adaptive basis-update-and-Galerkin integrator**
(Ceruti, Kusch & Lubich, *BIT* 62, 2022). Up to a declared truncation tolerance
it preserves:

- the norm, where the equation does — `conserve`, for instance `Tr γ̂`;
- the energy, for Hamiltonian systems — `conserve`, the `L` block;
- monotone decrease of the functional in gradient flows — `monotone`, the `M`
  block.

The blocks are [generic-dynamics#operators], so the three guarantees map
term-for-term onto the structure the residuals are written against.

Its error bounds are **independent of small singular values** — Ceruti & Lubich,
*BIT* 62(1) 23–44 (2022), which carries that robustness over to this family;
first proved for projector splitting by Kieri, Lubich & Walach, *SIAM J. Numer.
Anal.* 54 (2016), projector splitting itself being Lubich & Oseledets, *BIT* 54
(2014). That is the property no standard integrator has, and the one that makes
a low-rank density matrix safe to step at all.

**Naming the family is a declaration, not an implementation obligation.** The
oracle guarantees exactness against its scorer sibling, tag totality, structural
witnesses and refusal accounting. The consumer — the operator library, an
integration harness in the loops library, or a user program — owns scheme
choice, step-size control and the loop.

## What is not exported

`Predict`, `Certify` and `EnumerateObservables` remain available as the oracle's
internal interface for non-operator consumers — the loops library, debugging
tools, the cert-only batch validator. They are not part of the pino-bridge
contract.

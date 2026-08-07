---
id: learnable-structure-contract
title: "The learnable-structure contract"
owns:
  - operator-oracle seam obligations
  - state emission obligations
  - seam loop-agnosticism
  - operator architecture motivation
  - seam exclusions
anchors:
  scope: "What this contract fixes"
  why-an-operator: "Why an operator"
  loop-agnostic: "Loop-agnostic, by the two-loop symmetry"
  state-emission: "Emit the state in the oracle's type"
  evaluate-at-points: "Evaluate at points"
  vector-jacobian-product: "Vector–Jacobian product at the state boundary"
  conditioning-inputs: "Conditioning inputs"
  seam-purity: "Seam purity and determinism"
  batch-axis: "Batch axis"
  content-addressable-identity: "Content-addressable identity"
  loop-drivability: "Loop-drivability"
  optional-offers: "Optional offers"
  out-of-scope: "What the oracle does not ask about"
depends-on:
  - unified-state
  - product
  - representation-substrate
  - residual-definitions
  - compose-time-pipeline
  - pino-bridge
  - crystal-inputs
  - multiscale-state
  - purpose-and-scope
  - boundary
  - training-stages
open-questions:
  - id: environment-schema-at-the-seam
    anchor: conditioning-inputs
    summary: "The seam obliges the operator to accept the environment record as named typed conditioning channels, but no page fixes that record's field list, units or admissible ranges — so the obligation names a channel whose contents cannot be checked."
---
# The learnable-structure contract

## What this contract fixes

The **minimum observable behavior the oracle library requires of the operator at
their shared boundary** — and nothing about its interior.

Coupling between the two libraries is confined to what crosses the bridge
([pino-bridge#surface]), so this page is the complete list of demands. Everything
else about the operator's learnable structure is its own business.

## Why an operator

The problem asks for an operator. Not because of what an operator is, but because of
five properties this problem needs and a fixed-width predictor cannot supply.

| Property | Why it matters here |
|---|---|
| **Function-valued outputs** | the one-body density matrix is a function of two spatial points; the vector potential is a function of space and time; conductivity against temperature is a curve; the phonon density of states is a spectrum. A fixed-width output layer has to choose a discretization and bake it in |
| **Discretization invariance** | supercell size and reciprocal-space mesh density vary across the problem. A mesh-bound model is retrained per mesh; one set of weights carries across meshes |
| **Evaluation at arbitrary points** | the oracle scores residuals at axis points lying nowhere on the training grid. Interpolating after the fact is a second model with its own error |
| **Nonlocal kernels** | electronic structure is nonlocal — long-range Coulomb, collective phonon modes. An integral kernel couples the whole cell in one layer; a local stencil needs depth to move information across it |
| **Amortized solution map** | what is learned is the map from topology and partial properties to the rest of the state, not one solution. A new material is a forward pass, not a new solve |

The load-bearing one is evaluation at arbitrary points, and it is a contracted
requirement below.

**Architecture and training regime are two axes, and conflating them is an error.**
Fourier neural operator, branch-trunk operator, graph neural operator — that is one
choice. Supervised epochs followed by an informed epoch ([training-stages]) is a
different one. Neither constrains the other.

## Loop-agnostic, by the two-loop symmetry

Two loops drive this seam, and [product#two-loops] says what each does with the
gradient. What matters here is that **the seam does not distinguish them**: same
emission, same cotangent intake, same requirements, and no requirement below names a
loop.

That is what lets the loops library own the loop without the contract knowing which
loop it is.

## Emit the state in the oracle's type

Emitted candidates are the seven-slot state exactly as [unified-state#slots] defines
it: slot set, per-slot array shapes and layouts, units, and the gauge conventions
recorded there. Slots are addressed by the ordinal handles of the typed indexed
universe ([representation-substrate#primitives]), never by ad-hoc names.

That sentence asks for more than the target currently fixes. The gauge conventions are
recorded; which of the rest are specified and which are not is stated at
[unified-state#wire-schema], and this requirement tightens as that page does.

**Structural** well-formedness is mandatory at the seam: correct shapes, finite
IEEE-754 double precision. Internal training precisions are the operator's own
business — convert before the boundary.

**Physical** admissibility is *not* required. Admissibility is scored, never
presupposed: [residual-definitions#categories] owns the admissibility categories and
[purpose-and-scope#why-a-grader] owns score-not-solve. Emitting a structurally valid
but physically poor state is normal operation. That is what the residual surface is
for.

## Evaluate at points

The compiled oracle kernel for an instance carries instance-specific,
symmetry-quotiented axis grids fixed at compose time
([compose-time-pipeline#symmetry-quotient]). Given per-channel lists of query
coordinates, the operator returns that channel's values **at exactly those points**.
Emission on a fixed internal mesh with caller-side interpolation does not satisfy this.

This is discretization invariance made concrete, and it is the single most load-bearing
requirement of the seam: if the operator could answer only on its training grid, the
residual could not be scored where the physics asks. How the kernel realizes it
internally — spectral trunk, point branch, anything else — is unconstrained. Only the
query behavior is contracted.

## Vector–Jacobian product at the state boundary

Accept a cotangent structured like the emitted state, and backpropagate it to internal
parameters.

The oracle returns *per-key* cotangents ([pino-bridge#validate]). The external loop
linearly combines them into **one** state-shaped cotangent before handing it over, so
a single vector–Jacobian application per state-and-combined-cotangent pair is
sufficient. Per-key application is not required.

## Conditioning inputs

Accept the environment record, and the query time, as named typed conditioning
channels ([crystal-inputs#environment]). Emitted state is conditioned on environment;
the environment is an input the kernel never invents and never mutates.

The channel is named here; its contents are not fixed anywhere the seam can point to.
Until they are, this requirement obliges a shape no checker can verify.

## Seam purity and determinism

Only flat numeric arrays cross the boundary — no framework tensors with attached tapes,
no lazy graphs, no callbacks.

Inference-mode emission is deterministic, bitwise, for fixed inputs and fixed identity,
so content-addressed caching holds. Hashing applies the float normalization of
[representation-substrate#serialization]: canonical quiet not-a-number, negative zero
mapped to positive zero. A not-a-number or an infinity in an emitted state is already a
finiteness violation upstream of any hash.

## Batch axis

Emission and cotangent intake carry a leading batch dimension. Batch elements are
independent: no cross-batch coupling is observable at the seam.

## Content-addressable identity

Every operator instance — architecture, weights, version — exposes one stable content
hash, aligned with the addressing discipline of
[representation-substrate#identity-exact], so that any
residual map is permanently attributable to the pair *(oracle kernel hash × operator
hash)*. Retraining or a structural edit gives a new hash.

## Loop-drivability

The learnable structure never owns the loop. Emission and cotangent intake are plain
calls that an external driver interleaves with the oracle's validation call
([pino-bridge#validate]) at its own cadence. Loop logic — batching policy, curricula,
active learning, design search — lives in the loops library ([boundary]). No control
inversion, no required callbacks.

## Optional offers

Two offers. Neither blocks anything, and neither is an ask.

**Structure-plan intake.** The oracle's symmetry sidecar carries per-instance symmetry
structure: irreducible-representation blocks, orbit maps, per-channel group actions
([compose-time-pipeline#symmetry-quotient]). If the operator can consume a
compile-time descriptor of that shape and bake weight sharing or equivariance into a
compiled structure, the
corresponding equivariance residuals go to zero by construction. The oracle scores
equivariance either way.

**Per-slot update rates.** The state's tiers evolve at heterogeneous rates
([multiscale-state#three-tiers]). If the kernel supports per-slot update rates in a
compiled structure, a future multi-rate driver can exploit that. Nothing currently
depends on it.

## What the oracle does not ask about

- Internal architecture: layer types, trunk-and-branch decomposition, how
  hybridization is realized.
- Training numeric types, mixed precision, sharding, internal memory layout.
- Optimizer, schedules, initialization, regularization.
- How the operator declares, lowers, fuses or caches its own structures.
- Where weights live or how checkpoints are stored. Only the content hash is visible.
- Anything about the loop. Loop-drivability is the whole statement.

A need falling outside this list enters by amending this contract — never by reaching
through the seam.

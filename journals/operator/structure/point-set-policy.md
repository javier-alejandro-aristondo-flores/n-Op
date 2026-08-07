---
id: point-set-policy
title: "The point-set policy"
owns:
  - the point-set-policy constituent
  - the cadence-sampler-importance record
  - intermediate point-set selection
  - the importance function's typed home
anchors:
  scope: "What a point-set policy is"
  the-record: "The record"
  importance: "The importance function"
  intermediate: "Point sets between transforms"
  who-supplies: "Who supplies the terminal point set"
  defaults: "Defaults"
depends-on:
  - operator-decomposition
  - integral-transform
  - integration-domain
  - residual-loss-design
  - learnable-structure-contract
open-questions:
  - id: point-count-budget
    anchor: intermediate
    summary: "A policy chooses a point set at every stage of a stack of transforms, and nothing bounds how the count varies from stage to stage. A policy that refines at each stage multiplies the cost of every stage after it, and no constituent holds the budget that would stop it."
  - id: policy-under-batch
    anchor: the-record
    summary: "The seam requires a leading batch dimension with independent elements, and an importance function ranking candidate points by residual magnitude ranks them per sample. Whether a batch shares one point set or carries one per element is unfixed, and the two differ in cost by the batch size."
---
# The point-set policy

## What a point-set policy is

The constituent that decides **which points a transform is asked to answer at**
([operator-decomposition#five-constituents]). A transform answers wherever it is asked and
holds no opinion about where ([integral-transform#signature]); this is where the opinion
lives.

Separating them is what makes both swappable. A transform that chose its own points would
bind the sampling question to the evaluation question, and the two are independent: an
adaptively refined point set is as meaningful under dense quadrature as under a
neighborhood subsample.

## The record

A point-set policy is three things, and one record carries all three.

```
PointSetPolicy = ( cadence      -- how often
                 , sampler      -- how points are drawn
                 , importance )  -- optional; how candidates are ranked
```

**Cadence** is how often the point set is redrawn. Its four values are the operator
library's, and [residual-loss-design#cadence] specifies them and binds each to an
evaluation cost. This page reuses that vocabulary and does not restate it.

**Sampler** is how points are drawn from the integration domain: the domain's own
enumeration, a uniform random draw, a refinement of a previous set, or an explicit list
supplied by a caller. The domain owns what points exist
([integration-domain#scope]); the sampler owns which of them are taken.

**Importance** is optional and, where present, ranks candidate points so a sampler can
prefer some over others.

## The importance function

The importance function is a map from a candidate point to a scalar preference. It is the
field that gives residual-adaptive sampling somewhere to put its ranking, and it is
optional because a uniform sampler needs none.

Its typed home is this record. That placement is deliberate: an importance function
belongs neither to the oracle, which owns no loop and therefore no notion of how often
anything is drawn, nor to the loss, which consumes values at points already chosen. It
belongs to the constituent that chooses points, and the strategies it can express are
surveyed at [residual-loss-design#sampling].

## Point sets between transforms

A stack of transforms poses the question the terminal point set does not answer. If a
transform answers at some set of points, a transform consuming that answer integrates over
**that** set, so something has to choose it.

The policy does, at every stage. Three consequences:

- **No internal grid exists.** A stack has no privileged discretization that a later stage
  is bound to, so the seam's demand for arbitrary-point evaluation is met throughout rather
  than by one final interpolation ([learnable-structure-contract#evaluate-at-points]).
- **Refinement is expressible mid-stack.** A stage may be given more points than its
  predecessor, which is what residual-adaptive refinement requires and what a fixed grid
  forecloses.
- **The point set is an experimental axis.** Holding the integral kernel, the strategy and
  the domain fixed and varying only the intermediate point counts is a controlled
  measurement of how much of a result is discretization.

The cost of the third is that nothing bounds the counts, which is carried as an open item
above.

## Who supplies the terminal point set

The point set at the end of the stack is **not** the policy's. It is supplied by whoever
consumes the answer, and during the informed stage that consumer is the loss: the oracle
scores each residual at the axis points the compiled kernel carries, and the operator is
asked for values at exactly those.

The policy therefore governs the interior of a stack and stops at its output. A policy
that overrode the terminal set would be answering a question the oracle has already
answered, and the values scored would sit somewhere other than where the residual is
defined.

## Defaults

- **Uniform sampling from the domain's own enumeration**, at the coarsest cadence, with no
  importance function. This reproduces a fixed-grid operator exactly and is the baseline
  every other policy is measured against.
- **One policy per stack**, not one per transform, until a measurement shows per-stage
  policies matter.
- **The terminal set is never defaulted.** It is supplied or the call is incomplete.

The residual-side defaults — which residuals are evaluated at which cadence, and which are
importance-sampled by residual magnitude — belong to the loss and are stated at
[residual-loss-design#defaults]. They consume this record and do not restate it.

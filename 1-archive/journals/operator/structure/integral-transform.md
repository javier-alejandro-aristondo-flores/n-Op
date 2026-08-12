---
id: integral-transform
title: "The integral transform"
owns:
  - the integral-transform constituent
  - the transform signature
  - the resampling responsibility
  - the nonlocality budget
  - quadrature-error declaration
  - cross-domain tier coupling
  - transform exclusions
anchors:
  scope: "What the integral transform is"
  signature: "The signature"
  resampling: "Resampling is the whole job"
  measure: "Applying the weights"
  support: "The nonlocality budget"
  error-declaration: "Declaring the quadrature error"
  tier-coupling: "Two domains is a change of scale"
  exclusions: "What the transform does not own"
depends-on:
  - operator-decomposition
  - integration-domain
  - evaluation-strategies
  - point-set-policy
  - learnable-structure-contract
  - multiscale-state
  - residual-definitions
  - pino-bridge
open-questions:
  - id: stacked-error-composition
    anchor: error-declaration
    summary: "Each transform declares its own quadrature error, and nothing composes the declarations across a stack of transforms. A three-transform stack therefore has three per-application error statements and no end-to-end one, so a residual scored on its output cannot be attributed between physics and quadrature."
  - id: transform-cotangent-through-weights
    anchor: measure
    summary: "The seam takes one state-shaped cotangent and requires it be backpropagated to internal parameters. Where the quadrature weights are themselves differentiable in a predicted quantity, the transform has two routes to the parameters and no page states whether both are taken."
---
# The integral transform

## What the integral transform is

The constituent that applies an integral kernel to a function and returns a function. It
owns the discretization ([operator-decomposition#discretization-contract]) and nothing
else — no learnable parameter of its own, no opinion about physics, no loop.

## The signature

```
apply : Transform -> Function -> QueryPoints -> Function

Transform = ( integral kernel
            , input integration domain
            , output integration domain
            , evaluation strategy )
```

Three properties of that signature carry the design.

**Query points are an argument, not a field.** A transform that fixed its own output
points could not answer the seam's demand for values at coordinates lying nowhere on any
grid it holds ([learnable-structure-contract#evaluate-at-points]). Which points get
supplied is a separate constituent's business ([point-set-policy]).

**Two integration domains, not one.** Input and output are named separately even when
they are the same domain, because the case where they differ is the useful one, below.

**The return is a function, not an array.** It carries a reference to the output
integration domain ([integration-domain#sharing]), so a transform downstream inherits the
geometry rather than assuming it.

## Resampling is the whole job

An integral kernel takes two arguments and they do not play the same role. One ranges over
the point set the input function is sampled on. The other ranges over the point set the
answer is wanted on. **The transform is the only constituent with both in scope**, and
that is the structural reason arbitrary-point evaluation is its responsibility and could
not have been anyone else's.

An integral kernel evaluated at a pair of points knows nothing about either point set. A
function is samples against one domain and cannot produce another. A pointwise map cannot
change a discretization at all, and neither can a fixed-stencil operation.

**The change of discretization is the operation.** Everything else the transform carries
is machinery for performing it correctly, which is why "resample, then apply an integral
kernel" is not an available decomposition — the resampling is what applying the integral
kernel *is*.

This also settles what a stack of transforms means. Each application answers wherever it
is asked, so no internal grid exists for a later application to be trapped on, and the
error a caller-side interpolation would introduce never arises.

## Applying the weights

The transform multiplies each contribution by the quadrature weight its input integration
domain supplies ([integration-domain#weights]) and reduces. It does not choose the
weights, compute them, or override them.

That division matters under gradient. Where a weight is differentiable in a predicted
quantity — the real-space cell volume being the case that occurs here
([integration-domain#state-dependent]) — the transform is the site where that dependence
enters the contraction, and the seam requires the result be backpropagated to internal
parameters ([learnable-structure-contract#vector-jacobian-product]). The transform
therefore has two routes to the parameters, through the integral kernel and through the
weights, and which are taken is carried as an open item above.

## The nonlocality budget

The integral kernel says how strongly two points couple. **The transform says which pairs
are considered at all.** Truncation radius, screening length, sparsity pattern, and the
density of the point set swept are all decisions about the domain of integration rather
than about the coupling.

This is physics, not tuning. A long-range interaction cannot be truncated without changing
the operator; a short-range one can be truncated at a stated radius with a stated error.
The seam's argument for wanting an operator at all rests on nonlocal integral kernels
coupling a whole cell in one application ([learnable-structure-contract#why-an-operator]),
and a truncation silently applied is that argument withdrawn without notice.

The budget is declared with the error, below, because a truncation is exactly a case of
computing a different operator than the one requested.

## Declaring the quadrature error

The transform is the only constituent that knows both the operator it was asked for and
the operator it applied. **It publishes the gap.**

The declaration carries the strategy's exactness for the integral kernel's structure class
([evaluation-strategies#declaration]), the truncation applied, and the quadrature rule's
error class for the point count in play. It is a value the transform returns, not a log
line, so a consumer that ignores it has to ignore it explicitly.

Two precedents in the corpus say why silence is not available. The oracle hands a
consumer that integrates a tier the encoding each block was compiled against and the
conditions under which that encoding stops being fair, on the principle that exporting a
problem is legitimate and exporting it silently is not
([pino-bridge#encoding-validity-domain]). And a discretization chosen wrongly makes the
residual operator itself wrong at the operating point, so that what gets scored is a
discretization artifact rather than the physics ([multiscale-state#eom-continuum]).

**The second is the mirror of this page.** That statement is made about the oracle's
finite-volume residual; it is equally true of the transform's quadrature, and the operator
library has no compose-time refusal to fall back on. The declaration is the whole of the
defense. Where the declaration feeds an error budget, the budget's model-form term is the
oracle's ([residual-definitions#error-budget]).

## Two domains is a change of scale

When a transform's input and output integration domains differ, the operation is a change
of discretization **between measure spaces**, and that is not a special case to be handled
elsewhere — it is what the signature already describes.

The micro-to-macro coupling is one instance. Mapping a per-composition micro output onto a
macro coefficient on the device mesh ([multiscale-state#homogenization-map]) is a transform
whose input domain is the periodic cell and whose output domain is the mesh. The three
tiers stay stratified ([multiscale-state#three-tiers]) and the coupling between them stops
needing separate machinery.

The same shape covers the reverse direction and the slow tier's discrete domain. What makes
it work is that domain identity is decidable ([integration-domain#sharing]): *"the domains
differ"* is a fact about content addresses, not a naming convention.

## What the transform does not own

- **The pointwise linear term, the bias and the nonlinearity.** These are properties of
  whatever composes transforms, not of a transform.
- **Lifting and projection.** Raising a function to a wider channel count and lowering it
  again are pointwise maps that change no discretization.
- **The integral kernel's structure.** The transform requires only that a structure class
  be declared ([evaluation-strategies#kernel-classes]).
- **The point sets.** Supplied, never chosen ([point-set-policy]).
- **The quadrature weights.** Applied, never computed ([integration-domain#weights]).
- **The loop, the batching policy and the schedule.** These belong outside the operator
  library entirely.

Nothing on that list has an owner in this section, and the composition of several
transforms is the gap that follows from it
([operator-decomposition#boundaries]).

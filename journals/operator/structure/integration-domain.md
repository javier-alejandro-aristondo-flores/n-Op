---
id: integration-domain
title: "The integration domain"
owns:
  - the integration-domain constituent
  - quadrature weight sourcing
  - the four integration domains
  - integration-domain sharing
  - the discretization-invariance mechanism
  - state-dependent domain geometry
anchors:
  scope: "What an integration domain is"
  the-four: "The four integration domains"
  weights: "Where a quadrature weight comes from"
  invariance: "Discretization invariance is a property of the weights"
  symmetry: "The symmetry quotient"
  state-dependent: "The real-space domain is state-dependent"
  sharing: "Referenced, never owned"
depends-on:
  - operator-decomposition
  - integral-transform
  - unified-state
  - multiscale-state
  - compose-time-pipeline
  - representation-substrate
  - learnable-structure-contract
open-questions:
  - id: measure-gradient-route
    anchor: state-dependent
    summary: "The real-space quadrature weights are a function of the cell vectors, which the operator predicts, so the weights are differentiable in a predicted quantity. Whether a gradient is taken through the weights or they are frozen per step is unfixed, and the two differ by a volume term that grows with the strain the sweep reaches."
  - id: brillouin-weight-provenance
    anchor: weights
    summary: "Orbit multiplicities for the irreducible wedge are fixed by the oracle's symmetry quotient at compose time, and no page states whether the operator receives them across the seam or recomputes them. Recomputing invites two answers to one question; receiving them adds a channel the seam does not currently carry."
---
# The integration domain

## What an integration domain is

An **integration domain** is the measure space a function lives on and a transform
integrates over. It carries five things:

- **periodicity** — whether, and along which directions, the domain wraps;
- **a metric** — what the distance between two of its points is;
- **quadrature weights** — what each point contributes to a sum standing in for an
  integral;
- **a symmetry quotient** — which points are representatives of orbits rather than
  distinct degrees of freedom;
- **a point enumeration** — the ordered set of points the domain admits, addressed by
  the dense ordinal handles of the typed indexed universe
  ([representation-substrate#primitives]).

It carries no learnable parameter and no value. It is geometry, and it is the constituent
that makes the other four portable across scales
([operator-decomposition#five-constituents]).

## The four integration domains

| Integration domain | What it is | Quadrature weight |
|---|---|---|
| **Real-space periodic cell** | the crystallographic unit cell, as a torus | the cell volume, from the cell vectors |
| **Symmetry-quotiented Brillouin zone** | the irreducible wedge of reciprocal space | the orbit multiplicity of the representative |
| **Defect species against site** | a discrete index set with no metric | unit — a counting measure |
| **Finite-volume device mesh** | real-space mesh cells with faces and centroids | the mesh cell volume |

These are four measure spaces, not four coordinate systems, and the difference is the
weight column. The three state tiers carry three of them and are not unifiable into one
array for exactly that reason ([multiscale-state#three-tiers]); the device mesh is the
macro tier's ([multiscale-state#device-mesh]).

**A domain with no metric still integrates.** The species-against-site domain has no
notion of distance, and its transform is a sum over a discrete index with unit weights.
Nothing in the constituent requires a metric — only a weight.

## Where a quadrature weight comes from

A weight is never a hyperparameter. Each domain sources its weights from something the
domain already knows:

- the periodic cell, from the determinant of its cell vectors, divided across its point
  enumeration;
- the Brillouin wedge, from the multiplicity of each representative's orbit under the
  crystal symmetry group;
- the discrete domain, from unity;
- the device mesh, from the per-mesh-cell volume the mesh carries.

Weights that are guessed produce an operator that is internally consistent and wrong by a
constant, which is the class of defect no residual can name — every law is violated by the
same factor, so the violation reads as a scale error in the learnable structure rather
than as a defect in the sum.

## Discretization invariance is a property of the weights

**Not of the architecture.** The integral kernel does not know how many points there are;
a function is only values. The weights are the sole place the point count enters, and
therefore the sole place invariance can be established or lost.

An unnormalized sum grows with the point count. A transform built on one grows with it
too, silently: the structure trains at one mesh density, reports every metric green, and
returns values scaled by a ratio of point counts the first time it is asked at another.
Nothing downstream distinguishes that from a poorly fitted structure.

This is why the seam can demand evaluation at points lying nowhere on the training grid
([learnable-structure-contract#evaluate-at-points]) and have the demand be satisfiable.
The demand is satisfiable because the weights, not the grid, carry the measure.

## The symmetry quotient

The oracle's compiled kernel fixes instance-specific, symmetry-quotiented axis grids at
compose time ([compose-time-pipeline#symmetry-quotient]). A domain built on a quotient
holds representatives, not points, and its weights are orbit multiplicities.

Two consequences, and both bite:

- **A sum over representatives is not a sum over the zone.** It is a sum over the zone
  only when each representative is weighted by its orbit size. An unweighted sum over an
  irreducible wedge is a different quantity with no name.
- **A transform that emits at arbitrary points may be asked outside the wedge.** The
  domain owns the group action that maps such a query back to its representative. That
  map belongs to the domain because it is geometry, and placing it in the transform would
  duplicate it once per transform.

## The real-space domain is state-dependent

The real-space periodic cell's geometry is the cell vectors, which are a slot of the state
([unified-state#slots]) — a quantity the operator predicts.

**So the domain of integration depends on the operator's own output.** Its quadrature
weight is the cell volume, which is the determinant of a predicted array, and the metric
that decides which two points are near each other through the periodic wrap is predicted
too.

Two things follow that are easy to miss and expensive to find later:

- **A gradient can flow through the weights.** The volume is differentiable in the cell
  vectors, so the loss has a route to the structure through the measure and not only
  through the integral kernel. Whether that route is taken is unfixed, above.
- **The strain regime makes the term large.** The diamond sweep reaches Green–Lagrange
  strain approaching fifteen percent, so the cell volume is not approximately constant
  across the corpus and a frozen weight is not approximately right.

The other three domains are static. The mesh is generated once, the wedge follows the
symmetry group, and the discrete domain is an index set. **Only the real-space domain
moves**, and it moves because the thing it is made of is being predicted.

## Referenced, never owned

A function references an integration domain. A transform references an integration domain.
Neither owns one, and two constituents over the same physical region reference the *same*
domain rather than two equal copies.

Equal copies are the failure this rule exists to prevent. Two copies that agree today
disagree after one is edited, and the disagreement surfaces as a quadrature mismatch
between two transforms that a reader has every reason to believe integrate over the same
region.

Identity is therefore by content address, on the same discipline the substrate applies to
everything else it shares ([representation-substrate#identity-exact]), so that
*"the same domain"* is decidable rather than a matter of convention. A transform's input
and output domains being distinct is meaningful precisely because sameness is decidable
([integral-transform#tier-coupling]).

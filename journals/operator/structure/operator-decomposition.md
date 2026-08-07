---
id: operator-decomposition
title: "The operator's interior decomposition"
owns:
  - operator interior decomposition
  - the five learnable constituents
  - constituent boundary rules
  - the discretization-contract principle
  - function representation
  - integral-kernel qualifier
anchors:
  scope: "What this page fixes"
  five-constituents: "The five constituents"
  qualifier: "Why the integral kernel carries a qualifier"
  discretization-contract: "The integral transform is a discretization contract"
  function: "What a function is here"
  boundaries: "What crosses each boundary"
  swappability: "Swappable, and what it costs"
  unwritten: "What is not written here"
depends-on:
  - learnable-structure-contract
  - integration-domain
  - integral-transform
  - evaluation-strategies
  - point-set-policy
  - residual-loss-design
  - multiscale-state
  - unified-state
  - glossary
open-questions:
  - id: transform-stack-owner
    anchor: boundaries
    summary: "The integral transform excludes the pointwise linear term, the bias, the nonlinearity, the lifting and the projection, and no page owns them. A stack of transforms is therefore not a specified object: the five constituents describe one application of one transform, and what composes several is unfixed."
  - id: function-carrier-representation
    anchor: function
    summary: "A function is sampled values against an integration domain, and a spectral evaluation strategy's natural carrier is basis coefficients rather than samples. Which carriers a function may take, and which constituent converts between them, is unfixed — and the conversion is lossy in one direction."
---
# The operator's interior decomposition

## What this page fixes

The operator library's learnable structure is assembled from five **constituents**. This
page names them, states the boundary between each pair, and fixes the one principle that
decides which constituent a responsibility belongs to.

The seam contract fixes what the oracle observes at the shared boundary and declines to
constrain anything inside it ([learnable-structure-contract#out-of-scope]). This page is
inside it. Nothing here amends the seam, and the dependency runs one way — the interior
cites the seam, and the seam names no constituent.

## The five constituents

| Constituent | What it owns | Specified in |
|---|---|---|
| **Integration domain** | periodicity, metric, quadrature weights, symmetry quotient, point enumeration | [integration-domain] |
| **Function** | sampled values, and the integration domain they are sampled against | this page |
| **Integral kernel** | the learnable coupling between two points | not yet written |
| **Integral transform** | the terms on which an integral kernel and a function meet | [integral-transform] |
| **Point-set policy** | which points a transform is asked to answer at | [point-set-policy] |

The evaluation strategy is not a sixth constituent. It is a field of the integral
transform, swappable independently of it, and it carries enough structure to need its own
page ([evaluation-strategies]).

The loss is not on this list either, and for a stronger reason: it is not in the forward
pass at all. It consumes emitted values and returns a scalar
([residual-loss-design#loss-structure]).

## Why the integral kernel carries a qualifier

**The integral kernel is never written bare.** `kernel` is reserved for the compiled
oracle artifact, and every other sense carries a qualifier — the same discipline that
gives the corpus its collision kernel and its response kernel
([glossary#overloaded]).

This is not a formatting preference. An operator library and an oracle library that both
say *kernel* produce sentences like *"the kernel's gradient"* that are true of two
different objects, and the reader who resolves it wrongly gets a coherent and incorrect
picture. The qualifier is what makes the sentence decidable.

## The integral transform is a discretization contract

The reading under which the transform looks like a holder of two other objects — *an
integral kernel times a function, summed* — smuggles in an assumption: that the
discretization is already given. Once it is, the transform really does collapse to a
matrix-vector product, and there is nothing left in it worth a page.

The discretization is not given. It is chosen. **Every responsibility the integral
transform carries follows from owning that choice**, and that single sentence is the rule
for where a responsibility goes.

Six follow, each stated where it is owned:

- **Resampling.** The two arguments of an integral kernel do not play the same role: one
  ranges over the input's point set, the other over the output's. The transform is the
  only constituent with both in scope ([integral-transform#resampling]).
- **Quadrature weights.** Discretization invariance is a property of the weights, not of
  the architecture ([integration-domain#invariance]).
- **Evaluation strategy.** Which factorization computes the contraction, and what it
  costs in exactness ([evaluation-strategies#admissibility]).
- **Nonlocality budget.** The integral kernel says how strongly two points couple; the
  transform says which points are considered at all
  ([integral-transform#support]).
- **Quadrature error.** The gap between the operator asked for and the operator applied
  ([integral-transform#error-declaration]).
- **Cross-tier coupling.** An input integration domain differing from the output one is a
  change of discretization across scales rather than a special case
  ([integral-transform#tier-coupling]).

Strip those six out and what remains is a contraction of two arrays. **The container
reading is right about the remainder and wrong about the constituent.** The integral
transform does not hold an integral kernel and a function together; it holds them apart,
and states the terms on which they meet.

The converse is worth stating because it bounds the claim. Fix one discretization
permanently and five of the six evaporate, leaving a contraction. The integral transform
is thick exactly to the degree that discretization is a free variable.

## What a function is here

A **function** is sampled values together with the integration domain they are sampled
against. It owns the values. It references the domain and does not own it.

That split is what makes the domain swappable. Were the geometry carried on the function,
two functions over one physical region could disagree about that region's periodicity or
its quadrature weights, and nothing would be positioned to notice. Were it carried on the
transform, two transforms could disagree the same way. One referent, cited by both, cannot
disagree with itself.

The state's seven slots ([unified-state#slots]) instantiate functions over four different
integration domains, which is why the domain is a reference rather than a global.

## What crosses each boundary

| From | To | What crosses |
|---|---|---|
| Function | Integral transform | values, and a reference to an integration domain |
| Integration domain | Integral transform | quadrature weights, metric, periodicity, point enumeration |
| Integral kernel | Integral transform | coupling values at requested point pairs, and a declared structure class |
| Point-set policy | Integral transform | the points to answer at |
| Integral transform | Function | values at those points, and a reference to the output integration domain |

The integral kernel never sees a quadrature weight, and the integration domain never sees
a learnable parameter. Those two exclusions are what keep the axes independent enough to
be measured against one another.

## Swappable, and what it costs

Every constituent is swappable, and the framework admits the full cross-product of
integration domain, integral kernel, evaluation strategy, point-set policy and loss.

**Most cells of that product are not exact**, because an evaluation strategy is exact only
for integral kernels of a particular structure class. The operator library admits them
anyway and publishes what it actually computed
([evaluation-strategies#declaration]). It does not refuse.

That is a deliberate departure from the oracle's compose-time refusal, and the two are
consistent because the libraries do different jobs. **The oracle refuses because a grade
it cannot stand behind is worse than no grade. The operator declares because an experiment
that cannot be run is worse than one whose error has to be accounted for.**

The obligation the departure creates is that the declaration must reach something. A
declaration nothing consumes leaves the library wrong and reporting clean, which is the
failure the seam's content-addressed identity exists to prevent
([learnable-structure-contract#content-addressable-identity]).

## What is not written here

**The integral kernel has no page.** This decomposition states only what the integral
transform requires of one — that it declare a structure class
([evaluation-strategies#kernel-classes]) and answer at requested point pairs. Nothing here
presupposes what the integral kernel turns out to be.

**No substrate is committed.** Signatures throughout the section are given as types, in
the same form the oracle pages use. A constituent is specified by what crosses its
boundary and not by where its code sits, so an implementation may realize several
constituents in one file, or one across several, without contradicting anything here.

**The three tiers are not unified.** The micro, slow and macro tiers carry three
incompatible discretizations ([multiscale-state#three-tiers]), and this decomposition
does not flatten them. It makes the difference expressible: a transform whose input and
output integration domains differ is exactly a change of scale.

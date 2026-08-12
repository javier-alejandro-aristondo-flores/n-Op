---
id: evaluation-strategies
title: "Evaluation strategies"
owns:
  - the evaluation-strategy field
  - integral-kernel structure classes
  - the strategy admissibility table
  - the strategy declaration record
  - strategy identity
  - operator families as strategy cells
anchors:
  scope: "What an evaluation strategy is"
  kernel-classes: "The structure classes an integral kernel declares"
  strategies: "The five strategies"
  admissibility: "Which pairings are exact"
  families: "The named operator families are cells of this table"
  declaration: "The declaration record"
  identity: "The declaration is part of identity"
depends-on:
  - operator-decomposition
  - integral-transform
  - integration-domain
  - learnable-structure-contract
  - residual-loss-design
open-questions:
  - id: strategy-in-the-content-hash
    anchor: identity
    summary: "The seam requires one stable content hash per operator instance over architecture, weights and version, and this page requires the strategy declaration to enter it. Whether a strategy counts as architecture is a statement the seam has to make, and it does not yet make it — so two instances differing only in strategy may currently share a hash."
  - id: kernel-class-completeness
    anchor: kernel-classes
    summary: "Four structure classes are stated, and the page that specifies the integral kernel is unwritten. Whether the classes are exhaustive, and whether an integral kernel may declare more than one, are decided by that page and assumed here."
  - id: approximation-error-magnitude
    anchor: declaration
    summary: "An approximate pairing declares its error class and not a bound. For the stationary projection of a general integral kernel no computable bound is stated anywhere, so the declaration names the defect without sizing it, and a consumer cannot rank two approximate pairings against each other."
---
# Evaluation strategies

## What an evaluation strategy is

The **evaluation strategy** is the field of an integral transform that decides how the
contraction is computed ([integral-transform#signature]). It is swappable independently of
the integral kernel, and that independence is the point: it makes *"the same integral
kernel, evaluated two ways"* an experiment the framework can run.

A strategy changes cost and exactness. It never changes what the operator is asked to
compute.

## The structure classes an integral kernel declares

A strategy is exact only for integral kernels of a particular structure. **Every integral
kernel therefore declares a structure class**, and that declaration is the whole of what
an integral transform requires of it
([operator-decomposition#unwritten]).

| Class | The integral kernel satisfies |
|---|---|
| **Stationary** | it depends on the two points only through their separation |
| **Separable** | it is a finite sum of products of a function of one point and a function of the other |
| **Hierarchically admissible** | its far-field blocks are numerically low-rank under a stated admissibility condition |
| **General** | none of the above is claimed |

`General` is not a failure. It is the honest declaration for a learned integral kernel with
no imposed structure, and it is exact under dense quadrature.

The class is a claim about the integral kernel, and a wrong claim is not caught here — a
stationary declaration on a nonstationary integral kernel produces a fast, exact-looking
evaluation of a different operator.

## The five strategies

| Strategy | How it computes the contraction | Cost in the point count |
|---|---|---|
| **Dense quadrature** | every pair, weighted and summed | quadratic |
| **Fast Fourier transform** | multiply in the transformed domain | linearithmic |
| **Outer product** | contract the input against one factor, expand against the other | linear in the factor count |
| **Neighborhood subsample** | sum over a truncated neighbor set | linear in the neighbor count |
| **Hierarchical far-field** | near-field densely, far-field through compressed blocks | near-linear |

Dense quadrature is the definition rather than an optimization, which is why it is exact
for every class and why the other four exist.

## Which pairings are exact

| Structure class | Exact under | Approximate under |
|---|---|---|
| **Stationary** | dense quadrature; fast Fourier transform on a regular periodic grid | outer product, neighborhood subsample, hierarchical far-field |
| **Separable** | dense quadrature; outer product | fast Fourier transform, neighborhood subsample, hierarchical far-field |
| **Hierarchically admissible** | dense quadrature; hierarchical far-field, to the stated tolerance | fast Fourier transform, outer product, neighborhood subsample |
| **General** | dense quadrature | every other strategy |

**Every cell is admitted.** An approximate pairing runs, and the transform publishes what
it computed, below. The framework has no compose-time refusal
([operator-decomposition#swappability]).

The fast Fourier transform carries a second condition that the class alone does not
supply: a regular grid over a periodic integration domain. A stationary integral kernel
over the symmetry-quotiented Brillouin wedge, or over the device mesh, is an approximate
pairing even though the class matches, because the point enumeration is not regular
([integration-domain#the-four]). **Exactness is a property of the pairing with the domain,
not of the pairing with the class.**

## The named operator families are cells of this table

| Strategy, with its class | The family it names |
|---|---|
| Fast Fourier transform on a stationary integral kernel | the Fourier neural operator |
| Outer product on a separable integral kernel | the branch-trunk operator |
| Neighborhood subsample on a general integral kernel | the graph neural operator |
| Hierarchical far-field on an admissible integral kernel | the multipole graph neural operator |

The literature these are drawn from presents them as competing architectures, and the
survey this library works from records them that way
([residual-loss-design#survey]). **Under this decomposition they are four cells of one
table**, and the reading has consequences the architecture reading does not:

- The table has more cells than it has named families, and **an unnamed cell is an
  experiment that has not been run** rather than a gap in the taxonomy.
- Two families differ by one field, so *"the same integral kernel under two strategies"* is
  a controlled comparison rather than a comparison of two models.
- A result attributed to an architecture may belong to its strategy, its structure class,
  or their pairing, and only a decomposition that separates them can say which.

A framework holding the four as architectures cannot pose the question. That is the
argument for the decomposition, stated where it is testable.

## The declaration record

What the transform publishes on every application
([integral-transform#error-declaration]):

```
Declaration = ( structure class declared by the integral kernel
              , strategy applied
              , exactness           -- exact, or approximate
              , approximation kind  -- what different operator was computed
              , truncation applied  -- radius or neighbor count, where any
              , point count         -- what the quadrature summed over
              , integration domain identity, input and output )
```

`approximation kind` names the operator actually computed — the stationary projection of a
nonstationary integral kernel, the rank-truncated part of a nonseparable one, the
neighborhood restriction of a long-range one. It names the defect. **It does not size it**,
and that limit is carried as an open item above.

## The declaration is part of identity

The seam requires every operator instance to expose one stable content hash, so that a
residual map is permanently attributable to the pair of oracle kernel and operator
([learnable-structure-contract#content-addressable-identity]).

**The declaration enters that hash.** Two instances with identical weights and different
strategies are different operators, because they compute different functions, and a hash
that cannot tell them apart makes a residual map attributable to something that does not
determine it.

This is what keeps declare-without-refusing from being decoration. A declaration that only
narrates leaves the library free to report a clean result from an approximate pairing and
attribute it to the exact one. A declaration that participates in identity cannot: the
result carries the pairing that produced it, and two runs that disagree are visibly two
runs of two operators.

The seam offers a related mechanism in the other direction. Where the oracle's symmetry
sidecar lets an operator bake equivariance into a compiled structure, the corresponding
residuals go to zero by construction ([learnable-structure-contract#optional-offers]).
That is the same trade this page makes, taken the other way: structure declared up front
buys exactness, and structure assumed without declaration buys a silent approximation.

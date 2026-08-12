---
id: typeclass-alphabet
title: "The typeclass alphabet"
owns:
  - observable output typeclasses
  - tolerance composition
  - analytic witnesses
  - typeclass aliases
anchors:
  axes: "Three axes and a bucket"
  quantity: "Quantity — the value axis"
  sampleable: "Sampleable — the shape axis"
  analytic-structure: "HasAnalyticStructure — the constraint axis"
  discrete-structure: "DiscreteStructure — the combinatorial axis"
  aliases: "Aliases"
depends-on:
  - cert-obligations
  - topology-atlas
  - physics-graph
  - forced-decisions
  - named-formulas
  - computational-methods
  - property-templates
open-questions:
  - id: implementation-language-undecided
    anchor: axes
    summary: "The alphabet is written as language-neutral typed pseudocode because the implementation language is undecided; the typeclass mechanism each axis assumes — coherence, dispatch, à-la-carte capabilities — is a language property this corpus has not yet chosen."
  - id: three-aliases-never-expanded
    anchor: aliases
    summary: "Scalar, Tensor and FieldOnGrid are used as return types throughout the method and template signatures and are expanded nowhere, so those signatures cannot be typed as written."
---
# The typeclass alphabet

## Three axes and a bucket

Every observable output is typed along three orthogonal axes plus a discrete
bucket, captured as four typeclasses. Orthogonality is the point: a value carries
units *and* a shape *and* a set of analytic constraints, and typing them together
into one class hierarchy would force a choice between the three every time a new
observable arrives.

Every node of the physics graph carries a type drawn from this alphabet
([physics-graph#node]), and the certification obligations map onto these axes
mechanically ([cert-obligations#the-ten-obligations]) — an obligation is a
claim about one axis, so the axis decides which obligations even apply.

The alphabet is written here as language-neutral typed pseudocode. The
implementation language is undecided ([forced-decisions#implementation-language]).

## Quantity — the value axis

Units, equality within a tolerance, and behavior under a change of units or
basis. Every numeric output is a `Quantity`.

```
Quantity:
  unitsOf     : a → Units
  approxEq    : Tolerance → a → a → Bool
  rescale     : Units → a → a
  combineTol  : Tolerance → Tolerance → Tolerance
```

`combineTol` is how tolerances compose under arithmetic — the tolerance on
`κ = κ_el + κ_ph` given the tolerances on the two terms. It is associative,
commutative and monotone, and each instance chooses either maximum-absolute or
root-sum-square composition. Monotonicity is the load-bearing property: a
combination can never come out *tighter* than its inputs, which is what stops a
long composition from manufacturing precision it does not have.

Model-form error from a declared relaxation enters here, as a contribution to the
composed tolerance rather than as a separate quantity
([named-formulas#diff-tags]).

## Sampleable — the shape axis

Whether the output is a function on a domain.

```
Sampleable:
  evaluate : f → Domain → Codomain      -- total on the claimed domain
```

with optional à-la-carte capabilities:

- **`Integrable`** — `integrate(measure)`; linear, with change-of-variables.
- **`Differentiable`** — `derivative : f → Domain → Maybe Tangent`, total on the
  domain *minus* an `exceptionSet`. Phase transitions, band crossings and
  charge-transition levels live in the exception set: they are the points where
  the derivative genuinely does not exist, and naming them is what lets a
  consumer distinguish that from a numerical failure. Carries a `chart` tag, so
  derivatives are only compared across instances whose charts match.
- **`Restrictable`** — `restrict(subdomain)`.

À la carte rather than bundled, because a function that can be integrated need
not be differentiable and the converse fails as often.

## HasAnalyticStructure — the constraint axis

Global analytic laws carried as witnesses: causality and the Kramers–Kronig
relations, hermiticity, convexity, Onsager involution, sum rules.

```
HasAnalyticStructure:
  certifyAnalytic : a → Either Failure {Witness}

Witness = (Local | Global, law)
```

One output can carry several witnesses simultaneously. `certifyAnalytic` returns
the witnesses or a typed failure — never a boolean, because a consumer that
learns only *that* an analytic law failed cannot act on it, while one that learns
*which* can.

## DiscreteStructure — the combinatorial axis

Integer invariants, classification groups, holonomy spectra, polyhedra, convex
hulls: objects in a discrete category.

```
DiscreteStructure:
  identity : a
  compose  : a → a → a
  isoEq    : a → a → Bool
```

Not a `Quantity` — there are no units — and not `Sampleable` — there is no
domain. Attempting either is the error this class exists to prevent: an integer
invariant with a tolerance attached is a category error that a numerical pipeline
will happily carry all the way to a residual.

The topology-atlas outputs live here ([topology-atlas#entry]).

## Aliases

Four aliases name parameterizations that recur, so a signature elsewhere can be
written in one word instead of a conjunction: `Scalar`, `Tensor`,
`FieldOnGrid`, `Response`.

`Response` is
`Sampleable + Integrable + Differentiable + HasAnalyticStructure(KramersKronig)`
over a frequency domain.

The other three are named and used and **never expanded** — they appear as return
types throughout the method and template signatures
([computational-methods#signatures], [property-templates#signatures]) and no page
says which typeclasses and parameters each stands for. Those signatures do not
type without them, which puts these three in the same position as the argument
types ([computational-methods#argument-types]).

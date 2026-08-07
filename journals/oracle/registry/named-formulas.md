---
id: named-formulas
title: "Named formulas"
owns:
  - formula record schema
  - differentiability vocabulary
  - evaluation cost vocabulary
  - no-inline-math rule
  - anchor class
  - formula row bands
  - applicability decidability
  - corrected canonical forms
anchors:
  the-registry: "What the registry is"
  formula-record: "The formula record"
  no-inline-math: "No inline mathematics"
  diff-tags: "How a consumer obtains a gradient"
  mixed-outputs: "Rows with mixed outputs"
  cost-tiers: "Evaluation cost"
  anchor-class: "Anchor class"
  row-bands: "What the row bands hold"
  corrected-forms: "Canonical forms"
  applicability-decidability: "Applicability is decidable"
depends-on:
  - formula-registry
  - observable-bundles
  - computational-methods
  - typeclass-alphabet
  - topology-atlas
  - accuracy-ledger
  - cert-obligations
  - residual-definitions
  - residual-machinery
  - applicability-classifiers
  - compose-time-pipeline
  - build-sequence
  - build-verification
  - multiscale-state
  - traps
open-questions: []
---
# Named formulas

## What the registry is

The registry is the closed set of typed, fully parameterized algebraic formulas
the oracle is allowed to invoke. It is a contract between the property machinery
and the operator: each row is independently citable to published work and
independently verifiable by the certification sub-tree, and new rows enter only
through the registry-build gate ([build-sequence#phases]).

The rows themselves live in the manifest, which is canonical and
machine-readable. [formula-registry] describes its table shape; this page
describes what a row *is* and what its tags mean.

**Counts over the manifest belong to the manifest.** This page states the rules a
row obeys and names individual rows where a rule needs an example. It does not
tally them. A tally written in prose beside the table it counts is a second copy
with no mechanism holding it to the first.

Two rows are **architectural markers** rather than formulas: force as the
negative gradient of energy, which the autodiff engine satisfies identically, and
equivariance, which the representation carries by construction. They are in the
manifest so that the decision to enforce them structurally is recorded, and they
are deliberately not residualized — scoring a relation the compiler already
guarantees measures the compiler, not the physics.

## The formula record

```
record FormulaRecord {
  name              : Symbol            -- behavior-named; a person's name appears
                                        --   only in the provenance cell
  signature         : (Inputs) → Output -- typed, with units
  bundle            : {BundleName}      -- one or more observable bundles, or
                                        --   linear-response-primitive
  cost-tier         : microseconds | milliseconds | seconds | minutes
  differentiability : read | direct | adjoint | fixpoint-adjoint | relaxed | none
  anchor-class      : cheap | faithful
  provenance        : research stream, literature citation, or relaxation name
  depends-on        : {Symbol}          -- upstream formulas and primitives
  applicability     : (Crystal, Environment) → Bool
  adjoint-validated : Passed | Failed(witness) | NotApplicable | Relaxed(rationale)
}
```

The `bundle` field takes observable-bundle names ([observable-bundles#the-eleven])
or the value `linear-response-primitive`, which is what a row carries when it
feeds several bundles rather than belonging to one
([observable-bundles#linear-response-primitives]).

## No inline mathematics

Every algebraic combination invokes a named formula with typed inputs and an
explicit output type. No inline mathematics, no string-encoded expressions. This
is the rule the whole registry exists to enforce: an expression written at a call
site is unciteable, unverifiable and invisible to the gate, and the three
properties the registry sells are exactly citeability, verifiability and
gate-visibility.

The rule binds at the call site as well as here — `algebraic-combination` always
dispatches to a registry row ([computational-methods#signatures]).

## How a consumer obtains a gradient

The differentiability field answers exactly one question: **how does a consumer
obtain a gradient through this row?** Every value it takes is an answer to that
question, and the six answers are a set, not a scale — there is no ordering among
them and no arithmetic on them.

- **`read`** — the output is a stored or passed-through value and the adjoint is
  the identity. Registers without a synthesized adjoint, and the registration
  gate exempts it from adjoint synthesis ([build-verification#registration]).
  `reference-phase-energy-cache`, keyed on a phase identifier alone, is the row
  this describes.

  A row that also takes continuous arguments is **not** a pure read, however
  cache-backed its implementation. An implementation detail — a cache — is not a
  mathematical one — an identity adjoint. `chemical-potential-ref-table` is the
  case that makes the distinction concrete: it takes temperature and pressure, so
  reading it as `read` would zero the derivative of chemical potential with
  respect to temperature and leave the Maxwell cross-derivative residual it feeds
  vacuously satisfied. It is `direct`.

- **`none`** — no useful derivative. Integer, categorical, boolean or set-valued
  output: topology invariants, discrete classifications. Not differentiable and
  not relaxable in place, so a consumer needing a gradient must route around the
  row or use a relaxation registered as its own row.

  **This is the strongest claim in the vocabulary**
  ([traps#no-derivative-claim]). It asserts that no
  relaxation exists, not merely that none is written yet, so it is the value most
  likely to be wrong. Before assigning it, check two things: whether the output
  has a real-valued component — the mixed-output rule below — and whether this
  corpus already prescribes a relaxation for the construction elsewhere.

- **`direct`** — smooth, and the gradient is available directly: an analytic
  closed form, or a composition the autodiff engine handles. No registration
  gate.

- **`adjoint`** — an adjoint is required and is validated at registration.
  Vector-Jacobian and Jacobian-vector products must agree on sampled points
  within `τ_adj` ([residual-machinery#registration-gate]). The gate checks the
  *synthesized* adjoint, not a hand-written backward pass — a hand-written
  backward that agrees with itself proves nothing about the code the compiler
  emits.

- **`fixpoint-adjoint`** — **a refinement of `adjoint`, not an alternative to
  it.** The output is a converged fixed point, and the gradient is one linear
  solve against the transposed fixed-point Jacobian, independent of forward
  iteration count. **That independence is the test**: if the adjoint's cost
  scales with how many forward steps were taken — a backward-in-time sweep
  through a transient — the row is `adjoint`.

  The name says refinement and the gate matches it. Every `fixpoint-adjoint` row
  runs the same registration gate as `adjoint`, **and one more**: a conditioning
  check on the fixed-point Jacobian at the sampled points, refusing registration
  when the reciprocal condition number falls below `τ_cond`
  ([residual-machinery#registration-gate]). Without that second check the value
  would be strictly weaker than `adjoint`, which is backwards: it names a
  stronger structural claim than `adjoint` does, so it cannot carry a weaker
  obligation ([traps#fixpoint-claim]).

  The rows it bites are not exotic. `fermi-level-charge-neutral` and
  `self-consistent-charge-balance` solve charge neutrality, whose Jacobian is
  flattest exactly in a wide-gap intrinsic semiconductor — this corpus's subject.
  `SCPH-self-consistent-phonons` is invoked precisely where soft modes make its
  Jacobian near-singular.

- **`relaxed`** — genuinely non-smooth: argmin, convex hull, sort, discrete
  metric. Ships a declared smooth relaxation whose bias is a model-form error
  entering the tolerance composition of [typeclass-alphabet#quantity], approved
  at registration with a validity domain under obligation-9
  ([cert-obligations#the-ten-obligations]). **The relaxation is named in the
  row's provenance cell**; a `relaxed` row without one is un-gateable and fails
  the registry-build gate ([traps#unnamed-relaxation]).

The values are spelled out in English so that no differentiability value can be
read as a physical quantity. Wide-bandgap semiconductor physics is dense with
letter-and-digit labels — deformation potentials, deep-donor configurations — and
a tag drawn from the same alphabet cannot be searched for without returning the
physics, or the physics without returning the tag.

## Rows with mixed outputs

Several rows return a real quantity *and* a discrete label derived from it:
`radius-ratio-coordination-class` returns a ratio and a class,
`elastic-stability-criteria` a boolean vector and a slack,
`structure-uniqueness-CSP` a boolean and a distance.

**The differentiability value describes the continuous component.** The discrete
label is a downstream classification carrying no gradient of its own, and a
consumer needing a gradient differentiates the continuous part. A discrete label
never drags a row to `none` — without this rule the same construction is tagged
several ways depending on which half of the output the reader looks at.

Where the *map* from continuous to discrete is itself load-bearing — a threshold,
a min-over-set — that non-smoothness is what makes the row `relaxed`, and the
declared relaxation covers exactly that step.

## Evaluation cost

What one evaluation of the formula costs:

| Value | Work | Bound |
|---|---|---|
| `microseconds` | closed form | ≤ 10 µs |
| `milliseconds` | small linear algebra, one-dimensional quadrature | ≤ 10 ms |
| `seconds` | Brillouin-zone or mesh integral | ≤ 10 s |
| `minutes` | self-consistent loop or partial-differential-equation solve | ≤ 10 min |

Four rows make the scale concrete. `single-mode-rta-lattice-kappa` (row 25) and
`operator-position-derivative-tensor` (row 92) are `seconds` — a Brillouin-zone
integral each. `NEGF-transmission` (row 80) and `reference-phase-energy-cache`
(row 87) are `minutes`. These are examples and not the membership of either
value: the assignment for a given row is the manifest's `cost-tier` field, which
is where it is looked up ([formula-registry#fields]).

The last of the four is worth reading twice. `reference-phase-energy-cache` costs
`minutes` to evaluate and is `read` for differentiability — among the most
expensive evaluations in the registry, carrying the cheapest gradient there is,
an identity adjoint. Cost and differentiability are independent axes, and the
expensive tail is where they come apart.

**Evaluation cost is a property of the formula. Cadence is a training-loop policy
and lives in the operator library.** They are two vocabularies over two different
things, and the oracle owns no loop. An iterative residual is `minutes` by cost
and `per-epoch` by cadence, and nothing forces those to agree. The expensive tail
is where reading one as the other does its damage: at the cheap end a row is
evaluated on every step under either reading, so a confusion changes nothing,
while a `minutes` row sampled as though its cost value were a cadence is sampled
at the wrong rate on exactly the rows whose evaluation dominates the budget.

The cost value is what the residual factory reads when it decides how often to
sample a generator ([residual-machinery#factory]); the decision itself, and the
cadence vocabulary it is expressed in, belong to the operator.

## Anchor class

`cheap` against `faithful`. This is **not** a runtime path selector: under the
always-cheap pipeline ([compose-time-pipeline#always-cheap]) every registered
formula lands on the single residual surface and nothing chooses between two
paths at runtime.

What the field records is what a row's value is *anchored against*. A `cheap` row
stands on its own closed form. A `faithful` row is one whose value is trusted
only against a reference-grade computation — a density-functional, perturbation,
non-equilibrium-Green's-function or Monte-Carlo evaluation — or against a
measured battery entry.

That makes it the axis a consistency pair runs along:
[residual-definitions#pair-kinds] defines the pair kinds, and a consistency pair
is one whose two members sit on opposite sides of this field — the cheap model
against the microscopic reference it has no agreement theorem with
([traps#consistency-not-equivalence]). The `Cheap vs faithful` column of
[accuracy-ledger#observable-regimes] is the per-observable statement of the
same distinction.

## What the row bands hold

The manifest's row numbers are stable identifiers, and contiguous bands of them
were added as packages. The band map is what tells a reader which physics a row
range covers; the per-row provenance is the manifest's own
([formula-registry#provenance]).

| Rows | Package |
|---|---|
| 1–87 | the base catalog, grounded in the five research streams |
| 88–102 | linear-response and topology-atlas extensions |
| 103–104 | the two architectural markers |
| 105–112 | slow-tier degradation and radiation |
| 113–115, 117–118 | polarization, piezoelectricity and the two-dimensional electron gas |
| 116, 119 | interface traps and subthreshold swing |
| 120–127 | the per-material accuracy package |
| 128–134 | the gap-audit package |

**Rows 88–102** carry the long-range Coulomb directional-limit correction, the
charged-supercell finite-size schemes, the linear-response primitives (Born
effective charges, high-frequency dielectric response, electronic susceptibility,
the lattice Coulomb scalar), the composition-dependent excess-free-energy basis,
and the topology-atlas rows — symmetry-indicator group by Smith Normal Form,
elementary band representations, compatibility relations, Chern, Z₂ and
Wilson-loop invariants, and boundary-mode multiplicity ([topology-atlas]).

**Rows 105–112** are the slow-tier rows: vacancy generation, hydrogen
redistribution and desorption, platelet nucleation, vibration-driven vacancy
generation, air oxidation, and radiation displacement
([multiscale-state#slow-kinetics]).

**Rows 113–115 and 117–118** are gated by `is-noncentrosymmetric`. That is the
piezoelectric-class predicate of the two-predicate split in
[applicability-classifiers#polar-predicate-split], **not** the polar-coupling
gate `is-polar-material`. The two predicates look interchangeable and are not:
a material can be polar for coupling purposes without being piezoelectric.

**Rows 120–127** are the per-material accuracy package:
`ahc-gap-renormalization` (a one-shot temperature-dependent gap dressing),
`kappa-4phonon-high-t-correction` and `iterative-lbte-kappa` (the
high-temperature siblings of the single-mode relaxation-time thermal
conductivity), `breakdown-field-temperature-slope`, `tp-aware-hull`
(temperature- and pressure-aware metastability), `detailed-balance-cycle-residual`
and `rotational-sum-rule` (consistency residuals), and
`alloy-disorder-scattering`, an `is-alloy`-gated mobility limiter.

**Rows 128–134** are the gap-audit package: `pyroelectric-coefficient`, the
gate-dielectric aging trio `poole-frenkel-current`,
`tddb-thermochemical-e-model` and `dielectric-crystallization-jmak` (all
`is-dielectric-layer`-gated), the experimental-structure channels
`xrd-structure-factor` and `raman-activity`, and `radiative-recombination-rate`,
the detailed-balance rate backing radiative emission.

## Canonical forms

Five forms are canonical in the registry, and each is one a näive derivation gets
wrong:

- Optical absorption is `(2ω/c)·Im(√ε)` — the factor of two is part of the form.
- The operator-spectrum-area sum rule carries the `2/π` prefactor.
- The acoustic sum rule sums over all lattice translations,
  `Σ_J Σ_R Φ_{IαJβ}(R) = 0`, not over the sites of one cell.
- The magnetic relaxation term is the orientation-preserving double cross
  product `S × (S × H_eff)`.
- The harmonic transition-rate normalization consumes products over normal
  modes — scalars — not the spectra themselves.

## Applicability is decidable

Every `applicability` predicate is first-order decidable in
`(Crystal, Environment)`: finite case analysis on typeclass tags — lattice type,
site decoration, presence of an environment field — and never on numeric
thresholds or solver outputs. A predicate that had to run a solver to decide
whether a formula applies would make applicability a runtime property of the
answer rather than a compile-time property of the composition, and the mask the
operator trains against would stop being knowable before training.

Non-decidable classifiers are refused at registration by the registry-build gate
([build-sequence#phases]).

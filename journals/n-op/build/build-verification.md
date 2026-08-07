---
id: build-verification
title: "Verification"
owns:
  - static consistency set
  - runtime gate sequence
  - first end-to-end capability gate
  - diamond strain hypersurface
  - registration gate
  - worked example gate
  - curriculum gate
  - obligation firing gate
  - seam smoke test
anchors:
  static-consistency: "Internal consistency, checked statically"
  first-end-to-end-gate: "The first end-to-end gate"
  strain-hypersurface: "The strain hypersurface this gate runs against"
  gates: "The five runtime gates"
  registration: "Gate 1 — registration sanity"
  worked-example: "Gate 2 — end-to-end worked example"
  curriculum: "Gate 3 — curriculum sanity"
  obligations: "Gate 4 — cross-regime obligations fire"
  seam-smoke-test: "Gate 5 — operator seam smoke test"
depends-on:
  - build-sequence
  - capability-slices
  - canonical-vocabularies
  - named-formulas
  - property-templates
  - computational-methods
  - typeclass-alphabet
  - generic-dynamics
  - residual-definitions
  - residual-machinery
  - cert-obligations
  - compose-time-pipeline
  - pino-bridge
  - reference-battery
  - traps
open-questions: []
---
# Verification

Two kinds of check, and they fire at different times. The static set is checkable by
walking the tree and the registry manifest as soon as the scaffold exists. The gates
need a built system.

## Internal consistency, checked statically

The specification is internally consistent when:

1. Every observable invokes only registered methods, templates and registry formulas
   ([canonical-vocabularies], [named-formulas#no-inline-math]) — no inline
   mathematics, no ad-hoc combinators.
2. Every method, template and formula has a typed signature with no string-encoded
   parameters.
3. The directory tree built in the scaffold phase ([build-sequence#phases]) contains
   every concept this base names.
4. The nine regime extractions ([generic-dynamics#nine-regimes]) are realizable as
   typed compositions of the template and method vocabularies
   ([property-templates#signatures], [computational-methods#the-alphabet]).
5. Every residual category ([residual-definitions#categories]) is grounded in a
   GENERIC identity or a named formula.
6. Every certification obligation ([cert-obligations#the-ten-obligations]) corresponds
   to a residual category or an algebraic identity, and maps to an axis of the
   typeclass alphabet ([typeclass-alphabet#axes]).
7. The counts stated anywhere in this base agree with the vocabulary page and the
   registry manifest ([canonical-vocabularies]). No count is restated where it can be
   emitted.

Once the scaffold exists, items 1 to 7 are checkable **mechanically**, by walking the
tree and the registry manifest. That mechanisability is the point of the list: a
consistency claim a person has to re-read the corpus to confirm is a claim nobody
confirms twice.

## The first end-to-end gate

The crystal-structure slice's acceptance test is the first point at which the whole
chain runs ([capability-slices#structure-prediction]). Three parts, in order.

- **Null.** Grading a ground-truth, relaxed pure-diamond state returns every residual
  slot at approximately zero within its declared error scale. The oracle certifies a
  lawful structure as lawful.
- **Sensitivity.** Perturbing the state — an atomic displacement, a cell distortion
  off the energy minimum, or a wrong lattice constant — returns a non-zero residual
  **and the specific keys that fire name the violated law**: the vanishing-gradient
  residual for a broken relaxation, space-group equivariance for a broken symmetry,
  the elastic stability criteria for an over-stretch. Because residuals are keyed and
  never aggregated ([residual-definitions#granularity]), "the right law fired" is
  directly checkable rather than inferred from a total.
- **Data-backed sensitivity.** Perturbing along the diamond strain hypersurface, the
  residual tracks the reference energy rise off the minimum — a quantitative match,
  not only a sign check.

## The strain hypersurface this gate runs against

The data-backed arm runs against a recovered hybrid-level strain hypersurface of
diamond — HSE06 with gap-tuned exact exchange, six lattice-distortion families to
±10%, with stress tensors — in [strain-sweep]. It is **simulation
output, not measured reference data**, which is why it sits beside the reference data
rather than inside it: the reference battery is not a cache of computed results
([reference-battery#boundaries]).

**1,179 rows, of which 1,131 are distinct shapes.** Twenty-four shapes are each
computed three times, and the three copies agree bit for bit, so de-duplication drops
48 surplus rows and loses nothing. Left in, those 24 shapes carry triple weight in any
fit.

**De-duplicate before any fit, and de-duplicate on the manifest's own
`duplicate_group` column.** Naming the column is not pedantry — it is the only method
that works, and the obvious alternative fails *silently*:

- The three copies of a shape are geometrically identical and **textually different**.
  One row leaves the untouched skew columns blank; the others write an explicit
  `0.000` into one of them.
- The copies also arrive from different source archives under different shape-change
  labels, so de-duplicating on the shape-change kind together with the geometry fails
  the same way.
- Sorting the geometry columns for unique rows therefore returns all 1,179 and reports
  the data clean.

A careful person doing the sensible thing gets the wrong answer and no warning. The
`duplicate_group` column is the key; the coordinates are not.

## The five runtime gates

Five sequential gates validate the built system.

## Gate 1 — registration sanity

Every registered formula instantiates as a residual-generator record without error.
Then, by differentiability tag:

- Every `adjoint` **and** every `fixpoint-adjoint` entry passes the registration-time
  adjoint gate.
- Every `fixpoint-adjoint` entry additionally passes the fixed-point-Jacobian
  conditioning check ([residual-machinery#registration-gate]).
- Every `relaxed` entry carries a rationale **naming its relaxation**, under the
  obligation that governs relaxations ([cert-obligations#the-ten-obligations]).
- `read` and `none` entries register without an adjoint, and `direct` entries without
  a gate — none is needed.

**Fidelity pairing.** Every generator whose lowering introduces representation error
registers its paired fidelity generator ([residual-machinery#fidelity-generators]): a
compression plan that is not dense, a truncated inner solve, or a rewrite admitted
under a side condition. **A missing pairing fails the build.** It is not a warning —
without enforcement the pairing obligation would be prose that nothing checks, and a
build that passes without checking looks exactly like a build that checked
([traps#checker-not-looking]).

The adjoint-tape materialization schedule
([compose-time-pipeline#lowering-and-adjoint-synthesis]) is the one lowering
**exempt** by construction: it changes cost, not value, so there is no discrepancy to
estimate. Without that exemption the pairing rule would be over-broad.

## Gate 2 — end-to-end worked example

A diamond–tungsten Schottky contact at 500 °C. Input: diamond bulk, a tungsten contact
and a silicon substrate, with the environment record set to 773 K and a field of 1
MV/cm.

The graph layers fire in order; the equilibrium-statistics ↔ non-equilibrium-kinetics
cycle — charge balance against self-heating — closes by a same-pass fixed point in
five iterations or fewer; roughly three dozen residuals fire and are accounted for in
the certification manifest. Outputs: Schottky barrier, drift velocity, electron
temperature, self-heating temperature rise, and predicted mean time to failure. The
run completes within its declared cost budget, and certification obligations 1, 2, 3,
5 and 8 emit verdicts.

## Gate 3 — curriculum sanity

A synthetic three-phase training run on bulk silicon — about five observables and
about a thousand samples — completes without gradient-norm divergence, without an
equilibrium-statistics ↔ non-equilibrium-kinetics fixed-point failure, and without an
adjoint-certificate reset mid-training.

This gate is the one place a build check reaches across the seam into training. The
curriculum phases and their gating fractions are owned on the operator side
([residual-definitions#curriculum-gate]); what this gate asserts is only that a run of
that shape completes.

## Gate 4 — cross-regime obligations fire

Four obligations are exercised on cases chosen so that each *must* trip:

- **Obligation 6** — Boltzmann conductivity against Kubo conductivity on an
  equilibrium reference.
- **Obligation 9** — a `relaxed` query outside its declared domain trips with a
  witness.
- **Obligation 10** — a synthetic `adjoint` formula with a deliberately broken adjoint
  is refused at registration: loud, at build time.
- **Obligation 7** — non-topological diamond emits "not applicable" with a rationale,
  while a contrived time-reversal-invariant test system emits the predicted edge-state
  count.

## Gate 5 — operator seam smoke test

The seam is exercised through its own entry points ([pino-bridge#validate]):

- Validate with gradients skipped populates label values for about ten silicon
  observables.
- Validate with gradients computed returns finite per-residual scalars and finite
  cotangents of the declared shape, on a randomly initialized state.
- Import accepts a synthetic payload in the format the plane-wave reference code
  emits, and returns ground-truth bridge generators with their coverage masks.

All three return within their typed contracts. This is the gate the MVP exit criterion
depends on ([build-sequence#exit-criterion]).

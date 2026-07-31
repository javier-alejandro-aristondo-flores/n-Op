---
id: build-sequence
title: "Build sequence"
owns:
  - build phases
  - build language neutrality
  - applicability decidability gate
  - invariant synthesis attachment
  - MVP build column
  - MVP exit criterion
anchors:
  language-neutrality: "The phases are language-neutral"
  phases: "The phases"
  mvp-column: "How to read the MVP column"
  exit-criterion: "The MVP exit criterion"
depends-on:
  - forced-decisions
  - capability-slices
  - build-verification
  - library-landscape
  - crystal-inputs
  - unified-state
  - computational-methods
  - property-templates
  - observable-bundles
  - named-formulas
  - coupling-structure
  - generic-dynamics
  - residual-definitions
  - cert-obligations
  - pino-bridge
  - reference-battery
open-questions:
  - id: mvp-phase-coverage
    anchor: mvp-column
    summary: "Five phases — templates, GENERIC operators, observables, dynamics, and the seal — are marked open. The MVP's own scope statements require them (ten templates, five primary bundles, and an exit criterion plus a seam smoke test that both call the sealed entry points), while the step list the MVP build was written as does not name them. Which of the five are in the MVP is unresolved; the column records the disagreement instead of hiding it in a subset claim."
---
# Build sequence

Each phase produces a verifiable artifact, and the MVP is a **column on this table**
rather than a separate list. A projection kept on its own page can assert a subset
relation that nothing checks — and did.

## The phases are language-neutral

None of the phases below depends on which language fills which role
([forced-decisions#implementation-language]). That is why the picks can stay open this
long, and it is a property worth preserving: a phase that could only be built in one
language would move a language decision onto the critical path.

## The phases

| Phase | Scope | Verifiable artifact | MVP |
|---|---|---|---|
| 0 | Repository scaffold: the directory tree, orientation documents, per-directory readme files | Empty skeleton matching the architecture | in |
| 1 | **Numeric substrate** (`core`): coefficient and derivative layout, the automatic-differentiation engine, staged code generation, tensor algebra, mesh integration over k-meshes and tetrahedra | `core` implemented and tested against analytic references | in |
| 2 | **Physical primitives** (`shared`): pair sums under periodic boundaries, Ewald electrostatics, kinetic density, density from orbitals, Hellmann–Feynman forces, density-functional stress, and the tight-binding carbon Hamiltonian builder ([forced-decisions#tb-warm-start]) | Physical-primitive library, tested at analytic limits | in |
| 3 | **Input concepts** (`inputs`): typed constructors and readers for the periodicity structure, the site decoration and the environment record ([crystal-inputs#top-level-inputs]) | Round-trip-preserving system descriptions | in |
| 4 | **Unified state** (`state`): the state container, its per-level components, and enumerate, serialise and hash ([unified-state#slots]) | State encoding complete | in |
| 5 | **Methods vocabulary** (`methods`): the computational methods and sub-method dispatch ([computational-methods#the-alphabet]) | Computational vocabulary, tested per method | in |
| 6 | **Templates** (`abstract-properties`): the property templates as typed factories ([property-templates#signatures]) | Template machinery, tested with multiple argument tuples | open |
| 7 | **Formula registry** (`formulas`): the registry rows with typed signatures and citations, the manifest, and the **applicability-decidability gate** ([named-formulas#applicability-decidability]) | Closed registry; every algebraic combination named and typed | in |
| 8 | **GENERIC operators** (`generic`): the reversible and irreversible sub-brackets and their assembly, with **invariant synthesis** instantiating the active coupling specification and attaching the generated invariant terms to the coupling-energy and assembly aggregators ([coupling-structure#invariant-generator]) | Antisymmetry, positive semi-definiteness, Jacobi and degeneracy verified | open |
| 9 | **Canonicals** (`canonicals`): the energy and entropy functionals assembled across levels | Dimensional and analytic-limit checks pass | in |
| 10 | **Observables** (`observables`): the target observables as typed compositions, grouped into bundles ([observable-bundles#the-eleven]) | Library callable for any observable; reference-crystal checks | open |
| 11 | **Residuals and certification** (`residuals`, `cert`): the named residual categories, the residual-generator factory, the certification obligations, and the schema, freeze fixture and high-precision oracle ([residual-definitions#categories], [cert-obligations#the-ten-obligations]) | Self-certifying outputs; usable residual contract | in |
| 12 | **Dynamics and integration validation** (`dynamics`): assemble the unified right-hand side and validate it on the harmonic oscillator, the two-level Rabi problem and ideal-gas relaxation ([generic-dynamics#operators]) | Unified dynamics callable; right-hand side handed to any integrator | open |
| 13 | **Seal and operator seam**: the single typed seal, the validate and import entry points ([pino-bridge#surface]), worked examples, end-to-end demonstration | Shippable; downstream libraries can build against it | open |

Two admission rules live inside that table and are easy to lose there, so they are named
again:

- **Applicability decidability (phase 7).** Every applicability classifier must be
  first-order decidable on typeclass tags. A non-decidable entry is rejected at
  registration rather than evaluated at runtime.
- **Fidelity of the assembled operators (phase 8).** The generated invariant terms are
  attached to the aggregators, not evaluated beside them, so an invariant that is
  synthesised but never attached is a build error rather than a silent omission.

Recommended start order: the substrate phases before any concrete observable, then the
operator, canonical and observable phases, then residuals, certification and dynamics,
then the seal.

## How to read the MVP column

- **in** — the phase is named by the MVP build's own step list and its artifact is
  required by the exit criterion.
- **open** — the MVP's scope statements require the phase's output, and the step list
  the MVP build was written as does not name the phase. See the open question on this
  page. These cells are the reason the column exists: as a separate page, the MVP order
  asserted that it was a subset of this table, and nothing compared the two.
- Phases marked **in** map onto the MVP steps in order, with two collapses: the methods
  and the formula registry are built together, and the certification obligations land
  with the seeded diamond reference battery ([reference-battery#contents]) in the same phase as
  the residuals.

The MVP's final step is not a phase but a **run**: relaxed lattice constant, gap with
the quasi-particle correction, elastic constants, maximum phonon energy and
room-temperature thermal conductivity, each evaluated against the battery. It belongs to
verification ([build-verification]).

## The MVP exit criterion

Completing the MVP column yields a **diamond-only oracle library** that can emit a
granular residual vector with cotangents, expose observable values, and certify them for
all three capabilities ([capability-slices]) — the concrete substrate the operator
library then trains against ([library-landscape#operator]).

The criterion is stated in terms of what a caller can do, which is why it reaches the
seal phase: emitting cotangents through a typed entry point is what "trains against"
means. That is the same dependency the seam smoke test exercises
([build-verification#seam-smoke-test]), and it is why phase 13 sits in the open question
above rather than outside the MVP by default.

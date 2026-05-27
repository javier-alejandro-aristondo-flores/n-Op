# physics — Architectural Summary

A high-level structural read of the Racket library at
`/home/javier/Desktop/Physics/Library/physics/`. This is an architectural
characterization only: it describes how the code is organized and what
conventions hold across it, not what it computes.

---

## Top-Level Layout

The repository root contains a small set of orientation files and three
sibling project directories that correspond to three stages of a single
intended pipeline.

```
physics/
├── README.md            comprehensive overview (theory + use + visuals)
├── AGENTS.md            agent / contributor workflow (issue tracker, shell hygiene)
├── CLAUDE.md            stub form of AGENTS-style instructions for Claude agents
├── .gitignore           ignores compiled/, _darcs/, beads data
├── .claude/             local Claude settings
├── _darcs/              darcs working dir (project VCS)
├── .git/                git working dir (scaffolding for the beads issue tracker)
├── demo.ipynb           a notebook (exists; out of scope for this summary)
│
├── library/             the implementation (Racket); see below
├── install/             placeholder for a downstream compile pipeline
└── interface/           placeholder for a downstream user-facing surface
```

Two version-control systems coexist: `_darcs/` is the project VCS (the
`.gitignore` says so explicitly); `.git/` is present only as scaffolding for
the `bd` (beads) issue tracker, which uses git refs (`refs/dolt/data`) as a
sync transport for a local Dolt database.

`install/` and `interface/` are each one-file directories containing only
a `README.md` that declares the directory a placeholder. Their stated role
in the pipeline:

```
library/  →  emitted numeric code  →  install/  →  .so / standalone binary
                                                       │
                                                       ▼
                                                   interface/
                                            (user-facing surface)
```

Only `library/` contains implementation.

### Inside `library/`

```
library/
├── README.md
├── info.rkt          Racket package manifest + raco test wiring
├── main.rkt          single public entry point (typed)
├── core/             differentiation substrate (untyped)
├── kernel/           residual / solver / fixed recipes (untyped)
├── cert/             certifier obligations + schema + freeze (untyped)
├── physics/          typed boundary + worked examples
└── tests/            21 rackunit suites
```

`info.rkt` declares the collection `physics`, deps `base /
typed-racket-lib / rackunit-lib`, and — significantly — scopes `raco test`
to `tests/` only via `test-include-paths` plus an explicit
`test-omit-paths` of every source sub-tree. A green `raco test library/`
run therefore means "every rackunit suite passed", not "raco tried to
execute library modules".

`main.rkt` is a thin typed re-export shell: it requires
`physics/api.rkt` and re-exports its entire surface, and additionally
imports a few worked-example runners through `require/typed` from
`physics/examples.rkt`. A `module+ main` prints those examples'
verdicts.

---

## Module Architecture

The four `library/` sub-trees form a strict layered architecture.
Imports go only "upward" through the layers:

```
                     ┌────────────────────────────┐
                     │  physics/   (typed seal)    │
                     │   api.rkt, examples.rkt     │
                     └─────────┬──────────────────┘
                               │ require/typed
                  ┌────────────┼────────────┐
                  │            │            │
              ┌───▼──┐     ┌───▼──┐     ┌───▼─────┐
              │ core │ ◄── │kernel│ ◄── │  cert   │
              └──────┘     └──────┘     └─────────┘
              (substrate)  (solver,     (obligations,
                            mechanics,   schema, freeze)
                            linear alg.)
```

Concretely, by grepping the relative imports:

- `kernel/*` requires only from `../core/*`.
- `cert/*` requires from `../core/*` and `../kernel/*` (plus its own
  `certificate.rkt` for the renderer / freeze).
- `physics/api.rkt` is the only module that requires from all three
  lower layers, and does so exclusively through `require/typed` with
  `#:opaque` for every kernel data type.
- `physics/examples.rkt` is untyped and requires from `core/` and
  `kernel/` directly; the typed `main.rkt` then re-exposes it through
  `require/typed`.
- `tests/*` requires modules from all four sub-trees as needed; no
  source module ever requires `tests/`.

### `core/` — the numeric substrate

Seven modules, all `#lang racket/base`. Roughly:

- `derivative-layout.rkt` — the descriptor (variable count, per-axis
  caps, total cap) plus enumerated lex order-tuple tables. Built once at
  construction time; pure data.
- `coefficient-recurrences.rkt` — the numeric ring over coefficient
  vectors (`flvector`): add / multiply / reciprocal / sqrt / exp / log /
  power / sin-cos / etc., as the *reference* recurrences.
- `non-smooth-operations.rkt` — companion ring ops with explicit
  regime tags (`'smooth` / `'boundary` / `'branch`) and a numeric
  witness for the gap.
- `formula-trees.rkt` — an immutable struct algebra used purely as
  authoring source for the staging macro and the reference evaluator;
  explicitly *not* a runtime IR.
- `staged-code-generation.rkt` — `define-staged-coefficient-procedure`,
  the macro that unrolls formula trees against a compile-time-constant
  derivative layout into flat `flvector` straight-line code. All
  recursion lives in expand-time.
- `staged-reference-check.rkt` — battery support: paired
  (staged thunk, reference layout, formula) cases used by the oracle
  tests.
- `derivative-readout.rkt` — `seed-variable`, `mixed-derivative`,
  `gradient`, `hessian`, `jacobian` — the single seed-and-read
  differentiation surface.

### `kernel/` — residual representation and the IFT solve

Five modules, all `#lang racket/base`.

- `residual-state.rkt` — `state-layout` / `residual` / `state-correction`
  structs and their operations; the `explicit-rate-residual` shortcut.
  This is the most plumbing-heavy module; it owns the "stacked state"
  descriptor (blocks with kind / offset / width / level) that index
  reduction produces.
- `dense-linear-solver.rkt` — hand-rolled partial-pivot LU
  factorization plus forward/back substitution, with a 1-norm
  condition estimator. Pure `flvector` numeric loops.
- `residual-rate-solver.rkt` — `solve-residual-rates`: the
  Newton-step IFT solve. Jacobian via the readout layer; one dense
  linear solve per step.
- `constraint-index-reduction.rkt` — composes the readout primitive
  and the linear solver to differentiate-and-substitute constraint
  rows until the Jacobian is full rank.
- `mechanics-recipes.rkt` — fixed numeric recipes
  (`lagrangian-residual`, `hamiltonian-rate-field`,
  `hamiltonian-residual`, Legendre maps). Each is presented as a
  composition of the readout primitive with the solver, not as a
  re-derived formula.

### `cert/` — the three-obligation certifier

Seven modules, all `#lang racket/base`. Three discharger modules
(one per obligation), one schema/emitter, one text renderer, one
freeze/tripwire, one independent high-precision cross-check.

- `recurrence-ode-check.rkt` — obligation 1 (per-core identity).
- `ring-structure-check.rkt` — obligation 2 (ring axioms + homomorphism +
  shared-subexpression / DAG equality).
- `known-answer-check.rkt` — obligation 3 (a fixed battery of
  closed-form / conserved-quantity checks).
- `certificate.rkt` — schema, predicates, `emit-certificate`,
  `certificate->string`, `cert-verdict`, `cert-digest`. The output is
  an *inert* s-expression (booleans / exact-ints / inexact reals /
  symbols / strings / proper lists only — explicitly: no closures, no
  structs, no syntax). An `inert-sexpr?` guard enforces this.
- `certificate-text-renderer.rkt` — a deterministic fixed-layout text
  renderer over the certificate sexpr.
- `regression-freeze.rkt` — a frozen reference string plus a tamper
  tripwire (`tamper-check`, `freeze-diff`).
- `high-precision-crosscheck.rkt` — an MPFR/bigfloat re-derivation
  recorded under `oracle-xcheck` and explicitly marked
  `load-bearing #f`.

### `physics/` — the typed boundary

Two modules.

- `api.rkt` — the only `#lang typed/racket/base` module in the library.
  Everything from the lower layers crosses through `require/typed` with
  `#:opaque` declarations on the kernel datatypes
  (`DerivativeLayout`, `CoefficientVector` as a flvector alias,
  `StateLayout`, `Residual`, `StateCorrection`, `IndexReducedResidual`,
  `Certificate`). User-supplied closures are typed via four function
  type aliases: `RateField`, `ResidualClosure`, `LagrangianClosure`,
  `HamiltonianClosure`. Two non-typed helpers (`time-differential`,
  `time-differential-tower`) are defined directly in this module.
- `examples.rkt` — `#lang racket/base` runners returning pure
  numeric verdicts (energy drift, momentum drift, analytic deviation).
  Imported into `main.rkt` via `require/typed`.

### `tests/` — 21 rackunit suites

All `#lang racket/base`. File names mark either a gate or a target
module (`oracle-test.rkt`, `stage-test.rkt`, `lu-test.rkt`,
`reduce-test.rkt`, `holonomic-test.rkt`, `homomorphism-test.rkt`,
`certificate-test.rkt`, `freeze-test.rkt`, `tui-test.rkt`,
`integration-stress-test.rkt`, `generators-battery-test.rkt`, etc.).
Total of roughly 647 `test-case` / `check-*` occurrences across
21 files; the project advertises a 382-check authoritative count
(the larger number includes individual check forms inside parametrized
cases).

---

## Conventions and Style

The codebase reads as a deliberately curated house style. The
recurring patterns:

**Language choice.** 41 of 42 implementation modules are
`#lang racket/base`; exactly one (`physics/api.rkt`) is
`#lang typed/racket/base`. This is the stated rule: the typed surface
is one module wide; the hot numeric path is never typed.

**Boundary discipline.** Everything the typed boundary imports comes
through `require/typed` with `#:opaque` for kernel datatypes — the
caller can hold and pass kernel values but cannot inspect their
representation. The lower-level numeric ring constructors are
deliberately *not* re-exported through the typed boundary; modules
that need them require the untyped `core/` files directly.

**Header docstring.** Every source file begins with a multi-line
`;;;`-prefixed header comment that states what the module is, what
contract it upholds, and what it explicitly does *not* do. The
"global rule" — no expression trees, no symbolic IR, no
representation introspection on any runtime path — is restated in
nearly every file. Many headers also cite an issue ID
(`physics-XYZ`, e.g. `physics-3mz`, `physics-7hm`, `physics-7wn`,
`physics-gwr`, `physics-2jp`) tying the module to a tracker entry,
plus "gate" labels (E1, E4, E6) for tests that pin a particular
acceptance criterion.

**Identifier style.** Long, descriptive, hyphen-separated names
spelled out in full (`coefficient-recurrences`,
`derivative-layout-slot-count`, `multiply-coefficient-vectors`,
`solve-residual-rates`, `reduce-constraint-index`,
`scale-coefficient-vector`). Abbreviation is rare; the codebase
prefers the long descriptive name over a short one even at length
cost. Predicate names use a trailing `?` (`residual?`,
`inert-sexpr?`, `derivative-layout?`).

**File naming.** Files are named in the same long descriptive style
as identifiers (`coefficient-recurrences.rkt`,
`constraint-index-reduction.rkt`,
`high-precision-crosscheck.rkt`,
`certificate-text-renderer.rkt`,
`staged-code-generation.rkt`). Tests carry a `-test.rkt` suffix.

**`require` / `provide`.** Every module's `provide` block is
grouped by purpose with section comments and, for every binding,
an inline type-shape comment (e.g.
`; derivative-layout (vectorof fixnum) -> fixnum | #f`). `require`
forms are clustered by source: standard-library imports first,
then `"../<layer>/<file>.rkt"` relative imports.
The typed `api.rkt`'s `require/typed` annotations spell out the
full function type of each imported binding.

**Numeric representation.** A "coefficient vector" is always an
`flvector` of length `derivative-layout-slot-count`. The choice is
universal across `core/`, `kernel/`, and the worked examples.

**Error model.** "No silent numeric failure" is a stated invariant;
singular Jacobians, non-converged Newton iterations, order
escalation past a declared cap, shape mismatches, and non-inert
certificate schemas all raise typed boundary errors that carry the
offending numeric witness (residual norm, condition number, offending
order). The header of each module declares which failure modes it
raises and which numeric witness travels with the error. No status
codes, no silent fallback paths.

**Tests are first-class.** Tests are not optional smoke; they are
load-bearing gates ("E1 GATE", "E4 GATE", "E6 GATE",
"physics-gwr acceptance", etc.) named alongside the production code
that they pin. `info.rkt` deliberately scopes the test runner to
`tests/` only and omits every source tree, so a clean run cannot
silently execute library modules.

---

## Build / Install / Test Story

At a structural level:

- The library declares itself as a Racket collection named `physics`
  via `library/info.rkt`. Dependencies are only `base`,
  `typed-racket-lib`, and `rackunit-lib` — no external libraries,
  consistent with the "pure Racket numeric code" stance. (`cert/
  high-precision-crosscheck.rkt` uses `math/bigfloat`, which is
  in-tree under Racket's `math` package — still ships with Racket,
  no third-party dep.)
- The single public entry point is `library/main.rkt`, requireable as
  `(require "library/main.rkt")` from the repo root. It re-exports the
  full typed boundary `physics/api.rkt`.
- Running `racket library/main.rkt` executes its `module+ main`, which
  prints worked-example verdicts.
- Running `raco test library/` executes only files under
  `library/tests/` (per `test-include-paths` and `test-omit-paths` in
  `info.rkt`). Each test file's checks run at module load and emit a
  banner via `module+ main`.
- The downstream pipeline is structurally declared but not yet
  implemented:
  `install/` is expected to take the library's emitted numeric code
  through C++ → assembly → `.so`; `interface/` is expected to wrap
  the resulting compiled artifact. Both currently contain only
  `README.md` placeholders.

There is no top-level Makefile, build script, or CI configuration in
the tree.

---

## Design Philosophy

The codebase makes its organizing principles unusually explicit, both
in the top-level `README.md` and in the per-module headers. The
recurring themes that show up in the code itself, independent of the
prose:

1. **Layered with a single seal.** Four `library/` sub-trees in a
   strict dependency order (`core` ← `kernel` ← `cert`, with
   `physics/api.rkt` as the only module that crosses all of them).
   The typed module is one file wide and uses `#:opaque` on every
   kernel datatype; the rest of the codebase is untyped `racket/base`.

2. **Two primitives, everything else is composition.** The headers
   identify exactly two primitives — a seed-and-read differentiation
   surface (`core/derivative-readout.rkt`) and the IFT solve
   (`kernel/residual-rate-solver.rkt`) — and explicitly mark every
   other operation (mechanics recipes, index reduction, time
   derivatives) as a *composition* of those two with numeric linear
   algebra. The header of `kernel/mechanics-recipes.rkt` even says
   "no third primitive".

3. **No-symbolics as a hard, restated rule.** Practically every
   module header restates the same constraint: no expression trees,
   no IR, no rewriting, no representation introspection on any
   runtime path. The only places where structured data does live
   (`core/formula-trees.rkt` and the certificate sexpr) carry
   explicit annotations that they are *compile-time / inert data
   only* and never traverse a runtime path. The certificate's
   `inert-sexpr?` predicate is enforced; `formula-trees` are
   consumed by a macro at expand time.

4. **Macros for compile-time staging.** `core/staged-code-generation`
   produces flat straight-line `flvector` code per a fixed
   derivative layout; all recursion exists in expand-time. The
   reference evaluator and the staged code are wired against each
   other via the oracle/E1 gate.

5. **Verified provenance as a first-class deliverable.** The
   `cert/` sub-tree is roughly comparable in size to `kernel/` and
   carries its own freeze fixture, tamper tripwire, deterministic
   digest, and independent high-precision cross-check (explicitly
   non-load-bearing). The certificate schema is presented as a
   cross-workstream contract — byte-comparable against a sibling
   backend ("dual-gen") that produces the same schema.

6. **Loud failure carrying numeric witnesses.** Every layer commits
   to raising on degenerate / over-cap / non-converged / shape-
   mismatch conditions and carrying the offending number with the
   error. The dense linear solver carries a 1-norm condition
   estimate; the solver raises the last residual norm; index
   reduction raises a relative-scale degenerate-system error;
   non-smooth operations carry an explicit regime tag and witness.

7. **Substrate-agnostic.** Headers and README repeatedly stress
   that downstream consumers (PINO loss, DAE rhs, training-pair
   generator, conservation check) are *outside* the library, which
   only produces and validates residuals.

The top-level README has a fourth large section ("Parked /
Not-Integrated Ideas") cataloging old design fragments — a lattice
substrate, three S-expression dialects, a CUDA emitter, a registry
+ CLI, a Python user surface, language critiques, topological tooling
— each ending with a stated verdict. None of these are present in
the implementation; they are documented exclusively as triage notes
adjacent to the built kernel.

---

## Cross-Cutting Concerns

- **Logging.** None visible. The codebase is silent except for
  `module+ main` banners in test files and the `main.rkt`
  print-loop.
- **Contracts.** Used implicitly through `require/typed` at the
  `physics/api.rkt` boundary; not the Racket `racket/contract`
  library. Internal modules use plain Racket `error` raises with
  formatted messages that include the failing numeric witness.
- **FFI.** None.
- **External deps.** Only `typed-racket-lib`, `rackunit-lib`, and
  Racket's bundled `math` (for `math/bigfloat` in the
  non-load-bearing cross-check). The library otherwise runs on
  `racket/base` plus `racket/flonum` / `racket/list` /
  `racket/match` / `racket/math` / `racket/string` /
  `racket/vector` only.
- **Macros.** Used heavily but locally in `core/
  staged-code-generation.rkt` and `core/staged-reference-check.rkt`;
  all macro work is for-syntax compile-time work and emits flat
  numeric code.
- **Configuration.** None at runtime; the only configuration is the
  per-call derivative-layout descriptor and solver keyword
  arguments (`#:tol`, `#:max-iters`, `#:guess`,
  `#:rel-tol`, `#:max-order`, `#:project?`).
- **Issue / agent workflow.** `AGENTS.md` and `CLAUDE.md` route work
  through the `bd` (beads) tracker, which uses a local Dolt DB
  synced via git refs (`refs/dolt/data`). Issue IDs are embedded as
  header tags in module docstrings (`physics-3mz`, etc.) to anchor
  each module to its tracker entry.

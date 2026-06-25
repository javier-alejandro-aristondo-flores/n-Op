# Scoring, Not Solving — a verification oracle for materials physics

> **Slide-deck outline.** One block per slide: title, on-slide content, and a speaker note.
> Ready to drop into Beamer / reveal.js / PowerPoint. This is a **presentation artifact**, a
> hand-written companion to the spec — **not** part of the lint-enforced atomic tree (like
> `docs/accuracy-ledger.md` and `docs/computational-overview.md`). Every CS claim cites its
> canonical `arch-xx` / `impl-xx` source so a skeptic can verify rather than take it on faith.
>
> **Audience.** General-technical — engineers, materials scientists, physicists. The presenter
> is the room's only computer scientist; the deck's job is to make the computer science the
> visible, load-bearing contribution.
>
> **Spine.** *Verifying a solution is cheaper than producing one.* `/physics` is an **oracle**
> that grades a candidate state. Every CS technique in the deck — a compiler, a type system,
> content addressing, automatic differentiation, a decidable grammar — makes that grading fast,
> exhaustive, and trustworthy. We return to the spine in slides 2, 4, 9, 12, and 14.

---

## Slide 1 — Title

**Scoring, Not Solving: a verification oracle for materials physics**

- Subtitle: *It is harder to solve a problem than to verify a solution — so we built the
  verifier.*
- One line of stakes: the target application is designing **durable ultra-wide-bandgap
  semiconductor devices** for harsh environments (>500 °C, high field).
- Pivot line: *This talk is about the computer science that makes that design loop possible.*

> **Speaker note.** Set expectations in the first 20 seconds: the physics is the *domain*, but
> the talk is a CS talk. Promise one organizing idea (the next slide) and tell them it recurs.

---

## Slide 2 — The asymmetry (the thesis)

**Finding an answer is hard. Checking an answer is easy.**

- Complexity-theory hook: the defining property of **NP** is that a *certificate* (a witness)
  is checkable in polynomial time even when finding it is exponentially hard. Sudoku, factoring,
  satisfiability: hard to solve, trivial to check.
- `/physics` lives on the **cheap side of that gap on purpose**: it never searches for the
  physical state; it grades a state it is handed.
- The whole system is engineered to make *checking* fast, exhaustive, and trustworthy.

> **Speaker note.** This is the organizing idea. Say explicitly: "I'll come back to this five
> times." Everything downstream (compiler, types, AD) is in service of cheap, trustworthy
> checking.

---

## Slide 3 — What `/physics` is: a pure oracle

**Input: a candidate state. Output: how much it violates physics law, plus a certificate.**

- Contract, side by side:
  - **Solver:** search the space for an `x` with `F(x) = 0`. Expensive, iterative, global.
  - **Oracle (`/physics`):** take the `x` you're handed, return `‖F(x)‖` + a cert. Local, direct.
- "`/physics` is a pure oracle" — it owns no training loop and no sample-selection logic
  (`arch-01-purpose §72–75`).
- The scoring principle holds at **every length-and-time scale** — femtoseconds to years, atom
  to device (`arch-21-multiscale-state §87–88`).

> **Speaker note.** The candidate state comes from a learned model (the neural operator) — but
> that's another talk. Here the operator is just "whoever hands us an `x`." Keep the focus on
> the oracle's one job. Slides 4–5 show how cheap and how trustworthy that one job is.

---

## Slide 4 — The asymmetry, in numbers: the cost ladder

**Checking runs in microseconds where solving runs in minutes.**

- The four cost tiers (`impl-07-residual-factory §175–191`):

  | Tier | Budget | Cadence | Example |
  |---|---|---|---|
  | **T0** | ≤ 10 µs, closed-form | every gradient step | algebraic law residuals |
  | **T1** | ≤ 10 ms, small linear algebra / 1-D quadrature | per batch (importance-sampled) | response functions |
  | **T2** | ≤ 10 s, Brillouin-zone / mesh integral | per epoch (cached) | transmission spectra |
  | **T3** | ≤ 10 min, iterative / PDE | calibration only | full transport solves |

- The corresponding *solve* (a full BTE / NEGF / SCF run) is the **T3** rung — minutes. The
  oracle keeps scoring on the **T0/T1** rungs, "fast by construction" (`arch-07-pipeline §28–32`).

> **Speaker note.** This slide is the thesis made quantitative. The four-orders-of-magnitude gap
> between "check it" (µs) and "solve it" (min) is the entire reason a learning loop is feasible:
> you can afford to grade millions of candidates.

---

## Slide 5 — The certificate: a checkable witness

**Every score ships with a small, independently checkable proof object.**

- "The certificate emitted for any prediction is an inert s-expression carrying scalar verdicts
  plus numeric witnesses for failures" (`arch-12-cert §19–22`). This *is* an NP-style
  certificate: cheap to check, carries its own evidence.
- A failure carries a **witness** — the exact offending data, e.g. a `(P_sp, e₃₁)` coefficient
  pair or a `(row 120, row 63, observable)` triple (`arch-12-cert §109–119`).
- Verdicts combine by a **semilattice meet**: the composition passes only if every obligation
  leaf passes; one `Failed` leaf makes the whole verdict `Failed` (`impl-07-residual-factory §56–60`).
  Lattice theory, used by name.
- Ten obligations checked: symmetry, bounds, analytic limits, reference battery, conservation,
  consistency, bulk-boundary correspondence, versioning, surrogate validity, adjoint existence
  (`arch-12-cert §24–40`).

> **Speaker note.** Emphasize *independently checkable*: the cert is inert data, so a third party
> (or a future you) can re-verify a result without re-running the oracle. This is how you earn
> trust from a room of physicists — the claim comes with its receipt.

---

## Slide 6 — Physics as a formal language I: the alphabet and grammar

**The physics we score is a closed formal language.**

- Closed vocabularies — a finite alphabet (`arch-09-vocabularies`):
  - 12 computational **methods** (+3 sub-methods)
  - 20 abstract-property **templates**
  - 125 named **formulas** (+2 architectural markers)
  - 11 observable **bundles** · 19 **residual categories** · 10 **cert obligations** · 4 **typeclasses**
- "instances are programs in this vocabulary" (`arch-09-vocabularies §9.1`).
- Why *closed* earns its keep: a finite, decidable grammar means the set of well-formed
  questions is **enumerable and exhaustive** — *"there should be no more questions one can ask."*

> **Speaker note.** Materials scientists expect an open-ended pile of formulas. The CS move is to
> close the set and make composition the only growth mechanism — that's what makes exhaustiveness
> a provable property rather than an aspiration.

---

## Slide 7 — Physics as a formal language II: the AST

**A composed physics problem is an abstract syntax tree.**

- The `PhysicsGraph`: "a typed, hash-consed, content-addressed directed acyclic graph"
  (`arch-06-physics-graph`).
- Three node kinds — the grammar's terminals (`arch-06-physics-graph §6.2`):
  `Input | FormulaApply | MethodInvoke`.
- The 125 formulas and 12 methods are **typing rules** for these nodes (`arch-06-physics-graph §6.5`).
- Composing observables **is** composing subgraphs; the 20 templates are
  "graph-construction macros." A new observable is a new sentence in the language, not new code.

> **Speaker note.** Draw the analogy on the board: source code → AST → typed IR. A physics
> composition takes exactly the same path. This reframes "add a property" from a coding task to
> a parsing task — which is what unlocks the compiler on the next slide.

---

## Slide 8 — `/physics` is a compiler  ⟵ centerpiece

**It parses a physics problem and compiles it to a numerical kernel.**

- The five-stage pipeline reads as a textbook compiler (`arch-07-pipeline`,
  `docs/computational-overview.md §1`):

  | Stage | Compiler analogue | What happens |
  |---|---|---|
  | **1 Symbolic lift** | parse / front-end | instantiate templates → initial typed graph (`§7.1`) |
  | **2 Symmetry quotient** | domain optimization pass | irrep block-diagonalization; IBZ orbit collapse — *up to 48× fewer k-points* (`§7.2`) |
  | **2.5 Invariant synthesis** | semantic analysis | build the symmetry-adapted basis (`§7.2.5`) |
  | **3 Algebraic simplification** | classic IR optimization | **hash-consing**, **cross-formula CSE**, **tearing / alias elimination** (`§7.3`) |
  | **4 Lowering + adjoint synthesis** | codegen + register allocation | choose compression plans, synthesize adjoints, emit kernel (`§7.4`) |
  | **5 Runtime kernel** | the compiled executable | straight-line numeric code; all symbolic work already resolved (`§7.5`) |

> **Speaker note.** This is the "I built a compiler for physics" slide — land it. The named
> optimizations (CSE, hash-consing, lowering) are the same ones in GCC/LLVM; here they run over
> physics expressions. Stage 2's symmetry pass is the one *domain-specific* optimization, and it
> buys a 48× constant factor for free.

---

## Slide 9 — Staging: pay the symbolic cost once

**Compile once per problem; execute millions of times.**

- The compile/runtime split is **multi-stage programming / partial evaluation**:
  - Stages 1–4 run **once per composition** — seconds to minutes (`arch-07-pipeline §7.6`).
  - Stage 5 runs **per state sample** — microseconds to milliseconds.
- All symbolic reasoning, symmetry reduction, and optimization is resolved at compile time, so
  the hot path is a specialized, branch-free kernel.
- This is *why* checking is cheap (slide 4): the system residualizes the physics once and then
  evaluates the residual forever.

> **Speaker note.** Connect back to the spine explicitly: the µs cost on slide 4 isn't luck, it's
> the payoff of staging. Partial evaluation is a recognizable CS technique (Futamura, staged
> metaprogramming) — name it so the CS audience clocks the rigor.

---

## Slide 10 — A type system, and real categorical structure

**Four orthogonal typeclasses give every quantity a type; the algebra is genuine.**

- Four Layer-0 typeclasses — orthogonal axes every output is typed against (`arch-10-typeclasses`):
  - `Quantity` (value / units) · `Sampleable` (shape / domain) ·
    `HasAnalyticStructure` (constraint / law) · `DiscreteStructure` (combinatorial invariant).
- Cert checkers are "generic functions over the typeclasses" (`arch-12-cert §45–50`) —
  typeclass-dispatched parametric polymorphism: one checker per axis, reused across all physics.
- The category theory is real and load-bearing, not decoration:
  - cert obligation 7 is a "`DiscreteStructure` morphism" mapping bulk classification to boundary
    states (`arch-12-cert §31–34`);
  - `SymbolicTensorOps` forms a "colored-operad / free symmetric monoidal category"
    (`arch-20-representations §98–103`) — composition *is* operadic substitution;
  - the Reynolds projector `P = (1/|G|) Σ_g ρ(g)` maps representations to their invariant
    subspaces and **provably preserves positive-semidefiniteness** (`arch-19-coupling-structure`).

> **Speaker note.** State precisely what each structure *buys*: the typeclasses buy generic
> checkers (write once, dispatch everywhere); the operad buys lawful composition; the Reynolds
> projector buys a provable physical guarantee (a PSD dissipation operator). That's how the rigor
> reads as substance to engineers, not as jargon.

---

## Slide 11 — Content addressing: Git's idea, for physics

**Every object is named by the hash of its content.**

- `Address[D] = Hash(domain_separator, schema_version, canonical_bytes)`
  (`arch-20-representations §20.4`).
- Consequences, all free:
  - **Memoization & dedup** — identical sub-expressions collapse to one node (hash-consing).
  - **Tamper-evidence** — changing any payload changes its hash and trips the freeze comparison
    (`arch-12-cert §155–160`).
  - **Structural sharing** — the whole IR is a Merkle DAG, like Git commits or a build cache.

> **Speaker note.** The most relatable analogy in the deck: everyone in the room has used Git.
> "Same trick — a content hash as a name — applied to physics expressions." It's where the
> reproducibility and caching guarantees come from.

---

## Slide 12 — Automatic differentiation as a first-class output

**The oracle returns gradients, not just scores — cheaply.**

- Stage 5 emits **cotangents** (`∂R/∂x̂`) alongside residuals — reverse-mode AD built into the
  kernel.
- The **implicit-function-theorem adjoint** makes the gradient of a fixed-point solve cost "one
  extra linear solve, independent of forward iteration count" (`arch-07-pipeline §133–137`) —
  another instance of the verify-cheap asymmetry, now for derivatives.
- The bridge to the learned model is a typed **ABI / calling convention**: the oracle returns
  `∂R/∂x̂`; the consumer "brings its own backward" to chain `∂x̂/∂θ` (`arch-16-pino-bridge`).
  Three exports — Generate / Validate / Import — form the interface.

> **Speaker note.** Tie to the spine one more time: even differentiation obeys verify < solve —
> the adjoint replaces an unrolled iteration with a single linear solve. The "bring your own
> backward" line is the clean seam between the oracle and the learner; keep the learner offstage.

---

## Slide 13 — Well-formedness, checked by the compiler

**Ill-formed physics is rejected mechanically, before it ever runs.**

- Registration is a **decidable gate**: every applicability predicate is "first-order decidable …
  finite case analysis on typeclass tags, not numeric thresholds" (`impl-04-formulas`).
- The **adjoint gate** fails the build when a hand-or-auto-derived gradient disagrees with a
  finite-difference check beyond `τ_adj` (`impl-07-residual-factory §7.5`).
- Compose-time **refusals** reject inconsistent compositions by tag comparison — e.g. an
  unprovenanced coefficient, or a double-counted temperature path (`arch-12-cert §12.0.3`).
- The 13-phase build sequence (`impl-10-build-sequence`) is the state machine that sequences and
  enforces all of it.

> **Speaker note.** The message: correctness is a property the compiler *checks*, so a registered
> composition is well-formed by construction. This is the same guarantee a strongly-typed language
> gives — caught at build time, not discovered in production.

---

## Slide 14 — Why the computer science is the contribution

**Every guarantee the domain cares about is delivered by a CS construct.**

| The physicists want… | …delivered by |
|---|---|
| **Speed** (millions of evaluations) | staged compilation + the verify < solve asymmetry |
| **Exhaustiveness** ("no more questions") | a closed grammar + decidable applicability |
| **Trust** (verifiable claims) | checkable certificates + content-addressed tamper-evidence |
| **Composability** (new observables for free) | an AST with a type system |
| **Gradients** (a learning loop) | first-class AD + implicit-function adjoints |

- Closing line: *The physics is the domain; the computer science is what makes it a system.*

> **Speaker note.** This is the slide that answers "what did the computer scientist add?" — point
> at each row. End on the closing line and stop; let it sit.

---

## Slide 15 — Backup (Q&A reserve)

Held in reserve for domain-expert questions:

- The full closed-vocabulary tables (12 methods, 20 templates, 125 formulas, 11 bundles).
- The 19 residual categories (`arch-11-residuals §11.1`): 9 equation-of-motion, 3 structural,
  5 algebraic-identity, 2 constraint.
- The 10 cert obligations in full (`arch-12-cert §24–40`).
- The tier/cost/cadence table with per-tier examples (`impl-07-residual-factory §175–191`).
- The error model: per-residual budget composed from input σ, model-form error, compression
  truncation, dressing staleness, and coefficient-provenance σ (`arch-11-residuals §11.7`).

> **Speaker note.** Don't present these; pull them up only if asked. They're the receipts behind
> the headline claims.

---

## Appendix — CS concept → where it lives (citation map)

| CS concept | In `/physics` | Cite |
|---|---|---|
| NP certificate / verify < solve | the cert + the scoring principle (grade the candidate) | `arch-12`, `arch-01`, `arch-21` |
| Complexity tiers of checking | cadence T0–T3 | `impl-07 §175–191` |
| Formal language / closed grammar | the vocabularies | `arch-09` |
| AST + typing rules | PhysicsGraph, 3 node kinds | `arch-06` |
| Compiler passes (CSE, hash-consing, lowering, codegen) | Stages 1–5 | `arch-07` |
| Partial evaluation / staging | compile-once / run-per-sample | `arch-07 §7.6` |
| Type system / typeclass dispatch | 4 Layer-0 typeclasses | `arch-10`, `arch-12` |
| Category theory (operad, morphism, Reynolds functor) | SymbolicTensorOps, obligation 7, invariant generator | `arch-20`, `arch-19` |
| Lattice theory | verdict semilattice meet | `impl-07 §56–60` |
| Merkle DAG / content addressing (Git) | `Address`, hash-consing | `arch-20 §20.4` |
| Reverse-mode AD / implicit-diff adjoint | cotangent exports | `arch-07 §133–137`, `arch-16` |
| Decidability / type-checking / build automaton | applicability gate, refusals, 13-phase build | `impl-04`, `impl-10`, `arch-12 §12.0.3` |

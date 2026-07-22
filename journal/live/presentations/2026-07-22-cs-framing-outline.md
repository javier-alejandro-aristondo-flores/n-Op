# Talk outline + diagram specs — why the computer scientist belongs in crystal research

*2026-07-22 · working artifact under `journal/live/` (outside the book's `pages/`, exempt from
the checkers) · deliverable = outline + diagram specs, not a rendered deck*

> **This is the source material, not the talk.** The talk itself — 14 sparse slides with speaker
> notes — is `2026-07-22-talk-script.md`. Content cut from the spoken version is retained here
> and in that file's Q&A backup section; nothing was discarded.

---

## The situation this is built for

**Audience:** mixed technical, **non-CS** — materials scientists, electrical engineers,
physicists. They own the physics already. **The CS content is therefore the new information, and
it is the argument.**

**Rhetorical goal:** show why a computer scientist matters in crystal research. The talk must
never read as "here is my machinery." Every CS idea earns its slide by **dissolving a problem the
audience personally lives with**.

**Positioning:** against *both* incumbents — direct simulation and ML surrogates.

**The relationship, stated correctly (this is the spine — do not drift from it):**
You train a neural operator to predict material behavior. Its loss needs physics. The oracle
compiles the laws into **keyed, differentiable residual terms and their gradients**, which enter
that loss. That is the entire relationship. There is **no proposer component** — the operator
emits a state, the oracle scores it, the residuals are loss terms. "Properties in → structures
out" is a stated long-run *direction*; inverse design is explicitly out of scope for `/physics`
([out-of-scope]) and must be presented that way.

## The pain → concept → resolution table (the engine of the talk)

| Their pain | CS concept | Resolution |
|---|---|---|
| the problem is genuinely intractable in general | NP-hardness / QMA-completeness; verification asymmetry | stop trying to solve it; make *checking* cheap |
| simulation unaffordable at device conditions | partial evaluation / staging; symmetry as an optimization pass | compile once per material, specialize, reuse |
| "is my question even well-posed?" | parsing + static semantics; decidable predicates | it compiles or is rejected — never fails ambiguously at runtime |
| ML models can't say when they're wrong | totality; proof-carrying results | refusal-as-absence + certificates |
| "which code, which version, which parameters made this number?" | content addressing | reproducibility as a *structural property*, not a policy |
| sign/unit/frame errors that silently invert results | machine-checked invariants | "be careful" becomes "cannot be gotten wrong" ← **the closer** |
| every new observable = new bespoke code | closed formal language | a new observable is a new *sentence*, not new code |
| gradients are expensive | implicit-function adjoint | one linear solve, independent of iteration count |

---

## Act 0 — The frame

**Beat 1.** The problem: these materials must be predicted at conditions where measurement is hard
and simulation is unaffordable — harsh-environment ultra-wide-bandgap devices, the jet-turbine
hook (>500 °C, thermal cycling, vibration, high field, radiation).

**Beat 2.** Two incumbents, both unsatisfying: direct simulation is trustworthy but prohibitively
expensive; learned surrogates are fast but untrustworthy *exactly* in the extrapolated corners you
care about. → **D1**

**Beat 3.** The asymmetry, stated as the thesis: **verifying a solution is cheaper than producing
one.** → **D2**

**Beat 4.** The move: *don't build a faster solver — build a grader cheap enough to sit inside the
learner's loss and discipline it at every step.*
Thesis line: *"I'm not here to speed up your physics. I'm here to change what kind of object it
is."*

## Act 1 — What kind of problem is this? *(the complexity frame)*

> This act is where the CS credential is established. It is also the honest answer to "why not
> just compute it?" — because in general, **you cannot**.

**Beat 5 — where the problem actually sits.** Finding ground states of classical lattice models is
**NP-hard** (Barahona 1982, Ising spin glass). The general quantum case — the **local Hamiltonian
problem** — is **QMA-complete** (Kitaev; 2-local via Kempe–Kitaev–Regev). Nobody solves this in
general, and no amount of hardware changes that. So the question is not "how do we solve it," it
is **"what is the cheapest useful thing we can do?"** → **D13**

**Beat 6 — the oracle machine, properly.** A machine with a black box that answers queries at unit
cost. How complexity theory actually *uses* oracles: relativized classes `P^A`, `NP^A`; the
polynomial hierarchy built by iterated oracle access (`Σ₀ᵖ = P`, `Σ_{k+1}ᵖ = NP^{Σ_kᵖ}`) — oracles
as the instrument that *stratifies* difficulty. And their limit as a proof technique:
**Baker–Gill–Solovay** — there exist oracles `A` with `P^A = NP^A` and `B` with `P^B ≠ NP^B`, so
any argument that relativizes cannot settle P vs NP. → **D14**

**Beat 7 — and ours is deliberately *not* a decision oracle.** A complexity oracle returns a bit.
This one returns a real-valued residual vector **and its gradient**. That makes it a *function /
valuation* oracle, and the choice is deliberate: **collapsing to a bit destroys exactly the signal
a learner needs.** The better-matching models are the ones built around richer queries —
separation-vs-optimization (Grötschel–Lovász–Schrijver) and query learning (membership and
equivalence queries, Angluin's `L*`; statistical queries, Kearns). → **D15**

*Say this precisely. Getting the distinction right is what separates a computer scientist from
someone borrowing the vocabulary.*

**Beat 8 — CEGIS is the structural twin.** Counterexample-guided inductive synthesis: a learner
proposes a candidate, a verifier checks it and returns a counterexample, repeat. That is this
architecture, with the counterexample replaced by a **gradient** — a differentiable relaxation of
a mainstream synthesis pattern. The design is *known*, not ad hoc. → **D16**

**Beat 9 — the payoff, and the strongest argument in the talk.** Verification is only cheap **if
you are handed the complete witness.** That is precisely why the oracle demands a full state —
*including the electronic degrees of freedom* — rather than just a structure: hand it a partial
witness and the checker must **solve** for the rest, which puts you straight back in the hard
class. Therefore **"score-not-solve" is a complexity-theoretic requirement, not a stylistic
preference** — and it is also why the operator must carry the electronic state. → **D17**

## Act 2 — What the system actually is

**Beat 10.** The relationship in one diagram: operator emits a candidate state → oracle scores it
→ keyed residuals + gradients → those *are* terms in the operator's training loss. → **D3**

**Beat 11.** Why this is not merely "add a physics penalty": the residuals are **granular and
keyed** (per-law, per-axis-point), never aggregated into a single number — so the loss can be
weighted, curriculum-scheduled, and *audited law by law*.

**Beat 12.** Honest scope, stated here rather than defensively at the end: this is a specified and
audited design with **zero implementation code**; the long-run aim is property-targeted design,
which is explicitly out of scope for the oracle today.

## Act 3 — Inputs, parsing, and the object being scored

**Beat 13 — the front end.** CIF text → **parse** → **elaborate**. Canon states it already:
*"A CIF alone is not a scoreable object; it is a compile request"* ([product]). Parsing yields
syntax; elaboration yields a typed, checked object. The environment record is the extension no
crystallographic format carries. → **D18**

**Beat 14 — the closed grammar.** [product]: *"It accepts **no open-ended expressions**: the
grammar is the closed vocabularies."* [rationale]: *"build a typed dataflow graph … **from a fixed
grammar**."* So an observable request is a **sentence**, and compiling it is parse + type-check.
Terminals are the 132 substantive formulas, 12 methods, 20 templates, 11 bundles. *A new
observable is a new sentence, not new code.* Consequences: enumerable, traceable, decidable.
→ **D4**

**Beat 15 — the state, and a representation choice that buys an asymptotic class.** The state is a
fixed-width record; the electronic slot is the expensive one. Dense it is **`O(N_r²)`**
([gamma-budget]) — but it is **never densified**: reciprocal, block-diagonal, stored as
orbitals (low-rank in the band index). **~18 MB at MVP scale versus ~460 MB densified.** This is
the clearest single case of a CS instinct paying a physics dividend.

## Act 4 — The machine

**Beat 16 — the oracle *is* a compiler.** Front-end (lift + applicability prune) → middle-end
(symmetry quotient, invariant synthesis, hash-consing, cross-formula CSE, tearing, equality
saturation) → back-end (lowering, adjoint synthesis, codegen) → emitted kernel. → **D5**

**Beat 17 — Stage 1 is literally a front end, and the static semantics are decidable.**
[computational-overview]'s stage table: *"Symbolic lift: request + descriptors → pruned IR"* via
**macro expansion + Boolean decision diagrams**. Then the static check — the
**applicability-decidability invariant** ([named-formulas]): every predicate is *first-order
decidable* on typeclass tags, and **non-decidable classifiers are rejected at registration.**
Decidability here is enforced, not aspirational. Payoff for this audience ([rationale]): *requests
are decidable — they compile or are rejected, nothing fails ambiguously at runtime* →
**the tool tells you your question is ill-posed before it burns a week of CPU.** → **D18**

**Beat 18 — why compile-once/call-many is *principled*.** It is **partial evaluation / staging**
(Futamura): specialize a general law-checker to one material and you get a straight-line numeric
kernel. The corpus states the bet plainly ([audit-prompt]): push unavoidable cost to compile-time
specialization so the runtime hot path stays cheap. That is amortized analysis as an architecture.

**Beat 19 — the complexity ledger.** The headline is a *stated architectural commitment*: **no
runtime per-sample hot path exceeds `O(log n)`, and none calls a solver**
([computational-overview] §2.5, [representation-substrate] §5). This is the "better" claim in
its most defensible form — a checkable invariant rather than a vibe. → **D19**

**Beat 20 — symmetry as an optimization pass.** Representation theory deployed the way a compiler
deploys strength reduction: block-diagonalize by irrep, collapse orbits, and the work falls to the
number of *orbits* rather than points. Compile-time cost is bounded and paid once — the Reynolds
projection is `O(|G|·dim(T)²)` ≤ ~12M ops ([coupling-structure]); the runtime projector
apply is `O(|G|/|H| · tensor rank)`, cached after first evaluation. → **D6**

**Beat 21 — circuit-level optimization on the law graph.** Hash-consing (`O(1)` amortized, [computational-overview]) and
cross-formula CSE mean a sub-expression shared by a dozen formulas is computed once. Identical in
kind to circuit minimization. → **D7**

**Beat 22 — differentiation as a first-class design constraint.** The differentiability lattice
(`D0 | DX | D1 | D2 | D3 | D4`) *types* what is differentiable and how. The payoff: naive
reverse-mode through a fixed-point iteration must tape all `N` iterations, whereas the
**implicit-function adjoint** costs **one linear solve, independent of `N`**. → **D8**

**Beat 23 — an honesty beat.** Equality saturation is expensive, so it is confined **offline**;
there is deliberately no runtime rewrite engine. A complexity-motivated architectural boundary,
admitted rather than hidden.

## Act 5 — Outputs and guarantees

**Beat 24.** The four exits: keyed residuals, requested values, optional cotangents, kernel hash.

**Beat 25.** **Evidence, never verdicts** — raw keyed floats; no aggregation, thresholding, or
judgment anywhere. Judgment belongs to the consumer. For an instrument this is the honest
contract: *it measures; it does not editorialize.*

**Beat 26.** **Refusal is absence** (totality): a check the oracle cannot stand behind is not in
the kernel at all, and the absence is accounted for. Applicability is a decidable predicate,
evaluated as a decision diagram in `O(decision-path length)` ([representation-substrate] §5).
→ **D9**

**Beat 27.** **Proof-carrying results.** Every kernel carries a certificate: verdicts plus numeric
witnesses, no natural language. Aggregation is a **semilattice meet** over Passed/Pending/Failed,
`O(children)` with early exit on `Failed` ([representation-substrate] §5) — algebraic, not ad
hoc. → **D10**

**Beat 28.** **Content addressing.** Every object named by the hash of its canonical bytes; file
hash = kernel hash. *Reproducibility becomes a structural property, not a policy.* → **D11**

## Act 6 — Justification, evidence, honesty

**Beat 29 — a real negative result, offered deliberately.** "Can one intermediate representation
serve both a scorer and a stepper?" The strong form is **refuted** — causality assignment is a
*global matching* property, not per-node. What survives is a weaker, useful theorem: a shared
kernel with two separate lowerings. A crisp negative result buys more credibility than any
positive claim.

**Beat 30 — how correctness was engineered.** Machine-checked corpus invariants (globally unique
topic ownership, symmetric dependency graph, content-hash freshness), a calibration-gated
adversarial audit, and a **standing traps register**: durable findings where *the wrong version
looks exactly as plausible as the right one*. Show one worked sign-convention trap. → **D12**

**Beat 31 — the parser bug, told against myself.** `seams.py` originally scanned only
backtick-quoted formula names, so `formula = <name>` arguments were invisible: the checker
reported **clean** while pages invoked formulas absent from the registry. Widening the scan
surfaced 17 findings immediately. A false negative caused by an under-specified parser — proof
that parsing precision is a *correctness* property, not pedantry.

**Beat 32 — close.** Return to the asymmetry, then bookend the oracle frame honestly: oracles
stratify difficulty and make hard things approachable, but **relativization is also the limit of
the technique** — an oracle tells you what is reachable *relative to* what you are handed. That is
exactly why the completeness of the witness (Beat 9) was the load-bearing design decision.
Final line: *this is what a computer scientist brings to crystal research — not faster physics,
but physics that can be addressed, checked, and trusted.*

---

## Diagram specs

Each states what it **shows** and what it **proves**. Classes: (A) automata/state-transition,
(C) categorical, (L) logical circuit, (N) numerical analysis, (X) complexity.

> **Mapping to the talk's twelve figures.** The spoken deck merges and reallocates these:
> D1→F1 · D13+D2→F2 · D14+D15→F3 · D17→F4 · D3→F5 · **F6 is new** (the emitted artifact opened
> up — no D-spec, added because none of the originals showed the end product) · D4+D18→F7
> (grammar and front end merged into the compiler flow) · D6→F8 · D19+D8→F9 · D9→F10 ·
> D10+D11→F11 · D12→F12. Held as Q&A backup, unrendered: D7 (CSE), D16 (CEGIS), the pullback
> square, the evolver negative result. Slide *N* of the script uses figure *N−1*.

**D1 — The two incumbents.** 2×2, cost × trustworthiness: direct simulation trustworthy but
unaffordable, surrogates cheap but untrustworthy, target quadrant empty — then the third way,
*make the checker cheap instead of the solver fast*.
*Proves: this is not a midpoint compromise.*

**D2 — Verify < solve.** (A) Two paths to the same answer: an expansive search tree for
*producing*, one straight-line pass for *checking* a supplied candidate. Pictorial, no notation.
*Proves: the thesis, without prerequisites.*

**D3 — The actual loop.** (A) Operator → candidate state → oracle → keyed residual vector +
gradients → loss → back into the operator's weights. Label the oracle box **"loss term, not
solver."** The most important diagram in the talk.
*Proves: what the oracle is actually for.* **Uncuttable.**

**D4 — The closed grammar.** A short BNF-ish production plus vocabulary counts, and one observable
shown as a *sentence* derived from it.
*Proves: enumerable, traceable, decidable — no free-form expressions.*

**D5 — The compiler pipeline.** (A) Front/middle/back-end with the artifact at each stage
boundary, ending at the emitted kernel; annotate the two time scales (seconds–minutes once;
µs–ms millions of times).
*Proves: this is a compiler, not a script.*

**D6 — Symmetry quotient.** (C) Dense operator → group action → orbit collapse → block-diagonal by
irrep, with the work-unit count before/after.
*Proves: representation theory used as a compiler optimization.*

**D7 — Hash-consing and CSE on the law graph.** (L) Before: many formulas each re-deriving a
shared sub-expression. After: one shared node, fanned out. Circuit minimization.
*Proves: real optimization passes.*

**D8 — The implicit-function adjoint.** (N) A fixed-point iteration with `N` forward steps; naive
reverse-mode taping all `N` versus one linear solve against the transposed Jacobian, with a cost
bar flat in `N`.
*Proves: the numerical-analysis payoff, and why differentiation had to be owned in-house.*

**D9 — Applicability as a decision diagram.** (L) A reduced ordered BDD over material predicates
gating whether a check exists in the kernel at all; one path terminating in *absent*.
*Proves: validity is decided, not assumed — refusal is structural.*

**D10 — Certificate and verdict lattice.** (C) The three-element lattice with the meet operation,
over a Merkle DAG of obligation leaves; one leaf expanded to verdict + numeric witness.
*Proves: aggregation is algebraic; trust is carried, not asserted.*

**D11 — Content-addressed identity.** (C) A DAG where each node is named by the hash of its bytes;
identical inputs converge to the identical hash; file hash = kernel hash.
*Proves: reproducibility is structural.*

**D12 — A sign-convention trap, worked.** Two conventions for one physical quantity, both
plausible; lift a coefficient across and the physical consequence inverts. Then the fix: the
invariant stated once at a canonical location and machine-checked.
*Proves: the closing argument — the slide this audience feels most.* **Uncuttable.**

**D13 — The hardness landscape.** (X) Where the general problem sits — NP-hard for classical
lattice ground states, QMA-complete for the local Hamiltonian problem — against where *verifying a
supplied candidate* sits.
*Proves: nobody solves this in general, so verification is the only move.*

**D14 — Oracle machine and the PH ladder.** (X) A machine with a query tape and a black box; then
the ladder `P`, `P^NP`, `Σ₂ᵖ`, … built by iterated oracle access; a footnote panel for
Baker–Gill–Solovay (two oracles, opposite answers).
*Proves: oracles are a standard instrument for stratifying difficulty — and have known limits.*

**D15 — Decision oracle vs valuation oracle.** (X) The same black box drawn twice: one emitting a
single bit, one emitting a residual vector plus a gradient arrow.
*Proves: declining to be a decision oracle is deliberate, and is what makes it useful to a
learner.*

**D16 — CEGIS vs this architecture.** Side-by-side loops: propose → verify → counterexample →
refine, beside propose → score → **gradient** → refine.
*Proves: a known synthesis pattern, differentiably relaxed.*

**D17 — Certificate completeness.** Two panels. Partial witness: the verifier must run a solve to
fill the gap (drawn as the expensive path). Complete witness: the verifier only checks (drawn as
one pass).
*Proves: score-not-solve is a complexity requirement, not a preference.* **Uncuttable.**

**D18 — The parsing front end.** (A/L) CIF text → tokens → AST → elaborate + decidable prune →
typed IR, with an explicit **rejected** branch labelled *"ill-posed request, refused at compile
time."*
*Proves: questions are checked before they cost anything.*

**D19 — The complexity ledger.** (X) The `O(log n)` no-solver commitment as a banner, above the
per-operation table (set membership, map lookup, BDD evaluate, semilattice meet, projector apply),
each with its asymptotic and its constant-factor note.
*Proves: the performance claim is stated as a checkable invariant.*

---

## Slide-count reality check

Nineteen specs is more than one talk carries. Take **~12–14 spoken** and hold the rest as **Q&A
backup slides** — itself a credibility move with a technical audience. Uncuttable: **D3** (the
actual loop), **D17** (certificate completeness), **D12** (the sign trap). If the room skews
theoretical, promote D13–D16; if it skews applied, promote D6, D8, D19.

## Found vs. brought — keep this distinction honest

- **Found in canon:** every parsing hook, every complexity figure, and the decidability gate.
- **Brought in from outside:** the NP-hardness / QMA framing, all the oracle-class material, CEGIS,
  and **Beat 9** (certificate-completeness ⇒ score-not-solve). None of that is in the corpus.
  Beat 9 is a genuine synthesis and may deserve to land in canon — treat it as a candidate
  addition, not as something pre-existing.

## Honesty constraints (bake in; do not use a disclaimer slide)

- **Zero implementation code exists.** Every complexity figure is a **design commitment or
  architectural claim**, never a benchmark. Say so in the same breath as the number — volunteering
  it converts the vulnerability into credibility.
- Time-evolution / lifetime prediction is **deliberately unclaimed**.
- Inverse design is **out of scope for the oracle**; the end-goal framing is a direction.
- Language/toolchain is **open** (canon marks it closed; that decision has been reopened).

## Sources

By page `id`: [rationale] (narrative), [product] (behavioral contract; CIF-as-compile-request, the
closed grammar), [compose-time-pipeline], [computational-overview] (§2.5 hot-path commitments, stage
table), [representation-substrate] (§20.5 asymptotics), [canonical-vocabularies] (counts),
[residual-definitions], [cert-obligations], [applicability-classifiers], [named-formulas]
(differentiability lattice; applicability-decidability invariant), [coupling-structure]
(projection bounds), [topology-atlas] (Smith Normal Form, polynomial time),
[gamma-budget] (`O(N_r²)`, the 18 MB figure), [traps], [out-of-scope].
Negative result: `journal/live/specs/2026-07-16-evolver-duality-research.md`.

External (brought, cite as such): Barahona 1982; Kitaev, and Kempe–Kitaev–Regev; Baker–Gill–Solovay
1975; Grötschel–Lovász–Schrijver; Angluin `L*`; Kearns (statistical queries); Solar-Lezama et al.
(CEGIS); Futamura (partial evaluation).

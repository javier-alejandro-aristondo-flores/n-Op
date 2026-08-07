# Cohesion audit — the compile pipeline and the substrate

Subject: `journals/oracle/compilation/` — `compose-time-pipeline`, `representation-substrate`,
`physics-graph`.

Verdict in one line: **the central bet is met in substance and overstated in words; the real damage
is not in the bet but in the two bookkeeping layers under it — the error budget and the identity
scheme.**

The corpus genuinely hoists symmetry, dressing and structure discovery to compose time, and
score-don't-solve genuinely works for the equation-of-motion core. What fails is threefold:

1. **The bet is asserted at three strengths and the strongest is false** (F1) — "call no solver" is
   warranted by a table containing no physics operation.
2. **The error budget is assembled from intentions, not measurements** (F2–F4) — a trap the corpus
   itself marks *enforced* is violated by canon in three places including the canonical tolerance
   ledger; the one estimator that would check it does not exist for three of the four compression
   plans; and it runs before any state exists.
3. **`ResidualKey` is too coarse for three distinctions built on it** (F5–F6) — including one
   collision, `Import`'s cert-only leaf, that is specified outright and puts non-loss evidence under
   a loss-bearing key.

Findings 2 and 3 are the ones I would fix first. They are cheap to fix now and expensive later:
both are schema decisions that every downstream page has already been written against.

---

## 1 · Findings

### F1 — "call no solver" is asserted at three strengths, and the strongest is false
**Severity: high · Confidence: high**

Three formulations of one commitment:

| # | Location | Text | Strength |
|---|---|---|---|
| a | `compose-time-pipeline.md:64-68` | "the runtime only *applies* precomputed structured operators. That is what lets **every runtime hot path** stay logarithmic or better and **call no solver** ([representation-substrate#hot-paths])" | absolute, physics-scoped |
| b | `representation-substrate.md:289-290` | "No **runtime per-sample** hot path is worse than logarithmic. **No hot path requires a solver call.**" | absolute, substrate-scoped |
| c | `compose-time-pipeline.md:375-376` | "Runtime is a straight-line numeric function with no symbols, no structural branching, and **no solver invoked from scratch**." | qualified |

(a) and (c) are on the same page and contradict each other: (c)'s "from scratch" admits a
warm-started solver that (a) forbids outright.

(a) cites (b) as its warrant. **(b) cannot warrant it.** Every one of the fourteen rows in the
table at `representation-substrate.md:294-309` is a substrate/bookkeeping operation — `Address`
equality, `Universe` member equality, `SparseSet` membership, `PersistentMap` lookup/insert,
`MerkleDAG` root equality and diff, decision-diagram evaluate/equivalence, `EvidenceOps`
aggregate, group multiplication, symmetry projector. **Not one row is a physics operation.**
There is no eigensolve, no Brillouin-zone integral, no quadrature, no self-consistent loop.
(b) is a sound claim about the substrate's own contribution to the hot path; (a) reads it as a
claim about the physics and generalizes to "every runtime hot path".

The physics contradicts (a) directly:

- `computational-methods.md:63-107` — of the twelve closed methods, `variational-minimization`
  dispatches to **SCF-mixing** and **Pulay-mixing**; `kinetic-evolution` dispatches to
  **BTE-full**, master-equation, drift-diffusion, Cahn–Hilliard, Allen–Cahn and returns a
  `SteadyState`; `spectral-decomposition` dispatches to **Lanczos, Davidson, inverse-iteration,
  shift-invert**; `path-search` to NEB/dimer/string; `convex-optimization` to quadratic-program;
  `linear-response` to Sternheimer. Seven of the twelve are or contain iterative solvers.
- `physics-graph.md:149-154` — fixed-point solves "self-consistent field, relaxation-time
  transport, the steady-state Liouville problem — are `MethodInvoke` of the methods that carry
  fixed-point semantics", i.e. nodes *in* the graph.
- `compose-time-pipeline.md:341-342` — at the runtime stage, "The numeric work inside **is** the
  computational methods".
- `named-formulas.md:207-210` cost table — the `minutes` tier is "**self-consistent loop or
  partial-differential-equation solve**", ≤ 10 min, and it is a *per-evaluation* cost ("What one
  evaluation of the formula costs").

A per-sample stage billed at "microseconds–milliseconds" (`compose-time-pipeline.md:366`) cannot
contain a formula whose single evaluation is bounded at ten minutes.

**The corpus's real defense is good and is stated 310 lines later.** The three-class table at
`:384-391` confines the per-sample core to equation-of-motion residual evaluation and moves
solves into "on-request spectral" and "per-composition reference". That relocation is physically
sound — scoring `‖dx/dt − (L δE/δx + M δS/δx)‖²` at a *supplied* state needs one Hamiltonian
build, not an SCF solve, and that is the genuine content of score-don't-solve. The defect is that
sentence (a) is never qualified by it, and (a) is the sentence in the always-cheap section that
every other page inherits.

**What would refute F1:** a statement that "hot path" in (a) and (b) is a defined term meaning
"substrate operation on the per-sample path"; or evidence that the seven solver-bearing methods
are barred from the per-sample class. I found neither — `glossary.md` has no `hot path` entry.

**Proposed correction:** scope (a) to what (b) proves and let the three-class table carry the
physics claim. E.g. "…so the runtime only *applies* precomputed structured operators. Every
substrate operation on the per-sample path is then logarithmic or better
([representation-substrate#hot-paths]); which *physics* work remains per-sample, and which is
hoisted to composition scope, is the three-class table below." Then align (c) with (a).

---

### F2 — A trap the corpus marks "enforced" is violated by canon in three places, one of them mine
**Severity: high · Confidence: high**

`traps.md:792-800`, trap `target-is-not-measurement`:

> "A compression plan picks a rank to meet a truncation target; a truncated solve stops at a
> tolerance. **Those are intentions.** What the composition actually achieved is a different
> number, and **only that one is evidence** … *Breaks:* an error budget assembled from what every
> stage *meant* to do. — **enforced, [representation-substrate#estimate-dont-decide]**"

`residual-machinery.md:168-172` restates it normatively: "**An a-priori target is not a substitute
for an a-posteriori estimate** … The target is what the plan intended; the estimate is what it
achieved; only the second is evidence."

The enforcing anchor, `representation-substrate.md:257-269` (my page), is correct — it requires
an *a-posteriori* estimate and says "the estimates enter the error budget through
`Quantity.combineTol`".

Three canon pages state the opposite:

| Location | Text |
|---|---|
| `compose-time-pipeline.md:261-262` (**mine**) | "**The target** enters the per-residual error budget through `Quantity.combineTol`." |
| `residual-definitions.md:355-356` | the budget sums "**compression truncation** at the lowering stage, **against its per-plan error target**" |
| `cert-obligations.md:146` | "`δ_plan` \| per-compression-plan truncation error **target** …; **the sum over active plans is the compression term in `combineTol`** \| per plan, **declared at plan selection**" |

The third is the tolerance ledger, which `residual-definitions.md:368-369` names canonical for
tolerance values. So the canonical register for tolerances specifies the budget term as a sum of
declared intentions, "declared at plan selection".

This is not bookkeeping. `combineTol` is what a consumer reads to decide whether an answer is
good enough. Populating it with the target means the reported error bar is what the compiler
*hoped for*, and it is optimistic in exactly the regime where the rank estimate was wrong — see F3.

**What would refute F2:** a statement that both terms enter (target as budget line, estimate as
evidence). `residual-machinery.md:170-171` forecloses that ("only the second is evidence"), and
`cert-obligations.md:146` says "the sum over active plans **is** the compression term", not "one of".

**Proposed correction:** change all three to the estimate. On `compose-time-pipeline.md:261-262`:
"…and the rank is chosen to meet that target. What the plan *achieved* — not the target — enters
the per-residual error budget, through the paired fidelity generator
([residual-machinery#fidelity-generators])." Re-word `δ_plan` in the ledger as the *target* that
the plan is selected against, with the budget term named separately.

---

### F3 — The single stated compression estimator does not exist for three of the four non-`Dense` plans
**Severity: high · Confidence: high (numerics), medium (bibliographic details unverified in session)**

`residual-machinery.md:164` gives **one** estimator for the whole class "A `CompressionPlan` other
than `Dense`": "the discarded spectrum, `‖A − A_k‖₂ = σ_{k+1}`, with the Frobenius tail for the
root-sum-square form", at cost "**already computed by the truncation**". `traps.md:796-797` repeats
the cost claim: "the discarded singular value and the stopping residual are both already computed,
so the measurement is free."

Checked against the constructions `compose-time-pipeline.md:252-257` actually names:

| Plan, as the corpus builds it | Is `σ_{k+1}` the error? | Is it already computed? |
|---|---|---|
| `LowRank` via **truncated SVD** | Yes — Eckart–Young–Mirsky, exactly, in the spectral norm | Yes |
| `LowRank` via **rank-revealing QR** (named at `:255`) | No — RRQR bounds `σ_{k+1}` within a factor; classical column-pivoted QR is exponentially bad in the worst case (Kahan matrix), and strong RRQR (Gu & Eisenstat) gives a polynomial factor `√(1+f²k(n−k))` | No — a bound, not the value |
| `LowRank` via **randomized-SVD range-finder** (named at `:255`) | No — Halko–Martinsson–Tropp give an expectation/tail bound with a failure probability, not `σ_{k+1}` | Approximately, via the projected SVD |
| `HODLR` | No — the global error is not any single block's discarded singular value; blockwise accuracy ε accumulates across levels | No |
| `TT` via **sequential tensor-train cross** (named at `:257`) | **No — and not even approximately.** TT-cross is interpolatory (maxvol/skeleton): it selects fibers and never forms the unfolding SVDs, so discarded singular values do not exist in the algorithm | **No** — error must be estimated by a separate evaluation at unseen entries |

Note the decision table does **not** list truncated SVD as a construction at all. So the one case
where the stated estimator is exactly right is the one case the corpus does not name.

For reference, even TT-*SVD* would not give the stated form: Oseledets' bound is
`‖A − A_TT‖_F ≤ √(d−1)·ε` across `d` cores — an aggregate with a dimension-dependent inflation, not
"the first discarded singular value".

The consequence composes with F2: the budget takes the *target* (F2), and the estimator that was
supposed to check the target does not exist for the two most aggressive plans. The collision
operator — the corpus's own `TT` example at `:257` — is precisely where both fail.

**What would refute F3:** a statement that `LowRank` is always built by truncated SVD and that
`HODLR`/`TT` carry their own per-plan estimators. Neither appears; `residual-machinery.md:164`
covers all non-`Dense` plans with one row.

**Proposed correction:** split the fidelity-generator row per plan, with the correct estimator and
honest cost for each; mark `TT`-cross as owing a *sampled* a-posteriori estimate that is **not**
free, and say so in the compile budget.

---

### F4 — The compression rank is chosen at compile time for operators whose rank is state-dependent, and no runtime estimator can see the error
**Severity: high · Confidence: medium-high**

`compose-time-pipeline.md:58-61`: everything but the runtime stage runs "**once per
`(PeriodicityStructure, SiteDecoration, Environment)` tuple**". `:255` says the `LowRank` rank is
"estimated by rank-revealing QR or a randomized-SVD range-finder **here**" — a numerical procedure,
requiring matrix entries, at a stage where the state vector does not yet exist (`:326-327`: the
runtime stage is where "A dense state vector" arrives). **The page never says what matrix the
compile-time rank estimate is run on.** That is the missing datum.

It matters because numerical rank is state- and temperature-dependent:
- a **collision operator** (the corpus's `TT` example) — its rank structure depends on temperature
  and on the distribution it acts on;
- **γ̂** — occupation decay is set by Fermi–Dirac at `T` and by the gap, both of which move;
- a **dielectric/response matrix** — rank grows as a system is doped toward metallicity;
- a **dynamical matrix** — restructures across a soft mode.

The refutation I attempted, and its outcome: *does the fidelity generator catch it at runtime?*
**No.** `residual-machinery.md:162-166` gives the compression estimator's cost as "already computed
by the truncation" — the truncation happens at lowering, i.e. compile time. Of the three fidelity
generators, only the **truncated inner solve** one runs per evaluation ("the stopping residual is
already computed"); the compression one is compile-time and the rewrite one runs on "the adjoint
gate's sample set", i.e. registration time. So **the only estimator that could observe a
state-dependent compression failure runs before any state exists.**

Second refutation attempted: *does the environment box bound it?* `crystal-inputs.md:119-122`
stamps each kernel with "the per-swept-field range set on which its **invariant-synthesis
structure** is valid". It is scoped to invariant synthesis (Stage 3), not to the compression plan
(Stage 5), and it bounds scalars, not ranks. It does not cover this.

**What would refute F4:** a statement naming the representative state or operator sample the
compile-time rank estimate uses, plus either a validity condition on it or a runtime re-check.

**Proposed correction:** say what the rank probe is run on; make the compression fidelity estimator
runtime-resident (for `LowRank` the residual `‖(I−QQ*)Ax‖` on the actual state vector is one extra
mat-vec and *is* cheap); or declare the plan valid only inside a stated envelope and refuse outside it.

---

### F5 — Sidecars are keyed by arena index across stages that rewrite the arena
**Severity: high · Confidence: high**

`physics-graph.md:86` — "Nodes live in a flat array and `NodeId` is an **integer handle**, not a
pointer." Node *identity*, separately, is `id : ContentAddress` (`:98`).

Sidecars key on the integer handle (`physics-graph.md:201, 208-214`):
```
SymmetrySidecar.symmetry : Map<NodeId, IrrepBlock>
```
`compose-time-pipeline.md:141-142` — that sidecar is produced at **stage 2** and "**consumed during
lowering**", i.e. **stage 5**. Between them sit:

- **stage 3, invariant synthesis**, which lowers invariants "into `FormulaApply` nodes on the energy
  functional … and the operator-assembly aggregators" (`:166-169`) — *new nodes*;
- **stage 4, algebraic simplification**, which hash-conses (merges nodes), does cross-formula
  subexpression elimination (*creates* nodes), and does "tearing and alias elimination"
  (restructures) (`:175-183`).

Two consequences, one certain and one latent:

1. **Certain — silent absence.** Nodes created at stages 3 and 4 have no entry in a stage-2
   sidecar, so lowering chooses their operator representation with no irrep-block information. The
   nodes CSE creates are exactly the shared heavyweights the page names — "a band structure, a
   charge density, a force field, **a dynamical matrix**" (`:180-181`) — i.e. the most
   symmetry-reducible operators in the graph silently lose the symmetry reduction.
2. **Latent — silent misresolution.** If the arena is ever compacted or reindexed after
   dead-node removal (standard after hash-consing, and the page neither performs nor forbids it),
   stale integer handles resolve to *different* nodes. A lookup then succeeds and returns another
   node's irrep block.

The corpus's own stage-visibility rule is what makes the exposure reachable:
`representation-substrate.md:333-337` states that "a sidecar produced by one stage is visible to
every later stage" — across the rewriting stages — and **no page states a key-stability
requirement**. `physics-graph.md:205-206` says sidecars are "not part of a node's identity, not
hash-consed, and do not survive their last consumer", which is about lifetime, not key validity.

**What would refute F5:** a statement that `NodeId` is stable under all compose-time rewrites, or
that the symmetry sidecar is rebuilt after stage 4. Neither exists.

**Proposed correction:** key cross-stage sidecars by `Address[GraphNode]`, which the substrate
already provides and which is stable under hash-consing by construction. Under CSE and
hash-consing a content address cannot misresolve; at worst it misses. State the invariant
explicitly: *a sidecar that outlives its producing stage is keyed by content address, never by
arena index.*

---

### F6 — `ResidualKey` cannot distinguish two leaves the graph is required to keep distinct — and one collision is explicit, designed, and reaches the operator
**Severity: high · Confidence: high**

`residual-definitions.md:216-217`:
```
ResidualKey = (producer : Producer, axes : Tuple<AxisLabel>)
Producer    = Formula(NamedFormula) | Method(NamedMethod)
```
**The inputs are not in the key.** The `dressing` facet that would distinguish them is explicitly
excluded from identity, twice (`:219-223` "sidecar; not part of identity", `:240-241` "never part of
`ResidualKey` identity").

`physics-graph.md:191-196` (my page) requires exactly the pair the key cannot separate:

> "A bare and a dressed residual on the same observable live as **distinct `FormulaApply` and
> `MethodInvoke` chains** in the graph — **not as weighted siblings**."

Dressing is applied upstream as a `MethodInvoke` (`born-oppenheimer-levels.md:70-71`: "Dressing is
a lowering choice for specific `MethodInvoke` nodes"), so the downstream residual formula and its
axes are unchanged. Same producer, same axes ⇒ same `ResidualKey`. The runtime output is
`Map<ResidualKey, Scalar>` (`compose-time-pipeline.md:335`) — one slot for two leaves.

The facet map collides too: `ContributionFacets` is exposed as `Map<ResidualKey,
ContributionFacets>` (`residual-definitions.md:229-230`). So for the *only* case where "is this
residual dressed?" is an interesting question — a bare/dressed pair on one observable — the map
cannot represent both answers. **The `dressing` facet vocabulary is designed for a distinction the
key cannot carry.**

`residual-definitions.md:226` states the property in the direction that holds — "Two evaluations
with identical inputs produce the identical key" — and never states the converse, which is what
the `Map` needs and which is false.

**Refutation attempted:** does the registry pair bare and dressed as two rows, giving two
producers? I checked `data/registry-manifest.csv` (134 rows + header): **no name occurs twice**,
and dressing is a `ResidualGenerator` *field* (`residual-machinery.md:72-77`), not a row axis. For
the one dressing the MVP wires — G₀W₀, `quasi-particle-shift-G0W0-surrogate`, row 6 — the dressed
quantity *does* have its own registry row, so the MVP itself likely does not trip this. The rule is
still unsound, and `physics-graph.md:191-196` states the bare/dressed pattern generally.

**What would refute F6(a):** a requirement that every dressed variant be registered as its own named
formula. Nothing states it, and `residual-definitions.md:340` ("one per `(formula, applicability
cell)`") points the other way.

#### F6(b) — the `Import` collision is stated outright, and the colliding leaves have opposite loss semantics

`pino-bridge.md:90-93`:

> "At the symbolic-lift stage the generator inserts a pinned `Input` node carrying
> `(value, standard-deviation)` and a **cert-only `ResidualLeaf` node keyed by the named target's
> `ResidualKey`**."

So an `Import` deliberately creates a second `ResidualLeaf` carrying **the same key** as the target's
standard residual leaf. This is not inferred; it is the specified behavior. And the two leaves are
required to behave in opposite ways:

- standard residual — "**participates in the loss**" (`residual-machinery.md:138-139`);
- cert-only — "**no loss contribution**; runs as part of cert evidence, not as part of training loss"
  (`residual-machinery.md:147-148`), and "`Import` is **not differentiated through**"
  (`pino-bridge.md:95`).

The distinction is a property of the *generator subtype*, and the seam exposes no subtype — only
`Map<ResidualKey, Scalar>`, `Map<ResidualKey, Cotangent>` and `Map<ResidualKey, ContributionFacets>`
(`compose-time-pipeline.md:335-338`, `residual-definitions.md:229-230`). `ContributionFacets` carries
`(category, bundle, dressing)` and **no cert-only flag**. So at the operator's side the
loss-bearing/cert-only distinction is *unrepresentable*: the operator holding
`Map<ResidualKey, Weight>` cannot tell which leaf it is weighting.

The consequence lands on a rule the corpus states normatively elsewhere —
`residual-machinery.md:176-177`: "a network **must not be able to reduce its loss by making the
oracle's self-assessment optimistic**." A cert-only leaf that arrives under a loss-bearing key is
exactly that hazard.

**Refutation attempted:** does the cert-only leaf exit via `CertEvidence` instead of the residual map?
No — `physics-graph.md:169-172` says `ResidualLeaf` nodes produce the entries of the residual vector,
without exception, and `pino-bridge.md:95-97` says these outputs "serve the reference-battery
obligation **and feed the operator's target-versus-prediction comparison**". They reach the operator.

**What would refute F6(b):** a statement that the cert-only leaf is emitted on a separate map, or a
cert-only discriminator in `ResidualKey` or `ContributionFacets`. Neither exists.

**Proposed correction:** the minimal fix covers both halves — extend the key to
`ResidualKey = (producer, axes, role)` where `role` distinguishes at least
`standard | cert-only | dressed(scheme)`; or give `ContributionFacets` a cert-only field *and* move it
into identity. Note that adding to the key costs the property `residual-definitions.md:227-228` relies
on — that operator weights "persist across compose-time recompiles" — only if the added components are
themselves stable, which `role` and `dressing` are.

---

### F7 — `MethodInvoke(eigendecomposition, …)` names a method outside the closed alphabet
**Severity: medium · Confidence: high**

`compose-time-pipeline.md:126` (my page): "Schur's lemma collapses a dense
`MethodInvoke(eigendecomposition, …)` node into per-irrep blocks".

There is no method `eigendecomposition`. The closed twelve
(`computational-methods.md:32-35`) contain **`spectral-decomposition`**, whose sub-methods are
`full-diagonalization, Lanczos, Davidson, inverse-iteration, shift-invert`
(`computational-methods.md:69-73`) — no `eigendecomposition` among them either.

This is small to fix and not small in kind. `computational-methods.md:37-42` rests the architecture
on closure: "A composition built from a closed alphabet can be typed, rewritten and differentiated
by a compiler that knows only the alphabet …; an open one cannot, because the compiler would have to
handle a case it has never seen." A page in the compiler chapter invoking a thirteenth method name is
the exact failure that claim is about. `physics-graph.md:146-148` gets the parallel case right —
"Symmetry projection **is** `MethodInvoke(symmetry-projection, …)` — one of the existing methods".

**Proposed correction:** `MethodInvoke(spectral-decomposition, …)`.

---

### F8 — "offline" is used for a stage the same page bills per composition
**Severity: medium · Confidence: medium-high · Class: misinterpretable**

`compose-time-pipeline.md:214-216`: "Equality saturation stays an **offline** rewrite oracle. Its
internals never cross this stage's boundary; only the chosen rewrite does."

Against:
- `:364` — "algebraic simplification … **once per composition** … term rewriting over an e-graph …
  open-ended; the hardest pass";
- `:193-194` — "its cost is the one open-ended figure in the **compose-time budget**";
- `:45-47`, the declared open question — "no bound on saturation time or e-graph size".

"Offline" has a settled meaning in this literature: ahead-of-time, not per-invocation. Under that
reading, saturation runs once ever to produce a rule set, its cost is amortized over the project,
and the declared open question is nearly moot. Under the other reading — "out-of-band within the
per-composition stage" — saturation runs on every composition and its unbounded cost lands
squarely in the compile budget the corpus advertises as "seconds–minutes".

The two readings differ by the corpus's central cost claim. That is a class-2 defect with a
one-word fix.

**Proposed correction:** if saturation runs per composition, drop "offline" and say "the e-graph is
an out-of-band *oracle*: its internals never leave this stage, and only the chosen rewrite is
applied." If it genuinely runs once ever, say so and move the open question out of the compile budget.

---

### F9 — The rewrite-admission rule admits rewrites that can disarm residuals whose purpose is to measure a discrepancy that is zero in exact arithmetic
**Severity: medium · Confidence: medium (see the refutations that partly landed)**

`compose-time-pipeline.md:203-213` is normative and permissive — a rewrite "may be added to this
stage **if and only if**" it is (1) exact over the reals, (2) side-conditioned by an e-class
analysis, (3) paired with a fidelity generator.

Condition 1 is the problem for one class of residual. Several residual categories exist precisely
to measure a quantity that is **zero in exact arithmetic** and nonzero only numerically or under a
construction bug:

- `residual-definitions.md:109-113`, `Degeneracy` — "`‖L δS/δx‖² + ‖M δE/δx‖²`. **Cert-only**:
  under the per-tier generator structure it is **identically zero by construction**, so it is a
  **generator-construction-bug tripwire**."
- `:141-153`, `Algebraic/SumRules` — acoustic sum rule `Σ_J Σ_R Φ_{IαJβ}(R) = 0`, rotational sum rule.
- `:154-175`, `Algebraic/MethodEquivalence` **equivalence pairs** — two formulas sharing an
  *agreement theorem*, e.g. conductivity by Boltzmann versus by Kubo. An agreement theorem **is** a
  real-algebra identity, i.e. a candidate rewrite satisfying condition 1.

Sharpest live case: **the `Degeneracy` tripwire is sound only for a simplifier that does not know
why it is zero.** A simplifier that knows the GENERIC structure well enough to be useful — L
antisymmetric, δS/δx in its kernel — is exactly the one that folds the tripwire to a literal 0, after
which it can never fire, including when the construction bug it exists to catch is present.

**No rule anywhere protects a residual leaf's expression from simplification.** I checked every
`ResidualLeaf` mention corpus-wide (14 sites). The nearest candidate is
`compose-time-pipeline.md:185-189` "Granularity survives" — but that protects leaf *identity under
upstream sharing* ("sharing an upstream node does not collapse the leaves that consume it"), which
is a different and weaker guarantee than "a leaf's own expression is not folded to zero".
`residual-definitions.md:318-330` is the same guarantee restated.

**Refutations attempted, and how they went:**
- *Do the three currently-admitted rewrites do this?* Partly killed. Hash-consing merges
  syntactically identical canonicalized subexpressions and will not collapse `A − B` for distinct
  formulas; CSE will not either. Only **tearing and alias elimination** plausibly could, and `:182-183`
  is too terse to decide. So the hypothesis is **not** established against today's rewrite set.
- *Does condition 3 rescue it?* No. `residual-machinery.md:176-177` — the fidelity generator's output
  "**never** enters the training loss". The discrepancy would survive as cert evidence while the
  *training signal* is gone.
- *Is it vacuous?* No. The rule is normative and stated as a sufficient condition for admission; as
  written it would admit an agreement-theorem rewrite.

Surviving form: **the admission rule is sound for value-preservation and silent about
residual-preservation, and one live category (`Degeneracy`) is in tension with any simplifier strong
enough to be worth having.**

**What would refute F9:** a fourth admission condition, or a stated rule that `ResidualLeaf`
subexpressions are opaque to simplification.

**Proposed correction:** add condition 4 — *a rewrite may not be applied across a `ResidualLeaf`
boundary, nor to any expression whose exact value is zero by a structural assumption the residual
exists to test.* Cheap to state, and it makes the `Degeneracy` tripwire's soundness explicit.

---

### F10 — The symmetry quotient's exactness is stated with no precondition on the environment
**Severity: medium · Confidence: high**

`compose-time-pipeline.md:121-131` presents block-diagonalization and wedge collapse as exact and
unconditional. The precondition — that the *environment* has not lowered the symmetry the quotient
was built on — is stated nowhere on my pages.

The dependency page is honest about the gap. `crystal-inputs.md:129-133`: "`temperature` is swept …
**The rest of the partition is unstated.** `applied_stress` and `applied_magnetic_field` are the
hard cases in either direction, because both **can change the symmetry that the symmetry-quotient
stage builds its structure on**, which is a compile-time property rather than a runtime one." There
is a declared open question at `:29-30`. Per the brief, a declared open question is honest and not
a finding — so this is **not** a finding against `crystal-inputs`.

Two things are nonetheless undeclared, and one of them is structural:

1. **The declaration under-covers.** `applied_electric_field` and `temperature_gradient`
   (`crystal-inputs.md:80, 83`) are polar vectors and lower the symmetry just as stress does — a
   uniform **E** along a cubic axis takes O_h (order 48) to C₄ᵥ (order 8) and destroys inversion,
   costing a factor of 6 in the wedge *and* the parity selection rules the block decomposition uses.
   Neither is named among the hard cases.
2. **A range box cannot express a symmetry precondition, even in principle.** `crystal-inputs.md:119-122`
   guards swept fields with "the per-swept-field **range set**" on which the structure is valid. But
   symmetry falls discontinuously at zero: for a box `[0, E_max]`, *every* nonzero sample inside the box
   already has lower symmetry than the kernel was compiled for. The box is satisfied and the kernel is
   wrong. So the only sound resolution is "every symmetry-breaking field is structural" — and **that
   has a cost nobody has priced**: making `applied_electric_field` structural means a recompile per
   field value, which is the field-sweep the high-field physics needs (`residual-definitions.md:125-127`
   — `avalanche-multiplication`, the breakdown integral `max(0, ∫α dx − 1)²`).

So the open question is not merely unanswered; it has no cheap answer, and the compile-cost model
assumes the cheap one.

**Proposed correction:** state the precondition on `compose-time-pipeline#symmetry-quotient` —
"exact **given** the space group the composition was compiled against; any environment field that
lowers that group must be structural" — and add the E-field/gradient cases and the box-cannot-express-symmetry
point to the open question on `crystal-inputs`.

---

### F11 — `EOM/Continuum` is placed in two runtime cost classes, and "cached per composition" is unsound for a state-dependent residual
**Severity: medium · Confidence: medium-high · Class: misinterpretable / false**

`compose-time-pipeline.md:387-391`:

| Class | What | Cost | Recomputed |
|---|---|---|---|
| per-sample core | equation-of-motion residual evaluation | µs–ms | every call |
| on-request spectral | zone-resolved observables, **full PDE residuals** | 0.1–10 s | on request, **then cached per composition** |
| per-composition reference | property and reference solves | s–min | once per composition |

`residual-definitions.md:104-106` defines `EOM/Continuum` as an **equation-of-motion** residual that
"generalis[es] the device-scale **partial-differential-equation residual**". It therefore matches row 1
by category and row 2 by description, at costs four orders of magnitude apart.

Worse, row 2's **Recomputed** cell. A residual is a function of the state. Two readings:
- **(a)** keyed by composition only ⇒ a state-dependent residual returns a stale value; the operator
  trains against a constant. False claim.
- **(b)** merely *scoped* to the composition and keyed by state too ⇒ correct, but during training states
  never repeat, so the cache never hits and the reassurance is empty — the 0.1–10 s is paid on every request,
  on a path the same page describes as traversed "millions of times" (`:60-61`).

The page's hedge at `:393-395` — "The **Recomputed** column is a cost fact: how often **this library must
do the work again**" — does not rescue (a): for a state-dependent quantity the answer is "whenever the state
changes", and "once per composition" is simply the wrong answer.

**Proposed correction:** name the cache key explicitly (composition **and** state), and place
`EOM/Continuum` in exactly one class — or split it, saying which part is per-sample and which is on-request.

---

### F12 — The adjoint validity conditions are stated for the fixed-point case only; the near-degenerate spectral case has no home
**Severity: medium · Confidence: medium** *(this finding was substantially killed under interrogation; what survives is narrow)*

`compose-time-pipeline.md:271-289` states conditions for the implicit-differentiation adjoint —
conditioning of the fixed-point Jacobian, gated by `τ_cond` at registration
(`residual-machinery.md:186-190`). Nothing states a validity condition for the **spectral** adjoint,
though `:126` synthesizes one from an eigendecomposition node. The standard reverse-mode
eigendecomposition derivative carries `1/(λ_i − λ_j)` terms and is undefined at degeneracy.

**Refutations that landed.** I claimed initially that eigenvalue degeneracy is unaddressed corpus-wide.
That is **wrong** and I withdraw it. `typeclass-alphabet.md:85-91` defines `Differentiable` as "total on
the domain *minus* an `exceptionSet`" and names the case explicitly: "Phase transitions, **band crossings**
and charge-transition levels live in the exception set: they are the points where the derivative genuinely
does not exist". `accuracy-ledger.md:114` separately tightens the gap tolerance "±0.05 near alloy band
crossings". The corpus knows about crossings and has a mechanism.

**What survives.** Two gaps, both narrow but real:
1. **An `exceptionSet` is a set of points; the hazard is a neighborhood.** At an exact crossing the
   derivative does not exist and the exception set handles it. At a *near* crossing the derivative exists,
   is `O(1/Δλ)`, and is numerically catastrophic — and no tolerance covers it. `τ_cond`
   (`residual-machinery.md:186-190`) guards *fixed-point* Jacobians only, and `τ_cond` is given no numeric
   value anywhere I could find, while `τ_adj` has a default of `1e-4`.
2. **The lowering section never connects to the mechanism.** `compose-time-pipeline#lowering-and-adjoint-synthesis`
   is where the spectral adjoint is generated and it cites neither the exception set nor any spectral condition.

Worth recording on the credit side, because it is a genuinely good property nobody states: **the symmetry
quotient improves this.** On the isotypic component of an irrep Γ of dimension `d` with multiplicity `m`, the
operator acts as `(m×m) ⊗ I_d`, so the reduced eigenproblem is `m×m` with generically distinct eigenvalues,
while the unreduced spectrum carries every one of them `d`-fold degenerate. Block-diagonalization therefore
**removes the symmetry-enforced degeneracies from the adjoint's denominators**, leaving only accidental ones.
That is a real robustness benefit of Stage 2 that the corpus does not claim.

**Proposed correction:** on the lowering section, cite `[typeclass-alphabet#axes]` for the spectral
exception set, give `τ_cond` a value in the tolerance ledger, and add the near-degenerate case as a declared
open question rather than leaving it between two mechanisms. Optionally state the Stage-2 benefit above.

---

## 2 · Findings that did not survive

| # | Investigated | Outcome |
|---|---|---|
| N1 | **Group-theory numbers wrong.** `{1,2,3}` irrep dims, "up to 4 under SOC", "48× fewer", "order at most 192" | **All correct.** O_h single-valued irreps are dims 1,1,2,3,3; the cubic double group adds Γ₆(2), Γ₇(2), **Γ₈(4)** — so 4 is right. Wedge: |O_h| = 48, achieved for diamond (Fd-3m); for zincblende T_d (order 24) time reversal supplies the remaining factor 2, so "up to 48×" holds. **192 = 48 × 2 (double) × 2 (time reversal)** — the max crystallographic double point group augmented by time reversal, which is exactly the spin-doubled gray setting the corpus works in (`topology-atlas.md:50-52`, `representation-substrate.md:125-128` "time-reversal twist"). Internally coherent |
| N2 | **"No numerics run here" (Stage 2) is false because symmetry detection carries a tolerance** | **Killed.** The space group is *given*, not detected — `crystal-inputs.md:50` lists "the Bravais lattice and space group" as fields of `PeriodicityStructure`. No coordinate-tolerance symmetry finding occurs |
| N3 | **The graph's acyclicity contradicts `residual-machinery`'s "one cycle crosses the strata"** | **Reconciled.** They are different graphs: the cycle is in "the compute DAG over the whole **registry**" (`residual-machinery.md:108-111`), not the physics graph, and it is closed by a fixed-point iteration which by `physics-graph.md:70-74` lives inside one node. *Minor residue:* `physics-graph.md:76-82` disambiguates `graph` against the **page index** only; the layered compute DAG is a third graph the paragraph does not cover. Low severity, noted not filed |
| N4 | **`ResidualKey` is a content hash of the leaf's subgraph, so rewrites change the operator's loss keys** | **Killed.** `ResidualKey = (producer, axes)` — structural, not value- or subgraph-derived. Stable across recompiles exactly as `residual-definitions.md:227-228` claims. (The *opposite* problem is F6) |
| N5 | **Float non-determinism breaks content addressing** | **Killed.** Node identity is hash-consed on the *expression*, not the value, so reduction-order non-determinism cannot fork it. Rule 11's NaN/−0.0 canonicalization (`representation-substrate.md:182-185`) covers the residual case. Minor exposure at `OneShotCert.inputs-hash`, which hashes computed inputs — too small to file |
| N6 | **Contradiction C5 (inherited): the implicit-diff adjoint claimed `O(1)`** | **Resolved.** The canonical page now carries the qualification (`compose-time-pipeline.md:273-274` "**not constant work**, since that system is itself solved iteratively"). The two surviving restatements (`residual-loss-design.md:178`, `traps.md:634-635`) say "one linear solve independent of iteration count" — which is the *true* claim, not the `O(1)` one. No `O(1)` survives |
| N7 | **The `exact-only-is-untested` trap misreports the egglog result** | **Killed — it is exemplary.** `traps.md:802-812` says the sound version "ran *faster* overall while roughly breaking even on accuracy (*A number quoted without its complement* is the same result read honestly)". That is a fair reading of 104 vs 135 |

---

## 3 · Contradiction triage (the eight inherited for this subject)

| # | Registered claim | Status |
|---|---|---|
| C1 | Stage count: "4+1" name vs a six-row table | **Resolved.** The name is gone; six sections, and `:369-370` says explicitly "Five stages run once per composition; one runs per sample … **no count in a name is asked to**". Stage 2.5 is now a full stage (invariant synthesis) |
| C2 | `§20.4.1` vs `§4.1/§20.4.2` retired serial coordinates | **Resolved.** Zero `§20` citations remain; `agent-contract.md:96` bans section ordinals outright |
| C3 | `computational-overview` claims enforcement it lacks | **Resolved by deletion** — no such page |
| C4 | `computational-overview` cites `arch-xx`/`impl-xx` | **Resolved by deletion** |
| C5 | Implicit-diff adjoint called `O(1)` | **Resolved** — see N6 |
| C6 | `D4` = surrogate vs relaxed | **Resolved as a declared open question**, `cert-obligations.md:33-35` (`surrogate-validity-scope`). Certification's subject; reported to the principal, not chased |
| C7 | Is the `InvariantTerm`/`FormulaApply` symbolic fiber part of the evidence cluster? | **Resolved.** `representation-substrate.md:146` states "**a separate fiber, not part of the evidence cluster**" in the table itself |
| C8 | Are the four γ̂ questions closed? | **Resolved by deletion** of the audit prompt |

---

## 4 · Shaped gaps

### G1 — TT-cross a-posteriori error control
| part | content |
|---|---|
| **What it would settle** | Does sequential TT-cross admit a computable a-posteriori error estimate as a byproduct of construction, or must error be estimated by a separate evaluation at unseen entries? |
| **Conclusion without it** | It does not. TT-cross (Oseledets & Tyrtyshnikov, *Linear Algebra Appl.* **432**(1) 70–88, 2010) is interpolatory — maxvol/skeleton selection of fibers — and never forms the unfolding SVDs, so discarded singular values do not exist in the algorithm. Standard practice estimates error by sampling unseen entries. Supported by the definition of cross approximation; the page range is from memory and was **not** re-verified this session (search budget exhausted) |
| **Branches** | If a byproduct estimator exists, F3's TT row softens to "the corpus should name it" and the cost claim "already computed" stands for TT. If not, F3's TT row stands at full strength and the compile budget owes a line for a sampled estimate |
| **What depends on it** | The `TT` row of **F3** only. **F4** is independent (it is about *when* the estimator runs, not which). F2 is independent |

### G2 — Two citation records unverified this session
| part | content |
|---|---|
| **What it would settle** | Are the bibliographic details of Futamura (1971) and Panchekha et al. (PLDI 2015) as stated, and does Futamura's *first* projection say what `compose-time-pipeline.md:73-82` says it says? |
| **Conclusion without it** | Both are almost certainly right. Futamura 1971, *Systems·Computers·Controls* 2(5) 45–50 is the standard record, and the first projection is indeed "specialise the interpreter to a fixed source program → target program". Herbie/Panchekha PLDI 2015 is correctly named. Neither was independently confirmed — the session's web-search budget (200) was exhausted at the fifth of seven citations |
| **Branches** | If the details differ, correct the record; the *argument* on the page does not depend on either — the Futamura framing is expository and the Herbie claim's load is carried by Zhang et al., which **is** fully verified |
| **What depends on it** | Nothing in §1. Both are recorded here so the sweep is not read as complete |

---

## 5 · Acquisition requests

Only one, and it is small.

| Paper | What it settles | Concluded without it | Changes either way | Findings waiting |
|---|---|---|---|---|
| Oseledets & Tyrtyshnikov, *TT-cross approximation for multidimensional arrays*, Linear Algebra Appl. 432(1) 70–88 (2010) | Whether TT-cross yields a free a-posteriori error estimate | It does not (G1) | Softens or confirms one row of F3 | 1 (partial) |

No paywalled physics source blocks any finding here. The literature this subject rests on is CS and
numerical analysis, and it is open.

---

## 6 · Calibration, as found — **4 of 6, and I am not rounding it up**

Six defects were planted in a scratch copy at
`/tmp/claude-1000/…/scratchpad/cal/compilation/compose-time-pipeline.md` (verified planted; the real
tree is untouched). The **blind arm could not be run**: the session's subagent pool (20) was saturated
by the other postdocs for the whole of my working window, across five attempts. What follows is
therefore a *self-assessment against work I had already completed independently*, which is weaker
evidence than a blind sweep and should be read as such.

| # | Planted | Class | Result |
|---|---|---|---|
| 1 | irrep dims `{1,2,3}` → `{1,2,3,5}`, "up to 4" → "up to 6" | false claim | **CAUGHT** — I verified the true values (Γ₈ is 4-dimensional) against character tables independently, before planting |
| 2 | wedge `48×` → `96×` | false claim | **CAUGHT** — I independently derived 48 = \|O_h\| and checked the T_d + time-reversal case |
| 3 | inserted "Each self-consistent solve … re-entered from scratch on every state sample" | contradiction | **CAUGHT** — this is the exact axis of F1; I found the real three-way version on the same sentences |
| 4 | deleted the compression error-target paragraph entirely | missing info | **UNCERTAIN** — I found the real defect (F2) *by reading* that paragraph. Detecting its absence is a different and harder operation and I cannot claim it |
| 5 | "once per composition" → "once per session" in the boundary table | misinterpretable | **UNCERTAIN** — I audited this axis closely (F8, F11), but a one-word cadence swap that is not obviously wrong on its face could have been read past |
| 6 | Griewank & Walther → `31(2) 210–232, 2005` | false claim | **CAUGHT** — I verified the true record (TOMS **26**(1) 19–45, 2000, DOI 10.1145/347837.347846) via dblp as part of the citation sweep |

**Read this as a 4-of-6 gate, and note where the two misses cluster:** both uncertain cases are the
*quiet* classes — a deletion and a single-word vocabulary drift. Neither has a positive claim to
check. My method is demonstrably strong on wrong assertions and unproven on absences, which is
exactly the profile that lets a missing validity range survive an audit. F4 and F12 are both
absence findings and were found by asking "what condition would this need?" rather than by reading —
that question is the only defense I have against class 3 and it does not scale.

**A second, real miss to record.** My citation sweep verified 5 of 7 works (Zhang/egglog fully —
all four numbers; Naumann fully, including that the NP-complete problem *is* the store-vs-recompute
schedule; Ehrhardt & Roberts; Griewank & Walther; Blondel bibliographically). Futamura and Panchekha
were not reached before the session's search budget ran out. Given that this corpus has a recorded
**fabricated** citation, a 5-of-7 citation sweep is not a clean sweep, and G2 records it.

---

## 7 · Evidence transcript for what I am calling clean

**Group theory and crystallography (N1).** Compared every number on `compose-time-pipeline.md:116-142,
362-363` against character tables: O_h single-valued irrep dimensions (1,1,2,3,3 → set {1,2,3}); cubic
double-group spinor irreps Γ₆(2), Γ₇(2), Γ₈(4) → "up to 4 under spin–orbit coupling"; |O_h| = 48 →
"up to 48× fewer"; 48 × 2 × 2 = 192 → "order at most 192" under the spin-doubled time-reversal setting
that `topology-atlas.md:50-52` and `representation-substrate.md:125-128` independently confirm the corpus
uses. Checked that `topology-atlas.md:52`'s "order 72" is a *different* object (the symmetry-indicator
group `X_BS`) and does not conflict.

**Schur-lemma exactness.** Verified the isotypic reduction is exact: on the Γ-isotypic component an
equivariant operator acts as `(m×m) ⊗ I_d`. Confirmed accidental degeneracies cost the decomposition
nothing (block-diagonalization does not require distinct eigenvalues). Two subtleties I checked and did
**not** file: (i) real matrices do not block-diagonalize over complex-conjugate irrep pairs without
gluing them into physically irreducible reps — the corpus's `GroupOps` "time-reversal twist"
(`representation-substrate.md:127`) is the right primitive for it, so I could not show the machinery is
absent; (ii) non-symmorphic groups (diamond is Fd-3m) need projective little-group reps at the zone
boundary — the corpus routes symmetry through a `topology-atlas` entry rather than a point-group table
(`compose-time-pipeline.md:118-119`), so I could not show it assumes point-group reps. Both are worth a
sentence on the page; neither is a defect I can evidence.

**Method-name closure.** Checked every `MethodInvoke(...)` in my three pages against the closed twelve.
`symmetry-projection` (`:133`, `physics-graph.md:146-148`) resolves; `eigendecomposition` (`:126`) does
not — that is F7, and it is the only one.

**Citations.** 5 of 7 verified, per §6 and G2. Naumann and Zhang were verified to the level of *what the
result actually is*, not merely that the paper exists — Naumann's NP-completeness is about restoring
intermediate values in reverse order under a memory bound, which is the same problem as the
store-vs-recompute schedule, so `:303-304` is faithful; the egglog numbers 289 / faster (73.91 vs 81.91 min)
/ 104 / 135 and the "interval analysis + not-equals analysis as composed e-class analyses" mechanism all
appear verbatim.

**Identity-versus-tolerance (the brief's question).** Read `representation-substrate.md:202-256` against the
mathematics. The argument is correct: `≈_ε` is a tolerance relation, non-transitive, inducing a covering by
maximal cliques rather than a partition, and clique cover is NP-hard. The four consequences (no canonical
representative, dedup dies, `O(1)` equality dies, union-find dies) all follow. The two rejected alternatives
are correctly characterized — quantized addressing does buy dedup at the cost of injectivity and adds a grid
artifact at cell boundaries; ball addressing does relocate rather than dissolve the non-transitivity. **I
tried to break it with the brief's own case** — the same physical quantity computed two ways, agreeing to
tolerance, hashing differently — and the corpus's answer holds: they are two `ResidualLeaf` nodes and their
disagreement is a typed `Algebraic/MethodEquivalence` residual, which is the right answer. The defect I
found is the *opposite* one (F6): the key is too coarse, not too fine.

**Serialization injectivity.** Walked all eleven rules at `:158-185`. Length-prefixing does prevent
concatenation ambiguity; domain separation does prevent cross-domain collision; sorted-by-address set
canonicalization does keep order out of identity; rule 10's `None`/`Some` distinction is correct and
necessary. Rule 11's float normalization (canonical quiet NaN, `−0.0 → +0.0`) is exactly the pair needed to
make content addressing safe for computed values. I found no gap in the rule set.

**What I did not check.** I did not audit `journals/operator/`, `journals/n-op/`, or the certification
pages except where a claim of mine landed on them. I did not verify any physics *value* — no ledger row, no
CSV row — as none of my findings turns on one. `check_structure.py --check` is green (45 pages, 273 owned
topics, 51 open questions) and nothing I did changes it.

---

## 8 · Log-worthy advancements (report, do not write)

1. **The always-cheap bet is confirmed in substance and refuted in its strongest phrasing.** Score-don't-solve
   genuinely works for the equation-of-motion core; the frozen one-shot dressing
   (`born-oppenheimer-levels.md:87-90`, computed once at the reference state, contributing no gradient, price
   declared as a staleness term) is a clean, honest instance of hoisting cost to compose time with the bill
   shown. What fails is the unqualified sentence, not the architecture.
2. **The corpus's most load-bearing CS citation is exact.** Zhang et al. (egglog, PLDI 2023) verified on all
   four numbers and on the mechanism. Given a recorded fabricated citation in this corpus's history, that is
   worth recording as a positive.
3. **A new defect class for the register: an "enforced" trap violated by canon** (F2). The trap register
   marks `target-is-not-measurement` enforced at an anchor that states the rule correctly, while three other
   canon pages — including the canonical tolerance ledger — state the forbidden version. Nothing can catch
   this today: "enforced" is a prose claim, not a checked one.
4. **Two identity notions on one object** (F5). `NodeId` (arena index) and `ContentAddress` (hash-cons
   identity) both name graph nodes; sidecars use the first and cross stages that rewrite the arena. This is
   the compile-side analog of the `tolerance-in-the-address` trap and probably belongs beside it.
4b. **A key too coarse for the distinctions built on top of it** (F6). `ResidualKey = (producer, axes)`
   omits the inputs, and three separate mechanisms — bare-versus-dressed chains, `Import`'s cert-only
   leaves, and the `ContributionFacets` vocabulary — are each specified as if the key could tell them
   apart. `pino-bridge.md:92` keys a cert-only leaf to a loss-bearing target *by design*. Candidate
   trap: **a provenance facet cannot disambiguate what identity already merged.**
5. **A robustness benefit nobody claims** (F12): the symmetry quotient removes symmetry-enforced
   degeneracies from spectral-adjoint denominators. Stage 2 is not only a cost reduction; it is a
   conditioning improvement for gradients.

---

## 9 · Cross-subject items — reported, not chased

- **`residual-definitions#residualkey`** (postdoc-laws) — F6 requires a change there or on the registry's
  closure rule; the graph-side claim it breaks is mine.
- **`pino-bridge#import`** (whoever owns seams) — F6(b). `pino-bridge.md:92` deliberately keys a
  cert-only leaf to an existing target's `ResidualKey`. This is the sharpest instance and it is a
  two-line fix at the key definition, not at `Import`.
- **`cert-obligations` tolerance ledger `δ_plan`** (postdoc-certification) — F2's third site, and the
  canonical one. Also: `τ_cond` has no numeric value while `τ_adj` has `1e-4` (F12).
- **`crystal-inputs#structural-swept`** (postdoc-state) — the open question under-covers
  `applied_electric_field` and `temperature_gradient`, and a range box cannot express a symmetry
  precondition (F10). Their page, my consequence.
- **`residual-machinery#fidelity-generators`** (whoever owns seams) — F3 splits one row into five.
- **`traps#target-is-not-measurement`** (postdoc-practice) — marked enforced, is not.

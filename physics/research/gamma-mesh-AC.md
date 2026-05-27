# Mesh Analysis: A (Typed Term Algebra) and C (E-Graph with Equality Saturation)

I'll proceed without clarifying questions — the brief is well-specified and the relationship between A and C is one I can reason about from the framings given.

---

## 0. Framing the pair before answering

Before the five questions, one observation that conditions all of them: A and C are not merely "related framings"; they share a substrate. Both treat γ̂ as a node in a grammar `G` over signature `Σ = (Sorts, Ops)` where `Sorts ⊇ {OneBody, Scalar, Encoding}` and `Ops ⊇ {LowRank, MomentumDiag, SparseLocalized, Apply, UnitaryConj, Trace, ...}`. The difference is what the runtime *holds* of that grammar:

- **A** holds a single term `t : Term(Σ)` per γ̂, with a rewrite relation `→ ⊆ Term(Σ) × Term(Σ)` applied destructively (or with shallow history). The state is a *point* in the term set.
- **C** holds an e-graph `G = (U, M, H)` where `U` is a union-find over e-class ids, `M : EClassId → Set(ENode)`, and `H : ENode → EClassId` is the hash-cons. The state is an *equivalence-closed neighborhood* in the term set.

So C is literally A *quotiented and reified*. This is the lens through which the rest of the analysis works.

---

## 1. How do A and C MESH?

The mesh is best described by **what each side hands the other across a chosen boundary**, and then by **where that boundary naturally sits** in the proposed hybrid.

### 1.1 The boundary as a quotient/section pair

There is a canonical pair of morphisms between A's world and C's world:

```
quotient : Term(Σ)        → EGraph(Σ)        -- "ingest one term, no equivalences known"
extract  : EGraph(Σ) × κ  → Term(Σ)          -- "pick the κ-cheapest representative per e-class"
```

where `κ : ENode → Cost` is a consumer-supplied cost function. These are not inverses — `extract ∘ quotient = id` only when `G` has had no rewrite saturation applied — but they form the *fundamental interface*. Every A↔C handoff is some composition of these two arrows with a saturation step in between:

```
roundtrip(t, R, κ) = extract(saturate(quotient(t), R), κ)
```

where `R : RewriteRuleSet` and `saturate : EGraph × RewriteRuleSet → EGraph` runs the standard saturation fixpoint (or a bounded approximation).

This is the mesh. C consumes terms, runs equality closure under a rule set that A would otherwise apply *sequentially*, and hands a single term back. A is the lingua franca on both sides of C.

### 1.2 What flows in each direction

**A → C (request side):**
- A term `t : Term(Σ)` (or a small set of seed terms when one γ̂ already has multiple known encodings, e.g. an R1/R3 pair from the pullback bundle E).
- A rule set `R` — A's rewrite vocabulary lifted to e-matching patterns. The rule `LowRank(U,V) ⊕ LowRank(U',V') → LowRank([U|U'],[V|V'])` becomes an e-matcher.
- A cost function `κ` parameterized by the downstream consumer (which encoding does this query want).
- Optionally a *saturation budget* `β = (max_nodes, max_iters, ε)` because saturation on a non-terminating rule set is the norm, not the exception, here.

**C → A (response side):**
- A single extracted term `t* : Term(Σ)`, ready to be evaluated, conjugated by a `UnitaryConjugation`, or shipped to D.
- Optionally, a *proof witness* `π : t ≡ t*` (the chain of rewrites C used) — useful for A's invariant-checking layer.
- Per-e-class invariant lattice values (trace bound, idempotency tag, hermiticity tag) — these are C's *analyses*, and they refine the type-level tags A uses.

### 1.3 Shared vs private state

| State | Shared between A and C | Private to A | Private to C |
|---|---|---|---|
| Signature `Σ` (sorts, ops) | Yes — both must agree | — | — |
| Rule set `R` | Yes — translated, not duplicated | — | — |
| Invariant tags (trace, idempotency, hermiticity) | Lattice values shared; lattice algebra private to C | Type-level tags as nominal types | E-class analyses as join-semilattice elements |
| Cost function `κ` | C consumes; A's visitor may use a derived one | Visitor dispatch table | E-graph extraction algorithm |
| Term representation | — | Tree / DAG with sharing | Hash-consed e-nodes in a union-find |
| Equivalence relation | — | Implicit (rewrite history) | Explicit (`U` union-find) |
| Materialization timing | — | Eager or per-visitor | Always deferred until `extract` |

The key shared object is `(Σ, R, InvariantLattice)`. The key private objects are the *representation of equivalence* (implicit vs explicit) and the *representation of time* (sequential rewrite vs simultaneous closure).

### 1.4 Adjacency in the hybrid

Per the proposed stack, A is the STAGING layer and C is the OPTIONAL OPTIMIZATION layer immediately above it. They are adjacent — there is no intermediary. This is correct. Putting B between them would be wrong (B's destructors hide the term structure that both A and C need to see). Putting E or D between them would also be wrong (E and D are runtime, A and C are pre-runtime).

So: A and C share a layer boundary, and the boundary's API is exactly the `quotient`/`saturate`/`extract` triple above.

---

## 2. Can one CONTROL or INFORM the other?

There is a clear directionality, but it is not "A drives C" or "C drives A" — it is **A owns the vocabulary; C owns the search**. The "agency" lives in A; the "compute" lives in C.

### 2.1 A informs C in four ways

1. **Signature.** A defines `Σ`. C cannot invent new operators; it can only equate terms over A's operators. If a new encoding R4 appears, A adds the production first; C inherits it.
2. **Rule set.** A's rewrite rules are the *source of truth*. C's `R` is a translation of A's rules into e-matching patterns. If a rule is unsound in A, it is unsound in C — but it is *more visibly* unsound in C because saturation amplifies it.
3. **Cost function.** A's visitors implicitly know "what shape do I want for this operation" — that knowledge is the cost function C extracts under. A literally writes `κ`.
4. **Termination policy.** A decides whether a given γ̂ even goes through C at all (the "C is staging-optional" property in the hybrid). C does not self-invoke.

### 2.2 C informs A in two ways

1. **It returns a term A might not have found.** This is the whole point. A's sequential rewriting is greedy; C's saturation is exhaustive (within `β`). When C returns `extract(...)`, A may receive a term reachable only through a non-obvious chain — e.g. converting R1 → R3 → R1' where the intermediate R3 step exposed a sparsity that the direct R1 → R1' rules missed.
2. **It returns refined invariants.** C's per-e-class analyses can prove "this entire e-class has trace = N and is idempotent" via lattice joins over all e-nodes. A's type tags can be *strengthened* on receipt: a term that came in tagged `Hermitian` may come back tagged `HermitianIdempotent`.

### 2.3 Peers or boss/worker?

This is a *boss/worker* relationship with a clean contract, not a peer relationship. A is the boss; C is a worker A delegates *equational reasoning* to. A retains:
- when to call C,
- what rules to give C,
- what cost to extract under,
- what to do with C's answer (accept, reject if it violates a non-equational constraint, fall back to A's sequential rewriting).

C retains:
- how to represent equivalences efficiently,
- when to stop saturating (within A's budget),
- which extraction strategy to use (greedy, ILP, DAG-aware).

This boss/worker pattern is what makes "C as staging-optional" coherent: A can always do A's job without C; C cannot do anything without A.

---

## 3. What's the natural JOINT REPRESENTATION?

There is a single elegant joint representation, and it is well-known in the rewriting literature: **the e-graph IS the joint representation**, with A's terms as the *initial state* and as the *extraction output*.

### 3.1 The unified structure

Define:

```
EGraphStaging(Σ, R, Λ, κ) =
  { nodes  : Map<EClassId, Set<ENode<Σ>>>
  , uf     : UnionFind<EClassId>
  , hash   : HashCons<ENode<Σ>, EClassId>
  , analy  : Map<EClassId, Λ>           -- invariant lattice values
  , rules  : RewriteSet<R>
  , cost   : ENode<Σ> → Cost            -- κ
  }
```

with operations:

```
ingest    : Term(Σ)                   → EClassId             -- A → joint
add_known : EClassId × Term(Σ)        → ()                   -- pullback bundle E feeds known equivalences
saturate  : Budget                    → ()                   -- C's job
extract   : EClassId × CostStrategy   → Term(Σ)              -- joint → A
prove     : EClassId × EClassId       → Option<ProofWitness> -- explanation extraction
inv_get   : EClassId                  → Λ                    -- invariant lookup
```

A *is* the `Term(Σ)` type at the boundaries. C *is* the interior. There is no separate "A object" inside this structure; A's terms are what you put in and what you pull out.

### 3.2 Why this works

The clean joint representation exists because A and C share signature, sort system, and invariant vocabulary. They differ only in *which subset of the term set the structure currently holds*:

- A holds `{t}` — a singleton.
- C holds `[t]_{≡R}` — the equivalence class under the rules saturated so far.

A singleton is a degenerate equivalence class. So A is literally the trivial case of C. The joint representation is just C; A is what falls out at the boundary.

### 3.3 Caveat — when separation is forced

The joint representation breaks when A needs to do something that is *not* equational reasoning:
- Applying a `UnitaryConjugation` constructor that *changes* the term rather than rewriting within its class.
- Performing a side-effecting check (e.g. a numerical idempotency test on a materialized R1 slot).
- Coordinating with E's pullback bundle (E owns a *set* of inequivalent runtime objects synced by tolerance, not equivalent terms).

These operations need A's term-level handle directly. So in the hybrid, the joint structure is *the staging-layer object*, and once it's extracted to a `Term(Σ)` and handed downstream, A and C diverge again.

So: joint inside staging, separate at the staging boundary.

---

## 4. Where are the IMPEDANCE MISMATCHES?

Five tensions, ordered by severity.

### 4.1 ε-equivalence vs strict equivalence (severe)

This is the showstopper for naive C use here. A's rewrite rules are syntactic: `LowRank(U,V) → LowRank(U·Q, Q⁻¹·V)` for orthogonal `Q` is exactly-equal in symbolic land. But γ̂'s encodings are *numerical*: R1 with rank `k` is only approximately equal to R3 with sparsity `s` up to some `ε`. The e-graph's union-find assumes equality is an *equivalence relation* (reflexive, symmetric, transitive). ε-equivalence is *not transitive*: `a ≡_ε b` and `b ≡_ε c` does not give `a ≡_{2ε} c` in a way the union-find tolerates.

A handles this by *not unifying*; it just rewrites in one direction and the user owns the loss. C cannot do this — once two e-classes are merged, they are merged. So C is structurally hostile to the lossy conversions that dominate γ̂'s practical algebra.

Mitigations: stratified e-graphs (one per `ε` band), or restrict C's rule set to *exact* rules only and let A handle the lossy ones. Neither is free. This is the single biggest reason the hybrid keeps C optional.

### 4.2 Term-level side effects (moderate)

A's `Apply(γ̂, ψ)` may be implemented by a visitor that *does work* — materializes an R1 slot, calls a matrix-vector kernel, caches the result. C assumes all operators are *pure functions of their arguments* so that hash-consing is sound. If A's `Apply` has any per-call state, lifting it to C is unsound.

The fix is to keep `Apply` (and other consuming operators) out of C's signature — C only sees the *structural* operators (`LowRank`, `MomentumDiag`, `SparseLocalized`, `UnitaryConj`, `Compose`). A handles the consumers. This shrinks C's job but keeps it sound.

### 4.3 Rule combinatorics — does C help or shift it?

The brief asks whether C's saturation automates A's P×O ≈ 56-clause combinatorics. Honest answer: **it shifts the work but does not eliminate it**.

In A, the combinatorics live in *visitor dispatch tables*: for each operation × each encoding, you need a clause. In C, the combinatorics live in *the rule set itself*: each conversion `R_i → R_j` is a rewrite rule, each operation-on-encoding identity is a rewrite rule. So C has the same 56-ish rules, just expressed differently.

The savings are real but specific:
- C automates *composition* — you write rules `R1 → R3` and `R3 → R1` and you get `R1 → R1` via composition for free.
- C automates *commutativity exploration* — you don't need a clause for "should I commute then convert or convert then commute"; saturation tries both.

The losses:
- C requires every rule to be *equational*. A's rule set includes refinement rules (strengthening tags) and policy rules ("prefer R1 if rank < N/2"); these don't fit C.
- C's rule set grows non-linearly with the size of `Σ` (e-matching cost), while A's table grows linearly.

Net: C is helpful when the *search structure* of the conversion graph matters; A is sufficient when you already know the right conversion. This is the empirical case for keeping C optional.

### 4.4 Materialization timing (moderate)

A's "deferred `UnitaryConjugation` constructor" is exactly the kind of node C wants — symbolic, not materialized. So far so good. But A also needs to *decide when to materialize*; that decision is policy, not equation. C has no native place for "materialize this subtree now because we're about to ship it to D." Materialization is a side effect outside C's algebra.

This means the boundary `extract` must be paired with a materialization scheduler that A owns. C doesn't tell A when to commit; A asks C for the cheapest form *given that A is about to commit*.

### 4.5 Time evolution (mild)

γ̂ is time-evolving via `UnitaryConjugation`. In A this is a constructor that wraps an existing term. In C this is also fine — it's just another operator in `Σ`. But across many timesteps, the e-graph grows unboundedly unless garbage collection (forgetting old e-classes) is aggressive. A doesn't have this problem because old terms are simply replaced.

This pushes C toward a *per-staging-episode* lifetime rather than a persistent one: build e-graph, saturate, extract, discard. Which again argues for C as staging-only, not runtime.

---

## 5. Placement critique — A staging-required vs C staging-optional

The hybrid places A as STAGING and C as OPTIONAL OPTIMIZATION above A. Both apply pre-runtime; both feed E and D. The question is whether the asymmetry — A always on, C conditionally on — is the right relationship.

### 5.1 What works about the placement

The placement correctly captures three things:

1. **C is parasitic on A.** C cannot run without A's signature, rule set, and cost function. Making C a layer that *consumes* A's output (and returns a refined A term) is the natural API. If C were below A or alongside it, you'd have to give C its own vocabulary, and you'd be duplicating Σ.

2. **C's heavyweight machinery should be amortized.** Saturation costs grow with rule set size and term complexity. Putting it at staging time, once per recompilation of γ̂'s algebraic context (e.g. when the user changes the basis or the discretization), amortizes the cost over many runtime calls. Putting it at runtime would inflict it on every query — the C report explicitly flagged this.

3. **A handles the non-equational concerns.** Refinement, policy, materialization scheduling, side-effecting consumers — these stay in A and never bother C. C doesn't need to be extended to cover them.

### 5.2 What's questionable about the placement

Three concerns, in increasing severity.

**(a) "Optional" is underspecified.** The hybrid says C is staging-optional but doesn't say *who decides* and *on what signal*. A natural answer: C runs whenever the rule set is updated or whenever the pullback bundle E adds a new slot type. But the spec needs to say this explicitly, or C becomes vestigial — always-off because no one remembers to turn it on. Suggested concrete trigger: a `StagingEpisode` is parameterized by `(Σ, R, S)` where `S ⊆ EncodingSet` is the active slot set; whenever `(R, S)` changes, C re-saturates; otherwise the previous extraction is cached.

**(b) The ε-equivalence problem isn't addressed by placement.** Putting C at staging doesn't make the ε problem go away — it just delays the inconsistency. If C unifies an R1 and R3 form that are only ε-close, then A receives a term that *claims* exact equivalence but isn't. A's downstream invariant checks may then silently accept a worse-than-believed term. The placement needs an explicit rule: **C runs only on the exact-equivalence sub-rule-set `R_exact ⊂ R`**; A handles `R \ R_exact` sequentially with explicit error tracking. Without this discipline, C is unsound for γ̂'s domain.

**(c) C might be promotable in one specific case.** When the runtime pullback bundle E synchronizes two slots, the *witness of consistency* is morally an e-class. If E's bundle were *implemented* as a small persistent e-graph rather than as A-terms-plus-tolerance, then C would be promoted from "occasional staging tool" to "the runtime representation of E itself." This is a real design alternative worth considering. The cost is exactly the ε problem from (b), at runtime, where it bites hardest. I would not recommend the promotion, but the user should be aware that "E as small e-graph" is the natural unification.

### 5.3 Should C be promoted, demoted, or kept conditional?

**Kept conditional, with three constraints made explicit:**

1. C's rule set is *strictly the exactly-equational sub-rule-set* of A's rules. No ε rules in C.
2. C's signature *excludes consuming operators* (no `Apply`, no `Trace` as a side-effecting query). Only structural and constructor operators.
3. C runs on an explicit `StagingEpisode` trigger keyed on `(Σ, R, EncodingSet)`, not ambiently.

With those three constraints, C is a clean optional accelerator for A's combinatorial conversion search, without infecting A's other duties or threatening soundness. Without them, C is at best vestigial and at worst dangerous.

The brief's own framing — "C is A's natural upgrade path when encoding choice becomes a runtime optimization concern" — is correct in spirit but slightly misleading: encoding choice is *not* primarily a runtime concern for γ̂ because of the ε problem. It is a *staging* concern, and that is exactly where the hybrid puts C. So the hybrid's placement is correct; what's missing is the soundness fence around it.

### 5.4 One concrete sharpening of the layer boundary

The current spec says "INTERFACE: B / STAGING: A / OPTIONAL: C / RUNTIME REP: E / SUBSTRATE: D." I would refine the A/C slice to:

```
STAGING:
  A_core      : Term(Σ) construction, refinement, policy, materialization scheduling
  C_search    : e-graph saturation over R_exact, extraction under κ
  A_finalize  : apply non-equational rewrites in R \ R_exact, attach invariants, hand to E
```

With `C_search` as a *pure function* `(Term(Σ), R_exact, κ, β) → Term(Σ)` invoked by `A_core` and not the other way around. This makes the boss/worker contract from §2 explicit and removes the ambiguity in "optional."

---

## Summary

- **Mesh:** A and C share `(Σ, R, InvariantLattice)`; they differ in whether they hold a point or an equivalence class of `Term(Σ)`. The boundary is `quotient` / `saturate` / `extract`. They are correctly adjacent in the hybrid.
- **Control:** A is the boss; C is a worker for equational search. Agency lives in A. C cannot self-invoke and has no vocabulary of its own.
- **Joint representation:** The e-graph parameterized by A's signature *is* the joint representation, with A's terms appearing at the boundary as ingest and extract. A is the degenerate (singleton) case of C.
- **Mismatches:** ε-equivalence is the severe one — C's union-find is hostile to lossy conversions. Side-effecting consumers must stay out of C's signature. Rule combinatorics shift but do not vanish. Materialization timing and time-evolution lifetime push C toward per-episode use.
- **Placement:** Correct in shape (A required, C optional, both at staging). Underspecified in three places: who triggers C, how the ε-rule-subset is separated, and which operators are excluded from C's signature. With those three constraints made explicit, keep C conditional; do not promote, do not eliminate.

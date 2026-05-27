I'll analyze the C/D mesh thoroughly and return findings as my final message. No file creation needed — this is pure conceptual analysis grounded in what I already know about e-graphs (egg/equality saturation literature) and tensor network contraction optimization. Let me reason through this carefully.

---

# C × D Mesh Analysis: E-Graph meets Tensor Network for γ̂

## Framing the pair

C is an **equality-saturating term-equivalence engine**: it stores ALL provably-equal encodings of γ̂ as parallel e-nodes within a single e-class, runs rewrites until fixpoint (or budget exhaustion), and extracts the cheapest member per query under some cost function. Its core type is something like:

```
EGraph : { ENode } / ≡_rewrites
ENode  : Op × [EClassID]
EClass : Set ENode + Analysis (lattice-valued)
extract : EGraph → EClassID → CostFn → Term
```

D is a **cost-aware contraction planner over an array-flavored DAG**: γ̂ is a node in a hypergraph whose edges carry shared index spaces; the optimizer searches over contraction orderings (tree decompositions of the network) to minimize peak working-set size or FLOP count. Its core type is something like:

```
TN    : Hypergraph (Nodes × IndexLabels)
Node  : NodeTypeTag × IndexSig × Materializer
plan  : TN → Goal → ContractionTree
exec  : ContractionTree → SubstrateValue
```

C asks "**which expression**?" D asks "**which traversal**?" They optimize over different sets — and that asymmetry is the key to how they mesh.

---

## Question 1 — How do C and D mesh?

The natural geometry is **C strictly above D, with one important seam at the leaves**.

C operates over a space of equivalent symbolic descriptions of γ̂. D operates over a space of traversal orders of a fixed network. These are different search spaces and they compose by **stacking, not by interleaving**:

```
choose expression e ∈ EClass(γ̂)        ← C's job
        ↓
compile e to a TN T                      ← seam (lowering)
        ↓
choose contraction order σ of T          ← D's job
        ↓
materialize a substrate value            ← D's exec
```

C's extraction selects WHICH tensor network shape to even consider; D's optimizer plans how to evaluate it. C closes the door on whole classes of networks (e.g., "we don't need the natural-orbital factoring at all here") before D ever sees them. So C is meta to D in the precise sense that **C's output is D's input**.

The "seam at the leaves" caveat: C's per-e-class **analysis** lattice and D's per-node **tag+witness** can overlap if you let them. An e-class for γ̂ could carry an analysis value that is itself a TN-cost estimate (a *coarse* one). That doesn't make C parallel to D — it just means C's cost function for extraction can read D's estimates without re-running D's planner inside saturation.

So: **C above D**, parallel **only at the cost-estimate channel**, never sibling and never inverted. D contains nothing of C; C contains D-derived *summaries* but not D's planner.

Signature view:

```
CDStack : EGraph_γ̂  →  Extract(cost_TN)  →  Expr  →  Lower  →  TN  →  Plan  →  Exec
```

Where `cost_TN : Expr → ℝ` is supplied by an *estimator* (not D's full planner) that approximates "what would D do with this lowered form?"

---

## Question 2 — Can one control or inform the other?

**Bidirectional, but asymmetric.**

**C → D (control, strong).** C decides which expression survives extraction; that expression dictates D's hypergraph topology. Different e-nodes in the same e-class can lower to *radically* different networks: one with three large rank-4 tensors, another with a long chain of rank-2 factors. D's planner has nothing to say about that choice — it can only plan over the network it is given. So C controls D's *input space*.

**D → C (information, advisory).** D cannot drive C's saturation in the strong sense — that would entangle two optimizers and make termination murky. But D can inform C in three concrete ways:

1. **Cost feedback into extraction.** D produces estimates `costEst : TN → ℝ` that C consumes during extraction. C's extraction problem is famously the hard step (NP-hard in general), and a good cost oracle is exactly what makes it tractable in practice. D is a natural oracle.

2. **Analysis lattice values.** A per-e-class analysis can store "best known TN cost lower bound" updated monotonically as new e-nodes appear. This is a well-formed lattice if you take `min` as the join, with `+∞` as bottom. C's invariant: analyses are join-monotonic under e-class merging, so D-derived numbers compose cleanly.

3. **Rewrite gating.** C's rewrites can be conditioned on D-estimated cost windows: "apply rewrite R only if it does not increase TN cost by more than factor k." This is a heuristic, not soundness — but it prevents C from chasing rewrites that obviously hurt D. (Use with care: this can hide equivalences that pay off only after several subsequent rewrites.)

The asymmetry matters: **C controls; D advises**. If you flipped them — D drives C — you lose the discovery power that makes C worth having in the first place, because D's planner has no rewriting vocabulary and cannot manufacture new e-nodes.

Typed sketch:

```
costEst       : TN → ℝ
analysis(γ̂)  : EClass → ℝ  -- best-known-cost lower bound
extract       : EGraph → EClassID → (Expr → ℝ) → Expr
                            where (Expr → ℝ) := compose(lower, costEst)
```

---

## Question 3 — What's the natural joint representation?

The cleanest joint structure is **"e-graph whose nodes lower to tensor-network fragments,"** *not* "tensor network whose nodes are e-classes."

Here's why the other direction fails. If D's nodes were C's e-classes, you would need every contraction step to operate over an entire equivalence class of expressions — which would force D's planner to enumerate or pick a representative on the fly, smearing C's job into D's inner loop. The contraction-order problem is already hard; making each node a *set* of possible nodes makes it brutally hard, and the contraction cost is no longer well-defined per node.

The reverse direction is clean. An e-node in C carries an *operator symbol* (Op) plus child e-class IDs. We extend it to carry a **lowering rule** that turns the (Op, child-extractions) into a TN fragment:

```
ENode  : Op × [EClassID] × Lower
Lower  : Op × [TN] → TN
```

Then the joint object is:

```
γ̂ : EClass
EClass = { ENode_1, ENode_2, ... }
extract(γ̂, cost) → ENode_*  -- cheapest by cost
lower(ENode_*)   → TN
plan(TN)         → ContractionTree
```

The e-graph hosts the *symbolic plurality*. Each e-node has a known mapping to a TN fragment. Children of an e-node are e-classes, so lowering recurses: pick the cheapest child extraction, lower it, plug it in.

A second-order structure also lives naturally on top: **D's contraction-tree planner can itself be invoked at extraction time** as part of the cost function. That is, extraction's `cost(ENode)` calls a (possibly cheap, possibly cached) planner pass to estimate D-cost of the lowered TN. This is the only place where C "sees" D's planner — and it sees it through the cost API, not through structural embedding.

So the joint representation is layered:

- **Outer:** an e-graph keyed on γ̂'s symbolic identity.
- **Middle:** lowering rules per e-node that emit TN fragments.
- **Inner:** D's planner runs on the lowered TN of the extracted expression.

Naming this object: a **"costed e-graph with TN-valued lowerings."** It is *not* a tensor network in disguise; it's a symbolic structure whose extraction targets a substrate where D is fluent.

---

## Question 4 — Where are the impedance mismatches?

Four of them, in roughly decreasing severity.

### Mismatch 1 — ε-equality vs numeric precision (the most serious)

C's equality is *syntactic-up-to-rewriting*: two e-nodes are merged when a rewrite rule (or a derived chain) certifies they denote the same value *exactly*. D operates on substrate values where equality is meaningful only up to a tolerance ε, and that tolerance depends on accumulated rounding from contraction order, kernel choice, and substrate.

This is a real conflict. Concretely: suppose C contains a rewrite "low-rank factorization with truncation k ⇒ original," derived because the truncation error is bounded by some ε. C wants to merge those e-classes. But the merge is *only* valid for queries that tolerate ε. C's union-find has no notion of "merge holds for ε > ε₀."

Two stances exist; both have costs.

**Stance A: refuse approximate merges.** C only merges under *exact* rewrites. D handles all approximation downstream. C loses much of its discovery power (most physically interesting equivalences are approximate).

**Stance B: parameterize e-classes by tolerance.** C tracks an ε on each merge, and extraction is parameterized by a query-tolerance budget. This is a research-grade extension; the e-graph literature has no clean off-the-shelf solution for it. It also makes C's monotonic analysis lattice non-trivial: now the analysis must track the *worst-case error* induced by chosen extractions, and that is not a join-semilattice in the obvious way (errors compose multiplicatively along extraction paths).

This mismatch is **unresolved** in the joint framing as stated. It's not fatal, but it is the genuine hard problem at the C/D seam. Realistically: keep C to exact rewrites for the substrate-invariant algebra (linearity, idempotence-derived identities, trace cyclicity), and push *all* approximation into D's witness machinery.

### Mismatch 2 — compile-time vs runtime cadence

C is built for compile-time saturation. D is built for runtime planning per query. They run at different rates.

In the joint stack, saturation happens *once per program shape*, not per timestep. D's planner runs *per materialization request*. This is fine if γ̂'s symbolic shape is stable over time. It is **not** fine if the symbolic shape mutates each timestep — which can happen during long evolution when self-consistency iterations introduce structurally new expressions.

The resolution is to treat saturation as **batched and amortized**: re-run only when the symbolic shape changes enough to invalidate cached extractions. D runs constantly; C runs occasionally. They mesh fine as long as you don't try to saturate per timestep.

### Mismatch 3 — invariant systems overlap

C's per-e-class analysis is a monotone lattice value computed under merges. D's per-node tag + witness records substrate-level facts (e.g., "rank ≤ k," "trace within ε of N"). They overlap in what they can express, but they live at different levels:

- C's analysis lives in the *symbolic* world; merging two e-classes joins their analysis values.
- D's tag+witness lives in the *materialized* world; it's checked after substrate construction.

When paired, the clean rule is: **C's analysis is a coarse symbolic over-approximation; D's tag+witness is the precise runtime ground truth.** They do not subsume each other — they refine each other. C's analysis filters extractions that obviously violate an invariant; D's witness is the actual evidence after the fact.

The risk: temptation to make C's analysis carry D's witness directly. Don't. C runs at saturation time; D's witnesses depend on substrate state that doesn't exist yet.

### Mismatch 4 — write path

This is the one the user explicitly asked about.

A write to γ̂ in C is an e-node insertion (or merge) into the e-graph. A write to γ̂ in D is a contraction-tree re-plan + re-materialization. These are not the same operation at the same cadence.

The mesh rule: **writes update C; D rebuilds on demand**. Specifically:

- An update to γ̂ that is *symbolically* a new expression (new e-node) goes into C. C may or may not re-saturate immediately; that's a policy decision.
- D-networks are *derived*. They are not the source of truth. When a downstream query requests materialization, D's planner builds (or reuses a cache of) a contraction tree from the currently-extracted expression.
- D networks **do not update in place** from C's perspective. If you want them to, that's a separate optimization (incremental tensor contraction) that lives entirely inside D's substrate layer and is invisible to C.

This is asymmetric in a way that feels right: C is the symbolic ledger; D is the executor. The executor caches; the ledger is authoritative.

---

## Question 5 — Placement in the 5-layer hybrid

The proposed stack is:

```
Layer 1: B (codata interface)
Layer 2: A (typed term algebra, staging)
Layer 3: C (e-graph, optional optimization)
Layer 4: E (pullback bundle, runtime)
Layer 5: D (tensor network, substrate)
```

Two concerns about C and D's placement:

### Concern 1 — C and D separated by E

C lives at layer 3 and produces an *extracted expression*. D lives at layer 5 and consumes a *tensor network*. Between them sits E, the pullback bundle. So the flow is:

```
C extract → (lower) → E bundle → (each slot is) D node
```

This separation is **legitimate but worth scrutinizing**. The legitimate part: C's output is a symbolic expression, not a multi-encoding bundle. E's role is to maintain *multiple synchronized encodings at runtime*, which is a different concern from C's *symbolic plurality* at compile time. C reduces to one extraction; E expands that one extraction into several encodings kept consistent. So the layering reads as: "symbolic search collapses to one form; runtime then re-expands into a bundle for whichever consumer needs whichever encoding."

The worth-scrutinizing part: this means **C's extraction discards information** that E might want back. If C decided that natural-orbital form was cheapest, but a downstream consumer wants the position-basis form, E has to recompute it from scratch — even though C *knew* about the position-basis e-node and threw it away.

A modest fix: extraction can be **multi-target**. Instead of `extract : EClass → CostFn → Expr`, use `extract : EClass → [CostFn] → [Expr]` returning one extraction per consumer profile, which then populates E's slots. The signature stays clean; C now gives E its initial bundle directly. This is a small change in interpretation — extraction is plural, one per slot — and it removes the discard-and-recompute waste.

### Concern 2 — Should C live INSIDE D as D's contraction-order optimizer?

**No.** This is a real temptation and it is wrong.

C is for *expression* equivalence. D's contraction-order optimization is for *traversal* of a fixed network. Different search spaces. You don't need C's machinery (e-classes, analyses, saturation) to do D's planner's job — D's planner is a tree-decomposition / dynamic-programming problem with its own well-developed algorithms. Bringing C inside D would:

- Force C to operate on substrate-coupled objects (tensors), violating C's substrate-agnostic posture.
- Confuse the two costs (rewrite-cost vs contraction-cost), making the cost function for saturation unprincipled.
- Eliminate C's main strength (discovering non-obvious symbolic equivalences via rewriting), because there's nothing to rewrite at the network-traversal level.

C-beside-D? Also wrong, but in a different way. Beside-D suggests two parallel optimizers on the same input, which they are not. C's input is a symbolic expression; D's input is a TN. They compose serially.

So: **C above D, separated by E, with E's slots populated by *multi-extraction* from C**. That's the cleanest placement.

### Does the placement work?

Yes, with the multi-extraction adjustment. The layers are honestly separated by what they optimize:

- B: which interface query is asked.
- A: which symbolic form is staged.
- C: which equivalent symbolic forms are worth tracking, and which is cheapest per consumer.
- E: which encodings are kept synchronized at runtime.
- D: which contraction order materializes a given encoding.

Each layer answers a different question. None of them does another's job, and the seams (A→C, C→E via multi-extract, E→D via per-slot lowering) are explicit.

---

## Summary of the mesh

C and D mesh **vertically**, not horizontally. C is strictly above D in the optimization stack: C decides what to compute (which symbolic expression); D decides how to compute it (which contraction order). They share a thin information channel — D-derived cost estimates flow up into C's extraction — but their data structures are not embedded in each other. The joint representation is a costed e-graph whose e-nodes carry TN-valued lowerings, with D's planner invoked at the leaves.

Three genuine impedance mismatches: ε-equality vs numeric precision (the only seriously unresolved one; punt approximation into D), compile-time vs runtime cadence (resolved by amortizing C's saturation), and write-path asymmetry (resolved by making D-networks derived, not authoritative).

In the 5-layer hybrid, placement is right with one tweak: **C's extraction should be multi-target, populating E's bundle slots directly**, rather than single-extract-then-have-E-recompute. C does not belong inside D and does not belong beside D. C above D with E between them is the correct geometry.

The single biggest honest caveat: **C's discovery power survives the joint framing only for *exact* rewrites.** Approximate rewrites — which is where C's saturation finds its most interesting non-obvious equivalences in practice — collide with D's precision witnesses in a way that has no clean off-the-shelf solution. The joint framing inherits *some* of C's discovery power (exact algebraic identities) but not all of it (approximation-based equivalences). If you need the latter, you are inventing new e-graph theory, not assembling existing parts.

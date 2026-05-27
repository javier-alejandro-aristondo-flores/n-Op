I'll analyze the mesh between framings A (typed term algebra) and D (tensor network) for the γ̂ library design. Let me first investigate the project's current state to ground my analysis in concrete artifacts.
I have a solid grounding in the project's conventions. The "no-symbolics on runtime path" rule and "compile-time staging via macros" pattern are particularly relevant to A and D's mesh. Let me look briefly at the level-1 design notes for γ̂ specifically and the prior staging pattern.
I have sufficient grounding. The prior library's "compile-time staging via macros, no symbolics on the runtime path, formula trees as authoring/macro-input only" pattern is direct precedent for the A→D staging boundary. Let me write the analysis directly.

---

# Mesh Analysis: Framing A (Typed Term Algebra) and Framing D (Tensor Network) for γ̂

## Pair character

Both A and D are **constructive** framings: each names a concrete artifact whose shape you can describe and whose pieces you can point at. They part company on **when** the construction is for, and **what alphabet** it is in.

- A's alphabet is **labels**: `LowRank`, `MomentumBlock`, `LocalizedSparse`, `UnitaryConjugation`, `Compose`, `Trace`. Its productions are typed term constructors. Its operations are visitors that rewrite one term into another while preserving a denotational meaning.
- D's alphabet is **slots**: a graph with open spatial indices, internal indices, node-type tags (`Dense`, `Sparse`, `LowRank`, `BlockDiag`), structural-invariant predicates, and accuracy witnesses. Its operations are graph operations: add a node, splice an edge, defer a contraction, schedule a contraction order, materialize.

A has no runtime cost model. D has no equational vocabulary. They are duals across the symbolic/numeric divide, in the same way an AST is the dual of an evaluator's working set. Inside the project's prior library this exact dual already exists: `core/formula-trees.rkt` is A-shaped (immutable struct algebra, authoring-time only), and the working `flvector` numeric kernels are D-shaped at substrate level. A's term `Trace(Compose(γ̂, Ĥ))` corresponds, after staging, to a D-network with two open ends fused via an edge sum.

The five questions, answered.

---

## 1. How do A and D MESH? What's the natural boundary, what artifact does A produce, what flows each way?

The natural boundary is a **typed plan handoff**. Concretely, A's expand-time pipeline emits an artifact whose type can be written as

```
ContractionPlan(γ̂) =
    Network(
        nodes        : List<NodeSpec>,
        edges        : List<EdgeSpec>,
        open_indices : (r, r'),
        node_tags    : Map<NodeId, TagWithInvariant>,
        evaluation   : OrderedDAG<ContractionStep>
    )
```

where `NodeSpec` carries a node-type tag (`R1=LowRank(rank=r)`, `R2=MomentumBlockDiag(blocks=B)`, `R3=LocalizedSparse(nnz=s)`), `EdgeSpec` carries the dimension along which two nodes meet, `TagWithInvariant` carries the structural-invariant predicate plus an accuracy-witness slot, and `evaluation` is a totally-ordered sequence of fused/contracted operations the runtime is permitted to execute as-is.

What flows **A → D**: the entire `ContractionPlan`. It is closed (no further symbolic rewriting permitted), inert (no closures, no thunks containing symbolic terms), and self-describing (every node carries its tag and invariant, every edge its dimension). Crucially, it is **already a graph**, not a term. A's last act before handoff is to flatten its term-tree into a network — the same flattening pass that the prior library's `staged-code-generation.rkt` does when it turns a `formula-trees` value into straight-line `flvector` code.

What flows **D → A**: at the boundary, *nothing*. D never calls back into A on the runtime path. Off the runtime path, two things flow back from D to A's expand-time:

- **Cost annotations** for tags. D owns the cost model (`cost : TagWithInvariant × OperationKind → CostEstimate`). A consults this when choosing between two equivalent rewrites at expand time. In other words D exports a *reference* — a table — that A reads at staging, but D's runtime engine never sees A's terms.
- **Witness types**. D defines what an accuracy witness looks like for each tag (e.g. for `R1`, a residual-norm bound; for `R3`, a truncation-mass bound). A's invariants must be expressible in D's witness vocabulary; if not, A can't produce a usable plan.

This is a one-way pipeline at runtime, with a small static back-channel for expand-time decisions. The asymmetry is on purpose, and it matches the prior library's hard rule: structured data is permitted as expand-time macro input or inert certificate output, never on a runtime path.

---

## 2. Can one CONTROL or INFORM the other? Is there a natural directionality?

There is a **strong directionality**: A drives D. The directionality has two pieces.

**Structural drive.** A's expand-time decisions *determine* D's runtime structure entirely. Every node, every edge, every tag, every contraction-step ordering in the `ContractionPlan` is produced by A. D's runtime engine sees only a network of opaque-numeric-array nodes — it has no symbolic knowledge of why those nodes are arranged the way they are. The decisive consequence: if A decides at expand time that γ̂ stays in `R1=LowRank(r)` across a `UnitaryConjugation`, D inherits an `R1` node whose contraction-step ordering keeps it `R1` at every step. D cannot promote it back to `Dense` without violating A's invariant.

**Cost-informed drive.** A reads D's cost model. A's rewrite rules know not just whether two terms are equationally equal (`Trace(AB) = Trace(BA)`) but also what each side *costs* under D's contraction-order cost function. The natural shape of the boundary is:

```
StagingDecision : RewriteCandidate × CostModel<D> → ChosenRewrite

where
    RewriteCandidate := { term : Term<A>,
                          tagging : Map<Subterm, NodeTag> }
    CostModel<D>     := NodeTag → OperationKind → CostEstimate
```

So A is the controller; D is the model A consults. The runtime contains only D's substrate.

**Inverse direction is essentially absent**, and that's load-bearing. Allowing D to drive A — say, by having D's runtime engine emit "I would like to rewrite this expression" requests back to A — would re-introduce the symbolics-on-runtime-path that the project's whole architecture exists to avoid. A informs D once, statically, and goes away.

There is one narrow exception: a recompile loop. If D's runtime detects that an `R1` node's accuracy witness has degraded (e.g., the truncation-mass bound was violated by accumulated unitary-conjugation drift), it raises with the offending witness, and the *next* staging pass — a fresh invocation of A with the new witness as input — gets to re-decide. This is offline; the runtime path never observes A.

---

## 3. What's the natural JOINT REPRESENTATION?

If you merge A and D into a single structure, you get a **two-stage tagged hypergraph** where the same graph carries two views:

```
StagedNetwork(γ̂) =
    nodes : List<StagedNode>
where
    StagedNode = {
        node_id          : NodeId,
        symbolic_origin  : Term<A>,                     // A's view: which subterm produced this node
        structural_tag   : { kind         : NodeKind,    // D's view: how it lives at runtime
                             invariant    : InvariantPredicate,
                             witness_slot : WitnessSpec },
        index_ports      : List<(IndexName, IndexDim)>,  // D's view: open indices
        provenance       : RewriteHistory<A>             // A's view: which rewrites produced this tag choice
    }
    edge : (NodeId, IndexName, NodeId, IndexName)
```

Read along `symbolic_origin` and `provenance` and you have A — a term with rewrite history. Read along `structural_tag` and `index_ports` and you have D — a tagged graph ready for cost-aware contraction ordering. The graph is the same graph; the two views are projections.

This is the **right** joint representation because:

- A's productions and D's tags are in bijection at the leaf level. `R1` is both an A-production (`LowRank(rank=r)`) and a D-node-type (`Dense=False, structural-invariant=rank≤r`).
- A's `Compose` and `UnitaryConjugation` are graph-shaped — they have two operand slots, an output type, and a deferred-evaluation pattern. They translate to D's "add a node with two input edges and one output."
- A's deferred constructors stage cleanly into D's deferred contractions; see Q4.

But this representation is only natural at the **staging boundary**. On the runtime path D drops everything outside `structural_tag` and `index_ports`. On the authoring path A doesn't care about `index_ports`. The unified structure is the artifact at handoff, not the lifelong shape of γ̂.

The reason to keep A and D distinct rather than collapsing them is the **lifecycle mismatch**: A lives at expand time and is discarded; D lives at runtime and is mutated by each timestep. A unified live structure would force the runtime to carry A's symbolic baggage, violating the no-symbolics-on-runtime-path principle. So the right answer to "what is the joint representation" is: a **staging-boundary type**, not a runtime type.

This is closely analogous to how a compiler represents a program. The unified joint representation is the IR-after-lowering: it carries enough of the source's structure that the optimizer can reason, but it's stripped enough that the back end can emit code. A is the front end; D is the back end; the `ContractionPlan` is the IR.

---

## 4. Where are the IMPEDANCE MISMATCHES?

Four, and they are real.

**Mismatch 1: A's equalities can demand encoding changes D won't accept.**
A's rewrite vocabulary contains identities like `Trace(γ̂ Ĥ γ̂) = Trace(γ̂² Ĥ)`. Under closed-shell idempotence (γ̂² = γ̂), the right side is `Trace(γ̂ Ĥ)`, a cheaper contraction. But `γ̂²` is only equal to `γ̂` **as a meaning**; as a *representation*, if γ̂ is held in `R1=LowRank(r)`, then γ̂² is also `R1` with rank ≤ r, but the *witness* for the new rank may differ. A's identity preserves meaning; A's identity does *not* preserve D's witness. The mismatch: A is allowed to use idempotence freely; D needs a fresh witness for every node it materializes. The fix is to attach a **witness-derivation rule** to every A-rewrite, so that when A applies `γ̂² = γ̂`, it produces an updated `WitnessSpec` for the resulting node. Many rewrites won't have a clean derivation rule, and the architecture has to refuse those rewrites at staging or commit to re-deriving the witness at runtime (which contradicts the runtime path).

**Mismatch 2: A's identities are exact; D's costs are amortized over invariants.**
A's `Trace(AB) = Trace(BA)` is a clean symbolic identity. D's cost for the two sides depends on the tag combination: `(R1, R3) → R3` may be cheap, `(R3, R1) → R1` may be expensive, even though both contractions yield the same scalar. A doesn't naturally know which order produces which intermediate tag. The fix is to push **tag inference** into A: extend A's productions so that `Compose(R1, R3)` not only produces a `Compose` term but also infers an output tag (with rule `R1 × R3 → R3` or whatever the algebra says). Without this, A would produce a plan that's denotationally correct but with the wrong contraction order, and the project's hard rule forbids D from rewriting at runtime to fix it.

**Mismatch 3: D's contraction-order optimizer is NP-hard at scale; A's symbolic algebra is not a substitute.**
A *reduces* the problem size before D sees it — by collapsing equivalent subnetworks, eliminating identity rewrites, fusing adjacent unitary conjugations — but A does not *solve* the contraction-ordering problem. A's rewrites give D a smaller graph; D still has to pick an ordering on that smaller graph, and "smaller" doesn't mean "tractable." For a γ̂ at L1 of the BO hierarchy with cross-coupling to E_KS, the network can be quite wide even after A's collapsing pass. The fix is honest: D's runtime ships with a contraction-order *heuristic* (greedy, dynamic-programming-with-cutoff, or whatever), and the cost model A reads is the heuristic's cost model, not an exact one. A's job becomes "produce a plan whose heuristic-chosen ordering is good enough." There is no perfect handoff here; A reduces but does not eliminate D's NP-hard step.

**Mismatch 4: A can express things D has no node-type for.**
A's grammar is closed by its production set: `R1`, `R2`, `R3`, plus combinators. If a user asks for a γ̂ encoding that is, say, a sum of an `R1` part and an `R2` part — a perfectly legitimate symbolic expression — D needs a `SumOfNodes` tag with its own invariant and witness. If D's tag vocabulary doesn't contain `SumOfNodes`, A's term is denotationally valid but unstageable: A produces it; D rejects it; the staging boundary errors loudly. The fix is to either **close A's grammar against D's tag vocabulary** (refuse to type-check A terms whose tags D can't represent) or **keep D's tag vocabulary in lockstep with A's productions** (every A production has a D tag). The former is the project's style; the latter is brittle.

**A general statement of the mismatch.** A is a denotational algebra; D is a structural algebra. Denotational identities (`γ̂² = γ̂`) do not preserve structural witnesses; structural identities (associativity of contraction within a network) do not preserve denotational meaning if any operand carries a destructive invariant (e.g., a low-rank truncation accumulates error under reassociation). The two algebras commute only on a subset of operations, and the project's job is to identify that subset and refuse to compile anything outside it.

---

## 5. In the proposed 5-layer hybrid, does A and D's placement work?

The proposed stack:

```
INTERFACE LAYER          →  B
STAGING / EXPAND LAYER   →  A
OPTIONAL OPTIMIZATION    →  C
RUNTIME REPRESENTATION   →  E
RUNTIME SUBSTRATE        →  D
```

**Placement of A and D relative to each other is correct.** A is at the expand-time top; D is at the runtime bottom; the directionality is exactly what Q1–Q2 require. The two-stage tagged hypergraph of Q3 is the artifact that crosses from A (and optionally C) to E (and through E to D).

**The spacing concern.** C and E sit between A and D. Is that the right spacing?

C is **optional** and saturation-time only. If C is absent, A produces a `ContractionPlan` that goes directly to E and from E to D. If C is present, A produces a *term*, C saturates it into an e-graph keyed by tag-and-witness, and extraction produces the `ContractionPlan` D consumes. Either way, the A → D pipeline runs; C is a refinement of A's rewrite-choice step. The spacing is fine because C *is* part of A's job (just heavier machinery); A and C together produce the artifact for D.

E sits between **runtime representation** and **runtime substrate**. This is where the spacing decision actually matters. E is a multi-representation bundle that holds several synchronized encodings of the same γ̂. The proposed pattern is that each *slot* of an E-bundle is a D node — i.e., E indexes into a small collection of TN nodes, one per encoding, with a consistency witness across them.

Under this layering A produces, *per slot*, a sub-plan: "this slot holds γ̂ in `R1=LowRank(r)`; here is the contraction sub-network that maintains it across the next timestep; here is the witness." E aggregates `|B|` such sub-plans into a bundle and the consistency invariant becomes a witness on the boundary edges that cross from one slot to another. D's runtime engine then sees `|B|` parallel TN sub-graphs plus the consistency-witness edges.

**This works**, but it has a cost A's view doesn't immediately reveal: A has to know `|B|` at staging time and emit `|B|` parallel plans. A's `UnitaryConjugation` becomes `|B|` parallel `UnitaryConjugation` constructors, one per slot, each with its own tag. A's productions naturally lift across the bundle (a product structure), so this is mechanical, but it inflates the `ContractionPlan` by a factor of `|B|`.

**A direct A → D pipeline (skipping E) is cleaner**, but it forces a single-representation choice at staging, which is exactly what E exists to avoid. So E is load-bearing; A and D are not adjacent for a real reason; the cost is that A has to think in product-of-slot terms.

**One critique of the spacing.** B sits at the top as the interface, but B is destructive (codata, only observations). The staging layer A produces a structural plan but the interface B advertises only an observational vocabulary. A user calling B can never construct a term directly; A's terms exist only inside the staging pipeline. This is correct (B's purpose is to insulate users from the staging machinery), but it means A's algebraic vocabulary is **not** part of the user-facing surface. The "algebraic" benefits of A — the rewrite vocabulary, the named-formula composition style — are available only to library authors writing inside the staging pipeline, not to users of the library. If you wanted users to benefit from A's vocabulary, you would need a thin A-aware façade above B that lets users compose terms and then re-enters the staging pipeline. The proposal as written does not contain this façade, and the trade-off is deliberate (no symbolics on runtime path), but it does mean A's "algebraic vocabulary" advantage is internal infrastructure, not user-visible.

**Verdict on the layer placement.** A at staging and D at substrate is the right placement and the right directionality. E sitting between them is load-bearing and worth its cost. C is an optional A-side refinement that doesn't change the A→D pipeline shape. The only architectural concern is that A's vocabulary doesn't reach the user surface — which is by design, but worth flagging because some of A's strongest selling points (named-formula composition, rewrite legibility) are then internal artifacts only.

---

## Summary

A and D pair cleanly as **front-end and back-end of a staging compiler for γ̂**. A is the symbolic IR that lives at expand time; D is the numeric IR that lives at runtime; the boundary between them is a typed `ContractionPlan` produced once per staging pass and inert thereafter. A drives D: every node, edge, tag, and contraction order in D's runtime graph traces back to a decision A made. The cleanest joint representation is a tagged hypergraph at the boundary — two projections of one structure, dropped on either side of the staging line. The mismatches are real but localized: denotational identities don't preserve structural witnesses, and A's grammar must be kept aligned with D's tag vocabulary or staging errors loudly. The proposed 5-layer hybrid places A and D correctly with respect to each other and the spacing of E between them is justified by E's multi-representation contract, at the cost of A having to emit plans in slot-product form.

The mesh is the strongest of the five framings as a vertical pair. It maps directly onto the project's existing convention (formula trees → staged code → flat numeric kernels) and does not require introducing any new architectural pattern beyond what the prior library already practices.

**Relevant file paths**:
- `/home/javier/Desktop/Physics/Programs/n-Op/IMPLEMENTATION-PLAN.md` (sections 6 Level-1, 7 methods/12, 14 directory tree, 17 open questions especially #2 on γ̂ representation and #3 on macro grammar)
- `/home/javier/Desktop/Physics/Programs/n-Op/physics-library-architecture.md` (prior library's staging discipline — `core/formula-trees.rkt`, `core/staged-code-generation.rkt`, the "no-symbolics on runtime path" rule restated across module headers; this is the direct precedent for the A → D handoff pattern)

I'll analyze the B (codata) and D (tensor network) pair as the outer interface / inner implementation pairing for γ̂. Let me first orient myself by examining the existing repository structure to understand the project's actual vocabulary and conventions before producing the analysis.
I'll note the plan-mode constraint but my task is read-only analysis with a final-message deliverable, so I will continue research without making edits. Let me look at the existing architecture document since it likely already defines vocabulary.
Good context. I have enough background — the architecture document describes an *existing* library, but the new /physics library being designed (where γ̂ lives) is what the analysis is about. Let me check the implementation plan and properties.md, which likely contain γ̂-specific framing language.
I now have sufficient grounding. The user's task is conceptual analysis of the B-D pairing for γ̂. I've confirmed γ̂ is at the level of the unified state and that the project explicitly prefers typed signatures with opaque kernel types — which is exactly the abstraction B (codata) trades on. I have enough context to produce the report.

I do not need clarification: the task statement is self-contained and the five questions are well-specified. Plan mode is engaged, but the task is read-only research with a final-message deliverable — no files to create, no edits required. I'll skip the plan file because the deliverable IS the analysis itself, not a multi-step implementation.

---

# B (codata) × D (tensor network) — Mesh Analysis for γ̂

## Q1. How do B and D MESH? The natural boundary.

The natural picture is a **two-tier object** with a hard interface line between them:

```
        ┌─────────────────────────────────────────────┐
        │   B-surface: opaque γ̂ with destructor menu   │
        │   apply, density, trace, eigendecomp,        │
        │   timestep, restrict, basis_change           │
        └──────────────────┬──────────────────────────┘
                           │  (the boundary)
        ┌──────────────────▼──────────────────────────┐
        │   D-interior: tagged TN node + open indices  │
        │   tag ∈ { Dense, Sparse, LowRank, BlockDiag },│
        │   witness, deferred contraction plan         │
        └─────────────────────────────────────────────┘
```

The boundary is a **handler dispatch table**. For each destructor in B's signature, the handler is a function from the underlying D node to (i) a request for a fresh sub-network and (ii) a contraction planner invocation that will materialize the destructor's return value.

Schematically, in CS-style pseudotypes, B looks like a coalgebra

```
   γ̂  :  Gamma
   apply         : Gamma -> (Vec  ->  IO Vec)
   density       : Gamma -> (Point -> IO Scalar)
   trace         : Gamma ->          IO Scalar
   eigendecomp   : Gamma ->          IO Eigenpairs
   timestep      : Gamma -> Op    -> IO Gamma
   restrict      : Gamma -> Sub   -> IO Gamma
   basis_change  : Gamma -> Basis -> IO Gamma
```

and D supplies the concrete carrier:

```
   data Node tag = Node {
       openIndices : (Index, Index),
       payload     : tag,
       witness     : InvariantWitness tag,
       plan        : ContractionPlan        -- deferred edges, not values
   }
```

The mesh is: `Gamma ≡ ∃tag. Node tag` plus a handler `H : Destructor → Node tag → Plan`. A B destructor call does not return a value directly; it returns a `Plan` request, which then gets handed to D's contraction-order optimizer, which schedules it, and only then materializes the answer.

Concretely, `apply γ̂ v` decomposes into:

1. B receives `apply` on the opaque handle.
2. The handler looks up the tag.
3. If `Dense`, it emits a one-contraction plan `Node ⊗ v` on the matching index.
4. If `LowRank` with carriers `(U, S, V†)`, it emits `U · (S · (V† · v))` as a three-edge plan with a specific contraction order.
5. If `BlockDiag`, it emits a parallel reduction over block sub-plans.
6. D's planner executes; the result is wrapped back as `Vec` and handed to the caller.

So the destructor *names* the question; the tag *chooses* the network skeleton; the planner *orders* the contractions; D *executes*. B never sees the wire; D never sees the user.

The mesh is clean because B and D agree on two things and disagree on everything else:

- They agree γ̂ has *two open spatial indices* — D's structural commitment matches B's destructor arities (everything in B's menu either consumes one index of γ̂, both, or neither).
- They agree on the *destructor* shape — every B destructor reduces, in D-land, to a planned contraction whose result type is fixed by B's signature.

Everything else (storage, tag, witness, planner) lives strictly on D's side.

## Q2. Can one CONTROL or INFORM the other?

**Both directions exist, asymmetrically.**

**B → D control (top-down).** B's destructor menu is *closed* and small. That closure constrains what D is asked to do. D never needs to support an arbitrary contraction pattern — only the seven or so shapes B exposes. This is exactly the constraint that lets D's planner be predictable: the search space of "things B might next ask of D" is bounded by B's signature, which means D can precompute cost models per (destructor, tag) pair. So B's *interface shape* informs D's *planner heuristics*.

**D → B control (bottom-up).** D's tag system informs B in a softer but real way: B's destructors come with a *cost profile* that depends on tag. The handler can publish a *cost oracle* alongside the destructor table:

```
   cost : Destructor -> Tag -> CostEstimate
```

Downstream code that wants to be clever — schedulers, training loops, the upstream A/C/E layers in the hybrid — can query this oracle without breaking B's opacity, because the cost is a *property of the handle*, not a leak of the network itself. The handle stays opaque; only the cost of acting on it is visible.

So the asymmetry is: **B controls the shape of the conversation; D controls the price.** B says "you must answer these N questions"; D says "and here is what each answer costs given the current tag."

There is a third, subtler direction: **D's tag rewrites can be triggered by B's usage pattern.** If a γ̂ is hit repeatedly with `apply` and never with `density`, the handler can opportunistically re-tag from `Dense` to `LowRank` (with a witness-controlled tolerance) without B ever noticing. The destructor laws hold up to the witness; the price drops; B's interface is unchanged. This is the *codata version of adaptive memoization* — and it is only possible because B forbids B-callers from caring about the encoding.

## Q3. What is the natural JOINT REPRESENTATION?

The joint representation is, in concrete CS terms, an **existential record** carrying:

```
   data Gamma = forall tag.
     Gamma { handle      : OpaqueRef
           , destructors : Destructor -> Plan      -- B-tier menu
           , node        : Node tag                -- D-tier carrier
           , cost        : Destructor -> CostEst   -- shared boundary
           , witness     : InvariantWitness tag    -- D-tier proof object
           }
```

Read this as: **"a Gamma is a handle plus a fixed dispatch table over a hidden TN node."** The destructor signatures are public; the tag and node are existentially quantified — callers cannot pattern-match on them, only invoke destructors.

This is one structure, not two. It's a *coalgebra whose state functor is the D node-type sum*. In functor language:

```
   F(X) = (Vec → Vec) × (Point → Scalar) × Scalar × Eigenpairs
        × (Op → X) × (Sub → X) × (Basis → X)
```

B's coalgebra is `Gamma → F(Gamma)`; D supplies the *carrier* of that coalgebra. So the joint object is literally an F-coalgebra in which the carrier set is the disjoint union of tagged D-nodes:

```
   Carrier_D  =  Σ tag ∈ {Dense, Sparse, LowRank, BlockDiag}.  Node tag
   gamma_step : Carrier_D → F(Carrier_D)
```

This is the cleanest unified picture I can give: **the codata interface B is the F-coalgebra view of the D tensor-network carrier**. They are not two structures pasted together; they are two faces of one coalgebra. B is "what you can observe about it"; D is "what it is made of."

That said, the picture is not seamless — see Q4.

## Q4. IMPEDANCE MISMATCHES.

There are at least four real frictions. I'll be honest about them.

### M1. Cycle / self-consistency.

D's report admits the cycle in `Ĥ[γ̂] γ̂ = γ̂ Ĥ[γ̂]` lives *outside* the DAG, because a TN DAG by definition has no edges back to its root. B claims to "natively handle cycles via coalgebraic fixed points." Does B-over-D close the gap?

**Partly, yes — but the mechanism is not as automatic as B's marketing.** A coalgebraic fixed point of γ̂ in B-land is the unique γ̂* such that the destructor `timestep γ̂*` returns a γ̂ "observationally equal" to γ̂* — i.e. the full set of destructor outputs agree under whatever witness equality B picks.

The mechanism is:

1. B exposes `timestep : Gamma → Op → Gamma`. The `Op` is `Ĥ[·]`, a function from γ̂ to a Hamiltonian-shaped destructor target.
2. The fixed-point operator lives at B's level: `fix(F) = γ̂` such that `bisim(F(γ̂), γ̂)` under B's destructor laws.
3. Under the hood, this iterates `γ̂ ← timestep γ̂ Ĥ[γ̂]` — and each `timestep` call asks D to build a fresh sub-network whose root carrier is the next iterate.
4. D's DAG is *re-instantiated per iteration*; the cycle is closed at B's level by the fixed-point loop, while each individual D DAG remains acyclic.

So the resolution is: **D's DAGs are acyclic per-step; B's coalgebra closes the cycle across steps.** The cycle becomes a temporal loop over snapshots, not a structural loop inside any one DAG.

The honest part: **B does not give you the fixed point for free.** "Coalgebraic fixed point" is a *spec*, not an algorithm — you still need a concrete iterator with a termination witness (a contractive map, a damping schedule, a convergence test on the destructor outputs). B's contribution is *making the cycle expressible* (the recursive call typechecks) and *giving you bisimulation as the equality* (so two γ̂ that produce the same destructor outputs are equal). The work of converging still happens; B just gives it a clean type.

### M2. Opacity vs cost transparency.

This is the sharpest tension. B's whole pitch is opacity: callers cannot see the encoding. D's whole pitch is cost transparency: callers (especially the planner) want to know costs.

The resolution sketched in Q2 — publish a `cost` oracle alongside the destructor table — *works* but it weakens B. Once cost is observable, callers can branch on it. Code that does `if cost(apply, γ̂) < threshold then ... else materialize_alternative()` is, in a formal sense, observing the encoding, because the only thing the cost depends on is the tag.

The honest version: **B does not hide encoding from cost-aware callers; it hides it from value-consuming callers.** Cost is a *first-class observation* that B has to admit into its destructor menu, or downstream optimization is blind. The opacity holds against "what is the value of γ̂(r, r')?" but not against "how expensive is asking?"

I think this is acceptable but should be stated up-front: B is a *value-opacity* interface, not a *cost-opacity* interface.

### M3. Bounded shape vs lazy / streaming destructors.

D's nodes have *bounded shape* — fixed open indices, fixed tag (per snapshot), fixed contraction plan once chosen. B's destructors can be *streaming*: `apply` can be asked for one column of γ̂·v at a time; `density` is a function on a point and a caller may want to walk through many points lazily; `eigendecomp` may want only the top-k eigenpairs.

D's contraction planner is built for full materialization. Asking it for a *streaming* answer either forces full materialization upfront (wasted work) or demands the planner know how to *partial-contract* (extra machinery D's spec did not promise).

The resolution: B's destructor menu has to be redesigned to be *index-parameterized* where streaming matters. So `apply` becomes

```
   apply : Gamma -> Vec -> Index -> IO Scalar
```

(the one-column version) and the planner gets a slicing primitive. This is doable but it shifts work onto D and constrains the planner: the cost oracle now has to publish *per-slice* cost, not just per-call cost. It works but it is real friction.

### M4. Binary operations.

B's report flagged this independently: "binary operations strain F-coalgebra." Concretely, anything like

```
   compose : Gamma -> Gamma -> Gamma
   inner   : Gamma -> Gamma -> Scalar
```

does not fit the destructor template `Gamma → F(Gamma)` cleanly, because the second argument is itself a coalgebra carrier the destructor cannot observe.

D handles this fine: two tagged nodes get joined into a bigger plan, the planner picks an order, done. So D solves the operational side. But B's *typing* is awkward: a binary destructor wants to walk both arguments' carriers, which means B has to either (a) admit a "two-argument coalgebra" extension (clunky) or (b) treat binary ops as *not destructors* but as separate *building combinators* that produce new Gamma from existing Gammas without going through the destructor menu.

I think (b) is the right move and is consistent with D's "build then materialize" stance: binary ops are *constructors* in D and *not* destructors in B. B keeps its destructor menu unary; binary ops form a separate small algebra that produces Gammas which then expose B's destructor menu. This is exactly what the typed-term layer A is good at — which prefigures the answer to Q5.

## Q5. Does the 5-layer placement work? Is B-D separation real or artificial?

The current proposal puts:

```
   INTERFACE LAYER          B  (codata)
   STAGING / EXPAND LAYER   A  (typed term algebra)
   OPTIONAL OPTIMIZATION    C  (e-graph)
   RUNTIME REPRESENTATION   E  (pullback bundle)
   RUNTIME SUBSTRATE        D  (tensor network)
```

with three layers between B and D. **I think this is roughly right but mildly mis-described.** Let me argue.

**B and D should sit on each other for the read path.** A read-path destructor call — `apply`, `density`, `trace` — should go: B-handler → D-planner → D-execute → answer. Inserting A, C, E in the middle of *every* destructor call would be a tax. A is a staging / expand-time layer; it should not be on the runtime read path. C is *optional* by your own description. E (pullback bundle) is a *representation choice for a single γ̂* — it lives at the same conceptual level as D, not above it.

So the read path is really **B → D, two layers, full stop.** The other three layers are not in the read path; they're in the *write path* and the *construction path*.

**The write path is where A, C, E earn their keep.** When a γ̂ has to be *built* (initial state, after `timestep`, after `restrict`, after `basis_change`), there's a richer story:

1. B's `timestep γ̂ Ĥ` is a destructor that needs to return a new Gamma.
2. The *construction* of that new Gamma is a multi-step affair: pick a representation (E's job: which encodings should the new bundle carry?), possibly stage a symbolic expression for the new state (A's job: the term `γ̂' = step(γ̂, Ĥ, dt)` typed at A's level), possibly optimize the expression (C's job, but only at saturation time), and finally hand it to D for runtime carriage.
3. So the write path is **B (asks for new Gamma) → A (stages the symbolic term) → C (optionally rewrites it) → E (chooses synchronized encodings) → D (carries the chosen encoding as a network).**

That is a real five-layer pipeline, but only on the *write path*. On the *read path*, B sits directly on D.

So my refined picture is:

```
            ┌──────────── READ PATH ────────────┐
            │                                    │
            │      B  ──destructor──>  D         │
            │                                    │
            └────────────────────────────────────┘

            ┌──────────── WRITE PATH ───────────┐
            │                                    │
            │   B → A → (C?) → E → D             │
            │                                    │
            └────────────────────────────────────┘
```

The five-layer hybrid is right but it is a **write-path pipeline**, not a uniform stack. B and D are a **bidirectional pair**: B on top for reads, D on the bottom for both, with A/C/E mediating only when a new Gamma is constructed.

**Does B-over-D resolve B's "encoding-choice policy lives nowhere natural" weakness, or just push it into D?**

It *partly* resolves it and *partly* relocates it. The relocation is honest: D's tag (`Dense | Sparse | LowRank | BlockDiag`) is the encoding choice. So "where does the encoding live?" gets a clear answer: it lives in D's tag, witnessed by D's invariant witness, defended by D's contraction planner. That's a real win — B alone had no place to put it.

But the *policy* — i.e. when to switch from `Dense` to `LowRank`, when to break out a `BlockDiag` — does not live in D either. D knows what each tag costs; D does not know which tag is *appropriate* for *this* γ̂ at *this* moment. That policy comes from elsewhere: from E (which encodings are synchronized in the current bundle), from A (what symbolic structure the construction step produced), from C (what rewrites are available), or from external profiling.

So the honest story: **B-over-D gives encoding a *home*; E and A give encoding a *policy*; C gives encoding *rewrites*; D gives encoding *costs*.** All four are needed, but the home is D, which is exactly what B was missing.

**Should A and C sit between B and D in the hybrid?** No — they sit *next to* the B-D pair, on the construction side. C is optional because not every construction needs rewriting; A is mandatory for any *symbolically described* construction (`γ̂' = exp(-iĤdt) γ̂ exp(iĤdt)` etc.) but not for a primitive construction like "load this initial state." E sits *inside* a Gamma, not above or below D — a single Gamma can be a *bundle* whose members are each D-tagged nodes, with synchronization witnesses across them.

So a final layering I'd defend:

```
           ┌─────────────── B (codata: destructor menu, opacity, cost oracle) ────────────┐
           │                                                                              │
           │   each Gamma is internally:                                                  │
           │                                                                              │
           │   ┌──── E (bundle of encodings, synchronized) ────┐                          │
           │   │                                                │                          │
           │   │   each bundle slot is a D node                │                          │
           │   │   (Dense / Sparse / LowRank / BlockDiag)      │                          │
           │   │                                                │                          │
           │   └────────────────────────────────────────────────┘                          │
           │                                                                              │
           │   construction of new Gammas goes through A (+ optional C) before E/D        │
           └──────────────────────────────────────────────────────────────────────────────┘
```

B is the outer shell. E is the *internal multiplicity* (a Gamma may carry several synchronized encodings). D is the *internal substrate* under each E slot. A and C are *construction-time only*, sitting outside the B shell, producing new Gammas that then get sealed.

This is consistent with the proposed five-layer hybrid in spirit — B outermost, D innermost — but it disagrees with the proposal that A, C, E are *layers between* B and D. They are not all in series. **B and D are directly stacked**; E is *inside* the stack as a structural multiplier; A and C are *outside* as construction-time machinery.

---

## Summary

- **Mesh**: B is the F-coalgebra view of a tagged D-node carrier. The boundary is a handler table that lifts every B destructor to a D contraction plan. Clean because they agree on γ̂'s two open spatial indices and on the destructor menu.
- **Direction of influence**: B controls the *shape* of the conversation; D controls the *price*. B's closure of the destructor menu lets D specialize its planner; D's tag and witness let B publish a cost oracle.
- **Joint representation**: an existential record `Gamma = ∃tag. (handle, destructors, Node tag, cost, witness)`. This *is* the F-coalgebra; the two framings are two views of one object.
- **Mismatches**: D's acyclicity is patched by B's per-step fixed-point loop, but the loop is a spec not an algorithm. B's opacity does not extend to cost. D's bounded shape clashes with streaming destructors and requires per-slice cost. Binary ops escape the destructor template and become A-level construction combinators, not B destructors.
- **5-layer placement**: B and D belong **directly stacked on the read path** — the three "intermediate" layers are not in the read path. A and C are construction-time machinery that *produces* Gammas. E lives *inside* a Gamma as a multi-encoding bundle whose slots are D nodes. The five framings are real and needed; they just aren't a linear stack.

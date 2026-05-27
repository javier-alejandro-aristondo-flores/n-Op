# B and E Mesh Analysis: Codata Interface and Pullback Bundle

## Preamble: Framing the Relationship

Before answering the five questions, I want to state the structural intuition that drives this entire analysis, because it makes the questions easier to navigate.

B is a **specification of behavior**: a collection of destructor signatures and the laws they must satisfy. It says nothing about how γ̂ is stored, only what you can ask of it.

E is a **specification of state**: a particular shape of internal storage (a tuple of synchronized encodings with a consistency witness) and an update discipline (write-through, write-back, deferred-reconciliation).

When two design framings are at this distance from each other — one is a behavioral interface, the other is a state shape — the natural relationship is **implementation**. E implements B. This is not a discovery; both prior reports already noted it. The interesting questions are not "do they fit?" but "what does the fit cost?", "what does it constrain?", and "where do the edges show through?".

With that in mind:

---

## Question 1: How do B and E mesh?

The clean answer is: **E lives inside B's handlers as the concrete state of the opaque coalgebra**.

A codata object in B has, conceptually, the typed shape:

```
GammaHat ≅ {
  apply         : Vector → Vector,
  density       : Position → Scalar,
  trace         : () → Scalar,
  eigendecomp   : () → SpectralStream,
  timestep      : Duration → GammaHat,
  restrict      : Subspace → GammaHat,
  basis_change  : BasisMap → GammaHat,
  ...
}
```

This record type is the F-coalgebra signature. The **state carrier** behind this record — the thing the destructors close over — is unspecified by B. E proposes a specific carrier:

```
EBundleState = {
  slot_R1     : Encoding_R1,
  slot_R3     : Encoding_R3,
  witness     : ConsistencyWitness,
  policy      : UpdatePolicy
}
```

So the mesh is: B says "γ̂ : ν F", where ν F is the terminal coalgebra of some signature functor F. E says "I provide a coalgebra (EBundleState, step : EBundleState → F(EBundleState)) by writing each destructor as a dispatch over slot_R1 and slot_R3". The unique anamorphism from (EBundleState, step) into ν F is the implementation morphism. That morphism is B's view of an E-backed γ̂.

The boundary is sharp: **B sees only the anamorphism's image, not its source**. From B's side, γ̂ is just a record of destructors. The fact that those destructors happen to be implemented by dispatching to one of two slots is invisible unless E chooses to expose it.

E is therefore **inside** B's handlers, not sideways to it. "Sideways" would mean E provides operations B doesn't, and B provides operations E doesn't, with both visible to consumers. That's not the design: every E operation should be expressible as some B destructor (possibly composite), and B destructors should be free to be implemented by E dispatch.

But there is a subtler point. B is **abstract**; the destructor signature is a contract. E is **one carrier among many**. So while E lives inside B's handlers in any given instantiation, B exists prior to and independent of E. You can write down B without ever mentioning E. The reverse is harder: E's bundle structure is most naturally motivated by the need to make certain B destructors cheap.

---

## Question 2: Can one control or inform the other?

This is bidirectional, and the bidirectionality matters more than the answer.

### B's destructor signature constrains E's bundle structure.

E exists because some B destructors are expensive in one encoding and cheap in another. The set of destructors B exposes determines which encodings are worth keeping in the bundle. If B exposed only `apply : Vector → Vector`, you'd want one matvec-friendly slot and E would degenerate to a single-element bundle (i.e., E reduces to "pick one encoding"). If B exposes both `density : Position → Scalar` and `eigendecomp : () → SpectralStream`, suddenly two very different slots are justified, and E becomes a real bundle.

So the **cardinality and content of E's bundle is a function of B's destructor menu**. Concretely:

```
optimal_bundle : DestructorMenu × CostModel → BundleShape
```

where `BundleShape` is roughly a multiset of encoding types. E is therefore *informed* by B's API surface.

### E's bundle structure constrains what B can expose efficiently.

Conversely, once E commits to a bundle shape, only certain B destructors are cheap. If E maintains {R1, R3} only, then a destructor `transition_amplitude : Operator → Scalar` that's natural in some third encoding R7 becomes expensive — it must be served by conversion from R1 or R3 at call time.

This creates a feedback loop: B's API drives E's bundle, but E's bundle limits which extensions of B's API are practical. In typed terms:

```
B_efficient(E) ⊆ B_total
```

where `B_efficient(E)` is the subset of B destructors that E can serve without conversion. The hybrid design should probably either (a) freeze B's destructor menu early and let E optimize for it, or (b) keep E's bundle dynamic and let it grow when new B destructors get used hot.

### The deeper control question: who runs the coalgebra step?

B's coalgebraic structure says: `timestep : Duration → GammaHat` is a destructor that produces a new coalgebra state. From B's perspective, that's just function application. From E's perspective, each `timestep` call is a state transition that must update both slots and re-establish the consistency witness. So **B's destructor calls are the events; E's update policy decides how those events touch the bundle**.

This is the cleanest way to express the relationship: B is the **event interface** (what callers do), E is the **state machine** (how the bundle responds). Neither dominates; they're orthogonal aspects of the same coalgebra.

---

## Question 3: What's the natural joint representation?

I think there are two valid framings, and they differ in what gets emphasized.

### Framing 1: Codata interface with internally-bundled state.

```
GammaHat = {
  destructors : F(GammaHat),    -- the B-side: behavior
  carrier     : EBundleState    -- the E-side: state, private
}
```

This is the obvious composition. B's interface is public; E's bundle is the chosen carrier; the consistency witness lives in `EBundleState` and is not exposed via any destructor.

**Pros:** Clean opacity. B's consumers see only `destructors`. Bundle cardinality is invisible. E's update policy can change (write-through to write-back) without breaking B's contract.

**Cons:** The consistency witness is a real thing — it has computational content (it bounds the operator-norm gap between slot decodings). Treating it as purely private throws away information that downstream layers might want for diagnostics, error estimation, or to decide whether to trust a fast-slot result.

### Framing 2: Lenses with bundle-shaped focus.

A lens onto R1 is, roughly:

```
Lens(GammaHat, R1) = {
  view   : GammaHat → R1,
  update : R1 → GammaHat → GammaHat
}
```

E's bundle is essentially two such lenses (one per slot) plus a consistency law constraining their composition. The joint representation here is:

```
GammaHat ≅ Pullback(view_R1, view_R3)
```

with the destructors of B factoring through the lens views.

**Pros:** Categorically cleaner. The pullback structure is explicit. The consistency law is a property of the lens pair, not a side artifact. Generalizes naturally to bundles of arbitrary cardinality.

**Cons:** Lens algebra is heavier vocabulary than the user may want at the design stage. Also, lenses are bidirectional by default (you can write through `update`), but B's destructors are observational — they don't write back. A bundle that supports a `timestep` destructor needs more than lens views; it needs an evolution operator on the bundle state itself, which is a coalgebra step, not a lens operation.

### My recommendation: Framing 1, with the witness promoted to a destructor.

The lens framing is elegant but mixes two different ideas (observation and update) in a way that doesn't map cleanly onto the temporally-evolving γ̂. The codata framing maps cleanly: destructors are the public surface, the bundle is the private state, the coalgebra step (`timestep`) is the natural update operator.

The one modification I'd make to Framing 1 is to **promote `consistency_witness` to a B destructor**:

```
GammaHat = {
  apply, density, trace, eigendecomp, timestep, restrict, basis_change,
  consistency_witness : () → Witness    -- new destructor
}
```

For a single-encoding implementation of B, `consistency_witness` returns a trivial witness (e.g., "encoding matches itself, gap = 0"). For an E-backed implementation, it returns the real bundle gap. This way the destructor signature is uniform across implementations, but bundle-backed implementations carry real information. **The destructor exists; what it returns depends on the carrier.** This is exactly how good codata APIs handle implementation-dependent state — expose the question, let the answer carry the structure.

---

## Question 4: Where are the impedance mismatches?

### Mismatch 1: Opacity vs. structural visibility.

B's whole stance is "γ̂ is opaque; only destructors are visible". E's whole stance is "γ̂ is a synchronized bundle, and the consistency witness is part of its identity". These are genuinely in tension.

Resolution: B's opacity is about **encoding**, not about **state-shape metadata**. The witness is metadata, not encoding. Exposing the witness as a destructor (per Question 3) doesn't break opacity any more than exposing `trace` does — both are observational, both are encoding-independent at the type level, both happen to have implementation-dependent computational content.

But there's a residual mismatch. Bundle cardinality — "is this a 1-slot, 2-slot, or 3-slot γ̂?" — is also state-shape metadata, and B has no natural slot for exposing it. You could add `bundle_shape : () → BundleSpec` as a destructor, but now B is leaking implementation details that callers might start branching on, which would calcify what should be a private choice. The honest move is to **leave cardinality private** and only expose the witness, which is the part downstream consumers actually need.

### Mismatch 2: Coalgebraic fixed points vs. write-through/write-back update.

B says self-consistency is a coalgebraic fixed point: `γ̂_{n+1} = F(γ̂_n)` until `γ̂_{n+1} ≈ γ̂_n` under bisimulation. The iteration lives at the level of `GammaHat → GammaHat`.

E says updates have policies: write-through (every change updates both slots immediately), write-back (changes go to one slot, the other is refreshed lazily), deferred-reconciliation (slots drift, the witness tracks drift, reconciliation happens at chosen sync points).

These don't conflict, but they live at different levels. B's fixed-point iteration is **between successive γ̂ values**; E's update policy is **within a single γ̂ value, between its slots**. The mesh is fine as long as:

```
bisimilar(γ̂_n, γ̂_{n+1})  implies  reconciled(γ̂_{n+1})
```

i.e., B can't declare convergence while E's bundle is still mid-reconciliation. This is a soundness condition on the joint system, not a deep conflict.

### Mismatch 3: Bisimulation vs. operator-norm consistency.

B's notion of "equality" is observational: two γ̂s are equal iff they agree on all destructors. This is a logical/behavioral notion.

E's consistency invariant is metric: the two slot decodings should agree to within some operator-norm bound. This is a numerical/topological notion.

**Can they be unified?** They have to be related but not identified. The natural bridge is:

```
ε-bisimilar(γ̂_1, γ̂_2)  iff  ∀d ∈ destructors. |d(γ̂_1) - d(γ̂_2)| ≤ ε(d)
```

i.e., quantitative bisimulation. E's operator-norm bound on slot disagreement is a *sufficient condition* for ε-bisimulation of slot views, for some ε derived from the bound. So E's consistency invariant **implies** an approximate B-bisimulation between the two views of the bundle, but it doesn't replace the bisimulation notion at the B level.

Unifying them prematurely would over-commit. Keep them distinct, and provide the implication. The implication is itself a destructor-derivable property — given `consistency_witness`, you can compute the ε.

### Mismatch 4: Per-call dispatch vs. destructor extensionality.

A B-style destructor `density(r)` should be a function of γ̂ and r only. But E dispatches it to the cheapest slot, and "cheapest" can depend on history (which slot is currently fresher, whether the bundle is mid-reconciliation, what the cost model said yesterday).

If the two slots disagree by ε > 0, then `density(r)` is **history-dependent**: same γ̂, same r, possibly different answers depending on dispatch state. This breaks pure functional extensionality of B's destructors.

Resolution: B's destructor laws must be stated modulo ε, not exactly. This is the price of E's flexibility, and it's a real price. Downstream layers — the staging layer, the e-graph optimizer — must be aware that destructor results have noise bounded by the witness, not exact equality. This is a genuine mismatch that the hybrid design has to confront.

---

## Question 5: Does the 5-layer placement work?

Currently:

```
1. INTERFACE      → B
2. STAGING        → A
3. OPTIMIZATION   → C
4. RUNTIME REPR   → E
5. SUBSTRATE      → D
```

B is layer 1 (interface), E is layer 4 (runtime representation), separated by A (staging) and C (optimization).

### Is the separation real or artificial?

I think the separation is **real but easy to misread**.

The real content: B is the **specification**, E is the **default implementation**. A and C are not "between" them in any meaningful operational sense — A and C are **transformations** that operate on B-typed expressions before they get evaluated against E-backed state. Specifically:

- A takes a B-typed expression like `apply(timestep(γ̂, dt), v)` and produces a structured term tree.
- C takes the term tree and applies cost-aware rewrites that respect B's destructor laws.
- The rewritten term is then evaluated against an E-backed γ̂.

So the call graph is: caller writes B → A stages it → C optimizes it → E executes it. B and E are at opposite ends of this pipeline because they have opposite roles: B is the contract callers see, E is the state that fulfills it. A and C live between them because they're the **planner** layer.

### Should B and E be merged?

I think **no**, for one strong reason: there should be more than one implementation of B. Single-encoding implementations are useful for testing, for tiny problems where the bundle overhead doesn't pay, for theoretical analysis where you want a pure F-coalgebra without storage complications. An e-graph-backed implementation of B is conceivable (γ̂ as an e-class, destructors as extract-and-evaluate against the cheapest representative) — that's a different concrete carrier for the same B interface. If you merge B and E, you lose the ability to swap carriers.

**B is the type; E is one of its inhabitants.** Merging them is a type error.

But there is a real risk in the current layering description: it makes E look like infrastructure (layer 4, near the substrate) when it's actually the **default canonical implementation** of B (layer 1). The conductor's diagram might benefit from labeling E as "default carrier" rather than "runtime representation", and noting that the layer structure reflects the **pipeline**, not the **type hierarchy**.

### Is E the canonical implementation, or just one of many?

Alternative implementations of B:

- **Single-encoding (R1-only or R3-only) carrier.** Trivial to write, no consistency machinery. Good for cases where one encoding dominates.
- **E-graph-backed carrier.** γ̂ is an e-class; destructor calls extract a representative and evaluate. Good when many destructors are called and rewrite-based reasoning is more valuable than caching multiple slots.
- **Lazy / on-demand carrier.** γ̂ stores only one encoding; converts on demand and discards. Good when memory is tight and most destructors are rare.
- **E (the pullback bundle).** Stores multiple encodings synchronized via a consistency witness. Good when destructor workload is mixed and conversion cost dominates.

E is **the right default** when the workload mixes destructors that favor different encodings and when storage is cheap enough to pre-pay |bundle|× the memory. That's the working assumption for this project, so E is the canonical default — but B exists prior to and independent of E, and other carriers should be welcome.

### Final structural recommendation.

Treat layer 4 as "**carrier**" rather than "runtime representation", and explicitly note that E is the default carrier choice. The 5-layer diagram becomes:

```
1. INTERFACE      → B           (specification)
2. STAGING        → A           (terms over B)
3. OPTIMIZATION   → C           (rewrites over A's terms)
4. CARRIER        → E (default) (implementation of B; others possible)
5. SUBSTRATE      → D           (each slot of E is a TN node)
```

This makes the type/implementation split visible in the layering itself, rather than burying it.

---

## Summary

B and E are not peers; they are interface and carrier. The mesh is sharp: E lives inside B's destructors, B's destructor menu informs E's bundle shape, E's bundle shape limits what B can expose efficiently. The main impedance mismatches are (a) opacity vs. exposing the witness — resolved by promoting the witness to a destructor; (b) per-call dispatch breaking exact extensionality — resolved by stating destructor laws modulo ε; (c) bisimulation vs. operator-norm consistency — kept distinct, connected by the implication that E's invariant entails quantitative B-bisimulation. The 5-layer placement is real, not artificial, because the layers describe a pipeline; but the diagram should label layer 4 as "carrier (E default)" to make clear that B is the type and E is one of its inhabitants — the canonical one for this project's workload, but not the only valid one.

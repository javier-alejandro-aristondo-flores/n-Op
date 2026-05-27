# Mesh Analysis: B (Codata) and C (E-graph with Saturation)

## Preliminary framing

Before diving in, let me pin down what B and C actually *are* as computational structures, because the mesh question depends on getting this right.

**B (codata) treats γ̂ as a black box defined by an interface:**
```
interface Gamma {
  apply(ψ: State) → State
  density(r: Point) → Scalar
  trace() → Scalar
  eigendecomp(k: Nat) → Stream[(Scalar, State)]
  timestep(dt: Time, H: Hamiltonian) → Gamma
  restrict(S: Subspace) → Gamma
  basis_change(U: Unitary) → Gamma
}
```
Two `Gamma` values are equal iff every finite composition of destructors produces equal observations. There is no "what γ̂ *is*" — only "what γ̂ *does*."

**C (e-graph) treats γ̂ as a term in a free algebra modulo a rewrite system:**
```
type Term = NodeId
type ENode = (Operator, List[EClassId])
type EClass = Set[ENode]            -- all terms proven equivalent
type EGraph = (Map[EClassId, EClass], UnionFind)
type Analysis a = EClass → a         -- semilattice-valued
type CostFn = (Operator, List[Cost]) → Cost
extract(eg, eid, costFn) → Term      -- pick cheapest representative
```
Two `Term`s are equal iff `find(eg, t1) == find(eg, t2)` after saturation under the rewrite system R.

These are very different objects. The whole question is whether they compose, and where the seams fall.

---

## Question 1: How do B and C MESH?

**The natural boundary is the WRITE PATH versus the READ PATH.**

B owns reads. The user of γ̂ never sees terms, e-classes, rewrite rules, or extraction. They call `apply`, `density`, `eigendecomp`, etc. The codata interface is the only contract the rest of the system depends on.

C owns staging. Before any destructor call commits to an execution strategy, the *expression* that would produce the answer to that call can be lifted into an e-graph, saturated under a rewrite system, and an extracted (cheapest) representative compiled down to whatever the substrate runs.

Concretely, the mesh looks like this:

```
                ┌─────────────────────┐
   user code →  │  B: destructor call │  →  observation
                │  γ̂.density(r)        │
                └──────────┬──────────┘
                           │ (deferred / staged)
                           ▼
                ┌─────────────────────┐
                │  C: e-graph         │
                │  build → saturate → │
                │  extract            │
                └──────────┬──────────┘
                           │ (extracted plan)
                           ▼
                ┌─────────────────────┐
                │  substrate          │
                │  (D / E layers)     │
                └─────────────────────┘
```

**Directionality of flow:**

- **Down (B → C):** the *signature* of the destructor call plus the *expression* of γ̂ that the handler would evaluate. The handler in B doesn't itself contract anything; it constructs a term `t : Term` and hands it to C with a query: "I need the result of `density(t, r)` — give me the cheapest plan."
- **Up (C → B):** an extracted plan, typed at the destructor's return type. B presents that plan's output to the caller. The caller never knows C existed.

**C is BENEATH B, not above and not sideways.** B is the only public surface. C is one of (potentially several) implementation strategies B can choose. The codata interface remains opaque; the user cannot tell whether B is dispatching to a hand-rolled handler, a tensor network contraction, or a C-extracted plan.

This is the *honest* placement, and it matches the proposed hybrid. But it has costs we'll come back to under impedance mismatches.

**One subtlety:** the boundary is not at every destructor call. It's at *staged regions* — a chunk of code that wants several observations from the same γ̂, and is willing to let the system batch them. A single `density(r)` call doesn't justify e-graph construction. A simulation loop that wants `density` at 10⁶ grid points after each timestep does.

---

## Question 2: Can one CONTROL or INFORM the other?

**B's interface constrains what C can optimize. C informs B's handler choice within that envelope.**

Concretely:

**B → C constraint:** every C-rewrite must preserve the observational equivalence B promises. If B's contract says `γ̂.trace()` returns a Scalar, then any e-graph rewrite of the term that computes that scalar must yield the same scalar (up to whatever ε B's contract specifies). This is strong. It means C's rewrite system R is *not free*; R is a subset of `{(l, r) | ∀destructor d. d(l) ≈ d(r)}`. Bisimulation acts as the soundness criterion for e-graph rewrites.

This is a real constraint and it has bite. Examples:

- A rewrite like `γ̂.basis_change(U).basis_change(V) ⇒ γ̂.basis_change(U·V)` is sound: any subsequent destructor sees the same observation.
- A rewrite like `γ̂.restrict(S).density(r) ⇒ if r ∈ S then γ̂.density(r) else 0` is sound conditionally.
- A rewrite like "replace dense storage with low-rank approximation" is *not* sound under exact bisimulation. It's only sound under ε-bisimulation, which means C needs to know B's tolerance budget.

This last point is critical: B's bisimulation may be exact or ε. C must be parameterized over which.

**C → B inform:** at staging time, C can tell B "if you let me see N+1 calls together, I can give you the answer cheaper than N+1 separate handler dispatches." This is the *batching dividend*. The mechanism is a typed staging API:

```
stage : (Gamma → a) → Staged a
run   : Staged a → a    -- triggers e-graph build/saturate/extract
```

Inside `stage`, destructor calls don't execute; they construct terms. `run` hands the term forest to C, gets back an extracted plan, executes it.

So the directionality is: **B's contract bounds C's rewrite system; C's cost-driven extraction picks among B-compatible implementations.** Neither dominates; both are needed.

There's also a third channel that's easy to miss: **C can inform B about which destructor calls are likely cheap.** After saturation on a staged region, C knows the cost of every observation it has terms for. B could expose a `cost_estimate(d)` destructor of its own that delegates to C. This is borderline — it leaks optimization information through the interface — but it's useful for adaptive consumers (e.g., a solver that prefers cheap observations).

---

## Question 3: What's the natural JOINT REPRESENTATION?

**Bisimulation and e-class equality are NOT the same concept. They live at different points in a chain.**

Let me be precise:

- **E-class equality** is *syntactic equality modulo rewrites*. Two terms `t1, t2` are e-class equal iff there's a proof of equivalence using R. It is a *generated* equivalence, decidable up to saturation budget.
- **Bisimulation** is *observational equality*. Two coalgebra states `s1, s2` are bisimilar iff for every destructor `d`, `d(s1) ≈ d(s2)` (recursively). It is the *finest* observation-preserving equivalence, in general undecidable.

The relationship is `e-class equality ⊆ bisimulation`. C's rewrite system R is *sound* w.r.t. B iff every rewrite `l ⇒ r` in R preserves bisimulation. C's rewrites are *incomplete* w.r.t. bisimulation iff there exist bisimilar terms that R cannot prove equal. In practice R is always incomplete; that's fine.

This relationship suggests a joint representation:

```
type Joint = {
  egraph    : EGraph,                        -- C's state
  realize   : EClassId → Handler,            -- B's handler per e-class
  bisim_eq  : (EClassId, EClassId) → Maybe Proof,  -- bisimulation oracle
}
```

The intended invariant: if `find(egraph, t1) == find(egraph, t2)` then `bisim_eq(c1, c2)` is `Just _`. The converse need not hold.

**Why this is the right joint object:**

1. The e-graph carries C's accumulated equivalence knowledge.
2. `realize` per e-class is B's handler — given an e-class, what's the cheapest way to *answer destructor queries* about that e-class? This is the bridge: each e-class has *one* canonical handler that responds to destructors.
3. `bisim_eq` is the soundness audit channel. New rewrites added to R must be verified against `bisim_eq` (in design time, not runtime).

The joint structure makes explicit what each layer owns:
- C owns the e-graph and the rewrite system.
- B owns the handler-per-e-class realization.
- The arrow `EClassId → Handler` is the seam.

**But here's the honest part:** this joint object is *cleaner conceptually than it is operationally*. In practice, you don't want a handler per e-class — you want a handler per *extracted representative* of an e-class, and the choice of representative is cost-driven and consumer-dependent. So the actual seam is:

```
realize : (EClassId, ConsumerProfile) → Handler
```

where `ConsumerProfile` encodes which destructors the consumer cares about and at what precision. This breaks the clean one-to-one correspondence between e-classes and handlers. Each e-class has *many* handlers depending on who's asking.

Which means: **bisimulation and e-class equality are different. The joint representation is a stratified one (e-graph below, handler-realization above), not a unified one.**

---

## Question 4: Where are the IMPEDANCE MISMATCHES?

There are five real ones, in roughly decreasing severity.

### 4.1. Opacity vs. exposure

B's contract says: *don't look inside γ̂*. C's mechanism *requires* looking inside — it must see the term structure to rewrite it.

The resolution is that C doesn't look at *γ̂'s internal state*, it looks at *the expression that produced γ̂*. So as long as γ̂ is *constructed* through algebraic operations (`build_from_orbitals`, `basis_change`, `restrict`, `evolved_from`), C can see those constructors. But if γ̂ is constructed by a process that's already opaque (e.g., "the output of an iterative self-consistency solver"), C only sees that single constructor and has nothing to rewrite.

This is a real loss of optimization opportunity. The mitigation is: B's *constructors* (the categorical-dual of destructors) should be as algebraic as possible. Hidden monolithic constructors starve C.

### 4.2. Infinite / lazy destructors

B's destructors can return streams: `eigendecomp(k: Nat) → Stream[(Scalar, State)]` — a lazy enumeration. C's e-graph is a finite data structure. Saturation over rules involving streams doesn't terminate naively.

The resolution is that C operates on *staged* prefixes: the user requests `take(k, eigendecomp(γ̂))` and C optimizes the bounded computation. C cannot saturate over a destructor that hasn't been concretized to a finite query.

The mismatch is real: any B-destructor that returns an unbounded structure must be *projected* to a bounded query before C can touch it. C does not optimize streams; it optimizes finite plans that produce finite prefixes of streams. This means a chunk of B's expressiveness (lazy, infinite, online observations) is *outside C's reach*.

### 4.3. Compile-time vs. runtime

C is built for compile-time: build the e-graph, saturate until quiescence or budget, extract once. B is runtime: destructor calls happen during execution, including during long-running time evolution where γ̂ is *changing* at every step.

The honest reconciliation is that C operates *per staged region*, not globally. Each staged region is a mini-compile: build, saturate, extract, execute. The e-graph is discarded (or partially persisted) afterward.

But this means C *cannot* maintain a global, ever-growing e-graph of all γ̂s ever seen. The proposed hybrid implicitly acknowledges this by labeling C "OPTIONAL OPTIMIZATION." The mismatch with B is that B's `timestep` destructor produces a *new* γ̂ at each step, which would invalidate large parts of any persistent e-graph. So:

- A staged region inside a single timestep: C is appropriate.
- A staged region across many timesteps: C is wrong, because the rewrite rules involving γ̂ change with γ̂.

This bounds C's role sharply.

### 4.4. ε-equality and tolerance budgets

B's bisimulation can be exact or ε-tolerant. C's e-class equality is a Boolean union-find: two things are equal or they're not.

If B is ε-tolerant, then rewrites in R might be ε-sound but exact-unsound. Folding them into a Boolean e-graph loses the ε. Composition of ε-sound rewrites can compound error in ways the e-graph doesn't track.

Mitigations exist (interval analyses, e-class-level ε analyses) but they're awkward bolt-ons. This is C's known weak spot.

The honest statement: **if B's contract is "exact bisimulation," C is straightforward. If B's contract is "ε-bisimulation," C needs error-tracking analyses that complicate every rewrite.** The hybrid should pick one regime for the interface and stick with it.

### 4.5. Self-consistency / fixed points

B handles self-consistency (Ĥ[γ̂]) natively via coalgebraic fixed points: γ̂ = `fix(λγ. step_with_H(H[γ], γ))`. The coalgebra has a notion of "the bisimulation up to fixed point."

C handles it by allocating fresh e-classes per iteration with ε-merge convergence detection: each iterate is a separate e-class; when consecutive iterates are ε-close, declare them merged.

These are *different mechanisms with different semantics*:

- B treats the fixed point as a single mathematical object; bisimulation includes "two iterates of a contractive map at distinct steps are bisimilar to the limit."
- C treats each iterate as a distinct term that *might* eventually be proven equal; the merge is a *decision*, not a discovery.

Can they coexist? Yes, but B should *own* fixed-point semantics and use C only inside a single fixed-point iteration to optimize the per-step computation. If C tried to span multiple iterations, the e-graph would grow without bound and the merge logic would conflate things B's bisimulation would correctly separate.

This means: **B's self-consistency is strictly preferable when they're paired.** C plays inside each step, not across steps.

---

## Question 5: In the proposed 5-layer hybrid, does the placement of B and C work?

Mostly yes. The placement is:

```
INTERFACE        → B
STAGING          → A (typed term algebra)
OPTIMIZATION     → C (optional, saturation-time)
RUNTIME REP      → E (pullback bundle)
SUBSTRATE        → D (tensor network)
```

**What works:**

The interface/optimization separation is the right shape. B is what users see; C is one tool among the optimization layer's toolset. C being labeled "optional" matches its real status — it earns its keep only when staged regions are large enough.

The fact that A sits between B and C is also right, and resolves a question that would otherwise be sharp. C cannot operate directly on B's destructor signatures as a black box — it needs a term structure to rewrite. A provides that term structure. So the actual flow is:

1. User calls a B destructor in a staged region.
2. The destructor handler constructs an A-term representing the computation.
3. The A-term is lifted to a C e-node.
4. C saturates the relevant subgraph.
5. C extracts a cheapest A-term.
6. That A-term is realized on E/D substrates.
7. The substrate produces an observation; B returns it.

In this flow, C operates on A's terms, not on B's destructor signatures directly. The destructor signatures are the *boundary conditions* (input type, output type) that constrain what A-terms are well-formed.

**What I want to flag:**

**(a) C should not be in the same vertical column as B.** The diagram suggests a tower, but C is really a *parenthetical* optimization step in the path from staging to runtime. Mentally I'd draw C as a side-branch:

```
B  →  A  →  (C?)  →  E  →  D
              ↓
        optimization
```

Otherwise people will think every destructor call goes through saturation. It doesn't.

**(b) The "C operates on B's signatures vs. beneath them" question** is the right one. The answer is: **C operates on A-terms whose well-typedness is determined by B's signatures.** So C is *typed by* B but *operates on* A. This is the cleanest way to say it. If C tried to operate on B's signatures directly, it would have no term to rewrite (codata has no syntactic structure). If C operated entirely beneath B without seeing B's types, it would produce extractions that don't fit B's contract (wrong return types, wrong tolerance regime).

**(c) Should C be more tightly bound to B?** No. Tighter binding would force every B destructor call through saturation, which would be catastrophic for the long-running time-evolution case (impedance mismatch 4.3). The current looseness is correct.

**(d) The handler-per-e-class seam** described in Q3 is the one place the design should pin down explicitly. Right now it's implicit. The seam type:

```
extract : (EGraph, EClassId, ConsumerProfile) → Plan
realize : Plan → Handler           -- a B-handler for the destructor query
```

…is the contract between layers. Both parts need to be in the design.

**(e) Bisimulation as the soundness audit for C's rewrite rules** should be a *design-time* property of R, not a runtime check. This is non-negotiable: if R contains unsound rewrites, the whole hybrid is broken. The design should specify how each rule in R is justified against B's bisimulation contract — by hand, by proof, by property-test, but specified.

---

## Honest summary

B and C mesh well *within a bounded role for C*. The boundary is staged regions; the directionality is B-on-top with C-beneath as one implementation choice; the joint object is stratified (e-graph below, handler realization above), not unified.

The mismatches are real but manageable: opacity-vs-exposure is fine as long as B exposes algebraic constructors; lazy destructors are outside C's reach and that's accepted; ε-tolerance requires either committing to a regime or accepting awkward e-graph analyses; fixed-point semantics belong to B with C playing inside individual iterations.

Bisimulation and e-class equality are *not the same notion*. E-class equality is a sound under-approximation of bisimulation. The hybrid works precisely because they're different — C provides decidable, batchable equivalences; B provides the gold-standard observational contract. Conflating them would break both.

The 5-layer placement is right *if* C is understood as a side-branch optimization between A-staging and E-runtime, not as a vertical layer in a tower. And *if* the handler-per-e-class seam and the rewrite-soundness audit are made explicit.

Where I'd push back on the design: the proposed hybrid currently leaves implicit (i) the staging-region scoping rules that bound C's e-graphs, (ii) the ε-tolerance regime of B's bisimulation, and (iii) the soundness audit of R against B. All three need to be first-class design artifacts before B-and-C can be claimed to mesh cleanly.

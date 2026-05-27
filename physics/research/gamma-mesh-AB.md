# Mesh Analysis: A (typed term algebra) and B (codata) for γ̂

A note before the analysis: the two framings are widely advertised as duals, but duality in category theory is a strong claim and a weak guarantee. Dual structures interlock cleanly when you only use the universal interface (constructors on one side, destructors on the other); they fight as soon as you ask for things that live outside that interface — sharing, mutation, equational reasoning, identity. γ̂ in this project demands all four. So the report's structure: first describe the clean mesh, then catalogue every place it stops being clean, then critique the conductor's placement of the two layers.

---

## 1. How A and B Mesh

The natural mesh is the **fold**. A defines an inductive type `Gamma` (an initial algebra) — call its constructors `pure_R1`, `pure_R3`, `combine`, `evolve`, etc. B defines a record of destructors:

```
GammaCodata = {
    apply        : Vec -> Vec
    density      : Point -> Scalar
    trace        : Scalar
    eigendecomp  : Stream<EigenPair>
    timestep     : Duration -> GammaCodata
    restrict     : Region -> GammaCodata
    basis_change : Basis -> GammaCodata
}
```

The classical recipe — going back to Hagino's categorical work on data/codata and made famous by attribute grammars — is that any function `Gamma -> GammaCodata` is uniquely determined by an algebra structure on `GammaCodata`. Concretely, you give one definitional clause per A-constructor saying how to produce a `GammaCodata` from the children's already-computed `GammaCodata` values. The induced map is a fold, also called a catamorphism. So B's interface sits, in the clean case, *exactly* on top of A's grammar, and the implementation is a single mechanically-derived recursion scheme.

**Flow of information.**
- **A → B:** structure flows up. The constructor case at the root of an A-term tells you which strategy implements each destructor. For a `pure_R1` node, `apply` is matrix–vector via the low-rank factors; for a `pure_R3`, it's a sparse mat-vec; for `combine(γ₁, γ₂)`, it's the sum of the children's `apply`s.
- **B → A:** *nothing*, in the clean fold picture. B-clients never see A-terms. This is the whole point of codata: opacity.
- **Shared:** the carrier type `Gamma` (A-internal) and the operation signatures (B-defined). The destructor *signatures* are public; the algebra clauses that implement them are private to whoever owns the A-side.
- **Private to A:** the term grammar, encoding tags, rewrite rules, and any normalization machinery.
- **Private to B:** any handler state (caches, materialization decisions, the policy that decides when to reify a deferred subterm).

In the conductor's 5-layer stack, A is the staging/expand layer and B is the interface layer, and they're advertised as adjacent. Under the clean fold picture, adjacency is correct: the interface is just "the canonical fold of A into the destructor record." Nothing should sit between them.

**But the clean picture is only clean for first-order, single-pass, value-typed destructors.** Each of the following breaks it:

- `timestep : Duration -> GammaCodata` returns another `GammaCodata`. That means destructors aren't reducing to a fixed value type; they're corecursive. A fold doesn't produce that; you need a hylomorphism, or you need to interpret destructors against an A-term and return a *new* A-term, then re-wrap it. The boundary is no longer "A-term in, scalar out"; it's "A-term in, A-term out, re-wrapped as opaque."
- `eigendecomp : Stream<EigenPair>` is observably infinite. Folds don't natively produce streams; you need lazy / corecursive support, which means the A grammar has to be cocomplete enough (let-bindings, fix-points) to *name* the stream rather than enumerate it.
- `restrict`, `basis_change` are A-term transformations dressed up as destructors. Saying "B is the public interface and A is the private substrate" is not quite right here: half the destructors are really *rewrite operations on A* with the result re-presented through B.

So a more honest statement of the mesh: **B's interface sits on top of A, but several of B's destructors are not folds; they are rewrites on A composed with the re-wrap.** The boundary is one-way only for the destructors that genuinely reduce structure to a value (`trace`, `density(r)`, `apply`). For the structure-preserving destructors (`timestep`, `restrict`, `basis_change`), the boundary leaks: B's implementation lives inside A's rewrite system.

---

## 2. Control and Information Flow

There's a real directionality here, and it's the opposite of what the conductor's "B on top of A" picture suggests.

**A controls; B observes.** The agency lives in A's rewrite system. A's rewrites decide which encoding γ̂ currently sits in (R1, R2, R3, or a deferred composition). A's typing rules decide which operations are even legal. A's normalization decides when `evolve(t₁) ∘ evolve(t₂)` collapses to `evolve(t₁+t₂)`. None of those decisions are visible through B — they happen before B is called, or in the closure that B's destructors invoke. From B's vantage, γ̂ is opaque and there are no decisions, only observations.

So in the standard pattern: **A is the *interpreter*, B is the *interface to the interpreter*.** B has no agency. It cannot choose how γ̂ is encoded, cannot pick a rewrite, cannot decide when to materialize. All of those are A's job.

This matters because the conductor's stack lists C (e-graph) and E (pullback bundle) as separate layers below A — which implies that representational decisions happen *below* A. That's a category error. In a clean A+B mesh, A's term grammar is *exactly* the language in which representational decisions are made. C and E are tools A might invoke; they're not strata above which A floats.

**Is there reverse information flow?** In principle, yes: B's *observations* can inform A. If a client only ever calls `trace` and `density(r)` for r in a small region, A's rewriter can specialize accordingly. This is profile-driven rewriting. But realizing it requires B to *report* observation patterns back to A — and now B is no longer opaque; it's leaking usage information. This is the same issue that bedevils Haskell's `seq`: opacity is only opacity until you need optimization, and then you need a back-channel.

**Where the agency really sits in the proposed hybrid.** If A controls and B observes, then naming B the "interface layer" sitting *above* A is reasonable but should not be confused with B *controlling* A. In particular, when self-consistency arises (the Ĥ[γ̂] fixed-point question), the agency to find a fixed point cannot live in B alone, because B can't see the dependency. It also cannot live in A alone, because A's term-grammar fold has no fixpoint operator unless you add one. The agency lives in *the extension of A with a let/fix construct*, with B observing the outer fixed-point.

---

## 3. Joint Representation

If you collapse the apparent duality into a single structure, you get one of two things, depending on which side you privilege.

**Option 1: A with a "view" extension (constructor-privileged).** Extend A's grammar with no new γ̂-constructors but with a coalgebraic *view operation* — a function `view : Gamma -> CodataRecord` defined by the canonical fold. Then there is only one object (the term), and B is a derived view of it. This is what the clean mesh in §1 amounts to.

Signature sketch:

```
data Gamma where
    PureR1     : LowRankFactors -> Gamma
    PureR3     : SparseLocalized -> Gamma
    Combine    : Gamma -> Gamma -> Gamma
    Evolve     : Duration -> Gamma -> Gamma
    Restrict   : Region -> Gamma -> Gamma
    Let        : (Gamma -> Gamma) -> Gamma    -- HOAS, for sharing
    Fix        : (Gamma -> Gamma) -> Gamma    -- for self-consistency

view : Gamma -> GammaCodata
view = fold algebra
  where algebra : F Gamma GammaCodata -> GammaCodata
```

Pros: rewrite identities are first-class. `view ∘ rewrite ≡ view` is a theorem (a refinement of rewriting being sound). Sharing and fixpoint are explicit constructors. B is fully derivable.

Cons: every B-style destructor that returns a `Gamma` (timestep, restrict, basis_change) has to be *defined as a rewrite*, not as a fold target. The fold algebra has to know how to absorb a `Restrict` constructor for every encoding, which is the P×O problem A already had. Putting B on top doesn't help; it just renames it.

**Option 2: B with an internal A representation (destructor-privileged).** Treat γ̂ as a coalgebraic object whose *state* happens to be an A-term, but the state is hidden:

```
GammaCodata = ∃ State. {
    state    : State                  -- secretly an A-term, hidden
    apply    : State -> Vec -> Vec
    density  : State -> Point -> Scalar
    trace    : State -> Scalar
    timestep : State -> Duration -> ∃ State'. (State', destructors')
    ...
}
```

This is the **object-oriented / final-coalgebra** encoding. The A-term exists, but only as a private implementation detail of a `GammaCodata` value. Rewrites are bisimulation-preserving transformations on the hidden state.

Pros: opacity is total; clients cannot distinguish R1 from R3 from a deferred `Evolve` chain unless they call destructors. This is what B was after originally.

Cons: rewrite *identities* become invisible. They're now properties of the bisimulation relation on hidden states. You can't say "use the rewrite `R1 ∘ Evolve(t) ↝ R1'` to optimize" without breaking opacity, because the optimizer needs to see the constructor structure. Coalgebraic rewriting exists (e.g., the work on coalgebraic logic programming), but it's machinery that doesn't pay for itself unless you really need opacity for security or modularity, which γ̂ doesn't.

**A third option, and probably the right one: keep them separate, and define a coercion explicitly.** A is the language; B is one of several possible interpretations. There are others: a cost estimator, a serializer, a pretty-printer. None of these are "the interface to A"; they're all interpretations parameterized by an algebra. Treating B as primus inter pares is privileging it without reason. The honest joint representation is:

```
data Gamma = ...                       -- A's term type
class Interpret a where
    interp : Gamma -> a
instance Interpret GammaCodata where ...   -- B
instance Interpret CostEstimate  where ...
instance Interpret Serialization where ...
```

In this picture A and B are not adjacent layers; B is one of N satellites around A.

---

## 4. Impedance Mismatches

Five mismatches, in increasing severity.

**(a) Identity and sharing.** A's grammar is a tree by default; γ̂ in nonlinear closures (e.g., when γ̂ appears twice in `Ĥ[γ̂](γ̂)`) needs DAG-with-sharing. Without sharing, fold computes B's destructors twice on the same subterm. Standard fix: let-bindings in A's grammar, with hash-consing on construction. But now A's fold has to handle `Let`/`Var`, and B's destructors have to thread an environment. This isn't fatal; it's the usual cost of HOAS vs. de Bruijn vs. let-bindings. It's worth flagging because the clean fold story breaks the moment you have sharing.

**(b) Effects and corecursion.** B has destructors that produce streams (`eigendecomp`) and that return new `GammaCodata` (`timestep`). A pure fold returns a fixed type. You need either (i) a hylomorphism (anamorphism after catamorphism), which is fine but requires A to support codata constructors too — at which point the "A as initial algebra, B as final coalgebra" duality collapses into a mixed (mu-nu) framework, or (ii) you accept that some destructors are rewrites and route them differently.

**(c) Equational reasoning and observation equivalence.** A's rewrite system is *intensional*: it talks about term structure. B's only handle on equality is *observational*: γ̂₁ ≡ γ̂₂ iff every destructor agrees. These two are not the same. There exist A-terms that should be observationally equal but aren't related by any rewrite (because the rewrite system is incomplete relative to ε-equality of approximated representations). Conversely, there exist rewrites that don't preserve observation up to ε (they're algebraically valid but numerically destructive — basis changes that lose precision, for instance). Where do you adjudicate? The mismatch is fundamental: A wants term-rewriting equivalence; B wants bisimulation equivalence; the project's actual semantics is ε-approximate observational equivalence, which is neither. No coalgebra/algebra trick resolves this; it has to be handled by separate machinery (witnesses, error budgets).

**(d) Self-consistency.** Ĥ[γ̂] is a function from γ̂ to a Hamiltonian, and the system wants the γ̂ that's the ground state of Ĥ[γ̂(self)]. B handles this natively because final coalgebras have fixed points. A doesn't, unless you add a `Fix` constructor (which is "lifting A into a coalgebraic framework," as the prompt phrased it). The honest answer: A *needs an extension* — recursive let, or an explicit `Fix γ. ground_state(H(γ))` constructor — to express fixed points. Once you have it, fold-into-B yields B-fixed-points naturally. So A *can* be lifted into a framework where fixed points work, but it's an extension, not an interpretation. Pretending A in its base form covers this is wrong.

**(e) Encoding-choice policy.** B's documented weakness: "encoding-choice policy lives nowhere natural." The conductor's hybrid implicitly answers: it lives in A's rewrite system at expand-time. Is that true?

Partially. A's rewrite system encodes *legal* encoding choices and *normalization* preferences. It doesn't encode *cost-driven choice*, which depends on which destructors are about to be called, with what arguments, on what hardware. Cost is a coupling between A (what's there) and B (what's about to be observed). The policy lives **on the boundary between A and B**, not inside either. Saying "A holds the policy" papers over the fact that A doesn't see what B is going to be asked to do. Saying "B holds the policy" papers over the fact that B doesn't see A's structural choices. The honest answer is that there is a third object — a planner or scheduler — that consumes both A's structure and B's pending call pattern. In the conductor's hybrid this is hinted at by listing C (e-graph) as an "optional optimization" between them, but optionality doesn't dissolve the problem; either the planner is essential or the cost-driven mesh is incomplete.

---

## 5. The Proposed 5-Layer Hybrid: A as Staging, B as Interface

The conductor places:

```
INTERFACE (B) → STAGING (A) → OPTIMIZATION (C) → REPRESENTATION (E) → SUBSTRATE (D)
```

The relevant subjudgment is: A is immediately below B, with C optionally between A and E, and E above D.

**What works.** Putting B at the top is correct in one important sense: client code should not see A-terms. If a client computes `apply(γ, v)` and gets a vector back, the client shouldn't know whether γ was an R1 with cached factors or a deferred composition that just got materialized. This is interface stability, and it's a real win.

A directly below B is also correct in the sense that B's implementations *are* operations on A. Nothing should mediate them; the destructor record is the canonical fold of A.

**What doesn't work.**

*First, C and E shouldn't be "below" A; they should be options that A's rewrite system invokes.* A's grammar already includes encoding choices (R1, R3, deferred forms). E is the bundle representation, which is just one more constructor in A's grammar — `Bundle [R1_slot, R3_slot]` with a consistency witness. C is a tool A's rewrite system uses when normalization is hard. Putting them as strictly lower layers implies that data passes through them in sequence — but in the clean mesh, data lives in A's grammar throughout, and C and E are just *constructors* and *strategies* within it. Drawing them as layers below A imposes a passage-through-strata picture that doesn't reflect the algebra.

*Second, the "optional" qualifier on C is suspicious.* If A's rewriting is confluent and terminating for the rules you actually have, you don't need C — A's own normalization picks a normal form. If A's rewriting is not confluent (because there are cost-equivalent but structurally distinct choices), then you need C *always*, not optionally, because the choice between normal forms is precisely what's hard. "Optional optimization" reads like hedging on a structural decision.

*Third, the boundary between A and B is leakier than "adjacent layers" suggests.* Per §1, destructors like `timestep`, `restrict`, and `basis_change` are A-rewrites dressed as B-destructors. A clean stratification would push those *out of B* into A, so B has only value-returning destructors. That gives a cleaner mesh but a less useful B-interface. The conductor's hybrid hides this tension; it should be surfaced.

*Fourth, the absence of an explicit planner is the real gap.* Per §4(e), encoding-choice policy is not in A and not in B; it lives in the planner that consumes A's structure and B's pending call pattern. In the proposed hybrid, this planner is unnamed; possibly it's smuggled into "C as optional optimization," but C-as-equality-saturation doesn't have built-in call-pattern awareness, and the gap shows.

**Should A and B be rearranged or merged?**

Not merged. Per §3, merging them privileges one perspective at the cost of the other, and the honest joint representation treats B as one interpretation of A among several. Keep them distinct.

Not rearranged in the sense of "B below A" — that's just wrong, since B is the public interface.

But the picture should be redrawn so that A is not a layer with strata below it. A is the *language* in which γ̂ lives. B is a *view* of that language. C, D, E are *tools and strategies* the language uses internally — C as an alternative normalization engine, D as a value space, E as a particular family of constructors. Layered diagrams suggest data flows downward through filters, but A-terms don't flow downward; they get *interpreted* downward when (and only when) a B-destructor is called.

A more faithful picture, replacing the stack:

```
                              CLIENT
                                |
                                v
                          B  (destructors)
                                |
                                v   [canonical fold + planner]
                                |
                          A  (term grammar)
                              / | \
                             /  |  \
                       constructor families:
                             E (bundle)
                             plus single-slot R1/R2/R3
                       optional normalization tool:
                             C (e-graph)
                       value space for leaves:
                             D (tensor network)
```

In this picture A and B are still adjacent — the canonical fold is the boundary — but A is the trunk and C/D/E are branches rather than strata. The mesh between A and B is clean *given* this restructuring; it's awkward in the linear-stack picture because the linear picture forces a totally-ordered dependency that isn't there.

**Final verdict on placement.** A and B are placed in roughly the right relationship (B on top, A immediately under, communicating by fold). But the surrounding architecture — C/D/E as layers below A — is mismatched to how the algebra-coalgebra duality actually composes. The mesh is not elegant in the proposed hybrid; it's elegant in a fan-out architecture where A is central and C/D/E are A's tools. The conductor's stack works if you read it generously (treating "below" as "invoked by"), and breaks if you read it strictly (treating "below" as "data passes through"). Whether to redraw or rephrase is a presentation question; the conceptual fix is to stop calling C, D, E "lower layers" and start calling them components of A.

---

## Summary

A and B are duals in the technical sense: B's destructor record is the canonical fold of A's term type, and this gives a clean mesh for value-returning destructors. The mesh leaks for destructors that return new γ̂ values, for sharing under nonlinearity, for ε-approximate equality, and for fixed-point self-consistency. A controls; B observes; the agency lives in A's rewrite system, and B is one interpretation among several. The conductor's placement of B above A is correct, but the picture of C/D/E as layers below A misrepresents the relationship — they are tools A uses, not strata data flows through. The two real holes in the hybrid are an unnamed cost-and-call-pattern planner that lives on the A/B boundary, and the unacknowledged extension A needs (recursive let / fix) to handle self-consistency the way B handles it natively.

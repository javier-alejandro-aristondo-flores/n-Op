I'll research the e-graph framing for γ̂ thoroughly. Let me first read the available context files to ground my analysis.
I'll acknowledge the plan mode constraints. I'm in read-only research mode, which aligns perfectly with the task. The deliverable is a report returned as my final message, not file edits. Let me gather context.
I have enough context. Let me also peek at the relevant pieces of the implementation plan to confirm the broader design framing.
I have abundant context. Now let me write the structural report. I'll think through it carefully across the 10 sections and then produce the final deliverable.

The plan-mode constraint says I can write to a plan file. The task instructions explicitly say "Do NOT create files" and "Return your findings directly as your final assistant message". The task instructions take precedence over plan mode here because the task IS the research, the deliverable IS the report-as-message, and creating files would conflict with the conductor's parallel-agent orchestration. I'll return the report inline.

---

# Framing C — γ̂ as an e-class in an e-graph with cost-driven equality saturation

## 0. Setup and terminology in CS-only vocabulary

Throughout this report I treat γ̂ as a SELF-ADJOINT LINEAR MAP from a finite-dimensional vector space to itself, indexed by spatial coordinates (r, r'). The "Hilbert dimension" is just the dimension D of the underlying vector space — D is astronomically large (in plane-wave discretization, ~10⁵–10⁸), so any dense D×D representation is forbidden. We need γ̂ to be described by some compressed structure whose size is sub-quadratic in D.

The three encodings:
- **R1** (LOW-RANK SUM-OF-OUTER-PRODUCTS): γ̂ ≡ a list of pairs (cₙ, φₙ) where cₙ is a scalar weight and φₙ is a vector of length D. The set is small (rank K ≪ D).
- **R2** (BLOCK-DIAGONAL UNDER A DISCRETE TRANSLATIONAL SYMMETRY): γ̂ ≡ a finite map (k ↦ small self-adjoint matrix Γₖ) where the index set {k} has size Nₖ and each Γₖ has size Nᵦ×Nᵦ with Nᵦ ≪ D.
- **R3** (SPARSE IN A SPATIALLY-LOCALIZED BASIS): γ̂ ≡ a list of triples (i, j, γᵢⱼ) where (i, j) ranges over a CUTOFF-DETERMINED sparsity pattern, e.g. only (i, j) with |rᵢ − rⱼ| < r_c.

Operations: see the task brief. The e-graph framing claims γ̂ is not a value but a HANDLE into a shared DAG-with-equivalence-classes that simultaneously holds many encodings.

---

## 1. Representation

In the e-graph framing, γ̂ is literally an opaque integer: an **e-class ID** in a graph whose nodes carry data and whose edges express both subexpression structure (DAG edges) and provable equivalence (union-find edges).

The structural types (conceptual):

```
EClassID    = ℕ                          -- opaque handle
ENode       = Constructor × Vector[EClassID] × Payload
EClass      = Set[ENode]                 -- representations known equal
EGraph = {
  classes   : UnionFind[EClassID],       -- equivalence over IDs
  enodes    : Map[EClassID, Set[ENode]],
  hashcons  : Map[ENode, EClassID],      -- congruence closure
  parents   : Map[EClassID, Set[ENode]], -- back-edges for upward repair
  analyses  : Map[EClassID, Analysis]    -- abstract data per class (see §4)
}
```

The constructors that matter for γ̂:

```
LowRankSum     ( vecs : EClassID, scalars : EClassID )
BlockByMomentum( index_set : EClassID, blocks : EClassID )
SparseTriples  ( triples : EClassID, basis : EClassID, cutoff : Real )
BasisChange    ( transform : EClassID, gamma : EClassID )
UnitaryConj    ( U : EClassID, gamma : EClassID )
Apply          ( gamma : EClassID, v : EClassID )      -- γ̂·v
Compose        ( op_left : EClassID, op_right : EClassID )
Trace          ( gamma : EClassID )
Diagonal       ( gamma : EClassID )                    -- λr. γ̂(r, r)
Spectrum       ( gamma : EClassID )                    -- stream of (λ, v)
Projector      ( subspace : EClassID )
Sum, Scale, Identity, Zero, ...
```

Crucially, **γ̂ is not "a representation". γ̂ is the e-class ID that owns these representations as equivalent e-nodes.** A single e-class might at one moment contain:

```
EClass(γ̂_id) = {
  LowRankSum   (vecs=v_id, scalars=c_id),
  BlockByMomentum(index_set=K_id, blocks=B_id),
  SparseTriples(triples=T_id, basis=W_id, cutoff=10.0),
  BasisChange  (transform=F_id, gamma=γ̂'_id),         -- F·γ̂'·F†, derived
  Sum          (γ̂_alpha_id, γ̂_beta_id),               -- ⊕ of two halves
  ...
}
```

Each e-node references CHILD e-class IDs, not concrete data. The actual numbers (vectors, scalars, triples) live as leaves in their own e-classes — themselves opaque handles. So the e-graph stores γ̂ in a layered way: γ̂ ↦ encoding-e-node ↦ child-e-classes ↦ ... ↦ leaf e-classes holding genuine numerical containers.

The analyses field carries per-e-class abstract information that all members agree on: trace value, an upper bound on rank, a flag indicating whether self-adjointness is known to hold, an upper bound on operator norm, etc. (§4 details these.)

---

## 2. Encodings (R1/R2/R3)

In this framing all three encodings are **first-class** but their first-classness is at the e-NODE level, not at the e-CLASS level. They are SIBLINGS inside the same e-class.

- R1 manifests as a `LowRankSum` e-node. Its children are an e-class for the vector list and an e-class for the scalar list. The vector list itself might be encoded multiple ways (e.g. as a plane-wave-coefficient list or as a real-space sample list), so the vector list e-class is itself a multi-encoded thing.

- R2 manifests as a `BlockByMomentum` e-node. Its children are an e-class for the index set {k} and an e-class for the block-map (k ↦ Γₖ). The block-map e-class can ALSO host equivalent forms — e.g. each Γₖ might be itself LowRankSum-encoded if Γₖ is rank-deficient inside the small block.

- R3 manifests as a `SparseTriples` e-node. Its children include a basis e-class (the {ψᵢ}), a triples e-class, and a metadata field for the cutoff. The same γ̂ can appear in R3 with multiple cutoffs simultaneously — each cutoff is a different e-node but they live in the same e-class IF the e-graph also tracks an "approximately equal at tolerance ε" relation (see §6 caveat).

**Implicit vs first-class:** All three are equally first-class — the e-graph commits to none. The DISPATCH happens at extraction time, not at storage time. Extraction is a graph-walk that, given a cost function aware of the eventual consumer operation, picks one e-node per visited e-class to "materialize". The same γ̂ can be extracted as R1 for one consumer and R2 for another in the same program — different extractions, same e-class.

**Conversions are algebraic moves.** A conversion like "this LowRankSum equals this SparseTriples under the cutoff-induced basis projection" is recorded as a REWRITE RULE that, when fired during saturation, merges the two e-classes (or merges them with an attached error-witness if approximate; see §6).

Sample rewrite rules (in match-pattern → conclusion form):

```
(R1↔R2 under translational symmetry)
  match: γ as LowRankSum(vecs, scalars)
         where each vec ∈ vecs is labeled with momentum k (analysis says yes)
  add  : γ' = BlockByMomentum(index_set = K, blocks = group_by_k(vecs, scalars))
  merge γ with γ'

(R2→R3 by inverse momentum-to-real-space transform)
  match: γ as BlockByMomentum(K, B)
  add  : γ' = SparseTriples(triples = IFT∘B, basis = W, cutoff = ∞)
  merge γ with γ'

(R3 cutoff weakening)
  match: γ as SparseTriples(T, W, c)
  add  : γ' = SparseTriples(T_truncated_at_c', W, c') for c' < c, with witness ε
  ε-merge γ with γ'                                          (if ε-merging enabled)

(R1 rank truncation)
  match: γ as LowRankSum(vecs, scalars) with K e-nodes in vecs and
         scalars sorted descending in magnitude
  add  : γ' = LowRankSum(take_first_K'(vecs), take_first_K'(scalars))
  ε-merge γ with γ' under bound on tail energy
```

The key conceptual move: **encodings are not stored as alternatives behind a sum type; they are stored as parallel e-nodes in the same equivalence class.** Membership in an e-class is a positive assertion of equality, not a tagged choice.

---

## 3. Operations

For each operation in the task brief I'll describe how it is implemented in this framing. The shape is always the same: build (or look up) an e-node representing the operation, optionally trigger targeted saturation, then optionally extract — but often we just store the operation symbolically and defer extraction until a consumer demands a value.

### apply : γ̂ × Vector → Vector

Signature in the e-graph: `apply : EClassID × EClassID → EClassID`. It just returns the e-class ID of `Apply(γ̂_id, v_id)`. Materialization is deferred.

Once a downstream consumer demands the actual Vector value, extraction kicks in. Extraction visits the Apply e-class, chooses the cheapest e-node strategy. Equality-saturation has already populated rewrites of the form:

```
Apply(LowRankSum(vecs, scalars), v)
  → SumOver_n(Scale(scalars[n] · ⟨vecs[n], v⟩, vecs[n]))
                                       -- K inner products + K vector-axpys, O(K·D)

Apply(BlockByMomentum(K, blocks), v)
  → AssembleByK(λk. Apply(blocks[k], project_to_k(v)))
                                       -- decompose v into k-blocks, apply each
                                          Nᵦ×Nᵦ matrix, recompose. O(Nₖ · Nᵦ² + D)

Apply(SparseTriples(T, W, c), v)
  → Sum_{(i,j) ∈ T}(γᵢⱼ · ⟨ψⱼ, v⟩ · ψᵢ)
                                       -- O(|T|), with |T| linear in D for r_c-cutoff
```

Cost-driven extraction picks the rewrite whose materialized form has the smallest scalar cost given a cost function (§7). For a single random `v`, R1 is usually cheapest when K is small; if `v` itself is k-block-structured, R2 may dominate; if `v` is spatially localized, R3 may dominate. The e-graph itself doesn't decide — the cost function does.

### timestep : γ̂ × UnitaryOp × Δt → γ̂'

Implemented as a new e-node: `UnitaryConj(U_id, γ̂_id)` whose meaning is U·γ̂·U†. This produces a NEW e-class ID γ̂'_id. Saturation then fires:

```
UnitaryConj(U, LowRankSum(vecs, scalars))
  → LowRankSum(map(λφ. Apply(U, φ), vecs), scalars)
                       -- rotate each vector, preserve scalars. O(K · cost(U))

UnitaryConj(U, BlockByMomentum(K, B))
  → BlockByMomentum(K, map(λΓₖ. Conj(Uₖ, Γₖ), B))    if U is k-block-diagonal
                       -- otherwise this rule does not match

UnitaryConj(U, SparseTriples(T, W, c))
  → SparseTriples(NewTriples(T, U, W, c), W, c)       always applicable but expensive
```

The framework here is doing nothing magical — it just stores the timestep as a deferred computation that can be unfolded by the cheapest rewrite. If U is itself an exponential of a state-dependent self-adjoint operator (which it is — see §5), the U e-class itself contains multiple representations: Trotter splitting, Magnus series, etc.

### eigendecomp : γ̂ → Stream[(λ, v)]

The e-graph stores `Spectrum(γ̂)` as an e-class. Rewrites populate it:

```
Spectrum(LowRankSum(vecs, scalars))
  → IteratorFrom(
      For k in 0..K-1:
        emit (scalars[k], vecs[k])
      Then emit (0, basis_completion)
    )
                       -- only finite eigenvectors are the φₙ; the rest are zero eigenmodes

Spectrum(BlockByMomentum(K, B))
  → MergeSortedByEigenvalue(
      For each k: Spectrum(B[k])
    )
                       -- diagonalize each small Γₖ independently, merge streams

Spectrum(SparseTriples(T, W, c))
  → IterativeBuilder_via_Apply(γ̂)
                       -- the iterative procedure that builds a tridiagonal
                          projection of a self-adjoint linear map by repeated
                          application to a probe vector; one matvec per step
```

The key observation: **the eigendecomp e-node itself is opaque (it's just an e-class); the rewrites tell extraction how to compute it from a chosen child encoding.** Cost-driven extraction picks whichever spectrum-computation is cheapest given the structure of the current γ̂.

For R1, eigendecomposition is essentially free — the LowRankSum literally IS an eigendecomposition. For R2, eigendecomposition is the union of Nₖ tiny diagonalizations — embarrassingly parallel and cheap. For R3, you fall back on an iterative procedure that needs only apply(γ̂, v) and gives back the top-m eigenpairs in cost O(m · matvec_cost).

### density : γ̂ → RealFunction

`Diagonal(γ̂)` is an e-class. Rewrites:

```
Diagonal(LowRankSum(vecs, scalars))
  → λr. Sum_n scalars[n] · |vecs[n](r)|²

Diagonal(BlockByMomentum(K, B))
  → λr. Sum_k Diagonal(B[k])(r) · |e^{i k·r}|²
       (with the appropriate basis-function envelope; conceptually a sum over
        a structured basis indexed by k)

Diagonal(SparseTriples(T, W, c))
  → λr. Sum_{(i,i) ∈ T} γᵢᵢ · |ψᵢ(r)|²
        + Sum_{(i,j) ∈ T, i≠j} γᵢⱼ · ψᵢ(r) · ψⱼ*(r)
```

`Diagonal` is interesting: its result type is a function on space. The e-graph also represents this RESULT as an e-class — a function-shaped e-class whose member e-nodes are different evaluators. So `density` doesn't return a value; it returns an e-class handle to the density-function whose internal representation is also flexible.

### trace : γ̂ → Scalar

`Trace(γ̂)` is an e-class. Rewrites:

```
Trace(LowRankSum(vecs, scalars))
  → Sum_n scalars[n] · ⟨vecs[n], vecs[n]⟩        -- O(K · D), or O(K) if vecs are orthonormal

Trace(BlockByMomentum(K, B))
  → Sum_k Trace(B[k])                            -- O(Nₖ · Nᵦ)

Trace(SparseTriples(T, W, c))
  → Sum_{(i,i) ∈ T} γᵢᵢ · ⟨ψᵢ, ψᵢ⟩               -- O(N_diagonal)
```

Crucially, the analyses field (§4) caches `trace(γ̂) = N` if it has been established as an invariant — extraction may skip the computation entirely and return the cached invariant value.

### restrict, basis_change, apply_op

`Restrict(γ̂, S)` is an e-node; rewrites push the restriction through encodings (project the vectors in R1, drop k-sectors not in S in R2, mask triples in R3). `BasisChange(F, γ̂)` is an e-node; rewrites build the rotated R1 form (rotate the vectors), or the change-of-basis transformation in R3 (sandwich the triples with F). `apply_op(γ̂, B)` produces `Compose(γ̂, B)` as an e-class.

Importantly: **all of these "operations" are just constructor invocations.** They cost O(α(n)) — a constant — at construction time, because we only create e-nodes and let union-find/hashcons do the bookkeeping. Real cost arrives at extraction.

---

## 4. Invariants

There are three classes of invariants. The e-graph framing handles them through the **analyses** field — per-e-class abstract data updated lattice-theoretically as the e-graph grows. This is the "e-graph analysis" pattern from the egg library (Willsey et al.).

### Self-adjoint

Each γ̂ e-class carries an analysis field `SelfAdjointness ∈ {Known, Unknown, Falsified}`. Each constructor declares how it propagates:

- `LowRankSum(vecs, scalars)` is Known-self-adjoint if all scalars are real and the e-node is built as Σ cₙ (φₙ ⊗ φₙ*) — i.e. the outer products pair each vector with its own conjugate. This is a SYNTACTIC condition checkable from the constructor shape.
- `BlockByMomentum(K, B)` is Known-self-adjoint if each block in B carries `SelfAdjointness = Known`.
- `SparseTriples(T, W, c)` is Known-self-adjoint if T is built as a symmetric pattern with γⱼᵢ = γᵢⱼ*.
- `UnitaryConj(U, γ̂)` propagates: if γ̂ is Known-self-adjoint and U is Known-unitary, the result is Known-self-adjoint.

When two e-nodes get merged into the same e-class, the analyses lattice merges: `(Known ∧ Known) = Known`, `(Known ∧ Falsified) = error` (raises a structural violation), `(Known ∧ Unknown) = Known`. This is meet on a flat lattice.

**This is the right pattern: structure-by-construction for new e-nodes, lattice-merge for unifications.**

### Idempotency (closed-shell)

Idempotency is a STRONGER invariant: γ̂² = γ̂. The analysis field is `Idempotent ∈ {Known, Unknown, Falsified}`.

- `LowRankSum(vecs, scalars)` with `vecs` orthonormal AND `scalars ∈ {0, 1}` is Known-idempotent. The analysis can check this if vec-orthonormality is also tracked per-e-class.
- `BlockByMomentum(K, B)` is Known-idempotent iff each block is.
- `SparseTriples` is generally NOT Known-idempotent — sparsity doesn't imply idempotency. Stays Unknown unless a separate rewrite proves it.

The interesting case: a rewrite `γ̂ → γ̂·γ̂` (which only fires if Idempotent is Known) introduces an alternative e-node and merges it. So idempotency becomes USABLE: any place the program writes γ̂², the e-graph can rewrite it to γ̂. This is one of the few cases where saturation DISCOVERS a structural simplification automatically.

### Trace = N

`TraceValue ∈ ℝ ∪ {Unknown}`. The analysis tracks the trace of every γ̂ e-class. New e-nodes contribute computed-or-symbolic traces; unification requires the traces to agree (modulo a slack ε). If two e-nodes both claim membership in the same e-class but their analyses disagree, the e-graph raises.

**Cross-cutting observation.** The analyses pattern is the right tool for these invariants because:
- It's per-e-class (so it costs O(#classes), not O(#enodes)).
- It propagates UP through congruence closure for free.
- It UNIFIES at merge time and raises on contradiction — which is exactly "loud failure carrying a numeric witness" (principle 5 in the implementation plan).

What the analyses CAN'T do: enforce invariants on representations the framing doesn't know how to inspect. If γ̂ enters the e-graph via an opaque ExternalApply node (a black-box matvec from a library), the e-graph treats it as Unknown for all analyses — invariants degrade gracefully but quietly.

---

## 5. Time evolution

**Single step.** A timestep is just construction: `γ̂_{t+Δt}_id = UnitaryConj(U_id, γ̂_t_id)`. This is O(α(n)). No work is done until extraction or until saturation makes the e-class fat.

**Self-consistent closure.** The interesting bit: Ĥ = Ĥ[γ̂] depends on γ̂. So U_id depends on γ̂_id. So γ̂_{t+Δt}_id depends on γ̂_t_id BOTH directly AND through U_id. The DAG structure is:

```
γ̂_{t+Δt}_id  →  UnitaryConj(U_id, γ̂_t_id)
              →  U_id        →  Exp(H_id, Δt)
                              →  H_id   →  KSHamiltonian(γ̂_t_id, …)
                                       →  γ̂_t_id
```

No cyclic dependency: at each time t, γ̂_t is the FIXED INPUT, and H_t, U_t, γ̂_{t+Δt} are computed from it. The graph remains a DAG within a single timestep. The cycle only appears in the GROUND-STATE self-consistency loop, which is a fixed-point iteration over a sequence of e-classes γ̂⁽⁰⁾, γ̂⁽¹⁾, γ̂⁽²⁾, … each of which is a fresh e-class, with the iteration declaring convergence when two consecutive ones get merged by an ε-equality rewrite (see §6 caveat).

**Across many steps.** This is where the framing strains. Each timestep allocates new e-classes for γ̂_{t+Δt}, U_t, H_t. After 1000+ timesteps the e-graph has 1000+ chains of e-classes, each chain referencing the previous chain through `UnitaryConj`. Storage grows linearly in time.

**Eviction.** The e-graph needs a garbage-collection policy. Two natural strategies:

1. **DAG-reachability GC.** Keep an explicit set of "live root" e-classes (the current γ̂_t and any pending downstream queries). Reachable-from-root e-classes survive; the rest get freed. This is standard tracing GC on the e-graph DAG.

2. **Generational extraction-and-collapse.** Periodically, extract γ̂_t into a chosen materialized form, allocate a fresh e-graph (or fresh region of one) initialized from that extraction, and discard the old e-graph except for the analyses bookkeeping. This loses the equivalence-class richness — but it's the only way to keep memory bounded over very long runs.

**Both strategies have a deep cost.** They throw away saturation work. The rewrite rules that have populated γ̂_t's e-class — say, an R1↔R2 equivalence discovered during step 500 — must be REDERIVED at step 501 for γ̂_{t+Δt}, because the previous e-class is gone or trimmed. There is no obvious way to "reuse" the rewrite results across timesteps: the rules apply to the e-nodes inside the e-class, and those e-nodes contain different concrete data at each timestep.

There IS a mitigation: at each timestep, run a TARGETED saturation that propagates known rewrites forward by composition with `UnitaryConj`. For example, if γ̂_t was Known-Idempotent, and U_t is Known-Unitary, then γ̂_{t+Δt} is Known-Idempotent by the propagation rule. So invariants survive; only "alternative encodings" are lost and must be rediscovered.

**Net.** Time evolution is structurally fine for one or a few steps. For 1000+ steps the framing requires aggressive GC and accepts that most rewrites must be re-fired at each step.

---

## 6. Computational expressivity

What this framing expresses naturally:

- **Multiple equivalent encodings, simultaneously, with no commitment.** This is the framing's signature strength.
- **Deferred computation.** Build the whole computation as e-nodes, extract once at the end. This composes nicely.
- **Rewrites as facts.** "R1 and R2 forms of γ̂ are equal under translational symmetry" is a fact stated once and exploited forever.
- **Compile-time/runtime symmetry.** The same e-graph machinery can be used at compile time (over symbolic computation graphs) and at runtime (over actual γ̂ values).
- **Invariants as analyses.** Self-adjointness, trace, idempotency all fit the analyses pattern cleanly.
- **Discovery of non-obvious equivalences.** Equality saturation can find that, e.g., (Diagonal ∘ UnitaryConj ∘ LowRankSum) equals a simpler form that bypasses materializing the intermediate γ̂. This is the LAW-INFERENCE strength — the e-graph can spot common subexpressions across encodings and reuse work.

What this framing BENDS to express:

- **Approximate equality.** This is the deepest problem. The encodings of γ̂ are typically only equal up to a tolerance ε (rank truncation, cutoff truncation). Classical e-graphs model EXACT equality only. Modeling ε-equality requires either (a) using a much WEAKER notion of "equality" parameterized by ε (which destroys the union-find structure, because ε-equal isn't transitive) or (b) carrying error budgets as analyses and refusing to merge unless errors are within a global budget. Both are research-grade additions. The egglog community has explored "indistinguishability up to ε" but there is no widely-accepted treatment.

- **Iterative procedures.** An iterative procedure that builds a tridiagonal projection of γ̂ by repeated apply is NOT a pure functional operation: each step depends on the previous, and the output is a STREAM. The e-graph can represent this as `IterativeBuilder(γ̂, m)` — an opaque e-node parameterized by the number of steps — but it can't see INSIDE the iteration. Rewrites can't fire on individual iterations.

- **Cyclic self-consistency.** A fixed-point loop ρ → v_eff[ρ] → Ĥ → ψ → ρ is iterated, not directly representable as a DAG. The e-graph handles this by allocating fresh e-classes per iteration and adding ε-merge edges to detect convergence. But the loop is OUTSIDE the e-graph, not INSIDE it.

- **Mutable updates.** Updating γ̂ in place is anti-thetical to the framing. Every state change creates new e-classes. This is fine semantically but creates the GC pressure noted in §5.

What this framing CAN'T express:

- **First-class quantification.** The rewrite "for all unitary U, UnitaryConj(U, γ̂) preserves self-adjointness" is META-LEVEL — it's a rewrite RULE, not a fact INSIDE the e-graph. The e-graph can only ever instantiate it for a SPECIFIC U it's currently looking at.

- **Genuine asymptotic statements.** "γᵢⱼ decays exponentially in |rᵢ − rⱼ|" is not a fact the e-graph can hold or use. Such facts must be hard-coded as cost-function tweaks or as rewrite conditions external to the e-graph.

- **Non-deterministic operations.** A randomized rank-truncation that picks a random projection direction isn't expressible as a rewrite (it has no functional definition).

---

## 7. Speed/efficiency profile

The cost model has three layers:

**Layer 1 — e-graph operations.** Every construction (apply, timestep, restrict, ...) is O(α(n)) amortized via union-find. Hash-consing dedupes identical e-nodes for free. Adding a rewrite rule fires it once per matching e-node, and rule matching itself is O(#enodes × pattern_size) per rule per saturation pass. This layer is independent of D (the Hilbert dimension).

**Layer 2 — saturation.** Equality saturation runs rewrite rules to a fuel budget. Each rule firing creates new e-nodes (sometimes new e-classes) and possibly triggers union-find merges. The PATHOLOGICAL case is e-graph blowup: a small set of rewrites can generate combinatorially many e-nodes. For γ̂ this is a real risk: a rewrite like "γ̂ = U·U†·γ̂" applied liberally generates infinite e-nodes; rewrites must be carefully written or stratified.

**Layer 3 — extraction.** Given a cost function `cost : ENode × Cost_Map → Cost`, extraction is an integer linear program in general, but in practice greedy bottom-up DP works: visit each e-class once, for each member e-node compute its cost assuming children take their best-cost extraction, pick the minimum-cost e-node per e-class. This is O(#enodes) given a CACHED cost map.

**Per-operation costs at extraction time.** Using K for low rank, Nₖ for number of momentum sectors, Nᵦ for block size, |T| for sparse triple count, D for ambient dimension:

| Operation | R1 cost | R2 cost | R3 cost |
|---|---|---|---|
| apply (γ̂·v) | O(K · D) | O(Nₖ · Nᵦ²) | O(\|T\|) |
| timestep (one unitary conjugation) | O(K · cost(U)) | O(Nₖ · Nᵦ³) if U is block | O(\|T\| · cost(U)) |
| eigendecomp (top-m) | O(K) (already there) | O(Nₖ · Nᵦ³) | O(m · apply) via iterative procedure |
| density (per r) | O(K) per evaluation | O(Nₖ) per evaluation | O(neighbors of r) per evaluation |
| trace | O(K · D) or O(K) if orthonormal | O(Nₖ · Nᵦ) | O(N_diagonal) |

The cost function feeds these into extraction. The cost function must be co-designed with the operation graph — it isn't just a number per e-node, it's a number per (e-node, downstream-consumer) pair. This is the key insight: **for γ̂, the natural cost function is non-local — it depends on what's going to be done with the extracted form.**

**Composition costs.** When two operations chain — say, `density(timestep(γ̂, U, Δt))` — the e-graph rewriter has a chance to FUSE them. A rewrite like `Diagonal(UnitaryConj(U, γ̂))` → `λr. Diagonal(γ̂)(U†r) · |J(U)|` (schematically) can in some cases bypass materializing the intermediate γ̂'. This is the "kernel fusion" optimization that e-graphs are very good at. It's potentially a 10×+ speedup but only if the fusion rules are written.

**Materialization timing.** Materialization happens at extraction. The e-graph itself only ever manipulates handles. This means:
- Memory cost of the e-graph is O(#enodes × log(#eclasses)).
- Memory cost of any extracted γ̂ is whatever its chosen encoding requires.
- A long computation can run with everything as e-nodes and only materialize the final answer.

**Bottlenecks.**
1. **Saturation cost.** Each timestep needs targeted saturation to populate the new γ̂'s e-class. If the rewrite set is large or recursive, this can balloon. Mitigation: stratified rewriting, where rewrites are partitioned into phases (e.g. "first prove equivalences", "then propagate analyses", "then expand"). The egg literature has stratification tools.
2. **Memory.** Over many timesteps, the e-graph accumulates e-classes. GC is essential and lossy.
3. **The "no rule fires" case.** If saturation can't find a chain of rewrites connecting two encodings, extraction must pick one encoding and convert manually — paying the full conversion cost.
4. **ε-equality.** Approximate merges require error bookkeeping that adds O(1) per analysis but can cascade if errors compound.

**What's fast.** Building expression graphs over γ̂. Composing operations. Querying invariants. Choosing the right encoding for a known consumer. Caching repeated subexpressions across timesteps (if they survive GC).

**What's slow.** The first time a rewrite fires on a freshly-instantiated e-class. Saturation across many timesteps. Memory growth without GC. Any operation whose cost depends on the actual numbers — the e-graph can choose an encoding but the chosen encoding still does real work.

---

## 8. Generalization to BSE kernel and BTE collision matrix

The e-graph framing generalizes well in some ways and poorly in others.

**Well.** The BSE kernel is a 4-index tensor with multiple natural encodings: dense in particle-hole pairs, low-rank in screened-coulomb factors, sparse in some channels. The BTE collision matrix is a 4-index tensor with energy-conservation sparsity. Both objects have:

- multiple equivalent encodings (the same data, just reshaped);
- conversions that are algebraic moves (factorizations, sparsifications, channel decompositions);
- operations whose cost depends on encoding (matvec on BSE for an iterative solver; collision-evaluation on BTE);
- structural invariants (BSE is Hermitian under particle-hole exchange; BTE collision conserves momentum and energy).

So the conceptual model — e-class per object, e-nodes per encoding, rewrites for conversions, analyses for invariants — transfers directly. The same e-graph could hold γ̂, the BSE kernel, the BTE collision matrix as DIFFERENT e-classes with cross-references (the BSE kernel depends on γ̂, the BTE collision depends on the band structure derived from γ̂'s spectrum).

**Poorly.** Higher tensor rank multiplies the number of possible encodings. For γ̂ (2-index) we have three primary encodings; for the BSE kernel (4-index) there are more: low-rank in different index-pair groupings, block-diagonal in different symmetry channels, hierarchical (e.g. tensor-train, Tucker). The combinatorial space of rewrites between them is much larger, and saturation cost grows accordingly.

There's also a deeper issue: tensor decompositions (Tucker, tensor-train, etc.) have their OWN rich algebra (tensor contractions, canonical-form computations, etc.) that the e-graph would need to swallow. The e-graph can represent these as e-nodes, but expressing the rewrites between them naturally takes us into territory that overlaps with framing D (tensor networks). The e-graph would, in practice, end up wrapping a tensor-network rewriter as a black-box rewrite source.

**Net.** The framing generalizes structurally. It does NOT make the underlying problems easier; it just provides a uniform shell for storing-and-switching encodings of any of these objects. The hard problems (designing good cost functions for high-rank tensors, designing rewrite systems that don't explode) are still hard.

---

## 9. Inherent weaknesses

Honest assessment.

**1. Saturation is wrong for runtime objects.** E-graphs are designed for COMPILE-TIME: saturate the e-graph once, extract once, compile the result, done. γ̂ is a RUNTIME object that evolves at every timestep. Running saturation 1000+ times over the lifetime of a simulation is not what e-graphs are optimized for. Memory grows, GC is lossy, and rewrites must re-fire per timestep. The pattern fights the natural rhythm of the data.

**2. Approximate equality is unsolved.** Every encoding of γ̂ comes with a truncation: rank-K for R1, cutoff-c for R3. Different truncation levels of the same γ̂ are NOT equal in any classical algebraic sense; they're equal up to a controllable error. The e-graph's union-find machinery assumes equality is exact and transitive. Once we relax to ε-equality, transitivity fails (a ε-equal b and b ε-equal c does NOT imply a 2ε-equal c without additional bookkeeping that the e-graph isn't built to track). Workarounds exist (error-budget analyses, dedicated approximate-equality e-graphs) but they're research-grade.

**3. Cost functions are notoriously hard to design.** Extraction picks the cheapest e-node by cost. But the COST DEPENDS ON WHAT YOU'LL DO NEXT. For γ̂, "cheapest" for `apply(γ̂, v)` is encoding-dependent; "cheapest" for `density(γ̂)` is differently encoding-dependent. The cost function must be parameterized by the EVENTUAL CONSUMER, which means we either re-extract per consumer (expensive) or maintain a multi-objective frontier (combinatorial). The egg library acknowledges this; there's no clean answer.

**4. The "you discover an equivalence" superpower is rare.** The marketing of equality saturation is that it discovers non-obvious equalities. In practice, for a numerical-physics object like γ̂, the non-obvious equalities are between SYMBOLIC FORMS (e.g. fusion of operations) — and these symbolic equalities are the ones a human would write into the rewrite set anyway. The e-graph doesn't discover physical identities; it's a delivery vehicle for ones we know.

**5. The framing is heavy.** An e-graph has substantial bookkeeping: hashcons, parents, analyses, union-find. For an object accessed billions of times in a simulation loop, this overhead is hard to amortize unless every access participates in a non-trivial saturation. In the common case where we just need to compute `γ̂·v` repeatedly inside an inner loop, the e-graph is doing nothing useful — it's just dispatching to the chosen encoding's apply.

**6. The framing imposes a particular extraction-and-execute discipline.** Every operation becomes a two-phase process: build e-node, extract. This is foreign to imperative numerical code; it requires either generating closures at extraction time or producing a small IR that gets compiled per query. Both add latency to the hot path.

**7. Stratification vs unstratified rewriting trade-off.** Unstratified rewriting (the egg style) is more expressive but harder to bound; stratified (datalog-style) is more bounded but more rigid. For γ̂, the natural rewrites include things like "rank truncation introduces error ε" — these don't fit cleanly into either style.

**8. Self-consistency loops live outside the e-graph.** As noted in §5, ground-state SCF and time-step closures are fixed-point iterations, not pure rewrites. The e-graph holds each iterate as a fresh e-class, with the loop controller external. This works but undermines the claim that "everything is in the e-graph".

**9. Pauli-spinor extension.** γ̂ in the magnetic regime is 2×2 spinor-valued. Either we extend every encoding (LowRankSum-of-spinors, BlockByMomentum-of-spinor-blocks, SparseTriples-of-spinors) and double the rewrite set, or we model the spinor as another tensor index and inflate the encodings further. Either route doubles the rewrite-system complexity.

**10. Debuggability.** When extraction picks a "wrong" encoding for an operation, diagnosing why requires understanding the cost function, the saturation state, and the rewrites that fired. This is harder to reason about than direct dispatch to a concrete encoding.

---

## 10. Cross-framing position

How this framing relates to the other three:

### vs A (typed-term-algebra-with-rewrites)

A and C are CLOSELY RELATED. A typed-term-algebra-with-rewrites maintains a SINGLE canonical representative for each γ̂ and normalizes via confluent rewrites; C maintains MULTIPLE simultaneous representatives and chooses at extraction. C can be seen as A "with explicit equivalence classes made first-class" — instead of throwing away non-canonical forms after a rewrite, C keeps them around.

- **Overlap.** Both share the typed term algebra (LowRankSum, BlockByMomentum, SparseTriples as constructors), both define rewrite rules between encodings, both can express invariants as type predicates or analyses.
- **Divergence.** A bets on confluence: there should be a unique normal form for each γ̂, and rewrites converge to it. C bets on the cost function: there's no canonical form, the right form depends on the consumer. A is cheaper to maintain (less bookkeeping) but worse at adaptive dispatch. C is more flexible but heavier.
- **Picking between them.** If γ̂ has a clear best encoding for most operations, A wins (single canonical form, fast). If different operations consistently prefer different encodings, C wins (extraction picks per-operation).

### vs B (codata/coalgebraic)

B treats γ̂ as a stream of observations: γ̂ is whatever responds to apply, trace, density, etc. The internal representation is hidden behind a fixed observation interface. C and B are nearly orthogonal in design but compatible.

- **Overlap.** Both defer materialization: B by hiding the representation behind methods, C by storing operations as e-nodes. Both can support multiple encodings.
- **Divergence.** B exposes a NARROW interface (the observations) and hides everything else; C exposes a WIDE algebra and tracks equivalence between members. B is fundamentally hostile to introspecting WHY a particular response was given; C is built to expose the chosen representation. B is great for pure observation-driven flows; C is great for rewriting and fusion.
- **Composition.** They can stack: the e-graph could store γ̂ as an e-class one of whose e-nodes is a codata observer. The e-graph extracts to the codata view when downstream wants stream-style access.

### vs D (tensor-network-with-cost-aware-contraction)

D models γ̂ as a network of small tensors connected by index contractions, with the network shape itself as the data structure and cost-aware contraction-order optimization. C and D are SIMILAR IN SPIRIT (both about cost-aware computation over multiple representations) but operate at different levels of abstraction.

- **Overlap.** Both compute costs to drive choices. Both can express R2 (block decomposition) and R1 (low-rank as a 2-tensor decomposition) naturally. Both defer materialization.
- **Divergence.** D commits to the TENSOR NETWORK as the representation; C commits to the EQUIVALENCE CLASS over arbitrary representations. D's rewrites are tensor-network manipulations (gauge transformations, canonical forms, contraction reorderings); C's rewrites are arbitrary algebraic identities. D handles R3 (sparse in localized basis) less naturally because the locality structure isn't a tensor-network feature.
- **Stacking.** A tensor-network can be embedded as an e-node in the e-graph: `TensorNetwork(diagram, tensor_data)`. Then C's saturation can switch between tensor-network forms and other forms (R1, R3) at the same e-class. This actually argues that C could be a META-FRAMING that swallows D.

### Summary of overlap

```
A (typed-term-algebra)   ⊂  C (e-graph)     -- C is A with equivalence-classes promoted
B (codata)                ⊥  C              -- orthogonal axes; can compose
D (tensor-network)        ⊂  C (potentially) -- D embeds as one constructor in C
```

C is the most expressive of the four — it can swallow A's term algebra, hold codata views as one e-node, embed tensor networks as another. The price for this expressivity is the heaviest implementation burden, the worst memory profile under long-running time evolution, and the deepest unsolved problem (ε-equality). For γ̂ specifically — an object that lives at runtime for thousands of timesteps, is approximate in every encoding, and is consumed by many different operations — C's strengths and weaknesses are sharply traded off and the choice is genuinely close.

---

# Findings summary

**Strengths of C for γ̂.** First-class multi-encoding storage, deferred computation with cross-operation fusion, invariant tracking via e-class analyses, clean conceptual unification with BSE kernel and BTE collision matrix as cousins.

**Weaknesses of C for γ̂.** E-graphs were designed for compile-time, γ̂ lives at runtime; classical e-graphs model exact equality but every γ̂ encoding is approximate; cost-function design is unsolved for multi-consumer scenarios; long-time-evolution requires lossy GC that wastes accumulated saturation work; self-consistency loops sit outside the e-graph; the framing is heavy for an object accessed billions of times.

**Verdict.** C is the most flexible of the four framings and the only one that natively expresses "multiple equivalent encodings, each preferred for different operations, with equivalence as a first-class fact." But for γ̂ specifically, two structural mismatches are deep: (1) runtime evolution vs compile-time saturation, and (2) approximate vs exact equality. Either can be patched with research-grade extensions, but neither is solved. C is plausibly the right META-framing (a substrate that hosts A, B, or D as embedded e-nodes), but probably NOT the right inner representation for γ̂ if a single inner framing has to be chosen.

**Relevant context files** (read for this report):
- /home/javier/Desktop/Physics/Programs/n-Op/properties.md
- /home/javier/Desktop/Physics/Programs/n-Op/IMPLEMENTATION-PLAN.md (§3 unified state, §5 top-level concepts, §6 Born-Oppenheimer hierarchy, §7 computational vocabulary)
- /home/javier/Desktop/Physics/Programs/n-Op/research/group-B-electronic-magnetic-optical.md (full)

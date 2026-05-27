I'll research this framing thoroughly. Let me first read the relevant project files to ground my analysis in the actual γ̂ requirements.
I have enough physics context. Now let me check the implementation plan for the relevant sections.
I have sufficient context. I have a clear plan in mind for the report. Per the plan-mode constraint, I will not edit the plan file unless I need to refine my thinking — the report itself is the deliverable as a final message. Let me also note that the user did not ask for a plan; they dispatched me as a research agent to produce a structural report. Given the explicit constraint "**READ-ONLY RESEARCH. Do NOT create files. Return findings as a long detailed report in your final message,**" returning my findings directly is the correct action.

Here is the report.

---

# Framing E — Multi-Representation Pullback with Consistency Invariant

## 1. Representation

In Framing E, γ̂ is not a single object with one canonical form. It is a **synchronized bundle of concrete representations together with a consistency witness**. The bundle is a typed dependent record whose shape is fixed at the bundle's introduction point and whose contents are kept mutually consistent (up to a bounded error) under every operation.

The seed signature is:

```
EncodingTag      = R1 | R2 | R3
Repr             : EncodingTag → Type
Repr(R1)         = OuterProductSum  { vectors : List<HilbertVec>, scalars : List<Real> }
Repr(R2)         = BlockDiagonal    { blocks  : Map<MomentumLabel, DenseBlock> }
Repr(R3)         = SparseInBasis    { triples : List<(i, j, value)>,
                                      basis   : LocalizedBasis,
                                      cutoff  : Real }

Bundle           : SubSet(EncodingTag)             -- e.g. {R1, R3}
PullbackGamma B  = { encodings : DependentMap B Repr,
                     witness   : ConsistencyWitness B,
                     budget    : EpsilonBudget }
```

A `ConsistencyWitness` records the maximum drift between any two members of the bundle measured in an operationally meaningful norm (operator norm on apply, Frobenius on direct comparison, or trace-norm on Hermitian forms). It is updated by every operation that touches the bundle. It is **not a proof in the logical sense** — it is an evolving numeric scalar that bounds the disagreement between decoded forms.

`EpsilonBudget` is a small dependent record `{ε_consistency, ε_truncation, ε_drift_per_step}` that determines when a re-balancing step must fire. It is part of the bundle's identity because two bundles with the same encodings but different budgets behave operationally differently (one rebalances every five timesteps, the other every five hundred).

Three structural choices then govern the framing:

- **Bundle cardinality.** Typically 2 (the prototypical pullback) or 3 (when the workload spans operations whose cheap representations are mutually disjoint). Cardinality is part of the type. A `PullbackGamma {R1, R3}` and a `PullbackGamma {R1, R2, R3}` are not interchangeable.
- **Consistency form.** Either a runtime numeric witness (drift bound) or — for special structured bundles — a *constructive* witness in which one encoding is *derived* from another by a known retraction, and the consistency invariant collapses to "the second slot equals retract(first slot)." The constructive form has no drift but loses the symmetry of the pullback.
- **Update policy** (carried in the bundle, not the type): `WriteThrough | WriteBack | DeferredReconciliation`.

A useful mental picture: γ̂ is an **abstract handle** whose physical incarnation is a *pair of pointers* into two (or three) memory regions, each storing a different concrete form, plus a small piece of metadata declaring how far apart they have drifted. The pullback is real in the categorical sense — the object exists as the universal pair — and is materialized as the dependent record above.

## 2. Encodings

R1, R2, R3 manifest as distinct slots in the bundle's `encodings` map. Each slot stores its native concrete form and nothing else; it has no knowledge of the other slots' contents. Coexistence is a property of the **bundle**, not of the individual encoding.

- **R1 slot (low-rank outer sum).** A list of vectors `{φ_n}` and weights `{c_n}`, with `n ≤ K` for some target rank. Natural support for an operator-norm bound between forms.
- **R2 slot (block-decomposed by translation label).** A dictionary keyed by a discrete translation symmetry label, with each value a dense small block. Natural support for per-block Frobenius bounds.
- **R3 slot (sparse-in-localized-basis).** A coordinate list `{(i, j, v_{ij})}` of nonzero entries in a basis of spatially-localized vectors, plus a cutoff radius. Natural support for entrywise bounds restricted to the cutoff support.

Bundles are parameterized by **which subset** of these slots is present. The natural bundles are:

```
Bundle_R1R3 = {R1, R3}    -- contraction-heavy and entrywise-readout workloads
Bundle_R1R2 = {R1, R2}    -- low-rank-driven dynamics with translation-symmetric block structure
Bundle_R2R3 = {R2, R3}    -- block-structured systems with spatial restrictions
Bundle_All  = {R1, R2, R3} -- maximum dispatch flexibility, maximum overhead
Bundle_R1   = {R1}         -- degenerate single-slot case (= Framing A with R1 fixed)
```

Two encodings coexisting in a bundle means: **the bundle holds two distinct concrete data structures, neither of which decodes to the other directly, but both of which decode to the same abstract γ̂ up to ε**. The decoder maps `decode_t : Repr(t) → AbstractGamma` are partial inverses to encoder maps that may be lossy (R1 truncates beyond rank K; R3 truncates beyond cutoff). The pullback condition `decode_R1(r1) ≈_ε decode_R3(r3)` is the *only* glue between the slots.

A subtle point: the bundle's shape is not the universal categorical pullback. The categorical pullback `R1 ×_γ̂ R3` is the set of *all* pairs satisfying the equality. The bundle is a single *element* of that set, plus the choice of which element to track. So Framing E does not represent the pullback object itself — it represents a *trajectory* through the pullback.

## 3. Operations

The dispatcher selects the slot whose native cost on the requested operation is lowest, executes there, and then propagates (eagerly or lazily, per policy). The dispatch table is a static map:

```
dispatch_cost : EncodingTag × OperationKind → Cost
ApplyOp       : R1 ↦ rank-K mat-vec, R2 ↦ block-wise mat-vec, R3 ↦ sparse mat-vec
EigendecompOp : R1 ↦ trivial (rank K), R2 ↦ per-block dense, R3 ↦ iterative tridiagonalization
DensityOp     : R1 ↦ pointwise sum-of-squares, R2 ↦ inverse-translation-transform diag,
                R3 ↦ direct diagonal lookup
TraceOp       : R1 ↦ sum of scalars, R2 ↦ sum of block traces, R3 ↦ sum of diagonal entries
RestrictOp    : R1 ↦ project each vector, R2 ↦ select blocks, R3 ↦ mask rows/cols
BasisChangeOp : R1 ↦ rotate each vector, R2 ↦ congruence per block,
                R3 ↦ scatter-gather (often densifies)
ComposeOp     : R1 ↦ scalar-weighted outer products, R2 ↦ block matmul,
                R3 ↦ sparse-sparse matmul (fill-in risk)
TimestepOp    : R1 ↦ apply U to each φ_n, R2 ↦ exp on each block, R3 ↦ Krylov on sparse
```

Worked example 1: **`apply(γ : PullbackGamma B, v) → vector`.**

```
t  := argmin_{t ∈ B} dispatch_cost(t, ApplyOp)(γ.encodings[t], v)
out := apply_native(γ.encodings[t], v)
return out
```

Because `apply` returns a vector (not a new γ̂), no propagation is needed; the bundle is read-only for this operation. The dispatcher's choice is local and idempotent. If R1 has rank K and v is dense, R1 wins (O(K·n)). If R3 is sparse with bandwidth b, R3 wins (O(b·n)). The bundle pays only the dispatch overhead — a small constant — beyond the chosen-slot work.

Worked example 2: **`timestep(γ : PullbackGamma B, U, Δt) → PullbackGamma B`.**

Under write-through:

```
for t in B:
    γ'.encodings[t] := conjugate_native(U, γ.encodings[t], Δt)
γ'.witness := refresh_witness(γ', γ.witness, kernel = U)
return γ'
```

Each slot conjugates independently using its native machinery. R1 conjugates each φ_n separately (rank preserved exactly). R2 conjugates each block (block structure preserved if U is block-diagonal in the same translation label; otherwise the block structure breaks and re-blocking is needed). R3 conjugates entrywise via a sparse-sparse-sparse triple product (cutoff broadens, requiring re-truncation). The witness must be refreshed because two independently conjugated forms can drift apart even if they were ε-equal before — the conjugation step is not a contraction on the difference in general.

Under write-back: only the chosen slot is updated; the others are flagged invalid. Reads from invalid slots trigger a *transcoding* step (decode the valid slot, re-encode into the requested slot's native form). Transcoding is the framing's most expensive operation and the principal cost-centre of write-back.

Worked example 3: **`eigendecomp(γ : PullbackGamma B) → Stream<(λ, v)>`.**

If R1 is in the bundle and the rank is small, R1 wins trivially — its eigenpairs are essentially the stored `(c_n, φ_n)` pairs after Gram-Schmidt on the φ_n. If R1 is not in the bundle, the dispatcher chooses between R2 (per-block dense diagonalization, parallel across blocks) and R3 (iterative procedure that builds a tridiagonal projection via repeated matrix-vector products — a Krylov-style method). For R3, the dominant cost is the inner matrix-vector product, which itself dispatches *recursively* through the bundle: if R1 is also in the bundle, the inner mat-vec uses R1. This is one of the framing's quiet strengths — *nested dispatch* lets a sparse outer algorithm use a dense inner kernel transparently.

Worked example 4: **`density(γ) → real function n(r) = γ(r, r)`.**

R1 wins almost always: `n(r) = Σ_n c_n |φ_n(r)|²`. The cost is O(K · |grid|). R3 also performs well if the diagonal is directly indexable: O(|diagonal nonzeros|). R2 is poor because the diagonal of γ̂ is not the diagonal of the blocks — it requires an inverse translation-transform first. So the dispatcher picks R1 or R3 deterministically and never R2. This is exactly the pattern Framing E is designed for: per-query best-of-bundle without storing every possibility.

Worked example 5: **`restrict(γ, S) → γ̂'` where S is a subspace projector.**

Each slot restricts in its native fashion: R1 projects each φ_n (no rank growth); R2 selects only blocks intersecting S; R3 masks rows and columns outside S. Witness refresh is straightforward because restriction is a contraction on the operator-norm difference. Restriction is the framing's most-faithful operation: the bundle structure is exactly preserved.

The general dispatch logic is:

```
op(γ : PullbackGamma B, args) =
  t      := select_slot(B, op, args)
  result := op_native(γ.encodings[t], args)
  if op returns γ̂ then
    new_bundle := propagate(γ, t, result, policy)
    refresh_witness(new_bundle)
    maybe_rebalance(new_bundle)
    return new_bundle
  else
    return result
```

The `maybe_rebalance` check fires when the witness exceeds `ε_consistency` or when the rank/cutoff of any slot exceeds its budget. Rebalancing is the *coercion* operation: re-derive one slot from another using an explicit transcoding. This is expensive but bounded — it occurs O(1) times per O(timesteps_between_rebalances) operations, so the amortized cost is small.

## 4. Invariants

Framing E carries **two layers of invariants**.

**Layer 1 — physical invariants** (self-adjoint, idempotent for closed-shell, trace = N). These must hold for the abstract γ̂. Because they are properties of the abstract object, they must hold for *every* slot simultaneously, since each slot decodes to the same abstract object up to ε.

- **Self-adjoint** is preserved natively by all three encodings if the corresponding operation respects symmetry: R1 with paired conjugate factors is automatically self-adjoint; R2 with each block Hermitian; R3 with symmetric sparsity pattern and conjugate-symmetric values. Each slot enforces its own version; the consistency invariant doesn't enter.
- **Trace = N** is enforced per slot. The dispatcher must verify that all slots agree on trace (one of the cheapest checks possible — O(K) for R1, O(|blocks|·dim_block) for R2, O(|diagonal entries|) for R3). Disagreement *is* the consistency invariant violating.
- **Idempotency** (γ̂² = γ̂) is more subtle. In R1 with rank-K and integer occupations, idempotency is automatic when the φ_n are orthonormal — preserved exactly. In R2, idempotency holds per block. In R3, idempotency is *not* preserved by simple truncation: γ̂_truncated² ≠ γ̂_truncated even when γ̂² = γ̂. So R3 in a closed-shell setting must carry an explicit truncation error budget and the consistency witness must dominate the idempotency violation.

**Layer 2 — consistency invariant** (the new and load-bearing one). For every pair `(s, t) ∈ B × B`:

```
‖decode_s(γ.encodings[s]) − decode_t(γ.encodings[t])‖_op ≤ ε_consistency
```

The witness is the running upper bound on this distance under some chosen norm. Three enforcement strategies are possible:

1. **Type-level enforcement.** Make the bundle a refinement type whose well-formedness predicate is the equality. Only constructors that preserve the predicate can build a bundle. This is clean but requires either (a) symbolic decoders so equality is decidable or (b) a fixed ε baked into the type (which makes the type system carry numeric data — workable but heavy). This is the strongest form and corresponds most closely to the categorical pullback.
2. **Constructive enforcement.** One slot is *primary*; secondaries are *derived* by a retraction `retract_s→t`. Then the consistency invariant collapses to `t = retract(s)`, which is a structural equality. But this loses the symmetry: the primary slot is the source of truth, and the framing degrades to "Framing A with a cache of secondary views." It is no longer a pullback but a single-source-of-truth with derived projections.
3. **Runtime witness.** The bundle carries a numeric upper bound on the slot-pair distance; the bound is updated by every operation. Reads check that the bound is below tolerance; writes refresh the bound. This is the most flexible and the one that admits write-back and deferred-reconciliation policies, but it provides no static guarantee.

The framing's identity is most cleanly expressed in (1); its practical incarnation is almost always (3) with (2) as a degenerate option.

**Verification of the consistency invariant.** Cheap verifications are:

- Trace agreement across slots (O(min-cost-trace per slot)).
- Diagonal agreement at a sampled subset of grid points (O(|sample|)).
- Action on a sampled vector `v`: `‖(decode_s(.) − decode_t(.))·v‖` (O(apply per slot)).

These do not prove the operator-norm bound but provide cheap probabilistic monitoring. Full re-verification is a transcoding step. The pragma is: monitor cheaply, transcode rarely.

## 5. Time Evolution

A single timestep is the conjugation `γ̂' = U·γ̂·U†` with `U = exp(-i·Ĥ[γ̂]·Δt)`. Under write-through:

```
for t in B: γ'.encodings[t] := conjugate_native(U, γ.encodings[t])
```

Each slot's native conjugation is structure-aware:

- **R1**: `c_n` unchanged; `φ_n → U·φ_n` for each n. Cost: K applies of U. Rank exactly preserved. Self-adjointness exactly preserved.
- **R2**: if U is block-diagonal in the same translation label, each block conjugates independently. If U mixes blocks (e.g. an external field breaking the translation symmetry), R2's block structure breaks and R2 must be re-blocked or de-promoted to a less-structured form.
- **R3**: a triple sparse product whose fill-in is determined by U's support. Typical case: cutoff broadens monotonically with timestep — after a few steps, R3 densifies and must be re-truncated, introducing controlled error.

Across 1000+ timesteps, three failure modes emerge:

- **R1 stays clean** as long as the rank of the true γ̂ stays small. If the true γ̂ accumulates spectral weight outside the top-K eigenvectors (which happens under driving or strong interactions), R1's rank-K approximation drifts arbitrarily far from the truth. The witness will eventually fire; rebalancing requires increasing K, which raises R1's cost permanently.
- **R2 stays clean** as long as the translation symmetry remains exact. Under driving, R2 may need block-broadening (introducing inter-block coupling) which the framing treats as a degradation step.
- **R3 densifies** monotonically under most realistic Hamiltonians. Re-truncation must fire periodically. Each re-truncation injects a small ε into the witness; many such injections accumulate. The witness's growth rate per step is the framing's **operational drift rate**.

The bundle stays well-formed across long trajectories only if the rebalancing schedule keeps pace with the drift rate. The user must choose `ε_drift_per_step` such that `n_steps · ε_drift_per_step < ε_consistency_target` — a classical adaptive-error-budgeting problem.

A particularly elegant aspect: because Ĥ[γ̂] depends on γ̂ (the nonlinear closure), and Ĥ itself is computed from γ̂'s diagonal (the density, easy in R1 or R3) and some functional of γ̂'s eigenvectors (also easy in R1), the closure step *itself* benefits from the bundle dispatcher. Ĥ[γ̂] is built from cheap reads on the bundle; U is then built from Ĥ; conjugation then dispatches to all slots. The nonlinear feedback loop runs almost entirely through the cheap-read slot.

A subtle point about write-back under time evolution: write-back is *catastrophic* for timestep because invalidation propagates everywhere. Every timestep touches the entire γ̂, so write-back forces transcoding every timestep, which is *more* expensive than write-through. So for time evolution, **write-through is the only sensible policy**, and the bundle's value comes from cheap reads of derived quantities (density, trace, expectation values) between steps. This is the framing's intended use mode: dynamics drives the slots, observables read the best slot.

## 6. Computational Expressivity

Naturally expressed:

- **Cheap mat-vec dispatch** — the apply operator is the framing's killer use case. Each call picks the best slot with no overhead beyond a table lookup.
- **Diagonal and trace readouts** — every realistic γ̂ has at least one slot in which the diagonal is essentially free.
- **Restriction to subspaces** — every slot restricts cheaply; the bundle composes restrictions naturally.
- **Multi-observable readout** — when a downstream task wants several quantities (density, trace, top eigenvalues, action on a few vectors), each goes to its own optimal slot in parallel.

Awkwardly expressed:

- **Operations returning γ̂ under write-back** — invalidates the bundle's coherence advantage. The framing degrades to "Framing A with a stale cache."
- **Approximate-equality reasoning** — the consistency invariant is ε-equality, which is not transitive. Three-slot bundles cannot be reasoned about by chaining pairwise bounds; the bound on (s,u) is not the sum of bounds on (s,t) and (t,u) under most norms, but is bounded by their sum. This forces conservative witness updates.
- **Compositional algebraic identities** — Framing A can rewrite `(γ_a + γ_b)·γ_c → γ_a·γ_c + γ_b·γ_c` by tree rewriting. Framing E has no rewrite vocabulary; each operation runs natively in the slots. The framing pays this cost: lost algebraic optimization.

**Where you bend the framing:**

- **Hot rebalancing.** When drift exceeds budget mid-evolution, the framing must transcode. Transcoding is not a framing primitive — it's an escape hatch. Rebalancing schedules are workload-dependent hyperparameters with no principled default.
- **Cross-bundle operations.** If you have a `Bundle_R1R3` γ̂_a and a `Bundle_R1R2` γ̂_b and you want γ̂_a · γ̂_b, the dispatcher must pick a *common* slot — here only R1. If the bundles share no slot, you must transcode one to match the other. This is a hidden coupling between bundles' types.
- **Variable-cardinality bundles.** The cleanest framing fixes cardinality at type-introduction. Real workloads want to *add* a slot mid-computation (e.g. switch from `{R3}` to `{R1, R3}` when R3 starts to densify). Adding a slot requires a transcoding step and an update to the bundle's type, which most type systems cannot do dynamically.
- **Approximation-tolerant equality.** The consistency invariant must be ε-relaxed, but the rest of the system may expect equality. Lifting ε-equality into all downstream operations is a pervasive design tax.

## 7. Speed/Efficiency Profile

**Storage cost.** Each γ̂ stores `Σ_{t ∈ B} storage(t)`. For a typical `Bundle_R1R3` with K-rank R1 and bandwidth-b R3:

```
storage = O(K·n) + O(b·n) + O(witness_metadata)
```

Compared to single-slot storage, this is a constant-factor inflation by `|B|` *when the slots are individually compact*. The framing's value relies on each slot being compact in its own way. A bundle that includes a dense form would defeat the purpose.

**Per-operation cost.** For read-only operations:

```
cost(op) = O(|B|) dispatch lookup + cost_native(chosen_slot, op)
```

The dispatch overhead is negligible relative to the chosen-slot work for non-trivial operations. For trivial operations (e.g. trace on a small R1), the dispatch overhead might dominate, in which case the bundle layer can be short-circuited.

For γ̂-returning operations under write-through:

```
cost(op) = Σ_{t ∈ B} cost_native(t, op) + cost(refresh_witness) + maybe(cost(rebalance))
```

The write-through multiplier is the framing's principal performance tax. It is justified only if reads dominate writes by a factor greater than `|B|`. For dynamics, reads do dominate writes (each timestep produces one new γ̂ but many derived observables are queried), so the multiplier pays off.

For γ̂-returning operations under write-back:

```
cost(op)        = cost_native(chosen_slot, op) + cost(invalidate)
cost(later_read) = cost_native(latest_slot, op_read) + maybe(cost(transcode_to_chosen))
```

Write-back amortizes well when later reads happen to hit the same slot that did the write. It amortizes poorly when reads diverge from writes — the typical case under varied observable demand.

**Update cost under deferred reconciliation.** Bundle entries drift up to `ε_drift_per_step` per timestep; rebalancing fires every `ε_consistency / ε_drift_per_step` steps. Per-step cost is `cost_native(primary_slot, op) + ε_drift_per_step·(measurement)`. The amortized rebalancing cost is `cost(transcode) / (rebalance period)`. For long stable trajectories this is the cheapest policy; for short bursty trajectories it can be more expensive than write-through because of transcoding amortization mismatches.

**The operational trade-off.** The framing trades storage (`|B|×`) and update cost (per policy) for elimination of conversion cost on reads. The conversion that Framing A would charge on every basis-change query becomes free in Framing E because the converted form is already in the bundle. The break-even point is *read frequency*: when the same conversion would be requested more than `|B|` times before the bundle is updated, Framing E wins.

## 8. Generalization

For **BSE kernel** (a 4-index object with sparsity in particle-hole channels) and **BTE collision matrix** (a 4-index object with sparsity in energy-conserving mode-pair channels), the framing scales but with serious caveats.

The analog of R1 for a 4-index tensor is a low-rank Tucker-style decomposition (or its CP / canonical-polyadic cousin). The analog of R2 is a block decomposition along the conserved quantum numbers of the channel (particle-hole momentum for BSE; energy shell for BTE). The analog of R3 is a coordinate sparse format keyed on the indices where the kernel is nonzero. All three are reasonable native forms; all three exist in the wild for these objects.

A bundle `{Tucker, BlockByChannel, SparseCOO}` is a coherent framing. The operations dispatch analogously: contraction with a 2-index object dispatches to the Tucker form for fast inner products, to the block form when the contracted index is a channel index, to the sparse form when the contracted object is itself sparse.

**Storage concerns at higher rank.** This is where the framing strains. Each 4-index slot is fundamentally larger than its 2-index counterpart. A `|B|×` multiplier on a 4-index storage is a serious cost. The framing remains tractable only if each slot is genuinely compressed — Tucker-style with bounded ranks, sparse with strict bandwidth limits. If the kernel is dense, the bundle multiplies dense storage by `|B|`, which is the same disaster as keeping a dense γ̂.

A more practical mode for higher-rank objects is **bundle cardinality 2** with a *primary slot* and a *derived view slot*. The view slot is a structured projection of the primary slot (e.g. block-diagonal projection of the Tucker form). This is the constructive enforcement form from §4 and is genuinely useful at higher rank because the derived slot can be much smaller than the primary and is cheap to refresh.

**Unification with γ̂.** A bundle vocabulary is uniform across rank-2 (γ̂) and rank-4 (BSE, BTE) objects: declare slots, declare dispatch costs, declare an update policy, declare a consistency budget. The same dispatcher works on both. So Framing E unifies the three holes at the framing level even though the slot contents are very different in shape. This is a real generalization win.

## 9. Inherent Weaknesses

Honestly:

- **Storage overhead is real and unavoidable.** A bundle of `|B|` encodings stores `|B|×` data. If γ̂ is borderline-feasible in one encoding, multiplying by 2 or 3 may exceed memory. Framing E is most natural when each slot is *much* smaller than the dense form, which is most realistic encodings for γ̂ but not necessarily for BSE/BTE.

- **Consistency maintenance is the framing's principal cost-centre.** Write-through pays `|B|×` per operation. Write-back pays for transcoding on dispatch mismatches. Deferred reconciliation pays for periodic rebalancing. There is no policy that eliminates this cost; the framing chooses where to pay it.

- **Hyperparameter selection.** Bundle cardinality, slot choice, update policy, ε_consistency, ε_drift_per_step, rebalancing schedule — each is workload-dependent and lacks principled defaults. Choosing them well requires either workload profiling or a meta-layer that tunes them. The framing externalizes these choices to the user.

- **Approximate-equality issues.** The consistency invariant is ε-equality. ε-equality is reflexive and symmetric but not transitive, so three-slot bundles cannot use the usual chaining lemmas. The witness on (s, u) must be computed directly, not inferred from (s, t) and (t, u) bounds. This forces conservative witness updates and complicates the rebalancing logic.

- **Dispatch overhead is real for small operations.** A trace on a bundle pays a constant overhead per slot to check which slot is cheapest. For γ̂s with very small rank or very few nonzeros, this overhead dominates the native work. Framing E is best at non-trivial γ̂ sizes.

- **Cross-bundle composition is awkward.** Operations between two γ̂s with different bundle types require finding a common slot or transcoding. This is a hidden coupling that surfaces as type errors or runtime transcoding costs.

- **Long-trajectory drift accumulation.** Across many timesteps, each slot drifts in its own structure: R1's rank may need to grow; R3's cutoff may need to broaden; R2's block structure may break. The bundle's slot *types* are constant but the *parameters* inside each type drift. Rebalancing addresses the consistency invariant but not the per-slot quality. After many steps, the bundle may technically be consistent but operationally degraded (e.g. R1 with rank growing unboundedly).

- **The framing has no algebraic vocabulary.** Framing A can rewrite `(A·B)·C → A·(B·C)` based on type tags; Framing C can pick from cross-linked equivalents at extraction. Framing E only knows operations on slots — there is no rewrite vocabulary, no algebraic optimization, no learned simplification. The framing is *operational*, not *algebraic*.

- **Witness scalability.** For pairwise consistency in a `|B|`-slot bundle, the witness is `O(|B|²)` pairwise bounds (or the conservative single max). Each operation updates each pair. For `|B| = 3`, this is six bounds; for `|B| = 5`, fifteen. The framing scales poorly in bundle cardinality beyond 3.

## 10. Cross-framing Position

Framing E sits in the framing space as a deliberate compromise. Its relationship to the other four:

**Versus Framing A (typed term algebra).** A maintains one encoding per node and uses explicit rewrites to convert between encodings. E maintains a fixed small set of encodings simultaneously and pre-pays the conversion cost as storage. A pays the conversion cost on demand; E pays it once and amortizes over many reads. They are dual in trade-off. **E is not a special case of A** because A's term has a single shape tag; E's bundle has a set tag. But you could *encode* E inside A by introducing a "bundle" constructor with `|B|` child terms and consistency rules — at which point you have a refined A whose chosen refinement is E. So E is structurally an A specialization but operationally a distinct framing.

**Versus Framing B (codata/coalgebraic).** B exposes only destructors and hides the underlying representation; the consumer can never see whether the implementation is R1 or R3 or a bundle. E is, by construction, *internal* to the implementation of B. **E is a natural implementation of B's interface.** B says "here's an object; you can destruct it"; E says "internally, the object is a bundle and destructions dispatch to the cheapest slot." So B and E compose: B as outer wall, E as inner machinery. This is consistent with the conductor's earlier synthesis of a B-interface over A-staging — E slots into the same architecture as a particular A-staging strategy.

**Versus Framing C (e-graph with equality saturation).** C maintains *all* equivalent forms cross-linked, with per-query cost-driven extraction. E maintains a *fixed small subset* of forms with per-operation cheapest-slot dispatch. **E is C with cardinality bounded.** This is the most direct comparison. C's strength is that extraction can synthesize forms not in any single slot's storage (combinations and rewrites); C's weakness is unbounded storage and the difficulty of incremental update through saturation. E gives up the synthesis capability for bounded storage and trivial incremental update.

In categorical terms: C represents the *full equivalence class* of γ̂; E represents a *chosen point* in the equivalence class, plus a *tangent* (the secondary slot is a small perturbation through equivalence-preserving directions). C is the limit of E as `|B| → all encodings`; E is C with `|B| = 2 or 3`.

**Versus Framing D (tensor network with cost-aware contraction).** D treats γ̂ as a single node with a chosen type and optimizes contraction order. E treats γ̂ as a bundle of synchronized nodes (one per slot) and optimizes per-operation slot choice. **D and E address different optimization axes.** D optimizes the *path* through a contraction graph given a fixed node representation; E optimizes the *node representation* given a fixed operation. They are complementary: a bundle-aware tensor network would have nodes that are themselves bundles, with the contraction-order optimizer choosing both the contraction path and (for each step) which slot of each node to use. This is a genuine extension of D, not a contradiction.

**Versus profunctor optics.** A pair of lenses onto R1 and R3, with consistency laws relating their put-operations, is essentially a bundle with type-level enforcement. The lens laws (get-put, put-get, put-put) become the consistency invariant. E expressed via lenses is the same framing under a more polished categorical language. The lens form is cleaner; the bundle form is more operational. Both are the same idea.

**Versus dual numbers / forward-mode differentiation.** Dual numbers carry `(primal, tangent)` pairs with a defined arithmetic on the pair. This is exactly a bundle with cardinality 2 and a specific consistency rule (the tangent is the derivative of the primal). E generalizes dual numbers to a richer family of consistency rules. So forward-mode AD is a *specific* instance of E with a particular tangent semantics; E is the abstraction.

**Versus cache-coherence protocols (MESI/MOESI).** The hardware analogy is exact: each bundle slot is a cache line, the consistency invariant is the coherence protocol, write-through and write-back are literally the cache write policies, deferred reconciliation is weakly-consistent shared memory. The framing is *not* a metaphor with cache coherence — it *is* cache coherence, applied at the data-structure level rather than the memory-hierarchy level. This is reassuring (the policies are well-studied) and limiting (the framing inherits cache coherence's hard limits, including the impossibility of strong consistency with low coherence cost).

**Versus CRDTs.** CRDTs are eventually-consistent replicated objects with mergeable update operations. The deferred-reconciliation policy is a CRDT-style framing for γ̂. The merge operation is the rebalancing transcoding. CRDTs require that the merge be commutative-idempotent-associative; for γ̂ this is generally false (composition does not commute), so the CRDT analogy applies only to commutative subclasses of operations (additive updates, scalar rescaling).

**Is E genuinely new, or a refinement?** Honestly: **E is a refinement of C with bounded cardinality**, viewed under a *different optimization lens* (operational dispatch rather than extraction). It is also a *concrete implementation strategy* for B and an *operational sibling* of D. It is neither contained in A (because of the bundle structure) nor genuinely independent of C (because cardinality is the only essential difference). The novelty is in the *framing's foreground choices*: declaring cardinality and update policy as first-class type-level data, treating the consistency invariant as a *witness object* rather than an equality, and dispatching per-operation rather than per-query.

In the layered hybrid the conductor proposed (B-interface / A-staging / D-runtime / C as optional optimization), **E fits as a refinement of the A-staging layer**: instead of A's single-encoding term tagged with a production, the staging layer holds an A-term whose *leaves* are bundle handles. The runtime contraction (D) then operates on the bundle's chosen slot per contraction. C remains the saturation-time optimizer that can *choose* which bundle to materialize at staging time, given a workload profile of expected operations.

So E does not replace any framing; it slots into the existing layered hybrid as the **bottom-layer representation choice** for the most-touched objects, with cardinality and update policy as workload-specific tuning parameters.

---

**Summary of the framing's identity.** Framing E is the operational refinement of "γ̂ has many equivalent encodings" into "γ̂ has *exactly these few* equivalent encodings, maintained consistent up to a controllable ε, with per-operation dispatch to the cheapest one." It is the framing that takes seriously the cost-asymmetry of operations across encodings and pays for it in storage rather than per-query work. It is genuinely useful when reads dominate writes by a factor exceeding bundle cardinality and when each chosen slot remains compact under the workload — both of which hold for the γ̂ dynamics use case but degrade as one moves to larger tensors (BSE, BTE) or to write-heavy workloads (mid-evolution closure updates without observable reads). Its principal weaknesses are storage overhead, consistency-maintenance cost, and the lack of an algebraic vocabulary — but these are the prices it pays for cheap, predictable, per-operation best-of-bundle dispatch.

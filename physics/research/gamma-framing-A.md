I'll research the typed term algebra with rewrite rules framing for γ̂. Let me first explore the project context to ground my analysis.
I'll proceed with read-only research. The user explicitly told me to return the report as my final message (not to write files), so I'll respect that despite plan mode — my deliverable is a text response, not file changes.
I have enough context. Let me also briefly check the architecture document to understand the substrate stance.
I have sufficient context. Now I'll write the deep structural report on Framing A (typed term algebra with rewrite rules) directly as my final response.

---

# Framing A: γ̂ as a Typed Term Algebra with Rewrite Rules — Structural Report

## 1. Representation

In this framing, γ̂ is **not a matrix-shaped value**. It is a **node in an abstract syntax tree** drawn from a small grammar of constructors. The grammar is the public face; the leaves carry the actual numeric payloads (vector lists, sparse triples, scalar coefficients). Every node carries two parameters: a **production tag** (which constructor it is) and a **type-tag tuple** indexed by structural invariants.

The signature in scope is:

```
DensityTerm = forall (sa : Bool) (idem : Bool) (tr : Option[Real]).
              ProductionNode<sa, idem, tr>

ProductionNode ::=
    OuterProductSum     ( vectors  : List[Vector]
                        , scalars  : List[Real]
                        , basis    : BasisRef )
  | BlockDiagonal       ( labels   : FiniteSet[MomentumLabel]
                        , blocks   : Map[MomentumLabel, DensityTerm] )
  | SparseInBasis       ( entries  : List[(IndexI, IndexJ, Real)]
                        , basis    : LocalBasisRef
                        , cutoff   : Real )
  | BasisChange         ( transform : BasisTransform[FromBasis, ToBasis]
                        , inner     : DensityTerm )
  | UnitaryConjugation  ( unitary   : UnitaryOp
                        , inner     : DensityTerm
                        , delta_t   : Real )
  | LinearCombination   ( pieces    : List[(Real, DensityTerm)] )
  | Restriction         ( inner     : DensityTerm
                        , subspace  : Subspace )
```

The crucial distinction from a free-monad encoding (discussed in §6) is that **constructors here are pure data**, not operation requests. `UnitaryConjugation(U, inner, Δt)` is a static node, not a deferred call. The interpretation of the node — what numeric work it implies — is supplied externally by **visitors**.

A visitor has the signature

```
Visitor[Result] = DensityTerm -> Result
```

implemented as a structural match. Pattern matching is the sole mechanism of operation dispatch.

Two pieces of context propagate alongside the tree:

- **Basis registry**: `BasisRef` is a key into a global registry that names plane-wave grids, spatially-localized bases, and momentum-sector subdivisions. References avoid copying basis data into every node.
- **Type-tag environment**: the tags `<sa, idem, tr>` are carried at the type level. A node tagged `<true, true, Some(N)>` advertises self-adjoint, idempotent, and trace = N. The type system rejects constructions that would violate the tag.

## 2. Encodings

Encodings R1, R2, R3 are **first-class as productions**.

- **R1** is `OuterProductSum(vectors, scalars, basis)`. The list `vectors` holds the {φ_n} (each itself a numeric array in the named basis); `scalars` holds the {c_n}. This is the canonical low-rank form. The type tag is `<true, ?, Some(Σ c_n)>` — self-adjoint when scalars are real, trace immediately computable as their sum, idempotency only when all c_n ∈ {0, 1} and the vectors are mutually orthogonal (an extra invariant the constructor can demand or check).

- **R2** is `BlockDiagonal(labels, blocks)`. The map indexes a finite set of momentum sectors; each block is *itself a* `DensityTerm`, recursively. This is the key structural commitment: blocks can independently be in R1, R2, or R3. A typical bulk crystalline ground state would have `BlockDiagonal(k_mesh, {k ↦ OuterProductSum(...)})` — R2 outer, R1 inner.

- **R3** is `SparseInBasis(entries, basis, cutoff)`. Entries are the nonzero matrix elements; the basis reference names the spatially-localized basis; the cutoff records the spatial-decay threshold under which entries were dropped.

The remaining constructors are **structural glue** rather than encodings:

- `BasisChange` is conversion-as-construction. It does not perform the change of basis; it announces that the inner term, when forced, must be re-expressed in the named target basis.
- `LinearCombination` lets us write sums without committing them to a single production.
- `Restriction` projects to a subspace symbolically.
- `UnitaryConjugation` is the deferred timestep.

Dispatch on encoding is therefore explicit, structural, and observable: a visitor sees the outermost constructor and branches.

## 3. Operations

Each operation listed in the brief is realized as a **visitor**: a function that pattern-matches on the outermost production and recurses where needed. Below are worked sketches for the four required examples.

### apply : DensityTerm × Vector → Vector

```
apply (OuterProductSum(φs, cs, basis))   v  =
    Σ_n cs[n] * φs[n] * (φs[n] · v)        -- inner products in basis

apply (BlockDiagonal(labels, blocks))    v  =
    let v_k = split-by-sector(v, labels)
    in   reassemble({k ↦ apply(blocks[k], v_k[k]) for k in labels})

apply (SparseInBasis(entries, basis, _)) v  =
    let v_local = basis.gather(v)
        out = zeros_like(v_local)
        for (i, j, x) in entries: out[i] += x * v_local[j]
    in basis.scatter(out)

apply (BasisChange(T, inner))            v  =
    apply(inner, T.to_inner(v))           -- transform v into inner basis
    |> T.from_inner                       -- transform result out

apply (UnitaryConjugation(U, inner, Δt)) v  =
    U.adjoint_apply(v) |> apply(inner) |> U.apply

apply (LinearCombination(pieces))        v  =
    Σ_n a_n * apply(γ_n, v)   where (a_n, γ_n) in pieces

apply (Restriction(inner, S))            v  =
    S.project (apply(inner, S.project(v)))
```

Each clause is one rule. The complete `apply` visitor is the disjoint union of these rules — seven rules for seven productions. The cost of `apply` is **set by the outermost production** (with recursion). On R1 it is O(rank × dim); on R2 it is the sum over blocks; on R3 it is O(nnz). The visitor pattern makes this transparent.

### timestep : DensityTerm × UnitaryOp × Real → DensityTerm

The cheapest, most term-algebraic option is to **defer**:

```
timestep(γ, U, Δt) = UnitaryConjugation(U, γ, Δt)
```

This is O(1). It produces a one-node-larger tree. After 1000 steps the tree has accumulated 1000 nested `UnitaryConjugation` layers wrapping the original γ̂_0. This is essentially a normalized form: `UC(U_1000, UC(U_999, ..., UC(U_1, γ_0)))`. We discuss materialization in §5.

A **forced** timestep applies a rewrite rule that pushes the conjugation inward according to the inner production:

```
force-step (UnitaryConjugation(U, OuterProductSum(φs, cs, basis), Δt))
    = OuterProductSum(map(U.apply, φs), cs, basis)
        with type tag <true, idempotent inherited, trace inherited>

force-step (UnitaryConjugation(U, BlockDiagonal(labels, blocks), Δt))
    = if U commutes with the sector decomposition
        then BlockDiagonal(labels, {k ↦ force-step(UC(U_k, blocks[k], Δt))})
        else materialize → re-decompose
```

The R1 case is the gem of the framing: applying U to each φ_n preserves the outer-product structure exactly, so a single timestep on R1 stays in R1 at cost O(rank × cost(U)).

### eigendecomp : DensityTerm → Stream[(Real, Vector)]

The visitor returns a lazy stream rather than a closed list:

```
eigendecomp (OuterProductSum(φs, cs, _)) =
    -- when basis vectors are not orthonormal, perform an inner orthogonalization;
    -- when they are, scalars cs are already the eigenvalues
    if mutually_orthonormal(φs)
        then Stream.from_list(zip(cs, φs))
        else iterative procedure that builds a tridiagonal projection of γ̂
             via repeated γ̂·v starting from random seed; emit Ritz pairs lazily

eigendecomp (BlockDiagonal(labels, blocks)) =
    Stream.flatten({k ↦ eigendecomp(blocks[k]) for k in labels})
        |> Stream.merge_by_eigenvalue

eigendecomp (SparseInBasis(...)) =
    iterative procedure that builds a tridiagonal projection of γ̂ via
    repeated γ̂·v, using `apply` as the matrix-vector primitive

eigendecomp (UnitaryConjugation(U, inner, _)) =
    eigendecomp(inner)
      |> Stream.map (λ(λ_n, v_n) → (λ_n, U.apply(v_n)))    -- eigenvalues preserved
```

The last clause is a key rewrite: under a unitary conjugation, **eigenvalues are invariants**, only eigenvectors transform. This is one of those algebraic moves that a term-rewriting framing captures cleanly.

### density : DensityTerm → RealFunction

The diagonal-in-position visitor:

```
density (OuterProductSum(φs, cs, basis)) =
    λr. Σ_n cs[n] * |φs[n](r)|²

density (BlockDiagonal(labels, blocks)) =
    λr. Σ_k density(blocks[k])(r)         -- crystal Bloch sum

density (SparseInBasis(entries, basis, _)) =
    λr. Σ_{(i,j,x)} x * basis.ψ_i(r) * basis.ψ_j(r).conjugate

density (BasisChange(T, inner)) =
    -- density is basis-change invariant in r-space; recurse and ignore T
    density(inner)

density (UnitaryConjugation(U, inner, _)) =
    -- generally NOT invariant; force materialization or push U through
    density(force-step(UnitaryConjugation(U, inner, _)))

density (LinearCombination(pieces)) =
    λr. Σ_n a_n * density(γ_n)(r)
```

`density` is a fold: it produces a `RealFunction` (a callable in r) from the tree. Notice the **shortcut rule** at `BasisChange` — density is invariant under unitary basis changes, so the visitor's clause for `BasisChange` recurses into `inner` and discards `T`. This is the term framing earning its keep: a per-operation algebraic identity becomes a per-clause optimization, statically.

### The remaining operations

- `apply_op` composes another linear operator on the left or right. The simplest cases produce `LinearCombination` or `OuterProductSum` (when the result is still low-rank); the general case forces materialization in a specific encoding.
- `trace` is a one-liner per production: sum scalars (R1); sum traces of blocks (R2); sum diagonal entries (R3); fall through `BasisChange` (trace is basis-invariant); fall through `UnitaryConjugation` (trace is conjugation-invariant); linear over `LinearCombination`. **This is the most elegant operation in the framing** — every clause is one line and uses a known algebraic identity.
- `restrict` typically returns `Restriction(γ̂, S)` as a deferred node; on `OuterProductSum` it can immediately project each φ_n.
- `basis_change` is `BasisChange(T, γ̂)` symbolically. Forcing it is the work; **deferring it lets multiple compositions cancel** (`BasisChange(T_inverse, BasisChange(T, γ̂))` rewrites to `γ̂`).

## 4. Invariants

The invariants — self-adjoint, idempotent (closed-shell), trace = N — are managed on a **type-level axis orthogonal to the production axis**, using a triple of phantom tags:

```
DensityTerm<sa : Bool, idem : Bool, tr : Option[Real]>
```

The **type system enforces propagation**: visitor signatures advertise which tags they preserve. The signatures look like:

```
apply<sa, idem, tr> :
    DensityTerm<sa, idem, tr> × Vector → Vector

timestep<sa, idem, tr> :
    DensityTerm<sa, idem, tr> × UnitaryOp × Real → DensityTerm<sa, idem, tr>

basis_change<sa, idem, tr> :
    DensityTerm<sa, idem, tr> × BasisTransform → DensityTerm<sa, idem, tr>

restrict<sa, idem, _> :
    DensityTerm<sa, idem, _> × Subspace → DensityTerm<sa, idem, None>
        -- restriction breaks trace; sa and idem survive

apply_op<sa, _, _> :
    DensityTerm<sa, _, _> × LinearOp → DensityTerm<false, false, None>
        -- general composition kills everything but maybe self-adjointness
        -- if the other op is also self-adjoint (and they commute)
```

This is enforced at compile time for `timestep`, `basis_change`, `density`, `trace`: the visitor declares it preserves the tag, the type system propagates the tag through, and any constructor that *would* break the tag fails to type-check.

Some invariants are inherent in the structure rather than enforced by tags:

- `OuterProductSum` with positive scalars is automatically trace-positive. The type tag for `tr` can carry the exact computed value (`Some(Σ c_n)`).
- `BlockDiagonal` is automatically self-adjoint iff each block is; the type tag composes.
- `BasisChange(T, inner)` preserves self-adjoint iff T is unitary. The type tag for `T` carries `unitary : Bool`, and the constructor signature requires it.
- `UnitaryConjugation` preserves all three tags by construction.

**Where the tag axis leaks** (and this is real, not theoretical):

1. `LinearCombination(pieces)` is generally not self-adjoint, not idempotent, and has trace = Σ a_n * tr(γ_n). The type tag for the result is `<false, false, computed>` unless the coefficients and pieces conspire to keep self-adjointness (e.g., paired Hermitian conjugates with real coefficients).
2. `OuterProductSum` is always self-adjoint *only when the scalars are real*. The signature must require `scalars : List[Real]` (not `Complex`), and the type system catches violations.
3. `SparseInBasis` is self-adjoint only when `entries` are symmetric — `(i,j,x)` paired with `(j,i,x*)`. The constructor can enforce this by accepting only the upper triangle and implicitly mirroring, but that's a structural commitment.
4. `Restriction(γ̂, S)` always breaks `tr = N` (we lose the trace outside S). The type tag flips from `Some(N)` to `None`.

So the orthogonality is **mostly true but with explicit erasure points**. The framing is honest about this: the type system tracks the loss precisely. Whenever an operation cannot guarantee a tag, the tag is downgraded — never silently asserted.

## 5. Time evolution

The single-step rule, as shown in §3:

```
timestep(γ̂, U, Δt) = UnitaryConjugation(U, γ̂, Δt)
```

is **O(1)** and **invariant-preserving by construction**. The type system propagates `<sa, idem, tr>` through. Composition over many steps yields:

```
γ̂(Δt)       = UC(U_1, γ̂_0)
γ̂(2Δt)      = UC(U_2, UC(U_1, γ̂_0))
...
γ̂(1000 Δt)  = UC(U_1000, UC(U_999, ..., UC(U_1, γ̂_0) ...))
```

The tree grows by one node per step. **This is the framing's biggest structural problem** for 1000-step trajectories. Two strategies for managing it:

**Strategy A — eager partial reduction with a normalization rule.** Add a rewrite rule:

```
UC(U_b, UC(U_a, inner, Δt_a), Δt_b) → UC(U_b · U_a, inner, Δt_a + Δt_b)
```

This collapses nested conjugations into a single one whose unitary is the *product* of the constituent unitaries. **But this defeats the purpose** — multiplying the unitaries is itself expensive, especially when each U_n depends on γ̂(n·Δt), which we have not yet materialized. The closure is nonlinear, so we cannot bypass that dependency by simple algebraic merging.

**Strategy B — periodic materialization.** Choose a stride S (say S = 10). Every S steps, force the accumulated tower of `UC` nodes down to a concrete production — typically R1 by re-orthogonalizing the propagated outer-product vectors:

```
force-step^S (UC(U_S, UC(... UC(U_1, OuterProductSum(φs, cs, b))))) =
    -- propagate each φ_n through all S unitaries (cost: S × rank × cost(U))
    -- reorthogonalize (cost: rank² × dim)
    OuterProductSum(orthonormalize(U_S · ... · U_1 · φs), cs, b)
```

Strategy B is the realistic one. The trade-off is choosing S: smaller S → more re-orthogonalization overhead; larger S → larger tree, deeper recursion in visitors, eventually loss of orthogonality through numerical drift in the deferred unitaries.

**Self-consistency wrinkle.** Each U_n must be built from Ĥ[γ̂(n·Δt)], which depends on γ̂ at that step. If we defer, we have not yet *constructed* U_{n+1} — we cannot construct it until we have evaluated γ̂(n·Δt). So deferral is bounded by the closure: in practice, the term tree is only meaningfully "deferred" when the operator U_n can itself be expressed as a function of the unforced γ̂ (e.g., via Hartree-Fock-style closures expressible as further term constructors).

This is the central tension the framing introduces. **A pure term framing wants to defer; the physics demands frequent materialization.** The natural resolution is to *defer within a single SCF iteration and materialize at iteration boundaries* — which gives a hybrid lazy/strict pattern, but not an arbitrarily lazy one.

## 6. Computational expressivity

**Naturally expressed:**

- Encoding choice as production tag. Every visitor sees the outermost production explicitly.
- Algebraic identities as rewrite rules. `trace(UC(U, γ, Δt)) ⟶ trace(γ)`, `BasisChange(T_inv, BasisChange(T, γ)) ⟶ γ`, `eigendecomp(UC(U, γ)) ⟶ unitary-transformed eigenvectors with preserved eigenvalues` — these are clauses on the visitor or one-liners in a separate rewriter.
- Lazy composition. The deferred `UC` node accumulates work without committing to a representation.
- Multi-resolution structure. `BlockDiagonal(labels, {k ↦ OuterProductSum(...)})` is the natural form for a Bloch-decomposed low-rank ground state — the recursion through productions is essentially free.
- Invariants as types. The phantom-tag axis is a CS-natural way to encode "this term is provably self-adjoint."

**Awkwardly expressed:**

- **Iterative numerical procedures.** Lanczos-style iteration is just a loop calling `apply` repeatedly. It does not need to be in the grammar; it sits *above* the grammar as ordinary code. But this means the framing does not, by itself, give us a way to talk about "approximate γ̂" or "γ̂ to k-step Krylov precision" — those are inherent to the consumer, not the term.

- **Nonlinear closures.** Ĥ[γ̂] depends on γ̂. The construction `apply_op(Ĥ[γ̂], γ̂)` references γ̂ twice. In the term framing, both references must point to the **same node** (structure sharing) or we double the work and risk inconsistency. The grammar does not have native sharing; we have to model it as a let-binding or as a directed acyclic graph rather than a strict tree. The cleanest formulation is:

  ```
  Closure ::= LetTerm(name : Symbol, value : DensityTerm, body : Expr)
            | RefTerm(name : Symbol)
  ```

  with `Expr` ranging over operator-valued expressions that can use `RefTerm(name)`. Now `apply_op(Ĥ[γ̂], γ̂)` becomes `LetTerm(g, γ̂, apply_op(make-H(RefTerm(g)), RefTerm(g)))`. **This is a real extension of the grammar** — a DAG layer on top of the tree.

- **Nonlocal operations.** Computing a matrix element of γ̂ between two specific basis functions is awkward in `OuterProductSum` (requires evaluating φ_n at two indices), trivial in `SparseInBasis`. The grammar reflects this asymmetry honestly, but means uniform numerical interfaces require per-production glue.

- **Continuous-parameter sweeps.** Frequency-resolved response χ(ω) is a function of ω; in a term framing we either lift ω into the grammar (a new constructor `FrequencyParameterized(ω ↦ DensityTerm)`) or treat ω as a free variable in the consumer.

**Where we bend the framing:**

The biggest bend is the **DAG / sharing extension** for self-consistent closures (above). A second bend is **materialization rules that depend on numeric tolerances** — the rewrite "collapse UC(U_b, UC(U_a, ...))" depends on whether the U's commute, which is a numerical question with a tolerance, not a clean algebraic one. Term rewriting systems classically assume exact algebraic equality; here we have approximate equality, which makes confluence and termination *much* harder to reason about formally. We essentially abandon any hope of "proving the rewrite system is confluent" — in practice we maintain a normal form by convention rather than by theorem.

## 7. Speed/efficiency profile

The cost picture is **encoding-determined for primitives, accumulation-determined for compositions, and materialization-cost-driven for time evolution**.

**Per-operation costs (with N = Hilbert dimension, r = rank, B = block count, nnz = nonzeros, M = basis size):**

| Operation | OuterProductSum (R1) | BlockDiagonal (R2) | SparseInBasis (R3) |
|---|---|---|---|
| apply (γ·v) | O(r · N) | Σ_b O(cost(block_b)) | O(nnz) |
| trace | O(r) | Σ_b O(trace cost) | O(M) [diagonal entries] |
| density | O(r · N) per r | analogous | O(nnz·support²) per r |
| eigendecomp | O(r · N) if orthonormal; iterative otherwise | per-block | iterative, O(k·nnz) |
| basis_change | O(r · cost(T)) | O(B · per-block) | O(nnz · cost(T)) |
| restrict | O(r · cost(S)) | O(B · per-block) | O(nnz · cost(S)) |
| timestep (deferred) | O(1) | O(1) | O(1) |
| timestep (forced) | O(r · cost(U)) | per-block | O(M² · cost(U)) — expensive |

**Composition costs.** A visitor over a tree of depth d costs the sum of per-node costs. Composition is therefore additive: `density(apply_op(Ĥ, γ̂))` costs `cost(density on the apply_op result)` plus the cost of constructing that result. Because visitors are not fused automatically, repeated visits over the same tree incur repeated traversal — **traversal fusion is a separate optimization** at the visitor level (a "deforestation" pass, in functional-programming terms).

**Materialization timing.** The bottleneck is the period at which we collapse deferred `UC` towers. Three cost regimes:

- *Aggressive (S = 1)*: never defer. Every timestep produces a fully reduced term. The term framing buys nothing over a direct numerical representation.
- *Lazy (S = 1000)*: defer everything until a measurement. Each measurement (e.g., density) recursively visits the tower; each node in the tower applies one U to the visit. The traversal cost is O(steps × cost(U × visit)).
- *Hybrid (S = 10–100)*: amortizes re-orthogonalization cost. This is the realistic regime.

**What's fast:**

- `trace` is O(r) on R1 and additive across blocks. Sub-linear in N.
- `density` at a single r is O(r) on R1.
- Deferred timestep is O(1).
- Algebraic rewrites that exploit invariants (trace under UC, eigenvalues under UC, density under BasisChange) make these operations essentially free in the right encoding.

**What's slow:**

- Cross-encoding operations. `apply` of a `SparseInBasis` γ̂ to a vector expressed in the plane-wave basis requires a basis-change of the vector first, costing O(M · M_pw).
- Forced timestep on R3. Sparse·sparse multiplication is structurally expensive, and the result is often denser than the inputs.
- The first `density` evaluation that forces a deep `UC` tower — the visitor walks the entire tree.

**Bottlenecks unique to the framing:**

- Traversal overhead. Every operation must walk a tree. For deeply nested terms this is non-trivial dispatch overhead atop the numeric work.
- Rule combinatorics. With P productions and O operations, we have P·O visitor clauses (49 for the seed grammar above), each potentially with its own optimization branches.
- Materialization decisions. Choosing *when* to force is a policy that affects performance dramatically and is not captured by the term itself — it lives in the visitor strategy.

## 8. Generalization

**BSE kernel (4-index, sparse in particle-hole channels):**

The grammar generalizes naturally if we lift from rank-2 (matrix-shaped) to rank-4 (tensor-shaped) constructors. Productions become:

```
BSEKernelTerm ::=
    LowRankParticleHole ( ph_modes : List[PHMode]
                        , scalars  : List[Real] )                     -- analog of R1
  | BlockByChannel      ( channels : Map[ChannelLabel, BSEKernelTerm] ) -- analog of R2
  | SparseInProductBasis( quadruples : List[(I, J, K, L, Real)]
                        , basis      : ProductBasisRef
                        , cutoff     : Real )                          -- analog of R3
  | LadderCombination   ( pieces : List[BSEKernelTerm] )
  | BasisChange         ( ... )
```

The structural analogy is **exact**: low-rank decomposition (here in *particle-hole modes* rather than orbitals), block decomposition by channel quantum numbers, sparse in a localized product basis. The visitors port directly. The natural rewrite "BSE kernel applied to ph propagator via the BSE Dyson equation" becomes another visitor clause: `applyKernel(LowRankParticleHole(modes, cs), L) = Σ_n cs[n] * outer(modes[n], modes[n] · L)`.

So yes — Hole 2 fits.

**BTE collision matrix (4-index, sparse in energy-conserving channels):**

Same structural ports:

- "Low rank in scattering modes" = `LowRankInScatteringChannels`
- "Block-diagonal in conserved momentum/energy" = `BlockByConservedLabel`
- "Sparse in mode-pair space with energy-window cutoff" = `SparseInModePairBasis`

The energy-conservation constraint becomes a *cutoff parameter* in the sparse production (analogous to the spatial cutoff in R3). Visitors port. Hole 3 fits.

**The shared structure across all three:**

```
TypedTermAlgebra<rank, invariants> ::=
    LowRankDecomposition   ( modes : List[Mode^rank], scalars : List[Real] )
  | BlockDecomposition     ( blocks : Map[QuantumNumber, Self] )
  | SparseInLocalizedBasis ( entries : List[(Index^rank, Real)], basis, cutoff )
  | DeferredTransform      ( op : BasisTransform | Unitary | Restriction, inner : Self )
  | LinearCombination      ( pieces : List[(Real, Self)] )
```

This is the **generic core** that handles all three holes by parameterization on rank and invariant set. The framing therefore *does* unify the three. The cost is a generic-programming layer — but conceptually the abstraction is clean.

## 9. Inherent weaknesses

In order of severity:

**(a) Materialization is the central tension.** The framing wants to defer (that's where the elegance lives); the physics wants to materialize often (self-consistent closures). The honest position is that the framing's "term as datum" pattern earns most of its keep on **short trees** — a single timestep, a single measurement composed of a handful of operations. For long-running self-consistent dynamics, the tree gets collapsed often enough that the algebraic-rewrite advantage erodes. The framing's natural sweet spot is *not* exactly the n-Op application.

**(b) Rule combinatorics.** P productions × O operations = O(P·O) visitor clauses. For the seed grammar, that's 7 productions × 8 operations = 56 clauses, plus rewrite rules. Many clauses share machinery (the `LinearCombination` case is always "fan out and sum"), but the bookkeeping is real. There is no escape from this in the framing — *every operation must handle every production*.

**(c) DAG sharing for self-consistent closures.** A pure term tree cannot express `apply_op(Ĥ[γ̂], γ̂)` without either an explicit `LetTerm`/`RefTerm` extension (turning the tree into a DAG) or duplicating γ̂ (numerically wasteful and semantically wrong if γ̂ is approximate). This extension is straightforward but it's an extension; the framing does not naturally provide it.

**(d) Approximate equality breaks the algebraic-rewrite story.** Term rewriting systems are at their cleanest under exact equality. With floating-point numerics, "U_a and U_b commute" is a tolerance question; "this rewrite preserves trace to within ε" is a numerical claim. Confluence and termination become empirical, not theoretical. We lose the formal guarantees that motivate the term-rewriting approach in the first place.

**(e) Traversal overhead.** Every operation walks the tree. For deep trees this is dispatch overhead on top of the numeric work. Visitor fusion (deforestation) is possible but adds yet another layer.

**(f) The orthogonality of the type-tag axis leaks.** As discussed in §4, `LinearCombination`, `Restriction`, and `OuterProductSum` (when scalars are complex) require the type system to track invariant loss explicitly. The clean "tags are orthogonal to productions" story has visible erasure points.

**(g) Iterative numerics live above the framing.** Lanczos and related procedures use `apply` as a black box; they are not in the grammar. This is *fine* but it means the framing does not describe the most expensive parts of the workflow — it only describes the data and its algebraic identities, not the iterative procedures that consume it.

**(h) Encoding choice is policy, not data.** Whether a `BlockDiagonal` block should be in R1 vs R3 depends on the system, the temperature, the truncation choice — and that choice has to be made *outside* the grammar by whichever code constructs the term. The framing makes the choice visible but does not help us *make* it.

## 10. Cross-framing position

Compared to the other three framings:

**vs Framing B (codata / coalgebraic).** The deepest contrast. Framing B says γ̂ is *defined by what you can observe of it* — it is a coalgebra (a function `γ̂ → Observation × γ̂`) rather than a constructor. Framing A says γ̂ is *defined by how it was built* — explicit constructors, visible production tag. The two are dual in a precise mathematical sense (initial algebra vs final coalgebra).

The practical consequence: Framing A makes encoding **explicit and visible** (a node carries its production tag); Framing B makes encoding **hidden and uniform** (you only see the observations you can take, not the internal representation). For visitors that *need* to know the encoding to be efficient (like the algebraic shortcut `density(BasisChange(T, inner)) = density(inner)`), Framing A wins. For uniform consumers that just want to ask γ̂ for an observation, Framing B wins.

A hybrid is natural: implement Framing B's observation interface *as a visitor* over Framing A's term. The term is the data; the codata interface is the consumer API.

**vs Framing C (e-graph with equality saturation).** Framing C *extends* Framing A. An e-graph is a data structure that holds many equivalent terms in a compact shared form and applies rewrite rules in saturation to discover all equivalent forms. Framing A picks *one* form and rewrites it in place; Framing C maintains *all* forms simultaneously and extracts the best one according to a cost model.

The practical consequence: Framing C automates the encoding-choice problem that Framing A leaves to the constructor (weakness h above). If we have many possible representations of the same γ̂ and want the optimizer to pick the cheapest one for a given consumer, Framing C is the upgrade path. The cost is the e-graph machinery itself (potentially expensive to maintain) and the loss of the simple term structure (the tree becomes a graph with equivalence classes).

**vs Framing D (tensor network with cost-aware contraction).** Framing D is largely orthogonal to Framing A but partially overlapping. A tensor network is a specific *encoding* of an operator as a contraction graph — it would, in Framing A's vocabulary, be yet another production:

```
| TensorNetworkContraction ( nodes : List[Tensor]
                           , edges : List[ContractionEdge] )
```

Framing D's cost-aware contraction ordering is a *visitor strategy* for evaluating that production. So Framing A could absorb Framing D as one more constructor (with its own visitor clauses). But Framing D's distinctive contribution — the contraction-order optimization — is a complex visitor strategy that does not fit naturally into the simple-pattern-match style of Framing A. It is essentially a small embedded optimizer.

For γ̂ specifically, Framing D's tensor-network encoding is most natural for **strongly correlated** systems (MERA, MPS-like decompositions); the encodings R1/R2/R3 we're chartering here are *weakly correlated* (effectively single-particle). So Framing D overlaps with Framing A's encoding axis but for a different physics regime. If n-Op cares about strongly correlated systems eventually, the grammar grows a tensor-network production; if not, Framing D solves a problem we don't have.

**Synthesis.** The four framings partition naturally:

- A = explicit terms with manually-managed rewrites (current charter)
- B = abstract observations over hidden state (consumer interface)
- C = A's terms maintained as equivalence classes for automated optimization
- D = a specific encoding (tensor network) with sophisticated cost-aware evaluation

A and B are the *baseline* — every implementation has both data and a consumer interface, however implicit. The question is whether C's automated rewriting and D's contraction-ordering machinery pay for themselves *given the operations n-Op actually needs*. For γ̂ in n-Op (Born-Oppenheimer L1, low rank, frequent self-consistent updates), my best honest assessment from this framing's vantage point is:

- A's encoding-explicit grammar is **the right place to *start***. It makes the structural decisions visible and lets visitors be written cleanly per encoding.
- A's algebraic-rewrite layer **pays off best for the trace, basis-change, and eigenvalue-preserving identities** — the cheap-to-prove, large-payoff rewrites. The rule combinatorics get heavy fast beyond those.
- The framing **fights γ̂ at the self-consistent time-evolution boundary**: deferred trees collide with nonlinear closures, and materialization stride S becomes a policy with no in-framing justification.
- Generalization to BSE and BTE is **clean and structural**, giving the framing a unification advantage across the three feasibility holes.
- The framing's natural successor, if its limits bind, is **Framing C** (e-graph) — promoting the manual rewriting into automated equality saturation. Framing B and Framing D address orthogonal concerns and combine more readily than they replace.

The cleanest summary: Framing A is the **right substrate for the data** and the **right place for the cheap algebraic identities**, but it is *not by itself* a complete answer for γ̂'s time-evolution lifecycle. It is the necessary backbone of any answer; it is not the whole answer.

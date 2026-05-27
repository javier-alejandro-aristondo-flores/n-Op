I'll research this thoroughly. Let me first read the optional context files to ground myself in the project specifics, then produce the structural report.
I'll proceed with read-only research and return findings in my final message (not writing any plan file — this is a research deliverable, not an execution plan).
I have enough context now. Let me also check the BSE/BTE references for the generalization section.
I have sufficient grounding. Now I'll write the detailed report directly as my final message — no plan file needed since this is a research deliverable, not an execution plan.

---

# Framing D Research Report: Tensor Network with Cost-Aware Contraction Ordering for γ̂

## 0. Framing thesis in one paragraph

γ̂ is treated as **a single typed node embedded in a computation graph of multilinear arrays**. The graph is a DAG whose vertices are tensors (each carrying a `node_type` describing its internal structure) and whose edges are **contraction obligations** — pairs of named index labels declared equal. Every operation on γ̂ produces a *new* graph by appending nodes and edges; **nothing is actually summed-out** until a downstream consumer demands a concrete tensor. At demand time, a separate optimizer walks the pending graph and emits a **contraction-order plan** — a schedule that picks intermediate tensors so as to minimize a chosen cost model. The three encodings R1, R2, R3 become **node-type tags with structural constraints**, and conversions between them are graph rewrites. Invariants survive as **typed equalities on the DAG** plus a small set of structural symmetry tags.

The framing's central bet is that **γ̂ rarely stands alone**. It is almost always *applied to* a vector, *traced against* an observable, *commuted with* a self-adjoint linear map, or *projected onto* a subspace. The structural value of the tensor-network framing is realized in those compositions, not in storing γ̂ in isolation.

---

## 1. Representation

### 1.1 Core types

```
IndexLabel        = Symbol                       -- e.g. r, r', n, k, σ
IndexDomain       = { size:        Int,
                      kind:        Spatial | Orbital | Spin | Bond | Block
                      symmetry:    Option[GroupAction] }
Index             = { label: IndexLabel, domain: IndexDomain }

TensorData        = Dense        (raw: NDArray)
                  | Sparse       (pattern: SparsityPattern, values: NDArray)
                  | LowRank      (factors: List[Tensor], bond: List[Index])
                  | BlockDiag    (block_index: Index, blocks: Map[BlockLabel, Tensor])
                  | Subnetwork   (network: Network)              -- recursive

Symmetry          = SelfAdjoint(swap: Pair[IndexLabel])          -- index swap + conjugate
                  | Idempotent
                  | TraceFixed(value: Scalar)
                  | NonNegative
                  | Unitary

Tensor            = { node_id:     NodeId,
                      indices:     List[Index],
                      data:        TensorData,
                      symmetries:  Set[Symmetry] }

ContractionEdge   = { left: (NodeId, IndexLabel),
                      right: (NodeId, IndexLabel) }              -- declares these indices contracted

Network           = { nodes:     Map[NodeId, Tensor],
                      edges:     Set[ContractionEdge],
                      open:      List[(NodeId, IndexLabel)],     -- the network's external indices
                      schedule:  Option[ContractionSchedule] }

ContractionStep   = { left: NodeId, right: NodeId,
                      contracted_pairs: List[(IndexLabel, IndexLabel)],
                      result_node: NodeId,
                      cost_estimate: Cost }

ContractionSchedule = List[ContractionStep]   -- DAG-ordered

CostModel         = (Tensor, Tensor, List[(IndexLabel, IndexLabel)]) → Cost
                    where Cost = { flops: BigInt, peak_memory: BigInt, intermediate_rank: Int }
```

### 1.2 γ̂ as a network

γ̂ is **always represented as a `Network` with two open indices** — `(γ_out_row, γ_out_col)` — both ranging over the spatial domain. The interior may be:

- a single dense node (degenerate full materialization),
- a `LowRank` node (R1),
- a `BlockDiag` node (R2),
- a `Sparse` node (R3),
- a `Subnetwork` (compositions, response calculations, time-evolved γ̂).

The key signature:

```
Gamma : Type = Network with open == [γ_out_row : Spatial, γ_out_col : Spatial]
                       and  γ_out_row.domain == γ_out_col.domain
                       and  symmetries ⊇ { SelfAdjoint(swap=(γ_out_row, γ_out_col)),
                                          TraceFixed(N) }
```

The two-index-on-the-outside discipline means γ̂ presents the same external shape regardless of internal encoding — consumers can treat γ̂ uniformly and the optimizer specializes per encoding when it needs concrete cost.

### 1.3 What lives where

- **Open indices** of a `Network` are the user-visible "shape" of γ̂.
- **Internal bond indices** of a `LowRank` node are private contractions hidden behind the node-type tag. They never appear in the outer open index list.
- **Block labels** of a `BlockDiag` node are a quotient/refinement of an external index: the external index is logically the disjoint union of the per-block index ranges.
- **Sparsity patterns** of a `Sparse` node live in `TensorData.pattern` and are themselves typed (e.g. `BandedPattern(half-bandwidth)`, `NeighborPattern(graph)`, `CutoffPattern(distance, basis)`).
- **The contraction schedule is *not* part of the network's identity** — two networks differing only in `schedule` are observationally equivalent.

---

## 2. Encodings

R1, R2, R3 are **first-class node types**. They are not dispatched-by-class polymorphism; they are *constructors* of the `TensorData` algebraic data type, and each carries the structural invariants its encoding implies.

### 2.1 R1 — low-rank outer product

```
γ̂_R1  : Gamma  =  Network
  { nodes  = { sum_node: Tensor with data = Dense(c : NDArray[ranks]),
              orb_node: Tensor with data = Dense(φ : NDArray[ranks, spatial]),
              orb_conj: Tensor with data = Dense(φ̄ : NDArray[ranks, spatial]) },
    edges  = { (sum_node.rank, orb_node.rank),
              (sum_node.rank, orb_conj.rank) },
    open   = [ orb_node.spatial   ↦ γ_out_row,
              orb_conj.spatial   ↦ γ_out_col ],
    symmetries = { SelfAdjoint, TraceFixed(N), ... } }
```

Equivalently, packaged: `LowRank(bond_dim = ranks, factor_tensors = [orb_node, orb_conj], scalars = c)`. The two factors share a contracted "bond" index of size `ranks`. The bond is the rank.

### 2.2 R2 — momentum-block diagonal

```
γ̂_R2  : Gamma  =  Network
  { nodes  = { gamma_block:
                 Tensor with data = BlockDiag
                   { block_index = k : Index (domain = momentum mesh, size N_k),
                     blocks      = { k_i ↦ small_dense_self_adjoint_node
                                       with indices = [band_in_k, band_in_k'] } } },
    open   = [ (k, band_in_k)        ↦ γ_out_row,
              (k, band_in_k')       ↦ γ_out_col ],
    edges  = ∅,
    symmetries = { SelfAdjoint per-block, TraceFixed(N), ... } }
```

The "open" indices are *paired* `(block_label, intra-block_index)`. R2 captures discrete translational symmetry by *factoring* the spatial index into `(momentum, within-momentum)`.

### 2.3 R3 — sparse-in-localized-basis

```
γ̂_R3  : Gamma  =  Network
  { nodes  = { gamma_sparse:
                 Tensor with data = Sparse
                   { pattern = NeighborPattern(adjacency_graph_with_cutoff R),
                     values  = NDArray[nnz] } },
    open   = [ ψ_idx_row ↦ γ_out_row, ψ_idx_col ↦ γ_out_col ],
    edges  = ∅,
    symmetries = { SelfAdjoint, TraceFixed(N), ... } }
```

`NeighborPattern` is itself a structured object — it carries the adjacency graph implied by a spatial cutoff in the localized basis. Operations consult it for cost estimates and for legal-fill checks.

### 2.4 Are they first-class?

**Yes** — each is a distinct `TensorData` constructor. **They are also dispatched**: at contraction-planning time the optimizer reads the node type to pick the cheapest concrete kernel. **They are also implicit** in the sense that a `Subnetwork` node can re-emerge as a different concrete encoding after the optimizer truncates intermediate bonds.

This is the framing's strength: the same `Gamma` type accommodates all three encodings simultaneously without losing identity. A `Subnetwork` produced by `apply_op(γ̂_R1, M_R3)` is *neither* purely R1 nor R3 — it lives as a pending graph until consumed.

### 2.5 Conversion between encodings = graph rewrite

```
to_R1  : Gamma → Gamma                                 -- eigendecompose, truncate to rank
to_R2  : Gamma × MomentumBasis → Gamma                 -- basis change + block-diagonalization detection
to_R3  : Gamma × LocalizedBasis × Cutoff → Gamma       -- basis change + cutoff (lossy)
```

Each is a *rewrite rule on the graph* — adds basis-change nodes around γ̂, contracts them in, then collapses the result through the relevant decomposition. The lossy ones carry an `accuracy_witness` field reporting how much weight was thrown away (this feeds the cert-as-first-class invariant from the project).

---

## 3. Operations

Every operation **builds a new network rather than producing a concrete value**. The concrete value materializes only when (a) a scalar is needed (e.g. `trace`, dot product against a vector), (b) the user explicitly forces materialization, or (c) the schedule reaches a node with no further consumers downstream.

### 3.1 apply : γ̂ × Vector → Vector

```
apply (γ : Gamma) (v : Vector) : Vector =
  let v_node = wrap_as_tensor(v, index = ψ_in)
  Network
    { nodes  = γ.nodes ∪ { v_node },
      edges  = γ.edges ∪ { (γ.γ_out_col, v_node.ψ_in) },
      open   = [ γ.γ_out_row ↦ result_index ],
      symmetries = ∅ }
```

The result is a `Network` with one open index. It is *not yet contracted*. When the consumer asks for the vector's values, the optimizer:

1. Reads γ̂'s node type.
2. Picks an order:
   - R1: `(φ̄ · v) → scalar coefficients → (φ · coefficients)` — cost `O(r·d) + O(r·d)` where r=rank, d=dim. The "obvious" matrix-vector cost order, but the optimizer *derives* it from the cost model rather than hard-codes it.
   - R2: for each block, contract `γ̂_k · v_k`. Cost `Σ_k size(block_k)·dim(block_k)`.
   - R3: stream-multiply across the sparsity pattern. Cost `O(nnz)`.
3. Returns the schedule.

**Crucial point**: the cost-aware optimizer is what makes the framing pay off in compositions. For `apply(γ̂, apply(M, v))`, the optimizer can choose to contract `γ̂·M` first or `M·v` first depending on intermediate ranks. With R1 γ̂ and dense M, contracting `M·v` first is far cheaper than forming `γ̂·M` first.

### 3.2 timestep : γ̂ × UnitaryOp × Δt → γ̂

```
timestep (γ : Gamma) (Ĥ : SelfAdjointOp) (Δt : Scalar) : Gamma =
  let U = exp_iH(Ĥ, Δt)         -- itself a Network, often a low-rank approximation
                                 -- e.g. truncated polynomial in Ĥ, evaluated by repeated apply
  let U_dag = dagger(U)
  Network
    { nodes  = U.nodes ∪ γ.nodes ∪ U_dag.nodes,
      edges  = ((γ.γ_out_row, U.right_open) ∪
                (γ.γ_out_col, U_dag.left_open) ∪
                γ.edges ∪ U.edges ∪ U_dag.edges),
      open   = [ U.left_open ↦ γ_out_row',
                U_dag.right_open ↦ γ_out_col' ],
      symmetries = { SelfAdjoint (induced by U Unitary + γ SelfAdjoint),
                    TraceFixed(N) (induced by U Unitary),
                    Idempotent (induced — if γ was idempotent) } }
```

The "result" is again a `Network`. Critically, **U and U†'s structure is the same node** — they share contractions through Ĥ, so the optimizer can recognize the shared subexpression. If U is built as a truncated polynomial expansion in Ĥ, the structure of the network reflects this; the schedule decides how many times to contract Ĥ-against-γ̂ before propagating outward.

### 3.3 eigendecomp : γ̂ → Stream[(λ, v)]

The framing handles eigendecomposition *operationally* through `apply`: an iterative procedure that builds a tridiagonal projection of γ̂ via repeated `apply(γ̂, v)` consumes only the network's `apply` interface.

```
eigendecomp (γ : Gamma) (k : Int) : Stream[(Scalar, Vector)] =
  iterative_tridiagonal_projection
    { matvec       = (λ v. materialize(apply(γ, v))),
      restart_dim  = ...,
      tol          = ... }
  → produces top-k (λ, v) pairs via small tridiagonal-matrix eigendecomp
```

The framing's contribution is that `matvec` runs at the cost of `apply` *in the cheapest encoding* — the eigensolver doesn't know whether γ̂ is R1, R2, or R3.

**Special case**: if γ̂ is R1 (closed-shell ground state with known rank), eigendecomp is *trivial* — the φ_n already *are* eigenvectors with eigenvalues c_n. The framing should detect this: when the node-type is `LowRank` with `c_n ∈ {0, 1}` and `SelfAdjoint`, eigendecomp returns the stored factors directly. This is a **rewrite rule on the schedule**, not a separate code path.

### 3.4 density : γ̂ → RealFunction (n(r) = γ̂(r,r))

```
density (γ : Gamma) : RealFunction =
  Network
    { nodes  = γ.nodes,
      edges  = γ.edges ∪ { (γ.γ_out_row, γ.γ_out_col) },  -- close the trace edge
      open   = [ (γ.γ_out_row, free) ↦ r_diag ],          -- but keep the r-axis open
      symmetries = { Real, NonNegative } }
```

Wait — that's not right; the diagonal needs careful expression. More precisely, `density` is **a partial trace that keeps one spatial index open**:

```
density (γ : Gamma) : RealFunction =
  -- introduce a δ-node identifying γ_out_row and γ_out_col, leaving one open
  let δ = Tensor with data = Sparse(diagonal pattern),
                   indices = [r_in, r_out],
                   wires = identity
  Network
    { nodes  = γ.nodes ∪ { δ },
      edges  = γ.edges ∪ { (γ.γ_out_row, δ.r_in), (γ.γ_out_col, δ.r_out) },
      open   = [ δ.r_out ↦ r_diag ],
      symmetries = { Real, NonNegative, IntegratesTo(N) } }
```

Per-encoding cost:
- R1: density(r) = Σ_n c_n |φ_n(r)|² — cost O(r·d).
- R2: per-momentum-block trace, then sum across blocks weighted by Bloch envelopes — cost O(N_k · block_size · d_per_block).
- R3: read the diagonal of the sparse storage directly — O(d).

### 3.5 trace, restrict, basis_change, apply_op

```
trace (γ : Gamma) : Scalar =
  Network with all open indices closed via δ-nodes; materializes to a Scalar.
  -- By the TraceFixed(N) symmetry, evaluation of trace is statically known to be N.
  -- So trace(γ) returns the symbol N directly, no contraction needed.

restrict (γ : Gamma) (P : ProjectorTensor) : Gamma =
  Network with P sandwiching γ on both sides: P · γ · P.
  Result loses TraceFixed (now N' ≤ N), retains SelfAdjoint, may lose Idempotent.

basis_change (γ : Gamma) (U : BasisTransformTensor) : Gamma =
  Network: U · γ · U†.  Preserves SelfAdjoint, TraceFixed, Idempotent.
  Often used to switch encoding tag: basis_change to localized basis enables R3 detection.

apply_op (γ : Gamma) (M : LinearOp) : LinearOp =
  Network with γ.γ_out_col contracted to M.left_open.
  Returns a new Network of LinearOp type with γ̂'s row and M's right indices open.
```

---

## 4. Invariants

Three invariants must hold: self-adjoint, idempotent (closed-shell), trace = N. The framing offers three layers of enforcement; each invariant uses the layer where it is cheapest and most rigorous.

### 4.1 Self-adjoint — structural symmetry tag

`SelfAdjoint(swap=(γ_out_row, γ_out_col))` lives in `Tensor.symmetries`. **Type-level** enforcement at all interface boundaries: any function returning `Gamma` must produce a network with this tag. The tag carries a verifier:

```
SelfAdjoint.verify (T : Tensor) (swap : Pair[IndexLabel]) : Either[Witness, Failure]
```

For an R1 node, verification is structural: `factor_tensors[0] == conjugate(factor_tensors[1])`. For R2, each block must be self-adjoint. For R3, the sparsity pattern must be symmetric and `values[i,j] == conj(values[j,i])`. The verifier runs on demand and can be required by `cert` (which would catch any rewrite that silently breaks it).

### 4.2 Idempotent — tensor equation `γ̂ · γ̂ = γ̂`

This is **the hardest invariant** for this framing. It is structurally enforced *only* in R1 with closed-shell-known coefficients (`c_n ∈ {0, 1}` and `φ_n` orthonormal — both checkable). For arbitrary `LowRank`, the framing can express idempotency as a node-level constraint: `c_n^2 = c_n ∧ orthonormal(φ_n)` (verified once when the node is constructed). For R2, the constraint is per-block.

For R3 — the worst case — **idempotency is not naturally expressible**. A sparse matrix being idempotent doesn't follow from any local sparsity pattern; sparsity + idempotency together would require `γ̂ · γ̂` to fit the same sparsity pattern, which fails generically. R3 of an idempotent γ̂ is *approximate* — it discards small entries beyond the cutoff, and `(R3 of γ̂)² ≠ R3 of γ̂` in general. So the framing acknowledges: **R3 is fundamentally an approximation; the idempotency invariant is sacrificed up to a cutoff-controlled error**.

The most operational treatment: carry an `Idempotent` tag with a *witness slot* (the residual `‖γ̂² − γ̂‖`). The cert system reads this witness and rejects/warns when it exceeds tolerance.

### 4.3 Trace = N — symbolic constant

`TraceFixed(N)` is the easiest. Tag-level enforcement: any operation that *would* change the trace either (a) preserves trace because of structural identity (basis_change, timestep), or (b) is forbidden, or (c) explicitly updates the tag (restrict updates `TraceFixed(N) → TraceFixed(N')`). The runtime `trace(γ)` operation **reads the tag and returns N without contracting**. If the user wants empirical verification, a separate `verify_trace` operation forces actual summation.

### 4.4 Type-level vs. runtime

| Invariant | Enforcement | Cost |
|-----------|------------|------|
| SelfAdjoint | Type tag + structural for R1/R2, pattern-symmetry for R3 | O(1) construction, O(nnz) verification |
| TraceFixed(N) | Type tag, propagated through trace-preserving operations | O(1) |
| Idempotent | Type tag with witness; structural only for R1 closed-shell | O(1) for R1; needs apply²-and-compare for R3 |

The cert obligations from the implementation plan (§13, "cert as first-class") map cleanly onto the tag/witness pattern: every typed boundary that emits a `Gamma` emits a cert sub-tree carrying the witnesses.

---

## 5. Time evolution

### 5.1 Single step

A single `timestep` returns a new `Gamma` network as described in §3.2. Critically, it **does not materialize** the resulting density matrix; it appends U and U† to the existing γ̂ network.

### 5.2 Composition across 1000+ steps

**Naïve composition is catastrophic.** After k steps, the network has appended 2k unitary blocks around γ̂. The network grows linearly in steps. Contracting it grows polynomially in step-count via repeated matrix products on whatever intermediate rank emerges.

Two mitigations are essential:

**(A) Bond-dimension truncation between steps.** After each step (or every few steps), the framing **forces contraction** of the recently-appended U and U† into γ̂, possibly through a re-decomposition that truncates to a target rank or sparsity cutoff. This is the tensor-network analog of "rounding" in TT/TR arithmetic: after performing operations symbolically, project back onto the manifold of small representations.

**(B) Fixed-rank evolution on a low-rank manifold.** If γ̂ is rank-r (R1), evolution by `U·γ̂·U†` *preserves rank exactly* if U is unitary — the eigenvectors rotate, eigenvalues stay. So R1 evolution is **structurally cheap**: just transport the factors:

```
timestep_R1 (γ_R1 : LowRank{factors=[φ, φ̄], scalars=c})
           (U : UnitaryNet) (Δt) : Gamma_R1 =
  LowRank { factors = [apply(U, φ), apply(U, φ̄)], scalars = c }
```

This is a **massive speedup**: O(r·d) per step instead of O(d²) for dense. Over 1000 steps the structure stays at rank r the whole way.

**(C) Block evolution in R2.** If U commutes with the momentum-block structure (which it does iff Ĥ commutes with translations — *not* the case under nonlinear closure where Ĥ depends on γ̂'s density, breaking translation in general), each `γ̂_k` evolves independently in its block. Time-evolved R2 stays R2; otherwise it leaks across blocks and degrades.

### 5.3 What happens to the structure over time

- **R1 evolution stays R1**, rank preserved. Drift: numerical precision loss in orthonormality of factors; requires periodic re-orthogonalization (a graph rewrite that inserts a Gram-Schmidt sub-network).
- **R2 evolution stays R2 iff translation symmetry is preserved by Ĥ**. Under nonlinear closure Ĥ[γ̂], a density perturbation can break translation; the framing must detect block-leakage (off-diagonal blocks growing) and either tolerate it (allow Subnetwork structure with R2 plus a small off-diagonal correction) or convert to a different encoding.
- **R3 evolution drifts to denser sparsity**. Unitary evolution generally spreads support; the cutoff has to be retuned, or the framing has to allow controlled expansion of the sparsity pattern.

### 5.4 The nonlinear closure (Ĥ[γ̂]) and the cycle

This is where the DAG abstraction strains. `Ĥ` is built from `γ̂`'s density, so the *operator* depends on the state it acts on. In graph terms:

```
γ̂ → density → v_eff → Ĥ → ... → applied to γ̂
```

This **breaks the DAG property**: γ̂ appears both as a source and as a sink in the same computation.

The framing's honest response: **the cycle is not handled inside the network — it is handled by an outer fixed-point iteration**. The network for one timestep is computed assuming `Ĥ` is built from γ̂(t) (no cycle inside the step). For SCF (the self-consistent ground state), the outer loop iterates `γ̂_{n+1} = solve(Ĥ[γ̂_n])` to convergence; each iteration is a *fresh* DAG. The cycle lives **above** the tensor-network layer.

This is acknowledged as a structural limitation: tensor networks are at their best when the operator and the state are statically separated. Self-consistency is handled by repeating the network, not by embedding the recursion in it.

For TD evolution: predictor-corrector schemes (or midpoint-rule schemes) treat the within-step cycle (Ĥ at the midpoint depends on γ̂ at the midpoint) by fixed-point iteration *within* the step. Again, the cycle lives in the outer loop, not the network.

---

## 6. Computational expressivity

### 6.1 What is naturally expressed

- **Compositions of γ̂ with linear operators of any structure.** `apply`, `apply_op`, `restrict`, `basis_change`, `timestep` are all *node-and-edge additions* to a network. The optimizer handles cost.
- **Multi-step pipelines.** `density ∘ timestep ∘ ... ∘ timestep ∘ γ̂` is a single network whose contraction order can be globally optimized.
- **Sparsity exploitation.** The optimizer reads `Sparse(pattern)` and can interleave dense-and-sparse contractions intelligently.
- **Low-rank exploitation.** `LowRank(bond)` lets the optimizer route through the bond instead of forming the dense version.
- **Symmetry exploitation.** Tagged symmetries (SelfAdjoint, Unitary) prune the search space.
- **Block-structured operators.** `BlockDiag` and `Sparse` with block-banded patterns are natural.

### 6.2 What is NOT naturally expressed

- **Spectral functions (eigenvalues, eigenvectors) as first-class.** The framing handles them via iterative procedures consuming `apply`, not as primitives. Asking "what is γ̂'s spectrum?" requires *running* an iterative algorithm — the framing doesn't store a spectrum.
- **Stream / lazy / coalgebraic structure.** A tensor network is fundamentally finite-shape. Infinite Krylov streams or coinductive spectral observers are bolted on outside.
- **Symbolic algebraic identities.** "γ̂·γ̂ = γ̂" is captured as a *constraint* with a witness, not as a *rewrite rule* the system can use to simplify. (This is where Framing A and C win.)
- **Cross-encoding identities discovered automatically.** "This R3 sparse matrix is actually low-rank when expressed in momentum basis" is not detectable without explicit rewrite rules.
- **Causal/temporal closures elegantly.** The fundamental DAG abstraction wants acyclic flow; SCF and TD self-consistency must live outside.
- **Per-orbital exact occupations and chemical-potential constraints**. The encoding stores `c_n` as opaque scalars; constraints like "exactly N of them are 1" demand external bookkeeping.

### 6.3 Where you bend the framing

- **Self-consistency**: outer loop, as discussed. Bending: the framing forces a clean iteration boundary that physics would prefer to be implicit.
- **Idempotency for R3**: it is fundamentally lost; you carry a witness and accept controlled error.
- **Pauli-spinor structure**: γ̂ has a `2 × 2 σ` index in the magnetic case. The framing handles this by adding a spin index; the open indices become `[γ_out_row × σ_row, γ_out_col × σ_col]`. The spin index is small (size 2), so cost is benign, but it adds noise to every signature.
- **Fermi–Dirac smoothing**: at finite T, occupations are `c_n = f(ε_n; T, μ)`. The framing accepts arbitrary scalars in R1, so this is fine — but the *coupling* of c_n to ε_n (the spectrum, which is downstream of γ̂) again forces an outer self-consistency loop on μ.

---

## 7. Speed / efficiency profile

### 7.1 Per-operation cost in each encoding

Let `d` = Hilbert-space dimension, `r` = rank, `N_k` = number of blocks, `b` = average block size (so `N_k · b = d` for R2), `s` = nnz of R3.

| Operation | R1 | R2 | R3 | Dense |
|-----------|-----|-----|------|--------|
| apply(γ, v) | O(r·d) | O(N_k · b²) = O(d·b) | O(s) | O(d²) |
| trace | O(1) (tag) | O(1) (tag) | O(1) (tag) | O(1) (tag) |
| density(γ) — full diagonal | O(r·d) | O(d·b) | O(d) | O(d²) memory bound |
| timestep (unitary U) | O(r·d²) per apply iteration, structure preserved | O(N_k · b³) if U respects blocks, else mixes | O(s · cost(U)) and pattern grows | O(d³) |
| eigendecomp top-k | O(k · cost(apply) · iters) | same | same | same |
| restrict (project onto subspace P_dim) | O(r · P_dim) | O(N_k · b · P_dim) | O(s · P_dim) | O(d²·P_dim) |
| basis_change | O(r·d²) | O(d²) — full mixing | O(d²) — destroys sparsity | O(d³) |
| convert to other encoding | varies | varies | varies | — |

Key wins: **R1 makes apply and timestep linear-in-d**; **R3 makes apply linear-in-nnz**; **R2 makes timestep block-parallel when symmetry holds**.

### 7.2 Composition cost across operations

This is the framing's pitch. Naïvely, `apply(γ̂, apply(M, apply(γ̂, v)))` runs at `3·cost(apply)`. With cost-aware contraction, the optimizer can detect that `(γ̂ · M · γ̂)` should be applied to v in a single contraction with intermediate structure chosen optimally. If γ̂ is R1 and M is R3, the optimizer can route as:

```
(φ̄ᵀ · M · φ) — a small r × r dense matrix
intermediate := (φ · [(φ̄ᵀ · M · φ) · (φ̄ᵀ · v)])
final := intermediate
```

This is O(r·d + r·s + r²) vs. O(d·s) for naïve order. The wider the operation chain, the more the optimizer matters.

### 7.3 Materialization timing

The framing's discipline: **never materialize until forced**. Materialization is forced at:

- Scalar consumers (`trace`, inner products with a vector).
- I/O boundaries (writing out a density n(r) for visualization).
- Encoding-change rewrites that require numeric values (e.g. truncating a `Subnetwork` back to `LowRank` requires a numerical SVD on materialized intermediate).
- The end of a time-step batch (rounding step).

Between materializations, the network grows. The cost-aware optimizer must amortize: holding off too long inflates the network until the optimizer search itself becomes expensive.

### 7.4 Bottlenecks

- **Contraction-order optimization is NP-hard.** Practical heuristics (greedy, simulated annealing, hypergraph partitioning — opt_einsum / cotengra-style) are subpolynomial in nodes but can dominate for large networks. For γ̂ in isolation (small network), it's irrelevant; in deep pipelines, it costs real time.
- **Bond-dim truncation requires SVD-like operations** that themselves cost O(d · r²) — manageable when r is small but the dominant cost in long evolutions.
- **Schedule construction** is per-shape, so if shapes are stable, schedules can be cached and reused. With γ̂ shapes stable over a TD trajectory, this caches well.

### 7.5 What's fast, what's slow, why

- **Fast:** R1 single-shot operations, repeated trace/density of static γ̂ (tag-only), local sparsity exploits in R3.
- **Slow:** any operation that conjugates γ̂ between encodings (R3 → R1 conversion is essentially SVD on a sparse matrix), schedule optimization on networks with hundreds of nodes, materializing the dense form for backup.

---

## 8. Generalization to BSE kernel and BTE collision matrix

The tensor-network framing **does generalize**, but with honest qualifications about *which* network shape fits each.

### 8.1 BSE kernel (4-index tensor)

The BSE kernel `K[occ, virt; occ', virt']` is a 4-index object indexed by occupied and virtual orbital indices. It exhibits **structured sparsity in particle-hole channels** — most entries are negligible, with peaks along channels where energy conservation holds.

Tensor-network candidates:
- **Tucker decomposition** `K = C ×₁ U_occ ×₂ U_virt ×₃ U_occ' ×₄ U_virt'` — useful if the kernel's *spectrum* concentrates on few channels.
- **CP / canonical-polyadic** `K = Σ_α u_α ⊗ v_α ⊗ w_α ⊗ x_α` — useful when the rank is genuinely small (rarely the case for BSE in general).
- **Tensor-Train (TT)** with bond dimensions chosen per index pair — useful if the index ordering reflects strong-to-weak coupling.
- **Sparse 4-tensor** with explicit channel pattern — most honest for typical BSE problems.

My honest read: **for BSE, sparse 4-tensors with structured access patterns ("block-sparse in (k, k', q) momentum")** is the realistic representation. CP and Tucker decompositions are tried in the literature but rarely give large compression for BSE in real systems. TT works for some problems with carefully chosen index orderings. The framing **handles all of these as `TensorData` constructors**, but the choice between them is not automatic — it requires problem-specific analysis. The framing's value: a uniform interface so the choice is local.

### 8.2 BTE collision matrix (4-index tensor)

The BTE collision matrix `C[band, k; band', k']` carries transition rates between scattering states. It exhibits **structured sparsity in energy-conserving mode-pair channels**: nonzero only when energy/momentum conservation can be met by available phonon modes.

The structure here is *graph-like*: a sparse 4-tensor indexed by allowed transitions. The natural representation is a **`Sparse` 4-tensor with a pattern derived from a transition-graph**.

The tensor-network framing handles it: `BlockSparse(channel_graph, values)`. Operations on the collision matrix (e.g. iteratively solving the BTE) reduce to `apply(C, f)` over the sparse pattern. This is **clean and natural** — closer to R3 than to R1.

What the tensor-network framing buys beyond just "sparse storage":
- The collision matrix appears in compositions (e.g. response calculations, relaxation-time approximations), where cost-aware contraction order helps.
- The structure can carry symmetries (detailed balance: `C[a,b] · f_b^eq = C[b,a] · f_a^eq`) as tags.

### 8.3 Unified verdict

The framing handles all three (γ̂, BSE, BTE) **at the level of common interface** (every multilinear object is a `Tensor`, every operation extends a `Network`). It does **not** unify them in *shape* — γ̂ is 2-index R1/R2/R3, BSE is 4-index sparse-or-Tucker, BTE is 4-index sparse with a channel graph.

The win is *operational uniformity*: the cost-aware optimizer works on networks involving all three. A response calculation `χ = γ̂ · K · γ̂` mixes 2-index and 4-index objects in one network, and the optimizer plans contractions across them.

The loss is *modeling effort*: each object's choice of node type requires problem-specific decisions that the framing does not automate.

---

## 9. Inherent weaknesses

I am committed to giving this framing's weaknesses honestly.

### 9.1 The framing is fundamentally substrate-coupled

Tensor networks **assume tensors are the primitive**. Symbolic / structural reasoning ("γ̂ has a symmetry, so this commutator vanishes") sits awkwardly. The framing has no language for *symbolic simplification* — only numerical/structural one. If the implementation language is meant to express algebraic identities first and numerics second, the framing is fighting the grain.

This matters for the n-Op project specifically: the implementation plan's principle "no-symbolics on runtime path" is consistent with tensor networks — but the plan also wants typed-formula derivations and macro-staged identities (§4, §5–§9), which are a poor fit for a pure tensor-network worldview.

### 9.2 Self-consistency is exogenous

The nonlinear closure Ĥ[γ̂] forces an outer fixed-point loop. The framing does not internalize this — every SCF iteration is a fresh DAG. This is awkward when the rest of the architecture treats time evolution as a continuous flow (the GENERIC two-bracket of the project does). Framing B (codata/coalgebraic) handles cyclic/self-consistent flows more naturally.

### 9.3 Encoding choice is not principled

The framing knows how each encoding costs operations but **does not know which encoding to choose**. The user (or the calling site) picks R1 vs R2 vs R3. Auto-detection (e.g. "this R3 is actually rank-3 in some basis") requires explicit rewrite rules. This is a *policy gap* the framing does not fill.

### 9.4 Schedule-optimization cost is real

For shallow networks, contraction-order optimization is negligible. For pipelines with hundreds of operations, the optimizer can dominate runtime. Caching helps when shapes are stable; under heterogeneous workloads it's an open cost.

### 9.5 Idempotency is fragile across encodings

R3 sacrifices it; R1 preserves it structurally only with care; conversions between encodings risk breaking it. The framing makes the loss explicit (via witnesses) but does not heal it.

### 9.6 Streaming / unbounded spectra fit poorly

The eigendecomp operation streams (λ, v) pairs. Tensor networks are bounded-shape objects. Bridging requires the iterative procedure (a stateful object) to sit outside the network — that's a *coroutine / coalgebra*, which Framing B handles natively.

### 9.7 Bond dimensions are opaque tuning knobs

The framing's quality of approximation hinges on bond-dimension choices that the user must set (or that heuristics must guess). The framing has no internal language for "the right bond is r=12 because the spectrum decays exponentially with rate λ". That's empirical; the framing exposes the dial but not the dial's optimal setting.

### 9.8 The DAG abstraction implies "all operations are operations on finite arrays"

This excludes operations like analytic continuations, contour integrations along complex paths (e.g. Liechtenstein-formula exchange integrals from the physics text), Cauchy principal values, and other operations that are natural on Green's functions. Each requires extension; the framing is not closed under them.

---

## 10. Cross-framing position

How this framing relates to the other three (A = typed term algebra with rewrites, B = codata / coalgebraic, C = e-graph with equality saturation).

### 10.1 Overlap and divergence with A (typed term algebra with rewrites)

**Overlap**: both treat γ̂-bearing computations as *trees/graphs* of typed nodes. Both can describe operations as graph-building. Both want typed signatures.

**Divergence**: A is fundamentally *symbolic* — the tree's nodes are *terms* drawn from an algebra (commutator, anticommutator, projection, exp, etc.), and the engine *rewrites* terms using algebraic identities. D's nodes are *concrete tensors* with concrete `TensorData`. A reasons about identities; D reasons about contractions. A can prove `tr(γ̂·γ̂) = tr(γ̂) = N` symbolically without ever instantiating γ̂; D would have to compute it. Conversely, D *measures* costs precisely; A abstracts them.

**Could combine**: term algebra outside, tensor-network inside. A picks the algorithmic plan symbolically; D executes the array-level work. They aren't competitors; they live at different abstraction levels.

### 10.2 Overlap and divergence with B (codata / coalgebraic)

**Overlap**: both treat γ̂'s observables as **derived through interfaces** (apply, density, trace) rather than as stored data.

**Divergence**: B treats γ̂ as a *behavior*, an observation interface answering queries via possibly-infinite computation. Time evolution is *coinductive*: γ̂(t) is a stream parameterized by t. SCF is a least-fixed-point on a coalgebra. D treats γ̂ as a *concrete network of arrays*; the network is finite, even when it's never materialized.

B handles cyclic closures (Ĥ[γ̂]) elegantly via fixed-point semantics. D pushes them outside.
B handles streaming eigendecomp natively. D handles it by hosting an external iterative procedure.
B is at home with arbitrary-depth lazy structures. D is at home with bounded-shape arrays.

D's strength is *cost-precision*; B's is *unbounded-flow expressivity*. They are honestly different worldviews.

### 10.3 Overlap and divergence with C (e-graph with equality saturation)

**Overlap**: both maintain *multiple representations* of the same logical object simultaneously. C's e-class is conceptually similar to D's `Gamma`-with-multiple-`TensorData`-options (R1 ∨ R2 ∨ R3). Both want the system to *choose* the best representation for a downstream operation.

**Divergence**: C does this by *equality saturation* on a *symbolic* representation — it grows the e-graph by applying rewrite rules, then extracts the cheapest expression. D does it by *contraction-order optimization* on a *concrete* network — it doesn't grow the space of representations, it just plans the contraction sequence.

C is unbounded in the space of equivalent forms it can discover; D's equivalent forms are limited to the node-type tags the user declares. C can discover novel algorithmic identities; D cannot.

C is also expensive — equality saturation explodes combinatorially. D's optimizer is also NP-hard but typically tractable on the scale of physics calculations.

**Could combine**: e-graph at the algebraic level (choose between equivalent γ̂ expressions), tensor-network at the array level (execute the chosen expression). Together they cover symbolic and numeric optimization.

### 10.4 Cross-framing summary

| Aspect | A (term algebra) | B (codata) | C (e-graph) | D (tensor network) |
|--------|------|------|------|------|
| γ̂ identity | Symbolic term | Behavioral interface | Equivalence class of terms | Network of tensors |
| Encodings R1/R2/R3 | Term constructors | Possible behaviors of an interface | Members of one e-class | Node-type constructors |
| Self-consistency | Recursive term + rewrite | Coalgebraic fixed point | Saturation finds fixed term | Outer loop, exogenous |
| Eigendecomp | Symbolic spectrum | Stream from interface | Saturated identity | Iterative + apply |
| Cost awareness | Rewrites with cost guards | Effectful / observational | Cost-driven extraction | Native: NP-hard optimizer |
| Substrate posture | Symbolic-first | Interface-first | Equivalence-first | Numeric-first |
| Hole 2 (BSE) | Symbolic kernel + rewrites | Coalgebra over channels | E-class of kernel forms | Sparse 4-tensor / Tucker |
| Hole 3 (BTE) | Term algebra of collisions | Streaming distribution | E-class of collision forms | Sparse 4-tensor on transition graph |

### 10.5 Where D is the natural fit

- When γ̂ appears in **deep, heterogeneous-shape compositions** where contraction-order choice matters.
- When **costs are first-class** and must be predicted, not just observed.
- When the operations are **fundamentally numeric** (matvec, eigendecomp, density) and the symbolic layer is secondary.
- When the encodings R1/R2/R3 differ in their **internal multilinear structure** more than in their **algebraic identities**.

### 10.6 Where D is the wrong fit

- When **algebraic identities** drive the work (D has no language for them).
- When **streams / coinductive observers** are central (D is bounded).
- When **self-consistency** must be expressed natively (D pushes it outside).
- When the **implementation grammar wants symbolic-first composition** with numeric execution as backend (D inverts the priority).

### 10.7 Final structural note

Tensor networks are the **most concrete, most operational, and most cost-aware** of the four framings. They are also **the most committed to a numeric substrate**. For a library that emphasizes "no-symbolics on the runtime path" but wants typed compositional algebra at the *expand* layer, the natural decomposition is:

- The **expand-time layer** uses framing A, B, or C (symbolic / coalgebraic / equivalence-saturated reasoning over γ̂ as an abstract object).
- The **runtime layer** uses framing D (the chosen γ̂ expression compiles to a tensor network executed by a cost-aware contractor).

This pairing positions D not as a competitor to A/B/C, but as their natural **runtime implementation**. As a standalone framing for the *whole* γ̂ design, D is incomplete — it handles the operational core well but cannot host the algebraic and self-consistent reasoning that the rest of the n-Op architecture needs.

---

# Summary

The tensor-network framing represents γ̂ as a typed `Network` node with two open spatial indices, allows R1/R2/R3 to coexist as `TensorData` constructors carrying structural invariants as symmetry tags, and defers all contraction work to a cost-aware optimizer at materialization time. It handles linear operations (apply, timestep, restrict, basis_change, apply_op) elegantly through graph-building, and handles spectral operations (eigendecomp, density) through iterative procedures that consume the network's `apply` interface. Invariants live as tag-plus-witness pairs: self-adjoint and trace are nearly free; idempotency is fragile under R3 and requires controlled-error witnesses.

The framing's structural strengths are **cost-precision in deep compositions** and **honest exposure of approximation costs**. Its structural weaknesses are **substrate-commitment to numeric arrays**, **exogenous self-consistency** (the Ĥ[γ̂] cycle must live outside the DAG), **opacity of encoding choice** (no automatic selection between R1/R2/R3), and **no native language for algebraic identities**.

For BSE and BTE, the framing generalizes naturally at the level of common interface — both are 4-index objects fitting into `Sparse` or `Tucker`/`TT` constructors — but does *not* unify them in shape; problem-specific node-type choice remains the user's responsibility.

Among the four framings, D is the most operationally concrete and the most numerically committed. Its natural place is as the **runtime layer beneath one of the symbolic/coalgebraic/e-graph framings**, not as the sole framing for γ̂.

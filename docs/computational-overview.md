# `/physics` — Computational Architecture Reference

> A **computational-lens** reference for `/physics`: the system described as a *program* —
> data structures, algorithms, complexity, numerical behavior, data layouts, order of
> operations. **Physics meaning is deliberately suppressed** (when `E`, `S`, `L`, `M`, `γ̂`
> appear, they denote a functional, an operator, a matrix — not their physical content).
> This is a hand-written companion to the atomic spec (`docs/architecture/*`,
> `docs/implementation/*`), **not** part of the lint-enforced atomic tree. Every claim cites
> its canonical `arch-xx` / `impl-xx` source so it can be verified rather than re-derived.
> Depth target: an engineer can derive low-level structures, layouts, solver choices, and an
> order of operations from this document. It does **not** prescribe a language or write code.

---

## 1. What kind of program this is

`/physics` is **a compiler that emits a numerical kernel**, organized around **one
content-addressed data substrate**.

- **Compose-time** (the compiler): builds a typed symbolic IR (a hash-consed DAG), rewrites it
  through four passes, and *lowers it to a runtime kernel*. Runs **once per problem instance**
  — a `(PeriodicityStructure, SiteDecoration, Environment)` tuple — in seconds–minutes
  (`arch-07-pipeline §7.6`). Branchy, allocation-heavy, pointer-chasing; latency- and
  correctness-bound, not throughput-bound.
- **Runtime** (the emitted kernel): a straight-line numeric function `(state, env) → numbers`,
  run **millions of times** at µs–ms each. No symbols, no structural branching, no solver
  invoked from scratch.

Polyglot realization (`arch-18-open-decisions`, Closed): **compile-time = Haskell**;
**runtime = Julia** (the compiler *emits Julia source*, JIT-compiled once per composition, so
the hot loop is native and only flat arrays cross the seam); **GAP** offline for finite-group
tables; **Lean 4** offline for substrate-invariant proofs. (Language choice is orthogonal to
everything below; this document is language-neutral.)

The central design lever (`arch-07-pipeline`): **all expensive structure discovery — symmetry
reduction, sparsity pattern, low-rank/compression plan, adjoint factorization — is done once
at compile time; the runtime only *applies* precomputed structured operators.** This is what
lets every runtime hot path be `O(log n)` or better and call no solver (`arch-20 §20.5`).

---

## 2. The memory model — the representation substrate (`arch-20`)

Every load-bearing object is a *fiber* over five primitives. This is the storage and identity
contract for the whole system.

### 2.1 Primitives

| Primitive | Computational object | Core operation costs |
|---|---|---|
| `Address[D]` | 256-bit content hash (SHA-256), domain-separated | construct `O(payload)`; equality `O(1)` (32-byte compare ≈ two SIMD loads) |
| `Universe[U]` | interned vocabulary → dense integer ordinals (`u32` closed / `u64` open) | member equality `O(1)` (one word); ordinal doubles as a dense array index |
| `SparseSet[U]` | subset of a universe, density-chosen backend | membership `O(log n)`–`O(1)`; bulk set-ops backend-specific |
| `PersistentMap[K,V]` | immutable HAMT, branching factor 32 | lookup/insert `O(log₃₂ n)`, path-copy with structural sharing |
| `MerkleDAG[S,L]` | hash-consed DAG, parameterized by op-signature `S`, leaves `L` | root equality `O(1)`; structural diff `O(changed frontier)` |

`Node[S,L] = Leaf(L) | Op(op : S.Op, attrs : S.Attrs[op], children : S.Arities[op])`. The
op-signature `S` makes attribute types and arities a function of the op tag.

### 2.2 Content addressing and the canonical serializer (`arch-20 §20.4`) — the #1 correctness surface

`Address[D] = SHA-256(domain_separator(D) ‖ schema_version(D) ‖ canonical_node_bytes)`.
**Identity is the hash of the canonical bytes**, so the serializer's *injectivity* is the
single highest-consequence invariant in the system (two distinct values hashing equal breaks
all caching, dedup, and equality). The 11 rules:

1. 16-byte domain separator first (prevents cross-domain collision even on identical bytes).
2. `u32` schema version (bumped on incompatible change; old addresses never silently reinterpreted).
3. Records: fields **lexicographically sorted by name**, each `name_bytes ‖ length-prefixed value`.
4. Sequences: `u64` length prefix, elements in declared order.
5. Sets: elements canonicalized, **sorted by address bytes**, length-prefixed (order-independence).
6. Maps: `(key_bytes, value_bytes)` **sorted by key bytes**, length-prefixed.
7. Sum types: `u32` discriminant ordinal ‖ length-prefixed payload.
8. Continuous factors: U(1) sectors → signed integer lattice weights + basis-id; SU(2) → doubled spin labels (`2j : Nat`) + Clebsch–Gordan table-version address.
9. Group action laws: normalized homomorphism/twist generators, relation rows sorted by `(domain, codomain, action_label)`.
10. `Optional`: `0x00` (None) vs `0x01 ‖ value` (Some) — never confusable with empty-but-present.
11. Scalars: `Nat`/`Int` fixed-width **big-endian**; `Float` IEEE-754 binary64 big-endian with **two normalizations applied first — every NaN → one canonical quiet-NaN; `−0.0 → +0.0`** — so numerically-equal floats always share an address.

**Numerical note:** rule 11's float normalization is what makes content-addressing safe for
computed values; without it, `−0.0`/`+0.0` or distinct NaN bit-patterns would fork identity.
Length-prefixing (not delimiters) prevents concatenation ambiguity. Hashing is the only
`O(payload)` operation on the identity path; everything downstream is `O(1)` address compare.

### 2.3 Backend-selection decision procedures (apply these directly)

**`SparseSet` backend ladder** (`arch-20 §20.5`; a property of the *universe's* density estimate, fixed at registration):
- `n ≤ 8` → **sorted tuple** (free-monoid backend): no allocation, linear scan, cache-resident; `O(n)` membership with tiny constant.
- dense, `n ≤ 256`, small closed universe → **bitset**: word-parallel union/intersection.
- sparse over a large universe → **Roaring**: `O(log n)` container probe, SIMD bulk ops, compresses runs.
- persistent + diffable → **HAMT (branching 32)** or **Merkle trie**: `O(log₃₂ n)`, path-copy.

**`PersistentMap`**: HAMT depth `≤ ⌈log₃₂ |keys|⌉` (≤ ~6 for ≤ 10⁹ keys); insert path-copies one root-to-leaf path, leaving the rest shared (enables cheap stage-to-stage sidecar versioning).

**`MerkleDAG`**: node store = `Map<Address, Node>`; equality is one root-address compare; `diff` descends only subtrees whose addresses differ (skips equal subtrees in one compare) → diff cost is proportional to the changed frontier, not total size.

### 2.4 Op-signatures and the per-cluster storage table (`arch-20 §20.2–§20.3`)

Four op-signatures specialize the Merkle DAG:
- **`PredicateOps`** — reduced ordered binary decision diagrams (ROBDD) over versioned atoms (applicability, `arch-13`).
- **`SymbolicTensorOps`** — a colored-operad / free symmetric monoidal category over target shapes `{Scalar, AntisymmForm, PSDSymmForm}` with tensor product, contraction, derivative, group action, projection, binding (the tensor-algebra IR for invariants and `FormulaApply`).
- **`EvidenceOps`** — attestation, semilattice-meet aggregation, reference linkage, trajectory chunk (cert, `arch-12`).
- **`GroupOps`** — multiply, invert, restrict, antipode/TR-twist, character, projector (finite-group algebra).

| Cluster | Contents | Structure / backend | Identity |
|---|---|---|---|
| C1 | 10 closed/open vocabularies (`StateComponent`, `NodeKind`, `BundleId`, `AxisLabel`, `CategoryTag`, …) | `Universe[T]` + dense ordinals | ordinal compare |
| C2 | registered generators (`FormulaRecord`, `ResidualGenerator`, `CouplingChannel`) | registry-universe element, kind-indexed dispatch | `Address[Element]` |
| C3 | sidecars (Stage 1/2/2.5/4) | `PersistentMap[TypedKey, EvidenceBearing[V]]`, HAMT-32, stage-visible | root address |
| C4 | evidence + symbolic forms | `MerkleDAG[EvidenceOps,…]` / `MerkleDAG[SymbolicTensorOps,…]`, hash-consed | root address |
| C5 | all content addresses (node id, `ResidualKey`, generator-hash, cache keys) | SHA-256 domain-separated (§2.2) | 256-bit digest |
| C6 | selected subsets (`CouplingSpec`, active residual/formula/bundle subsets) | `SparseSet[RegistryUniverse]` (Boolean lattice) | subset root |
| C7 | sparse masks (`RoaringCoverageMask`, axis sets, irrep-block indices) | `SparseSet[Universe]`, density-derived | root |

`CrystalSymmetryGroup` stays sui generis (its algebra is not reduced to the substrate; its
*identity* is `Address[GroupAtlas]` and its *derived outputs* are substrate fibers). `PhysicsGraph`
is the closure of output addresses under children-pointers — no separate edge identity.

### 2.5 Hot-path complexity commitments (`arch-20 §20.5`)

**No hot path exceeds `O(log n)`; none calls a solver; none serializes twice.**

| Operation | Asymptotic | Constant |
|---|---|---|
| `Address` equality | `O(1)` | one 32-byte compare |
| `Universe` member equality | `O(1)` | one word compare |
| `SparseSet` membership (Roaring / HAMT / tuple) | `O(log n)` / `O(log₃₂ n)` / `O(n≤8)` | container probe / path walk / linear scan |
| `PersistentMap` lookup / insert | `O(log₃₂ n)` | HAMT walk / path copy |
| `MerkleDAG` root equality / diff | `O(1)` / `O(changed frontier)` | address compare |
| ROBDD evaluate / equivalence | `O(path len)` / `O(1)` after canon | 3-pointer fetch / memoized apply |
| `EvidenceOps` aggregate | `O(children)` | semilattice meet, early-exit on Failed |
| group multiply / projector eval | `O(1)` avg / `O(\|G\|/\|H\|·rank)` | Schreier–Sims table / cached after first eval |

---

## 3. The data operated on — state and `γ̂` (`arch-04`, `arch-15`, `arch-08`, `arch-21`)

**Three-tier state (`arch-21-multiscale-state`).** The state is stratified by
timescale/scale into **micro** (the 7-tuple below, unchanged), **slow** (defect
populations / aging — first-class state evolving by Arrhenius generation–annihilation
kinetics, which the PINO predicts and `/physics` scores), and **macro** (homogenized
device-mesh fields `T_L(r), φ(r), n(r), p(r), j(r)`). The full carrier distribution
stays *emergent* by moment closure (`T_e`, `j` closed-form), so no distribution-as-state
DAE arises. The slow tier is an adiabatic parameter of the micro tier; the macro tier is
homogenized from it (micro `κ(T), σ(T), α(E)` → device-PDE coefficients). The 7-tuple
below is the micro tier; the slow and macro tiers, the homogenization map, and the two
extra EOM-family residuals (`EOM/DefectPopulation`, `EOM/Continuum`) are in `arch-21`.

### 3.1 The 7-tuple `x = (h, R_I, P_I, Π_h, Z_I, γ̂, A)` — computational types

| Component | Container | Layout / notes |
|---|---|---|
| `h`, `Π_h` | 3×3 real matrices | 9 doubles (72 B) each; trivially cache-resident |
| `R_I`, `P_I` | `N×3` real arrays | row-major by atom → per-atom locality; `N` = #atoms |
| `Z_I` | integer vector, length `N` | immutable species labels; dense ordinals |
| `A` | field on a grid | dense array, FFT-friendly layout (reciprocal-space ops) |
| `γ̂` | encoded operator (below) | the one feasibility-critical structure |

Slots are a closed `StateComponent` vocabulary (`Universe[StateComponent]`); the whole tuple is
content-addressed by §2.2. Downstream code indexes slots by dense ordinal, not symbol.

### 3.2 `γ̂` — the load-bearing data structure (`arch-15`)

Logically an `N×N` Hermitian operator; physically a **single logical object with a 5×4
encoding grid** `(Basis ∈ {Real, Reciprocal, Wannier, NaturalOrbital, SymmetryAdapted}) ×
(Form ∈ {Dense, Sparse, BlockDiag, LowRank})`. Stage 4 selects exactly one slot per
density-matrix node.

**Selection decision procedure** (by `(PeriodicityStructure, SiteDecoration)`, `arch-15 §15.2`):
- periodic bulk → `(Reciprocal, BlockDiag)` (MVP default)
- defect / surface / amorphous → `(Real, Sparse)`
- interface layers / dangling bonds → `(Wannier, Sparse)`
- low-rank substrate → `(NaturalOrbital, LowRank)`
- output of symmetry-adapted construction → `(SymmetryAdapted, BlockDiag)`

**Data layout of the MVP slot `(Reciprocal, BlockDiag)`** (`mvp-02-gamma-budget`): one block per
k-point; **each block stored as orbitals `N_PW × N_b` (low-rank in the band index), never the
dense `N_PW × N_PW` matrix.** Complex doubles (16 B). k-blocks are mutually independent →
embarrassingly parallel and independently addressable. Budget:
`N_PW × N_b × 16 B × N_k`. Concrete MVP: `N_PW ≈ 1000` (≈400 eV plane-wave cutoff),
`N_b ≈ 40`, `N_k ≈ 29` irreducible (8×8×8 mesh) ⇒ **≈ 18 MB**. The dense form of the same data
would be `N_PW² × 16 × N_k ≈ 460 MB` — **the slot choice is the feasibility boundary, not an
optimization.** Warm-start seed: a tight-binding `~18×18` Hamiltonian per k (kilobytes) feeds
the SCF inner loop. Beyond MVP, supercells grow `N_PW` linearly; orbital storage stays linear
in `N_atoms × N_b` *provided the encoding is never densified*.

**Read/write asymmetry** (`arch-15 §15.3`) — optimize for read:
- **Read path (dominant, every trajectory step):** lazy materialization via destructor methods —
  apply operator (`matmat` against the `N_PW × N_b` factors), extract density (outer products),
  trace (inner products), eigendecomposition. Costs are set by `N_b` (the rank), not `N_PW²`.
- **Write path (rare — construction, self-consistency, time-stepping):** staged through a planner;
  self-consistency's gradient handled by the Stage-4 implicit-diff adjoint (§5), not by unrolling.

**Open data-structure problems (`arch-15 §15.4`)** — these are *unsolved CS problems*, flag as intentionally open:
1. **ε-equality / error tracking:** if identity is bisimulation-up-to-ε, the rewrite (e-graph) layer needs norm-bounded approximate equality; unsolved → e-graphs stay an *offline* rewrite oracle in V1, never on the runtime path.
2. **Materialization policy:** when to force vs defer materialization on the read path is workload-dependent with no principled default (a lazy-evaluation strategy without a heuristic).
3. **Long-trajectory drift / rank growth:** over many steps, low-rank factors densify and sparse patterns fill in; detecting rank explosion and a rebalance/refresh policy is undefined.
4. **Rank-dependent applicability:** the `(NaturalOrbital, LowRank)` slot relies on cheap consistency checks that become prohibitive at high rank (four-index objects, dense collision matrices) → those bypass the slot and go to TT compression directly.

### 3.3 Level layering L1–L4 (`arch-08`) — a computational dependency order

Dependencies flow strictly **upward** `L4 → L3 → L2 → L1`; each level introduces irreducible
state. The level of a node is **derived from its transitive inputs, not stored**; Stage 1
constructs the graph in level order.

| Level | Operates on | Operations (computational) |
|---|---|---|
| L1 | `γ̂`, `A` at fixed `(R,h)` | apply operator, eigendecomposition, trace, density extraction (single-particle linear algebra on the `γ̂` encoding) |
| L2 | `(R,P,h,Π_h)`, `Z` fixed | **nested minimization** `E_BO(R,h) = min_{γ̂} E[γ̂;R,h]` (L1 inner loop), derivative-based forces, MD timestepping |
| L3 | spectra from L1/L2 | spectral reductions / statistical aggregation (quadrature over eigenvalues) |
| L4 | distributions over L1–L3 | kinetic/transport: sparse linear solves, transition-matrix methods, sampling |

**Order-of-operations consequence:** an L2 force evaluation contains a *converged L1 inner
solve*; the adjoint must thread the implicit-diff chain through both. The
L3↔non-equilibrium cycle closes by a same-pass fixed point (`impl-11 §15.2`: ≤ 5 iterations in
the worked example).

### 3.4 Dressing tiers (`arch-08 §8.1`) — an implementation-scoped layering, not a runtime hierarchy

- **Layer 1** — bare substrate.
- **Layer 1.25** — one-shot, closed-form corrections (single non-iterated solves); evidence = `OneShotCert`. **MVP runs entirely here.**
- **Layer 1.75** — iterative fixed-point corrections (each needs a bespoke Stage-4 lowering); evidence = `IterativeResult`. **V2-deferred**; V1 ships type/cert scaffolding with loud `not-implemented` stubs (`impl-07 §7.7`).

---

## 4. The IR — the PhysicsGraph (`arch-06`)

A **hash-consed, content-addressed DAG**. Recommended low-level representation: an **arena /
index DAG** — nodes in a flat array, `NodeId` = integer handle (not a pointer) — which gives
compact storage, cache locality on traversal, trivial serialization, and a natural hash-cons
table keyed by `Address`.

```
Node = ( id   : Address[GraphNode]          -- hash-cons identity
       , type : Layer0Type                  -- the 4 typeclasses (arch-10)
       , kind : NodeKind , role : OutputRole )

NodeKind   = Input(StateSlot | EnvScalar)
           | FormulaApply(formula : NamedFormula, args : [NodeId])     -- 110 formulas
           | MethodInvoke(method  : NamedMethod,  args : [NodeId])     -- 12 methods
OutputRole = Internal | Observable(bundle : 1..11) | ResidualLeaf(ResidualKey)
```

- **Edges are the `args` lists** inside apply/invoke nodes — there is no separate edge table;
  the graph *is* the multiset of output-root addresses closed under children-pointers.
- **Identity / hash-consing:** identical subgraphs collapse to one address (`O(1)` amortized
  via the address table). Two graphs are equal iff their output-root multisets match.
- **Per-stage sidecars** (`arch-06 §6.4`): ephemeral `Map<NodeId, T>` produced by one stage and
  consumed by the next, **not** hash-consed, erased before runtime. Stage-visibility poset
  `1 < 2 < 2.5 < 3 < 4 < 5`. Backed by HAMT-32 (C3).
  - `Stage1Sidecar.applicability : Map<NodeId, Predicate>` (discarded after pruning)
  - `Stage2Sidecar.symmetry : Map<NodeId, IrrepBlock>` (consumed by Stage 4)
  - `Stage4Sidecar.compression : Map<NodeId, CompressionPlan>`, `.adjoint : Map<FixedPointNodeId, AdjointSolver>` (erased after codegen)

**`CompressionPlan` family (`arch-06 §6.4`) and its Stage-4 decision procedure:**
`Dense | Sparse(pattern) | LowRank(rank) | HODLR(params) | TT(ranks)`. Choose per operator node by:
- small or dense operator → **Dense**;
- known/inferred sparsity pattern (from Stage-3 sparsity inference) → **Sparse**;
- numerical rank `r ≪ n` (estimate via rank-revealing QR or randomized SVD at Stage 4) → **LowRank(r)**;
- hierarchically low-rank off-diagonal blocks → **HODLR**;
- high-dimensional tensor operator (e.g. a collision kernel) → **TT(ranks)**, cores built once via sequential TT-cross.

---

## 5. The core algorithm — the 4+1 pipeline (`arch-07`)

Each compose-time pass rewrites the IR; the fifth is the emitted numeric loop. The table gives
input→output, the algorithm/math class, and cost; details follow.

| Stage | In → Out | Algorithm class | Cost (compile-time unless noted) |
|---|---|---|---|
| 1 Symbolic lift | request + descriptors → pruned IR | macro expansion + Boolean decision diagrams | seconds; ROBDD eval `O(path len)` |
| 2 Symmetry quotient | IR → block-structured IR | finite-group representation theory (rewrites only) | seconds; group sums `O(\|G\|)`, `\|G\| ≤ 192` |
| 2.5 Invariant synthesis | coupling decls → tensor-algebra DAGs | Reynolds projection over a finite group | seconds; ≤ 12 M ops worst case, cached |
| 3 Algebraic simplification | IR → shared sparse IR | term rewriting / e-graph (union-find + e-matching) | the algorithmically hardest pass |
| 4 Lower + adjoint + codegen | IR → kernel | numerical-LA planning + implicit-diff AD + codegen | seconds–minutes |
| 5 Runtime apply | (state, env) → numbers | the 12 numeric kernels | µs–ms × millions (runtime) |

**Stage 1 — lift + prune.** Order: instantiate each requested template (a graph-construction
macro) into a subgraph of `Input` / `FormulaApply` / `MethodInvoke` nodes in **L1→L4 level
order**; evaluate each node's applicability predicate (ROBDD, `O(decision-path)`, three-pointer
fetch per node); **delete** any subgraph whose applicability is false for this `(Crystal,
Environment)`. Output is a pruned graph; the applicability sidecar is discarded.

**Stage 2 — symmetry quotient (rewrites, no numerics here).** Two transformations that *reduce
the work Stage 5 will do*:
- **Schur block-diagonalization:** an operator commuting with the group action is rewritten into
  its per-irrep blocks (block dim `Σ_λ d_λ m_λ`). This turns a single `O(n³)` dense eigensolve
  into `Σ_λ O((d_λ m_λ)³) ≪ O(n³)`. **Numerical note:** the blocks are *small* (cubic point
  groups give `d_λ ∈ {1,2,3}`, up to 4 under spin–orbit), which favors a cache-resident dense
  solve per block and is a poor fit for wide-SIMD/GPU batching unless many blocks are batched.
- **IBZ orbit collapse:** orbit–stabilizer reduces a full-zone k-mesh to the irreducible wedge
  with integer orbit weights (cubic: up to 48×). Requires character tables (GAP, offline) and a
  Schreier–Sims product table (`O(1)` avg multiply).

**Stage 2.5 — invariant synthesis (`arch-19 §19.3`).** For each active `CouplingChannel`, in order:
1. **Spinor-parity pre-prune** (`O(#pieces)`): odd total spinor parity cannot form the target shape → empty basis, computed before any character work.
2. **Character-inner-product emptiness test:** `⟨χ_T, χ_trivial⟩ = (1/|G|) Σ_g χ_T(g)` (`O(|G|)` traces, ≤ ~200 ops, **never materializing `ρ(g)`**) predicts whether the invariant basis is non-empty *before* building it.
3. If non-empty, apply the **Reynolds (trivial-irrep) projector** `P = (1/|G|) Σ_g ρ(g)` to the
   target tensor `T` (`O(|G|·dim(T)²)`, ≤ ~12 M ops worst case). Result cached on
   `Address[CrystalSymmetryGroup] × Address[CouplingChannel]`.
   Bounds enforced: `|G| ≤ 192`, `dim(T) ≤ 250`, ≤ 12 M ops. Output: `InvariantTerm`s as
   `MerkleDAG[SymbolicTensorOps, …]`, lowered in Stage 3 into `FormulaApply` nodes on the
   `E_coupling` / `L_assembly` / `M_assembly` aggregators (`arch-05`).

**Stage 3 — algebraic simplification.** Hash-consing (intern identical subexpressions, `O(1)`
amortized), cross-formula common-subexpression elimination (the 110 formulas share
intermediates), tearing / alias elimination, sparsity-pattern inference. Implemented as
equality-saturation over an e-graph (union-find of equivalence classes + e-matching). Symbolic;
no numeric cost. **This is the hardest pass to build** and the one whose performance is
open-ended; granularity is preserved (each `ResidualLeaf` keeps its content-addressed key).

**Stage 4 — lowering + adjoint synthesis + codegen.**
- **Compression-plan selection** per operator node (the §4 decision procedure; may run a
  randomized-SVD range-finder to estimate numerical rank).
- **Implicit-differentiation adjoint synthesis** for fixed-point / implicit nodes (SCF
  minimization, BTE-RTA): the gradient of a converged fixed point is **one linear solve against
  the (transposed) fixed-point Jacobian**, independent of the forward iteration count — versus
  differentiating through the unrolled loop. Conditioning of that solve is set by the fixed-point
  map's Jacobian; near-singular Jacobians (slow self-consistency) are the failure mode.
- **Registration-time adjoint gate (`impl-07 §7.5`):** every `D2` generator runs a
  forward-vs-reverse consistency check (vJp vs JvP) on `N ≈ 64` sampled points; if the max
  relative error exceeds **`τ_adj = 1e-4`** the build **fails loud**, forcing an honest adjoint
  or an explicit downgrade to `D3`/`D4` with recorded rationale.
- **Codegen:** lower the whole graph to one kernel with one entry (the `Input` slots) and typed
  exits (residual map, gradient map, observable map, cert evidence). Sidecars erased.

**Stage 5 — runtime apply.** Apply the compiled kernel to a dense state vector. The 12 methods
(§6) are the numeric kernels invoked here. Forward pass cost = kernel-DAG evaluation; the
optional adjoint pass is reverse-mode by structural projection, `O(residual-vector size)`.

---

## 6. The operation alphabet (`arch-09`, `impl-02`, `impl-03`)

### 6.1 The 12 methods → numerical kernels (with selection criteria, complexity, stability)

| # | Method (sub-methods) | Kernel | Complexity (constants/notes) | Selection / numerical notes |
|---|---|---|---|---|
| 1 | state-readout (distance-PBC, sphere-integral, diagonal-trace, cell-metric, extremum, occupation-sum) | array traces / reductions | `O(n)`; distance-PBC `O(N)` with cell lists vs `O(N²)` naive | minimum-image convention; reductions are bandwidth-bound |
| 2 | algebraic-combination | registry-dispatched formula eval | `O(#inputs)` | no inline math; pure leaf evaluation |
| 3 | functional-differentiation (grad, hessian, higher) | automatic differentiation | fwd `O(1)`×forward per input dir; rev `O(1)`×forward per output; Hessian `O(n)` vJp-of-JvP | reverse-mode for scalar→many-inputs (gradients); user supplies the AD, Stage 4 supplies the plan |
| 4 | variational-minimization (SD, CG, BFGS, FIRE, Newton, SCF-mix, Pulay) | nonlinear optimization / fixed-point | CG/LBFGS superlinear, low memory; Newton quadratic but `O(n³)`/iter; FIRE robust first-order | convergence on gradient-norm tol; SCF+Pulay/DIIS accelerates fixed points but can oscillate (mixing-parameter & DIIS-conditioning sensitive); the nested `min_γ̂` inner loop is the L2 bottleneck |
| 5 | spectral-decomposition (full-diag, Lanczos, Davidson, inverse-iter, shift-invert) | eigensolve | dense `O(n³)`; Lanczos `O(k·n²)` + reorthogonalization; shift-invert needs `(A−σI)` factorization | **select by `n`, sparsity, #eigenpairs, spectral region:** full-diag for `n ≲ few-thousand`/all pairs; Lanczos for few extremal pairs (loses orthogonality → needs selective/full reorthogonalization); Davidson when a good diagonal preconditioner exists; shift-invert for interior pairs near `σ`. **Ill-conditioned at near-degeneracy → use block solvers per degenerate subspace.** Stage-2 blocks make these small. |
| 6 | spectral-aggregation (delta-sum/DOS, partition-Z, thermal-avg) | quadrature | `O(n)` | **tetrahedron method** for DOS (`O(n_k)`, linear interp, less broadening bias than Gaussian smearing); **log-sum-exp** for partition sums (`log Σ eˣⁱ = m + log Σ e^{xᵢ−m}`, `m = max`) to avoid overflow; thermal weights need care near degeneracy / low temperature |
| 7 | linear-response (Kubo, LR-DFT/Dyson, Green's-fn, Sternheimer, interface-tunneling) | sparse linear solves / resolvent | `O(n³)` full; `O(freq·n²)` per-frequency | **Sternheimer** solves `(H−εI)|δψ⟩ = −P·perturbation` to avoid an explicit sum-over-states; near-resonance the system is near-singular → regularize with a finite broadening `η` (controls conditioning vs accuracy) |
| 8 | path-search (NEB, CI-NEB, dimer, string, field-line-integral) | constrained optimization on a curve + ODE | `O(images · force-eval)`; field-line = stiff ODE integrator | saddle search is **inherently ill-conditioned** (one negative-curvature direction); CI-NEB converges on the perpendicular force; dimer avoids needing both endpoints |
| 9 | convex-optimization (convex-hull, common-tangent, QP) | computational geometry / LP / QP | hull `O(n log n)`; LP `O(n²·L)` interior-point | floating-point hulls need **robust orientation predicates** to avoid topological inconsistency; rational/exact arithmetic ideal for the combinatorial part |
| 10 | kinetic-evolution (BTE-RTA, BTE-full, master-eq, drift-diffusion, Cahn–Hilliard, Allen–Cahn) | sparse transport / PDE timestepping | BTE-RTA `O(n_k·n_band)` (diagonal collision, direct); BTE-full = large sparse iterative solve; PDEs ∝ #timesteps | **stiffness** drives the choice: implicit timestepping for stiff diffusion (stability beats explicit-CFL limits); off-diagonal collision matrices are large+sparse, conditioning set by scattering stiffness; high-dim collision → TT-cross (built once at Stage 4) |
| 11 | statistical-sampling (MC, MD, kMC, importance) | Monte-Carlo / dynamics | variance `O(1/√samples)`; MD ∝ #timesteps | symplectic integrators for MD (bounded energy drift); importance sampling for variance reduction; kMC for rare-event time-scales |
| 12 | symmetry-projection (point-group, space-group, time-reversal) | group Reynolds projector + algebra | multiply `O(1)` avg (Schreier–Sims); projection `O(\|G\|·dim²)` | exact up to floating round-off in `ρ(g)`; projector cached as an `Address` after first eval |

### 6.2 The 20 templates → graph-construction macros (`impl-03`)

A template is a **macro that emits a subgraph** wiring methods/formulas; it is a partially
applied method chain with a typed `inputs → output`. Representative signatures (full list in
`arch-09 §9.2`):

| Template | Signature (types) | Composes |
|---|---|---|
| `SpectrumOf` | `(ParametricOperator, Domain) → FieldOnGrid` | spectral-decomposition |
| `SpectralAggregateOf` | `(spectrum, Aggregator, Field) → FieldOnGrid` | spectral-aggregation |
| `SecondDerivativeOf` | `(Functional, Point, Coord, Metric) → Tensor` | functional-differentiation (order 2) |
| `HarmonicStiffnessHessianOf` | `(Functional, Point, basis, method) → Tensor[3N×3N]` | order-2 diff **+ symmetrization + acoustic-sum-rule enforcement** (a numerically-stabilized Hessian) |
| `ResponseOfTo` | `(obs, pert, Kernel, freq) → Response` | linear-response |
| `PathStationaryOf` | `(Functional, init, final, method) → ReactionCoord` | path-search |
| `KineticEvolutionOf` | `(Distribution, Collision, Gradient) → SteadyState` | kinetic-evolution |
| `SymmetryAdaptedHamiltonianOf` | `(SpaceGroup, WyckoffOrbits, Orbitals, shells) → ParameterizedBlochHamiltonian` | symmetry-projection (constructive Reynolds basis) |
| `SelfConsistentChargeBalanceOf` | `(host, defects, Env, solver, tol) → (E_F, {N_q}, {n,p})` | fixed-point: spectral-decomposition + convex-optimization (closes the L3↔non-eq cycle) |
| `SelfConsistentRenormalizationOf` | `(bare, scheme, T, conv) → DressedQuantity` | scheme-selected variational/spectral/linear-response (→ `IterativeResult`) |

(The remaining 10 — `StateReadoutOf`, `AlgebraicOf`, `ClassifyOf`, `ComparisonOf`,
`RadiativeEmissionOf`, `MicrokineticSteadyStateOf`, `ConfigurationalFreeEnergyOf`,
`InterfaceEquilibriumOf`, `BiSlabGrandPotentialOf`, `MassActionEquilibriumOf` — follow the same
macro-emits-subgraph pattern; see `arch-09 §9.2`, `impl-03`.)

### 6.3 The 110 formulas — distribution (`arch-09 §9.3`, `physics/library/formulas/registry-manifest.csv`)

Leaf evaluations with typed signatures, grouped into 11 bundles (B1–B11) and tagged:
- **cost-tier:** T0 closed-form ≤ 10 µs (~50 formulas) · T1 small LA / 1-D quadrature ≤ 10 ms (~35) · T2 BZ/mesh integral ≤ 10 s (~15) · T3 self-consistent loop / PDE ≤ 10 min (~2).
- **diff-tag:** D0 no AD (~15) · D1 analytic forward (~50) · D2 adjoint-required-and-gated (~25) · D3 implicit-function adjoint (~8) · D4 surrogate / finite-diff relaxed (~4).

### 6.4 The dynamics, computationally (`arch-05`)

`dx/dt = L·δE/δx + M·δS/δx`. Computationally: `E`, `S` are functional subtrees of the IR;
`δ/δx` is functional-differentiation (AD); `L` is an **antisymmetric** structured block operator,
`M` a **positive-semidefinite** one (PSD by construction — a numerical invariant cert checks by
projection). The grounding scalar output is the EOM-violation residual `‖dx/dt − (L δE/δx + M
δS/δx)‖²`; every other residual is a refinement (per component / per axis) or an algebraic
identity (`arch-11`).

---

## 7. Symmetry & topology data structures (`arch-09 §9.5`, `arch-14`)

| Structure | Representation | Cost |
|---|---|---|
| `CrystalSymmetryGroup` | finite presentation (generators + relators) + action homomorphisms over layer ids; `\|G\| ≤ 192` (double cover + time-reversal of the 230 space groups) | identity = `Address[GroupAtlas]` |
| Schreier–Sims product table | strong generating set + base | storage `O(\|G\|·d)`; multiply `O(1)` avg |
| character table | `χ_ρ(g)` per irrep | GAP offline; `O(\|G\|·#irreps)` storage; `O(1)` lookup |
| Reynolds / Fourier projector | `P_ρ = (1/\|G\|) Σ_g χ_ρ(g) ρ(g)` | build `O(\|G\|·dim²)`; cached as `Address` |
| little groups / BZ stalks | coset tree per k | orbit enumeration `O(\|G\|)`; lookup `O(log #orbits)` |
| topology classification `X_BS` | **Smith Normal Form** of an integer matrix | `O(m·n·log(max entry))` (Hermite reduction) — polynomial |
| elementary band representations | irrep decomposition of site-symmetry reps | storage `O(#Wyckoff·#irreps)`; feeds cert obligation 7 |

These are computed offline (GAP) and **baked into the compiler** as content-addressed tables;
nothing here is on a runtime hot path.

---

## 8. Outputs and the consumer boundary (`arch-11`, `arch-16`)

The emitted kernel's single entry point:

```
evaluate(state, env, request : all|{ResidualKey}|{ObservableRef}, gradient : Skip|Compute)
  → ( residuals : Map<ResidualKey, Scalar>
    , values    : Map<ObservableRef, Value>
    , cograds   : Optional<Map<ResidualKey, Cotangent>>
    , cert      : CertEvidence )
```

- **`ResidualKey = (producer, axes)`**, `producer = Formula(NamedFormula) | Method(NamedMethod)`;
  content-addressed (C5). Output is **granular by construction** — one scalar per
  `(producer, axis-tuple)`, no pre-aggregation; the consumer chooses the reduction. The 17
  `CategoryTag`s (7 EOM-per-component, 3 GENERIC-structural `Degeneracy`/`Conservation`/
  `Positivity`, 5 `Algebraic/*` identities, 2 `Static/*` constraints) are a **facet** in a
  parallel `Map<ResidualKey, ContributionFacets>`, **never part of identity and never a loss
  weight** (`impl-09 §9.3`).
- **Gradients:** one reverse-mode pass over the selected subgraph, projected per key →
  `O(output size)`. Granularity adds only that leaves are individually addressable; upstream
  sharing is already deduplicated by Stage-3 hash-consing.
- **`request` / `gradient`** prune the evaluated subgraph and toggle the adjoint.
- **`Import`** injects external ground truth `(value, σ, provenance, coverage-mask) →
  GroundTruthBridgeGenerator`; it inserts a pinned `Input` + a cert-only `ResidualLeaf`, is **not
  differentiated through**, and feeds cert obligation 4.
- **`RoaringCoverageMask`**: a serialized Roaring bitmap over `enumerate(product(axes))` (lexicographic
  flat-index), marking which axis-tuples a datum constrains. Sparse-from-start; `O(1)` membership,
  fast intersection/union/cardinality for cert set-ops; persisted in `SqliteReferenceCache`.
- **The consumer reads by content-hash key (`ResidualKey` / `ObservableRef`), never by node id.**

---

## 9. Verification — cert (`arch-12`, `impl-11`)

Ten obligations, each a **graph traversal emitting an `EvidenceOps` Merkle-DAG node**; verdicts
combine by **semilattice meet** (`Failed ⊓ X = Failed`, early-exit, `O(children)`). Most checks
are *projection-residuals* (`‖v − P v‖/‖v‖ < ε`) or content-addressed table lookups — **no
solver on the cert path.**

| # | Obligation | Computational check | Complexity |
|---|---|---|---|
| 1 | symmetry equivariance | sample form, apply trivial-irrep projector, residual `< ε` | `O(1)` per invariant |
| 2 | bounds / positivity | ROBDD applicability eval + scalar range test | `O(path)` |
| 3 | analytic limits | compare to closed-form reference, `\|pred−exact\|/σ < 3` | `O(1)` per formula |
| 4 | reference battery | `SqliteReferenceCache` lookup, trip at `σ > 3` | `O(log n)` B-tree |
| 5 | conservation (antisymmetry of `L`, PSD of `M`) | project emitted form onto antisymmetric / PSD cone, residual `< ε` | `O(1)` per invariant |
| 6 | GENERIC degeneracy + method equivalence | for equivalent compositions, compare formula trees / coefficients within tol | `O(\|G\|)` per equivalence |
| 7 | bulk–boundary correspondence | EBR-table lookup + multiplicity enumeration | `O(1)` + `O(#Wyckoff)` |
| 8 | reference-battery versioned | obligation 4 + `schema_version` check | `O(log n)` + `O(1)` |
| 9 | surrogate-net validity (D4 only) | surrogate vs held-out validation set | forward-pass |
| 10 | adjoint existence (D2, build-time) | DAG walk: every upstream node has a registered adjoint | `O(#nodes)` memoized |

**`SqliteReferenceCache`** (`arch-12 §12.1`): a content-addressed table keyed by the §2.2 hash
over `(observable, value, σ, provenance, coverage_mask, schema_version)`; **write-once** (updates
= new row, deletes disallowed); WAL mode for concurrent reads; `O(log n)` B-tree lookup,
`n ≈ 10–10⁴` rows. The five **runtime gates** (`impl-11 §15.2`) — registration sanity (all 110
formulas instantiate, D2 pass the τ_adj gate), an end-to-end worked example (the L3↔non-eq fixed
point closes in ≤ 5 iterations), curriculum sanity, cross-regime obligation firing, and a
consumer smoke test — are the acceptance battery.

---

## 10. Coupling structure (`arch-19`) — the Stage-2.5 generator's data

```
CouplingChannel = { pieces, target ∈ {Scalar, AntisymmForm, PSDSymmForm}, order, derivative,
                    applicability, mechanism_range, kernel_extension?, gauge_rule?, provenance? }
```

`generate-invariants(CrystalSymmetryGroup, CouplingChannel) → GeneratorOutput` runs the §5
Stage-2.5 algorithm (pre-prune → emptiness test → Reynolds projection) and returns the finite
`InvariantTerm` basis (or `∅`, with the integrity note that emptiness ≠ correctness). A derived
`polynomial_sufficient` flag (from `mechanism_range`) decides whether the symmetry-generated
polynomial basis is the *whole* coupling; long-range channels carry a typed `KernelExt` for the
non-polynomial part. `CouplingSpec` carries a `TheoryContext` (theory frame); `PSDSymmForm`
channels carry documented PSD assumptions rather than a runtime semidefinite search. The nine
named cross-regime couplings of `arch-05` collapse to a handful of channel declarations; **terms
are generated, not registered** (`impl-09 §9.4`).

---

## 11. The math-to-location map (one screen)

| Branch of math / CS | Where it enters |
|---|---|
| cryptographic hashing / content-addressing | substrate identity — everywhere |
| persistent data structures (HAMT, Roaring, Merkle DAG) | all storage / sidecars |
| Boolean decision diagrams (ROBDD) | Stage 1 applicability |
| finite-group representation theory | Stage 2 (Schur, IBZ) + Stage 2.5 (Reynolds) |
| tensor algebra / colored operads | Stage 2.5 symbolic forms |
| term rewriting / e-graphs (union-find, e-matching) | Stage 3 |
| numerical linear algebra (eigensolve, sparse, low-rank / HODLR / TT) | Stage 4 plans + Stage 5 |
| automatic differentiation + implicit-function adjoints | Stage 4 synthesis, Stage 5 gradients |
| nonlinear & convex optimization, root-finding | Stage 5 methods 4 / 9 |
| quadrature / mesh integration (tetrahedron, log-sum-exp) | Stage 5 aggregation |
| kinetic / PDE / stochastic solvers (BTE, MC, MD) | Stage 5 methods 10 / 11 |
| computational geometry (convex hull, robust predicates) | Stage 5 method 9 |
| integer linear algebra (Smith Normal Form) | topology atlas (offline) |
| lattice / order theory (semilattice meet) | cert aggregation |

---

## 12. Implementation mapping (`impl-01`, `arch-18`)

- **Layered import DAG (`impl-01` principle 1):** one-way dependencies
  `core ← shared ← {state, canonicals, generic, methods} ← observables ← cert ← api`, under one
  typed seal with opaque cross-seal datatypes. This is the build/parallelization backbone:
  freeze a layer's typed interfaces, then implement upper-layer leaves independently.
- **Polyglot seam (`arch-18`, Closed):** the Haskell compiler **emits Julia source** for Stage 5;
  Julia JIT-compiles it once per composition; the hot loop is native Julia with **no per-sample
  FFI** and **only flat arrays crossing** (no substrate object serializes across). GAP and Lean
  are offline leaves. The seam's correctness is guarded by a **differential golden test** (emitted
  kernel vs a tree-walking interpreter of the same IR).
- **Compose-time / runtime boundary (`arch-07 §7.6`):** a composition fingerprint (content hash of
  `(Periodicity, Decoration, Environment-structural)`) keys a kernel cache; scalar environment
  parameters (e.g. temperature sweeps) are runtime inputs, not recompile triggers.

---

## 13. State of the research, and deliberately-open items

The conceptual/computational design is internally coherent (38 atomic docs, lint-clean) and
was deep-audited (`docs/audits/2026-06-09-physics-audit.md`). The **multiscale-state decision**
(`arch-21-multiscale-state`) since stratified the state into micro/slow/macro tiers — closing
the audit's two biggest structural gaps (the aging/degradation state mechanism and the
device-scale bridge) and normalizing the GENERIC degeneracy layer (`arch-05`). What remains is
**not conceptual design**:

- **Formalization gaps (engineering, not design)** — researched but not yet fully machine-readable:
  the ~80-entry observable catalog, the crystal-structure-validity residual catalog, the
  polarization/piezo/2DEG package, and the rest of the `B9` bundle. (The per-host defect inventory
  and degradation kinetics are now landed as the slow tier, `arch-21`.) These are *enumeration*
  tasks tracked in the audit's P0/P1 lists.
- **Genuinely open data-structure problems** — the four `γ̂` `§15.4` items (§3.2 above): ε-equality
  error tracking, materialization policy, long-trajectory rank drift, rank-dependent applicability.
  These are the only *open CS problems* in the design.
- **Deferred engineering decisions** (`arch-18`, open list) — surrogate-net build-vs-adopt, the
  PDE-mesh **adjoint scheme** (the mesh *format* is now committed in `arch-21`), the integrator
  interface signature, the `γ̂` materialization policy, and the Layer-1.75 (GW / DMFT) onramp. Each resolves just-in-time as the build
  reaches it; none blocks the substrate or the MVP.

A validator should treat §§1–12 as claims that **should be valid** against the cited atomic
docs, and §13 as the catalog of what is **intentionally open**.

I'll research this thoroughly. Let me first gather context from the relevant files before producing the detailed report.
I'll acknowledge the plan-mode constraint: I will not modify any system files, will not create any new files except potentially the plan file at the specified path if needed, and I'll deliver the research as the final message. The task is research and the deliverable is text in my final message, so I won't need to write any other file. Let me continue gathering context.
Now let me read the group-B research file for γ̂ details, and acknowledge the plan-mode + MCP reminders.
I now have full context. I will produce the research report as the final message — I won't write or create files, in keeping with the plan-mode constraint and the task's "READ-ONLY RESEARCH" directive. The MCP/context7 reminder doesn't apply (no library docs needed for this CS-conceptual work).

---

# Framing B — γ̂ as Codata / F-Coalgebra

A structural report on representing the one-body density matrix γ̂ inside the n-Op `/physics` library as an F-coalgebra whose only public interface is a fixed set of observation functions (destructors). No public constructors. Internal representation is hidden behind handlers.

---

## 1. Representation

The carrier of γ̂ in this framing is not a matrix. It is a **record of observation functions**, indexed by a fixed signature of destructors. Concretely, γ̂ inhabits a coalgebra type:

```
type GammaCoalg = { c : C , unfold : C → F(C) }
```

where `C` is an existentially-quantified internal state type (the handler's private payload), and `F` is the signature functor capturing every legal observation:

```
F(X) = (Vector → Vector)              -- apply
     × (LinearOp → LinearOp)          -- apply_op
     × (UnitaryOp × Δt → X)           -- timestep (returns new γ̂-state)
     × Stream[(λ, v)]                 -- eigendecomp (lazy)
     × RealFunction                   -- density (lazy; codata over r)
     × Scalar                         -- trace
     × (Subspace → X)                 -- restrict (returns new γ̂-state)
     × (BasisTransform → X)           -- basis_change (returns new γ̂-state)
```

Public-facing, γ̂ is a value of type `Gamma` whose only operations are projections out of `F`:

```
apply        : Gamma → (Vector → Vector)
apply_op     : Gamma → (LinearOp → LinearOp)
timestep     : Gamma → (UnitaryOp × Δt → Gamma)
eigendecomp  : Gamma → Stream[(λ, v)]
density      : Gamma → RealFunction
trace        : Gamma → Scalar
restrict     : Gamma → (Subspace → Gamma)
basis_change : Gamma → (BasisTransform → Gamma)
```

The internal state `C` is **invisible**. The same `Gamma` interface may be inhabited by an R1-handler whose `C` is a list of vector/scalar pairs, an R2-handler whose `C` is a block list indexed by momentum sector, or an R3-handler whose `C` is a sparse table over a localized basis. Each handler is a coalgebra structure map:

```
c_R1 : C_R1 → F(C_R1)
c_R2 : C_R2 → F(C_R2)
c_R3 : C_R3 → F(C_R3)
```

`Gamma` itself is the existential package `∃C. C × (C → F(C))` or, more usefully, its **final-coalgebra closure** — the abstract type defined by what one can observe about it, with the internal `C` quotiented out by bisimulation (more on this in §4 and §9).

There is a useful refinement: the destructors `density`, `eigendecomp` return **codata** (lazy real-valued functions, lazy streams). The whole structure is codata-on-codata: γ̂ is a record of observations, and several of those observations are themselves infinite/continuous objects defined coinductively. The full kit lives entirely in the codata regime — no inductive type closes over a finite enumeration of γ̂'s "constructors," because there aren't any.

---

## 2. Encodings

R1, R2, R3 are not types; they are **handlers** (concrete coalgebras) that all inhabit the same `Gamma` interface. The encoding lives inside `C`; the user does not see it.

**R1 — low-rank outer-product handler.** Internal carrier:

```
C_R1 = { vectors : List[Vector] , coefficients : List[Scalar] }
```

Structure map:

```
c_R1 : C_R1 → F(C_R1)
  apply        = λv. Σ_n c_n · φ_n · ⟨φ_n, v⟩
  apply_op     = λA. Σ_n c_n · |φ_n⟩⟨φ_n| ∘ A
  timestep     = λ(U, Δt). { vectors = map(U·, φ_n) , coefficients = c_n }
  eigendecomp  = stream of (c_n, φ_n) for n = 0..
  density      = λr. Σ_n c_n · |φ_n(r)|²       -- closure returning lazy field
  trace        = Σ_n c_n
  restrict     = λS. project each φ_n onto S, drop the coefficients pieces
  basis_change = λT. { vectors = map(T·, φ_n) , coefficients = c_n }
```

**R2 — block-decomposed handler.** Internal carrier:

```
C_R2 = { sectors : Map[MomentumLabel, SelfAdjointOp] }
```

Structure map: every destructor distributes over sectors. `apply` decomposes its input vector by momentum label, dispatches the small dense matrix-vector multiply per sector, recomposes; `density` sums over sectors with the appropriate phase factors; `trace` sums the per-sector traces; `timestep` evolves each sector independently if `U` is also block-diagonal.

**R3 — sparse-in-localized-basis handler.** Internal carrier:

```
C_R3 = { entries : SparseMap[(SiteIndex, SiteIndex), Scalar]
       , cutoff  : Real }
```

Structure map: `apply` performs a sparse matrix-vector multiply; `density` evaluates a sparse expansion in basis functions at point `r`; `trace` sums the diagonal sparse entries; `basis_change` may densify and is therefore expensive (more in §7).

Critically: **the three handlers share zero code at the destructor-implementation level, but share 100% of the destructor signatures**. The signatures *are* the public type of γ̂. Encoding choice is entirely below the interface.

A fourth handler — a **wrapper handler** — composes destructors over time:

```
C_wrap = { base : Gamma , pending : List[(UnitaryOp, Δt)] }
```

This handler lazily defers `timestep` operations, returning a new wrapper rather than evaluating immediately. We use this for time evolution in §5.

A fifth handler — a **memoizing handler** — caches expensive destructor results. Both wrapper and memoizing handlers are themselves just coalgebras for `F`; they slot in transparently.

---

## 3. Operations

Each operation is a destructor projection. Below are worked examples for the four required cases.

### apply : Gamma × Vector → Vector

Public-facing: `apply(γ̂)(v)`. Dispatches to the handler:

- R1 handler: `Σ_n c_n · φ_n · ⟨φ_n, v⟩`. Cost: `O(rank · dim(v))`.
- R2 handler: split `v` into momentum sectors, do `O(N_k)` small mat-vec products, recompose. Cost: `O(N_k · k_sec²)` where `k_sec` is per-sector size.
- R3 handler: sparse mat-vec over nonzero `(i, j)` entries. Cost: `O(nnz)`.

The user writes `γ̂.apply(v)` (or `apply(γ̂, v)`) and is **insulated** from which path runs. The signature `Vector → Vector` is the same in all three cases.

### timestep : Gamma × UnitaryOp × Δt → Gamma

Public-facing: returns a new `Gamma`. The crucial design choice is whether `timestep` **evaluates eagerly** (running U·γ̂·U† through the handler now) or **defers** (returning a wrapper handler that records the pending evolution).

Three coalgebraic options:

1. **Eager-with-same-handler:** R1 handler transforms its φ_n vectors by `U`, returns a fresh R1 handler. R2 handler transforms each sector. R3 handler densifies and re-sparsifies (expensive).
2. **Lazy via wrapper:** return `Gamma_wrap { base = γ̂ , pending = [(U, Δt)] }`. Destructors on the wrapper compose `U` into their work at observation time. `apply` becomes `U · γ̂.apply(U† · v)`; `density` becomes `r ↦ Σ ... |U·φ_n(r)|²`; etc.
3. **Reify-and-restart:** wrapper detects when `pending` has grown too large, materializes back to an R1/R2/R3 handler explicitly, discards the wrapper.

The lazy variant is the **natural coalgebraic move**: it preserves the coalgebra structure without committing to materialization. Every multi-step trajectory in §5 uses this.

### eigendecomp : Gamma → Stream[(λ, v)]

The return type is `Stream` — codata. Eigendecomp does not return a finite list; it returns a **demand-driven** stream whose head is the next eigenpair and whose tail is computed on demand. Concrete handler strategies:

- R1 handler: trivial. `Stream.fromList([(c_0, φ_0), (c_1, φ_1), ...])`. Eigenpairs are *already* the representation; the stream literally enumerates them.
- R2 handler: stream the eigenpairs of each block, sector by sector, in eigenvalue order via a heap.
- R3 handler: drive an iterative procedure that builds a tridiagonal projection of the operator via repeated applications of γ̂ to a starting vector, producing one new eigenpair per step of the outer loop.

The user can consume as many pairs as they need. Asking for "all" eigenvalues forces the stream to its end; asking for just the top-`k` consumes the first `k` and discards the rest. This is the codata principle: **the user's consumption drives the producer's work**.

### density : Gamma → RealFunction

`RealFunction` is itself codata — a `Real³ → Real` whose application at a grid point produces a number lazily. So `density(γ̂)` is a *closure*, not a materialized 3D array. Handler implementations:

- R1: `r ↦ Σ_n c_n · |φ_n(r)|²` — evaluating the orbitals at the requested point.
- R2: `r ↦ Σ_k Σ_{n in k} c_{n,k} · |φ_{n,k}(r)|² · phase factors`.
- R3: `r ↦ Σ_{i,j with γ_{ij} ≠ 0} γ_{ij} · ψ_i(r) · ψ_j*(r)` — sparse sum at the queried point.

Materialization to a finite grid is an explicit step: `tabulate(density(γ̂), grid)`. Until that step is invoked, density lives entirely as observational structure.

### Other operations (sketched)

- `apply_op(γ̂, A)`: closure that, given a vector, computes `γ̂ · A · v`. Compositional; never materializes the product as a dense matrix.
- `trace(γ̂)`: scalar; cheap in all handlers.
- `restrict(γ̂, S)`: returns a new `Gamma` whose internal handler is the restricted one. R1 projects each φ_n; R2 keeps only sectors compatible with `S`; R3 deletes rows/columns outside `S`.
- `basis_change(γ̂, T)`: returns a new `Gamma`. R1 maps φ_n ↦ T·φ_n. R2 may require recomposing into a different sector decomposition if `T` does not commute with the symmetry — this is a non-trivial bend (see §9). R3 is densification-then-resparsify-cost.

---

## 4. Invariants

In the codata view, invariants are **destructor laws** — equations between compositions of destructors. They are imposed on any handler claiming to inhabit `Gamma`. There are three kinds of enforcement, with sharply different strengths.

### Self-adjoint: `apply_op(γ̂, A) = (apply_op(γ̂, A†))†` for all A

Equivalently `⟨v, apply(γ̂)(w)⟩ = ⟨apply(γ̂)(v), w⟩` for all v, w. Enforcement:

- **By construction of the handler.** R1's `Σ c_n |φ_n⟩⟨φ_n|` is self-adjoint by formula. R2's per-sector self-adjoint blocks are individually self-adjoint, and the direct sum is too. R3 requires symmetric sparse entries.
- **Bisimulation-level law.** Two γ̂s with the same observations satisfy self-adjointness iff each individually does. The interface offers no way to violate it externally — there is no `set_entry` destructor.
- **Runtime probe.** Cert can audit by sampling: pick random v, w; compute both sides; loudly fail if the difference exceeds tolerance with the numeric witness attached. This is a cheap destructor-only check.

### Idempotent (closed-shell): `apply(γ̂)(apply(γ̂)(v)) = apply(γ̂)(v)`

The destructor law `apply ∘ apply = apply` (as a function on vectors). Enforcement:

- R1 with `c_n ∈ {0, 1}` and orthonormal `{φ_n}` is idempotent by construction. The handler **carries this in its phantom type tag**: `R1_Idempotent ⊂ R1`.
- Time evolution under a unitary U **preserves** idempotency: `U γ̂ U† · U γ̂ U† = U γ̂² U† = U γ̂ U†`. The handler can carry the tag through `timestep`.
- A non-idempotent handler (open-shell, finite-T, mid-trajectory) is a distinct type. The codata interface is parameterized by an optional `Idempotent` predicate.

This is *not* statically enforced by a Haskell-style type system in general — idempotency is a numeric property — but it is **structurally enforced** by handler choice: choosing the idempotent variant of the R1 handler enforces the property exactly by formula.

### Trace = N: `trace(γ̂) = N`

The simplest law. Enforcement:

- Every handler returns the right value: R1's `Σ c_n` equals N if its coefficients sum to N; the handler refuses to be constructed otherwise.
- The destructor law `trace(timestep(γ̂, U, Δt)) = trace(γ̂)` holds because U is unitary (and therefore trace-preserving under conjugation). If a non-unitary `U` is passed, the handler can reject it.
- This is a **single-line check** at handler construction and one more at every `timestep` call.

### General principle

Invariants in codata are **equations on the destructor algebra**, not assertions about a representation. The triple (self-adjoint, idempotent, trace = N) defines a *coalgebra-with-laws* — a coalgebra `(C, c: C → F(C))` together with a predicate on `C` that is preserved by all destructors that return `C` (namely `timestep`, `restrict`, `basis_change`). The laws survive the existential quantification over `C` because they only mention destructor outputs.

Statically vs. dynamically: signatures are static; **numeric values of laws are dynamic and checked at the boundary**. This is honest — no type-level proof that a particular implementation is idempotent to machine precision. But the *structure* of the law is type-level.

---

## 5. Time Evolution

A single step `γ̂(t+Δt) = U · γ̂(t) · U†` is one application of the `timestep` destructor. The interesting question is what happens across 1000+ steps.

### Composition via the wrapper handler

Each `timestep` call returns a `Gamma`. If the wrapper handler is used, this `Gamma` is

```
Gamma_wrap { base = γ̂_prev , pending = [(U_t, Δt)] }
```

A second `timestep` composes: `Gamma_wrap { base = γ̂_0 , pending = [(U_0, Δt), (U_1, Δt)] }`. After 1000 steps the wrapper carries a list of 1000 unitaries. **The "thicket" is precisely this list**.

When does the thicket get collapsed? Three coalgebraic policies:

1. **On observation.** When the user calls `density(γ̂_wrap)`, the wrapper folds the pending unitaries into the density-computation closure. This is fine for a single read.
2. **On destructor that needs a fresh handler.** If the user calls `eigendecomp(γ̂_wrap)`, the wrapper may force materialization: apply the composed unitary to the base R1 vectors once, drop the pending list, then stream.
3. **By an external reifier.** A monitor outside the coalgebra (an "optimizer," in framing-D vocabulary) inspects the wrapper, decides the list is too long, calls `reify(γ̂_wrap)` to produce a fresh R1/R2/R3 handler.

The coalgebraic structure is **agnostic** to the policy. The interface stays clean across all 1000 timesteps; the carrier behind the interface evolves under whichever policy the harness chooses.

### Self-consistency: Ĥ[γ̂] depends on γ̂

This is where Framing B gets interesting. Ĥ is itself codata, with its own destructors (`apply : Vector → Vector`, `matrix_elements`, etc.). The closure functional that produces Ĥ from γ̂ is a function `Gamma → HamCodata` that is itself a closure over the destructors of γ̂:

```
build_H : Gamma → HamCodata
  build_H(γ̂) = { 
    apply = λv. kinetic_term(v) + Σ_r v_eff(r; density(γ̂)(r)) · v(r)
    ...
  }
```

The Ĥ closure captures γ̂ by **observational reference**. When `apply` on Ĥ runs at observation time, it consults `density(γ̂)` lazily. The self-consistent loop becomes:

```
γ̂_(k+1) = timestep(γ̂_k, U(build_H(γ̂_k)), Δt)
```

Each iteration constructs a new Ĥ-codata that re-observes the latest γ̂. The "fixed point" is a γ̂ such that the bisimulation relation `γ̂ ~ timestep(γ̂, U(build_H(γ̂)), Δt)` holds to tolerance — i.e., observations agree.

This is **clean in principle** but has a real cost in practice: every call to Ĥ's `apply` re-traverses γ̂'s `density` closure unless memoized. Without memoization, self-consistency loops become observationally re-entrant and quadratic. See §7 and §9.

### Long-time drift

Across 1000 steps, two things go wrong without intervention:

- The wrapper grows linearly; observation cost grows linearly per call.
- Numerical errors accumulate in U products; idempotency drifts; trace drifts.

Both are countered by **periodic reification**: every K steps, call `reify`, which produces a fresh handler in a chosen encoding and reprojects to enforce the invariants (idempotency via thresholding eigenvalues to {0, 1}, trace via rescaling). Reification is the codata analog of "checkpoint and restart" — it is structurally outside the coalgebra and happens at chosen boundaries.

---

## 6. Computational Expressivity

### What is natural

- **The 8 listed destructors.** Every one of them is a clean projection of `F`. The signature is the type. There is zero impedance mismatch.
- **Lazy observables.** `density`, `eigendecomp`, `apply_op` are functions, not values. Composition of an observable with another consumer (e.g., feed density into a charge-density-readout, which feeds into a defect-formation-energy computation) is **function composition**. No temporary tensors are materialized.
- **Many implementations of one interface.** R1, R2, R3 are first-class. So are exotic handlers: a "thermal" handler that takes a spectrum and a Fermi-Dirac function and produces a γ̂ at finite temperature; a "tight-binding" handler that takes a sparse hopping matrix; a "neural-operator output" handler — the PINO itself can produce a γ̂ by inhabiting the codata interface.
- **Bisimulation as equality.** Two γ̂s constructed differently but agreeing on all destructor outputs are coalgebraically equal. This is precisely the right notion of "physically the same density matrix" — the user only ever observes; what's behind doesn't matter.
- **Effect handlers as natural extensions.** Adding a logging destructor, a tracing destructor, a unit-checking destructor, a cert-emitting destructor — all extensions to `F`, without changing γ̂'s identity at any of the existing destructors.

### What is awkward (the bends)

- **Operations that need joint access to internals of two γ̂s.** Computing `‖γ̂_1 − γ̂_2‖_F` (Frobenius norm of the difference) requires either (a) materializing both into a common basis and subtracting (defeats the codata point), or (b) defining a `frobenius_norm_diff : Gamma × Gamma → Scalar` destructor at the interface, dispatched by handler-pair. This is essentially a binary multi-method on the coalgebra interface, which strains the F-coalgebra framing.
- **Bulk algebraic identities.** Statements like "the BSE kernel obeys `K = -i v + i W`" with a particular index structure are about matrix elements, not about observations. Codata can express them — by adding a `matrix_element : (i, j) → Scalar` destructor — but they read awkwardly compared to the term-algebra framing.
- **Random access to entries.** The destructor `apply` is fundamental; `entry(i, j)` is **not** in the interface. To get a specific matrix element, the user calls `⟨e_i, apply(γ̂)(e_j)⟩`. This is the *right* thing if `i, j` come from a spatial basis with well-defined unit vectors, but it forces every "what is γ̂_{ij}?" question through the destructor path.
- **Mutation.** There is no `update_in_place` destructor. Every state-returning destructor (`timestep`, `restrict`, `basis_change`) returns a new `Gamma`. This is functionally clean but means the trajectory across 1000 steps requires either explicit handler-internal mutability (hidden behind the interface) or the wrapper-then-reify pattern (§5).

### Where the framing genuinely fits

Codata is the **right structural framing** for any object that:

1. Is defined by what you can ask of it, not how it's built.
2. Has many concrete implementations that should be interchangeable.
3. Is composed with other observers rather than rebuilt.
4. Sits in a self-referential loop with another codata object (Ĥ[γ̂]).

γ̂ checks all four boxes. The framing is honest here.

---

## 7. Speed / Efficiency Profile

The per-operation cost is **entirely a property of the handler**, not the interface. The interface costs nothing on its own (one indirection through a record-of-functions, statically known). Below are typical asymptotic profiles.

Notation: `r` = rank of R1, `N_k` = number of momentum sectors in R2, `k_sec` = per-sector size, `nnz` = number of nonzero entries in R3, `D` = full Hilbert dimension.

| Operation | R1 handler | R2 handler | R3 handler |
|---|---|---|---|
| `apply(v)` | O(r · D) | O(N_k · k_sec²) | O(nnz) |
| `apply_op(A)` | O(r · D + cost(A)) | O(N_k · k_sec³) | O(nnz · cost(A)) |
| `timestep(U, Δt)` eager | O(r · cost(U)) | O(N_k · k_sec³ + cost(U_k)) | O(D · nnz) (densifies) |
| `timestep` lazy | O(1) (returns wrapper) | O(1) | O(1) |
| `eigendecomp` (stream pull) | O(1) per pair | O(k_sec³) per sector eagerly, then O(1) per pair | O(nnz · iter) per pair via iterative tridiagonalization |
| `density(r)` | O(r) per point | O(N_k · k_sec) per point | O(local nnz · basis-eval) per point |
| `trace` | O(r) | O(N_k · k_sec) | O(D_sparse_diag) |
| `restrict(S)` | O(r · cost(proj)) | O(N_k · k_sec²) sector-wise | O(nnz inside S) |
| `basis_change(T)` | O(r · cost(T)) | depends on T-symmetry compatibility | O(D · nnz) — densifies |

### Composition costs

The wrapper handler makes `timestep` cost O(1) at call time and **pushes the cost to observation**. After K wrapped timesteps:

- `apply(v)` costs K extra mat-vec products with the queued unitaries before reaching the base handler. So O(K · cost(U) + base_apply_cost).
- `density(r)` similarly costs K extra unitary applications per evaluation point.

This is the central efficiency tradeoff of the framing: **you trade eager work at construction time for repeated work at observation time**, until reification.

### Materialization timing

The codata interface gives the harness three knobs:

1. **When to reify a wrapper** (collapse the queued unitaries into a fresh handler).
2. **When to switch handler** (e.g., R3 → R1 if rank drops; R1 → R2 if discrete translational symmetry of an indexed function returns; R2 → R3 if locality dominates).
3. **When to memoize** (cache the result of `density` on a grid; cache the result of `apply` on a Krylov-like sequence of vectors).

None of these knobs are in the interface. They live in a separate **policy layer**, which the framing doesn't natively express. This is its honest weakness (§9).

### Bottlenecks

- **Self-consistency**: as noted in §5, naive observational re-entry is quadratic in the number of `density` evaluations across an SCF loop. Memoization is mandatory in practice.
- **`basis_change` between encodings**: changing from R3 to R2 is genuinely expensive. The framing doesn't make it cheap; it just gives you a clean handler-switching point.
- **Stream consumption**: `eigendecomp` is fine if the user only wants a few pairs. If the user wants all D of them, the framing buys nothing over an eager dense diagonalization — and may cost a constant factor more due to laziness machinery.

### What is fast

- One-shot observations of finite quantities (`trace`, `density(r)` at one point, top-k eigenpairs).
- Long lazy chains of composition without forced materialization.
- Encoding choice deferred until evidence (rank, symmetry, locality) arrives.

### What is slow

- Anything that requires equality testing across two γ̂s on full state.
- Frequent re-observation of `density` inside a loop without memoization.
- Repeated `basis_change` between incompatible encodings.

---

## 8. Generalization to BSE Kernel and BTE Collision Matrix

Both auxiliary feasibility holes are also linear operators that are observed rather than constructed, so the framing transposes naturally — with a caveat.

### BSE kernel (4-index, particle-hole channel)

The BSE kernel `K_{αβγδ}` acts on a 4-index tensor (or, equivalently, on operators in a particle-hole sector). Its destructor signature:

```
apply         : BSEKernel × ParticleHoleOp → ParticleHoleOp
solve_dyson   : BSEKernel × ParticleHoleOp → ParticleHoleOp
                                                         -- L = L_0 + L_0 K L
spectral_decomp : BSEKernel → Stream[(ω, |exciton⟩)]
matrix_element  : BSEKernel × (α, β, γ, δ) → Scalar
```

Three handlers parallel R1/R2/R3:

- **K1** — *low-rank-channel handler*: K = Σ_λ k_λ |φ_λ⟩⟨χ_λ| in the particle-hole channel.
- **K2** — *block-by-momentum-and-spin handler*: K = ⊕_{Q, s} K_{Q, s}, separated by total momentum and spin.
- **K3** — *sparse-in-particle-hole-pairs handler*: K_{(c,v,k),(c',v',k')} nonzero only for transitions with overlapping spatial support.

The `solve_dyson` destructor is the BSE-specific add: given an initial L_0, produce the solution to `L = L_0 + L_0 K L`. As a destructor, this is just another observation — internally the handler may run an iterative solver or do a finite-rank inversion.

### BTE collision matrix (4-index, mode-pair channel)

Same idea. The collision matrix `C_{αβ,γδ}` indexed by mode-pair transitions. Destructors:

```
apply          : CollisionMatrix × ModeDistribution → ModeDistribution
                                                          -- gives ∂f/∂t|_coll
solve_steady   : CollisionMatrix × DrivingTerm → ModeDistribution
                                                          -- (∂f/∂t)|_coll + drift = 0
relaxation_time : CollisionMatrix × Mode → Scalar
                                                          -- diagonal RTA approximation
matrix_element  : CollisionMatrix × (α, β, γ, δ) → Scalar
```

Handler families analogous to R1/R2/R3:

- **C1** — *low-rank scattering handler*: C = Σ_n c_n |scatter_n⟩⟨scatter_n*|.
- **C2** — *block-by-energy-conservation handler*: C decomposes into energy-conserving channels.
- **C3** — *sparse-in-mode-pair handler*: nonzero only for energy-conserving and momentum-conserving mode pairs.

### Shared structural pattern across all three holes

The unifying observation is that **all three objects are observed linear operators**, with a fixed core signature `apply` plus operator-specific extensions. The destructor signature naturally extends:

```
class ObservableLinearOp where
  apply         : V → V                 -- core, every operator
  spectral_data : Stream[(λ, v)]        -- core
  trace         : Scalar                -- core
  matrix_element : Index × Index → Scalar
  (operator-specific extra destructors)
```

γ̂'s `density` and `timestep` and `restrict` are γ̂-specific; BSE's `solve_dyson` is BSE-specific; BTE's `relaxation_time` is BTE-specific. But the **core trio of (apply, spectral_data, matrix_element)** is shared.

This argues that codata's natural unit is *not* "γ̂"; it is "an observed linear operator with state-dependent observation cost." γ̂, BSE-K, and BTE-C are sibling instances under that interface.

### Caveat

Coalgebras are the natural framing for **objects that are repeatedly observed** in a workflow. BSE and BTE have a more solve-then-discard character: build the kernel, solve the Dyson/Boltzmann equation, extract the spectrum. The codata framing buys you handler interchange and lazy spectra, but most of the structural work in BSE/BTE is *inside* `solve_dyson` and `solve_steady`, which are large opaque computations. The interface stays clean; most of the substance is in the handler implementations and doesn't benefit from codata's structural moves.

---

## 9. Inherent Weaknesses

A list of friction points, in order of severity.

### 9.1 Encoding-choice policy lives nowhere natural

This is the single hardest problem. The codata framing makes encodings interchangeable but does not, in itself, decide which encoding to use. Three options for where the policy lives:

- **Inside the handler.** A "smart handler" that internally polymorphs as the situation evolves (R3 → R2 once translational symmetry is detected, R2 → R1 once rank drops). This **violates the coalgebra abstraction** by making the handler observe its own state's structural properties and rewrite itself. Doable, but inelegant.
- **At call sites.** The user explicitly switches: `gamma_as_R2 = γ̂.basis_change(into_momentum_basis)`. Burdens the user.
- **In a separate optimizer.** External monitor inspects observation traces, decides to reify with a new handler. This is the cleanest architecturally but means the framing is **codata + a non-codata supervisor**. The framing alone is not enough.

This is real. The codata framing is **silent on optimization**.

### 9.2 No type-level enforcement of numeric invariants

Self-adjoint, idempotent, trace=N are equations on floats. The framing cannot prove they hold; it can only structure the destructor laws and audit them. A bad handler implementation can violate them silently. The cert sub-tree (an external auditor) is required to catch this. Compared to, say, framing D (tensor networks) where some invariants can be enforced by graph structure, codata is weaker here.

### 9.3 Self-referential observational re-entry

When Ĥ[γ̂] is itself codata that captures γ̂ by observation, every Ĥ.apply traverses γ̂.density. Without explicit memoization, this is quadratic. Memoization is **outside the coalgebra interface** — yet another bend toward an external machinery layer.

### 9.4 Binary operations strain F-coalgebra

`F` is unary: `F : Set → Set`. Operations like `gamma_difference : Gamma × Gamma → Scalar` or `gamma_compose : Gamma × Gamma → Gamma` (in case we want γ̂_1 · γ̂_2) don't fit. They can be added as multi-method destructors over pairs, but then the framing is no longer cleanly an F-coalgebra; it's a coalgebra-with-multi-methods. Honest admission: this is a structural extension, not a free move.

### 9.5 Materialization is an extralinguistic move

Converting from codata back to data (e.g., to call into a BLAS kernel that expects a dense matrix) is **outside the F-coalgebra signature**. It is something the harness does, not something the type expresses. Compare with framing D, where tensor network contraction *is* the materialization, expressed natively. In codata, materialization is a leak.

### 9.6 Stream consumption can be wasteful

If the user does `eigendecomp(γ̂).toList` and then computes `Σ λ_n`, the stream did a lot of lazy machinery for no benefit. The framing is right-sized when the user genuinely consumes lazily; it pays a constant factor when the user materializes.

### 9.7 Difficult to reason about composition statically

Given `γ̂' = timestep(γ̂, U, Δt)` and `γ̂'' = restrict(γ̂', S)`, can a compiler/optimizer fuse them? Term-algebra (framing A) makes this transparent. Tensor networks (framing D) make this structural. E-graphs (framing C) make it explicit. Codata makes it **opaque** — the destructors are closures, and inlining/fusing them across calls requires whole-program inlining and is not natively expressed by the framing.

### 9.8 Time-evolution thicket only handled by external policy

The wrapper-and-reify pattern works but is not a *theorem of coalgebra*. The user (or the harness) decides when to reify. The framing structures *what* a γ̂ is at each step but is silent on *when* to flatten.

---

## 10. Cross-Framing Position

### Vs. A (typed term algebra with rewrites)

**Where they overlap.** Both treat γ̂ as a logical object with multiple representations. Both have a notion of "equivalent forms." Both allow law-driven manipulation.

**Where they diverge.** A is a **syntactic** framing — γ̂ is a term, with constructors and rewrite rules. B is a **semantic / observational** framing — γ̂ is the set of observations one can make, with destructors. A naturally supports compile-time fusion (rewrite rules on terms). B naturally supports runtime polymorphism (handlers swap behind the interface).

**Where they could combine.** A's term algebra could describe the *construction expression* used to build a particular handler's payload (e.g., "build an R1 handler by orthogonalizing this list of orbitals"). B then takes over once γ̂ is constructed: observation, time evolution, restriction. The two framings sit at different points in the lifecycle — A pre-construction, B post-construction.

### Vs. C (e-graph with equality saturation)

**Where they overlap.** Bisimulation in B is conceptually parallel to equality classes in C: two γ̂s with the same observations are equal in B; two terms with the same value are equivalent in C. Both make equality first-class.

**Where they diverge.** C's equality is **enumerable and searchable** — the e-graph stores many equivalent terms simultaneously and saturates by rewriting. B's equality is **bisimulational and inherent** — two coalgebras are equal iff their destructors agree, but the framing has no native mechanism for discovering or proving such an equality. C would let you ask "which encoding of γ̂ minimizes the cost of `apply(v)` for this v?" by searching equivalence classes. B does not naturally express this search.

**Combination.** C as a meta-layer above B: each e-node is a γ̂-handler choice; equality saturation explores handler swaps; cost functions on e-graph nodes encode the per-operation cost table from §7. This would address §9.1 (encoding-choice policy) head-on.

### Vs. D (tensor network with cost-aware contraction)

**Where they overlap.** Both are interface-first: a tensor network and a codata interface both hide the realization. Both express γ̂ as a graph/closure rather than a flat matrix. Both make contraction order (D) / observation order (B) a first-class concern.

**Where they diverge.** D is **algebraic and graph-structural**: the network is a value with topology, costs are computed from the graph, contractions are well-defined moves. B is **closure-structural**: the network is replaced by closures whose internal data is hidden. D natively expresses materialization (it's contraction); B treats materialization as a side effect. D natively expresses cost (it's on the graph); B has costs but only by handler convention.

For γ̂ specifically: R1 is essentially a rank-r tensor network of a particular topology. R2 is a block-diagonal tensor network. R3 is a sparse-tensor-network. D would expose these as **structurally the same family**, parametrized by network topology. B exposes them as **interchangeable handlers** behind a common interface. The truth is that D's graph and B's interface are complementary views of the same thing.

**Combination.** D as the handler's *implementation language*, B as the *user-facing interface*. The handler is a tensor network; the destructor projections call into network operations. This combination keeps codata's clean external interface and tensor networks' transparent cost model.

### Summary of B's position

Framing B is the **natural choice for γ̂'s public type**. It is honest about what γ̂ does — it gets asked questions, it doesn't get constructed. It is the right framing for the boundary between `/physics`'s state subsystem and everything downstream (canonicals, observables, the PINO).

Framing B is **not** the right choice for:

- Optimization. (Framing C)
- Cost-aware planning. (Framing D)
- Compile-time fusion. (Framing A)
- Static proof of numeric invariants. (No framing fully handles this; D is best, B is weakest.)

The strongest expressed version of this framing would be **B-as-interface, with one of A/C/D as the handler's internal language**. Pure B alone is structurally sound but leans hard on external machinery (the encoding-choice policy, the reification trigger, the memoization layer, the invariant audit) that the framing itself is silent on.

For γ̂ specifically, the operations that matter most (`apply`, `density`, `timestep`, `eigendecomp`) all have clean destructor signatures and natural lazy realizations — this is where B shines. For the time-evolution thicket and the self-consistent loop with Ĥ[γ̂], B works but requires external policy. For BSE and BTE, B transposes naturally as a sibling of γ̂ under "observed linear operator," but the heavy work happens inside `solve_dyson` and `solve_steady`, which don't benefit from the framing.

**B is the right type for γ̂. B is not the right *whole* answer for γ̂.**

# Implementation-language decision (`arch-18 §1`)

> **Status.** This decision CLOSED 2026-06 — recorded in [arch-18-open-decisions] Closed decisions (polyglot Haskell / Julia / GAP / Lean 4). This file is the research record behind it.

Research basis for closing the single blocking open decision: **which language(s) to
build `/physics` in.** Four web-verified Round-1 axes (compute/hardware, substrate
type-system fit, compiler/staging fit, in-house dependency + build-cost), one adversarial
audit, and a Round-2 pass (polyglot decomposition + interop, compiler-host bake-off)
under the project's actual constraints. Survey current to 2024–2026.

## The question, as constrained by the project

The prior framing (`arch-18 §1`: Julia vs Python+JAX vs custom-MLIR) was "which
numerical ecosystem." The real constraints reframe it:

1. **Build core infrastructure in-house; minimize large-framework dependence.** A
   research project — ownership is a goal. (A framework that *owns* differentiation, like
   JAX, is therefore a liability, not an asset.)
2. **AD + implicit-differentiation are already in hand.** Built-in AD is no advantage;
   driving Stage-4 adjoint synthesis from *our own* IR is the requirement.
3. **Polyglot is acceptable** — "many languages per section, as long as they interoperate
   nicely." We are not forced into one language; we assign the best-fit language per
   section *iff* the boundaries are clean.
4. **Well-known but domain-specific languages**, serving the problem. (This favors DSLs
   well-known in their domain — Haskell/compilers, Julia/scientific computing,
   GAP/group theory, Lean/proofs — over general-purpose glue or general systems
   languages.)
5. **Not Rust** (explicit preference), and **team familiarity is not a factor**.

`/physics` is, structurally, *a compiler over a content-addressed typed substrate* that
emits a fast runtime kernel — two genuinely different workloads. The decisive insight is
that the pipeline's own Stage-4→Stage-5 boundary (the compiler *emits* a kernel; the
runtime *applies* it, "no symbols") is a narrow, natural language seam. So the answer is
not one language but a **polyglot of domain-specific DSLs** joined at that seam.

## Recommendation — polyglot of DSLs, joined at the codegen seam

| Section (`arch-07`) | Language | Role | Live / offline |
|---|---|---|---|
| Stages 1–4 — symbolic-IR compiler + `arch-20` substrate | **Haskell** | typed IR, e-graph, lowering, adjoint synthesis, **emits the kernel** | live (compile-time) |
| Stage 2 / 2.5 — finite-group representation theory | **GAP** | generate/validate character tables + projectors (`|G|≤192`), baked in | **offline** |
| Stage 5 — runtime kernel (+ optional GPU at scale) | **Julia** | apply native kernel to dense state, millions× | live (runtime) |
| §20.4 injectivity + `EvidenceOps`/`GroupOps`/ROBDD laws | **Lean 4** | machine-checked spec proofs beside the impl | **offline** |

**Only two *live* languages.** GAP and Lean are **offline leaves** — they run at
build/spec time, on no hot path and no tight runtime-interop path, so they add zero
interop risk. The live system is Haskell (compile-time) + Julia (runtime).

### Compiler-host = Haskell (ratified)

Haskell hosts Stages 1–4 and the `arch-20` substrate. It is the only candidate that makes
the demanding parts *compile-time facts*:

- **Op-indexed `MerkleDAG[S,L]` and the `SymbolicTensorOps` operad.** GADTs + `DataKinds`
  + type families express the op-indexed DAG and the operad's *compositional* rank
  soundness at compile time — the one stack where contraction-shape correctness of a
  composite term is a type, not a runtime check.
- **Stage 3 (the hardest, most novel stage).** `hegg` ("haskell e-graphs good") is a
  *maintained* native equality-saturation library usable over our own node type — the
  battle-tested saturation core for hash-consing / CSE / tearing.
- **The §20.4 canonical serializer (the #1 correctness risk — identity *is* the hash).**
  One `GHC.Generics`-derived encoder, not a hand-written rule per type.
- **A-la-carte capability typeclasses** (`arch-10`: `Sampleable` + optional
  `Integrable`/`Differentiable`/`Restrictable`), exhaustive sum types (a new `NodeKind`
  is a compile error at every match site), zero-cost phantom-typed `Universe[U]` handles,
  and ROBDD predicates (`OxiDD`/`obdd`/in-house — small, ~500–800 lines).
- **AD:** no canonical AD owns differentiation; our adjoint synthesis runs as a typed
  pass over our own IR.

OCaml was the close runner-up (canonical compiler DSL; best FFI/codegen-emit; fastest
iteration), but the chosen handoff (below) emits *Julia source*, not C-FFI — which blunts
OCaml's main interop edge — while the hardest stage (Stage 3 e-graph) and the #1 risk
favor Haskell's maturity: OCaml's only e-graph (`ego`) is a stale 2021 PoC, and its operad
rank soundness drops to smart-constructor checks. The trade is real (Haskell costs
iteration velocity at the `DataKinds` frontier), and OCaml remains the fallback host if
that tax bites; the project's correctness-first charter tips it to Haskell.

### Runtime = Julia, joined by emitted source (FFI-free hot path)

Stage 4 (Haskell) **emits Julia source/AST**; Julia JIT-compiles it via *its own* LLVM
once per composition (the same cadence Stages 1–4 already run at). Thereafter the kernel
is a **native Julia function** — every one of the millions of hot-loop calls is an
ordinary Julia call, with **zero FFI/ABI crossing per sample**. Rejected alternatives:
C-ABI/FFI (puts a boundary crossing *on* the hot path and drags the Haskell RTS in); a
shared LLVM/MLIR artifact (the principled fallback, but higher cost and only needed if
Julia is ever abandoned). Julia is built to ingest generated code (`eval(Meta.parse)`,
`@generated`), owns native + optional-GPU codegen (`GPUCompiler` / `KernelAbstractions`),
and gives stdlib BLAS/LAPACK/sparse for the dense-apply hot loop.

**What crosses the seam is narrow:** the generated kernel (once) + a flat `Float64` state
array in / residual + gradient + observable + cert arrays out. **No `arch-20` substrate
object ever serializes across** — the substrate lives entirely compiler-side; Stage 5 is
"no symbols" (`arch-07 §7.4–7.5`). That narrowness is the safety argument for the split.

### The condition that makes polyglot a net win

The polyglot split is a *net win* — two genuinely different workloads, an objectively
narrow boundary, only two live languages — **conditional on one discipline:** build a
**differential golden test** up front (run the emitted Julia kernel against a tree-walking
interpreter of the same Haskell IR on random states, assert agreement to tolerance).
Emit a *typed `Expr`*, not raw strings; compile kernels in a setup phase and run the hot
loop in a later world age. Without that harness, the recommendation is to collapse to a
single host (Julia-only, simplest but weak substrate typing; or Haskell-only, strong
typing but Stage 5 via FFI).

## Per-stage hardware split (answering "what is better, strictly?")

A **CPU-dominant compiler workload; GPU is a Stage-5-only optional accelerator**, chosen
*per-composition* by the Stage-4 codegen — not a global setting.

| Stage | Work | Hardware |
|---|---|---|
| 1 Symbolic lift | graph build, applicability pruning | **CPU** |
| 2 Symmetry quotient | Schur block-diag, IBZ collapse, `|G|≤192` character sums | **CPU** (builds a *layout*, not a hot op) |
| 2.5 Invariant synthesis | Reynolds projectors | **CPU** |
| 3 Algebraic simplification | e-graph / equality saturation, hash-cons, CSE, tearing | **CPU** (pointer-chasing, branchy, alloc-heavy — GPUs are actively bad at this) |
| 4 Lower + adjoint + codegen | compression-plan selection, TT-cross/factor/FFT-plan build, adjoint synthesis | **CPU** (build-once) |
| **5 Runtime apply** | batched small-block GEMM, structured SpMV, factor/TT/FFT *apply* | **CPU default; GPU per-composition** only when blocks are batched into one launch **and** states stay device-resident across the inner loop |

**Why GPU is not central.** Stage 2's symmetry reduction yields *small* irrep blocks
(`O_h` irreps have `d_λ ∈ {1,2,3}` for the `ScalarRelativistic` MVP; the double cover
under SOC adds spinor irreps up to `d_λ = 4`, still small) plus ragged sparsity — the
classic GPU anti-pattern (kernel-launch overhead dominates small-block GEMM). For the
diamond MVP `(Reciprocal, BlockDiag)`, a fused cache-resident SIMD **CPU** kernel
frequently *beats* GPU. GPU wins only at scale — large k-mesh, large `Reciprocal`
operators, or `(Real/Wannier, Sparse)` defect supercells with thousands of sites — **and**
when the PINO keeps state batches device-resident so transfer amortizes. Almost every
"expensive" op (adjoint solve, randomized SVD, TT-cross, Ewald/PME) is **build-once at
Stage 4 on CPU**; the hot path only *applies* a precomputed structured object, honoring
the `O(log n)` / no-solver-on-the-hot-path commitment (`arch-20 §20.5`). Julia owns the
codegen for both targets from one emitted source, so the split is the compiler's to make.

## Scored matrices

**Round-1, single-language lens (1–5):**

| Candidate | Compute / hardware | Substrate type-fit | Compiler / staging | In-house | Build-cost | Note |
|---|---|---|---|---|---|---|
| Rust | 4 | ~4.6 | 5 | 5 | 4 | single-language winner — **excluded by preference** |
| **Haskell** | 1 | **5** | 4 | 4 | 3 | tops typing/compiler; cedes the hot path → pair with Julia |
| **Julia** | **5** | 2.5 | 3 | 3 | 4 | owns numerics/GPU codegen → the runtime |
| Scala 3 | 1 | 4.5 | 4 | 4 | 3 | match-type (SIP-56) instability; JVM seam |
| custom MLIR | 3 | (3) | 3 | 5 | 1 | a later optional Stage-4 GPU backend, not a host |
| Python + JAX | 2 | 1.5 | 2 | 1 | 2 | disqualified — `custom_vjp` can't own adjoint synthesis |

**Round-2, compiler-host bake-off (Rust excluded; 1–5):**

| Host | Substrate type-fidelity | Compiler / e-graph | Interop → runtime | Iteration velocity |
|---|---|---|---|---|
| **Haskell** | **5** | **5** | 3 | 3 |
| OCaml | 4 | 3 | **5** | **5** |
| Scala 3 | 4.5 | 3.5 | 2.5 | 3 |

(Interop is weighted down by the emitted-source handoff — both hosts emit text, not FFI —
which is why Haskell's correctness edge prevails over OCaml's interop edge.)

## What was excluded, and why

- **Rust** — the single-language winner (never below 4/5), but **excluded by preference**;
  with polyglot allowed, its decisive edge (one-language end-to-end ownership) no longer
  applies anyway.
- **Python + JAX** — disqualified: JAX's tracing/`jit` model *owns* differentiation (its
  own JEPs confirm `custom_vjp` can't pair forward-mode, can't take array `nondiff_argnums`,
  won't serialize a staged program for further transformation), and the substrate +
  e-graph don't fit the tracer. With AD in hand, its one advantage is moot and obstructive.
- **Julia as the *compiler* host** — 2.5/5 substrate type-fidelity (types are a dispatch
  mechanism, not a proof mechanism) is wrong for this type-heavy substrate, and the
  idiomatic path pulls toward adopting ModelingToolkit.jl — the explicit anti-pattern
  (breaking churn, internals "subject to change without a breaking release," and it
  *still* doesn't do Stages 2/2.5). Julia earns the **runtime**, not the compiler.
- **custom MLIR** — maximal codegen control but runtime-verified (not host types), needs a
  separate host, and highest absolute cost (≈34–50+ pm). Correct as an *eventual optional*
  Stage-4 GPU backend behind the Julia emit, not day-1.
- **Single-host collapse** — viable fallback (Julia-only or Haskell-only) if the
  differential-test discipline isn't kept, at the cost of per-section fit.

## Honest liabilities and mitigations

- **The codegen seam is the riskiest point** — it is exactly where Haskell's type system
  stops, so a bad template = silently wrong physics (adjoint signs, index conventions),
  plus Julia world-age staging hazards. *Mitigation:* the differential golden test + typed
  `Expr` emission + setup/hot-loop world-age discipline (the net-win condition above).
- **Two-language build tax** for a solo research build (two toolchains, CI, cognitive
  load). *Mitigation:* the seam is narrow and the offline DSLs add nothing at runtime;
  accepted as the price of best-per-section fit, with single-host as the escape valve.
- **Haskell iteration velocity** at the `DataKinds`/operad frontier (cryptic type errors,
  lazy-eval space discipline). *Mitigation:* keep the type-level encoding only where it
  buys real soundness (the operad, handles, serialization); OCaml is the fallback host if
  the tax proves too high.
- **The operad's compile-time soundness is Haskell-specific** — it does not survive a host
  swap to OCaml/Julia (drops to smart-constructor checks). A reason the host choice is
  load-bearing, not cosmetic.

## Build-cost (order-of-magnitude)

The live system (Haskell compiler + substrate + Julia runtime) ≈ 26–34 person-months for
the full spec; the **most likely cost blow-up** is Stage-3 sparsity inference + the
`SymbolicTensorOps` operad typechecker (the open-ended, algorithmically subtle pieces),
not the commodity wiring (`hegg`, `GHC.Generics`, BLAS/LAPACK via Julia stdlib). GAP and
Lean are bounded offline efforts. The MVP diamond slice exercises a small fraction of this.

## Sources

Per-axis dossiers under `/tmp/impl-lang-research/` (`a1`–`a4`, `b1`–`b2`). Key external:
`hegg` (Hackage), `egg`/`egglog` (egraphs-good, the e-graph reference), `OxiDD` (TACAS'24),
GHC `DataKinds`/type-families (first-order) roadmap, `ego` (verse-lab, stale 2021),
`ppx_deriving` / OCaml 5.3 (multicore, Jane Street), Scala 3 match-type SIP-56 + 2024
soundness bugs, JAX custom-derivatives JEPs (`custom_vjp` limits), Julia `GPUCompiler` /
`KernelAbstractions` / `eval(Meta.parse)` / `@generated`, OSCAR/GAP.jl + GAP CTblLib,
Lean 4 → C (4.22/4.23 codegen), ModelingToolkit.jl releases/FAQ (churn + undocumented
internals), batched-BLAS small-block launch overhead, TT-cross (sequential build-once),
Ewald/PME GPU 10–100×.

---

## Changelog

- **2026-07-16 (strata rewrite):** status header note added; no other changes.
- **2026-06 (decision closed):** the recommendation here was adopted (commit ec52314-era) —
  polyglot Haskell / Julia / GAP / Lean 4, joined at the Stage-4→Stage-5 codegen seam. Recorded
  in arch-18 "Closed decisions"; this file remains the research record behind it.

# Learnable_Structure × `/physics` — the seam contract

> Hand-written cross-workstream contract, dated **2026-07-16**. Not part of the
> lint-enforced atomic tree; the atomic tree (`the canon chapters*`,
> `the canon chapters*`) is canonical for every shape, convention, and count
> cited here. Scope: the **minimum observable behavior `/physics` requires of
> `Learnable_Structure` at their shared boundary** — and nothing about its
> interior.

`Learnable_Structure` is the operator-side kernel that compiles arbitrary
learnable structures; the PINO is built on it. `/physics` is a
substrate-agnostic reference oracle (`arch-02-libraries`): it defines what a
state *is* and scores law violation; it never trains, steps, or holds state
values. The only surface a downstream consumer sees is the pino-bridge
(`arch-16-pino-bridge`) — states and cotangents in, keyed floats out. So the
coupling between the two modules is confined to what crosses that seam, and
this document is the complete list of demands. Everything else about
`Learnable_Structure` is its own business.

The contract is loop-agnostic by the two-loop symmetry: in **training**, the
external loop pushes the oracle's cotangents into weights; in **design**, into
the candidate itself. Same seam, same requirements — only the gradient sink
differs.

## 1. Required

**R1 — State emission in the oracle's type.** Emitted candidates must be the
7-slot state tuple exactly as `arch-04-state` defines it — slot set, per-slot
array shapes and layouts, units, and the gauge conventions recorded there
(state slots are addressed by the `StateComponent` universe ordinals of
`arch-20-representations §20.3`, not by ad-hoc names). **Structural**
well-formedness is mandatory at the seam: correct shapes, finite IEEE-754
float64 (internal training precisions are `Learnable_Structure`'s business;
convert before the boundary). **Physical** admissibility is *not* required:
admissibility is scored, never presupposed (the admissibility categories of
`arch-11-residuals §11.1`; the score-not-solve principle of
`arch-01-purpose`). Emitting a structurally-valid but physically-poor state is
normal operation — that is what the residual surface is for.

**R2 — Evaluate-at-points.** The compiled oracle kernel for an instance
carries instance-specific, symmetry-quotiented axis grids fixed at compose
time (`arch-07-pipeline §7.2`). Given per-channel lists of query coordinates,
`Learnable_Structure` must return that channel's values **at exactly those
points**. Emission on a fixed internal mesh with caller-side interpolation
does not satisfy this. This is discretization-invariance made concrete and is
the single most load-bearing requirement for the hybridization — how the
kernel realizes it internally (spectral trunk, point branch, anything else) is
unconstrained; only the query behavior is contracted.

**R3 — VJP at the state boundary.** Accept a cotangent structured like the
emitted state and backpropagate it to internal parameters. The oracle returns
*per-key* cotangents (`arch-16-pino-bridge §16.1`, `cograds`); the external
loop linearly combines them into **one** state-shaped cotangent before handing
it over — so a single VJP application per (state, combined-cotangent) pair
must be supported; per-key VJP is not required.

**R4 — Conditioning inputs.** Accept the `Environment` record (and query
time) as named, typed conditioning channels (`arch-03-inputs`). Emitted state
is conditioned on environment; the environment is an input the kernel never
invents or mutates.

**R5 — Seam purity + determinism.** Only flat numeric arrays cross the
boundary — no framework tensors with attached tapes, no lazy graphs, no
callbacks. Inference-mode emission must be deterministic (bitwise, for fixed
inputs and identity) so content-addressed caching holds; hashing applies the
float normalization of `arch-20-representations §20.4` (canonical quiet-NaN,
`−0.0 → +0.0`) — and a NaN/Inf in an emitted state is already a violation of
R1's finiteness upstream of any hash.

**R6 — Batch axis.** Emission and VJP intake carry a leading batch dimension;
batch elements are independent (no cross-batch coupling observable at the
seam).

**R7 — Content-addressable identity.** Every `Learnable_Structure` instance
(architecture + weights + version) exposes one stable content hash, aligned
with the `arch-20-representations` addressing discipline, so any residual map
is permanently attributable to the pair *(oracle-kernel hash × operator
hash)*. Retraining or structural edit ⇒ new hash.

**R8 — Loop-drivability.** `Learnable_Structure` never owns the loop. Emit
and VJP are plain calls an external driver interleaves with `Validate` at its
own cadence; loop logic — batching policy, curricula, active learning, design
search — lives in `/interface` (`arch-01-purpose`). No control inversion, no
required callbacks.

## 2. Optional offers (non-blocking; decide later)

**O1 — Structure-plan intake.** The oracle's Stage-2 sidecar carries
per-instance symmetry structure — irrep blocks, orbit maps, per-channel group
actions (`arch-07-pipeline §7.2`). If `Learnable_Structure` can consume a
compile-time descriptor of that shape to bake weight-sharing/equivariance into
a compiled structure, the corresponding equivariance residuals go to ~0 by
construction. An offer, not an ask: the oracle scores equivariance regardless.

**O2 — Tiered cadence.** The state's tiers evolve at heterogeneous rates
(`arch-21-multiscale-state`). If the kernel supports per-slot update cadences
in a compiled structure, a future multi-rate driver can exploit it. Purely
informational; nothing currently depends on it.

## 3. What `/physics` does not care about

- Internal architecture: layer types, trunk/branch decomposition, how
  hybridization is realized.
- Training dtypes, mixed precision, sharding, internal memory layout.
- Optimizer, schedules, initialization, regularization.
- `Learnable_Structure`'s own compilation story — how structures are declared,
  lowered, fused, or cached internally.
- Where weights live or how checkpoints are stored (only the R7 hash is
  visible).
- Anything about the loop (R8 is the whole statement).

If a future need falls outside this list, it enters by amending this contract
— never by reaching through the seam.

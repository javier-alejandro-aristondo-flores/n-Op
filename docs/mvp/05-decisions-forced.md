---
id: mvp-05-decisions-forced
title: Decisions this slice forces
status: draft
revision: 1
canonical-for:
  - MVP-forced decisions
depends-on: []
referenced-by: []
research-sources: []
---
# Decisions this slice forces

- **Implementation language (H1) — resolved.** The concrete needs (reverse-mode
  AD through implicit-diff adjoints for BTE-RTA / SCF / G₀W₀, staged symbolic IR
  with Stage-4 codegen, IBZ tooling, optional GPU for k-point meshes) are met by a
  **polyglot of DSLs** (`arch-18-open-decisions`, Closed decisions;
  `physics/research/implementation-language.md`): a **Haskell** compiler-host for
  Stages 1–4 + the substrate, emitting a **Julia** Stage-5 runtime (which owns the
  optional GPU codegen), with **GAP** (group-theory tables) and **Lean 4** (spec
  proofs) offline.
- **TB-3NN-sp³d⁵ for carbon as warm-start initializer.** Used as a seed for
  the SCF inner loop only; not a separately-evaluated formula and not an
  independent residual.
- **Layer-1.25 substrate data (H7).** The closed-form discipline needs L1 to
  expose more than `γ̂`: G₀W₀ needs ~30–50 **unoccupied bands + wavefunctions**;
  QHA needs **volume-dependent (Grüneisen) phonons**. These are the L1 outputs
  the MVP requires — specify them when building `state/level-1`.
- **Reference-battery seed (H4).** Seed `physics/library/cert/reference-data/`
  with the ~10 diamond rows the MVP validates against: lattice a, indirect gap,
  C₁₁/C₁₂/C₄₄, Debye T, κ(300 K), **κ(773 K) ≈ 620 W/m·K** (the high-T 4-phonon
  anchor), max phonon energy, cohesive/formation energy, and the diamond–graphite
  boundary point.
- **Design-grade accuracy targets (H8).** The MVP's headline outputs must meet
  declared accuracy: gap ±0.15 eV post-G₀W₀, C_ij ±5%, κ(300 K) ±20%, E_form
  ±0.2 eV, μ factor-2 (full per-observable ledger in `docs/accuracy-ledger.md`,
  wired via `arch-11-residuals §11.7`). Cert obligation 4 checks them at the
  battery anchors; the high-T anchors κ(773 K)/κ(1100 K) are **landed** (registry
  rows 121–122, the 4-phonon correction + iterative-LBTE sibling; curated κ(T)
  battery in `docs/accuracy-ledger.md`).

---

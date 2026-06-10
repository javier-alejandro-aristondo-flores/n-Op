---
id: arch-17-out-of-scope
title: Out of scope
status: draft
revision: 1
canonical-for:
  - scope exclusions
depends-on: []
referenced-by: []
research-sources: []
---
# Out of scope

Stated and held, so the architecture is honest about what it does not cover:

- Strongly-correlated systems (frustrated Wigner crystals, spin liquids, Mott
  physics) — `γ̂` is mean-field by construction; UWBG materials are large-gap and
  far from Mott physics.
- Flexoelectricity in centrosymmetric materials — below the numerical-noise
  floor; order-of-magnitude only.
- Magneto-thermal coupling in heavy contact metals — formally in `S`, not
  modeled.
- Deep-defect non-Markovian dynamics — Markov master-equation closure assumed.
- Polaron localization beyond Fröhlich.
- 4-phonon scattering, full NEGF tunneling, full SCPH/SSCHA — deferred to
  Layer-1.75 V2 scaffolding. Where a cheap proxy is needed during training it is a
  registered D4 surrogate with an obligation-9 validity domain; **no such surrogate
  ships in V1** (the closed-form / Layer-1.25 path is used, with the accuracy regime
  declared in the ledger, `arch-11-residuals §11.7`).
- Absolute Berry-phase / Wannier-center polarization (the λ-path `P_sp` evaluator) —
  deferred to V2. V1 uses the Z*-composition path (`arch-19`/registry rows 113–114, ±5%,
  `accuracy-ledger` #35); the absolute modern-theory integral needs a
  `berry-phase-polarization` sub-stage not in the closed 12-method alphabet, analogous to
  the G₀W₀ gap upgrade over PBE.
- Plasma-process surface damage; grain-boundary statistics; continuum creep /
  dislocation climb; quantum-tunneling-corrected reaction rates (classical
  Eyring TST adequate at T_op ≥ 600 K).
- True renormalization-group flow; inverse design / minimal-model search (would
  live in `/informed-operator` as a PINO head, not a `/physics` primitive);
  fragile topology.

`predict` raises `out-of-scope` with a witness for any of these; cert
obligation-3 flags suspect cases.

---

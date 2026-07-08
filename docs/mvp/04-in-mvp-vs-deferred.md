---
id: mvp-04-in-mvp-vs-deferred
title: In-MVP vs deferred
status: draft
revision: 1
canonical-for:
  - MVP scope
depends-on: []
referenced-by: []
research-sources: []
---
# In-MVP vs deferred

**In the MVP**
- ~35 named formulas (the rows above) of the 132.
- 9 of the 12 methods (all but `path-search`, `convex-optimization` beyond the
  hull check, `statistical-sampling`, `microkinetic-steady-state` — chemical/MC
  machinery not on the diamond path).
- ~9 templates of the 20.
- Bundles B1, B2, B3, B7, B10 (+ B5 surface, B9 self-heating for two formulas) and
  the structural/thermo scalars — 5–7 of the 11.
- Residual families exercised: micro EOM-violation, Conservation, Positivity,
  Algebraic-identities, Static-snapshot, Static-thermodynamic. `Degeneracy` is
  cert-only (`arch-05`, `arch-11 §11.1`); the slow/macro EOM siblings
  (`EOM/DefectPopulation`, `EOM/Continuum`) defer with their tiers.
- Cert obligations 1–6 **and 10** of 10 — the registration adjoint gate (10) stays
  in the MVP (D2 gradients must be validated when the PINO first trains); only the
  battery/topology obligations 7–9 defer.
- Layers 1 + 1.25 (G₀W₀, QHA, DFPT) wired.

**Deferred (the other ~⅔ of the spec)**
- The remaining ~90 formulas: the defect zoo beyond row 30, surface chemistry,
  interface/Schottky physics (no metal contact in the pure-diamond MVP), high-
  field / hot-carrier / breakdown, degradation, most of the topology atlas (rows
  96–102) beyond basic symmetry classification.
- Cert obligations 7–9 (bulk-boundary, versioned battery, surrogate-net). The
  registration adjoint gate (10) is **not** deferred — see above.
- Layer 1.75 (iterative dressing), SCPH/SSCHA, the D4 surrogate nets, the non-
  diamond materials, heterostructures beyond the single c-BN lattice-match.

The buildable unit is roughly one-third of the full vocabulary.

---

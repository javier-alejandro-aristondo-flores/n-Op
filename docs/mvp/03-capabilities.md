---
id: mvp-03-capabilities
title: The three capability slices
status: draft
revision: 1
canonical-for:
  - MVP capabilities
depends-on:
  - arch-08-bo-levels
  - arch-09-vocabularies
  - arch-11-residuals
  - arch-12-cert
  - mvp-05-decisions-forced
referenced-by: []
research-sources: []
---
# The three capability slices

Each capability is a strict selection from the closed vocabularies of
`arch-09-vocabularies` (methods, templates, formulas, bundles), the residual
categories of `arch-11-residuals`, and the cert obligations of `arch-12-cert`.
Formula numbers reference `physics/library/formulas/registry-manifest.csv`.

### Cap 1 — Crystal-structure prediction

*Construct a symmetry-allowed candidate, relax to the E_BO minimum, certify
stability; one heterostructure check (c-BN on diamond) via lattice matching.*

| Facet | MVP content |
|---|---|
| State used | `h`, `R_I`, `Z_I`; `γ̂` (T=0, for `E_BO`) |
| BO levels | L1 (`E_BO = min_γ̂ E`) → L2 (relaxation on (R, h)) |
| Methods | variational-minimization · functional-differentiation · algebraic-combination · symmetry-projection · spectral-decomposition · convex-optimization (hull check only) |
| Templates | `SymmetryAdaptedHamiltonianOf` · `SecondDerivativeOf` · `ClassifyOf` · `StateReadoutOf` · `AlgebraicOf` |
| Formulas | **57** born-stability-criteria · **60** elastic-constants-Cij · **61** bulk-modulus · **62** sound-velocity-isotropic · **85** structure-uniqueness-CSP · **30** defect-formation-energy-zhang-northrup · **44** surface-grand-potential-γ (B5) · **52** vegard-correction · **54** matthews-blakeslee-critical-thickness (c-BN/diamond hetero) · **67** phase-diagram-convex-hull · **124** tp-aware-hull (δ_meta metastability band — metastable diamond reads R_hull = 0) |
| Bundles | B10 static-validity · B7 mechanics · B4 defect (row 30) · B6 interface (rows 52/54; row 54 also B11) · (B5 surface for row 44) · B8 thermodynamics (rows 67/124, the diamond–graphite hull) |
| Residuals | static-validity (Born stability, dynamical stability, space-group equivariance) · structural EOM (`∇_R E_BO = 0`, stress matches) · thermodynamic-consistency (diamond–graphite hull, rows 67/124) |
| Cert | 1 symmetry · 2 bounds · 3 analytic limits · 5 conservation |
| Implementation | DFT `E_BO` + DFPT-stress `C_ij`; TB 3NN sp³d⁵ as SCF warm-start initializer (`mvp-05-decisions-forced`) |

**Acceptance test (first end-to-end gate).** *Null:* grading a ground-truth, relaxed
pure-diamond state returns every residual slot ≈ 0 within σ — the oracle certifies a lawful
structure as lawful. *Sensitivity:* perturbing the state (an atomic displacement, a cell
distortion off the `E_BO` minimum, or a wrong lattice constant) returns a non-zero residual
**and the specific keys that fire name the violated law** — `∇_R E_BO = 0` for a broken
relaxation, space-group equivariance for a broken symmetry, Born stability for an over-stretch.
Because residuals are keyed and never aggregated, "the right law fired" is directly checkable.
*Data-backed sensitivity:* perturbing along the diamond strain-hypersurface reference dataset,
the residual tracks the reference energy rise off the minimum — a quantitative match, not only a
sign check.

### Cap 2 — Electron-cloud (carrier) diffusion

*Electronic-structure substrate + carrier transport through the lattice.*

| Facet | MVP content |
|---|---|
| State used | `γ̂`, `A`; emergent carrier distribution `f_n(k,r)` |
| BO levels | L1 (bands from `γ̂`) + L4 (carrier transport) |
| Methods | spectral-decomposition · linear-response · kinetic-evolution · state-readout |
| Templates | `SpectrumOf` · `ResponseOfTo` · `KineticEvolutionOf` · `StateReadoutOf` · `AlgebraicOf` |
| Formulas | **1** bandgap-direct · **2** bandgap-indirect · **3** effective-mass-tensor · **4** DOS-tetrahedron · **5** fermi-level-charge-neutral · **6** quasi-particle-shift-G0W0-surrogate · **14** drude-conductivity · **15** matthiessen-mobility · **16** caughey-thomas-mobility · **18** v-sat-intervalley · **19** hall-mobility-from-σ · **20** mobility-impurity-phonon · **24** wiedemann-franz-electronic-kappa |
| Excluded (non-polar) | **17** v-sat-POP-limit · **21** frohlich-coupling · **22** frohlich-scattering-rate — masked off by the `is-polar-material` applicability classifier (false for diamond) |
| Bundles | B1 electronic-structure · B3 transport |
| Residuals | EOM (Liouville on `γ̂`; carrier streaming) · conservation (charge continuity `∂ρ/∂t + ∇·j = 0`) · positivity (`ρ ≥ 0`, `f ∈ [0,1]`) · algebraic (Einstein `D = μ k_B T / q`) |
| Cert | 1 symmetry · 2 bounds · 5 conservation · 6 named-formula consistency (BTE-σ ≡ Kubo-σ) |
| Implementation | DFT+G₀W₀ bands + BTE-RTA; TB 3NN bands as SCF warm-start initializer |

### Cap 3 — Heat diffusion

*Phonon spectrum + phonon-mediated thermal transport through the lattice.*

| Facet | MVP content |
|---|---|
| State used | `R_I`, `P_I`; emergent phonon distribution `n_{qs}`, `T_L` |
| BO levels | L2 (`E_BO` Hessian → phonons) + L3 (Bose statistics) + L4 (phonon BTE) |
| Methods | spectral-decomposition · spectral-aggregation · kinetic-evolution |
| Templates | `HarmonicStiffnessHessianOf` · `SpectrumOf` · `SpectralAggregateOf` (heat capacity, aggregator = `bose-einstein-cv`) · `KineticEvolutionOf` |
| Formulas | **7** acoustic-sum-rule · **8** dynamical-matrix-hermiticity · **9** phonon-dispersion · **10** phonon-DOS · **11** phonon-group-velocity · **12** grueneisen-mode (QHA / thermal expansion) · **25** callaway-lattice-kappa · **121/122** high-T κ siblings of row 25 (4-phonon factor + dormant iterative-LBTE consistency pair) · **70** self-heating-T_op (B9; cheap closure) |
| Deferred | **13** SCPH (QHA suffices ≤800 °C) · **26** phonon-poiseuille-length · **27** second-sound-speed (low-T hydrodynamics, out of harsh-env scope) |
| Bundles | B2 phonon · B3 transport · (B9 self-heating for row 70) |
| Residuals | EOM (phonon streaming + collision; heat equation `∂_t T = ∇·(κ∇T)`) · conservation (energy) · positivity (`ω² ≥ 0`) · algebraic (acoustic sum rule `Σ_J Σ_R Φ(R) = 0`) |
| Cert | 2 bounds · 3 analytic limits (harmonic-crystal, Dulong–Petit) · 5 conservation |
| Implementation | DFPT phonons + 3-phonon BTE-RTA; QHA + Callaway κ available as a closed-form sibling formula whose method-equivalence with the DFPT/BTE path is asserted under cert obligation-6 |

---

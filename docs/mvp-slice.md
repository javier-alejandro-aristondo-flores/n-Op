<!-- GENERATED FILE — do not edit. Source files under docs/{architecture,implementation,mvp}/. Regenerate with `python docs/meta/assemble.py`. -->

# n-Op Diamond MVP Slice

## Contents

- [The system](#mvp-01-system)
- [γ̂ budget at MVP scale](#mvp-02-gamma-budget)
- [The three capability slices](#mvp-03-capabilities)
- [In-MVP vs deferred](#mvp-04-in-mvp-vs-deferred)
- [Decisions this slice forces](#mvp-05-decisions-forced)
- [MVP build order](#mvp-06-build-order)


<a id="mvp-01-system"></a>

# The system

**Diamond, primitive cell.** Space group Fd-3m (No. 227); 2 carbon atoms at the
8a Wyckoff site; sp³; lattice constant a = 3.567 Å. Eight valence electrons
(2s²2p² × 2) → **4 occupied bands**.

| Anchor | Value | Consequence for the MVP |
|---|---|---|
| Indirect gap | 5.47 eV (X-point) | PBE gives ~4.2 eV (−23%); **G₀W₀ or hybrid required** (registry row 6) |
| Max phonon energy | ~165 meV (~1332 cm⁻¹) | highest of any solid; phonon grid must resolve it |
| Debye temperature | ~2200 K | **QHA valid through ~800 °C** → SCPH (row 13) deferred |
| Thermal conductivity | ~2000 W·m⁻¹K⁻¹ | the headline Cap-3 target |
| Elastic constants | C₁₁≈1079, C₁₂≈124, C₄₄≈578 GPa | Cap-1 stability + sound velocity |
| Polarity | **non-polar (homopolar)** | Z\*=0 by symmetry → **no LO-TO, no Fröhlich** → registry rows 17, 21, 22 excluded by applicability |
| High-T failure | sp³→sp² (graphitization) above ~700 °C in vacuum | the diamond–graphite phase boundary is the Cap-1 thermodynamic check |

**Units.** Atomic units internally; report eV, Å, W·m⁻¹K⁻¹, cm²V⁻¹s⁻¹.

---


<a id="mvp-02-gamma-budget"></a>

# γ̂ budget at MVP scale

The dense one-body density matrix is `O(N_r²)` and was flagged as a feasibility
risk. At MVP scale it is a non-issue, because γ̂ is **never densified**:

- **Encoding:** `(Reciprocal, BlockDiag)` — one block per k-point — with each block
  stored as **orbitals** (low-rank in the band index: `N_PW × N_b`), not as a
  dense `N_PW × N_PW` matrix.
- **Sizing (primitive cell, G₀W₀-capable basis):** PW cutoff ~400 eV ⇒ `N_PW ≈ 1000`;
  `N_b ≈ 40` (4 occupied + unoccupied manifold for G₀W₀); 8×8×8 Monkhorst–Pack ⇒
  **~29 irreducible k-points**. Orbital storage ≈ `N_PW × N_b × 16 B × N_k`
  ≈ 1000 × 40 × 16 × 29 ≈ **~18 MB**. (Densifying would cost `N_PW² × 16 × N_k`
  ≈ 460 MB per the same mesh — which is exactly why we never do it.)
- **Warm-start initializer:** tight-binding **3NN sp³d⁵** for carbon ⇒ a `~18 × 18` Hamiltonian
  per k — kilobytes. Used to seed the SCF inner loop (`mvp-05-decisions-forced`);
  not a separate residual path.
- **Beyond the MVP:** defect/interface supercells grow `N_PW` linearly; orbital
  storage stays ≈ linear in `N_atoms × N_b`. The dense-γ̂ concern returns only if
  a large supercell is densified — which the encoding forbids. A supercell memory
  budget is the first thing to revisit when leaving the primitive cell.

---


<a id="mvp-03-capabilities"></a>

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
| Methods | variational-minimization · functional-differentiation · classify-of · symmetry-projection · spectral-decomposition |
| Templates | `SymmetryAdaptedHamiltonianOf` · `SecondDerivativeOf` · `ClassifyOf` · `StateReadoutOf` · `AlgebraicOf` |
| Formulas | **57** born-stability-criteria · **60** elastic-constants-Cij · **61** bulk-modulus · **62** sound-velocity-isotropic · **85** structure-uniqueness-CSP · **30** defect-formation-energy-zhang-northrup · **44** surface-grand-potential-γ (B5) · **52** vegard-correction · **54** matthews-blakeslee-critical-thickness (c-BN/diamond hetero) |
| Bundles | B10 static-validity · B7 mechanics · (B5 surface for row 44) · structural scalars |
| Residuals | static-validity (Born stability, dynamical stability, space-group equivariance) · structural EOM (`∇_R E_BO = 0`, stress matches) · thermodynamic-consistency (diamond–graphite hull) |
| Cert | 1 symmetry · 2 bounds · 3 analytic limits · 5 conservation |
| Implementation | DFT `E_BO` + DFPT-stress `C_ij`; TB 3NN sp³d⁵ as SCF warm-start initializer (`mvp-05-decisions-forced`) |

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
| Formulas | **7** acoustic-sum-rule · **8** dynamical-matrix-hermiticity · **9** phonon-dispersion · **10** phonon-DOS · **11** phonon-group-velocity · **12** grueneisen-mode (QHA / thermal expansion) · **25** callaway-lattice-kappa · **70** self-heating-T_op (B9; cheap closure) |
| Deferred | **13** SCPH (QHA suffices ≤800 °C) · **26** phonon-poiseuille-length · **27** second-sound-speed (low-T hydrodynamics, out of harsh-env scope) |
| Bundles | B2 phonon · B3 transport · (B9 self-heating for row 70) |
| Residuals | EOM (phonon streaming + collision; heat equation `∂_t T = ∇·(κ∇T)`) · conservation (energy) · positivity (`ω² ≥ 0`) · algebraic (acoustic sum rule `Σ_J Σ_R Φ(R) = 0`) |
| Cert | 2 bounds · 3 analytic limits (harmonic-crystal, Dulong–Petit) · 5 conservation |
| Implementation | DFPT phonons + 3-phonon BTE-RTA; QHA + Callaway κ available as a closed-form sibling formula whose method-equivalence with the DFPT/BTE path is asserted under cert obligation-6 |

---


<a id="mvp-04-in-mvp-vs-deferred"></a>

# In-MVP vs deferred

**In the MVP**
- ~35 named formulas (the rows above) of the 102.
- 9 of the 12 methods (all but `path-search`, `convex-optimization` beyond the
  hull check, `statistical-sampling`, `microkinetic-steady-state` — chemical/MC
  machinery not on the diamond path).
- ~9 templates of the 20.
- Bundles B1, B2, B3, B7, B10 (+ B5 surface, B9 self-heating for two formulas) and
  the structural/thermo scalars — 5–7 of the 11.
- Residual categories: EOM-violation, conservation, positivity, algebraic
  identities, static-validity, thermodynamic-consistency (6 of 7; degeneracy
  enters with full GENERIC dynamics).
- Cert obligations 1–6 of 10.
- Layers 1 + 1.25 (G₀W₀, QHA, DFPT) wired.

**Deferred (the other ~⅔ of the spec)**
- The remaining ~62 formulas: the defect zoo beyond row 30, surface chemistry,
  interface/Schottky physics (no metal contact in the pure-diamond MVP), high-
  field / hot-carrier / breakdown, degradation, most of the topology atlas (rows
  96–102) beyond basic symmetry classification.
- Cert obligations 7–10 (bulk-boundary, versioned battery, surrogate-net,
  registration adjoint gate as a hard build gate).
- Layer 1.75 (iterative dressing), SCPH/SSCHA, the D4 surrogate nets, the non-
  diamond materials, heterostructures beyond the single c-BN lattice-match.

The buildable unit is roughly one-third of the full vocabulary.

---


<a id="mvp-05-decisions-forced"></a>

# Decisions this slice forces

- **Implementation language (H1).** Now decidable against concrete needs:
  reverse-mode AD through implicit-diff adjoints (BTE-RTA, SCF, G₀W₀), staged
  symbolic IR with Stage-4 codegen, IBZ tooling, and GPU support for k-point
  meshes. Candidates per `arch-18-open-decisions §1`: Julia (Symbolics +
  ModelingToolkit + Enzyme), Python + JAX (jit + JAXopt), or a custom MLIR
  stack.
- **TB-3NN-sp³d⁵ for carbon as warm-start initializer.** Used as a seed for
  the SCF inner loop only; not a separately-evaluated formula and not an
  independent residual.
- **Layer-1.25 substrate data (H7).** The closed-form discipline needs L1 to
  expose more than `γ̂`: G₀W₀ needs ~30–50 **unoccupied bands + wavefunctions**;
  QHA needs **volume-dependent (Grüneisen) phonons**. These are the L1 outputs
  the MVP requires — specify them when building `state/level-1`.
- **Reference-battery seed (H4).** Seed `physics/library/cert/reference-data/`
  with the ~10 diamond rows the MVP validates against: lattice a, indirect gap,
  C₁₁/C₁₂/C₄₄, Debye T, κ(300 K), max phonon energy, cohesive/formation energy,
  and the diamond–graphite boundary point.

---


<a id="mvp-06-build-order"></a>

# MVP build order

A focused subset of the phases in `impl-10-build-sequence`:

1. `core` — autodiff, tensor algebra, mesh integration (k-mesh, tetrahedron).
2. `shared` — Ewald; the tight-binding (3NN sp³d⁵) carbon Hamiltonian builder.
3. `inputs` — the diamond `PeriodicityStructure` + `SiteDecoration` + `Environment`.
4. `state` — `γ̂` as k-blocked orbitals (§2); `(R, P, h)`.
5. methods (the 9) and formulas (the ~35) of §3.
6. canonicals — `E_BO` (DFT, with TB 3NN sp³d⁵ as SCF warm-start) and the phonon Hessian.
7. the three capability residuals (Cap 1/2/3 rows above).
8. cert obligations 1–6 + the 10-row diamond reference battery.
9. validate: relaxed lattice, gap (with G₀W₀), C_ij, phonon max, κ(300 K) against
   the battery.

Completing this slice yields a diamond-only `/physics` that can emit a granular
residual vector with cotangents, expose observable values, and certify them for
all three capabilities — the concrete substrate `/informed-operator` then trains
against.

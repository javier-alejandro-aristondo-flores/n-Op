# Per-observable accuracy ledger

The per-observable **accuracy regime** — the target tolerance each closed-form / one-shot
path must meet, and the cheap-vs-faithful note. Restored from
`physics/research/uwbg-observable-catalog.md §C` (the catalog's "Accuracy regime" column,
dropped in the original CSV transcription). This is the **error-model seed**: each value is a
declared characteristic scale that `arch-10-typeclasses Quantity.combineTol` composes into a
per-residual error budget (`arch-11-residuals §11.7`). It is a *reference table*, not part of
the lint-enforced atomic tree; the canonical per-formula `Bundle`/`Tier`/`Diff` live in
`physics/library/formulas/registry-manifest.csv`.

"Design-grade" means **device-design-adequate at the UWBG operating point (>500 °C, high
field)** — not ab-initio-converged. Where the closed-form path cannot meet design-grade, the
gap is named (and tracked in the audit's P2 list).

## The 52 observables (+ 16 FoMs)

| # | Observable | Accuracy regime | Cheap vs faithful |
|---|---|---|---|
| 1 | bandgap_direct | ±0.1 eV (±0.05 near alloy band crossings) | hybrid-DFT / G₀W₀ required; AHC adds the −0.3…−0.6 meV/K T-shift |
| 2 | band_structure E_n(k) | RMS 50 meV within 2 eV of edges | TB-3NN-sp³d⁵ or Wannier interpolation (cheap) |
| 3 | effective_mass_tensor | ±10% (transport-relevant) | parabolic / k·p; non-parabolicity grows with T |
| 4 | density_of_states g(E) | ±5% within ±k_BT of E_F | tetrahedron / Gaussian σ=50 meV |
| 5 | fermi_level E_F(T,n_d) | ±5 meV | charge-neutrality bisection |
| 6 | DOS_at_E_F | ±5% | readout of #4 |
| 7 | band_offset ΔE_C, ΔE_V | ±0.1 eV | Anderson/Tersoff cheap; GW supercell faithful |
| 8 | electron_affinity χ | ±0.1 eV | H-desorption >700 °C shifts χ >1 eV |
| 9 | phonon_dispersion ω_λ(q) | ±2% acoustic, ±5% optical | anharmonic Δω ~1–2% at 1500 K |
| 10 | phonon_DOS F(ω) | ±5% | derived from #9 |
| 11 | mode_gruneisen γ_λ(q) | ±15% | single γ_avg acceptable cheap |
| 12 | phonon_lifetimes τ_λ(q,T) | ±20% (gives κ ±10%) | **4-phonon needed >1000 K** |
| 13 | thermal_conductivity κ(T) | ±10% (diamond), ±20% (III-N) | **RTA/3-ph underestimates 30–50% near 300 K** |
| 14 | thermal_expansion α_αβ(T) | ±10% | QHA breaks above ~Θ_D/2 (GaN fails at 500 °C) |
| 15 | e-ph self-energy Σ_ep (AHC) | ±20% on T-shift of gap | **dominant gap renorm >1000 K — absent from MVP** |
| 16 | carrier_mobility_electron μ_n | ±20% @300 K, ±30% @800 K | BTE-RTA |
| 17 | carrier_mobility_hole μ_p | ±20% (critical, p-type diamond) | as #16 |
| 18 | saturation_velocity v_sat | ±15% | Shockley / Caughey–Thomas |
| 19 | impact_ionization α_ii | **factor-2** | Chynoweth fit; misses hot-electron tail |
| 20 | breakdown_field E_b | ±15% (critical, BFOM) | via gap renorm; drops ~20% 300→800 K |
| 21 | hall_factor r_H | ±10% | constant r_H≈1.18 acceptable |
| 22 | seebeck S | ±15% | Mott formula |
| 23 | dielectric_constant_static ε_r | ±5% | LST from phonons |
| 24 | dielectric_function ε(ω) | ±10% | RPA / BSE |
| 25 | defect_formation_energy E_f | ±0.2 eV (controls [defect]) | FNV/Kumagai mandatory |
| 26 | defect_ionization_energy E_a | ±50 meV | hydrogenic / empirical |
| 27 | dopant_solubility c_sol | ±factor-2 | Arrhenius |
| 28 | defect_level_in_gap E_t | ±0.1 eV | trap-assisted leakage |
| 29 | capture_cross_section σ_n,p | factor-3 | **OUTSIDE registry** (Huang–Rhys+Marcus) |
| 30 | surface_dipole p_s | ±0.1 D | tabulated by termination |
| 31 | schottky_barrier φ_B | ±0.1 eV (→ ×e⁴ contact R @500 °C) | Cowley–Sze; carbide shifts with soak |
| 32 | contact_resistivity ρ_c | ±50% (orders span) | dominated by φ_B |
| 33 | interface_trap_density D_it | factor-2 | dangling-bond + strain |
| 34 | tunneling_transmission T_WKB | ±20% in log | Fowler–Nordheim closed form |
| 35 | spontaneous + piezo polarization P_sp/P_pz | ±5% | landed: Z*-composition (rows 113–114); absolute Berry-phase λ-path deferred V2 |
| 36 | elastic_tensor C_ijkl | ±5% | DFT stress-strain / DFPT |
| 37 | bulk/shear modulus B,G | ±5% | Voigt average |
| 38 | sound_velocity v_s | ±5% | Christoffel |
| 39 | cohesive/surface energy γ_s | ±0.1 J/m² | slab DFT |
| 40 | fracture_toughness K_IC | ±20% (statistical) | Griffith+Young |
| 41 | resonant_modes ω_n | ±10% | **device-scale (continuum elastic)** |
| 42 | displacement_threshold E_d | ±5 eV | tabulated (~37 eV C, ~25 eV Ga) |
| 43 | gibbs_free_energy G | ±10 meV/atom | QHA: E_DFT+F_vib+PV |
| 44 | phase_boundary | ±5% in P–T | ΔG crossing |
| 45 | specific_heat c_v,c_p | ±3% | Debye cheap |
| 46 | oxidation_rate r_ox | **factor-3** | Eyring; diamond air-ox >600 °C the lifetime limiter |
| 47 | hydrogen_desorption r_H | **factor-2** | Eyring E_des≈3.8 eV; drives χ shift |
| 48 | self_heating T_op | ±10 K | **device-scale continuum heat eq** |
| 49 | hot_carrier_distribution f(E,F) | shape ±20%; high-E tail decisive | **OUTSIDE registry** (full-band MC) |
| 50 | electromigration E_a^EM | ±0.1 eV | NEB interface hop |
| 51 | defect_evolution dN/dt | **factor-2** | master-equation / kMC (slow tier, `arch-21`) |
| 52 | 2DEG_sheet_density n_s | ±10% | landed: Ambacher composition (row 115) from rows 113/114/116 |

(The **16 FoMs** — BFOM, JFOM, combined breakdown/mobility/thermal figures — are algebraic
compositions of the above and inherit their composed `combineTol` budget.)

## MVP design-grade targets (the headline outputs the closed-form bet must meet)

| Observable | Design-grade target | Status |
|---|---|---|
| bandgap (300 K) | **±0.15 eV** post-G₀W₀ | met (registry row 6) |
| C_ij (300 K) | **±5%** | met (row 36) |
| κ(300 K) | **±20%** (RTA/3-ph; documented) | limited — 4-ph caveat |
| κ(800 K) | **±35%** until 4-ph lands | deferred (P1.5) |
| E_form (300 K) | **±0.2 eV** | met (rows 30 + FNV 31–33) |
| μ (300 K) | **factor-2** | met with caveats |

The reference battery (cert obligation 4, `arch-12 §12.1`) checks these at the MVP anchors;
**high-T anchors (κ(773 K), κ(1100 K)) are added with the 4-phonon work (P1.5)**.

## Composition

Each `ResidualGenerator` carries a `characteristic-scale : σ` field seeded from this ledger
(`arch-11 §11.7`); `Quantity.combineTol` composes them along the DAG (max-abs or RSS per
`arch-10`). Stage-4 `CompressionPlan` (LowRank/HODLR/TT) truncation carries a **per-plan error
target** that also enters `combineTol` (`arch-07 §7.4`), so the emitted residual's budget
includes model-form + truncation + dressing-staleness terms, not just input σ.

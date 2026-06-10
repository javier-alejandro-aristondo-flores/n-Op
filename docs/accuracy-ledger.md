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
| 1 | bandgap_direct | ±0.1 eV (±0.05 near alloy band crossings) | hybrid-DFT / G₀W₀ required; AHC gap(T) one-shot dressing landed (row 120, `ΔE_g=ZPR·coth(Θ/2T)`); `slope-kind∈{isochoric,total}` tag guards vs row-63 strain double-count (`arch-19 §19.8`, `arch-12 §12.0.3`) |
| 2 | band_structure E_n(k) | RMS 50 meV within 2 eV of edges | TB-3NN-sp³d⁵ or Wannier/Fourier interpolation (`mesh-interpolation` sub-method, cheap); a **Wannierization quality gate** (band-reproduction error on held-out k-points) feeds the declared mesh-σ floor — maximal localization can fail quietly on entangled conduction bands |
| 3 | effective_mass_tensor | ±10% (transport-relevant) | parabolic / k·p; non-parabolicity grows with T |
| 4 | density_of_states g(E) | ±5% within ±k_BT of E_F | tetrahedron / Gaussian σ=50 meV |
| 5 | fermi_level E_F(T,n_d) | ±5 meV | charge-neutrality bisection |
| 6 | DOS_at_E_F | ±5% | readout of #4 |
| 7 | band_offset ΔE_C, ΔE_V | ±0.1 eV | Anderson/Tersoff cheap; GW supercell faithful |
| 8 | electron_affinity χ | ±0.1 eV | H-desorption >700 °C shifts χ >1 eV |
| 9 | phonon_dispersion ω_λ(q) | ±2% acoustic, ±5% optical | anharmonic Δω ~1–2% at 1500 K |
| 10 | phonon_DOS F(ω) | ±5% | derived from #9 |
| 11 | mode_gruneisen γ_λ(q) | ±15% | single γ_avg acceptable cheap |
| 12 | phonon_lifetimes τ_λ(q,T) | ±20% (gives κ ±10%) | 4-phonon correction needed **≳0.4 Θ_D** (diamond ≈880 K), landed row 121 (Slack-like factor) |
| 13 | thermal_conductivity κ(T) | ±20% @300 K (diamond, anchored), ±25% @773 K, ±35%→±15% @1100 K | RTA/3-ph **underestimates** 30–50% near 300 K; anchor diamond ±20% to `κ_iter≈2200` (rows 25+121+122), **not** `κ_RTA≈1800`; diamond κ(773 K) & β-Ga₂O₃ high-T are interpolations (±40%, lowest confidence) |
| 14 | thermal_expansion α_αβ(T) | ±10% (diamond); **III-N σ widened, no design-grade path** | QHA breaks above ~Θ_D/2 (GaN fails at 500 °C); III-N high-T is a flagged hole (`arch-17`), V2 = first-order self-consistent-phonon dressing (Layer-1.25 shape); propagates into gap(T) row-63 strain, G(T), T,P-hull |
| 15 | e-ph self-energy Σ_ep (AHC) | ±0.05 eV non-polar / ±0.1 eV polar on T-shift | **landed row 120**; per-material ZPR (diamond −345 meV indirect; omitting it mis-states `n_i` by ×11 @800 K) — see curated table below |
| 16 | carrier_mobility_electron μ_n | ±20% @300 K, ±30% @800 K | BTE-RTA; **alloy-disorder scattering (row 127) dominant for AlGaN channel** — without it μ(AlGaN) is systematically optimistic |
| 17 | carrier_mobility_hole μ_p | ±20% (critical, p-type diamond) | as #16 |
| 18 | saturation_velocity v_sat | ±15% | Shockley / Caughey–Thomas |
| 19 | impact_ionization α_ii | **factor-2** (per-material σ: diamond ×2.5 contested, GaN ×1.5, 4H-SiC ×1.3, β-Ga₂O₃ ×3, AlN/AlGaN ×2+) | Chynoweth `α=a·exp(−b/E)` landed (row 74 + curated `(a,b,σ)` below); misses hot-electron tail — the EDF-tail `Δα` correction ships as identity until external anchors exist (#49) |
| 20 | breakdown_field E_b | ±15% @≤500 °C (critical, BFOM, enters cubed → σ(BFOM)≈±60% diamond); **>500 °C cert-refused / frontier** | **E_b RISES with T** (`κ_BR>0`, +5×10⁻⁴/K diamond, +7×10⁻⁴/K 4H-SiC; row 123) — UWBG breakdown *hardens* with T; the prior "drops ~20%" was a sign error (conflated with mobility collapse). The EDF-tail anchor data are absent, so >500 °C is **not a met target** |
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
| 31 | schottky_barrier φ_B | ±0.1 eV (→ ×e⁴ contact R @500 °C) | Cowley–Sze; carbide shifts with soak; **image-force-lowering inconsistency (0.06 vs 0.18 eV across research files) unresolved — must be reconciled before any barrier-lowering coefficient seeds a `ProvenanceLedger` table** (shifts φ_B-derived contact R by `e^(Δ/kT)`) |
| 32 | contact_resistivity ρ_c | ±50% (orders span) | dominated by φ_B |
| 33 | interface_trap_density D_it | factor-2 | dangling-bond + strain |
| 34 | tunneling_transmission T_WKB | ±20% in log | Fowler–Nordheim closed form |
| 35 | spontaneous + piezo polarization P_sp/P_pz | ±5% (on the interface ΔP that `n_s` consumes) | landed: Z*-composition (rows 113–114); the linearized `Z*·Δw` path is ±10–20% on *absolute* P_sp, but the ±5% claim holds because `n_s` reads interface *differences* ΔP where the reference ambiguity largely cancels; absolute Berry-phase λ-path deferred V2 |
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
| 49 | hot_carrier_distribution f(E,F) | shape ±20%; high-E tail decisive | **OUTSIDE registry** (full-band MC); V1 EDF-tail correction `Δα(E,T_L,T_e)` is **fit only to external anchors and frozen w.r.t. the PINO loss** (else circular) — and since no anchor data exist in V1, it **ships as identity** and the high-E×high-T corner stays cert-refused (`arch-19 §19.8`, `arch-12 §12.0.3`) |
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
| κ(300 K) | **±20%** (anchored to `κ_iter≈2200`, not `κ_RTA`) | met (rows 25 + 121 + 122) |
| κ(773 K) | **±25%** | met (4-ph correction row 121, `≳0.4 Θ_D`) |
| κ(1100 K) | **±35%→±15%** with 4-ph | met (rows 121 + 122; battery anchors below) |
| E_form (300 K) | **±0.2 eV** | met (rows 30 + FNV 31–33) |
| μ (300 K) | **factor-2** | met with caveats |

The reference battery (cert obligation 4, `arch-12 §12.1`) checks these at the MVP anchors;
the **high-T κ anchors (κ(773 K), κ(1100 K)) are now landed** (rows 121–122 + the curated κ(T)
battery below).

## Per-material curated coefficients (ProvenanceLedger seed)

The per-material values the Pass-C rows (120–127) consume, recorded here as the canonical
curated-coefficient seed. Each is a `ProvenanceLedger` entry `(value, σ, source, cost-class)`
(`arch-19-coupling-structure §19.8`); for the MVP diamond they are `curated`, other materials
`per-material-DFPT` (the gating data-acquisition task before that material is claimed). Values are
literature-anchored (full citations in `docs/superpowers/specs/2026-06-10-pass-c-accuracy-design.md`).

**AHC ZPR / gap T-slope (row 120; `slope-kind` tagged):**

| Material | ZPR (meV) | dE_g/dT (meV/K) | slope-kind | source |
|---|---|---|---|---|
| diamond | −345 (indirect; exp 340–370) | −0.45 | total | Cardona / Engel PAW −323; **−628 meV is the *direct* gap (Antonius PRL 112 215501, 2014), kept separate** |
| c-BN | −400 | ~−0.50 (unmeasured) | total | Engel −402 / Miglio −406 |
| AlN | −385 | −0.55 | total | Engel −377 |
| GaN | −180 | −0.50 | total | Engel −171; Varshni (Nepal APL 2005) |
| β-Ga₂O₃ | −200 | −0.90 (anisotropic, polar) | total | Lee APL Mater. 2023 |

(`total`-tagged ⇒ cert refuses co-activation with row-63 strain on the same observable, `arch-12 §12.0.3`.)

**κ(T) battery (W/m·K @ 300 / 773 / 1100 K; rows 121–122):**

| Material | 300 K | 773 K | 1100 K | source |
|---|---|---|---|---|
| diamond | 2200 (exp 2000–2500) | 620 | 450 | Feng–Lindsay–Ruan PRB 96 161201 (2017); Broido APL 91 231922 (2007) |
| GaN (a) | 240 | 100 | 70 | almaBTE |
| AlN (c) | 339 | ~140 | ~95 | Lindsay–Broido–Reinecke PRL 109 095901 (2012) |
| β-Ga₂O₃ | [010] 27, [100] 11 (tensor, ~2.5–3× anisotropy) | — | — | Guo APL 106 111909 (2015) |

**High-field Chynoweth `α_ii=a·exp(−b/E)` + Caughey–Thomas + `κ_BR` (rows 123, 74):**

| Material | a (cm⁻¹) | b (V/cm) | σ (×a) | v_sat (cm/s), β | κ_BR (K⁻¹) | source |
|---|---|---|---|---|---|---|
| diamond | 1.93e5 | 7.59e6 | ×2.5 (contested) | 1.5e7, β=1; μ₀∝T^(−1.5..−2.8) | +5e−4 (±50%) | Hiraiwa–Kawarada JAP 114 034506 (2013); Isberg JAP 109 (2011) |
| GaN | e 1.5e5 / h 6.4e5 | e 1.41e7 / h 1.45e7 | ×1.5 | 2.5e7, β=2 | — | Maeda APL 112 (2018) |
| 4H-SiC (ref) | 1.88e6 | 9.13e6 | ×1.3 | — | +7e−4 | literature |
| β-Ga₂O₃ | e (anisotropic) | E_c 10.2/4.8/7.6 MV/cm | ×3 | — | — | Ghosh–Singisetti JAP 124 (2018); **holes never measured** |

Residue (cert-refused / frontier until provenanced): diamond `α_n`/`α_p` never separated;
pure-AlN and β-Ga₂O₃-hole `α_ii` missing; per-`(host,particle)` NIEL `σ_d` (row 112) and
`η_recomb(T_L)` have no closed form; BTE/MC EDF-tail anchors absent.

## Composition

Each `ResidualGenerator` carries a `characteristic-scale : σ` field seeded from this ledger
(`arch-11 §11.7`); `Quantity.combineTol` composes them along the DAG (max-abs or RSS per
`arch-10`). Stage-4 `CompressionPlan` (LowRank/HODLR/TT) truncation carries a **per-plan error
target** that also enters `combineTol` (`arch-07 §7.4`), so the emitted residual's budget
includes model-form + truncation + dressing-staleness terms, not just input σ.

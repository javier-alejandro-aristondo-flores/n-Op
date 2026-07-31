---
id: accuracy-ledger
title: "Per-observable accuracy ledger"
owns:
  - per-observable accuracy regime
  - design-grade
  - ledger-tracked observable counts
  - MVP design-grade targets
  - curated coefficient seed
  - monoclinic frame guard
  - polarization sign guards
  - seeded-value provenance status
  - accuracy residue
anchors:
  what-this-is: "What this ledger is"
  design-grade: "Design-grade"
  observable-counts: "Two counts, two terms"
  observable-regimes: "Per-observable accuracy regimes"
  mvp-targets: "MVP design-grade targets"
  curated-coefficients: "Per-material curated coefficients"
  ahc-zpr: "Zero-point renormalization and gap temperature slopes"
  kappa-battery: "Thermal-conductivity battery"
  monoclinic-frames: "Monoclinic frame guard"
  high-field-coefficients: "High-field coefficients"
  iii-n-electronic: "III-nitride electronic baseline"
  polarization-coefficients: "Polarization, piezoelectric and Born coefficients"
  polarization-bowing: "Alloy polarization bowing"
  elastic-coefficients: "Elastic constants"
  transport-coefficients: "Carrier transport coefficients"
  seed-provenance: "What the seeded values rest on"
  residue: "Residue"
  composition: "How ledger values reach the residual budget"
depends-on:
  - cert-obligations
  - reference-battery
  - out-of-scope
  - coupling-structure
  - residual-definitions
  - typeclass-alphabet
  - compose-time-pipeline
  - multiscale-state
  - traps
open-questions:
  - id: mesh-uncertainty-floor-undeclared
    anchor: observable-regimes
    summary: "No numeric per-observable mesh-uncertainty floor is declared anywhere in the corpus. Transport observables computed from a Boltzmann solve need roughly 50-cubed-equivalent sampling of the Brillouin zone, and the MVP's 8×8×8 mesh is factor-two-grade for transport even with exact inputs. Row 2 of the regime table needs that floor as a number before any transport regime below factor two can be claimed."
  - id: alloy-polarization-bowing-unseeded
    anchor: polarization-bowing
    summary: "The aluminium-gallium-nitride polarization bowing coefficient and the piezoelectric-tensor bowings are UNSEEDED. Until they are seeded, mid-composition interface-polarization claims carry a widened uncertainty, and the sign guard between the ledger's minus-b form and the reference file's plus-b form is live. Seeding is gated on a paywalled pin-read of the two primary sources."
  - id: diamond-static-permittivity-unseeded
    anchor: seed-provenance
    summary: "The diamond static permittivity, 5.7 ± 0.05, is UNSEEDED: no primary measurement was found, and every trail ends in an unreferenced compilation. It is load-bearing — it is the permittivity in the image-force-lowering formula of regime row 31. Two closes are available: name a measurement, or derive it from the long-wavelength refractive index and cite that. The row does not state a frequency window, and the derivation only works at the right one — the infrared index gives 5.66, the visible index gives 5.84."
  - id: diamond-debye-temperature-unseeded
    anchor: seed-provenance
    summary: "The diamond Debye temperature, 2200 K ± 50, is UNSEEDED, and the literature spread is method-dependent from about 1860 K (elastic constants) to about 2230 K (low-temperature specific heat) — far wider than the stated uncertainty, which is 2.3%. A stated uncertainty narrower than the disagreement between methods is a claim the corpus cannot support. This row is coupled to the thermal-conductivity battery: it sets the four-phonon validity threshold at 0.4 of it, so 2200 K puts the 773 K conductivity anchor outside the four-phonon window and 1860 K puts it inside. Closing it means first deciding which Debye temperature the corpus needs, because they are different numbers."
  - id: diamond-thermal-conductivity-provenance
    anchor: kappa-battery
    summary: "The diamond thermal conductivities at 773 K and 1100 K have two incompatible descriptions in canon. This ledger attributed all three temperatures to a pair of papers; the reference file declares these two theory-interpolation with no source named beyond an internal audit pointer. The primary measurement spanning 170–1200 K — Olson et al., Phys. Rev. B 47, 14850 (1993) — is the source both rows would rest on and could not be retrieved. The reference file's own stated law for the 1100 K row does not reproduce the 773 K row: the implied exponent falls from 1.34 to 0.91 across the interval, whereas four-phonon scattering steepens the high-temperature falloff."
  - id: diamond-thermal-conductivity-citation-material
    anchor: kappa-battery
    summary: "Broido et al., Appl. Phys. Lett. 91, 231922 (2007), cited for the diamond 300 K thermal conductivity, appears from its published abstract to be about silicon and germanium. The diamond paper from that group is Ward et al., Phys. Rev. B 80, 125203 (2009). Settling it needs one look at the 2007 paper to confirm diamond is absent."
  - id: diamond-cohesive-energy-allotrope
    anchor: seed-provenance
    summary: "The diamond cohesive energy, 7.37 eV/atom, matches the standard tabulated figure for graphite (7.374) to three decimals and diamond (7.346) only to within 24 meV. Both sit inside the stated ±0.05 eV/atom, so the value is defensible either way — but the provenance may be another allotrope's number, and 24–28 meV/atom is the same size as the diamond-graphite formation-energy row it has to be consistent with, and half this row's own uncertainty."
  - id: aln-high-temperature-conductivity-absence
    anchor: seed-provenance
    summary: "The aluminium-nitride 1100 K thermal-conductivity row states that no single-crystal measurement above 500 K exists, and the 300 K row of the same file cites Slack et al., J. Phys. Chem. Solids 48, 641 (1987) — a paper whose measurements are reported to extend far above 500 K. Either the absence claim is too strong or the citation is being read wrongly. This matters in the opposite direction from a wrong value: an unnecessary refusal costs coverage silently, and nothing will ever fire on it."
  - id: figures-of-merit-count
    anchor: observable-counts
    summary: "The count of figures of merit is asserted as 16 in three places, and the corpus's only enumeration of them has 15 rows. Either one is missing from the enumeration or the count is wrong."
---
# Per-observable accuracy ledger

## What this ledger is

The per-observable **accuracy regime**: the target tolerance each closed-form or one-shot
path must meet, with the note on what the cheap path buys against the faithful one.

This is the **error-model seed**. Each value is a declared characteristic scale that
`Quantity.combineTol` ([typeclass-alphabet]) composes into a per-residual error budget
([residual-definitions]).

**It is a reference table, not the registry.** The canonical per-formula bundle,
evaluation cost and differentiability live in
`physics/library/formulas/registry-manifest.csv`, and the canonical per-value citations
live in the `Source` column of `physics/library/cert/reference-data/*.csv`
([reference-battery]).

## Design-grade

**Design-grade** means *device-design-adequate at the ultra-wide-gap operating point*,
above 500 °C and at high field — not ab-initio-converged. Where the closed-form path
cannot meet design-grade, the gap is named rather than narrowed.

## Two counts, two terms

Two counts circulate and they are not the same number.

- **Catalog observables** — 52. The observables of the derivation catalog.
- **Ledger-tracked observables** — 59. Everything this ledger carries an accuracy regime
  for: the 52 catalog observables plus seven more.

A document quoting "52" means the catalog sense.

Separately there are **16 figures of merit** — Baliga, Johnson, Keyes, the combined
breakdown-mobility-thermal figures and the rest. They are algebraic compositions of the
observables below and inherit their composed `combineTol` budget. The count is the open
question `figures-of-merit-count`.

## Per-observable accuracy regimes

| # | Observable | Accuracy regime | Cheap vs faithful |
|---|---|---|---|
| 1 | bandgap_direct | ±0.1 eV, ±0.05 near alloy band crossings | hybrid density functional or quasi-particle correction required; the one-shot gap dressing is registry row 120, `ΔE_g=ZPR·coth(Θ/2T)`; the `slope-kind` tag guards against double-counting the strain path ([cert-obligations#composition-refusals]) |
| 2 | band_structure E_n(k) | RMS 50 meV within 2 eV of the edges | three-nearest-neighbour tight binding or Wannier-Fourier interpolation, cheap; a **Wannierization quality gate** on held-out k-points, which can fail quietly on entangled conduction bands. **Mesh convergence, quantified:** mobility, electronic conductivity and impact ionization from a Boltzmann solve need about **50³-equivalent k-sampling**, and the MVP's **8×8×8, 29-point irreducible mesh is factor-2-grade for transport** even with exact inputs. Irreducible-zone reduction helps *cost*, not convergence; interpolation is the only path off factor two. **No numeric per-observable mesh-uncertainty floor is declared** — `mesh-uncertainty-floor-undeclared` |
| 3 | effective_mass_tensor | ±10%, transport-relevant | parabolic or k·p; non-parabolicity grows with temperature |
| 4 | density_of_states g(E) | ±5% within ±k_BT of E_F | tetrahedron or Gaussian at 50 meV |
| 5 | fermi_level E_F(T,n_d) | ±5 meV | charge-neutrality bisection |
| 6 | DOS_at_E_F | ±5% | readout of #4 |
| 7 | band_offset ΔE_C, ΔE_V | ±0.1 eV | Anderson or Tersoff cheap; quasi-particle supercell faithful |
| 8 | electron_affinity χ | ±0.1 eV | hydrogen desorption above 700 °C shifts χ by more than 1 eV |
| 9 | phonon_dispersion ω_λ(q) | ±2% acoustic, ±5% optical | anharmonic shift is 1–2% at 1500 K |
| 10 | phonon_DOS F(ω) | ±5% | derived from #9 |
| 11 | mode_gruneisen γ_λ(q) | ±15% | a single averaged γ is acceptable as the cheap path |
| 12 | phonon_lifetimes τ_λ(q,T) | ±20%, giving conductivity ±10% | the four-phonon correction is needed above `≈0.4 Θ_D` and is registry row 121. For diamond that threshold is about 880 K on the seeded Debye temperature — a number that is itself UNSEEDED and method-contested, so the threshold moves with it |
| 13 | thermal_conductivity κ(T) | ±20% at 300 K for diamond, anchored; ±25% at 773 K; ±35% falling to ±15% at 1100 K with the four-phonon correction | relaxation-time three-phonon **underestimates** diamond by 30–50% near 300 K, so the anchor is the iterative solution near 2200, **not** the relaxation-time value near 1800. In the other direction, three-phonon **overpredicts** the nitrides at high temperature — measured gallium nitride falls as `T^−1.2` to `T^−1.5` — so both branches are carried, three-phonon as the upper and measured as the lower. **Aluminium nitride above 500 K is theory-only.** Diamond above 300 K and β-Ga₂O₃ at high temperature are interpolations at ±40%; see the thermal-conductivity battery below |
| 14 | thermal_expansion α_αβ(T) | ±10% for diamond; **III-nitride uncertainty widened, no design-grade path** | quasi-harmonic validity is per-material and does not follow a Debye-scaled rule ([traps]): diamond holds to about 800 °C, gallium nitride and aluminium nitride both fail by 500 °C. The III-nitride high-temperature hole is [out-of-scope#exclusions]; V2 is a first-order self-consistent-phonon dressing. It propagates into the gap through the strain path, into the shear modulus, and into the temperature-pressure hull |
| 15 | e-ph self-energy Σ_ep | ±0.05 eV non-polar, ±0.1 eV polar, on the temperature shift | registry row 120. Per-material **isochoric** zero-point renormalization is the `coth` amplitude and lattice expansion is the strain row's job. Omitting the diamond renormalization mis-states the intrinsic carrier density by a factor 11 at 800 K — see the curated zero-point renormalizations below |
| 16 | carrier_mobility_electron μ_n | ±20% at 300 K, ±30% at 800 K | relaxation-time Boltzmann. **Alloy-disorder scattering (registry row 127) is dominant for the aluminium-gallium-nitride channel** — without it the alloy mobility is systematically optimistic. Aluminium nitride intrinsic 871 perpendicular / 619 parallel, best measured 426; the widely quoted "≈300" is doped or defective material, not intrinsic |
| 17 | carrier_mobility_hole μ_p | ±20%, critical for p-type diamond | as #16 |
| 18 | saturation_velocity v_sat | ±15% | Shockley or Caughey-Thomas |
| 19 | impact_ionization α_ii | **factor 2 or worse**, per material: diamond ×2.5 and contested, **gallium nitride ≥×3** with published prefactors spanning more than four orders, 4H silicon carbide ×1.3, β-Ga₂O₃ ×3, **aluminium nitride measured is UNSEEDED and cert-refused** with only an electron-only Monte-Carlo value | the Chynoweth form `α=a·exp(−b/E)` is registry row 74, with the curated triples in the high-field coefficient table below. It misses the hot-electron tail; the tail correction ships as identity until external anchors exist (#49) |
| 20 | breakdown_field E_b | **per material: diamond ±20%, gallium nitride ±15%**, at or below 500 °C. The chain: a factor-2 uncertainty in the Chynoweth prefactor propagates to 10–20% in `E_b`, amplified by field non-uniformity, and `E_b` enters the Baliga figure **cubed**, so the figure carries about ±60% for diamond. **Above 500 °C is cert-refused frontier** | **`E_b` rises with temperature** — the coefficient is positive, +5×10⁻⁴/K for diamond and +7×10⁻⁴/K for 4H silicon carbide (registry row 123). Ultra-wide-gap breakdown *hardens* with temperature; the falling quantity it is easily confused with is mobility. The distribution-tail anchor data are absent, so above 500 °C is **not** a met target |
| 21 | hall_factor r_H | ±10% | a constant near 1.18 is acceptable |
| 22 | seebeck S | ±15% | Mott formula |
| 23 | dielectric_constant_static ε_r | ±5% | Lyddane-Sachs-Teller from the phonons |
| 24 | dielectric_function ε(ω) | ±10% | random-phase or Bethe-Salpeter |
| 25 | defect_formation_energy E_f | ±0.2 eV, which controls the defect concentration | finite-size charge correction mandatory |
| 26 | defect_ionization_energy E_a | ±50 meV | hydrogenic or empirical |
| 27 | dopant_solubility c_sol | ±factor 2 | Arrhenius |
| 28 | defect_level_in_gap E_t | ±0.1 eV | trap-assisted leakage |
| 29 | capture_cross_section σ_n,p | factor 3 | **outside the registry** — Huang-Rhys with Marcus theory |
| 30 | surface_dipole p_s | ±0.1 D | tabulated by termination |
| 31 | schottky_barrier φ_B | ±0.1 eV, which is a factor `e⁴` on contact resistance at 500 °C | Cowley-Sze; the carbide shifts it with soak. Image-force lowering is `Δφ=√(qE/4πε_sε₀)`, giving 0.16 eV at 10⁶ V/cm and 0.50 eV at 10⁷ for diamond at a static permittivity of 5.7 — **and that permittivity is UNSEEDED**, `diamond-static-permittivity-unseeded` |
| 32 | contact_resistivity ρ_c | ±50%; the measured spread is orders | dominated by φ_B |
| 33 | interface_trap_density D_it | factor 2 | dangling bonds plus strain |
| 34 | tunneling_transmission T_WKB | ±20% in the logarithm | Fowler-Nordheim closed form |
| 35 | spontaneous and piezoelectric polarization | ±5% on the interface difference, **aluminium-gallium-nitride on gallium nitride only**; ±10–20% on the absolute spontaneous polarization | the Born-charge composition path, registry rows 113–114. The ±5% holds by an **accidental cancellation** between the spurious reference term and the proper-versus-improper `e₃₁` error, which are large, opposite in sign and nearly cancelling — **not** by generic reference cancellation. It requires a zincblende-reference spontaneous polarization paired with a **proper** `e₃₁` and no reference correction ([cert-obligations#composition-refusals]), and **fails for high-indium alloys**, which are cert-refused. Off-axis holography refutes the reference-frame bowing curvature for indium-gallium-nitride and validates the local frame, which narrows where the cancellation may be relied on; the aluminium-gallium-nitride anchor is untouched |
| 36 | elastic_tensor C_ijkl | ±5% | stress-strain or perturbation theory |
| 37 | bulk and shear modulus | ±5% | Voigt average |
| 38 | sound_velocity v_s | ±5% | Christoffel |
| 39 | cohesive and surface energy γ_s | ±0.1 J/m² | slab calculation |
| 40 | fracture_toughness K_IC | ±20%, statistical | Griffith with Young's modulus |
| 41 | resonant_modes ω_n | ±10% | **device-scale**, continuum elastic |
| 42 | displacement_threshold E_d | ±5 eV | tabulated: about 37 eV for carbon, about 20 eV on the gallium sublattice, about 25 eV for nitrogen |
| 43 | gibbs_free_energy G | ±10 meV/atom | quasi-harmonic: static energy plus vibrational free energy plus `PV` |
| 44 | phase_boundary | ±5% in pressure-temperature | free-energy crossing |
| 45 | specific_heat c_v, c_p | ±3% | Debye is adequate as the cheap path |
| 46 | oxidation_rate r_ox | **factor 3** | Eyring; diamond air-oxidation above 600 °C is the lifetime limiter |
| 47 | hydrogen_desorption r_H | **factor 2** | Eyring at about 3.8 eV desorption energy; drives the affinity shift |
| 48 | self_heating T_op | ±10 K | **device-scale** continuum heat equation |
| 49 | hot_carrier_distribution f(E,F) | shape ±20%; the high-energy tail is decisive | **outside the registry** — full-band Monte Carlo. The V1 tail correction is **fit only to external anchors and frozen against the training loss**, else it is circular. Since no anchor data exist in V1 it **ships as identity**, and the high-field-by-high-temperature corner stays cert-refused ([out-of-scope#exclusions]) |
| 50 | electromigration E_a | ±0.1 eV | nudged-elastic-band interface hop |
| 51 | defect_evolution dN/dt | **factor 2** | master equation or kinetic Monte Carlo, on the slow tier ([multiscale-state]) |
| 52 | 2DEG_sheet_density n_s | ±10% | the Ambacher composition, registry row 115 |
| 53 | pyroelectric slope p (row 128) | ±30% on p | primary plus secondary at fixed stress; drives the sheet-density drift with temperature |
| 54 | Poole-Frenkel dielectric leakage (row 129) | ±1 decade | trap-parameter-dominated, per film |
| 55 | time-dependent dielectric breakdown (row 130) | order of magnitude | thermochemical field model per film; a lifetime figure of merit, not a precision target |
| 56 | crystallized fraction (row 131) | factor ~3 on the rate | history-dependent for a deposited film; the onset window, about 700 °C for alumina, is the load-bearing output |
| 57 | \|F_hkl\|² diffraction intensity (row 132) | peak positions exact given the cell and ion positions; ±10% on intensity ratios | kinematic limit, with no extinction or multiple scattering; the Debye-Waller factor comes from the phonon density of states |
| 58 | Raman response (row 133) | shifts ±0.2 meV, zone-centre grade; activities factor ~2 | the shifts ride #9; the activities are the new linear-response output |
| 59 | radiative recombination (row 134) | order of magnitude on the coefficient | negligible in the ultra-wide-gap device balance, given the tiny intrinsic carrier density; a photoluminescence validation channel only |

## MVP design-grade targets

The headline outputs the closed-form bet must meet.

**Status legend.** *path-met* means the closed-form path exists in the registry **and**
its diamond reference anchors are seeded in the machine-readable battery, so cert
obligations 4 and 8 can actually check the target. It is **not** a claim that a cert run
has passed — no code exists yet.

| Observable | Design-grade target | Status |
|---|---|---|
| bandgap at 300 K | **±0.15 eV** after the quasi-particle correction | path-met — registry row 6; battery row `bandgap-indirect`, diamond |
| elastic constants at 300 K | **±5%** | path-met — registry row 60; battery rows `elastic-C11`, `elastic-C12`, `elastic-C44`, diamond |
| κ at 300 K | **±20%**, anchored to the iterative solution near 2200 and not the relaxation-time value | path-met — registry rows 25, 121, 122; battery row κ at 300 K |
| κ at 773 K | **±25%** | path-met — the four-phonon correction, registry row 121, valid `≳0.4 Θ_D`; battery row κ at 773 K |
| κ at 1100 K | **±35% falling to ±15%** with the four-phonon correction | path-met — registry rows 121, 122; battery row κ at 1100 K |
| formation energy at 300 K | **±0.2 eV** | path-met — registry rows 30 and the finite-size correction 31–33; battery cohesive-energy and graphite-boundary anchors |
| mobility at 300 K | **factor 2** | path-met with caveats — battery time-of-flight electron and hole mobilities |

The reference battery checks these at the MVP anchors ([cert-obligations#reference-cache]).

**The diamond battery is seeded** — lattice constant, indirect gap, three elastic
constants with bulk modulus and density, Debye temperature, maximum phonon energy, κ at
300, 773 and 1100 K, cohesive energy, the diamond-graphite boundary point, static
permittivity, time-of-flight mobilities, saturation velocity with its exponent, and the
Chynoweth pair. **Seeded means a row exists carrying a value and an uncertainty. It does
not mean the row's provenance resolves** — five of those anchors are in
the seeded-value provenance section below, two of them UNSEEDED.

## Per-material curated coefficients

The per-material values the dressing rows 120–127 consume, recorded here as the
canonical curated-coefficient seed. Each is a `ProvenanceLedger` entry
`(value, σ, source, cost-class)` ([coupling-structure]). For the MVP diamond they are
`curated`; for other materials `per-material-DFPT`, which is the gating data-acquisition
task before that material is claimed.

**Per-value citations are the `Source` column of
`physics/library/cert/reference-data/*.csv`, which is canonical for them.** This page
carries the values and the composition rules that travel with them; it is not the
citation of record. Where a `Source` cell names no author and no year,
the seeded-value provenance section below says what the row actually rests on.

### Zero-point renormalization and gap temperature slopes

Registry row 120. The `coth` amplitude is the **isochoric** electron-phonon
renormalization; zero-point lattice expansion is the strain row's job
([coupling-structure]).

| Material | Isochoric (meV) | Lattice (meV) | Total (meV) | dE_g/dT e-ph (meV/K) | slope-kind | source |
|---|---|---|---|---|---|---|
| GaN | −189 (Engel −171) | −49 | −238 | −0.45 | isochoric | Engel PRB 106 094316 (2022); Miglio npj CM 6 167 (2020); Nepal APL 87 (2005) |
| AlN | −399 (Engel −377) | −85 | −484 | −0.55 | isochoric | Engel 2022; Miglio 2020 |
| diamond, indirect | −345 (band −320…−366) | small | ≈−345 | −0.45 | isochoric | Antonius PRL 112 215501 (2014); Engel −323 |
| c-BN | −402 | — | — | ~−0.50, unmeasured | isochoric | Engel −402; Miglio −406 |
| β-Ga₂O₃ | −200 | — | — | −0.90, anisotropic and polar | isochoric — clamped-cell, expansion minor over 0–900 K; the −0.45 eV shift at 700 K is *total* and must not be composed with the strain row | Lee APL Mater. 11 011106 (2023); Arabov arXiv 2603.29484 (2026) |

An `isochoric` tag composes with the strain path freely; a `total` tag makes the cert
**refuse** co-activation with it on the same observable
([cert-obligations#composition-refusals]). **The tag must describe what the value
contains** — the clamped-lattice values above are electron-phonon only, and carrying them
under a `total` tag both overstates them and blocks the composition that would complete
them. The diamond **direct**-gap renormalization of −628 meV stays quarantined: it is a
different valley.

### Thermal-conductivity battery

W/m·K at 300, 773 and 1100 K; registry rows 121–122.

| Material | 300 K | 773 K | 1100 K | source |
|---|---|---|---|---|
| diamond | 2200, measured spread 2000–2500 | 620 | 450 | 300 K: measured — Inyushkin PRB 97 144305 (2018) gives 2400 to 410 K; Vandersande Proc. SPIE 2428 610 (1995) gives 2400–2500 for type IIa. Four-phonon calculation: Feng, Lindsay & Ruan PRB 96 161201 (2017). **773 and 1100 K: the reference file declares these `theory-interpolation` and names no literature** — `diamond-thermal-conductivity-provenance` |
| GaN, a-axis | 240 three-phonon / ~200 measured | three-phonon 100 / **measured ~60** | three-phonon 70 / **measured ~35–40** | three-phonon from an anharmonic Boltzmann solve; measured Zheng PRMat 3 014601 (2019), falling as `T^−1.2` to `T^−1.5` |
| AlN, c-axis | 339, measured with first-principles agreement | ~140, theory-only | ~95, theory-only | Rounds APEX 11 071001 (2018); Slack J. Phys. Chem. Solids 48 641 (1987). The 1100 K row states that no single-crystal measurement above 500 K exists — `aln-high-temperature-conductivity-absence` |
| β-Ga₂O₃ | `[010]` 27.0, `[100]` 10.9, `[001]` ≈14 — about 2.5× anisotropy; Klimm's `λ₂₂ ≡ [010]` 24.26 and `λ₃₃ ≡ [001]` 14.09 concur in the crystal-physical frame | `[010]` ≈9 | `[010]` ≈6 | Guo APL 106 111909 (2015); Klimm CRT 58 2200204 (2023), open access. The high-temperature values are derived — the 300 K tensor scaled by its own `T^−m` with `m ≈ 1.0–1.2`, at about ±20% |

**A confusion trap in the diamond citation.** Feng, Lindsay & Ruan (2017) is cited for
diamond, and it is genuinely about diamond: it states that three-phonon scattering alone
**overpredicts diamond conductivity by 31% at 1000 K**, and that including four-phonon
scattering reduces the prediction by 30% at 1000 K. That result is what registry row 121
implements. But the paper's widely-quoted "2200 → 1400 W/mK at room temperature" figures
are **for boron arsenide, not diamond** — and they collide numerically with diamond's own
value near 2200, one paragraph away. Anyone re-deriving the diamond anchor from this
paper can land on the right number for the wrong material and see nothing wrong. The
paper gives no diamond number in its text; its diamond values are in a figure.

### Monoclinic frame guard

β-Ga₂O₃ — never relabel. **Four** distinct axis systems are in play and none may be
interchanged.

- The **crystal-physical frame** is `e₂∥b`, `e₃∥c`, `e₁ = a*`. Klimm's tensor components
  are therefore `λ₂₂ ≡ [010]` and `λ₃₃ ≡ [001]`.
- His **plane-normal** measurements `λ₍₁₀₀₎` and `λ₍₀₀₁₎` lie along `a*` and `c*` and must
  **never** be relabelled `[100]` and `[001]`.
- The **high-field frame** of Ghosh and Singisetti has `c*` as its third axis, about 13.8°
  off `[001]`, which is why the critical-field and impact-ionization entries below are
  tagged `c*` rather than `[001]`.
- The **elastic-tensor frame** is `x∥a y∥b z∥c*`, from resonant ultrasound with
  laser-based determination. Its first axis is the *real* `a`, 13.83° from `a*`, so its
  `C₁₁` is not along the crystal-physical `e₁`.

In a material with about 2.5× anisotropy, a relabel silently attaches a value to the
wrong crystallographic direction. [traps] carries this as a hazard and points here.

### High-field coefficients

Chynoweth `α_ii=a·exp(−b/E)`, Caughey-Thomas saturation, and the breakdown-field
temperature coefficient; registry rows 123 and 74.

| Material | a (cm⁻¹) | b (V/cm) | σ (×a) | v_sat (cm/s), β | temperature coefficient (K⁻¹) | source |
|---|---|---|---|---|---|---|
| diamond | 1.93e5 | 7.59e6 | ×2.5, contested | 1.5e7, β=1; `μ₀∝T^(−1.5..−2.8)` | +5e−4 (±50%) | Hiraiwa & Kawarada JAP 114 034506 (2013); Isberg JAP 109 (2011) |
| GaN | e 4.48e8 / h 7.13e6; spread includes e 1.5e5 | e 3.39e7 / h 1.46e7; the low-prefactor set gives e 1.41e7 | **≥×3**; prefactor spread exceeds four orders | v_sat 1.4e7, peak 2.85e7, β=2 | +3.85e−4 as a device breakdown-voltage slope; the normalized form is UNSEEDED | Cao APL 112 262103 (2018); Özbek & Baliga IEEE EDL 32 1361 (2011); Frontiers Mater. 9 846418 (2022) |
| AlN | e 8.875e6, Monte Carlo, electron-only; **measured UNSEEDED** | e 3.759e8 | unbounded | v_sat 1.4e7, β~2 | UNSEEDED — no avalanche data; positive by analogy | Bulutay SST 17 L59 (2002); measured coefficients cert-refused |
| 4H-SiC, reference | 1.88e6 | 9.13e6 | ×1.3 | — | +7e−4 | standard compilations |
| β-Ga₂O₃ | e per direction 0.79 / 2.16 / 0.706 ×10⁶ on `a` / `b` / `c*` | 2.92 / 1.77 / 2.10 ×10⁷; critical field 10.2 / 4.8 / 7.6 MV/cm on the same axes | ×3 | 1–1.5e7 saturation, peak ~2e7 | — | Ghosh & Singisetti JAP 124 085707 (2018) Table 1. **Holes never measured** — self-trapped, cert-refused |

### III-nitride electronic baseline

Registry rows 1–6 and 63.

| Quantity | GaN | AlN | source |
|---|---|---|---|
| E_g at 0 K, direct Γ | 3.51 eV | 6.25 eV | Vurgaftman & Meyer JAP 94 (2003) |
| Varshni α / β | 0.909 meV/K / 830 K | 1.799 / 1462 | Vurgaftman & Meyer 2003; Nepal APL 87 (2005) gives 0.94/791 and 2.63/2082 |
| alloy gap bowing | 0.7–1.0 eV | — | Vurgaftman & Meyer 2003; Nepal 2005 |
| m*_e, perpendicular / parallel | 0.20 / 0.20 | 0.32 / 0.33 | Vurgaftman & Meyer 2003; Rinke PRB 77 (2008) |
| ε_0 / ε_∞, perpendicular | 8.9 / 5.35 | 8.5 / 4.77 | Ioffe NSM archive; Wagner & Bechstedt PRB 66 (2002) |
| gap deformation potential a_V | −7.6 eV | −9.8 eV | Rinke 2008 |
| wurtzite deformation potentials, five components | −5.33 / −8.84 / 5.80 / −3.09 / −2.82, quasi-particle | −4.31 / −12.11 / 9.12 / −3.79 / −3.23, hybrid | Yan APL 95 121111 (2009) |

### Polarization, piezoelectric and Born coefficients

Zincblende-reference spontaneous polarization with the **proper** `e₃₁`, which is the
self-consistent pairing the cert enforces ([cert-obligations#composition-refusals]).

| Quantity | GaN | AlN | source |
|---|---|---|---|
| P_sp, zincblende reference | −0.029…−0.034 | −0.081…−0.090 C/m² | Bernardini, Fiorentini & Vanderbilt PRB 56 (1997); Zoroddu PRB 63 (2001) |
| Z*, axial, cation positive | +2.7 | +2.7 | Bernardini 1997 |
| e₃₃, full | 0.73 / 1.02 hybrid | 1.46 / 1.57 | Bernardini 1997; Dreyer PRX 6 (2016) |
| **e₃₁ proper** | −0.49 / −0.55 hybrid | −0.60 / −0.68 C/m² | Bernardini 1997; Dreyer 2016 |
| e₃₁ improper — **do not pair with a zincblende-reference P_sp** | −1.86 | −2.03 | Dreyer 2016, reference only |
| d₃₃ / d₃₁ / d₁₅ (pm/V) | 2.7 / −1.4 / 1.8 | 5.4 / −2.1 / 2.9 | Bernardini & Fiorentini cond-mat/0202496 |
| n_s, gallium face, x≈0.3 | 1.1×10¹³ cm⁻² | — | Ambacher JAP 87 (2000) |

**Pyroelectric sign guard.** The drift is `P_sp(T) = P_sp(T₀) + p·(T−T₀)`, with `p` the
combined primary and secondary coefficient at fixed stress. **`p` is positive in the
seeded zincblende-reference frame**: the reference-frame values are negative and their
magnitude decreases toward zero as temperature rises, so `dP_sp/dT > 0`. Raw literature
quotes `p` as negative under the opposite, positive-polarization convention, and lifting
a published value without flipping it inverts the sheet-density drift. Seeded values are
AlN `+3.0×10⁻⁶` and GaN `+4.5×10⁻⁶` C/m²K, both at ×2 — `polarization-piezoelectric.csv`
is canonical for them. The drift is **20–30% of the sheet charge over a 750 K rise**,
which is larger than the ±5% polarization budget at the operating point.

### Alloy polarization bowing

**Spontaneous polarization and the piezoelectric tensor are not linear in composition for
aluminium-gallium-nitride.** The quadratic-bowing form is

```
P_sp(x) = x·P_AlN + (1−x)·P_GaN − b_P·x(1−x)
```

with the analogous form per piezoelectric component. The nonlinearity exceeds the ±5%
interface-polarization target at mid-to-high aluminium fraction.

**Sign guard.** In this `−b_P` form, **`b_P` is negative** — the bowing is always upward.
The reference file states the same physics in the opposite convention, `+b·x(1−x)` with
**b positive**, expected near `+0.019–0.021 C/m²`. The two are equivalent through the
double negative, and **lifting the file's `+b` straight into this form flips the bowing**
and corrupts interface charge at mid-to-high aluminium fraction.

`b_P` and the piezoelectric bowings are UNSEEDED — `alloy-polarization-bowing-unseeded`. Until they
are seeded, mid-composition polarization-difference claims carry a widened uncertainty in
`combineTol`.

### Elastic constants

GPa. Gallium nitride is pinned to Polian and aluminium nitride to McNeil; the
surface-acoustic-wave aluminium-nitride set is excluded.

| Quantity | GaN | AlN | source |
|---|---|---|---|
| C₁₁/C₁₂/C₁₃/C₃₃/C₄₄ | 390/145/106/398/105 | 410.5/148.5/98.9/388.5/124.6 | Polian JAP 79 (1996); McNeil JACerS 76 (1993) |
| bulk modulus; density (g/cm³) | 210; 6.15 | 210; 3.23 | Ioffe NSM archive |
| aluminium-gallium-nitride interpolation | linear Vegard within 4.7% bowing, largest on C₄₄, **except C₁₃, which is superlinear in composition** — `elastic-tensors.csv` carries the rule. **C₁₃ is the weak link**: it has the largest experiment-against-experiment and experiment-against-theory spread, and it is the constant the piezoelectric and elastic-stability paths are most sensitive to | — | Łopuszyński arXiv 1110.1346 |

### Carrier transport coefficients

| Quantity | GaN | AlN | source |
|---|---|---|---|
| Caughey-Thomas electron quartet — max / min / N_ref / α | 1460.7 / 295 / 1e17 / 0.66 | **UNSEEDED** — paywalled | Farahmand IEEE TED 48 (2001) |
| Caughey-Thomas hole quartet — max / min / N_ref / γ | 170 / 10 / 2.5e17 / 1.5 | **UNSEEDED** — genuine absence | Mnatsakanov SSE 47 (2003) |
| first-principles mobility ceiling, electron / hole, 300 K | 1034 / 52 | 871 perpendicular / 619 parallel, electron | Poncé PRB 100 (2019); Wang arXiv 2506.09240 (2025) |
| Fröhlich coupling; ω_LO | 0.40; 92 meV | 0.58; 110–114 meV | Mora-Ramos cond-mat/9812021; Davydov PRB 58 12899 (1998) |
| Debye temperature | ~600 K | ~1000 K, measured 971 | Slack; Zheng PRMat 3 014601 (2019); Wang Powder Diffr. 29(4) 352 (2014) |
| alloy disorder potential; mobility minimum | 1.8 eV; minimum at x≈0.5–0.6, about 7× below gallium nitride | — | Pant APL 121 (2022) |
| alloy conductivity dip | minimum at x≈0.6–0.71; dilute −46.5% for 1% aluminium into gallium nitride, −75.8% for 1% gallium into aluminium nitride | — | Dagli, Mengle & Kioupakis arXiv 1910.05440 (2019) |

## What the seeded values rest on

179 rows sit in the five reference files. **24 of them carry a `Source` cell that names no
author and no year.** Not all 24 are defects, and they are not all the same kind of thing.
This section states what each rests on. It changes no value: the reference files stay
canonical for the values and for the `Source` cells themselves.

**The rule.** A row whose provenance does not resolve is not wrong — it is *unknown*, and
the word for that is `UNSEEDED`. A value carried forward because it has always been there
is the failure this section exists to prevent.

**Declared absences — the mechanism working.** Aluminium-nitride hole mobility is a
genuine absence: the acceptor is deep and the equilibrium hole density is below
`10¹⁰ cm⁻³`. Its electron Caughey-Thomas quartet is a declared acquisition task, paywalled
rather than missing. The β-Ga₂O₃ electron quartet has no consensus published fit. These
three rows are `UNSEEDED` by design and the cert refuses on them, which is correct.

**Resolves inside the corpus — no acquisition needed.**

| Row | Material | Rests on |
|---|---|---|
| `frohlich-alpha` | AlN | its own inputs — two rows of `phonon-frequencies.csv`, both citing Davydov PRB 58 12899 (1998) with a DOI |
| `bulk-modulus` | AlN | derivable from the McNeil elastic constants already in `elastic-tensors.csv` |
| `mass-density` | β-Ga₂O₃ | crystallographic, from the cell of Åhman, Svensson & Albertsson, Acta Cryst. C52 1336 (1996) |
| `mass-density` | diamond | crystallographic, from the lattice constant below and the standard atomic weight: `ρ = 8M/(N_A a³)` gives 3.5157 g/cm³. The atomic weight matters at this precision — natural abundance gives 3.5157, pure carbon-12 gives 3.5125 |

**Resolved to named literature.**

| Row | Material | Source |
|---|---|---|
| `debye-temperature` | AlN | Wang et al., *Powder Diffr.* **29**(4) 352 (2014), DOI 10.1017/S0885715614000542 |
| `lattice-constant-a` | diamond | Hom, Kiszenick & Post, *J. Appl. Cryst.* **8** 457 (1975) — `a = 3.566986 Å` at 25 °C, relative uncertainty 2.6×10⁻⁶. The seeded ±0.001 Å is about 400× looser than the measurement |
| `bandgap-indirect` | diamond | Clark, Dean & Harris, *Proc. R. Soc. Lond. A* **277** 312 (1964), the origin of the 5.47 eV figure. A modern re-measurement of the phonon-assisted absorption edge, *Diamond Relat. Mater.* **132** 109638 (2022), reports 5.480 ± 0.004 eV near 0 K; whether that agrees with a 5.47 eV 300 K value at the stated ±0.01 depends on the shift between those temperatures, which is what that paper re-measured |
| `phonon-max-energy` | diamond | Solin & Ramdas, *Phys. Rev. B* **1** 1687 (1970) — the zone-centre Raman mode at 1332.5 cm⁻¹, which is 165.21 meV. **The row is named for the dispersion maximum and this is the zone-centre value**, and diamond's longitudinal optical branch overbends: Kulda et al., *Phys. Rev. B* **66** 241202 (2002) measure the overbending at 1.5 meV along Γ–X, so the true maximum is near 166.7 meV, three times the row's stated uncertainty above its value |
| `formation-energy-vs-graphite` | diamond | Berman & Simon, *Z. Elektrochem.* **59** 333 (1955). The eponym resolves, but their line is a pressure-temperature boundary stated valid above 1200 K, and the row is a 300 K energy — a derivation, not a quotation. The three defensible readings differ by more than the stated ±5 meV/atom: the standard enthalpy difference is 19.6, the Gibbs difference 30.1, and the boundary line through `P·ΔV` gives 29.8 |
| `cohesive-energy` | diamond | Brewer, LBL-3720, through the standard textbook table. **The trail may point at the wrong allotrope** — `diamond-cohesive-energy-allotrope` |
| `mobility-electron-best-exp` | β-Ga₂O₃ | four primaries, three matching exactly: Zhang APL 112 173502 (2018) for the two-dimensional gas at 180; Zhang APL Materials 7 022506 (2019) for 176 by vapour-phase epitaxy; Peterson APL 125 182103 (2024) for 200 in a doped drift layer; Galazka J. Cryst. Growth 529 125297 (2020) for bulk Czochralski at 80–152, where 152 is the top of a range rather than a headline |
| `bulk-modulus`, `mass-density` | AlN, GaN | the Ioffe NSM archive — a real database, named without a locator, and one that names no primary reference of its own |

**Method stated where a source belongs.** Four rows carry a *method* in the `Source`
cell. A method says how a number was made, not what it can be checked against.

| Row | Material | What the cell says |
|---|---|---|
| `thermal-conductivity` at 773 and 1100 K | AlN | three-phonon Boltzmann with a Slack extrapolation, theory-only. The 1100 K cell adds that no single-crystal measurement above 500 K exists — `aln-high-temperature-conductivity-absence` |
| `pyroelectric-coefficient` | GaN | first-principles plus heterostructure measurements, thin data |
| `displacement-threshold-Ed` | β-Ga₂O₃ | `literature`, carried from an appendix that states the value as a bare parenthetical with no citation. The modern literature reports this quantity **per site** — two inequivalent gallium and three inequivalent oxygen sites — with a strong dependence on recoil direction (He et al., *Acta Mater.* **276** 120087 (2024)), so a single scalar is a modelling choice rather than a measurement |
| `thermal-conductivity` at 773 and 1100 K | diamond | an internal audit pointer — `diamond-thermal-conductivity-provenance` and `diamond-thermal-conductivity-citation-material` |

**UNSEEDED — no source found.** Two diamond rows, and neither is minor.

| Row | Value | Why it is UNSEEDED |
|---|---|---|
| `dielectric-static` | 5.7 ± 0.05 | every trail ends in an unreferenced compilation. It feeds image-force lowering in regime row 31 — `diamond-static-permittivity-unseeded` |
| `debye-temperature` | 2200 K ± 50 | no single source, and the literature spread runs about 1860–2230 K **by method**, so the stated uncertainty is narrower than the disagreement between methods. It sets the four-phonon validity window the 773 K conductivity anchor depends on — `diamond-debye-temperature-unseeded` |

## Residue

Cert-refused or frontier until provenanced.

- Diamond electron and hole impact-ionization coefficients have never been separated;
  the cert treats the single pair as both.
- Aluminium nitride: measured impact ionization is absent, with only an electron-only
  Monte-Carlo value; hole impact ionization is absent; the electron Caughey-Thomas
  quartet is paywalled; hole mobility is a genuine absence.
- β-Ga₂O₃ hole impact ionization is absent, and refusing it is correct
  ([out-of-scope#exclusions]).
- The normalized breakdown-field temperature coefficient in K⁻¹ is absent for gallium
  nitride and aluminium nitride — only a device breakdown-voltage slope exists. Its sign
  is confirmed positive.
- The perpendicular Born charge and the sign of `e₁₅` are unresolved; the literature is
  split on the sign.
- The per-host, per-particle non-ionizing energy-loss cross-section (registry row 112)
  and the recombination efficiency as a function of lattice temperature have no closed
  form.
- Boltzmann and Monte-Carlo anchors for the hot-carrier distribution tail are absent, so
  the III-nitride tail correction ships as identity.

## How ledger values reach the residual budget

Each `ResidualGenerator` carries a `characteristic-scale` field seeded from this ledger
([residual-definitions]), and `Quantity.combineTol` composes them along the DAG, by
maximum absolute value or in quadrature per [typeclass-alphabet].

A compression plan's truncation carries a **per-plan error target** that also enters
`combineTol` ([compose-time-pipeline]), so an emitted residual's budget includes
model-form, truncation and dressing-staleness terms — not just the input uncertainty.

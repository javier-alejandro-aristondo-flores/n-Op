# Wave-2 seeding spec — β-Ga₂O₃ (+ III-N polarization riders)

**Status: draft for adversarial audit — CSV seeding does NOT land until the audit pass clears it**
(the Wave-1 gate: two adversarial auditors, one on convention traps, one on numbers/provenance/gaps;
`docs/audits/2026-06-10-wave1-iii-n-audit.md` is the pattern). Web-verified sources are tagged
**[verified]** (located and cross-checked 2026-07-08); values recorded from expert knowledge that the
audit must pin to primary sources are tagged **[audit-pin]**. Scope: β-Ga₂O₃ per-material package on
the Wave-1 schema, plus the two III-N riders the 2026-07 gap-audit opened (pyroelectric coefficients,
B1; polarization bowing, B3). Diamond battery: landed (gap-audit Phase 3). c-BN / 4H-SiC: Wave 3.

## §1 Conventions & traps (read before any value)

1. **Centrosymmetric-but-polar — the predicate split (LANDED with this spec).** β-Ga₂O₃ is
   monoclinic **C2/m (space group 12): centrosymmetric ⇒ no spontaneous polarization, no
   piezoelectricity, no pyroelectricity** — rows 113–119/128 are inert here. Yet it is **strongly
   polar-phonon**: a massive multi-mode Fröhlich interaction is its *dominant mobility limiter*
   (μ < 200 cm²/Vs at 300 K despite a GaN-like m*; Ma 2016 **[verified]**). This splits the old
   `is-polar-material` conflation into two predicates — `is-polar-material` (Born charges / LO–TO;
   gates Fröhlich/POP) vs `is-noncentrosymmetric` (piezo classes; gates rows 113–119/128) — now
   normative in `arch-13-applicability`. **Wave-2 numbers must never be filtered through the old
   single-predicate assumption.**
2. **Direction tags are mandatory on every anisotropic row.** Monoclinic anisotropy is large
   (κ[010]/κ[100] ≈ 2.5; α_ii direction-resolved; polarized absorption onsets spread ~0.4 eV).
   Every κ / α_ii / onset / ε row carries `[100]`, `[010]`, `[001]`, or a polarization tag in
   `Environment` or `Material`. Cartesian frame for tensors: the RUS elastic frame (x∥a, y∥b,
   z∥c*) — state it wherever a C_ij or ε tensor component is quoted.
3. **Gap bookkeeping.** The fundamental gap is *indirect* by a few tens of meV with the direct gap
   at Γ almost degenerate ("quasi-direct"); the *measured absorption onset is
   polarization-dependent* (E∥c ≈ 4.5–4.6 eV, E∥b ≈ 4.8–4.9 eV). Seed the effective RT gap
   ≈ 4.85 eV **and** the polarized onsets as separate rows; never average them.
4. **ZPR `slope-kind` (closes the ledger's ⚠).** The −200 meV ZPR entry was tagged
   `total (⚠ Wave-2: verify)`. Preliminary verdict from the 2026 first-principles+MLIP study
   **[verified — arXiv 2603.29484]**: ZPR ≈ −0.2 eV, gap shrinks ≈ −0.45 eV by 700 K, and **lattice
   thermal expansion / anharmonicity contribute only minorly** over 0–900 K ⇒ the slope is
   **e-ph-dominated → retag `isochoric`** (composes freely with row 63). The adversarial audit
   must confirm against APL Mater. 11 011106 (2023) **[verified — exists]** before the ledger flips.
5. **Hole physics = polarons, by design refusal.** Valence bands are flat; holes self-trap (STH)
   with sub-band-gap UV luminescence (~3.2–3.6 eV) and no band-like p-transport. The existing
   cert-refuse stance (arch-17 "polaron localization beyond Fröhlich"; ledger: "holes never
   measured") is the correct disposition — **do not seed hole mobility, hole α_ii, or a p-type
   Caughey–Thomas set; cert-refuse instead.** PL channel note: row 134's B_rad applies to the STH
   emission, not band-edge PL (there is essentially none).
6. **Fröhlich is multi-mode.** The interaction is dominated by *low-energy* polar modes (not the
   highest LO): a single-α_F shorthand fits β-Ga₂O₃ poorly. The `KernelExt.Parametric` slot for
   the Fröhlich channel should carry the multi-mode (Verdi–Giustino-form) parameter set — mode
   energies + mode-resolved coupling — rather than one α_F **[audit-pin: mode table]**.

## §2 β-Ga₂O₃ seed tables (value · σ · source · class)

*Structure (space group C2/m, #12):*

| Quantity | Value | σ | Source | Class |
|---|---|---|---|---|
| a; b; c | 12.214; 3.037; 5.798 Å | 0.005; 0.002; 0.002 | Åhman/Geller structure refinements **[audit-pin exact ref]** | experimental |
| β (monoclinic angle) | 103.83° | 0.05° | same | experimental |
| ρ | 5.95 g/cm³ | 0.02 | standard | experimental |

*Electronic:*

| Quantity | Value | σ | Source | Class |
|---|---|---|---|---|
| E_g effective (RT) | 4.85 eV | 0.10 | absorption/ellipsometry consensus **[audit-pin]** | experimental-review |
| onset E∥c / E∥b | ≈4.55 / ≈4.88 eV | 0.05 | polarized absorption **[audit-pin]** | experimental |
| m*_e | 0.28 m₀ (near-isotropic) | 0.02 | DFT+ARPES consensus **[audit-pin]** | experimental-review |
| ε_∞ | ≈3.6 | 0.1 | optical **[audit-pin per-axis]** | experimental |
| ε_0 | ≈10–12 (direction-dependent) | per-axis | **[audit-pin per-axis]** | experimental |
| ZPR (isochoric-dominant, §1.4) | −0.20 eV | 0.05 | arXiv 2603.29484 (2026) **[verified]**; APL Mater. 11 011106 (2023) **[verified]** | dft-mlip |
| ΔE_g(700 K) − E_g(0) | −0.45 eV | 0.10 | arXiv 2603.29484 **[verified]** | dft-mlip |

*Elastic (all 13 monoclinic constants — complete RUS determination; frame x∥a, y∥b, z∥c*):*

| C_ij (GPa) | Value ± σ | | C_ij (GPa) | Value ± σ |
|---|---|---|---|---|
| C₁₁ | 242.8 ± 2.9 | | C₂₃ | 70.9 ± 2.1 |
| C₂₂ | 343.8 ± 3.8 | | C₁₅ | −1.62 ± 0.05 |
| C₃₃ | 347.4 ± 2.5 | | C₂₅ | 0.36 ± 0.01 |
| C₄₄ | 47.8 ± 0.2 | | C₃₅ | 0.97 ± 0.03 |
| C₅₅ | 88.6 ± 0.5 | | C₄₆ | 5.59 ± 0.69 |
| C₆₆ | 104.0 ± 0.5 | | | |
| C₁₂ | 128.0 ± 0.1 | | | |
| C₁₃ | 160.0 ± 1.5 | | | |

Source: resonant ultrasound spectroscopy + laser-Doppler interferometry, "Unusual elasticity of
monoclinic β-Ga₂O₃", JAP 124 085102 (2018) **[verified]**. Notable anisotropy: C₁₁ ≈ 30% below
C₂₂/C₃₃; C₄₄ vs C₆₆ differ >50% — Born-stability check must use the full monoclinic criteria
(row 57 generalizes; **not** the cubic reduced set).

*Phonon / thermal:*

| Quantity | Value | σ | Source | Class |
|---|---|---|---|---|
| κ[010] (300 K) | 27.0 W/mK | 2.0 | Guo et al. APL 106 111909 (2015) **[verified]** | experimental (TDTR) |
| κ[100] (300 K) | 10.9 W/mK | 1.0 | Guo 2015 **[verified]**; Handwerg 2015 concurs (29±2 / 11±1) **[verified]** | experimental |
| κ[001] (300 K) | ≈15 W/mK | 1.5 | Guo 2015 **[audit-pin exact value]** | experimental |
| κ(T) high-T | ~1/T (Umklapp) to ≥495 K; tensor to 1275 K exists | — | Guo 2015 **[verified]**; Cryst. Res. Technol. 2022 tensor study **[verified — audit extracts 773/1100 K anchors]** | experimental |
| Θ_D | ≈740 K | 150 (literature spread 420–870) | **[audit-pin; spread is real — record the spread]** | mixed |
| phonon modes | 30 branches (10-atom primitive cell); IR-active A_u/B_u set; dominant Fröhlich modes at low energy | — | Ma 2016 / phonon studies **[audit-pin mode table for the KernelExt]** | dft-dfpt |

*Transport / high-field:*

| Quantity | Value | σ | Source | Class |
|---|---|---|---|---|
| μ_n POP ceiling (300 K, n<10¹⁸) | <200 cm²/Vs | ×0.2 | Ma et al. APL 109 212101 (2016) **[verified]** | theory (POP-limited) |
| μ_n BTE @ n=1.1×10¹⁷ | ≈115 cm²/Vs | ×0.25 | Ghosh & Singisetti (ab-initio BTE) **[verified]** | first-principles-bte |
| μ_n best measured (300 K) | ≈130–180 cm²/Vs | range | **[audit-pin]** | experimental |
| v_sat | 1–2×10⁷ cm/s (direction-dependent) | ×0.3 | full-band MC **[audit-pin per-direction]** | monte-carlo |
| α_ii(E) electron, per direction | Chynoweth fits per [100]/[010]/[001], fields to 8 MV/cm | ×3 | Ghosh & Singisetti JAP 124 085707 (2018) **[verified — audit extracts the three (a,b) pairs]** | monte-carlo |
| α_ii hole | **cert-refused** (never measured; STH) | unbounded | ledger residue | gap |
| E_c theoretical | ≈8 MV/cm | ×0.15 | Ghosh–Singisetti 2018 **[verified]**; device-measured lower | monte-carlo |
| C–T quartet (μ_max/μ_min/N_ref/α) | **GAP — no consensus fit**; derive from published μ(N_D) or acquire | — | acquisition item | gap |
| E_d (radiation) | ≈25 eV | ±5 | non-eq H.1 (already carried) | literature |

*Defect inventory pointers (for the future defect-formation-energies.csv; host row already in
`arch-21 §21.2.1`):* V_O(I/II/III) are **deep donors** (~1 eV+) — *not* the n-type source (Si/Sn
shallow donors are); V_Ga deep acceptors (multiple charge states); STH self-trapping energy
~0.5 eV **[audit-pin: Varley et al. — V_O deep-donor APL 2010-class + STH PRB 85 081109(R)
(2012)-class citations]**.

## §3 III-N riders (gap-audit B1/B3 coefficients)

*Pyroelectric coefficients (row 128; sign convention: record `p = dP_sp/dT` in the same
ZB-proper frame as rows 113–114 — the measured pyro response has |P_sp| decreasing toward zero
with rising T; the audit must fix the sign in the ZB-reference frame before seeding):*

| Material | p (μC/m²K) | σ | Source | Class |
|---|---|---|---|---|
| AlN | ≈3.0 (measured, 6–12 μm epilayers); reports up to ~6–8 | ×0.5 | Temperature dependence of the pyroelectric coefficient of AlN **[verified — exists; audit-pin exact ref]** | experimental |
| GaN | ≈4–5 (first-principles + heterostructure measurements; thinner data) | ×0.5 | first-principles pyroelectricity studies **[audit-pin]** | dft |
| impact | ΔP over ΔT≈750 K ≈ 2–4×10⁻³ C/m² vs n_s·q ≈ 1.6×10⁻² ⇒ **~15–25% n_s(T) drift** | — | vs the ±5% ΔP target | — |

Secondary (thermal-expansion-mediated) pyroelectricity grows above ~100 K and dominates at the
operating point — the seeded `p` must be the **total (primary+secondary) coefficient at fixed
stress**, which is what the epilayer measurements give **[verified — T³ primary → secondary
crossover ~100 K for AlN]**.

*Polarization bowing (B3; rows 113–114 interpolation rule in `accuracy-ledger`):*

| Quantity | Form / value | Source |
|---|---|---|
| P_sp(Al_xGa₁₋ₓN) | `x·P_AlN + (1−x)·P_GaN + b·x(1−x)`, b ≈ +0.019…0.021 C/m² **[audit-pin exact b + sign convention against the ZB-proper frame]** | Fiorentini & Bernardini PRB 64 085207 (2001) **[verified]** — **plus the published Erratum PRB 65 129903 (2002); the audit MUST read the erratum before seeding** |
| deviations from parabolic | ≲10% (worst case AlInN; smaller for AlGaN) | PRB 64 085207 **[verified]** |
| e_ij(x) piezo | nonlinear in *strain* (bulk response), disorder-independent — parameterize e(x, ε) per FB's prescription | PRB 64 085207 **[verified]** |
| modern cross-check | off-axis electron-holography quantification of polarization bowing (PRB, recent) **[verified — exists; audit-pin]** | — |

## §4 GAP register (genuine; carried, not hidden)

AlGaN-analog alloying ((Al_xGa₁₋ₓ)₂O₃) — out of Wave-2 scope, note for a later wave; hole
transport / hole α_ii — cert-refused (STH), by design; C–T quartet — no consensus fit
(acquisition or fit-from-published-μ(N_D)); per-axis ε₀ — pin; Θ_D — genuine literature spread,
record as spread; κ(773/1100 K) anchors — extract from the 2022 tensor study; Fröhlich mode
table for the multi-mode KernelExt — assemble from DFPT phonon studies; pyro-GaN measured value —
thin data, may stay `dft`-class; e_ij(x) bowing numbers — from FB01 + erratum.

## §5 Landing plan

1. Adversarial audit (two auditors, Wave-1 mandate: refute). Special attention: the FB **erratum**,
   the ZPR slope-kind retag, the pyro sign convention in the ZB-proper frame, per-direction α_ii
   extraction, and every **[audit-pin]** tag above.
2. On clear: seed `material-constants` / `elastic-tensors` / `phonon-frequencies` /
   `transport-coefficients` rows for β-Ga₂O₃ (direction-tagged), the III-N pyro/bowing
   coefficients, retag the ledger's Ga₂O₃ ZPR row, and update the ledger κ(T)/high-field tables.
3. Registry: no new rows needed — Wave 2 is coefficients + gates (the predicate split landed with
   this spec: `arch-13`, `arch-09 §9.3`, row 128's note).

## §6 Sources (verified this pass)

- Guo et al., "Anisotropic thermal conductivity in single crystal β-gallium oxide", APL 106
  111909 (2015) — κ[010]=27.0±2.0, κ[100]=10.9±1.0 W/mK, ~1/T.
- Handwerg et al. (2015) — κ[010]=29±2, κ[100]=11±1 (concurring).
- "The Thermal Conductivity Tensor of β-Ga₂O₃ from 300 to 1275 K", Cryst. Res. Technol. (2022) —
  high-T anchors source.
- Ma et al., "Intrinsic electron mobility limits in β-Ga₂O₃", APL 109 212101 (2016) — POP-limited
  μ<200; massive Fröhlich despite GaN-like m*.
- Ghosh & Singisetti, "Impact ionization in β-Ga₂O₃", JAP 124 085707 (2018) — anisotropic α_ii to
  8 MV/cm, three direction sets; also their ab-initio BTE mobility (≈115 @ 1.1×10¹⁷).
- "Unusual elasticity of monoclinic β-Ga₂O₃", JAP 124 085102 (2018) — all 13 C_ij by RUS+LDI.
- "Electron–phonon effects and temperature-dependence of the electronic structure of monoclinic
  β-Ga₂O₃", APL Mater. 11 011106 (2023) — the ledger's flagged e-ph source.
- arXiv 2603.29484 (2026) — ZPR ≈ −0.2 eV; −0.45 eV by 700 K; thermal-expansion contribution minor
  (slope-kind evidence).
- Fiorentini & Bernardini, "Nonlinear macroscopic polarization in III-V nitride alloys", PRB 64
  085207 (2001) + **Erratum PRB 65 129903 (2002)**.
- AlN pyroelectric-coefficient measurement (6–12 μm epilayers, p≈3.0 μC/m²K; primary→secondary
  crossover ~100 K) — exact reference pinned at audit.

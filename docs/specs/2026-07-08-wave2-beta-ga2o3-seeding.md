# Wave-2 seeding spec — β-Ga₂O₃ (+ III-N polarization riders)

**Status: ADVERSARIALLY AUDITED 2026-07-16 — β-Ga₂O₃ package + III-N pyro rider (B1) CLEARED
and seeded; III-N bowing rider (B3): gate texts READ 2026-07-16 (FB Erratum: P_sp bowing
untouched; "Ebert" = Lan et al. PRB 113 155302, CC-BY, InGaN-only) — seeding pends the
mandated FBA APL 80 1204 (2002) / Ambacher JPCM 14 3399 (2002) pin-read.** Audit register:
`docs/audits/2026-07-16-wave2-beta-ga2o3-audit.md`
(two auditors on the Wave-1 mandate; all value/provenance corrections applied **in place**
below — the tables now carry the audited values). Historical note: drafted 2026-07-08 with
**[verified]** / **[audit-pin]** tags; pins are resolved below except the two G1/G2
acquisition items. Scope: β-Ga₂O₃ per-material package on the Wave-1 schema, plus the two
III-N riders the 2026-07 gap-audit opened (pyroelectric coefficients, B1; polarization
bowing, B3). Diamond battery: landed (gap-audit Phase 3). c-BN / 4H-SiC: Wave 3.

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
   (κ[010]/κ[100] ≈ 2.5; α_ii direction-resolved; polarized absorption onsets spread ~0.3 eV).
   Every κ / α_ii / onset / ε row carries `[100]`, `[010]`, `[001]`/`c*`, or a polarization tag
   in `Environment` or `Material`. Cartesian frame for tensors: the RUS elastic frame (x∥a,
   y∥b, z∥c*) — state it wherever a C_ij or ε tensor component is quoted. **Audit finding:
   the Ghosh–Singisetti high-field axes are a / b / c\* (c\* is 13.83° from [001]) — α_ii and
   E_c rows are tagged c\*, never [001].** Klimm's κ tensor (full text read post-audit — open
   access) is in the crystal-physical frame **e₂∥b, e₃∥c, e₁ = a\*** (⊥ c in the ac-plane):
   λ₂₂ ≡ [010] *and* λ₃₃ ≡ [001] coincide with crystallographic-direction rows; λ₁₁ is along
   a\* (13.83° from [100]), and the direct plane-normal measurements λ₍₁₀₀₎/λ₍₀₀₁₎ are along
   a\*/c\* — never relabel those as [100]/[001].
3. **Gap bookkeeping.** The fundamental gap is *indirect* by a few tens of meV with the direct gap
   at Γ almost degenerate ("quasi-direct"); the *measured absorption onset is
   polarization-dependent* (E∥c ≈ 4.5–4.6 eV, E∥b ≈ 4.8–4.9 eV). Seed the effective RT gap
   ≈ 4.85 eV **and** the polarized onsets as separate rows; never average them.
4. **ZPR `slope-kind` (ledger ⚠ CLOSED at audit).** Audited verdict (Arabov et al. arXiv
   2603.29484 read in full; cross-confirmed Lee et al. APL Mater. 11 011106 (2023),
   −0.19±0.05 eV): the ZPR = −0.20±0.01 eV is a clamped-cell harmonic-sampling value —
   genuinely **isochoric** e-ph (same class as the III-N Engel/Miglio entries); thermal
   expansion contributes only minorly to the gap renormalization over 0–900 K. Ledger
   retagged `isochoric`. **Refinement:** the −0.45 eV shift at 700 K is the *total*
   (expansion included) — the isochoric tag rides the ZPR amplitude only, else row 63
   double-counts the strain term.
5. **Hole physics = polarons, by design refusal.** Valence bands are flat; holes self-trap (STH)
   with sub-band-gap UV luminescence (~3.2–3.6 eV) and no band-like p-transport. The existing
   cert-refuse stance (arch-17 "polaron localization beyond Fröhlich"; ledger: "holes never
   measured") is the correct disposition — **do not seed hole mobility, hole α_ii, or a p-type
   Caughey–Thomas set; cert-refuse instead.** PL channel note: row 134's B_rad applies to the STH
   emission, not band-edge PL (there is essentially none).
6. **Fröhlich is multi-mode.** The interaction is dominated by *low-energy* polar modes (not the
   highest LO): a single-α_F shorthand fits β-Ga₂O₃ poorly for T-dependent transport
   (Ghosh & Singisetti JAP 122 035702 (2017) / JAP 124 085707 (2018); Ma et al. 2016 used a
   single effective α_F ≈ 1.68 at ℏω ≈ 44 meV for the 300 K ceiling only). The
   `KernelExt.Parametric` slot for the Fröhlich channel carries the multi-mode
   (Verdi–Giustino-form) parameter set — **pinned at audit: Mengle & Kioupakis, AIP Advances
   9 015313 (2019), Table I** (12 IR-active modes, TO + directional LO along a/b/c; dominant
   e-ph mode at 29 meV); assembly into the KernelExt remains research-side work.

## §2 β-Ga₂O₃ seed tables (value · σ · source · class)

*Structure (space group C2/m, #12):*

| Quantity | Value | σ | Source | Class |
|---|---|---|---|---|
| a; b; c | 12.214; 3.037; 5.798 Å | 0.005; 0.002; 0.002 | Åhman, Svensson & Albertsson, Acta Cryst. C52 1336 (1996), 10.1107/S0108270195016404 (pinned at audit; Geller 1960 is the older determination) | experimental |
| β (monoclinic angle) | 103.83° | 0.05° | same | experimental |
| ρ | 5.96 g/cm³ | 0.02 | crystallographic density from the Åhman cell (Z=4) — derived, not "standard" | derived-experimental |

*Electronic:*

| Quantity | Value | σ | Source | Class |
|---|---|---|---|---|
| E_g effective (RT) | 4.85 eV | 0.10 | absorption/ellipsometry consensus (Ricci et al. JPCM 28 224005 (2016) compilation) | experimental-review |
| onset E∥c / E∥b | 4.55 / 4.80 eV | 0.08 / 0.12 | polarized absorption — audited spread: E∥c ∈ 4.50 (Matsumoto 1974) … 4.59 (Onuma APL 108 (2016)); E∥b ∈ 4.65 … 4.90 (Ueda 1997 gives 4.79); σ widened to cover the spread | experimental |
| m*_e | 0.284 m₀ (near-isotropic) | 0.013 | mid-IR optical Hall — Knight et al. APL 112 012103 (2018) (audit corrected the "DFT+ARPES" label) | experimental |
| ε_∞ | ≈3.6 | 0.1 | Schubert et al. PRB 93 125209 (2016), per-axis 3.5–3.7 | experimental |
| ε_0 ⊥(100)/⊥(010)/⊥(001) | 10.2 / 10.87 / 12.4 | 0.2 / 0.08 / 0.4 | J. Solid State Sci. Technol. 8 Q3083 (2019), 10.1149/2.0201907jss (pinned at audit — moved out of the GAP register) | experimental |
| ZPR (isochoric, §1.4) | −0.20 eV | 0.05 | Arabov et al. arXiv 2603.29484 (2026); Lee et al. APL Mater. 11 011106 (2023) −0.19±0.05 | dft-mlip |
| ΔE_g(700 K) − E_g(0) (total, §1.4) | −0.45 eV | 0.10 | Arabov et al. arXiv 2603.29484 (2026) | dft-mlip |

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
| κ[010] (300 K) | 27.0 W/mK | 2.0 | Guo et al. APL 106 111909 (2015), TDTR, 80–495 K, ~1/T^1.1–1.3; Klimm λ₂₂ = 24.26 (principal-axis, laser-flash) concurs ~10% | experimental (TDTR) |
| κ[100] (300 K) | 10.9 W/mK | 1.0 | Guo 2015; Handwerg SST 30 024006 (2015), 3ω, measured [100] only: 13±1 (audit corrected the earlier "concurs (29/11)" parenthetical — those were not Handwerg values) | experimental |
| κ[001] (300 K) | 14 W/mK | 1.5 | Guo 2015 Table-I fit (8140/300^1.12 ≈ 13.7; Fig. 2b reads ≈14) — audit corrected from ≈15 | experimental |
| κ(T) high-T | ~1/T^m (m≈1.0–1.2) to 1200 K; **derived anchors seeded: κ[010](773 K) ≈ 9 ± 2, κ[010](1100 K) ≈ 6 ± 1.5 W/mK** (λ₂₂(300)=24.26 direct × the paper's own T^−m law) | 2 / 1.5 | Guo 2015; Klimm et al. Cryst. Res. Technol. **58** 2200204 (**2023**), 10.1002/crat.202200204 — **open access (Projekt DEAL; archival copy d-nb.info/1274779782/34), full main text read 2026-07-16 → G2 closed**; 300 K tensor: λ₁₁ 12.13 (a\*) / λ₂₂ 24.26 (b) / λ₃₃ 14.09 (c) / λ₁₃ −0.992; λ₍₀₀₁₎ 13.53 (c\*), λ₍₂̄₀₁₎ 14.33; min ≈11.73 near a; exact per-T SI tables = optional refinement | experimental + derived |
| Θ_D | 738 K | 150 (literature spread 420–870; central = Guo calorimetric Debye fit; upper endpoint = FP 872 K; lower endpoint unpinned) | Guo 2015; Mengle–Kioupakis 2019 concur ≈738 | mixed |
| phonon modes | 30 branches (10-atom primitive cell); 12 IR-active modes, TO + directional LO (a/b/c); dominant e-ph (Fröhlich) mode at 29 meV | — | **Mengle & Kioupakis, AIP Advances 9 015313 (2019), Table I** (the KernelExt mode table — pinned at audit; attribution corrected from Ma 2016) | dft-dfpt |

*Transport / high-field:*

| Quantity | Value | σ | Source | Class |
|---|---|---|---|---|
| μ_n POP ceiling (300 K, n<10¹⁸) | <200 cm²/Vs | ×0.2 | Ma et al. APL 109 212101 (2016), 10.1063/1.4968550 | theory (POP-limited) |
| μ_n BTE intrinsic (300 K, phonon-limited) | ≈115 cm²/Vs | ×0.25 | Ghosh & Singisetti APL 109 072102 (2016), Rode ab-initio (audit re-cited; density tie dropped) | first-principles-bte |
| μ_n best measured (300 K) | 150–200 cm²/Vs | range | bulk CZ 152 / MOCVD 176–~200 / 2DEG 180 (pinned at audit; upper end has crept to ~200) | experimental |
| v_sat | 1–1.5×10⁷ cm/s sat; peak ~2×10⁷ at ~200 kV/cm (direction-dependent) | ×0.3 | Ghosh & Singisetti JAP 122 035702 (2017), full-band MC | monte-carlo |
| α_ii(E) electron, per direction | Chynoweth (a, b): **a-axis 0.79×10⁶ /cm, 2.92×10⁷ V/cm · b-axis 2.16×10⁶, 1.77×10⁷ · c\*-axis 0.706×10⁶, 2.10×10⁷** (E_g = 4.9 eV; fields to 8 MV/cm; c\* is 13.83° from [001]) | ×3 | Ghosh & Singisetti JAP 124 085707 (2018), 10.1063/1.5034120, Table 1 (extracted at audit) | monte-carlo |
| α_ii hole | **cert-refused** (never measured; STH) | unbounded | ledger residue; Varley PRB 85 081109(R) (2012) | gap |
| E_c (ionization-integral, per direction) | **10.2 [a] / 4.8 [b] / 7.6 [c\*] MV/cm** at E_g = 4.9 eV (audit REFUTED the earlier scalar "≈8, Ghosh–Singisetti" — no such value in-paper; ≈8 is Higashiwaki SST 31 034001 (2016) bandgap-scaling / the max simulated field; device-measured lower) | ×0.3 | Ghosh–Singisetti 2018 Table 1 | monte-carlo |
| C–T quartet (μ_max/μ_min/N_ref/α) | **GAP — no consensus fit** (audit confirmed genuine); derive from published μ(N_D) or acquire | — | acquisition item | gap |
| E_d (radiation) | ≈25 eV | ±5 | non-eq H.1 (already carried) | literature |

*Defect inventory pointers (for the future defect-formation-energies.csv; host row already in
`arch-21 §21.2.1`):* V_O(I/II/III) are **deep donors** (~1 eV+) — *not* the n-type source (Si/Sn
shallow donors are); V_Ga deep acceptors (multiple charge states); STH self-trapping energies
−0.39/−0.46 eV (O_I/O_II sites). Pinned at audit: **Varley, Weber, Janotti & Van de Walle,
APL 97 142106 (2010), 10.1063/1.3499306 (+ Erratum APL 108 039901 (2016))** for V_O;
**Varley, Janotti, Franchini & Van de Walle, PRB 85 081109(R) (2012),
10.1103/PhysRevB.85.081109** for the STH.

## §3 III-N riders (gap-audit B1/B3 coefficients)

*Pyroelectric coefficients (row 128; sign FIXED AT AUDIT: the seeded ZB-ref P_sp values are
NEGATIVE and |P_sp| decreases toward zero with rising T ⇒ **p = dP_sp/dT is POSITIVE in the
seeded frame**. Trap: raw literature quotes p negative under the positive-P_s convention —
seed the positive value; a sign-guard note rides the CSV rows):*

| Material | p (μC/m²K, ZB-ref frame) | σ | Source | Class |
|---|---|---|---|---|
| AlN | +3.0 (6–12 μm epilayers / Debye analysis); thin-film reports 6–8 | ×2 (covers the 3→6–8 spread; the drafted "×0.5" was malformed under the σ convention) | Yan et al. APL 90 212102 (2007), 10.1063/1.2742589 (epilayer/Debye analysis; T³ primary regime) **+** Fuflyigin et al. APL 77 3075 (2000), 10.1063/1.1324726 (thin-film 6–8) — source split at audit | experimental |
| GaN | +4.5 (first-principles + heterostructure measurements; thinner data) | ×2 | first-principles pyroelectricity studies (data thin — stays dft-class per §4) | dft |
| impact | ΔP over ΔT≈750 K ≈ 2–4×10⁻³ C/m² vs n_s·q ≈ 1.6×10⁻² ⇒ **~15–25% n_s(T) drift** | — | vs the ±5% ΔP target | — |

Secondary-crossover physics confirmed at audit: primary (T³) → secondary transition ≈100 K for
AlN (GaN 70 K, InN 60 K, tied to AlN's <100 K negative thermal expansion); the epilayer
measurement gives the **total (primary+secondary) coefficient at fixed stress** — the correct
seed for the operating point.


*Polarization bowing (B3; rows 113–114 interpolation rule in `accuracy-ledger`) —
**GATE TEXTS READ 2026-07-16; seeding pends one pin** (audit finding G1; closure
dispositions in the audit register's §4): the FB Erratum corrects only the CuPt-ordered
In-alloy **piezoelectric** polarization — the P_sp bowing (FB01 Eq. 4–5 / Fig. 7) is
untouched, and CuPt-ordered AlGaN is Vegard-within-error; the holography paper is
**Lan et al. (Ebert group), PRB 113, 155302 (2026), CC-BY** and is **InGaN-only** —
nothing imports for AlGaN (corrected cross-check row below). The sign trap stands as
navigated: FB01's Eq-4/5 define `−b·x(1−x)` with b negative — "bowing always upward" — so
the `+b, b positive` form below is the same physics via double-negative. **B3 seeds on
the mandated primary read of FBA APL 80 1204 (2002) / Ambacher JPCM 14 3399 (2002)**
(the exact b: +0.019 vs +0.021 both circulate, and secondary quotes are demonstrably
corrupted — a 2026-07-16 web check surfaced the InGaN bowing misattributed to AlGaN).
The gate row rides in `polarization-piezoelectric.csv` until then.*

| Quantity | Form / value | Source |
|---|---|---|
| P_sp(Al_xGa₁₋ₓN) | `x·P_AlN + (1−x)·P_GaN + b·x(1−x)`, b ≈ +0.019…0.021 C/m² — exact b pins to FBA APL 80 1204 (2002) / Ambacher JPCM 14 3399 (2002) at the gated seeding (FB01's preprint gives only the ideal-structure AlInN chemical-only value) | Fiorentini & Bernardini PRB 64 085207 (2001), 10.1103/PhysRevB.64.085207 + **Erratum PRB 65 129903 (2002), 10.1103/PhysRevB.65.129903 — read in full 2026-07-16: corrects only CuPt-ordered In-alloy piezo (Fig.-6 k-mesh error); P_sp bowing untouched** |
| deviations from parabolic | ≲10% (worst case AlInN; smaller for AlGaN) | PRB 64 085207 |
| e_ij(x) piezo | nonlinear in *strain* (bulk response), disorder-independent — parameterize e(x, ε) per FB's prescription | PRB 64 085207 |
| modern cross-check | **Lan, Schnedler, Ji, Carlin, Butté, Grandjean, Dunin-Borkowski, Ebert — PRB 113, 155302 (2026), 10.1103/4rsc-ysk8, CC-BY (read in full 2026-07-16)** — off-axis electron holography, **InGaN-only** (x = 0.030–0.132 on GaN; ΔP_total = −0.00091±0.00034 … −0.0077±0.00135 C/m²). P_spon(InGaN) strongly nonlinear; **only the layered-hexagonal (Dreyer) reference matches the measured curvature — ZB-frame theory bows with the OPPOSITE curvature sign** (their Figs. 5–6), so curvature is **NOT** reference-invariant and the pre-read "import their b as a curvature on ZB-ref endpoints" path is moot for AlGaN (bowing also does not transfer across alloy systems) and unsound in general. LH-frame b(InGaN, x<0.25) = 0.382 ± 0.075 C/m²; full-range cubic b(x) = 0.105 − 0.238x; LH endpoints 1.299 (GaN) / 1.032 (InN). Contributes to B3 as a **guard**: experimentally confirms the ledger row-35 high-In InGaN/GaN cert-refusal (ZB curvature refuted for InGaN); AlGaN stays inside the ZB-consistent proper-e₃₁ family (2DEG-validated; AlGaN/GaN-only cancellation guard stays). In-hand primary source for a future In-wave. | — |

## §4 GAP register (post-audit; genuine, carried, not hidden)

AlGaN-analog alloying ((Al_xGa₁₋ₓ)₂O₃) — out of Wave-2 scope, note for a later wave; hole
transport / hole α_ii — cert-refused (STH), by design; C–T quartet — no consensus fit,
audit-confirmed genuine (acquisition or fit-from-published-μ(N_D)); Θ_D — genuine literature
spread, recorded as spread (central 738 K pinned); κ(773/1100 K) anchors — **G2 CLOSED
2026-07-16** (Klimm 2023 turned out open access via Projekt DEAL; derived [010] anchors
seeded from its direct 300 K tensor + its own T^−m law; exact SI tables optional); Fröhlich
multi-mode KernelExt —
source pinned (Mengle–Kioupakis 2019 Table I), assembly remains research-side; pyro-GaN
measured value — thin data, stays `dft`-class; e_ij(x) + P_sp bowing numbers — **G1 gate
texts read 2026-07-16; residual = the FBA APL 80 1204 / Ambacher JPCM 14 3399 pin-read**
(then B3 seeds). *Removed from the register at audit:* per-axis ε₀ (pinned to
JSST 8 Q3083 (2019) and seeded).

## §5 Landing plan — EXECUTED 2026-07-16

1. ✔ Adversarial audit (two auditors, Wave-1 mandate: refute) —
   `docs/audits/2026-07-16-wave2-beta-ga2o3-audit.md`. Conventions: CLEAR-WITH-PINS;
   numbers: BLOCK→fixed at adjudication (E_c triple + c* labels + six fixes, applied above).
2. ✔ Seeded: `material-constants` / `elastic-tensors` / `phonon-frequencies` /
   `transport-coefficients` β-Ga₂O₃ rows (direction-tagged, monoclinic frame stated), the
   III-N **pyro** coefficients (positive-p, sign-guarded); ledger Ga₂O₃ ZPR row retagged
   `isochoric`; ledger κ(T)/high-field tables updated. **NOT YET seeded: the B3 bowing
   rider — G1 gate texts read 2026-07-16; pin-read residual** (the gate row rides in
   `polarization-piezoelectric.csv` until the FBA/Ambacher read).
3. ✔ Registry: no new rows — Wave 2 is coefficients + gates (the predicate split landed with
   this spec: `arch-13`, `arch-09 §9.3`, row 128's note).
4. Open acquisitions (user): **G1 gate texts read 2026-07-16** (user-acquired FB Erratum;
   the "Ebert" paper — Lan et al., PRB 113, 155302 (2026) — turned out CC-BY, the
   audit-time 403 was a bot-block). Dispositions in the audit register's §4. **Residual:
   FBA APL 80 1204 (2002) / Ambacher JPCM 14 3399 (2002) full text** for the exact AlGaN
   b — no open copies exist (Semantic Scholar / OpenAlex / arXiv / UNICA-IRIS checked
   2026-07-16); user acquiring; B3 seeds on that read.
   ~~G2~~ **closed 2026-07-16**: Klimm 2023 is open access (Projekt DEAL; d-nb archival
   copy); derived κ[010] anchors seeded; exact SI tables remain an optional refinement.

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
  085207 (2001) + **Erratum PRB 65 129903 (2002) — erratum read in full 2026-07-16** (CuPt-ordered
  In-alloy piezo only; P_sp bowing untouched).
- Lan, Schnedler, Ji, Carlin, Butté, Grandjean, Dunin-Borkowski & Ebert, "Quantification of
  polarization bowing in III-nitrides by off-axis electron holography and impact on the
  polarization controversy", PRB 113, 155302 (2026), 10.1103/4rsc-ysk8 (CC-BY) — **read in full
  2026-07-16**; InGaN-only; LH-frame bowing b = 0.382 ± 0.075 C/m² (x < 0.25); ZB-frame curvature
  experimentally refuted for InGaN.
- AlN pyroelectric-coefficient measurement (6–12 μm epilayers, p≈3.0 μC/m²K; primary→secondary
  crossover ~100 K) — exact reference pinned at audit.

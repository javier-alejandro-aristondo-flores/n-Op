# Wave-1 per-material seeding — III-N flagships (GaN / AlN / Al_xGa_{1-x}N)

**Date:** 2026-06-10
**Scope:** Wave 1 of the per-material research phase. Seed the III-N flagship family
(wurtzite GaN, wurtzite AlN, the alloy Al_xGa_{1-x}N) across every coefficient family the
127-row formula registry consumes, to a fully sourced + adversarially-audited state — and
fix the in-repo errors the audit exposed. Diamond (the MVP) was already curated; β-Ga₂O₃
(Wave 2) and c-BN (Wave 3) are out of scope here.

**Method:** 2 read-only inventory agents → 6 primary-literature deep-dive agents (one per
coefficient family) → 2 adversarial auditors (conventions; numbers/provenance/gaps).
**Completeness gate honored:** every value carries a primary citation + σ, or is recorded as
an explicit `GAP — no reliable source`. No value was invented. Adversarial-audit verdicts:
`docs/audits/2026-06-10-wave1-iii-n-audit.md`.

---

## 1. Conventions (load-bearing — these are where silent errors live)

### 1.1 AHC zero-point renormalization: seed the ISOCHORIC value, tag `isochoric`

The `ahc-gap-renormalization` dressing (registry row 120, `ΔE_g(T)=ZPR·coth(Θ/2T)`) is a
**pure electron-phonon** quantity. The thermal/zero-point **lattice-expansion** part of the
gap shift is carried *separately* by the strain/deformation-potential path (registry row 63,
`Ξ·strain`). Therefore the ZPR coefficient seeded into the `coth` path must be the
**isochoric** (clamped-lattice) AHC value, tagged `isochoric`, which composes freely with
row 63. Seeding a `total` value (which already contains the expansion part) while row 63 is
active **double-counts** thermal expansion — the refusal in `arch-12 §12.0.3` guards exactly
this, so the tag must describe what the value actually contains.

- Engel et al. PRB 106 094316 (2022) Tbl VII and Miglio et al. npj Comput. Mater. 6 167
  (2020) Tbl S2 report **isochoric** AHC ZPR (fixed DFT-relaxed cell; no expansion term).
- Miglio reports the zero-point **lattice-expansion** term *separately*: GaN −49 meV,
  AlN −85 meV ⇒ totals GaN −238, AlN −484.
- **Prior in-repo error:** GaN −180 / AlN −385 / c-BN −400 / diamond −345 were all tagged
  `total` and sourced "Engel" — but Engel's numbers are isochoric, and GaN −180 was actually
  the experimental (Pässler) *total*, not Engel's −171. Value, tag, and source were mutually
  inconsistent. Fixed below.

### 1.2 III-N polarization: reference choice + proper/improper e₃₁ + self-consistent pairing

Spontaneous polarization is **reference-dependent**, so absolute P_sp is only ±10–20%, but
the **interface ΔP** that the 2DEG density n_s (row 115) consumes is ±5% for AlGaN/GaN — **not**
because of generic "reference ambiguity cancelling in differences," but because of a specific
**accidental cancellation** (Dreyer et al. PRX 6 021038 (2016) §V.D–E): the spurious
zinc-blende(ZB)-reference term in P_sp and the proper-vs-improper e₃₁ error are two large,
opposite-sign quantities that nearly cancel for AlGaN/GaN over the whole composition range.

This imposes a **self-consistent-pairing invariant** the spec must enforce (silent violation
corrupts n_s, because improper e₃₁ ≈ 3.4× proper for GaN/AlN):

> Use **exactly one** of two self-consistent conventions and never mix them:
> (a) **ZB-reference P_sp + PROPER e₃₁ + no ZB-correction term** (the spec's path), or
> (b) layered-hexagonal-reference P_sp + ΔP_corr + **improper** e₃₁.

The spec seeds BFV/ZB-reference P_sp, so it **must** pair with **proper** e₃₁ (BFV's tabulated
e₃₁ are proper) and must **not** add a ZB correction. A machine-checkable cert tag enforces this
(`arch-12 §12.0.3`, new fourth refusal).

**Scope guard:** the ±5%-ΔP cancellation is **AlGaN/GaN-specific**; it **fails for high-In
InGaN/GaN** (large mismatch, incomplete cancellation — Dreyer §V.E). The ±5% claim carries an
explicit "AlGaN/GaN only" guard; high-In alloys are σ-degraded / cert-refused.

### 1.3 Thermal conductivity: 3-phonon BTE overpredicts at high T

For GaN/AlN the cheap κ path is 3-phonon BTE (almaBTE-class), which **overpredicts at high T**
because it omits 4-phonon scattering. The measured GaN curve (Zheng et al. PRMat 3 014601
(2019), TDTR, low-dislocation bulk) is κ ≈ 200 W/m·K @300 K, ≈ 50 @850 K, with
κ ∝ T^(−1.2) (300–600 K) steepening to T^(−1.5) (600–850 K) — stronger than the 3-phonon
T^(−1), the excess attributed to 4-phonon scattering. Carry **both** the 3-ph value (upper)
and the measured/4-ph-corrected value (lower); the spread is physical, not interpolation noise.

### 1.4 Impact ionization: published coefficients span >4 orders of magnitude

GaN Chynoweth prefactors `a` range from 1.5×10⁵ (Özbek 2011) to 2.11×10⁹ (Ji 2019) cm⁻¹
across groups. The honest posture: seed the most-defensible **modern** set (Cao 2018/2021 —
native-substrate, separated e/h photomultiplication) and carry σ ≥ ×3 (matching the spec's
diamond ×2.5 / β-Ga₂O₃ ×3 posture), documenting the spread. The prior ×1.5 was too optimistic.

---

## 2. Seeded coefficients (primary-sourced)

Units: C_ij/B in GPa; ρ g/cm³; ω meV; κ W/m·K; μ cm²/V·s; v cm/s; E_g eV; P C/m²; e C/m².
`m₀` = free-electron mass. ⊥/∥ are relative to the wurtzite c-axis.

### 2.1 Electronic baseline + deformation potentials
| Quantity | GaN | AlN | Source |
|---|---|---|---|
| E_g (0 K, direct Γ) | 3.51 | 6.25 | Vurgaftman & Meyer JAP 94 3675 (2003) |
| Varshni α / β | 0.909 meV/K / 830 K | 1.799 / 1462 | Vurgaftman & Meyer 2003 (Nepal APL 87 242104 (2005): GaN 0.94/791, AlN 2.63/2082) |
| AlGaN bowing b | 0.7 (rec) … 1.0 (exp) eV | — | Vurgaftman 2003; Nepal 2005 |
| m*_e (⊥ / ∥) | 0.20 / 0.20 | 0.32 / 0.33 | Vurgaftman 2003; Rinke PRB 77 075202 (2008) |
| m*_h (A-band ∥ / ⊥) | 1.88 / 0.33 | (CH-like; Δ_cr<0) | Rinke 2008 |
| ε_0 (⊥ / ∥) | 8.9 / 10.4 | 8.5 / 9.14 | Ioffe NSM; Wagner & Bechstedt PRB 66 115202 (2002) |
| ε_∞ (⊥ / ∥) | 5.35 / 5.8 | 4.77 / 4.84 | Ioffe NSM; Wagner & Bechstedt 2002 |
| Gap volume def. pot. a_V | −7.6 | −9.8 | Rinke 2008 |
| Wurtzite (a_cz−D1)/(a_ct−D2)/D3/D4/D5 | −5.33/−8.84/5.80/−3.09/−2.82 (G0W0) | −4.31/−12.11/9.12/−3.79/−3.23 (HSE) | Yan et al. APL 95 121111 (2009) |

### 2.2 AHC zero-point renormalization (tag `isochoric`; see §1.1)
| Material | ZPR isochoric (meV) | ZPR_lat (meV) | total (meV) | source |
|---|---|---|---|---|
| GaN | −189 (Engel AE −171) | −49 | −238 | Engel PRB 106 094316 (2022); Miglio npj CM 6 167 (2020) |
| AlN | −399 (Engel AE −377) | −85 | −484 | Engel 2022; Miglio 2020 |
| diamond (indirect) | −345 (band −320…−366) | small | ≈−345 | Antonius PRL 112 215501 (2014)/arXiv 1505.07738; Engel −323 |
| c-BN | −402 | — | — | Engel 2022; Miglio −406 |

(diamond **direct** gap ZPR −628 meV stays quarantined — different valley — Antonius 2014.)

### 2.3 Polarization / piezoelectric / Born (ZB-reference P_sp + PROPER e₃₁; see §1.2)
| Quantity | GaN | AlN | source |
|---|---|---|---|
| P_sp (ZB ref) | −0.029 … −0.034 | −0.081 … −0.090 | BFV PRB 56 R10024 (1997); Zoroddu PRB 63 045208 (2001, GGA) |
| Z*_∥ (axial, cation +) | +2.7 | +2.7 | BFV 1997; Zoroddu 2001 |
| e₃₃ (full) | 0.73 (BFV) / 1.02 (HSE) | 1.46 / 1.57 | BFV 1997; Dreyer PRX 6 021038 (2016) |
| **e₃₁ PROPER** | −0.49 (BFV) / −0.55 (HSE) | −0.60 / −0.68 | BFV 1997; Dreyer 2016 |
| e₃₁ improper (do NOT pair with ZB P_sp) | −1.86 | −2.03 | Dreyer 2016 (reference only) |
| d₃₃ / d₃₁ / d₁₅ | 2.7 / −1.4 / 1.8 (pm/V) | 5.4 / −2.1 / 2.9 | Bernardini & Fiorentini arXiv cond-mat/0202496 |
| n_s (Ga-face, x≈0.3) | 1.1×10¹³ cm⁻² | — | Ambacher JAP 87 334 (2000) |

### 2.4 Elastic constants (pin GaN→Polian, AlN→McNeil; exclude superseded AlN SAW set)
| Quantity | GaN | AlN | source |
|---|---|---|---|
| C₁₁ / C₁₂ / C₁₃ / C₃₃ / C₄₄ | 390 / 145 / 106 / 398 / 105 | 410.5 / 148.5 / 98.9 / 388.5 / 124.6 | Polian JAP 79 3343 (1996); McNeil JACerS 76 1132 (1993) |
| B (bulk modulus) | 210 | 210 | Polian 1996; Ioffe NSM |
| ρ | 6.15 | 3.23 | Ioffe NSM |
| AlGaN interpolation | linear Vegard (≤4.7% bowing, max on C₄₄; C₁₃ superlinear) | Łopuszyński & Majewski arXiv 1110.1346 |

**C₁₃ is the weak link** for both materials (largest experiment-vs-experiment & vs-DFT spread,
and the constant the piezo/Born-stability paths are most sensitive to) — flag, validate in-house.

### 2.5 Carrier transport
| Quantity | GaN | AlN | source |
|---|---|---|---|
| Caughey–Thomas μ_n (μ_max/μ_min/N_ref/α) | 1460.7 / 295 / 1×10¹⁷ / 0.66 (MC) | `GAP` (paywalled — Farahmand Tbl II / Wang Tbl SIII) | Farahmand IEEE TED 48 535 (2001) |
| Caughey–Thomas μ_p (μ_max/μ_min/N_ref/γ) | 170 / 10 / 2.5×10¹⁷ / 1.5 | `GAP` (genuine) | Mnatsakanov SSE 47 111 (2003) |
| μ FP ceiling (n / p, 300 K) | 1034 / 52 (Hall) | 871(⊥) / 619(∥) [n] | Ponce PRB 100 085204 (2019); Wang arXiv 2506.09240 (2025) |
| μ_n best experiment | 1265 | 426 | (cmp. Ponce 2019); Taniyasu APL 89 182112 (2006) |
| v_sat / v_peak ; β | 1.4×10⁷ / 2.85×10⁷ ; 2 | 1.4×10⁷ / 1.7×10⁷ ; ~2 | Foutz JAP 85 7727 (1999); O'Leary JMSE 17 87 (2006) |
| Fröhlich α_F ; ω_LO | 0.39–0.41 ; 92 meV | ~0.58 ; 110–114 meV | Mora-Ramos arXiv cond-mat/9812021; Davydov PRB 58 12899 (1998) |
| Alloy ΔU ; μ-min(x) | ΔU = 1.8 eV ; μ_min at x≈0.5–0.6 (~7× below GaN) | Pant APL 121 032105 (2022) |

### 2.6 Phonon baseline + thermal conductivity (κ flagged by axis; high-T see §1.3)
| Quantity | GaN | AlN | source |
|---|---|---|---|
| Θ_D | ~600 K | ~970–1000 K | Slack; Zheng 2019 (636); Wang–Zhao Powder Diffr. (AlN 971) |
| ω_TO A1 / E1 | 66.1 / 69.6 meV | 76.1 / 83.4 | Davydov PRB 58 12899 (1998) Tbl II |
| ω_LO A1 / E1 (max) | 91.1 / 92.1 meV | 110.7 / 113.6 | Davydov 1998 |
| mode γ (TA, LA) | 0.18, 1.36 | 0.16, 1.04 | first-principles QHA (arXiv 2211.03960) |
| κ(300 K) | 240 (a; FP) / ~200 (exp) | 339 (c; exp+FP) | Lindsay-Broido-Reinecke PRL 109 095901 (2012) [GaN]; Rounds/Slack APEX 11 071001 (2018) + Slack JPCS 48 641 (1987) [AlN] |
| κ(773 K) | 3-ph ~100 / measured ~60 | ~140 (theory-only) | Zheng PRMat 3 014601 (2019) |
| κ(1100 K) | 3-ph ~70 / measured ~35–40 | ~95 (theory-only) | Zheng 2019 |
| AlGaN κ dip | minimum at x≈0.6–0.71; dilute −46.5% (1% Al→GaN) / −75.8% (1% Ga→AlN) | Dagli-Mengle-Kioupakis arXiv 1910.05440 (2019) |

### 2.7 High-field (impact ionization, breakdown)
| Quantity | GaN | AlN | source |
|---|---|---|---|
| Chynoweth α_n (a, b) | seed Cao 4.48×10⁸, 3.39×10⁷ ; spread incl. Özbek 1.5×10⁵/1.41×10⁷, Maeda 2.69×10⁷, Ji 2.11×10⁹ | `GAP` (measured); MC-only Bulutay 8.875×10⁶, 3.759×10⁸ (electron) | Cao APL 112 262103 (2018); Özbek & Baliga IEEE EDL 32 1361 (2011); Bulutay SST 17 L59 (2002) |
| Chynoweth α_p (a, b) | Cao 7.13×10⁶, 1.46×10⁷ | `GAP` (genuine) | Cao 2018 |
| σ on α | ≥ ×3 | unbounded | Ji review AIP Adv 12 030703 (2022) |
| E_BR (critical) | 3.0–3.8 MV/cm | 12–15.4 (theory; no measured avalanche) | Maeda JAP 129 185702 (2021) |
| κ_BR sign | positive (dV_BR/dT +3.85×10⁻⁴ K⁻¹, device) | `GAP` (no avalanche; positive by analogy) | Frontiers Mater. 9 846418 (2022) |

### 2.8 Image-force barrier lowering (diamond; reconciles the in-repo 0.06-vs-0.18 eV flag)
Δφ = √(qE/(4πε_sε₀)), diamond ε_s=5.7: **0.16 eV @ 10⁶ V/cm**, 0.50 eV @ 10⁷ V/cm.
The in-repo 0.06 eV is a √10 field-scaling error; 0.18 eV is ~13% high. Seed 0.16 eV @ 10⁶.

---

## 3. Corrections to prior in-repo values (the audit's "these are wrong now" list)

A1 ZPR `total`→`isochoric` + values (§1.1, §2.2). A2 ±5%-ΔP justification → Dreyer accidental
cancellation (§1.2). A3 proper-e₃₁ self-consistent-pairing cert (§1.2). A4 InGaN high-In guard
(§1.2). A5 GaN κ high-T 100/70 → carry measured 60/35–40 (§1.3). A6 AlN κ high-T → theory-only.
A7 GaN α citation "Maeda APL 112 (2018)" → **Özbek & Baliga IEEE EDL 32 1361 (2011)**. A8 AlN
κ citation Lindsay-PRL-109 → Rounds/Slack APEX 11 (2018) + Slack JPCS 48 (1987). A9 AlN ω_LO
100 → ~111–114 meV. A10 AlN Θ_D 1150 → ~1000 K. A11 v_sat(GaN) 2.5e7 → v_sat 1.4e7 / v_peak
2.85e7. A12 Fröhlich α_F GaN 0.49→~0.40, AlN 0.65→~0.58. A13 μ_n(AlN) 300 → 871(⊥)/619(∥) FP,
426 exp (300 = doped/defective). A14 GaN α σ ×1.5 → ≥×3, reseed Cao. A15 image-force → 0.16 eV
@10⁶ (§2.8). A16 the 2026-06-10 re-audit over-cleared A5/A7/A8 as "sound" — recorded.

---

## 4. Genuine GAPS (flagged, never invented)

AlN electron Caughey–Thomas quartet (paywalled — one targeted follow-up); AlN hole mobility
(deep Mg, genuine); AlN **measured** avalanche α_ii (only MC, electron-only → measured stays
cert-refused); AlN hole α_ii; κ_BR as normalized (1/E)dE/dT in K⁻¹ for GaN/AlN (only device
dV_BR/dT exists; sign positive confirmed); Z*_⊥ (perpendicular Born charge); e₁₅ sign
(literature split ±); AlGaN d-constants / v_sat(x) / holes; AlN B′ / per-axis sound velocities
/ experimental elastic bowing; AlN high-T (>500 K) κ measurement; III-N EDF-tail Δα (ships as
identity, V2).

---

## 5. Sources (primary, DOI)

Vurgaftman & Meyer JAP 94 3675 (2003) 10.1063/1.1600519 · Engel et al. PRB 106 094316 (2022)
10.1103/PhysRevB.106.094316 · Miglio et al. npj Comput. Mater. 6 167 (2020)
10.1038/s41524-020-00434-z · Antonius et al. PRL 112 215501 (2014) 10.1103/PhysRevLett.112.215501 ·
Bernardini, Fiorentini & Vanderbilt PRB 56 R10024 (1997) 10.1103/PhysRevB.56.R10024 ·
Dreyer et al. PRX 6 021038 (2016) 10.1103/PhysRevX.6.021038 · Ambacher et al. JAP 87 334 (2000)
10.1063/1.371866 · Polian, Grimsditch & Grzegory JAP 79 3343 (1996) 10.1063/1.361236 ·
McNeil, Grimsditch & French JACerS 76 1132 (1993) 10.1111/j.1151-2916.1993.tb03730.x ·
Farahmand et al. IEEE TED 48 535 (2001) 10.1109/16.906448 · Mnatsakanov et al. SSE 47 111 (2003)
10.1016/S0038-1101(02)00256-3 · Ponce, Jena & Giustino PRB 100 085204 (2019)
10.1103/PhysRevB.100.085204 · Wang et al. arXiv 2506.09240 (2025) · Taniyasu et al. APL 89 182112
(2006) 10.1063/1.2378726 · Pant et al. APL 121 032105 (2022) 10.1063/5.0099516 ·
Davydov et al. PRB 58 12899 (1998) 10.1103/PhysRevB.58.12899 · Lindsay, Broido & Reinecke
PRL 109 095901 (2012) 10.1103/PhysRevLett.109.095901 · Rounds, Slack et al. APEX 11 071001 (2018)
10.7567/APEX.11.071001 · Zheng et al. PRMat 3 014601 (2019) 10.1103/PhysRevMaterials.3.014601 ·
Dagli, Mengle & Kioupakis arXiv 1910.05440 (2019) · Cao, Ye, Wang & Fay APL 112 262103 (2018)
10.1063/1.5031785 · Özbek & Baliga IEEE EDL 32 1361 (2011) 10.1109/LED.2011.2162221 ·
Bulutay SST 17 L59 (2002) · Ji et al. AIP Adv 12 030703 (2022) 10.1063/5.0083111 ·
Rinke et al. PRB 77 075202 (2008) · Yan et al. APL 95 121111 (2009) 10.1063/1.3236533 ·
Wagner & Bechstedt PRB 66 115202 (2002).

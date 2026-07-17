# 2026-07-16 — Wave-2 β-Ga₂O₃ adversarial audit (gate of the 2026-07-08 seeding spec)

Two independent web-verifying auditors on the Wave-1 mandate (refute), per the spec's §5
landing plan: **Auditor 1 — conventions & physics traps** (verdict: CLEAR-WITH-PINS);
**Auditor 2 — numbers / provenance / gaps / extractions** (verdict: BLOCK pending fixes,
all fixes applied at adjudication). **Adjudicated outcome: β-Ga₂O₃ package + III-N
pyroelectric rider (B1) CLEARED and seeded; III-N polarization-bowing rider (B3) GATED on
two paywalled primary texts** (gate texts read 2026-07-16 — see §4 G1; residual = the
FBA/Ambacher pin-read). Target: `docs/specs/2026-07-08-wave2-beta-ga2o3-seeding.md`
(corrections applied in place, status line updated).

## 1. Convention verdicts (Auditor 1)

1. **FB erratum / bowing sign+frame — CONFIRMED in substance.** The sign trap is real:
   FB01's own bowing definition (PRB 64 085207 Eq. 4–5) is `P = xP_AN + (1−x)P_BN −
   b·x(1−x)` with **b negative** ("bowing always upward"); the spec's `+b·x(1−x),
   b ≈ +0.019…0.021` is the same physics via double-negative — a naive lift of FB01's Eq-5
   b into a `+b` formula would flip the bowing and corrupt interface charge. Frame
   consistent with the repo's certified ZB-ref-P_sp + proper-e₃₁ pairing (arch-12
   §12.0.3; Dreyer PRX 6 021038). **However: the erratum text itself (PRB 65 129903,
   2002) could not be read from open sources** — the spec's mandated "read the erratum
   before seeding" is formally unmet → **B3 gated** (finding G1).
2. **Pyroelectric sign — CONFIRMED with derivation.** Seeded III-N P_sp are negative
   (ZB-ref frame); |P_sp| decreases toward zero with rising T ⇒ **p = dP_sp/dT is
   POSITIVE in the seeded frame**. Trap: raw literature quotes p negative (positive-P_s
   convention). Seed positive; a sign-guard note rides the CSV rows. The ~100 K
   primary→secondary crossover and the "total (primary+secondary) at fixed stress"
   methodology are confirmed (AlN T_p ≈ 100 K, tied to its <100 K negative thermal
   expansion). **B1 rider CLEAR.**
3. **ZPR retag `total (⚠)` → `isochoric` — CONFIRMED, with a refinement.** Arabov et al.
   (arXiv 2603.29484, 2026, read in full): ZPR = 0.20±0.01 eV from clamped-cell harmonic
   sampling (genuinely isochoric e-ph, same class as the III-N Engel/Miglio entries);
   thermal-expansion contribution to the gap renormalization is minor over 0–900 K.
   Cross-confirmed by Lee et al., APL Mater. 11 011106 (2023) (−0.19±0.05 eV).
   **Refinement:** the −0.45 eV shift at 700 K is Arabov's *total* (includes the small
   expansion term) — the isochoric tag applies to the ZPR amplitude, not to the 700 K
   slope, else row 63 double-counts.
4. **Predicate split — CONFIRMED, no residual conflation.** C2/m (No. 12) centrosymmetric
   ⇒ `is-noncentrosymmetric` FALSE (rows 113–119/128 inert); `is-polar-material` TRUE
   (massive multi-mode Fröhlich).
5. **Anisotropy/frame — CONFIRMED.** Onset ordering E∥c < E∥a < E∥b; never-average rule
   correct; RUS frame (x∥a, y∥b, z∥c*) matches the elasticity paper; full 13-constant
   monoclinic Born-stability criteria required (not the cubic reduced set). Trivial fix:
   §1.2's onset spread is ~0.3 eV, not ~0.4.
6. **Hole/STH cert-refusal — CONFIRMED.** Varley et al., PRB 85 081109(R) (2012):
   self-trapping −0.39/−0.46 eV; UV luminescence ≈3.5 eV is free-electron ↔ STH
   recombination, not band-edge; no band-like hole transport. Refusing hole μ / hole
   α_ii / p-type C-T is correct, and row 134's B_rad applies to the STH emission.
7. **Multi-mode Fröhlich — CONFIRMED physics, CORRECTED attribution.** The mode table
   exists: **Mengle & Kioupakis, AIP Advances 9 015313 (2019), Table I** (12 IR-active
   modes, TO + directional LO, dominant e-ph mode at 29 meV) — resolving the spec's
   `[audit-pin: mode table]`. Ma et al. 2016 (previously credited) actually used a single
   effective α_F ≈ 1.68; the "single-α_F inadequate" claim belongs to Ghosh–Singisetti
   (JAP 122 035702 (2017); JAP 124 085707 (2018)).

**Holography cross-flag (raised by Auditor 2, adjudicated by Auditor 1):** the 2026
electron-holography bowing paper (Ebert et al., PRB 113) uses a layered-hexagonal
reference — which is Dreyer's *recommended* reference, so it agrees with the repo's
foundational frame source rather than contradicting it; bowing is a curvature (second
difference), ~invariant under reference choice; measured interface charge is
reference-independent. **Converts cleanly — no tension with arch-12 §12.0.3.** Guards:
import Ebert's b only as a curvature on ZB-ref endpoints (never their absolute
endpoints); the AlGaN/GaN-only accidental-cancellation guard stays; Ebert's numeric b is
an unresolved pin until the text is read (part of G1).

## 2. Number verdicts (Auditor 2) — as adjudicated

- **[BLOCK→fixed] E_c mis-attribution.** The spec's scalar "≈8 MV/cm, Ghosh–Singisetti"
  appears nowhere in that paper; Table 1 gives the anisotropic triple **10.2 / 4.8 / 7.6
  MV/cm along a / b / c*** (ionization-integral critical field at E_g = 4.9 eV); "≈8" is
  the bandgap-scaling estimate attributable to Higashiwaki (SST 31 034001, 2016) or the
  paper's max simulated field. The accuracy-ledger's existing triple was already correct.
  Seeded as the direction-tagged triple, σ ×0.3.
- **[BLOCK→fixed] Direction labels.** The paper's third axis is **c\*** (13.83° from
  [001]), per its own frame (x∥a, y∥b, z∥c*). All α_ii and E_c rows seeded with a/b/c*
  tags, honoring the spec's §1.2 rule.
- **Chynoweth extraction (seed-ready, Table 1):** a,b = (0.79×10⁶ /cm, 2.92×10⁷ V/cm)
  along a; (2.16×10⁶, 1.77×10⁷) along b; (0.706×10⁶, 2.10×10⁷) along c*; σ ×3.
- **[FIX] Polarized onsets.** Published E∥c ∈ {4.50 (Matsumoto 1974), 4.52 (Ueda 1997),
  4.59 (Onuma 2016)}; E∥b ∈ {4.65, 4.79, 4.90} (same sources). The two auditors landed on
  different endpoints of the E∥b spread (4.79 vs 4.88–4.90) — **adjudication: seed the
  spread centers with σ covering the spread: E∥c 4.55 ± 0.08, E∥b 4.80 ± 0.12** (the
  spec's σ = 0.05 would have made the literature spread a ~2σ event in a 3σ-trip battery).
- **[FIX] Handwerg parenthetical.** Handwerg 2015 (SST 30 024006, 3ω) measured [100]
  only, κ = 13±1 — the spec's "concurs (29±2 / 11±1)" matched no Handwerg value. Guo's
  own κ values confirmed exact (27.0±2.0 [010] / 10.9±1.0 [100], TDTR, ~1/T^1.1–1.3).
- **[FIX] κ[001](300 K) = ≈14 W/mK** (Guo Table-I fit, 8140/300^1.12), not ≈15.
- **[FIX] m*₍e₎ source.** 0.284 ± 0.013 m₀ by mid-IR optical Hall (Knight et al., APL 112
  012103, 2018) — value confirmed, "DFT+ARPES" label corrected.
- **[FIX] Klimm tensor study.** Cryst. Res. Technol. **58** 2200204 (**2023**, not 2022),
  DOI 10.1002/crat.202200204; 300 K principal-axis tensor λ₁₁=12.13, λ₂₂=24.26,
  λ₃₃=14.09, λ₁₃=−0.992 W/mK. **Frame finding:** principal axes ≠ crystallographic
  directions — only λ₂₂ ≡ [010] is frame-shared (24.26 vs Guo 27.0, ~10% method split).
  The 773/1100 K per-component values are **paywalled → acquisition item** (finding G2).
- **[FIX→seeded] Per-axis static dielectric constants** — listed as GAP in the spec but
  pinnable: ⊥(100) 10.2±0.2, ⊥(010) 10.87±0.08, ⊥(001) 12.4±0.4 (J. Solid State Sci.
  Technol. 8 Q3083, 2019, DOI 10.1149/2.0201907jss). Moved out of the GAP register and
  seeded.
- **[MINOR] AlN pyro sources split**: Yan et al. APL 90 212102 (2007) (epilayer/Debye
  analysis, p≈3.0) + Fuflyigin et al. APL 77 3075 (2000) (thin-film, 6–8); σ reformed
  from the malformed "×0.5" to **×2** (covers the 3→6–8 spread). GaN pyro stays
  dft-class.
- **[MINOR] μ_BTE ≈115 cm²/Vs** re-cited to Ghosh & Singisetti APL 109 072102 (2016)
  (Rode, phonon-limited; density tie dropped). APL Mater. first author confirmed: Lee.
- **Pins landed:** Åhman, Svensson & Albertsson, Acta Cryst. C52 1336 (1996) (lattice;
  ρ 5.96 derived); Θ_D 738 K central (Guo calorimetric fit) with FP endpoint 872 K
  (lower endpoint of the 420–870 spread unpinned — recorded as spread); best measured μ
  150–200 (bulk CZ 152 / MOCVD 176–~200 / 2DEG 180); v_sat 1–1.5×10⁷ sat, peak ~2×10⁷
  at ~200 kV/cm (JAP 122 035702, 2017); V_O deep donor (Varley et al., APL 97 142106,
  2010 + Erratum APL 108 039901, 2016); STH (Varley et al., PRB 85 081109(R), 2012).
- **Verified exact:** the full 13-constant RUS elastic set (JAP 124 085102, 2018) —
  including all small off-diagonals — zero transcription error; FB01+erratum existence
  and DOIs; Arabov ZPR/700 K numbers; Ma 2016 μ<200.

## 3. GAP register (post-audit)

Genuine and carried: C–T electron quartet (no consensus published fit — derive from
μ(N_D) or acquire); hole transport / hole α_ii (cert-refused, STH); Θ_D spread (recorded
as spread); Fröhlich multi-mode KernelExt parameter assembly (source now pinned to
Mengle–Kioupakis Table I — assembly remains research-side work); GaN pyro measured value
(stays dft-class); AlGaN-analog (Al_xGa₁₋ₓ)₂O₃ alloying (later wave). Removed from GAP:
per-axis ε₀ (pinned + seeded).

## 4. Acquisition items (one open end — user action)

- **G1 (gates B3):** obtain full texts of the **FB Erratum, PRB 65 129903 (2002)** and
  **Ebert et al., PRB 113 (2026)** (both APS-paywalled). The B3 bowing rider does not
  seed until both are read directly (physics risk judged LOW — post-erratum citing
  sources carry the upward bowing — but the spec's own mandate requires the read).
  A gate row rides in `polarization-piezoelectric.csv`.
  **Gate texts READ 2026-07-16** (erratum user-acquired via Texas State; the second
  paper turned out CC-BY open access — the audit-time 403 was a bot-block). Dispositions:
  1. **Erratum — benign for B3, as anticipated.** It corrects only the **piezoelectric**
     polarization of **CuPt-ordered In₀.₅Ga₀.₅N and Al₀.₅In₀.₅N** (a k-point-mesh
     subtraction error in FB01's Fig. 6; corrected Table I, % deviation from Vegard
     piezo: random −2/+4, chalcopyrite −3/−10, CuPt-ordered **−13/−38** for
     InGaN/AlInN). Verbatim: for CuPt-ordered Al₀.₅Ga₀.₅N "Vegard's law holds within
     the error bar"; "all the conclusions drawn in Ref. 2 about polarization in nitride
     alloys remain unchanged, except those on the piezoelectric polarization of
     In₀.₅Ga₀.₅N and Al₀.₅In₀.₅N CuPt-ordered alloys." **The spontaneous-polarization
     bowing (FB01 Eq. 4–5 / Fig. 7) is untouched**; the AlGaN piezo linear-interpolation
     stance is strengthened (CuPt-ordered AlGaN is Vegard-within-error).
  2. **"Ebert et al." = Lan, Schnedler, Ji, Carlin, Butté, Grandjean, Dunin-Borkowski,
     Ebert — PRB 113, 155302 (2026)**, off-axis electron holography with
     surface-potential calibration + self-consistent electrostatics, and it is
     **InGaN-only**: four In_xGa₁₋ₓN/GaN pairs, x = 0.030/0.062/0.102/0.132 (±0.005);
     ΔP_total = −0.00091±0.00034 / −0.00442±0.00107 / −0.00622±0.00089 /
     −0.0077±0.00135 C/m². **There is no AlGaN data in the paper**, so the §1
     cross-flag's "import Ebert's b only as a curvature" path is **moot** (bowing does
     not transfer across alloy systems) — and its "~invariant under reference choice"
     premise is **unsound**: the paper's own Figs. 5–6 show ZB-frame theory bowing with
     the *opposite* curvature sign to LH-frame theory and experiment (the ZB reference
     procedure injects spurious composition dependence — Dreyer's original criticism).
     Their LH-frame result: b(InGaN, x < 0.25) = 0.382 ± 0.075 C/m² on P_spon,LH
     endpoints 1.299 (GaN) / 1.032 (InN); full-range cubic b(x) = 0.105 − 0.238x.
     **Net contribution: experimentally refutes the ZB-reference bowing curvature for
     InGaN and validates the LH frame** — upgrading the accuracy-ledger row-35 high-In
     InGaN/GaN cert-refusal from theoretical to experimental. In-hand primary source
     for a future In-wave; nothing seeds from it for AlGaN.
  **Residual (last pin before B3 seeds):** the mandated primary read of **FBA APL 80
  1204 (2002)** / **Ambacher JPCM 14 3399 (2002)** for the exact AlGaN b — +0.019 and
  +0.021 C/m² both circulate, and secondary quotes are demonstrably corrupted (a
  2026-07-16 web check surfaced "−0.032(1−x) + 0.039x(1−x)": wrong GaN endpoint and the
  InGaN bowing misattributed to AlGaN). No open copies exist (Semantic Scholar, OpenAlex,
  arXiv, UNICA-IRIS all checked 2026-07-16); user acquiring via Texas State.
- **G2 — CLOSED same day.** The Klimm paper turned out **open access** (Projekt DEAL;
  archival copy at d-nb.info/1274779782/34) — the auditor's 403s were bot-blocks, not a
  paywall. Full main text read 2026-07-16. Frame corrected from the auditor's caution:
  the tensor is in the **crystal-physical frame** (e₂∥b, e₃∥c, e₁ = a\*), so λ₂₂ ≡ [010]
  *and* λ₃₃ ≡ [001] are crystallographic-direction components (λ₃₃ = 14.09 independently
  confirms the audit's κ[001] ≈ 14 correction); the direct plane-normal measurements
  λ₍₁₀₀₎ = 12.13 / λ₍₀₀₁₎ = 13.53 are along a\*/c\* (never relabel as [100]/[001]).
  Derived high-T anchors seeded: κ[010](773 K) ≈ 9 ± 2, κ[010](1100 K) ≈ 6 ± 1.5 W/mK
  (λ₂₂(300) = 24.26 direct × the paper's own T^−m law, m ≈ 1.0–1.2, consistent with its
  Figs. 2–3). Residual (optional): the SI's exact per-temperature tables.

## 5. Disposition

Spec corrected in place (status line records this audit); β-Ga₂O₃ rows seeded across the
four reference CSVs (direction-tagged; monoclinic frame stated); III-N pyroelectric
coefficients seeded (positive-p in the ZB-ref frame, sign-guard noted); accuracy-ledger
β-Ga₂O₃ ZPR row retagged `isochoric`, κ row completed ([001] ≈14), Chynoweth/E_c row
direction-tagged; reference-data README population status updated. B3 held behind G1
(gate texts read 2026-07-16; residual = the FBA/Ambacher pin-read, then B3 seeds).

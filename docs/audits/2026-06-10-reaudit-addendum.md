# Re-audit addendum — fix verification + Pass C design audit

**Date:** 2026-06-10 · **Scope:** verification of the remediation commits (`68b61cd`, `e826668`,
`0078157`) against `docs/audits/2026-06-09-physics-audit.md`, plus a physics audit of the
pre-landing Pass C design (`docs/superpowers/specs/2026-06-10-pass-c-accuracy-design.md`).
Format follows the original audit: verdict (defect / risk / open / verified-ok), severity
S1–S4, scope tag. Items the original audit marked verified-ok were not re-read (commissioner
instruction).

## 1. Fix-verification scorecard

| Original finding | Fix | Verdict |
|---|---|---|
| P2.1/P2.3 + P1.1/P1.4 — GENERIC layer (degeneracy, Lie–Poisson γ̂, Jacobi, E-assembly) | arch-05 "Generator structure is per-tier" + level-conditional `E_KS[γ̂;R,h]` (with `v_ext`/`V_II` home) + Degeneracy→cert-only + arch-19 §19.4 form-vs-values | **RESOLVED.** The Lie–Poisson degeneracy argument (spectral `S_el` ⇒ `[δS_el/δγ̂, γ̂]=0`) is correct; the L2 isothermal single-generator contraction is the standard and right reading; the Jacobi per-block status (exact for canonical blocks, restricted-class-or-flagged for generated cross-blocks) is honest. |
| Structural gap 1 — degradation/aging kinetics | arch-21 slow tier: `DefectSpecies` universe, rows 105–112 (incl. oxidation #46→109, H-desorption #47→110), `EOM/DefectPopulation`, adiabatic driving contract, R-T1..T3 identities | **RESOLVED** (with one new S2 defect, §3.1 below). Barriers and rates check against the research and independent knowledge: NRT `0.8·T_dam/2E_d` correct; `E_d` (C 37–50, GaN ~20, AlN ~35, Ga₂O₃ ~25 eV) correct; migration barriers (V_C⁰ 2.3, C_i 1.6–1.7, V_Ga 1.9 eV…) consistent; diamond `E_form(V_C)≈7.2 eV` ⇒ interface/irradiation-dominated 500 °C budget is the right conclusion. |
| Structural gap 3 — unit-cell↔device bridge | arch-21 macro tier: `DeviceMesh` FV universe, moment closures (T_e, j), HM-1..8 homogenization map, `EOM/Continuum`; arch-18 §2 narrowed to adjoint-scheme-only | **RESOLVED** (with one new S2 risk, §3.2 below). Two-temperature closure algebra verified; HM map physically complete for (P)+(DD)+(H); score-not-solve preserved at every tier. |
| Radiation silent scope drop | Rows 111–112 + `Environment` fields (`radiation_flux`, `Φ_dose`, `E_d`, vibration PSD, `p_O2`) in arch-03 | **RESOLVED** (modulo §3.1). |
| P0 tranche (error model, D-tags, cadence, cost, PSD, provenance, mechanical) | accuracy-ledger.md + arch-11 §11.7 + arch-12 §12.0.1/§12.0.2 + impl-04 + impl-07 §7.8 + arch-07 §7.6 + arch-19 §19.7/§19.8 + all mechanical fixes | **ALL RESOLVED.** Spot-verified: tolerance values, ε→δ/τ rename, congruence-action Reynolds + assembled-super-block PSD statement, obligation indices (PSD=2, antisym=5), graphitization vacuum/air split, B11=degradation reconcile, 52(+16), four op-signatures, cadence table, three-class cost contract. Ledger #20 still carries the κ_BR sign error — correctly queued as a Pass C must-fix, acceptable pre-landing. |
| P1.3 — polarization/piezo/2DEG | Rows 113–119 + arch-19 §19.10 piezo-acoustic channel (`LongRangeStatic(1)`) + arch-17 Berry-phase deferral | **RESOLVED.** Constants are the correct BFV/literature values (P_sp: GaN −0.029, AlN −0.081 C/m²; e₃₃: GaN +0.73, AlN +1.46 C/m²); the 1/q piezo-acoustic pole vs 1/q² Fröhlich is right; the Berry-phase λ-path deferral is honestly tracked. Note (S4): the linearized `Z*·Δw` path is ±10–20% on *absolute* P_sp; the ±5% claim is defensible only because `n_s` consumes interface *differences* ΔP, where the reference ambiguity largely cancels — worth one sentence at landing. |
| ω²≥0 gating to claimed-stable phases | arch-11:83–84 applicability-gated | **RESOLVED.** |
| T,P-aware hull | Pass C §5(b) | **Designed, pending landing** — form is correct (δ_meta band; diamond +25 meV/atom reads R=0). |

**Still open from the original P1 list (not addressed by any pass):** see §3.5 and §3.6.

## 2. Pass C design — physics verdicts

**The design's two corrections of the original audit are CONFIRMED; the audit record is
amended:** (a) diamond 3-phonon-only κ overprediction is ~1% @300 K → ~30% @1000 K
(Feng–Lindsay–Ruan PRB 96 161201(R)); the dramatic RT 4-phonon collapse (≈2200→1400 W/mK) is
**BAs**, which the original audit conflated into its "10–15% @300 K" figure — retracted. (b)
`E_b` **rises** with T (κ_BR > 0; phonon scattering suppresses α_ii); ledger #20 as landed has
the sign backwards and Pass C's fix is correct.

| Section | Verdict |
|---|---|
| §1 AHC gap(T) | **SOUND.** Adiabatic AHC one-shot is legitimately Layer 1.25 / C1-clean. ZPR table verified: diamond −345 meV indirect (exp 340–370) with Antonius PRL 112 215501 −628 meV **direct** correctly quarantined; c-BN ≈−400 (Miglio −406); AlN −385, GaN −180, Ga₂O₃ −200 plausible. `n_i` ×11 @800 K arithmetic checks (exp(0.345/2kT) ≈ 12). **One landing defect — see §3.3.** |
| §2 κ(T) | **SOUND.** The decoupling argument (RTA-underestimate ≠ 4-ph-overestimate; no cancellation reliance) is correct physics. Anchors verified: diamond 620 @773 K (independent estimate 600–700), Ga₂O₃ [010] 27 / [100] 10.9 (Guo 2015), GaN 240, AlN 339. Dormant MethodEquivalence anchored to published κ_iter is honest for V1. Validity domain `T ≳ 0.4Θ_D` for the Slack-like 4-ph factor is reasonable (diamond ≈880 K). |
| §3 high-field | **SOUND on parameters; one structural defect (§3.4).** Chynoweth/Caughey–Thomas values and σ's consistent with the literature basis (Hiraiwa–Kawarada contested ×2.5 correctly carried); cert-refusal of unprovenanced breakdown channels is the right rule; ">500 °C breakdown = cert-refused, not met" is the honest call. |
| §4 interpolation | **SOUND.** Fourier-for-bands / Wannier-for-e-ph split with mandatory dipole+quadrupole polar corrections (incl. c-BN) is the standard, correct design; all compile-time. Suggestion (S4): add a Wannierization quality gate (band-reproduction error on held-out k-points) feeding the declared mesh-σ floor — maximal localization can fail quietly on entangled conduction bands. |
| §5 residuals | **ALL CORRECT.** Wegscheider cycle, rotational sum rule (Born–Huang/Gazis–Wallis), `T_e≥T_L`, breakdown-integral guard, hull δ_meta, Callaway→consistency-pair reframe, and the duplicate-row deletions (72/75) all check. |
| §6 bookkeeping | Row-collision must-fix correct. Add: fix the row-name typo `kappa-4phonon-hight-correction` → `…-high-t-…` **before landing** — names are hash-consed into content addresses; a later rename is a substrate-wide rekey, not an edit. |

## 3. New findings (this re-audit)

1. **[S2 defect, V1, row 112]** `frenkel-pair-yield` is dimensionally short a damage
   cross-section: `[V]_irr = N_d·(1−η_recomb)·Φ_dose` is cm⁻² (N_d is per-PKA,
   dimensionless; Φ in cm⁻²). It needs the macroscopic displacement cross-section,
   `[V]_irr = Φ·Σ_d·N_d·(1−η_recomb)` with `Σ_d = N_atom·σ_d` (cm⁻¹), σ_d NIEL-derived per
   particle type/energy — i.e. one more curated ProvenanceLedger coefficient per
   (host, particle). As written the row cannot produce a `Concentration`.
2. **[S2 risk, V1, arch-21 §21.9]** The `EOM/Continuum` drift-diffusion face flux must commit
   to **Scharfetter–Gummel** (Bernoulli-function exponential fitting), not central/naive FV
   differencing. At MV/cm with ~10 nm cells the cell Péclet `qEΔx/kT ≈ 40`; a
   centrally-differenced `j_f` makes the *residual operator itself* wrong at exactly the
   operating point, so the PINO would be scored against a discretization artifact. SG is
   closed-form, differentiable (one removable singularity at small Péclet, standard guard),
   C1-clean — it just has to be named in HM-2/§21.9.
3. **[S2 landing-gate, Pass C §1]** The AHC-vs-thermal-expansion double-count protection must
   be **machine-checkable, not a caveat sentence**: the quoted per-material `dE_g/dT` slopes
   are (mostly) *total* experimental slopes, while row 63 (Ξ·strain) separately carries the
   lattice-expansion part (~30–40% of the shift). Landing rule: each ProvenanceLedger slope
   entry carries a `slope-kind ∈ {isochoric, total}` tag; cert refuses a composition where a
   `total`-tagged AHC slope and row 63's T-path are both active on the same observable.
4. **[S2 structural risk, Pass C §3]** The V1 EDF-tail `Δα(E,T_L,T_e)` as a *PINO-learned*
   correction inside the avalanche residual is circular **if trained on the same loss it
   modifies** — the model can co-adapt Δα to zero its own residual, silently destroying the
   supervision signal in the unmeasured corner the obligation-9 domain is meant to protect.
   Landing rule: Δα may be fit **only against external anchors** (measurements / future
   BTE-MC points) and is **frozen w.r.t. the PINO loss**; until such anchors exist (design
   admits they are absent), Δα ships as identity and the corner stays cert-refused. This
   makes the design's own ">500 °C cert-refused" stance load-bearing rather than decorative.
5. **[S3 open, unaddressed by any pass]** Compose-time applicability vs runtime T-sweeps:
   Stage-2.5 channel skipping and formula validity windows are evaluated against the
   composition's nominal `(Crystal, Environment)`, but `arch-07` passes T as a runtime input.
   A sweep crossing a validity boundary (QHA window, regime windows, `ω²≥0` claimed-stable
   gate, Chynoweth domain) leaves a stale kernel silently in force. Needed: predicates/validity
   windows depending on swept Environment scalars are re-evaluated per-sample in the loss mask
   (the per-sample mask path already exists in arch-13), and a kernel is tagged with the
   Environment box on which its Stage-2.5 structure is valid.
6. **[S3 open, unaddressed]** Plasmon–phonon coupling / LST breakdown at degenerate doping
   (>~1e20 cm⁻³ — reached by p⁺ B-doped diamond contact layers): the research-side limit was
   dropped; neither an arch-17 exclusion entry nor an applicability gate on the LST/ε_r path
   exists. Cheapest honest fix: applicability-gate LST-derived ε_r (and Fröhlich screening)
   on `n < n_degenerate(host)` + an arch-17 entry.
7. **[S3 gap, V1, materials]** High-T thermal expansion for the III-N members: ledger #14
   documents "QHA breaks above ~Θ_D/2 (GaN fails at 500 °C)" but no pass provides a
   design-grade path — this propagates into gap-vs-T (row 63 strain part), G(T), and the
   T,P-hull for exactly the flagship polar materials. Minimum: per-material σ widening in the
   ledger + arch-17 entry; better (V2): a first-order self-consistent-phonon correction as a
   second Layer-1.25 dressing (one-shot, same amortization shape as AHC).
8. **[S3 gap, V1, materials]** Alloy-disorder scattering is absent (registry has only
   `vegard-correction`, a lattice-constant helper). For AlGaN-channel devices — in scope per
   arch-01/arch-19 — alloy scattering is the dominant mobility limiter; without it μ(AlGaN)
   will be systematically optimistic. One closed-form row (Harrison-type
   `τ_alloy⁻¹ ∝ x(1−x)·ΔU²·g(E)`) in the mobility composition, `is-alloy`-gated. The 2DEG
   n_s package (rows 113–119) is unaffected; this is the *transport* half of the alloy story.
9. **[S4]** HM-2 uses the nondegenerate Einstein relation `D = μk_BT/q`; p⁺ diamond layers at
   1e20–1e21 cm⁻³ are degenerate — note the generalized form
   `D/μ = (k_BT/q)·F_{1/2}/F_{−1/2}` as the declared model-form error or a gated variant.
10. **[S4]** The image-force-lowering inconsistency between research files (0.06 vs 0.18 eV)
    is still unresolved; resolve before any barrier-lowering coefficient seeds a
    ProvenanceLedger table (it shifts φ_B-derived contact R by e^(Δ/kT)).

**Open items correctly flagged (no action beyond tracking):** `η_recomb(T_L)` closed form,
mesh-adjoint scheme, hole-transport anchors, Berry-phase λ-path (V2), EDF-tail BTE/MC anchors
(the gating acquisition), live iterative-LBTE (V2).

## 4. Verdict

The remediation is **genuine, not cosmetic**: every P0 item and all three structural gaps from
the original audit are resolved in-spec with research-grounded content, correct constants, and
honest flagging of what the corpus could not support. The Pass C design is **ship-with-fixes**:
its physics is sound and twice *improved* on the original audit; the must-fix list in its §6
is necessary but not sufficient — items 1–4 above (Frenkel-pair dimensions, Scharfetter–Gummel,
slope-kind tag, Δα training contract) should join it as landing gates, and items 5–8 are the
last known physics holes in the V1 claim.

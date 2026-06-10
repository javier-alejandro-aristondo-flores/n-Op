# Pass C — per-material accuracy package (design + audited findings)

**Date:** 2026-06-10 · **Status:** approved design, not yet landed · **Method:** 4 web-grounded
deep-dive subagents → 1 adversarial web-verifying audit (`/tmp/n-op-passc/{d1..d4,audit}.md`,
ephemeral — the concrete content is reproduced here). Closes audit P2 items P1.5–P1.8 + P1.10
(the last remediation tranche from `docs/audits/2026-06-09-physics-audit.md`). Lifts the MVP's
headline accuracy from "stated regimes" to **literature-anchored σ's the error ledger
(`arch-11 §11.7`) composes** — the design-grade-at-500 °C bet, made checkable.

## 0. Audit outcome (the rigor result)

Verdicts: **D1 (AHC) / D2 (κ) / D3 (high-field) SHIP-WITH-FIXES**; **D4 (interp/residuals)
RECONSIDER → SHIP once duplicate rows removed**. C1 (closed-form, no runtime solver) clean for
all. The web re-verification **corrected the original audit twice** (deep-dives beat the audit,
primary-source-confirmed):

- **diamond 3-phonon overprediction is ~1% @300 K → ~30% @1000 K** (Feng–Lindsay–Ruan *PRB* 96,
  161201 (2017): "overpredicts κ of diamond and silicon by 31% and 26% at 1000 K"), **not** the
  audit's 10–15%→25–35%; and the "2200→1400 W/m·K RT" drop is **BAs, not diamond**.
- **breakdown field rises with T** (positive `κ_BR ≈ +5×10⁻⁴/K`, confirmed across 4H-SiC,
  +200 mV/K) — the accuracy-ledger `#20` "drops ~20% 300→800 K" is a **sign error** (conflated
  `E_b` with mobility collapse).

## 1. AHC gap(T) renormalization (P1.6) — Layer-1.25 one-shot dressing

**Form (one-shot, no self-consistency — C1-clean, audit-confirmed):** adiabatic Allen–Heine
`ΔE_g(T) = Σ_qν A_qν [2 n_qν(T) + 1]` (Giustino RMP 2017, Eq. 167; Fan–Migdal + Debye–Waller on
the mass shell). The `A_qν` are T-independent — computed **once** over the already-DFPT'd phonons
and DFT/G₀W₀ bands; all T-dependence is the scalar Bose factor. Curated cheap form:
`ΔE_g(T) = ZPR · coth(Θ/2T)`. Composition (no double-count, G₀W₀ is at clamped nuclei):
`E_g(T,ε) = E_g^{G₀W₀} + ΔE_g^{AHC}(T) + ΔE_g^{strain}(ε)` (existing row 63 = strain part).

**Per-material ZPR / high-T slope (curated `ProvenanceLedger`, literature-anchored):**

| Material | ZPR (meV) | dE_g/dT (meV/K) | source |
|---|---|---|---|
| diamond | **−345** (indirect; exp 340–370, Cardona) | −0.45 | Engel PAW −323; **−0.628 eV is the *direct* gap (Antonius PRL 112 215501, 2014) — kept separate** |
| c-BN | −400 | ~−0.50 (slope unmeasured) | Engel −402 / Miglio −406 |
| AlN | −385 | −0.55 | Engel −377 |
| GaN | −180 | −0.50 | Engel −171; Varshni Nepal APL 2005 |
| β-Ga₂O₃ | −200 | −0.90 (worst >500 °C; anisotropic, polar) | Lee APL Mater. 2023 |

**σ(T-shift):** ±0.05 eV non-polar / ±0.1 eV polar. **`n_i` leverage:** `δn_i/n_i = δE_g/2k_BT`
→ omitting diamond's 345 meV mis-states `n_i` by **×11 at 800 K** (this is why leakage/thermionic
rows needed it).

**Audit must-fixes applied:** cite **Antonius PRL 112 215501 (2014)** (not PRB); add a
thermal-expansion(strain)-vs-AHC-slope double-count caveat (the two T-paths must not both carry
the lattice-expansion contribution).

**Lands as:** registry row `ahc-gap-renormalization` (B1, T1, D1, depends-on row 6 + DFPT
phonons/`g_qν`, applicability `gap-bearing`); the 5-material ZPR/slope table as curated
`ProvenanceLedger` coefficients; accuracy-ledger `#1`/`#15` updated. **V2-deferred:** the faithful
`A_qν` BZ-sum + non-adiabatic AHC (Layer 1.75; ~25% on polar ZPR).

## 2. κ(T) accuracy (P1.5) — iterative-LBTE sibling + 4-phonon correction + high-T battery

**Two dispositions.** (a) **Iterative-LBTE** as the faithful sibling — the converged off-diagonal
(normal-process) redistribution of the **same collision matrix RTA already assembles**, run
**per-composition (T3 calibration cadence, `impl-07 §7.8`)**, *not* per sample (C1-clean). Its
V1 MethodEquivalence binding is **dormant** — anchored to published `κ_iter`, no live solve
(stated honestly). (b) **Closed-form Slack-like 4-phonon correction** (multiplicative κ-factor)
with explicit validity domain **`T ≳ 0.4·Θ_D`**. Both bind to the cheap Slack/Callaway fit (row 25)
via `Algebraic/MethodEquivalence` **retargeted at the iterative reference** — this is what closes
"validated at the wrong point."

**Why near 300 K the errors do NOT cancel:** RTA underestimates κ ~30–50% (normal-process
dominance; Broido 2007 ~50% enriched, ~30–40% natural diamond), while missing-4-phonon
*overestimates* only ~1% @300 K → ~30% @1000 K. So near RT the RTA-underestimate dominates (net
~−30–40%) and the fix **decouples** them rather than relying on cancellation.

**κ(T) battery anchors (W/m·K @ 300/773/1100 K), literature-anchored:** diamond **2200 / 620 /
450** (exp 2000–2500 RT); GaN(a) 240/100/70; AlN(c) 339/~140/~95; β-Ga₂O₃ **tensor** ([010] 27,
[100] 11 @300 K, ~2.5–3× anisotropy, Guo APL 2015). Sources: Feng–Lindsay–Ruan PRB 96 161201
(2017); Broido APL 91 231922 (2007); Lindsay–Broido–Reinecke PRL 109 095901 (2012); almaBTE
GaN/AlN.

**Honest envelope:** ±20% diamond @300 K **only if anchored to `κ_iter ≈ 2200`, not
`κ_RTA ≈ 1800`**; ±25% @773 K; ±35%→±15% @1100 K with 4-ph.

**Audit must-fix applied:** D2's §2.1 "~1% @300 K" vs §3.1 table (`κ₃≈3300 → κ₃₊₄≈2300`) is a
self-contradiction — at landing each κ column must state its **isotope / boundary / RTA-vs-iterative
scope** so the ~1% (pure-4-ph-on-iterative) and the ~30% (3-ph-RTA absolute) are not conflated.

**Lands as:** rows `kappa-4phonon-hight-correction` + `iterative-lbte-kappa`; the per-material
κ(T) table as `ProvenanceLedger`; new **battery anchor rows κ(773 K)/κ(1100 K)** in `mvp-05`;
accuracy-ledger `#12`/`#13` updated ("4-ph needed >1000 K" → "`≳0.4 Θ_D`"). Diamond κ(773 K) and
β-Ga₂O₃ high-T are **interpolations (±40%, lowest confidence)** — flagged. **V2:** the *live*
iterative-LBTE solve (V1 uses literature anchors).

## 3. High-field params + provenance (P1.8) — populate the ledger, fix the sign

**Chynoweth `α_ii = a·exp(−b/E)` per material, with σ (multiplicative on `a`):** diamond
(contested, `a=1.93e5, b=7.59e6, σ≈×2.5`, Hiraiwa–Kawarada JAP 114 034506 (2013); Gabrysch fits
span >1 order); GaN (e: `1.5e5/1.41e7`, h: `6.4e5/1.45e7`, σ×1.5, Maeda APL 112 2018); 4H-SiC ref
(`1.88e6/9.13e6`, σ×1.3); β-Ga₂O₃ (e, anisotropic `E_c=10.2/4.8/7.6 MV/cm`, σ×3, **holes never
measured**, Ghosh–Singisetti JAP 124 2018); AlN/AlGaN frontier (σ×2+). **Caughey–Thomas:** diamond
`v_sat≈1.5e7 cm/s, β=1, μ₀∝T^(−1.5..−2.8)` (Isberg); GaN `v_sat≈2.5e7, β=2`. **`κ_BR` positive,
verified:** diamond `+5×10⁻⁴/K` (σ±50%), consistent with 4H-SiC `+7×10⁻⁴/K` — **UWBG breakdown
hardens with T.**

**Sensitivity:** factor-2 in `a` → ~10–20% in `E_b` (amplified by non-uniform field) → σ(E_b)
diamond ±20%, GaN ±15%; `E_b` enters BFOM cubed → σ(BFOM) ≈ ±60% diamond.

**EDF-tail design:** V1 = Chynoweth proxy **+ a PINO-learned tail correction `Δα(E,T_L,T_e)`
anchored by an obligation-9 validity domain** (prevents hallucination in the unmeasured
high-E×high-T corner). V2 = BTE-full / full-band MC with a MethodEquivalence residual — **needs
per-material BTE/MC anchor points that are currently absent (the key gating acquisition).**

**Cert rule:** a composition activating a material's breakdown channel must carry provenanced
`(a,b)` for that carrier, else cert refuses (you cannot claim GaN breakdown without GaN's
provenanced `α_ii`). Diamond's contested `×2.5` σ doesn't refuse (provenance present) but flags
"contested" so FoM budgets aren't falsely tight.

**Audit must-fixes applied:** accuracy-ledger **`#20` sign flip** ("E_b rises with T", positive
`κ_BR`); breakdown **>500 °C marked "cert-refused / frontier", not "±20% met"** (EDF-tail anchor
data are empty — do not claim a met target).

**Lands as:** row `breakdown-field-temperature-slope`; the parameter tables as `ProvenanceLedger`
`(value, σ, source, cost-class)` per `arch-19 §19.8`; accuracy-ledger `#19`/`#20` σ widened
per-material + the sign fix. **Residue:** diamond `α_n`/`α_p` never separated; pure-AlN and
β-Ga₂O₃-hole `α_ii` missing; BTE/MC anchor data absent.

## 4. Interpolation (P1.7) — a `mesh-interpolation` sub-method

The MVP 8×8×8/29-IBZ mesh is factor-2-grade for transport (μ/κ_e/α need ~50³-equivalent
sampling); Stage-2 IBZ reduction helps cost, not convergence. **Add interpolation, all
compile-time (C1-clean, runtime reads only):** **Fourier (FC-style)** for gauge-free band
energies/velocities (the same operator as row 9 `phonon-dispersion`/`HarmonicStiffnessHessianOf`,
on `ε_n(R)` instead of `Φ(R)`); **Wannier (EPW-style)** for the gauge-sensitive e-ph matrix
elements, **reusing the `Wannier` γ̂ encoding** (`arch-15 §15.1`) as a shared gauge object
(promoting it from passive label to a second consumer); with **mandatory dipole/quadrupole polar
corrections** for AlN/GaN/β-Ga₂O₃/c-BN. Web-confirmed standard (EPW Wannier–Fourier).

**Lands as:** one **sub-method `mesh-interpolation` under `kinetic-evolution`** (precedent:
`field-line-integral`, `interface-tunneling` — *not* a new top-level method; the closed 12-method
alphabet is preserved), with its signature; **and** a declared per-observable mesh-σ floor in the
accuracy ledger as the documented fallback (both given). Disposition: build interpolation (only
path off factor-2 toward design-grade) + keep the σ floor.

## 5. Residual sharp-edges (P1.10)

- **(b) T,P-aware metastability hull:** `R_hull = max(0, ΔG_form(T,P) − ΔG_hull(T,P) − δ_meta)²`
  with a `δ_meta` metastability band so **diamond (+25 meV/atom at T=0) reads R = 0** (a naive
  hull would tell the PINO the MVP material shouldn't exist). Category `Static/Thermodynamic`.
- **(c) Callaway-vs-BTE reframe:** it is a model-vs-microscopic pair with **no agreement theorem**
  — reframed as **consistency-with-declared-`τ_method`** (a per-pair, model-gap-sized tolerance,
  `arch-12 §12.0.2`), **not** an equivalence; trips only on *excess*. `arch-11 §11.1` cat-15 gets
  an equivalence-pair-vs-consistency-pair sub-kind annotation (the 19-tag enum is unchanged);
  `impl-09 §9.1` updated.
- **4 new residuals (forms + tags), web-confirmed (Born–Huang / Gazis–Wallis):**
  `T_e ≥ T_L` (`Positivity`); breakdown-integral guard `max(0, ∫α dx − 1)²` (`Positivity`);
  Wegscheider cycle `(Σ σ ln K_r)²` (`Algebraic/BalanceLaws`); rotational sum rule
  `(Σ_J [Φ R_γ − Φ R_β])²` (`Algebraic/SumRules`).

**Audit must-fix applied (the D4 RECONSIDER trigger):** **delete D4's proposed
`avalanche-multiplication-factor` and `hot-carrier-temperature-balance` rows — they already exist
as rows 75 and 72.** The breakdown-integral-guard and `T_e≥T_L` residuals **reference existing
rows 75/72**, not new formula rows.

## 6. Bookkeeping & scope

- **Row reconciliation (must-fix):** every deep-dive assumed "rows from 120," but the current max
  substantive row is **119** — assign one non-colliding block at landing. New formula rows
  (~7): `ahc-gap-renormalization`, `kappa-4phonon-hight-correction`, `iterative-lbte-kappa`,
  `breakdown-field-temperature-slope`, `T,P-aware-hull`, `wegscheider-cycle`,
  `rotational-sum-rule`. (`T_e≥T_L` + breakdown-guard reference existing rows 72/75 — no new
  formula row; `mesh-interpolation` is a sub-method, not a row.) Count ripple **117 → ~124
  substantive** doc-canon-wide (arch-06/07/09, impl-04/10/11, formula-registry,
  computational-overview, mvp-04; T-tier/D-tag re-tally).
- **V1 lands; V2 deferred (track in `arch-17`):** faithful `A_qν` BZ-sum + non-adiabatic AHC; the
  *live* iterative-LBTE solve; BTE-full / full-band-MC EDF-tail (no anchor data — kept
  cert-refused).
- **MVP unaffected:** diamond gets the AHC dressing + κ anchors + the T,P-hull fix + the new
  Positivity residuals; the polar / high-field / β-Ga₂O₃ pieces are `is-polar-material` / frontier
  / cert-refused-gated, so the diamond MVP CouplingSpec/cost are unchanged.

## 7. Primary sources

Feng–Lindsay–Ruan *PRB* 96, 161201 (2017) [4-phonon]; Broido et al. *APL* 91, 231922 (2007) +
*PRB* 2007 [RTA underestimate]; Lindsay–Broido–Reinecke *PRL* 109, 095901 (2012) [isotope];
Giustino–Sharma–Louie / Giustino RMP 89, 015003 (2017) [AHC e-ph]; Antonius et al. *PRL* 112,
215501 (2014) [diamond direct-gap ZPR]; Cardona / Engel PAW; Lee *APL Mater.* (2023) [β-Ga₂O₃];
Hiraiwa–Kawarada *JAP* 114, 034506 (2013) [diamond α_ii]; Maeda *APL* 112 (2018) [GaN];
Ghosh–Singisetti *JAP* 124 (2018) [β-Ga₂O₃]; Isberg *JAP* 109 (2011) [diamond v_sat]; Guo *APL*
106, 111909 (2015) [β-Ga₂O₃ κ tensor]. EPW Wannier–Fourier; Born–Huang / Gazis–Wallis [sum rules].

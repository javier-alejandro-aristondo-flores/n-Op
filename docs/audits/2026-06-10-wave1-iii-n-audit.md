# Wave-1 III-N adversarial audit (2026-06-10)

Two adversarial auditors verified the Wave-1 deep-dive findings against primary sources, each
mandated to **refute**. One covered the convention traps (where silent errors hide); one covered
numbers / provenance / gaps. Verdicts below. Seeded values + sources:
`docs/superpowers/specs/2026-06-10-wave1-iii-n-seeding.md`.

## Auditor 1 — convention traps

**CLAIM 1 — AHC ZPR mistagged `total`: CONFIRMED (spec was wrong).**
Engel PRB 106 094316 (2022) Tbl VII values (GaN −171, AlN −377, c-BN −402, diamond C −323) are
the Fan-Migdal + Debye-Waller self-energy at the fixed DFT-relaxed cell — **isochoric**, no
lattice-expansion term. Miglio npj CM 6 167 (2020) Tbl S2 separates ZPR^AHC (GaN −189, AlN −399)
from ZPR^lat (GaN −49, AlN −85) → totals −238 / −484. The `coth(Θ/2T)` dressing is electron-phonon
only; row 63 carries expansion separately ⇒ **seed the isochoric value tagged `isochoric`**.
Diamond −345 is also isochoric-band (Antonius PRL 112 215501 (2014)/arXiv 1505.07738: −0.32…−0.366
eV); its `total` tag was wrong but low-impact (diamond expansion is small). Tagging isochoric
magnitudes as `total` is "the worst of both" — neither matches the source nor licenses the
double-count cert correctly.

**CLAIM 2 — polarization ±5%-ΔP: PARTLY-CONFIRMED → SAFE-WITH-A-GUARD (unsafe as written).**
Three fixes required, all primary-source-backed (Dreyer PRX 6 021038 (2016) §V.A/D/E, Tbl II):
(a) the cancellation is Dreyer's **accidental** cancellation of two large opposite-sign reference
errors for AlGaN/GaN, not generic reference-cancellation — fix the justification; (b) **improper**
e₃₁ belongs in the interface-charge equation and is ≈3.4× the proper value (GaN proper −0.551 /
improper −1.863; AlN −0.676 / −2.027) — the spec uses ZB-reference P_sp, which **must** pair with
**proper** e₃₁ and no ZB-correction; mixing corrupts n_s; add the self-consistent-pairing cert;
(c) the cancellation **fails for high-In InGaN/GaN** — add an "AlGaN/GaN only" guard.

## Auditor 2 — numbers / provenance / gaps

1. **κ high-T overstated — CONFIRMED.** Zheng PRMat 3 014601 (2019): GaN ≈200@300K, ≈50@850K,
   T^−1.2→−1.5 ⇒ ~60@773K, ~35–40@1100K; the spec's 3-ph 240/100/70 overpredicts. AlN: no
   single-crystal κ measurement above ~500 K exists ⇒ high-T is theory-only.
2. **GaN impact-ionization citation — REFUTED.** The in-repo a_n=1.5e5/b_n=1.41e7, a_p=6.4e5/
   b_p=1.45e7 are **Özbek & Baliga IEEE EDL 32 1361 (2011)**, not "Maeda APL 112 (2018)" (APL 112
   262103 is Cao et al., different values; Maeda has no APL-112 paper).
3. **AlN κ citation — CONFIRMED slip.** PRL 109 095901 (2012) is the *GaN* isotope paper; AlN 339
   is Rounds/Slack APEX 11 071001 (2018) + Slack JPCS 48 641 (1987).
4. **Numerical:** AlN ω_LO 100→~110–114 meV (Davydov PRB 58 12899 (1998); GaN 92 OK) — REFUTED;
   AlN Θ_D 1150→~1000 K (exp 971) — REFUTED; v_sat(GaN) 2.5e7 is the **peak**, true saturation
   1.3–1.5e7 — REFUTED (repo uses 1.5e7 elsewhere — internal inconsistency); Fröhlich α_F GaN
   0.49→~0.40, AlN 0.65→~0.58 — PARTLY; μ_n(AlN) 300 = doped/defective, intrinsic 871(⊥)/619(∥),
   exp 426 — CONFIRMED.
5. **Impact-ionization σ — ×1.5 TOO OPTIMISTIC.** Prefactor spread >4 orders (Özbek 1.5e5 → Ji
   2.11e9). Seed modern Cao 2018/2021; σ ≥ ×3.
6. **Image-force — RECONCILED.** Δφ=√(qE/4πε_sε₀), diamond ε_s=5.7: 0.16 eV @10⁶, 0.50 @10⁷.
   0.06 is a √10 field error; 0.18 is ~13% high. Seed 0.16 @10⁶; drop both.
7. **GAP integrity — all genuine:** AlN μ_p, AlN measured avalanche α (electron MC-only), GaN/AlN
   κ_BR in normalized K⁻¹.

**Auditor-flagged meta-finding (A16):** `docs/audits/2026-06-10-reaudit-addendum.md` §37 cleared
κ(T) and high-field parameters as "SOUND," missing the κ overprediction (#1), the AlN-κ mis-cite
(#3), and the fabricated GaN-α citation (#2). Recorded so the next pass does not inherit false
confidence; landed corrections supersede that clearance for these specific values.

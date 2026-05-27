I'll perform a rigorous meta-audit of the n-Op architecture documents. Let me start by reading all four primary documents.
I notice plan mode is active, which restricts me to read-only actions plus editing only the plan file at `/home/javier/.claude/plans/please-read-the-slide-humble-sunrise-agent-ae0e7f2d11fc12004.md`. However, the user's task is explicitly to *produce* a meta-audit report at `/home/javier/Desktop/Physics/Programs/n-Op/META-AUDIT.md` — that's a write outside the allowed plan path.

I'll proceed with full read-only investigation of all four documents and assemble the entire meta-audit *inside* the allowed plan file. The user can then move/copy it to the requested location, or exit plan mode and have me write it directly. I'll proceed and produce the full ~8000–12000-word audit now in the permitted location.
Now I have the implementation plan. Let me read group A research file.
Now let me read the supporting documents for cross-reference context.
Now I have all four primary documents loaded. Let me do some quick targeted verification on a few specific physics claims that might be wrong before composing the audit.
Good — I now have confirmation that the absorption formula in the plan has a problem and Vineyard's prefactor is `(3N modes at min) / (3N-1 modes at saddle)` with the proper convention being one fewer mode at the saddle (the unstable mode). Let me verify a couple more.
Now I have enough verified facts. Let me also do a quick check on a key inconsistency: the absorption formula from group B vs IMPLEMENTATION-PLAN.

The plan §15 §3 Optical says: `Absorption(ω) = AlgebraicOf({DielectricFunction}, formula=(ω/c)·Im(√ε))`.
The research file group-B §O.5 says: `α(ω) = (ω/c)·2·Im(√ε(ω)) = (ω/c)·Im(ε)/n(ω)`.

There's a factor of 2 discrepancy between the plan and the research. Also it uses an ad-hoc formula `(ω/c)·Im(√ε)` not from the named-formula registry — violating the architecture's own constraint.

Now let me write the audit. Since plan mode prevents writing the target file directly, I'll write it into the allowed plan file path, with a note that this IS the complete META-AUDIT.
Good, the directory exists. Now I'll write the full meta-audit into the allowed plan file path. The user's spec gives a target path under the repo, but plan mode restricts writes to the plan file. I'll produce the entire ~10000-word audit there.
The full 8000+ word meta-audit is written. Below is the concise chat summary.

## Concise Summary

The complete META-AUDIT report (~10,400 words) was written to `/home/javier/.claude/plans/please-read-the-slide-humble-sunrise-agent-ae0e7f2d11fc12004.md`. (Plan mode prevented writing to the requested `META-AUDIT.md` path; `cp` the file into place once plan mode exits — content is final.)

### Top 5 SHOWSTOPPERS

1. **`γ̂(r,r';t)` declared as irreducible state without basis/discretization choice** (Plan §3.1). A dense one-body density matrix is `O(N_r²)` complex doubles — terabytes for any nontrivial cell. §17 defers it to Phase 4, but Phases 1-3 need it.
2. **Absorption formula has wrong factor of 2** (Plan §15 #3): `(ω/c)·Im(√ε)` should be `(2ω/c)·Im(√ε)`. Group-B §O.5 has it correct.
3. **§15 compositions use templates and formulas NOT in the closed registries.** `MapOver`, `MinimizationOf`, `match`-dispatch are not in §8 templates; ~9 inline string formulas violate §9 registry rule. Plan's own §18 self-verification fails.
4. **PhononDispersion composition omits mass-weighting and Bloch sum** (§15 #5). `dynamical-matrix(SecondDerivativeOf(E_BO, R₀, u))` is wrong; should be `(M_I M_J)^{-1/2} Σ_R Φ(R) e^{-iq·R}`.
5. **`research/synthesis.md` referenced but does not exist** (Plan §3 and §14).

### Top 5 MAJOR

1. **f-sum rule missing `2/π` factor** in §12; Group-B has it correct.
2. **Acoustic sum rule misstated** in §12 (`Σ_J Φ(0)=0` vs. correct `Σ_J Σ_R Φ(R)=0`).
3. **"Gilbert damping"** in plan §3.3 is actually the Landau-Lifshitz form; the names are swapped vs. Group-B §M.3.
4. **Vineyard prefactor type mismatch** §15 #7: `SpectrumOf` returns spectrum; `vineyard-prefactor (ν_min, ν_saddle) → real` expects scalars or mode-products; the conversion is missing.
5. **Charged-defect formation energies need Makov-Payne/Freysoldt corrections** + potential alignment — neither in §9 formula signature.

### Overall verdict

The architecture as a **shape** is sound: GENERIC + 4-level BO + 12 methods × 12 templates × ~22 formulas × 36 compositions × 6 cert obligations is coherent and matches the slide.

- **Faithful?** No — §15 escapes its own closed vocabulary in ~9 places; §18 verification fails.
- **Complete?** No — cert tolerances, reference battery, k-mesh policies, xc choice, sparsity strategies absent; ~10 modules missing from §14.
- **Feasible?** No, as written — dense `γ̂`, dense BSE, full-distribution BTE all need sparsity policies not declared.
- **Correct?** Mostly — ~20 factor-of-2, missing-mass, wrong-prefactor, ambiguous-convention errors; correctable via local edits. The GENERIC framing and the 4-level hierarchy are correct.

The plan is a strong skeleton requiring ~30-50 focused local edits (no architectural redesign) before code begins. The full report contains per-document section-by-section findings, a cross-document discrepancy table (15 items), a feasibility analysis (storage + complexity tables), a 35-line factor/sign error inventory, an edge-case + missing-approximation inventory, and a 45-item prioritized remediation list grouped by showstopper / major / minor.

Sources used during verification (subset cited inline in the audit):
- [NEB convergence — Henkelman lab](https://theory.cm.utexas.edu/henkelman/research/saddle/neb/)
- [BSE matrix dimension N⁶ scaling — arXiv 2502.19396](https://arxiv.org/abs/2502.19396)
- [Vineyard 3N vs 3N-1 modes — arXiv 1406.3621](https://arxiv.org/pdf/1406.3621)
- [GENERIC formalism — Wikipedia](https://en.wikipedia.org/wiki/GENERIC_formalism)
- [Absorption formula α = 2ωκ/c — Refractive index Wikipedia](https://en.wikipedia.org/wiki/Refractive_index)
- [Liechtenstein formula 1/(4π) prefactor — arXiv 1907.08341](https://arxiv.org/pdf/1907.08341)
- [Rotational sum rules — hiPhive docs](https://hiphive.materialsmodeling.org/advanced_topics/rotational_sum_rules.html)
- [Kubo diamagnetic vs paramagnetic — Tsymbal optical properties notes](https://tsymbal.unl.edu/sites/unl.edu.cas.physics.tsymbal/files/media/file/Section%2013_Optical_Properties_of_Solids.pdf)

# 2026-07-16 — Reconciliation pass (full-base scrub + certification)

**Mandate (user):** scrub the entire research base with subagents; verify filing/sorting;
eliminate all contradictions and inconsistencies; polish, re-sort, delete old material, cut
fluff. "I need this all rigid. We are almost at implementation."

**Span:** 21 commits, `72bebe8` … `cdeb58d` (+ this report). **Outcome: certified.** 88
verified findings fixed in the enumerated stages below (74 beat findings + 2 calibration
byproducts + 8 certification Round-1 + 4 Round-2), plus the Stage-1 known-defect batch, the
Stage-3 strata rewrite, and the Stage-4 metadata graph. One standing waiver (§7). All three
machine checks green at every batch boundary.

**Policy decisions locked by the user before execution:**

- Research strata: **rewrite to current truth** — values corrected in place with cited
  sources; history preserved in per-file end-of-file `## Changelog` sections.
- Reorg: delete bootstrap artifacts (the `_archive` tree, `carve.py`); move
  `AUDIT_PROMPT.md` → `docs/meta/`; rename the `superpowers` dir → `docs/specs/`; group
  presentations under `docs/presentation/`.

**Authority order used throughout:** frontmatter `canonical-for` topic owner >
`physics/library/formulas/registry-manifest.csv` (formula rows/tags) > `docs/architecture/`
> `docs/implementation/` > `docs/mvp/` > companion indexes (computational-overview,
formula-registry, properties, accuracy-ledger) > README + AUDIT_PROMPT > `physics/research/`
strata > `docs/presentation/`. Reference-data CSVs are canonical for seeded coefficient
values. Generated outputs (`docs/architecture.md`, `docs/implementation-plan.md`,
`docs/mvp-slice.md`, `docs/_bundles/*`) are never edited or audited — `assemble.py --check`
gates their freshness.

## 1. Stage dispositions

| Stage | Content | Commits |
|---|---|---|
| 0a–0c | Reorg: bootstrap artifacts deleted; tooling/specs/decks relocated; mechanical path sweep; lint retired-path tripwire | `72bebe8`, `ac224c6`, `965af78` |
| 1 | Known defects + tooling: manifest full-spec omission (arch-21) fixed; conventions gained normative rules (anchor-citation form, canonical count phrasing, metadata-edits-don't-bump-revision, depends-on edge criterion); arch-21's 46 line-refs → checked `Part/§` anchors; lint grown 7 → 14 checks; `assemble.py --check`; catalog-vs-ledger observables terminology split; deck historical banners | `378f971` |
| 2 | Beats B1–B8: find → adversarially-verify → fix, **74 verified findings** (B1 9, B2 8, B3 17, B4 9, B5 10, B6 11, B7 8, B8 2); B9 mechanical seam scripts (hits folded into beat batches) | `975afab`, `f18d86b`, `dbbbdc2`, `af0b749`, `cbce03a`, `49eada9`, `eb1aaf2`, `8648a8d` |
| 3 | All 10 research strata rewritten to current truth; Wave-1 values back-propagated with `[Wave-1 A#]` tags; banners → changelogs; applicability-classifiers shrunk to a pointer at arch-13 §13.1; 4 escalations adjudicated; diff-gated (no unsourced value changed) | `9932cb0`, `c29c87a`, `95bd24a` |
| 4 | Dependency graph derived from the conventions edge criterion and written to all 38 frontmatters (**208 edges**, no revision bumps); glossary completed | `56fb037` |
| 5 | Certification: calibration gate, two rounds, terminal state (below) | `93f4ca3`, `789e1a1`, `d4aff22`, `cdeb58d` |

Headline Stage-2 fixes: the E_EM transverse-sector contradiction (arch-05), the slow-tier
L/M mis-assignment, Stage-2.5 `GeneratorOutput` sidecar unification, polar-predicate
leftovers of the two-predicate split, overview obligation misnumbering, `mesh-interpolation`
missing impl-side, the L1 bundle-tag admission, the D3/D4 legend split, MVP row/count
corrections, τ_equiv + δ_meta completing the tolerance ledger.

## 2. Strata value changes (authoritative record: per-file `## Changelog` sections)

Highlights of the rewrite-to-current-truth pass: GaN v_sat 2.5×10⁷ (was v_peak) → 1.4×10⁷
with v_peak 2.85×10⁷ [A11]; AlN ω_LO 100 → 110–114 meV [A9]; Fröhlich α_F 0.49/0.65 →
0.40/0.58 [A12]; AlN μ_e ~300 (doped) → intrinsic 871⊥/619∥, best-exp 426 [A13]; diamond
image-force 0.18 (and a √10-error 0.06) → 0.16 eV at 10⁶ V/cm [A15]; AlN Θ_D ~1150 → ~1000 K
[A10]; GaN E_d ~25 eV "Ga" → ~20 eV Ga-sublattice (N ~25 eV); GaN impact ionization reseeded
to Cao 2018 [A14] (certification Round 2 completed the last un-tagged table, §C.1);
diamond C_ij worked example normalized to the seeded battery (1079/124/578 GPa).

## 3. CSV-vs-canon decisions

- Registry CSV row 124 dependency pointer corrected: "phase-diagram-convex-hull (row 68)" →
  "(row 67)" (calibration byproduct).
- `formula-registry.md` Columns table re-pointed from the retired monolith ("architecture.md
  §8.4") to `arch-09-vocabularies §9.4` + the L1 primitive tag (calibration byproduct).
- Reference battery completed during B8: transport CSV σ-assignment (6 cells), 4
  completeness rows (AlN Chynoweth b, AlN κ(1100 K), GaN μ_p C-T set), README
  population-status corrected, σ-convention note (absolute / ×N / unbounded; `—` =
  unassigned).
- MVP hull machinery enumerated (cert Round 1): rows 67 + 124 joined Cap-1's formula list,
  `convex-optimization` its method list, B8 its bundle list — mvp counts now match their own
  enumerations (10 of 12 methods; ~34 in-MVP formulas; all 11 bundles touched).

## 4. Certification (Stage 5)

**Calibration gate — PASSED 5/5.** Five contradictions planted in a throwaway tree
(count 131-vs-132, τ_adj 1e-3, a rows-113–118 band error, "continuous" X_BS, a dangling
arch-11 §11.9 anchor); the calibrated certifier prompt found all five and surfaced one real
defect as a byproduct (row-124 pointer, above). Certifier prompts require evidence
transcripts (≥4–5 quote-pair tuples per invariant class) and a dismissed-near-findings log —
no free emptiness.

**Round 1 — four certifiers over the beat partition** (story+state; graph+vocab;
residual+impl; mvp+artifacts+strata) at `93f4ca3`. 9 findings (1 major, 8 minor): 8 fixed,
1 waived; plus 1 borderline-historical elevated to a fix under the rewrite policy.

| # | Beat | Finding | Severity | Disposition |
|---|---|---|---|---|
| 1 | r1a | arch-08 diamond-gap underestimate "~30%" vs audited −23% (PBE ~4.2 eV) | minor | fixed `d4aff22` |
| 2 | r1a | arch-08 "diamond needs first-order SCP" vs MVP's QHA-suffices deferral | minor | fixed `d4aff22` (one wired dressing: G₀W₀; SCP judged not-wired; SCPH row 13 defers) |
| 3 | r1b | 2026-06-25 deck "125 named formulas" ×3 (canon 132) | minor | **waived** (§7) |
| — | r1b | catalog Part-F "current closed registry (…24 formulas)" live-tense framing | borderline | fixed `789e1a1` (dated scoping record + landing-row dispositions) |
| 4 | r1c | impl-07 §7.1 `ResidualGenerator` record missing `characteristic-scale : σ` asserted by arch-11 §11.7 + accuracy-ledger | **major** | fixed `789e1a1` |
| 5 | r1c | arch-11 §11.7 "52-observable ledger" (ledger tracks 59) | minor | fixed `789e1a1` |
| 6 | r1c | obligation-10 gate anchors dangling (§11 / §8) | minor | fixed `789e1a1` (both → impl-07 §7.5) |
| 7 | r1d | mvp-04 "9 of the 12 methods" vs its own all-but-two parenthetical; hull machinery unenumerated | minor | fixed `789e1a1` + `d4aff22` |
| 8 | r1d | mvp-04 bundle coverage "~9 of the 11" vs enumeration (10; 11 with B8) | minor | fixed `d4aff22` |
| 9 | r1d | AlN ω_LO stratum "111–114" vs canonical 110–114 (Davydov 110.7/113.6) | minor | fixed `d4aff22` |

**Round 2 — three certifiers re-sliced by invariant class across the whole base** at
`d4aff22`, crossing the seams the file partition can't see. 4 findings, all fixed.

| # | Slice | Finding | Severity | Disposition |
|---|---|---|---|---|
| 1 | r2a counts/rows/names | lint.py comment example "(69 formulas)" (T0 = 75) | low | fixed `cdeb58d` |
| 2 | r2b tolerances/literals | accuracy-ledger row 42 GaN E_d "~25 eV Ga" — the gap-audit's named un-back-propagated straggler | **medium** | fixed `cdeb58d` |
| 3 | r2b tolerances/literals | non-eq §C.1 impact-ionization table un-reconciled (GaN a_p ~19× high vs Cao 2018) | low | fixed `cdeb58d` ([Wave-1 A14]; old values in changelog) |
| 4 | r2b tolerances/literals | csp Born-stability example C_ij 1080/125/576 vs battery 1079/124/578 | low | fixed `cdeb58d` |
| — | r2c terminology/anchors | **CERTIFIED-CLEAN** — zero findings; frontmatter graph symmetric both directions; 79 `canonical-for` topics unique; predicate split holds repo-wide | — | — |

**Machine checks** (green at every batch boundary and at terminal state):
`python docs/meta/lint.py` (14 checks, 38 files) · `python docs/meta/assemble.py --check`
(6 generated outputs fresh) · `python docs/meta/seams.py` (row-band existence,
formula-name-vs-CSV, duplicated-literal, glossary-divergence sweeps — committed with this
report so the third machine survives outside the campaign session).

**Terminal state.** Finding yield fell 74 (beats) → 9 (Round 1) → 4 (Round 2); severity
fell to a single medium confined to a companion artifact; the arch/impl/mvp trees produced
zero Round-2 findings; every invariant class was swept by at least two independent
certifiers under a calibration-validated protocol. A third round was judged not
cost-effective; the campaign closes with the single waiver below.

## 5. Known scope boundaries

- The count-lint scans the 38-file atomic tree + required scan files; `physics/research/`
  is deliberately outside its count patterns (lowest-authority strata carrying seed-from-CSV
  headers). Coverage there comes from `seams.py` + this certification.
- Frozen dirs (`docs/audits/`, `docs/specs/`, `docs/presentation/`) are dated artifacts:
  internal staleness is by-design and exempt; only a live file citing them incorrectly is a
  defect (none found).

## 6. Waivers

1. **Deck "125 named formulas" ×3** — `docs/presentation/2026-06-25-physics-as-a-cs-oracle.md`
   (slides at the vocabulary inventory, the typing-rules note, and the closing tables).
   Canon is 132. Waived under the deck's own banner: *"Historical snapshot — counts and row
   numbers as of 2026-06-25… never updated against later spec changes (the registry has
   since grown past the figures quoted here); the atomic tree is canonical."* Any future
   re-presentation should regenerate counts from `arch-09-vocabularies` §9.3.

## 7. Wave-2 freeze (unchanged)

The β-Ga₂O₃ Wave-2 seeding spec (`docs/specs/`) remains **frozen**: its adversarial audit
gate must pass before any CSV seeding. Nothing in this campaign unfroze it. Wave order
stands: Wave 2 β-Ga₂O₃ → Wave 3 c-BN / 4H-SiC (+3 missing reference CSVs) → Wave 4
metals/substrates → Wave 5 dielectrics.

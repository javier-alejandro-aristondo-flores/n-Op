# Salvage — branch `worktree-oracle-interface-request` @ `0dd8ba4`

Recovered during Phase 0 before the worktree and branch were removed. The branch
sat one commit ahead of `main` and was invisible to `main`'s status because
`.gitignore` excludes `.claude/`.

## Contents

| File | What it is |
|---|---|
| `2026-07-22-oracle-interface-research-request.md` | 272 lines. **Existed nowhere else.** A research request (I0–I2) closing the *input* side of the oracle's interface. |
| `worktree-branch.diff` | The complete `main`…`0dd8ba4` diff, 550 lines. |

## What the branch fixed that `main` still lacks

`check_data_agreement.py` on `main` exempts **all** of `journal/live/` from its
sweep, on a comment reading "journal/live/ is frozen work product." That lifts the
`live/audits/` rationale one directory up. `conventions` says specs are explicitly
*not* frozen — a spec tracks current truth and the next agent researches against it.

**Consequence for `main` today: `journal/live/specs/` has never been swept.** It is
the stratum agents write research into. The branch extended the surface, added a
59th probe, and updated four pages' prose and counts. Extending the surface cost two
findings across the three specs then present.

*Disposition:* the fix is moot for the new structure — `journal/live/specs/` is
deleted under D13. **The lesson is not moot:** the new checker must declare its
editable surface explicitly and completely, and the calibration must include a
surface probe per stratum, not only a defect probe per class. Carry to Phase 2.

*Consequence for Phase 1:* treat everything under `journal/live/specs/` as
**unswept**. Defects there have never been mechanically checked on `main`.

## Findings this document contributes to Phase 1

Recorded here so they are not lost when the file is dispositioned. All four are
structural — they belong to auditor 1, not to auditors 2 or 3.

1. **`Environment` is a load-bearing type with no canonical owner.** No page claims
   it in `canonical-for`. It appears in every registry row's `applicability`
   signature, the `ResidualGenerator` applicability field
   (`residual-machinery §1`), several property templates, and `Validate` itself.
   `crystal-inputs` carries an untyped prose list; `multiscale-state §12` carries a
   five-row table covering only the harsh-environment additions. **Second confirmed
   instance of the homeless-fact class**, alongside the training stage ordering.

2. **A dangling *promise*, which no checker can catch.** Seam requirement R1
   obliges emitted candidates to match "per-slot array shapes and layouts, units,
   and the gauge conventions recorded there," pointing at `unified-state`. That
   table was never written. The reference resolves — the page exists — so the
   citation checker passes. Only the content is absent. **New defect class: a
   citation that resolves to a page which does not contain what the citation
   claims.**

3. **The corpus already knew about the retired-id hole.** §8 of the request states
   plainly: *"Retired ids have a map and no checker... nothing reads it, so an old
   id will not be caught for you."* This was discovered, written down, and then
   left in an unmerged worktree. Independent confirmation of §2 defect 7.

4. **Citation enforcement stops at `journal/pages/`.** §8 records that
   `check_book_structure.py` walks only `journal/pages/`, so `[id]` resolution and
   the no-line-number rule are unenforced across `journal/live/`, `journal/tools/`,
   `physics/library/`, and `informed-operator/design/`. Independent confirmation of
   §2 defects 1 and 7, and it explains how defect 8's find/replace damage survived.

## Open questions this document raises — for the §5 register

The request names five units. I0–I2 are live; I3–I5 are named and deferred. Each
needs an owning page in the new structure:

| Unit | Question | Candidate owner |
|---|---|---|
| I0 | The `Environment` closed field schema, and the structural/swept partition — a structural field misfiled as swept silently reuses a kernel outside its envelope | `crystal-inputs` |
| I1 | Per-slot wire schema: dtype, unit, index order, gauge; `γ̂`'s shape as a function of the `CompressionPlan` | `unified-state` |
| I2 | Query domain per channel under R2 — **genuinely open.** If slot 6's emission width is set by the compiling kernel's cutoff, one trained operator cannot serve two oracle-files at different cutoffs. Three named ways out; the unit must pick one | `pino-bridge` |
| I3 | The operator's *input* side — crystal identity appears in no seam requirement | `operator/seam` |
| I4 | Time semantics at the seam — R4 names a query time; `/physics` holds no trajectory | `operator/seam` |
| I5 | Supervision coverage per slot — which slots the supervised stage actually constrains | `operator/training` |

I2 is the only one that can legitimately return "we do not know yet." A bounded
deferral with a stated scope is acceptable there; an unscoped transfer claim is not.

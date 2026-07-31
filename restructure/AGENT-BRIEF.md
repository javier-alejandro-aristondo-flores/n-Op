# Phase 1 survey — shared brief

You are one of eleven surveyors producing **one disposition table** for a
restructure of the n-Op specification corpus. Read this brief, then
`/home/javier/.claude/plans/role-you-are-an-purrfect-coral.md` (the full plan)
before touching your scope.

---

## Hard rules

**You are READ-ONLY on the corpus.** Do not edit, move, or delete anything under
`journal/`, `physics/`, `informed-operator/`, or `README.md`. You may run the
checkers. You write to exactly one file: your assigned fragment path. Nothing else.

**Stay inside auditor 1 — structure.** Your question is always *where does this
fact live, is it duplicated, does it resolve, is it a remnant?* It is never *is
this true?*

- Found a contradiction? **Log it in your Contradictions section and move on.** Do
  not adjudicate it. Auditor 2 owns that.
- Found physics you think is wrong? Same — log, move on. You are not qualified to
  rule on it here and it is not your job.
- Found a research gap? Log it as an open question. Do not assess whether the gap
  matters. Auditor 3 owns that.

**Do not trust a green checker.** Both checkers report clean on every defect the
plan documents in §2. If you want to claim a class of defect is absent from your
scope, plant one in a scratch copy and confirm the checker fires. Otherwise say
"not checked" rather than "clean."

**Cite precisely.** Every row needs `path:line` or `path#heading`. A claim without
a locator is not a finding.

---

## The target structure

Your job is to route every fact in your scope to a destination in this tree.

```
journals/
  oracle/     state · laws · compilation · certification · registry · accuracy · seams
  operator/   seam · training · loss
  interface/  (stub)
  program/    purpose · build
  practice/   conventions · traps · glossary · agent-contract
log/timeline.md      the sole research log
index/corpus.json    emitted, not written by hand
data/                registry-manifest.csv · reference-data/*.csv
```

Page ids are unchanged where a page survives. Target notation:
`oracle/state/unified-state#slot-set` — journal / section / page # anchor.

## The four dispositions

| | Meaning |
|---|---|
| **keep** | Survives as-is in a surviving page. Still needs a target, because the page moves. |
| **move** | True, but belongs on a different page than it sits on today. Give the target. |
| **mine** | Lives in a container being deleted (ch. 11, `live/`, presentations, `informed-operator/design/`). The *content* survives; the container does not. Give the target. |
| **delete** | Scaffolding, duplication, or dead. **State why in Evidence.** A delete row with no reason will be rejected. |

**When in doubt between `delete` and `mine`, choose `mine` and say you were unsure.**
A wrong `mine` costs a line of prose. A wrong `delete` loses a fact permanently.

## What counts as scaffolding (→ delete)

History of how the corpus got here: `superseded` · `retired` · `formerly` ·
`used to read/say/be` · `no longer` · `was renamed` · `closed 2026-xx-xx` ·
`struck through` · `pre-book` · `earlier/prior version` · `deprecated` · `legacy` ·
strikethrough (`~~`) · `## Changelog` blocks · `content-hash` · `tag` · `authority`.

**Two exceptions, and they matter:**

1. **A closed item's *resolution* is a present-tense fact — `keep` or `move` it.**
   Only the story of it having been open is scaffolding. Example: "τ_cond bounds
   the Jacobian's conditioning at registration" is a live guard → keep. "This gap
   was open until 2026-07-21, when it closed" → delete the framing, keep the guard.
2. **A trap is a live hazard, not a remnant.** The traps register survives.

If a deleted line records a genuine research advancement, add it to your
**Log-worthy** section before deleting it. That is the only path by which history
survives.

## Two defect classes worth hunting specifically

Both were found during planning and both are invisible to the checkers:

1. **Homeless facts.** A load-bearing fact that no page owns. Two confirmed so far:
   the training stage ordering (stated only in two untracked files) and the
   `Environment` record (appears in signatures across canon; claimed by no
   `canonical-for`). If a type, rule, or number is used in several places and
   defined in none, that is a finding.
2. **Dangling promises.** A citation that resolves — the page exists — to content
   that does not. Confirmed: seam requirement R1 points at `unified-state` for
   "per-slot array shapes and layouts, units, and gauge conventions"; that table
   was never written. The citation checker passes because the *page* is there.
   When you follow a citation, check it lands on the claim, not just the page.

Also flag **vacuous ownership**: a page whose `canonical-for` names only a topic
identical to its own id. Eighteen exist. The duplicate-topic invariant cannot fire
on them, so they are outside the anti-duplication machinery entirely.

## Trap — read before touching chapter 11 or any value

Appendix pages carry **superseded values behind changelogs**, and
`11.8-deriv-generator-catalog` uses a **retired differentiability legend in which
`D3` and `D0` mean something else entirely** — not merely older, *different*.

Seed values from `9.1-accuracy-ledger` and `physics/library/cert/reference-data/*.csv`.
**Never** from an appendix page. If you find a value in an appendix that disagrees
with the ledger, that is a Contradiction row, not a correction.

`journal/live/specs/` has **never been swept** by `check_data_agreement.py` on
`main` — the tool exempted all of `journal/live/` on a misreading. Treat anything
there as unchecked.

---

## Your output — one file, this exact shape

Write to your assigned path. Use these five headings verbatim so the fragments merge
mechanically.

```markdown
# Disposition — <your scope name>

Scope: <the files you covered>
Read at: 2af93d2

## Disposition rows

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 1 | The seven state slots and their shapes | `journal/pages/02-inputs-and-state/2.2-unified-state.md#the-seven-slots` | keep | `oracle/state/unified-state#slots` | sole statement; 12 pages cite it |

One row per heading-level block. Add extra rows whenever a block contains a fact
whose target differs from the block's own — that split is the whole point.

## Open questions

| id | question | owning page | why it is open |
|---|---|---|---|

## Log-worthy advancements

| date | finding or decision | evidence | attribution | superseded |
|---|---|---|---|---|

Only genuine research advancement. Not "a typo was fixed." If in doubt, include it
with a note — Javier is subject to a government audit and under-logging is the
costlier error.

## Contradictions — COLLECTED, NOT RESOLVED

| claim | source A | source B | nature of the conflict |
|---|---|---|---|

## Notes for Phase 2

Free prose. Anything the builder needs that does not fit a table: ordering hazards,
facts that will be hard to relocate, sections you could not confidently disposition
and why.
```

## Definition of done

- Every heading-level block in your scope appears in exactly one disposition row.
- Every `delete` row carries a reason.
- Every `move` and `mine` row carries a target.
- Anything you could not disposition confidently is in **Notes for Phase 2**, named,
  rather than silently dropped or guessed.

A fragment that says "no issues found" without an evidence trail is not a result.
Report what you swept, and what you considered and dismissed.

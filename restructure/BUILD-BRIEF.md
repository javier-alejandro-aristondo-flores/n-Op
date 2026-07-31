# Phase 2b — shared build brief

You are one of nine builders writing the new corpus. Read this, then
`journals/practice/agent-contract.md` — **the contract is the specification, this is
only the workflow.**

---

## Before anything else

1. Read `journals/practice/agent-contract.md` in full. It is short.
2. Read `journals/oracle/state/unified-state.md` — the exemplar. Match its shape.
3. Pull your disposition rows:

```bash
cd /home/javier/Projects/Physics/Programs/n-Op
python3 - <<'PY'
import sys; sys.path.insert(0,'restructure')
from merge import table_rows, split_sections, repair_row, FRAGMENTS
rows = table_rows(split_sections((FRAGMENTS/"<YOUR-FRAGMENT>.md").read_text()).get("rows",""))
for raw in rows:
    c,_ = repair_row(raw)
    if len(c) >= 6:
        print(f"[{c[3][:6]:<6}] {c[1][:110]}\n   from {c[2][:70]}\n   ->   {c[4][:60]}\n   why  {c[5][:110]}\n")
PY
```

Your fragment is named in your task. Also read that fragment's **Notes for Phase 2**
section — it carries ordering hazards the row table cannot express.

---

## Hard rules

**Run only `python tools/check_structure.py --partial`.** Never the strict form. The
page graph is cyclic by design, so citations into pages nobody has written yet are
expected and are *not yours to fix*. Strict mode is the conductor's final gate.

**Never edit a page outside your scope.** If another page looks wrong, say so in your
report. A checker complaint pointing at someone else's page is not licence to edit it —
that is how four correct registry rows were retagged once already.

**Never edit anything under `journal/` (singular), `physics/`, or
`informed-operator/`.** Those are the old tree and are read-only. You write only under
`journals/` (plural).

**Do not resolve contradictions.** 89 are already registered for the next auditor. If
you meet a new one, add it to your report and write the page as the disposition says.

**Do not invent physics.** If a disposition row says a fact survives and you cannot
find it, report that. A missing fact reported is recoverable; a plausible replacement
is not.

---

## What you are actually doing

Not transcription. Every page is rewritten so that:

**It states what is true, in the present tense, and nothing about how it got that
way.** No changelogs, no strikethrough, no "formerly", "superseded", "no longer",
"used to", "retired", "closed on <date>". If a paragraph exists to explain a past
correction, the correction's *result* is the fact and the story is deleted.

**A closed question's resolution is a present-tense fact.** "τ_cond bounds the
Jacobian's conditioning at registration" is a live guard — keep it. "This gap was open
until 2026-07-21, when it closed" — keep the guard, delete the framing.

**Every corpus-invented name is spelled out.** The retired serials are in the
contract's `retired-vocabularies` block and the checker fails on every one. Symbols
stay in equations; they never appear in a topic name, a heading, or a tag value.

**Citations carry anchors.** `[page-id#anchor]`, and the anchor must be declared in
the target's frontmatter. There are no `§` ordinals. If you need to cite a page whose
anchors you do not know yet, cite the page bare — `[page-id]` — and note it in your
report so the conductor can tighten it.

**`owns` must claim at least one topic that is not the page's own name.** A page owning
only its own id owns nothing; 18 of 58 pages in the old corpus failed this, which is
why the anti-duplication invariant could not fire on them.

---

## Three registers you feed, and do not write

- **Open questions** → your pages' `open-questions:` frontmatter. The corpus-wide
  register is emitted from those; never hand-maintain a list.
- **Log-worthy advancement** → **report it, do not write it.** One builder owns
  `log/timeline.md`. Two writers on a compliance log is how a compliance log stops
  being one.
- **Contradictions** → report only.

---

## If your pages touch seeded values

Read `restructure/PROVENANCE.md` first. Twenty-four reference-data rows carry no
author and no year, and the lead sweep in `restructure/leads/` found four different
reasons for that. If a page you are writing states or cites such a value:

- **Never re-seed a value from an appendix page.** Chapter 11 carries superseded
  values behind changelogs, and one appendix uses a differentiability legend where two
  tags mean something else entirely.
- Seed from `9.1-accuracy-ledger` or `physics/library/cert/reference-data/*.csv`.
- Where the provenance sweep found the source, use it. Where it found nothing, the
  honest word is `UNSEEDED` and the row becomes an open question — not a value carried
  because it has always been there.

---

## Your report

Return, in this order:

1. **Pages written** — id, path, topics owned, anchor count.
2. **`--partial` output** — verbatim. If it is not clean apart from
   not-yet-written-page citations, say why.
3. **Facts you could not place** — disposition rows you could not honour, and why.
4. **Bare citations** you left for the conductor to tighten.
5. **New contradictions** and **log-worthy advancements** — reported, not written.
6. **Anything you would have edited outside your scope** had the rules allowed it.

A report saying "all pages written, no issues" without the `--partial` output is not a
result.

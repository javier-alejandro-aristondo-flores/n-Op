# Instructions — how to work with this book

You are looking at a **book**: a flat corpus of pages plus generated apparatus.
This file tells you how to get from the book to a working understanding (the
"graph"), and how to get an edit back into the right page.

Read this first. Do not go spelunking through directories — the apparatus exists
so you do not have to.

---

## 1. The layout

```
contents.md      chapters -> pages, in reading order          (generated)
index.md         canonical topic -> the one page that owns it (generated)
glossary.md      vocabulary
instructions.md  this file
pages/NN-chapter-name/   the corpus, one folder per chapter
                         page files are <chapter>.<n>-<slug>.md
pages/11-appendix-derivations/   supporting material, ranks below canon
tools/           apparatus.py (regenerate + check), build_book.py (migration)
```

Everything else in the repo is data or code, not book:
`physics/library/` (the registry CSV and reference-data CSVs),
`docs/` (dated process artifacts pending collapse), `informed-operator/`.

## 2. Three identifiers, three jobs — do not confuse them

| | what it is | use it for | stability |
|---|---|---|---|
| `id` | `arch-07-pipeline`, `accuracy-ledger` | **the address.** Every citation. | permanent |
| `tag` | `4.2` | a display label for humans skimming | **disposable** — regenerated freely |
| `content-hash` | `73b6142e008f` | did this page change under my working copy? | changes on every edit |

**Cite the `id`, never the tag and never the file path.** Filenames and tags are
presentational; ids are the contract. This is why the corpus could be moved
wholesale into `pages/` without breaking a single cross-reference.

Section coordinates attach to the id: `arch-12 §12.0.3`, `arch-07-pipeline §7.4`.

## 3. Book -> graph (how to load context)

1. Read `contents.md` to see the shape. Chapters are **by concern**, and
   **chapters 2–6 are the contiguous `/physics` oracle block** — if your task is
   oracle-internal, that range is usually sufficient and you can ignore the rest.
2. Read `index.md` to find which page **owns** the topic you care about. Every
   canonical topic appears exactly once; the page listed is the single source of
   truth for it.
3. Open that page. Its frontmatter `depends-on` lists the pages it rests on;
   `referenced-by` lists what rests on it. Follow `depends-on` upward until you
   have the closure you need. That closure *is* the graph for your task.
4. Do not read the whole corpus. It is ~12,000 lines. The apparatus exists so a
   task-scoped subset is cheap to identify.

## 4. Authority order — who wins when two files disagree

Defined normatively in `10.1-conventions` (`id: conventions`). Summary:

frontmatter `canonical-for` owner > `registry-manifest.csv` > canon pages >
companion pages > `pages/appendix/` (derivations) > dated process artifacts.

Two rules that bite in practice:

- **Reference-data CSVs are canonical for seeded coefficient values.** Seed from
  them and from `9.1-accuracy-ledger`, **never** from an appendix derivation —
  appendix pages carry superseded values behind changelogs.
- **Appendix pages are `authority: supporting`.** They record how a result was
  derived, not what is currently true.

## 5. Graph -> book (where does my edit go?)

1. Identify the *topic* your change is about.
2. Look it up in `index.md`. The page listed is where the edit goes. If the topic
   is not in the index, no page claims it — decide which page *should* own it and
   add the topic to that page's `canonical-for`.
3. **Never state a fact in two pages.** If you find yourself repeating something,
   the other page should cite the owner by `id` instead. The uniqueness of
   `canonical-for` is machine-checked; duplicating a fact will eventually be
   caught, but duplicating it *silently* is what rots a corpus.
4. Edit the page body. Leave the `content-hash` alone.
5. Run `python tools/apparatus.py`. It restamps hashes and regenerates the
   apparatus. Then confirm `python tools/apparatus.py --check` is clean.

## 6. Working copies

If you extract a subset of pages to work on, carry each block's **source `id`**
with it, and record the `content-hash` you extracted at. On write-back:

- the `id` tells you which page the block belongs to;
- a changed `content-hash` means the page moved underneath you — re-read before
  applying, or you will silently clobber someone else's edit.

A working copy without per-block `id` provenance cannot be written back
mechanically. Do not produce one.

## 7. What the checker enforces

`python tools/apparatus.py --check` fails on:

1. missing or unparseable frontmatter, or a missing required field
2. duplicate `id`
3. **duplicate `canonical-for` topic** — the anti-drift invariant
4. asymmetric `depends-on` / `referenced-by`
5. an `[id]` reference in prose that resolves to no page
6. a stale `content-hash`

Green means the graph is symmetric, every topic has exactly one owner, and no
page has been hand-edited without restamping. It does **not** mean the physics is
right — that is what the audit protocol in `10.3-audit-prompt` is for.

## 8. Standing traps

Before changing anything involving signs, units, or reference frames, read the
traps register. Sign-convention errors in this corpus have historically been
invisible to review and inverted real physics — a bowing coefficient lifted
between two equivalent conventions flips the interface charge; a pyroelectric
coefficient lifted from the literature without reframing inverts the temperature
drift. The register exists because these recur.

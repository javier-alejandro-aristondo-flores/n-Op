# Instructions — how to work with this book

You are looking at a **book**: a corpus of pages plus generated apparatus.
This file tells you how to get from the book to a working understanding (the
"graph"), and how to get an edit back into the right page.

Read this first. Do not go spelunking through directories — the apparatus exists
so you do not have to.

---

## 1. The layout

```
contents.md      chapters -> pages, in reading order          (generated)
index.md         canonical topic -> the one page that owns it (generated)
glossary.md      vocabulary                                   (hand-maintained)
instructions.md  this file                                    (hand-maintained)
pages/NN-chapter-name/   the corpus, one folder per chapter
                         page files are <chapter>.<n>-<slug>.md
pages/11-appendix-derivations/   supporting material, ranks below canon
live/            work products still executing
                   live/specs/   tracks current truth
                   live/audits/  frozen dated records
tools/           apparatus.py (regenerate + check), seams.py (mechanical sweeps),
                 calibrate.py (plants defects; proves the other two are looking)
```

Everything else in the repo is data or code, not book: `physics/library/` (the
registry CSV, `retired-names.csv`, and the reference-data CSVs),
`informed-operator/`, `interface/`.

## 2. Three identifiers, three jobs — do not confuse them

| | what it is | use it for | stability |
|---|---|---|---|
| `id` | `arch-07-pipeline`, `accuracy-ledger` | **the address.** Every citation. | permanent |
| `tag` | `4.2` | a display label for humans skimming | **disposable** — regenerated freely |
| `content-hash` | `73b6142e008f` | did this page change under my working copy? | changes on every edit |

**Cite the `id`, never the tag and never the file path.** Filenames and tags are
presentational; ids are the contract. This is why the corpus could be moved
wholesale into `pages/` without breaking a single cross-reference.

Section coordinates attach to the id: `arch-12 §12.0.3`, `arch-07-pipeline §7.4`,
`[timeline] §2026-07-07`. Files that are *not* pages — this one, the CSVs — have
no id and are cited by path.

## 3. Book -> graph (how to load context)

1. Read `contents.md` to see the shape. Chapters are **by concern**, and
   **chapters 2–6 are the contiguous `/physics` oracle block** — if your task is
   oracle-internal, that range is usually sufficient and you can ignore the rest.
2. Read `index.md` to find which page **owns** the topic you care about. Every
   canonical topic appears exactly once; the page listed is the single source of
   truth for it.
3. Open that page. Its frontmatter `depends-on` lists the pages it rests on;
   `referenced-by` lists what rests on it. Follow `depends-on` outward until you
   have the neighbourhood you need.
4. **`depends-on` is not a build order.** The graph is cyclic by design —
   `arch-04-state` and `arch-05-generic` each explain the other, and the corpus
   is one large strongly-connected component. Follow edges to find what to read
   *alongside* a page; do not compute a closure and read it as layering.
5. Do not read the whole corpus. The apparatus exists so a task-scoped subset is
   cheap to identify.

## 4. Authority order — who wins when two files disagree

Defined normatively in `10.1-conventions` (`id: conventions`), which is the only
place to change it. Summary:

frontmatter `canonical-for` owner > `physics/library/formulas/registry-manifest.csv`
> `physics/library/cert/reference-data/*.csv` > canon pages (as peers, settled by
topic ownership) > `pages/11-appendix-derivations/` > `journal/live/` > `README.md`.

Three rules that bite in practice:

- **Reference-data CSVs are canonical for seeded coefficient values.** Seed from
  them and from `9.1-accuracy-ledger`, **never** from an appendix derivation —
  appendix pages carry superseded values behind changelogs.
- **Appendix pages are `authority: supporting`.** They record how a result was
  derived, not what is currently true. Their tag legends and row numbers are
  snapshot-local; `11.8` in particular uses a **retired** differentiability
  legend in which `D3` and `D0` mean something else entirely.
- **`live/audits/` is frozen; `live/specs/` is not.** An audit is a dated record
  and rewriting it destroys the record. A spec is still executing and a stale
  claim in one misdirects the next agent, so specs track current truth.

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
5. If you cite another page's `[id]` in prose, add it to `depends-on` and add
   yourself to that page's `referenced-by`. The checker derives this and will
   tell you if you forget.
6. Run `python journal/tools/apparatus.py`. It restamps hashes and regenerates
   the apparatus. Then confirm both checkers are clean:
   `python journal/tools/apparatus.py --check` and
   `python journal/tools/seams.py`.

## 6. Renaming a registry formula

Registry names are content addresses. Renaming one is a rekey, not an edit, so
**fix names before they land, never after**. Until then:

1. Change the `Name` cell in `registry-manifest.csv`.
2. Add a row to `physics/library/formulas/retired-names.csv` mapping the old name
   to the new one.
3. Sweep the prose. `seams.py` fails on any retired name a page mentions without
   resolving it in the same paragraph — an appendix may keep the historical name
   as long as the paragraph says what it landed as.

## 7. Working copies

If you extract a subset of pages to work on, carry each block's **source `id`**
with it, and record the `content-hash` you extracted at. On write-back:

- the `id` tells you which page the block belongs to;
- a changed `content-hash` means the page moved underneath you — re-read before
  applying, or you will silently clobber someone else's edit.

A working copy without per-block `id` provenance cannot be written back
mechanically. Do not produce one.

## 8. What the checkers enforce

`python journal/tools/apparatus.py --check` fails on:

1. missing or unparseable frontmatter, or a missing required field
2. duplicate `id`, or a page filed in a folder its `chapter` does not match
3. **duplicate `canonical-for` topic** — the anti-drift invariant
4. asymmetric `depends-on` / `referenced-by`
5. an `[id]` reference in prose that resolves to no page
6. a body citing an `[id]` without the corresponding `depends-on` edge
7. a section coordinate that resolves to no heading in the target
8. a line-number citation (`file.md:42`) — line refs rot on every edit
9. a registry count claim that disagrees with the CSV, including a per-tag
   diff tally and a per-tier cost distribution quoted in prose
10. a duplicated or skipped trap number, or a `[traps] §N` citing one that
    does not exist
11. an out-of-vocabulary `status` or `authority`
12. a stale `content-hash`

`python journal/tools/seams.py` fails on fourteen classes: row-band claims whose
endpoints are not in the CSV; backticked formula names that are not registry rows;
`formula =` arguments carrying inline mathematics, or an undeclared name; divergent
tolerance literals; duplicate glossary entries; retired formula names left
unresolved; case-variant near-misses; `D4` rows whose `source` cell names no
relaxation; registry `name (row N)` pointers naming the wrong row;
`unregistered-formulas` declarations the body no longer invokes; glossary rows
whose canonical pointer names no page; and reference-data rows with no uncertainty
or no source. Its sweep covers the book, the
README, this file, the reference-data CSVs, and `informed-operator/design/`.

**Green means the corpus is internally consistent. It does not mean the physics
is right** — that is what the audit protocol in `10.3-audit-prompt` is for. And
green does not mean a check ran: both checkers have shipped holes that made them
silently skip whole classes of citation. Before citing a clean run as evidence,
plant a defect of exactly the class you claim is absent and confirm the checker
fails (`10.4-traps` §58). That is now a script:
`python journal/tools/calibrate.py` plants a defect in a temporary copy and
asserts it fires — 45 probes. It reports three failure modes, and all three are
holes: a **missed** probe is a hole in the checker; a **stale** probe — one whose
planted text no longer exists — is a hole in the probe list; an **uncovered**
check is one no probe reaches at all, which the script derives from `seams.py`'s
source rather than from a list it could drift from. That last mode exists because
for most of this file's life the sentence above read "one defect per check" and
was false of four seams classes and nine apparatus ones, while a clean run was
being cited as though it established them. **Run it whenever you change a
checker**, and cite its result rather than a bare green.

## 9. Standing traps

Before changing anything involving signs, units, or reference frames, read
`10.4-traps`. Sign-convention errors in this corpus have historically been
invisible to review and inverted real physics — a bowing coefficient lifted
between two equivalent conventions flips the interface charge; a pyroelectric
coefficient lifted from the literature without reframing inverts the temperature
drift. The register exists because these recur.

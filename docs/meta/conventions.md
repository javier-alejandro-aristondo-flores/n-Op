# Doc-tree conventions

Rules for the atomic-file tree under `docs/architecture/`,
`docs/implementation/`, `docs/mvp/`. The tree is the source of truth;
the monoliths are regenerated.

The **authority order** and the corpus-wide rules immediately below
govern the whole base, not only the atomic tree.

## Authority order

When two files disagree, the higher-ranked source wins:

frontmatter `canonical-for` topic owner >
`physics/library/formulas/registry-manifest.csv` (formula rows/tags) >
`docs/architecture/` > `docs/implementation/` > `docs/mvp/` >
companion indexes (computational-overview, formula-registry,
properties, accuracy-ledger) > README + AUDIT_PROMPT >
`physics/research/` strata > `docs/presentation/`.

- **Reference-data CSVs are canonical for seeded coefficient values.**
- **Seed from the ledger and the reference CSVs, never from the
  research tables.** `physics/research/` is the lowest-authority
  stratum and carries superseded values behind per-file changelogs;
  reseeding from it silently reverts a landed fix.
- **Generated outputs are never edited or audited.** `assemble.py
  --check` gates their freshness.
- **Frozen dirs** (`docs/audits/`, `docs/specs/`,
  `docs/presentation/`) are dated artifacts: internal staleness is
  by-design and exempt. Only a *live* file citing them incorrectly is
  a defect.

## Naming is addressing

Registry formula names are hash-consed into content addresses. A
post-landing rename is a substrate-wide rekey, not an edit — every
cached kernel, certificate, and address keyed on the old name breaks.
**Fix names before they land, never after.**

## File layout

- One concept per file. Filename: `NN-slug.md` where `NN` is a
  zero-padded ordinal that fixes assembly order within its directory.
- Three doc trees: `architecture/` (the spec), `implementation/` (the
  build plan), `mvp/` (the diamond slice). Each assembles to one
  monolith via `assemble.py`.
- `meta/` holds the manifest, conventions, glossary, and the
  assembly + lint scripts. Not assembled into any monolith.

## Frontmatter (mandatory)

Every atomic file starts with a YAML frontmatter block:

```yaml
---
id: <tree>-NN-slug
title: <human-readable title>
status: draft | review | stable
revision: <integer, monotone>
canonical-for:
  - <topic the file is the single source of truth for>
depends-on:
  - <id of upstream file>
referenced-by:
  - <id of downstream file>
research-sources:
  - <path under physics/research/>
---
```

Field rules:

- **`id`** — `<tree>-NN-slug` where `<tree> ∈ {arch, impl, mvp}` and
  `NN-slug` matches the filename. Globally unique. Anchors in prose
  use the bare id, written `[arch-06-physics-graph]`.
- **`canonical-for`** — every concept appearing in this list must
  appear in *exactly one* file's `canonical-for`. The lint enforces
  this; that's how we prevent drift.
- **`depends-on` / `referenced-by`** — symmetric. If `A.depends-on
  contains B`, then `B.referenced-by must contain A`. Empty lists are
  written `[]`. Lint enforces.
- **`status`** — `draft` until reviewed; `review` while a rewrite is
  in flight; `stable` once accepted.
- **`revision`** — incremented on every substantive content change.
  Metadata-only edits (populating `depends-on` / `referenced-by` /
  `research-sources`) do **not** bump `revision` — revisions track
  content drift, not graph housekeeping.
- **`depends-on` edge criterion** — `A depends-on B` iff A's body
  references B's id, **or** A uses a term whose `canonical-for` owner
  is B. Nothing else creates an edge; the graph is derivable and
  auditable, not vibes.
- **`research-sources`** — paths under `physics/research/` only;
  other docs go under `depends-on`.

## Anchor and cross-reference style

- Cross-references use the `id`, written either inline as
  `[arch-06-physics-graph]` or with section coordinate as
  `arch-07-pipeline §7.4`. Section coordinates must resolve against a
  real heading in the target file (lint check 11).
- Section numbers inside a file match the original monolith section
  for continuity (e.g. `arch-11-residuals` uses §11.x). New keystone
  files use whatever numbering reads cleanly.
- Never link by file path. Links go through `id`s so file moves don't
  rot references.
- **Id-less targets** (research strata, audits, specs — files outside
  the atomic tree) are cited by **path + stable heading anchor**:
  `defects-surfaces-interfaces.md Part G.2`,
  `docs/audits/2026-07-07-gap-audit.md §B7`. **Never by line number**
  — line references rot on every edit and are forbidden in the
  editable surface (lint check 10; frozen audit records are exempt as
  historical text).
- **Count phrasing is canonical** so the count-lint has a contract:
  whole-vocabulary counts are always written `N substantive formulas`,
  `N residual categories`, `N methods`, `N templates`, `N observable
  bundles`, `N cert obligations`. Subset phrasings ("~35 formulas",
  "5–7 bundles") stay un-linted by construction.

## Style

- American English everywhere.
- One topic per file; if a file grows past ~250 lines, split it and
  give each part its own `canonical-for`.
- Use ATX headings (`#`, `##`, `###`). Do not use setext (`===` /
  `---` underlines).
- Code fences are bare (no language tag) for the project's
  pseudo-syntax records; tag real code (`python`, `yaml`, `bash`).
- No decorated separator comments anywhere in prose
  (`# ──────`, `# ===`).

## Lint discipline

`docs/meta/lint.py` enforces:

1. Frontmatter present and parseable.
2. Required fields present.
3. `id` matches filename and tree.
4. `canonical-for` topics globally unique.
5. `depends-on` / `referenced-by` symmetric.
6. Every `[arch-NN-…]` / `[impl-NN-…]` / `[mvp-NN-…]` reference in
   prose resolves to an existing file.
7. `research-sources` paths exist on disk.
8. Vocabulary counts quoted in README / AUDIT_PROMPT / docs match the
   arch-09 canon + registry CSV (opt-out marker `lint:ignore-counts`).
9. No retired path (the pre-reorg superpowers / archive directories)
   appears in tracked text.
10. No line-number citations (`file.md:N`, `id:N`) in the editable
    surface (frozen audits exempt).
11. Every section-coordinate citation (`arch-NN §X.Y`; research
    `Part X` / `§X.Y` path-anchors) resolves against a real heading
    in its target.

## Assembly

`docs/meta/assemble.py` reads `manifest.yaml` and concatenates the
atomic files in the listed order, stripping frontmatter and emitting
a regenerated monolith with a TOC at the top. Three monoliths are
regenerated by default; named bundles produce LLM-context subsets.

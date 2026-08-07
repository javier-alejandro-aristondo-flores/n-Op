---
id: agent-contract
title: "Agent contract"
owns:
  - frontmatter schema
  - citation syntax
  - fact placement rule
  - vocabulary rule
anchors:
  shape: "The shape of the base"
  frontmatter: "Frontmatter"
  citing: "Citing"
  placement: "Where a fact goes"
  vocabulary: "The vocabulary rule"
  forbidden: "Forbidden"
  schema: "The machine-readable schema"
depends-on: []
open-questions: []
---
# Agent contract

Read this before editing anything in `journals/`. It is short on purpose.

The rules below are not advice. **The block at the end of this page is the schema
the checker parses** — this document and the enforcement are the same artifact, so
they cannot disagree. Changing a rule means changing that block.

## The shape of the base

**n-Op is the project — the neural operator, assembled.** Beneath it are
**libraries**, each serving to build it. There is no other word for these: not
*module*, not *component*, not *subsystem*.

```
n-Op
├── physics/            the oracle library
├── informed-operator/  the operator library
└── interface/          the loops library
```

The specification is a set of **journals**. A journal is one cohesive corpus on one
topic, made of **sections**, made of **pages**. A page is one file. Headings inside a
page are addressed by **anchor**.

```
journals/<journal>/<section>/<page>.md
```

**The filename is the id.** `journals/oracle/state/unified-state.md` has
`id: unified-state`. One name per page — no display tag, no serial, no content hash.
The journal and section are read off the path and never restated in frontmatter,
because a field that restates the path can disagree with it.

## Frontmatter

Strict YAML. Exactly these keys, no others.

```yaml
---
id: unified-state              # must equal the filename stem
title: "The unified state"     # always quoted — backticks and colons are legal here
owns:                          # ≥1 topic; none may equal the id
  - state seven-tuple
  - slot gauge conventions
anchors:                       # slug: exact heading text
  slots: "The seven slots"
  gauge: "Gauge conventions"
depends-on: [generic-dynamics, representation-substrate]
open-questions: []
---
```

`owns` is the anti-duplication mechanism and the reason this base can be updated in
one place. A topic appears in exactly one page's `owns` across the whole corpus. If
you find yourself stating a fact that another page owns, **cite it instead**.

A page that owns nothing but its own name owns nothing at all — hence the rule that no
entry may equal the id. Thirty-one percent of the previous corpus failed this, which
is why the invariant could not fire there.

`referenced-by` is **not** a frontmatter key. The reverse edges are emitted into
`generated/corpus.json`. Nothing in a page is ever restamped by a tool.

## Citing

One syntax:

```
[unified-state]              the whole page
[unified-state#slots]        a specific anchor
```

Every cited id must appear in your `depends-on`. Every cited anchor must be declared
in the target's `anchors`. Both are checked.

**There are no section ordinals.** `§4.1` is not a citation here. Ordinals rot when a
heading is inserted above them, and in the previous corpus they silently failed to
resolve into 33 of 58 pages — a citation to a section that did not exist passed.
Anchors are declared, so they cannot.

**Never cite by file path or line number.** Paths move; line numbers rot on every edit.

**Data files are cited by id too.** The registry, the reference data and the datasets
are named in `data-artifacts` below and cited exactly like pages — `[registry]`,
`[reference-data]`. They carry no anchors and need no `depends-on` edge, because there
is no page on the other end.

This exists for one reason: **no wording of a path is true across a move.** A page that
names where a file lives today is wrong the moment the file moves, and right now is
wrong afterwards — the present tense cannot disambiguate a claim about a location that
is about to change. An id can. Moving a file is one edit to the map below, not one edit
per page that mentions it. This is the same discipline that let the pages themselves be
moved wholesale without breaking a single reference; data files were the one class
still outside it.

## Where a fact goes

1. Name the topic.
2. Find its owner in `generated/corpus.json` — the `topics` map answers this in one
   hop.
3. That page is where the edit goes.
4. If no page owns it, decide which page *should*, and add the topic to that page's
   `owns`.

**Never state a fact in two pages.**

## The vocabulary rule

> **When the corpus owns a word for something, no synonym is admissible; and no token
> may name two things.**

This is checked, not advised. The `owned-terms` block below is the list.

Two collision classes, and they fail differently:

- **Concept against concept.** One token, two meanings in this corpus. The owned-term
  sweep catches these.
- **Concept against physics.** A corpus-invented tag reusing a token that already
  denotes a physical quantity. This one cannot be fixed by renaming the physics, so
  the rule is narrower: **no corpus-invented name may be a serial or a symbol.**

**Everything the corpus invents is spelled out in English.** Standard deviation is the
name; `σ` is not. `direct` and `adjoint` are names; `D1` and `D2` are not. Symbols
belong in equations, where the surrounding mathematics binds them.

This is not a style preference. Corpus tags and physics symbols were drawn from one
alphabet, and two checkers were written for that and then deleted because no rule
could separate them. Spelling the corpus half out separates them by construction.

**Eponyms are different and mostly stay.** The test is whether a reader could bind the
name to the wrong object — not whether a person's name appears in it.
`born-oppenheimer-surface` names one thing unambiguously and stays. A name that
shadows a second quantity gets renamed, and the person moves into the source cell as
an `a.k.a.`, which is where a literature search starts anyway.

## Forbidden

**History.** No changelogs, no strikethrough, no *"formerly"*, *"superseded"*,
*"no longer"*, *"used to"*, *"retired"*, *"closed on <date>"*. Pages state what is
true, in the present tense, and nothing about how they got that way.

History is not destroyed — it is centralized. `log/timeline.md` is the only place
research advancement is recorded, and it is a compliance artifact. Each entry carries
**date · finding · evidence link · attribution · what it superseded**.

A *closed* question's **resolution** is a present-tense fact and belongs on the page
that owns the topic. The story of it having been open belongs in the log or nowhere.

**Unescaped pipes in tables.** Physics notation contains literal `|` — bra-kets,
norms, determinants. An unescaped one splits the row and shifts every cell right of
it, and every by-name check still passes because the cells it reads are non-empty and
merely hold the wrong values. That defect shipped for a month in this project's
reference data. Write `\|`. Table arity is checked.

**Restating a fact another page owns.** Cite it.

## The machine-readable schema

The checker parses this block. It is the contract.

```yaml
frontmatter:
  required: [id, title, owns, anchors, depends-on, open-questions]
  forbidden: [tag, content-hash, authority, chapter, status, referenced-by, journal, section, library]
  rules:
    - id-equals-filename-stem
    - title-must-be-quoted
    - owns-non-empty
    - owns-excludes-own-id
    - owns-unique-across-corpus
    - anchors-resolve-to-headings
    - depends-on-resolves-to-pages

citations:
  syntax: "[page-id]  or  [page-id#anchor]"
  rules:
    - cited-id-must-resolve
    - cited-id-must-be-in-depends-on
    - cited-anchor-must-be-declared-on-target
  forbidden:
    - section-ordinal        # §4.1
    - line-number            # file.md:42
    - bare-path              # journals/oracle/state/unified-state.md

# Data artifacts are cited by id, exactly like pages, and for the same reason: the
# corpus survived being moved wholesale because nothing referenced a path. These
# files are the one class that still did — and the cutover is the move that would
# have broken them. Changing where a file lives is one edit here, not N across the
# corpus.
data-artifacts:
  registry: data/registry-manifest.csv
  reference-data: data/reference-data/
  strain-sweep: data/diamond-strain-sweep/
  research-log: log/timeline.md
  corpus-index: generated/corpus.json

libraries:
  oracle: physics
  operator: informed-operator
  interface: interface
  n-op: ~                    # cross-cutting: the project itself
  practice: ~                # cross-cutting: how to work here

forbidden-markers:
  history: [superseded, formerly, "no longer", "used to", retired, deprecated,
            legacy, "prior version", "earlier version", "struck through", "pre-book"]
  markup: ["~~", "## Changelog"]

owned-terms:
  library: "one of physics / informed-operator / interface. Never module, component, subsystem."
  journal: "a cohesive corpus on one topic"
  section: "a group of pages within a journal"
  page: "one file"
  anchor: "a declared heading slug — the target of a citation"
  owns: "the topics a page is the single source of truth for"

retired-vocabularies:
  differentiability: {D0: read, D1: direct, D2: adjoint, D3: fixpoint-adjoint,
                      D4: relaxed, DN: none}
  cost-tier: {T0: microseconds, T1: milliseconds, T2: seconds, T3: minutes}
  cadence-tier: {T0: per-step, T1: per-batch, T2: per-epoch, T3: on-demand}
  bundle: {B1: electronic-structure, B2: phonon, B3: transport, B4: defect-resolved,
           B5: surface-resolved, B6: interface-resolved, B7: mechanics,
           B8: thermodynamics, B9: non-equilibrium-operating, B10: static-validity,
           B11: degradation, L1: linear-response-primitive}
  cluster: {C1: vocabularies, C2: registered-generators, C3: sidecars, C4: evidence,
            C5: content-addressing, C6: selected-subsets, C7: sparse-masks}
  born-oppenheimer-level: {L1: quantum-electronic-substrate, L2: born-oppenheimer-surface,
                           L3: equilibrium-statistics, L4: non-equilibrium-kinetics}
  research-stream: {S1: observable-catalog, S2: crystal-structure-prediction,
                    S3: defects-and-interfaces, S4: non-equilibrium-high-field,
                    S5: residual-loss-methodology}
  dressing-layer: {"Layer 1": substrate, "Layer 1.25": one-shot-dressing,
                   "Layer 1.75": iterative-dressing, "Layer 2": property-machinery}
  missing-data-marker: {GAP: UNSEEDED}
```

**Cost tiers and cadence tiers are two vocabularies, not one.** Cost is a property of
a formula and lives in the oracle. Cadence is a training-loop policy and lives in the
operator — the oracle owns no loop. They shared a token and already mis-bound: an
iterative residual is `minutes` by cost and `per-epoch` by cadence, which under the old
names read `T3` and `T2`.

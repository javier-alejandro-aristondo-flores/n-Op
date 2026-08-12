# n-Op

n-Op trains a **physically-informed neural operator** over the multiphysics state of
crystalline materials, in service of designing **durable ultra-wide-bandgap
semiconductor chips for harsh environments** — jet-turbine class: above 500 °C, thermal
cycling, mechanical vibration, high field, high current density, possibly radiation.

The minimum viable demonstration is **diamond**, with three capabilities: crystal
structure prediction, electron-cloud diffusion, and heat diffusion. The specification is
comprehensive; the build is diamond-first.

The specification came first and still dominates. The oracle library has begun —
`programs/oracle/` scores real VASP output against invariants, equations of state and
elastic constants, under 42 tests — and four go/no-go studies in
`apparatus/feasibility/` have measured whether the operator has a signal worth learning.
The operator library answers one of them: it learns strain → HSE06(0.27) electronic
structure for diamond, and beats the baseline it contains. The loops library is empty.

## Start here

**[`journals/practice/agent-contract.md`](journals/practice/agent-contract.md)** — the
front door, for a person or an agent. It is short, and it is the specification the
checker parses, so it cannot drift from what is enforced.

Then, to find anything: **`apparatus/generated/corpus.json`**. Its `topics` map answers
*"which page owns this?"* in one hop, for every one of 302 topics. It is emitted, never
hand-written.

## The shape

**The specification and the implementation are twin trees.** A journal and the library it
specifies carry the same name, so the same subpath under the other root reaches the work
that realizes it — `journals/oracle/accuracy/` against `programs/oracle/accuracy/`, and
`tests/oracle/accuracy/` beside them.

| | |
|---|---|
| **`programs/oracle/`** | the oracle library — encodes the laws, scores a candidate state against them, and never solves, completes, or judges |
| **`programs/operator/`** | the operator library — the neural operator, which consumes the oracle's residuals during one training stage |
| **`programs/loops/`** | the loops library — training, design search, active learning |

```
journals/          the specification — 50 pages
  oracle/          state · laws · compilation · certification · registry · accuracy · seams
  operator/        seam · structure · training · loss
  loops/           the loops boundary
  n-op/            purpose · build
  practice/        agent-contract · conventions · traps · glossary
programs/          the implementation, mirroring journals/ section for section
  oracle/          state · laws · certification · registry · accuracy · seams
  operator/        seam · training · structure (empty) · models · the lifecycle modules
  loops/           empty; the specification for it is the corpus
tests/             mirrors programs/, section for section
apparatus/         everything that checks or feeds the two trees
  apparatus/log/timeline.md  the research record — the only place history is kept
  audit/           the corpus audit — can the oracle be built from this specification?
  feasibility/     four go/no-go studies — is there a signal worth building it for?
  generated/       corpus.json, emitted; regenerating it is a no-op
  data/            the registry, the reference battery, the diamond sweeps
  tools/           the checkers, and the calibrations that prove they are looking
```

**The mirror is section-level and not enforced.** A section directory with no code is an
empty directory, not a finding — `programs/operator/structure/` is empty against five
pages. Sections appear on the implementation side only where the correspondence is real,
so a library organized on a different axis than its journal keeps that axis and its files
sit flat. `programs/operator/` decomposes by data-and-experiment lifecycle rather than by
the anatomy its journal describes, and filing one into the other would assert a
correspondence the corpus does not state.

## How it holds together

**One name per page.** The filename is the id. No display tag, no serial, no content
hash. Journal and section are read off the path, never restated.

**Cite the id, never the path.** `[unified-state#slots]`. Data files carry ids too, so
moving one is a single edit to a map rather than an edit per page that mentions it.

**A topic has exactly one owner.** That is the anti-duplication mechanism and the reason
a fact can be updated in one place. It is machine-checked, and no page owns only its own
name.

**Everything invented here is spelled out in English.** Standard deviation, not `σ`;
`adjoint`, not `D2`. Corpus tags and physics symbols were drawn from one alphabet, and
two checkers were written for that collision and then deleted because no rule could
separate them. Spelling the corpus half out separates them by construction.

**Pages carry no history.** They state what is true, in the present tense. Research
advancement is recorded in `apparatus/log/timeline.md`, which is a compliance record and carries
date, finding, evidence, attribution, and what each entry superseded.

**What is not yet known is declared where it is missing.** 62 open questions live in the
frontmatter of the page that owns the affected topic; the corpus-wide register is emitted
from them, so it cannot disagree with the pages it summarizes.

## Checking

```
python apparatus/tools/check_structure.py          regenerate the index, then check
python apparatus/tools/check_structure.py --check  check only; fails if the index is stale
python apparatus/tools/check_the_checker.py        prove the checker is looking
python apparatus/tools/check_no_licensed_content.py   prove no pseudopotential leaked
python -m pytest                                   42 tests over the oracle library
```

**Green is not evidence a check ran.** This project has shipped two copies of the corpus
both reporting green, a citation syntax that went unverified across 47% of references,
and section coordinates that silently failed to resolve into 33 of 58 pages. The
calibration plants a defect of each class and asserts the checker fails, reports any
error site no probe reaches, and includes negative probes — because a check that only
proves it fires cannot tell you it fires too often.

## History

Three tags hold what the working tree no longer does. No single commit holds all of it,
so each names what it actually contains:

| tag | holds |
|---|---|
| **`pre-restructure-main`** | the corpus as it stood before the 2026-07-31 restructure |
| **`pre-cutover-apparatus`** | the audit apparatus — dispositions, provenance register, contradiction register, leads |
| **`pre-cutover`** | the 2026-07-22 talk deck, which had never been committed before that point |

Anything the log marks as no longer present is readable from the tag that holds it:

```
git show pre-restructure-main:<path>
```

Those paths predate the twin-tree layout, so they are the old ones — `physics/…`,
`informed-operator/…`, `tools/…`, and the six directories now under `apparatus/`. A tag
holds the tree as it stood; it does not follow a later rename. `git log --follow <new
path>` crosses the move for a file that was tracked before it.

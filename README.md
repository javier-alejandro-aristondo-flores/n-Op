# n-Op

n-Op trains a **physically-informed neural operator** over the multiphysics state of
crystalline materials, in service of designing **durable ultra-wide-bandgap
semiconductor chips for harsh environments** — jet-turbine class: above 500 °C, thermal
cycling, mechanical vibration, high field, high current density, possibly radiation.

The minimum viable demonstration is **diamond**, with three capabilities: crystal
structure prediction, electron-cloud diffusion, and heat diffusion. The specification is
comprehensive; the build is diamond-first.

**No code has been written yet.** This repository is specification and research.

## Start here

**[`journals/practice/agent-contract.md`](journals/practice/agent-contract.md)** — the
front door, for a person or an agent. It is short, and it is the specification the
checker parses, so it cannot drift from what is enforced.

Then, to find anything: **`generated/corpus.json`**. Its `topics` map answers *"which
page owns this?"* in one hop, for every one of 273 topics. It is emitted, never
hand-written.

## The shape

n-Op is the project. Beneath it sit three **libraries**, each serving to build it.

| | |
|---|---|
| **`physics/`** | the oracle library — encodes the laws, scores a candidate state against them, and never solves, completes, or judges |
| **`informed-operator/`** | the operator library — the neural operator, which consumes the oracle's residuals during one training stage |
| **`interface/`** | the loops library — training, design search, active learning |

All three are empty. The specification for them is the corpus.

```
journals/          the specification — 45 pages
  oracle/          state · laws · compilation · certification · registry · accuracy · seams
  operator/        seam · training · loss
  interface/       the loops boundary
  n-op/            purpose · build
  practice/        agent-contract · conventions · traps · glossary
log/timeline.md    the research record — the only place history is kept
generated/         corpus.json, emitted; regenerating it is a no-op
data/              the registry, the reference battery, the diamond sweeps
tools/             the checker, and the calibration that proves it is looking
```

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
advancement is recorded in `log/timeline.md`, which is a compliance record and carries
date, finding, evidence, attribution, and what each entry superseded.

**What is not yet known is declared where it is missing.** 51 open questions live in the
frontmatter of the page that owns the affected topic; the corpus-wide register is emitted
from them, so it cannot disagree with the pages it summarises.

## Checking

```
python tools/check_structure.py          regenerate the index, then check
python tools/check_structure.py --check  check only; fails if the index is stale
python tools/check_the_checker.py        prove the checker is looking
```

**Green is not evidence a check ran.** This project has shipped two copies of the corpus
both reporting green, a citation syntax that went unverified across 47% of references,
and section coordinates that silently failed to resolve into 33 of 58 pages. The
calibration plants a defect of each class and asserts the checker fails, reports any
error site no probe reaches, and includes negative probes — because a check that only
proves it fires cannot tell you it fires too often.

## History

The corpus before the 2026-07-31 restructure is tagged **`pre-restructure-main`**, and
the state including the audit apparatus and the talk deck is tagged **`pre-cutover`**.
Anything the log marks as no longer present is readable from there:

```
git show pre-restructure-main:<path>
```

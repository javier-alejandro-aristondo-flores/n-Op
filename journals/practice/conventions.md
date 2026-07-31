---
id: conventions
title: "Writing conventions"
owns:
  - page style
  - count phrasing
  - verdict discipline
  - data and generated files
anchors:
  scope: "What is left here"
  style: "Style"
  counts: "Count phrasing"
  verdicts: "What a result has to show"
  artifacts: "Data files and generated files"
depends-on:
  - agent-contract
  - traps
  - accuracy-ledger
open-questions:
  - id: appendix-comparison-replacement
    anchor: verdicts
    summary: "An auditor was previously told to diff the research stratum against the specification. There is one stratum now, so a certification pass has nothing to compare the corpus against except git history and the log. What the second source for a certification pass is has not been decided."
---
# Writing conventions

## What is left here

[agent-contract] owns the structure: the frontmatter schema, the citation syntax, where
a fact goes, and the vocabulary rule. Read it first; it is the specification.

This page is deliberately small. Four things are left over, and none of them is
structural:

1. how a page reads,
2. how a count is phrased,
3. what a check result has to show before it can be cited as evidence,
4. how prose relates to the files it quotes.

There is no authority order. One tier, one rule: the page whose frontmatter claims a
topic is the only place that topic is stated, and if two pages disagree, one of them is
restating a fact it does not own ([agent-contract#placement]). Nothing here ranks pages
against each other, because nothing needs to.

## Style

- **American English** everywhere.
- **One subject per page.** A page may own several topics when they are facets of one
  machine — a substrate, a generator, a tiered state. That is cohesion, not drift. What
  is forbidden is one topic owned in two places, and that is machine-checked.
- **Length** targets about 250 lines. A keystone page may exceed it where splitting
  would fragment one mechanism; a page that exceeds it for any other reason is two
  pages.
- **ATX headings** (`#`, `##`, `###`). Never setext underlines.
- **Code fences** are bare for this project's pseudo-syntax and tagged for real code
  (`python`, `yaml`, `bash`). The distinction matters because a fenced block is invisible
  to the citation sweep: pseudo-syntax that needs to create a dependency edge belongs in
  prose, not in a fence.
- **No decorated separator comments** in prose.

## Count phrasing

A count over a whole vocabulary is written in one of six fixed forms:

```
N substantive formulas      N templates
N residual categories       N observable bundles
N methods                   N cert obligations
```

A number in one of those forms is read as a claim about the entire vocabulary. A subset
or a delta must therefore be phrased so it cannot be mistaken for one: spell the number
out ("three new methods"), or write "10 of the 20". Approximations and ranges — "about
35 formulas", "5 to 7 bundles" — are safe by construction. A bare `+N` in front of one of
the six forms is not.

**A tally is checked against its source, or it is not checked.** An internal consistency
test on a distribution — confirming that the parts sum to the total — is not a test of
the distribution: every part can be wrong and the sum still right
([traps#sum-preserving-errors]). The count phrasings exist so that a checker can find
the claim; finding it is not the same as verifying it, and only the source file does
that.

## What a result has to show

These apply to any check — a tool run, a review pass, a certification, an agent
reporting on its own work.

**Green means the structure is sound. It does not mean the physics is right.** The
structure checker verifies frontmatter, citations, table arity and vocabulary. It has no
opinion about whether a coefficient is correct. [traps] records what has gone wrong
before.

**Green does not mean a check ran.** Before citing a clean run as evidence, plant a
defect of exactly the class you are claiming is absent and confirm the run fails
([traps#checker-not-looking]). A checker that finds nothing and a checker that is not
looking produce identical output.

**No free emptiness.** A clean verdict is earned and shown. A result reporting no
findings carries an evidence transcript — the specific comparisons actually made, per
class swept — and a log of near-findings considered and dismissed, with the reason each
was dismissed. A bare "no defects found" is not a result; it is an absence of one.

**Calibrate before certifying.** A discovery pass looks for what is wrong. A
*certification* pass asserts that nothing is, and that assertion is only worth what the
auditor is worth — so validate the auditor first: plant a known set of defects in a
throwaway copy and confirm every one is found. An uncalibrated clean verdict measures
the auditor, not the corpus. Report the calibration result as found, including a partial
one: a pass that finds four of six planted defects is a four-of-six gate, and rounding it
up is the same failure the calibration exists to prevent.

**An invariant held by construction beats one held by a checker.** Where a rule can be
made unrepresentable, make it unrepresentable, and delete the check along with the
possibility it policed. That is not lost coverage — it is coverage that cannot go stale.
A check is what remains for the rules that cannot be built out.

## Data files and generated files

Three kinds of file sit outside the journals, and each relates to prose differently.

**Data files are sources.** The registry manifest and the reference data under
`physics/library/` hold the corpus's coefficients, formula rows, signatures and tags. A
page that states one of those values is *quoting* it: the file is where the value
changes, and where a disagreement between a page and the data is settled. Seed from the
file, or from [accuracy-ledger#seed-provenance], never from a page that quotes one
([traps#seed-from-the-source]). A value carried forward because it has always been there
is not a seeded value — a row whose provenance does not resolve is `UNSEEDED`, which is
a thing the corpus knows how to say.

**Generated files are outputs.** `generated/corpus.json` is emitted from page
frontmatter by `tools/check_structure.py`. It is never hand-edited and never audited: a
finding "in" a generated file is a finding in the pages it was generated from, and
editing the output only hides it until the next run.

**Neither kind has a page id**, so both are named by path rather than cited. Paths in
prose belong in backticks, which also keeps them out of the citation sweep.

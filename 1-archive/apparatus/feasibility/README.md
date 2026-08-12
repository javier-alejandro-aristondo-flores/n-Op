# Feasibility — is there a learnable signal worth building the operator for?

Four go/no-go studies against the diamond corpora. Each asks whether a proposed learning
target carries structure that a neural operator could capture and a cheap baseline could
not. Each was pre-registered with a kill condition before it ran, and each was run to
answer rather than to confirm.

This is the empirical sibling of `audit/`. That campaign read the specification and asked
*can the oracle be built from this corpus?* This one reads the data and asks *is there
anything in it worth building the operator for?*

## Why this directory is not called `gates/`

The reports inside call these Gates 1–4, and so does everyone who worked on them. The
directory does not, because the corpus already spends "gate" twice — the
*applicability-decidability gate* in the formula registry, and the build-sequence gates
that `audit/findings/seams.md` calls "build gate 3". Both mean *an acceptance check a
candidate passes*. These four mean *a decision about what to build*. In a corpus whose
central discipline is one name per concept, a third sense at the top level is the
collision the checkers exist to prevent. The word is kept where it cannot be mistaken:
inside this directory.

## The four questions and their answers

| | question | verdict | the number that decided it |
|---|---|---|---|
| **1** | Is the PBE→HSE06 **charge-density** difference predictable from cheap descriptors? | **KILL** | the target died outright |
| **2** | Is the PBE→HSE06 **eigenvalue** correction a rigid scissor shift? | **PROCEED**, not for the proposed reason | 0.759 eV in-gap residual after two constants — the shift is a *stretch*, ≈0.10·E occupied, ≈0.07·E + 0.84 unoccupied |
| **3** | Is the per-configuration **offset** predictable before seeing the answer? | **PROCEED WITH ACKNOWLEDGED RISK** — and the prize shrank | best of eight models closes **20.5%** of the 0.2154 eV oracle gap, under a 30% threshold; a free four-parameter formula cut DOS deformation 32.7% → **14.8%** |
| **4** | Does **strain**→electronic-structure carry response beyond textbook theory? | **PROCEED, REFRAMED** — no decision row fired cleanly | R2 = **148.9 meV**, 7.4× threshold; but deformation-potential theory from the 1950s already captures 82% |

## The through-line

Read in order, the case for an operator has thinned at every step, and that is the most
important thing this directory records.

The density target died. The eigenvalue target survived but turned out to be dominated by
an energy-dependent stretch that four free parameters capture — beating a 162-parameter
per-configuration model. The configuration-specific remainder proved unpredictable from
dopant chemistry, from PBE scalars, and from the PBE spectrum and density-of-states curve,
with no descriptor distinguishable from zero importance once the permutation noise floor
was measured. And the strain target, which reaches genuinely large nonlinearity — the gap
swings from 4.81 eV to 0.441 eV — turns out to be four-fifths explained by
Bardeen–Shockley and Bir–Pikus.

What has strengthened instead, twice, is the case for shipping the **cheap correction** as
the deliverable. Gate 3 recommended it. Gate 4 produced the result that makes it citable:

> Applying diamond's equilibrium-geometry hybrid gap correction to strained diamond
> mis-corrects by **47.5 meV on average and 201 meV at worst**. The correction drifts at
> **−9.1 meV per 1% of strain magnitude**, a 325 meV spread across 1,131 shapes, against a
> **0.002 meV** noise floor.

That corrects standard practice — equilibrium scissor and stretch corrections are routinely
applied to strained structures — and it needs no operator at all.

## Layout

```
gate-1-charge-density/            was pbe_hse_delta        outputs only
gate-2-eigenvalue-correction/     was pbe_hse_eig          outputs only
gate-3-offset-predictability/     was pbe_hse_offset       outputs only
gate-4-strain-sweep/              was strain_gate4         outputs and code
METHOD.md                         what carried across all four
```

Each gate's `VERDICT.md` is the primary record and is the thing to read. Every other file
in its directory is evidence the verdict cites by name.

**Gates 1–3 have no surviving code.** Their analyses were run without the scripts being
written to disk, so those three directories are outputs only and their results cannot be
regenerated — only checked against what they reported. Gate 4 has all eleven of its
programs, documented in its own README, and reproduces its published numbers from this
repository.

## Licensing

Everything here is derived numerical output: eigenvalues, gaps, fitted coefficients,
figures. None of it is VASP-licensed material, which is the pseudopotentials and the
source. The extractor denies `POTCAR` by assertion rather than by omission from a
keep-list, and skipped 2,364 of them.

`tools/check_no_licensed_content.py` enforces that on every file in this tree and carries
its own calibration probe, because a guard nobody has watched fail is indistinguishable
from one that cannot fire.

The raw archives — 10.7 GB, one licensed pseudopotential per run directory — live on
`/Pool` and are never committed. So does Gate 4's 1.6 GB extracted cache, which is
regenerable in about two minutes.

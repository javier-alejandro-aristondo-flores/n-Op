# Gate 3 — is the per-configuration offset predictable? Verdict

**Result: the third outcome — PROCEED WITH ACKNOWLEDGED RISK. And the prize shrank.**

## Verdict

The per-configuration offset is not predictable from any scalar summary available before
seeing the answer. Under leave-one-dopant-set-out cross-validation the best of eight models
(a random forest on atomic descriptors plus PBE scalars) closes **20.5% of the 0.2154 eV
oracle gap**, reaching 0.3295 eV against the 0.3737 eV no-information anchor. That is below
the 30% threshold, and it is not a linear-model artifact: the gradient-boosted and
nearest-neighbor models fail alongside it (13.2% and 14.6%), and both linear tiers score
*worse than predicting a constant* (A-lin −26.7%, AB-lin −70.1%) — the signature of models
that cannot generalize across dopant chemistry. **Tier C, the test built specifically to
give this project its one chance at positive evidence, returned nothing**: capacity-matched
to Tier B and run on identical folds, the PBE DOS curve and in-gap spectrum score −0.6% to
−11.4%, and get monotonically *worse* as more components are retained, which is the shape of
noise rather than of signal being unlocked. The controls confirm the harness rather than the
result: shuffled targets score worse still (0.4557 eV), and grouped CV is uniformly worse
than plain leave-one-out (+0.001 to +0.028 eV), confirming that the 47-group design is
suppressing real leakage that would otherwise have flattered every tier. Permutation
importance finds no mechanism either — the single most useful feature is worth **0.0071 eV,
3.3% of the gap**. The one partial positive is chemical: offsets cluster weakly by
periodic-table group (within/total variance 0.640) but not by period (0.935) or defect order
(0.991), so some structure exists along one chemical axis even though no regressor could
exploit it. **Set against this, Task 2 materially shrinks what an operator would be built to
capture**: adding the missing linear-in-energy row shows that a free four-parameter formula
cuts DOS deformation from 32.7% to **14.8%** at σ = 0.3 eV (9.5% at σ = 0.5), and beats the
162-parameter per-configuration model. By the brief's own standard — *"if 32.7% falls to
something like 12%, the architecture decision changes"* — it changed.

## The asymmetry caveat, stated plainly

This test can kill the project cleanly but cannot confirm it. A low score means only that
**evidence for predictability is absent**, not that an operator would fail — an operator sees
the full field and the full curve, not a handful of scalars. Tier C narrows that gap but does
not close it: it shows the PBE *spectrum and DOS curve* carry no usable signal about the
offset, which is a substantial part of what an operator would see, but not the charge-density
field itself. **Proceeding from here means building on a hypothesis rather than on a
measurement, and that should be said out loud rather than buried.**

## Task 1 — the spin flag: a null result

**Every INCAR in the corpus carries an active `ISPIN = 2` — 199 of 199, none commented out,
none absent.** The premise behind the flag (spin polarization switched off) is false, so by
the stated rule zero runs are excluded and **the headline in-gap residual moves by exactly
0.0000 eV** (0.7590 eV before and after).

The flag was, however, standing in for something real, and it conflated two populations:

| population | pairs | states | M2 (global) | refit within group |
|---|---:|---:|---:|---:|
| clean | 54 | 2007 | 0.674 eV | 0.317 eV |
| odd-nelect-no-mag | 13 | 404 | 0.879 eV | 0.338 eV |
| **mag-quarter** | **14** | **472** | **1.017 eV** | **0.604 eV** |

`odd-nelect-no-mag` is unremarkable once refit. `mag-quarter` is not: it retains 0.604 eV
even when fitted on itself. Those 12 configurations converged to symmetry-constrained
fractional occupations — the odd electron spread over four degenerate states rather than the
cell breaking symmetry. That is a physics limitation (they may not be at their true ground
state), not a setup error. They stay by the stated rule, but they are the runs to re-examine
before any training set is frozen.

## Task 2 — the completed DOS table

Residual difference from the HSE06 curve, as a percentage of its integral (mean over 81
configurations, standard deviation in brackets).

| model | free params | σ = 0.1 eV | σ = 0.3 eV | σ = 0.5 eV |
|---|---:|---:|---:|---:|
| no shift (M0) | 0 | 74.8% (11.2) | 54.1% (6.1) | 43.4% (3.6) |
| rigid scissor (M1) | 1 | 61.6% (9.9) | 40.4% (5.8) | 30.8% (4.7) |
| two constants (M2) | 2 | 56.0% (10.8) | 32.7% (6.2) | 23.0% (5.1) |
| **linear in energy (M2L)** | **4** | **35.8% (13.3)** | **14.8% (10.9)** | **9.5% (8.7)** |
| per-configuration (M3) | 2 × 81 | 53.1% (10.4) | 31.0% (4.8) | 21.7% (2.5) |

The missing row more than halves the deformation, and four global parameters beat 162
per-configuration ones — because two constants per configuration cannot express an
energy-dependent stretch, and the stretch is the dominant effect.

## Task 3 — the ladder

Anchors reproduced exactly from the previous gate: global **0.3737 eV**, oracle **0.1583 eV**,
gap **0.2154 eV**. 60 configurations, 47 dopant-set groups, Tier A 27 features, Tier B 19,
Tier C 169 raw reduced to 19.

| model | residual | gap closed |
|---|---:|---:|
| Model 0 (global mean) | 0.3737 eV | — |
| A-lin (atomic descriptors) | 0.4313 eV | −26.7% |
| B-lin (PBE scalars) | 0.3621 eV | +5.4% |
| AB-lin | 0.5246 eV | −70.1% |
| **AB-rf (best)** | **0.3295 eV** | **+20.5%** |
| AB-gb | 0.3452 eV | +13.2% |
| AB-knn | 0.3423 eV | +14.6% |
| C-lin (k=19) | 0.3984 eV | −11.4% |
| C-rf (k=19) | 0.3750 eV | −0.6% |
| ABC-lin (k=19) | 0.3885 eV | −6.8% |

**Tier C capacity sweep** (grouped CV, identical folds): −3.4% (k=2), −4.2% (k=4), −3.9%
(k=6), −4.2% (k=8), −9.7% (k=12), −9.6% (k=20). Shuffled controls 0.4125–0.4324 eV.

**Leakage check.** Grouped worse than plain LOO for A-lin (+0.0282 eV), B-lin (+0.0009) and
AB-rf (+0.0164) — the grouping is doing real work. Had plain LOO been used, Tier A would have
looked meaningfully better than it is.

**Permutation importance (AB-rf, held-out) — no feature is distinguishable from zero.**
The single-draw ranking put in-gap level position as a fraction of the host gap on top
(+0.0071 eV), followed by highest in-gap level (+0.0063), summed valence mismatch with carbon
(+0.0063), maximum displacement (+0.0060) and magnetic moment (+0.0057), with several Tier A
features *negative*.

That ranking should not be used. Permutation importance is a single stochastic draw, so its
noise floor was measured directly: re-running the top-ranked feature with six independent
permutations gives **+0.0021 ± 0.0025 eV**, and one of the six draws came out *negative*. The
+0.0071 eV headline was a high draw, roughly 2σ above the repeated-draw mean. The noise on
one draw (0.0025 eV) is of the same order as the entire reported spread of importances across
all 46 features (0.0154 eV).

The defensible statement is therefore stronger than a ranking: **no descriptor carries
measurable importance — the best candidate is worth about 1% of the 0.2154 eV gap and is
within noise of zero.** There is no mechanism to find, not merely a weak one.

**Chemical clustering.** By periodic group 0.640 (clusters), by period 0.935, by defect order
0.991 (neither). Weak structure along one chemical axis only.

## Recommendation

Formally this is a proceed, but a weak one, and the honest summary across three gates is that
the case has thinned at every step: the density target died outright; the eigenvalue target
survived but is dominated by an energy stretch that four free parameters capture; and the
configuration-specific remainder is not predictable from dopant identity, from PBE scalars,
or from the PBE spectrum and DOS curve — and no individual descriptor is distinguishable from
zero importance once the permutation noise floor is measured.

Two defensible paths:

1. **Ship the four-parameter linear correction as the deliverable.** It is free, it reaches
   0.347 eV on in-gap states and 14.8% DOS deformation, and it is a genuinely useful, cheap
   tool of exactly the kind gate 1 recommended publishing when a cheap model wins.
2. **Build the operator anyway**, accepting explicitly that the target is the ~0.216 eV
   configuration-specific residual, that nothing tested predicts it, and that the operator's
   advantage must come from the charge-density field — the one input this gate could not
   test. The baseline it must beat is 0.347 eV (formula) and 0.3295 eV (random forest), not
   0.374 eV.

What should **not** happen is building it on the belief that localization, dopant chemistry,
or the PBE curve will supply the signal. Gate 2 ruled out the first; this gate ruled out the
other two.

## Files
- `spin_classification.csv`, `spin_results.json` — Task 1
- `dos_table.md`, `dos_table.json` — Task 2
- `offsets_per_config.csv` — targets plus every Tier A and Tier B descriptor
- `ladder_results.json` — every model, both CV schemes, sweep, controls, importance, clustering
- `plot_ladder.png`, `plot_predicted_vs_actual.png`, `plot_tierC_capacity.png`,
  `plot_chemical_clustering.png`
- `ladder_arrays.npz` — feature matrices and targets

## Method notes
- Cross-validation is leave-one-dopant-set-out (47 groups). Necessary, not decorative: the 60
  configurations span only 47 distinct dopant sets and `BNS` alone appears in 6 with
  identical Tier-A features.
- Standardization and PCA are fitted **inside each training fold**.
- HSE-derived columns are blocked by an assertion on the feature names, not by omission; the
  run completed, so nothing named `hse`/`shift`/`target`/`offset` entered the matrix.
- Offsets are weighted medians (L1-optimal for the reported MAE), matching the previous gate.
- The importance sweep was resumed after an interrupted run, so features scored in the second
  pass drew different permutations than a single uninterrupted run would have. This does not
  bias the result — any permutation destroys a feature's association equally — but it is why
  the noise floor was measured rather than assumed, and the measurement is what the conclusion
  now rests on.
- All outputs under `/Pool/`, asserted at the top of each script. No POTCAR or raw run content
  copied elsewhere.

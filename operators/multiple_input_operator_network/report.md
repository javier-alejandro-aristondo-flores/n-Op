# multiple_input_operator_network — results

## Block

`charge_and_potential_to_localization`, split `paired_fields_fivefold`, restricted to the eighty-cube cubic block (charge density and both potential channels at 80-cubed, electron localization at 40-cubed):

- evaluation (fold 0, the kill block): 76 runs
- validation (fold 1): 65 runs
- member_train (folds 2-4): 196 runs
- floor_train (folds 1-4 pooled): 261 runs

counted directly from `operators.evaluation.CubicBlock`, the same promoted partition the four floor builders below read.

## Architecture and parameter count

Two `SensorEncoder((32, 128, 128))` branches over rank-32 proper-orthogonal coefficients of the log-compressed spin densities and of the mean-removed spin potentials, combined by an elementwise product in the shared 128-wide latent, split into two 128-wide per-channel rows by one learned channel head, read out by a shared `BasisExpansion(128, (256, 256, 256))` trunk with a bounded zero-to-one head. **Two-branch member: 245632 parameters. Density-alone twin: 224896 parameters** (the twin's density branch, channel head and trunk are seeded identically to the member's own; only the potential branch is absent).

Proper-orthogonal basis decay, fit on 64 of the pooled floor-training runs (a report-scale sample kept small for this section's own timing; the parameter counts above depend only on the fixed rank, not on which runs the fit used):

| branch | gate passed | gate rank | error at rank 8 | error at rank 16 | error at rank 32 |
|---|---|---|---|---|---|
| density | True | 9 | 0.031576 | 0.019330 | 0.007836 |
| potential | True | 22 | 0.074277 | 0.045011 | 0.015209 |

## Floors and the pre-registered ladder

Four localization floors, read live through `operators.evaluation` on the cubic block's own evaluation fold, mean absolute error (the flagship's own kill anchor, recomputed here rather than copied):

| group | metric | units | runs | median | interquartile | 95% interval |
|---|---|---|---|---|---|---|
| semilocal_ridge_floor | mean_absolute_error | 29 | 152 | 0.097618 | 0.002436 | [0.097382, 0.098625] |
| per_shell_filter_floor | mean_absolute_error | 29 | 152 | 0.083022 | 0.008000 | [0.082713, 0.100953] |
| training_mean_trivial_floor | mean_absolute_error | 29 | 152 | 0.015957 | 0.009715 | [0.014533, 0.024347] |
| nearest_run_copy_floor | mean_absolute_error | 29 | 152 | 0.006164 | 0.008750 | [0.005945, 0.016482] |

Pre-registered ladder, absolute mean absolute error, once the member and its twin are trained:

- **the decisive gate** (`test-suite.md`'s own words): two-branch vs density-alone twin, required improvement 5% — kill if the potential branch adds five percent or less; no absolute number until the twin is trained, since the twin is the floor here, not a fixed archive quantity.
- canon pattern rule vs the semilocal ridge, required improvement 20%: two-branch member's own mean absolute error must fall at or below **0.078094**.
- added context, never a kill: beat the training-mean template (**0.015957**), beat the nearest-run copy (**0.006164**), the stretch level at half the template (**0.007978**).

**One-seed caveat, recorded per house policy**: the built branch–trunk family measured a 14-35% seed spread on its own floors on this same block, so a pass by a small margin over the twin is reported as unresolved on one seed, not as a win.

**Dead end, pre-registered**: five percent or less improvement over the density-alone twin — a few-percent pass is "unresolvable on one seed", not a win.

**A defect, found and fixed before any verdict was written.** The first matched-budget run (`elf_fold0_member_33650`, void) never had a working forward pass: the potential branch's own rank-32 coefficients entered the product un-standardized, at roughly 48x the density branch's own scale, which saturated the bounded head (`Bounded_Values`) to exactly 0.0 everywhere from step one -- the recorded validation score (0.091299, unmoved to six digits across all three stages) is what an all-zero prediction scores against this target, not a trained member. See `IMPLEMENTATION.md`'s own defect section for the full diagnosis. **Fix, landed**: `Potential_Coefficient_Statistics` and `Standardized_Potential_Coefficients` center and scale each of the potential basis's rank-32 coefficients by its own training-fold mean and spread before the potential branch ever reads it, leaving the density path -- and the twin's already-trained checkpoint (`elf_fold0_twin_33650`) -- untouched. A host sanity check (300 steps, `learning_rate=1e-3`, card hidden) confirmed the fix trains: validation score 0.076946 at step 25, falling every checkpoint after (one wobble, step 150 to 175) to 0.015901 at step 300 -- below the all-zero baseline (0.0913) from the first checkpoint and still falling at the run's end. The two runs share one step budget, matched by construction: the twin's cost probe measured 0.451 s/step (100 steps, mostly one-time accelerator and kernel-cache initialization), the member's, run second in a fresh process, measured 0.107 s/step against an already-warm kernel cache -- the two probes are not comparable, and sizing each run from its own probe would have handed the twin 7,976 steps against the member's 33,650, confounding the decisive twin-vs-member comparison with unequal training rather than isolating the potential branch's own contribution. Both runs instead took the member's warm-cache figure, 33,650 steps each (the fixed member's own retrain, `elf_fold0_member_v2_33650`).

## Result

Both runs trained under the identical matched 33,650-step schedule and seed, stage-wise best validation score (mean squared error, the training loss's own metric) read from each run's own manifests:

- **density-alone twin** (`elf_fold0_twin_33650`):
  - 10095 steps completed (ran the full stage), best validation 0.001787 at step 6400, 679.8s
  - 10095 steps completed (ran the full stage), best validation 0.001542 at step 8200, 831.2s
  - 1700 steps completed (stopped early by patience), best validation 0.001529 at step 200, 144.4s
  - total wall-clock: 1655.4s (27.6 min)
- **two-branch member (fixed)** (`elf_fold0_member_v2_33650`):
  - 10095 steps completed (ran the full stage), best validation 0.002560 at step 7600, 704.8s
  - 10095 steps completed (ran the full stage), best validation 0.002474 at step 1700, 623.7s
  - 1700 steps completed (stopped early by patience), best validation 0.002453 at step 200, 114.6s
  - total wall-clock: 1443.1s (24.1 min)

Evaluated on fold 0 (the kill block's evaluation split), every card metric, pooled over both spin channels of every run:

| group | metric | units | runs | median | interquartile | 95% interval |
|---|---|---|---|---|---|---|
| member | mean_absolute_error | 29 | 152 | 0.016454 | 0.017463 | [0.015667, 0.030779] |
| member | structural_similarity_3d | 29 | 152 | 0.987451 | 0.021461 | [0.952594, 0.987866] |
| member | relative_l2 | 29 | 152 | 0.069531 | 0.094099 | [0.069938, 0.137758] |
| twin | mean_absolute_error | 29 | 152 | 0.014553 | 0.029947 | [0.018067, 0.034460] |
| twin | structural_similarity_3d | 29 | 152 | 0.991394 | 0.026765 | [0.952164, 0.987112] |
| twin | relative_l2 | 29 | 152 | 0.070017 | 0.119577 | [0.074994, 0.140723] |

Member median mean absolute error **0.016454**, twin **0.014553** (per-campaign and per-functional breakdowns, every card metric, in `results.json`).

| verdict | floor | metric | floor median | member median | improvement | required | result |
|---|---|---|---|---|---|---|---|
| pattern_rule_vs_semilocal_ridge | semilocal_ridge_floor | mean_absolute_error | 0.097618 | 0.016454 | 83.1% | 20.0% | pass |
| decisive_vs_twin | density_alone_twin | mean_absolute_error | 0.014553 | 0.016454 | -13.1% | 5.0% | kill |

**Kill, of a repaired member.** The potential branch adds nothing measurable on this task at this matched budget (or hurts): the member does not beat its density-alone twin by the required 5% improvement. This is the entry's pre-registered dead end -- reached honestly, after the defect above was found and fixed, not from a broken run.

**One-seed caveat, per house policy**: one seeded run each, no five-fold protocol or seed sweep yet -- the built branch-trunk family measured a 14-35% seed spread on its own floors on this same block (pre-registered above), so this verdict is read as what one seed shows, not a sweep-confirmed result.

Figures under `figures/fold_0/` (38 written): the inspection suite, the error spread by campaign, and the member against its floors and the twin.

## Inspection

See `IMPLEMENTATION.md`'s own Inspection section: every branch, projection, the channel head, the composition's carried vector and the trunk's own arrays are reachable by name through `Inspect()`, confirmed by `Test_Every_Inspect_Key_Renders` and `Test_The_Member_Inspects_Under_Part_Prefixes`.

## Standing

Built and tested (`operators/tests/test_multiple_input_operator_network.py`): the assembly, the basis fitting and cache, the gate contract, the product-reduces-to-branch-trunk identity, two-path agreement and gradients on both engines, the twin's shared-name and constant-potential properties, a deterministic toy training run, the full inspection surface, the exact cubic-block fold counts, the built configuration's own parameter counts against the live corpus, and (added after the defect above) the saturation guard confirming real-scale branch latents and a non-saturated bounded head at a fresh init. Floors are pre-registered above, read live through the promoted `operators.evaluation` package. **Both the twin (`elf_fold0_twin_33650`) and the fixed member (`elf_fold0_member_v2_33650`) are trained and evaluated on fold 0 -- see Result for the verdict.** Context, computed from the rows above: the member does not beat the training-mean template floor (0.016454 against 0.015957), and the twin only just does (0.014553, 0.001404 below it). Both sit roughly 7.6x (member) and 6.7x (twin) above the flagship's own 0.002170 mean absolute error on the same block (`factorized_fourier/report.md`).

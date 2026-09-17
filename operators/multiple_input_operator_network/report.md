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

## Result

Not yet run. Training is scheduled by the integrator on the shared card: the density-alone twin then the two-branch member, both under the flagship's staged protocol on the member_train fold, validated on the validation fold, evaluated on the evaluation fold above. **The two runs share one step budget, matched by construction rather than each sized from its own cost probe.** The twin's cost probe measured 0.451 s/step (100 steps, mostly one-time accelerator and kernel-cache initialization); the member's, run second in a fresh process, measured 0.107 s/step against an already-warm kernel cache -- the two probes are not comparable, and sizing each run from its own probe would have handed the twin 7,976 steps against the member's 33,650, confounding the decisive twin-vs-member comparison with unequal training rather than isolating the potential branch's own contribution. Both runs instead take the member's warm-cache figure, 33,650 steps each (the twin, the smaller network, can only finish sooner, never later).

## Inspection

See `IMPLEMENTATION.md`'s own Inspection section: every branch, projection, the channel head, the composition's carried vector and the trunk's own arrays are reachable by name through `Inspect()`, confirmed by `Test_Every_Inspect_Key_Renders` and `Test_The_Member_Inspects_Under_Part_Prefixes`.

## Standing

Built and tested (`operators/tests/test_multiple_input_operator_network.py`): the assembly, the basis fitting and cache, the gate contract, the product-reduces-to-branch-trunk identity, two-path agreement and gradients on both engines, the twin's shared-name and constant-potential properties, a deterministic toy training run, the full inspection surface, the exact cubic-block fold counts, and the built configuration's own parameter counts against the live corpus. Floors are pre-registered above, read live through the promoted `operators.evaluation` package. Not yet run: the twin's and the member's own training, scheduled on the card.

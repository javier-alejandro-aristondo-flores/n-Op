# galerkin_transformer — results

## Stage 1 — perovskite angle stratum, fold 0 (pre-registration, before training)

`lattice_to_charge`, `perovskite_folds` fold 0, angle stratum: 25 evaluation runs scored against the closest of 100 training runs in the same fold, on the shared 64-cubed grid. The linear-in-angle floor is measured separately, over every interior level of the angle arm's own parameter grid, unrestricted by fold (27 interior levels, each bracketed by its own eight corner levels), following the strain atlas's own bracketing-interpolation precedent.

| group | metric | units | runs | median | interquartile | 95% interval |
|---|---|---|---|---|---|---|
| nearest_angle_copy_floor | relative_l2 | 25 | 25 | 0.085278 | 0.006871 | [0.084757, 0.089932] |
| linear_in_angle_interpolation_floor | relative_l2 | 27 | 27 | 0.026421 | 0.000821 | [0.025932, 0.027168] |

**Nearest-angle field copy, relative L2 median = 0.0853** over 25 units, reproducing `deep_operator_network`'s own measurement of this exact floor on this exact fold (0.0853), computed independently here from `operators.training.Parameter_Field_Examples` and `operators.data.Nearest_Training_Run` alone.

**Linear-in-angle interpolation, relative L2 median = 0.0264** over 27 units, through the promoted arm machinery (`All_Perovskite_Arms`, `Interior_Levels`, `Bracket_Corners`, all exported from `operators.factorized_fourier`'s own root). Levels at the edge of the angle grid carry no full eight-corner bracket and are excluded from this floor rather than scored, exactly as `Interior_Levels` itself excludes them -- they would be extrapolation rows, not interpolation ones, and this gate is an interpolation floor.

**The pre-registered stage-1 gate**: within a two-hour wall-clock cap, the member's own relative L2 median on this same angle-stratum evaluation set must fall at or below both of the following, or the entry dies before any fine-grid spend.

1. vs nearest-angle copy (50% improvement): **0.0426**
2. vs linear-in-angle interpolation (50% improvement): **0.0132**

## Stage 2 — the cubic block, fold 0 (pre-registration, before training)

`charge_to_localization`, `paired_fields_fivefold` fold 0: the semilocal-ridge floor, recomputed on this member's own kill block through `operators.evaluation.Elf_Ridge_Rows`, over 152 evaluation run-channels across 29 units.

| group | metric | units | runs | median | interquartile | 95% interval |
|---|---|---|---|---|---|---|
| semilocal_ridge_floor | mean_absolute_error | 29 | 152 | 0.097618 | 0.002436 | [0.097382, 0.098625] |

**The pre-registered stage-2 bar** (the pattern rule, twenty percent better than the ridge; run only once stage 1 passes): mean absolute error at or below **0.078094**.

## Parameter count and memory

- stage 1 (32-cubed tokens): 373377 parameters, 2.849 MiB at float64 (parameters alone)
- stage 2 (40-cubed tokens): 373762 parameters, 2.852 MiB at float64 (parameters alone)

## The training driver

`Train_Perovskite_Gate_Member` is written and covered by this package's own tests: the staged 0.3/0.3/0.4 schedule at learning rates 1e-3, 3.3e-4, 1.1e-4, validating every 100 steps with a final-stage patience of 15, seed 20260916, single precision, checkpoints under `_training/galerkin_transformer/` -- the same staged idiom `factorized_fourier.report.Train_Flagship_Member` uses. **It has not been run.** The card is scheduled by the integrator; the step count for the two-hour cap is chosen from a short timing probe once the card is granted, the same way the deep-equilibrium ladder's own rungs choose theirs.

## Results artifact

`results.json` carries the three floor rows above, written through `operators.evaluation.Write_Member_Results`. It carries no verdicts yet: a verdict compares the member against a floor, and no configuration has trained.

## Standing

No training has run. The gate class, the attention kernel, the query-point decoder and the member are built and pass every test (`operators/tests/test_galerkin_transformer.py`). Both stage-1 floors and the stage-2 semilocal-ridge floor are measured and pre-registered above; the training driver for the stage-1 gate is written but not run. What remains: the card.

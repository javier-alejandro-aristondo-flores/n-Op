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

## Defect found and fixed before any gate verdict

`perovskite_gate_48840` (stopped mid stage 1, validation flat at 1.7422 from the probe onward) was
diagnosed as a real defect, not a dead end -- see `IMPLEMENTATION.md`'s own two sections for the
full numbers. Three fixes:

1. The decoder's query now carries the lattice parameters directly (they were being washed out by
   the token-axis normalization on every path except this one, and training was driving that
   surviving path toward zero).
2. The training loss no longer renormalizes to the electron count -- that belonged only on the
   inference path. A 300-step sanity run showed this alone was not the dominant cause of the run's
   second anomaly (scoring worse than the trivial training-mean field): both the pre-fix and de-
   renormalized loss shapes plateaued 15-16x worse than their own mean-field floor.
3. The training target is now standardized per voxel across the training runs (`Pointwise_Statistics`,
   reused from `operators.deep_operator_network`, the canon's own §A.4-prescribed fix for this
   corpus's cusp-dominated dynamic range), replacing a first attempt at one pooled scalar. A 600-step
   sanity run, reported in the gate's own metric (median relative L2 on the raw density, the 20
   held-out angle-stratum runs): 0.2093 → 0.1787 → 0.1770 → 0.1779 → 0.1772 at steps 0/100/200/300/600,
   against the training-mean field's own 0.1765 on the same runs and the two floors (copy 0.0853,
   interpolation 0.0264); input-dependence at step 600 is 3.87e-2. This closed the gap from 15-16x
   worse to within 1% of the mean field, oscillating just above it rather than clearly below --
   healthier (a stable band, not a persistent large gap) but not yet the integrator's own criterion.

The integrator's own read: the defect is fixed (the network reaches the training-mean field within a
hundred steps instead of sitting sixteen times above it, and input-dependence survives training), and
600 single-example host steps are far too few to resolve the lattice-dependent deviation that is the
whole gap between the mean field and the copy floor. The pre-registered gate now decides on its own
terms: two hours, step count from a fresh `Cost_Probe`, both bars, a miss is a real kill.

**`perovskite_gate_48840` is void and must never be evaluated as this member's result** -- it predates
every fix above. The rerun is `perovskite_gate_v2_52283`.

## Stage-1 gate run

Launched under the fixed member, card granted at 13:40. `Cost_Probe()` measured 0.137711 seconds per
step and a peak of 1,520,456,704 bytes (100 steps, GPU), giving `step_count = floor(7200 / 0.137711) =
52283` for the two-hour cap. Run name `perovskite_gate_v2_52283`, launched detached
(`Train_Perovskite_Gate_Member(52283, "perovskite_gate_v2_52283")`), confirmed on the card by
`nvidia-smi` (process on GPU 0, ~1.6 GiB, ~94% utilization). Pass this run name as this module's own
command-line argument (`python -m operators.galerkin_transformer.report perovskite_gate_v2_52283`)
once it completes, to fold its checkpoint back in and score both bars in one host command.

## Stage 2 — the cubic block, fold 0 (pre-registration, before training)

`charge_to_localization`, `paired_fields_fivefold` fold 0: the semilocal-ridge floor, recomputed on this member's own kill block through `operators.evaluation.Elf_Ridge_Rows`, over 152 evaluation run-channels across 29 units.

| group | metric | units | runs | median | interquartile | 95% interval |
|---|---|---|---|---|---|---|
| semilocal_ridge_floor | mean_absolute_error | 29 | 152 | 0.097618 | 0.002436 | [0.097382, 0.098625] |

**The pre-registered stage-2 bar** (the pattern rule, twenty percent better than the ridge; run only once stage 1 passes): mean absolute error at or below **0.078094**.

## Parameter count and memory

- stage 1 (32-cubed tokens): 374145 parameters, 2.855 MiB at float64 (parameters alone) -- +768 over the
  original 373377 for the decoder's own lattice-parameter condition channels, added while diagnosing why
  the gate was not learning (see "Defect found and fixed before any gate verdict" above)
- stage 2 (40-cubed tokens): 373762 parameters, 2.852 MiB at float64 (parameters alone), unaffected

## The training driver

`Train_Perovskite_Gate_Member` is written and covered by this package's own tests: the staged 0.3/0.3/0.4 schedule at learning rates 1e-3, 3.3e-4, 1.1e-4, validating every 100 steps with a final-stage patience of 15, seed 20260916, single precision, checkpoints under `_training/galerkin_transformer/` -- the same staged idiom `factorized_fourier.report.Train_Flagship_Member` uses. **It has not been run.** The card is scheduled by the integrator; the step count for the two-hour cap is chosen from a short timing probe once the card is granted, the same way the deep-equilibrium ladder's own rungs choose theirs.

## Results artifact

`results.json` carries the three floor rows above written through `operators.evaluation.Write_Member_Results`. It carries no verdicts yet: a verdict compares the member against a floor, and no configuration has trained.

## Standing

No training has run. The gate class, the attention kernel, the query-point decoder and the member are built and pass every test (`operators/tests/test_galerkin_transformer.py`). Both stage-1 floors and the stage-2 semilocal-ridge floor are measured and pre-registered above; the training driver for the stage-1 gate is written but not run. What remains: the card.

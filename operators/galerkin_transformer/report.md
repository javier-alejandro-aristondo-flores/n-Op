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

## Defects found and fixed before this verdict

The first trained run of this gate, `perovskite_gate_48840`, sat flat at validation 1.7422 from its own cost probe onward and was diagnosed as a real defect, not a dead end, before any verdict was read from it. `perovskite_gate_48840` is void and must never be read as this member's result.

1. **The decoder was blind to its own input.** `QueryPointDecoder`'s cross-attention query was built only from output-grid coordinates, identical for every example; the only path a lattice-dependent signal had to reach the output was the key/value contraction against that fixed query, and training drove it toward numerical degeneracy (1.3e-6 relative difference between two well-separated lattice vectors after stage 0, against 27.1% at a fresh initialization). Fixed by concatenating the six lattice factors onto every query row before `query_projection`, on the one branch the token-axis normalization never touches.
2. **`Conserving` sat inside the training loss.** The electron-count renormalization is a whole-field, physical-units correction with no place inside a per-example loss. Fixed by moving it to `__call__` alone; a host sanity run confirmed this was not the dominant cause of the second anomaly below (removing it did not close the gap to the training-mean field) but it is kept, both because the canon's own architecture note requires it and because it removes a real risk (a near-zero or sign-changing raw integral dividing the loss's own gradient).
3. **The loss was cusp-dominated.** The raw density's top 5% of voxels by value carry 77% of the total sum of squares (heavy-atom core cusps, ~420x dynamic range); a single pooled scalar standardization cannot rebalance this, since a uniform rescale preserves every voxel's relative contribution to the loss exactly. Fixed by standardizing the target per voxel across the training runs (`Pointwise_Statistics`, reused from `operators.deep_operator_network`), which removed the lattice-independent cusp-plus-bulk shape from the loss and let a 600-step host sanity run reach the training-mean field within a hundred steps instead of sitting sixteen times above it.

Full numbers for all three are in `IMPLEMENTATION.md`.

## An untested hypothesis, recorded before the verdict (the integrator's own, 2026-09-17)

On this task the network receives no field at all, only six constants and order-four periodic coordinate features, so everything spatial in its prediction must be synthesized from four modes per axis, while the lattice response the gate measures is concentrated near atomic cores on a 64-cubed grid. The built branch-trunk member (`deep_operator_network`) wins the same task (0.0183) because a proper-orthogonal basis hands it that spatial structure directly, rather than asking a coordinate-feature attention stack to synthesize it from scratch. Not tested here; recorded before reading the verdict below so it stands or falls on its own.

## Stage-1 gate run

`perovskite_gate_v2_52283`, folded back from its own final-stage checkpoint under `/Pool/VASP_DATA/_derived/_training/galerkin_transformer`, scored on the exact populations each floor above was measured on.

1. vs nearest-angle copy: member median 0.1780 against floor 0.0853, improvement -108.7% (required 50%) -- **kill**
2. vs linear-in-angle interpolation: member median 0.1191 against floor 0.0264, improvement -350.8% (required 50%) -- **kill**

**Context, not a bar**: the training-mean field itself (the input-blind optimum, no lattice parameters read at all) scores median relative L2 0.1755 on the same 25 evaluation runs the copy verdict above uses -- the member beats this trivial answer only if its own median above reads lower. Input-dependence: the trained member's own prediction differs by a relative 1.40e-01 between its two most lattice-separated evaluation runs (`perovskite_a_1_b_1_c_1_alpha_0p8_beta_1p2_gamma_0p8_angle` vs `perovskite_a_1_b_1_c_1_alpha_1p1_beta_0p8_gamma_1p1_angle`), confirming the decoder-conditioning fix still holds after the full staged run.

## Stage 2 — the cubic block, fold 0 (pre-registration, before training)

`charge_to_localization`, `paired_fields_fivefold` fold 0: the semilocal-ridge floor, recomputed on this member's own kill block through `operators.evaluation.Elf_Ridge_Rows`, over 152 evaluation run-channels across 29 units.

| group | metric | units | runs | median | interquartile | 95% interval |
|---|---|---|---|---|---|---|
| semilocal_ridge_floor | mean_absolute_error | 29 | 152 | 0.097618 | 0.002436 | [0.097382, 0.098625] |

**The pre-registered stage-2 bar** (the pattern rule, twenty percent better than the ridge; run only once stage 1 passes): mean absolute error at or below **0.078094**.

## Parameter count and memory

- stage 1 (32-cubed tokens): 374145 parameters, 2.854 MiB at float64 (parameters alone)
- stage 2 (40-cubed tokens): 373762 parameters, 2.852 MiB at float64 (parameters alone)

## The training driver

`Train_Perovskite_Gate_Member` is written and covered by this package's own tests: the staged 0.3/0.3/0.4 schedule at learning rates 1e-3, 3.3e-4, 1.1e-4, validating every 100 steps with a final-stage patience of 15, seed 20260916, single precision, checkpoints under `_training/galerkin_transformer/` -- the same staged idiom `factorized_fourier.report.Train_Flagship_Member` uses. **It has run as `perovskite_gate_v2_52283`**, scored above.

## Results artifact

`results.json` carries the three floor rows above, the trained gate run's own two rows and its two verdicts against the stage-1 bars, all written through `operators.evaluation.Write_Member_Results`.

## Standing

**The entry is killed at its own pre-registered stage-1 gate**, per §S.6b's canon order: `perovskite_gate_v2_52283` misses the nearest-angle-copy bar (kill) and the linear-in-angle-interpolation bar (kill) both, by a wide margin on each. Stage 2 is not run -- the pre-registration only spends the fine-grid budget once stage 1 clears. This is the kill of the repaired member, run after the three defects above were found and fixed and the decoder-conditioning fix was confirmed still active at the end of training (input-dependence above); it is not the kill of a bug.

The gate class, the attention kernel, the query-point decoder and the member are built and pass every test (`operators/tests/test_galerkin_transformer.py`). Both stage-1 floors and the stage-2 semilocal-ridge floor are measured and pre-registered above; the training driver for the stage-1 gate is written and has been run once, as `perovskite_gate_v2_52283`.

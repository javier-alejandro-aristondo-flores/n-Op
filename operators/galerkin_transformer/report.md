# galerkin_transformer — results

## Stage 1 — perovskite angle stratum, fold 0 (pre-registration, before training)

`lattice_to_charge`, `perovskite_folds` fold 0, angle stratum: 25 evaluation runs scored against the closest of 100 training runs in the same fold, on the shared 64-cubed grid.

| group | metric | units | runs | median | interquartile | 95% interval |
|---|---|---|---|---|---|---|
| nearest_angle_copy_floor | relative_l2 | 25 | 25 | 0.085278 | 0.006871 | [0.084757, 0.089932] |

Pre-registered floor: **nearest-angle field copy, relative L2 median = 0.0853** over 25 units. This reproduces `deep_operator_network`'s own measurement of this exact floor on this exact fold (0.0853), computed independently here from `operators.training.Parameter_Field_Examples` and `operators.data.Nearest_Training_Run` alone — both already exported at their package roots, no promotion needed.

**Blocked: the linear-in-angle interpolation floor.** Needs `Interior_Levels`, `Bracket_Corners` and `Perovskite_Level` from `factorized_fourier/parametric.py`, not yet exported from that package's root (`operators.factorized_fourier`). Per the house rule against reaching into a sibling package's non-root module, this floor is not computed here; it is not duplicated either, since the team lead's brief names this as a promotion landing separately. **Both floors, not just the copy floor, are required by the pre-registration policy before any training spend** — stage 1 training has not started for exactly this reason.

**Blocked: all four stage-2 localization floors**, and `Card_Metric_Errors` / `CubicBlock` / `Write_Member_Results` generally. These are named as landing in `operators.evaluation`; stage 2 is also gated behind a stage-1 pass under the staged protocol, so this is not on the critical path yet.

## Parameter count and memory

- stage 1 (32-cubed tokens): 25761 parameters, 0.197 MiB at float64 (parameters alone)
- stage 2 (40-cubed tokens): 25858 parameters, 0.197 MiB at float64 (parameters alone)

## Standing

No training has run. The gate class, the attention kernel, the query-point decoder and the member are built and pass every test that does not need a not-yet-landed promotion (`operators/tests/test_galerkin_transformer.py`). The stage-1 verdict awaits: the interpolation floor, and the card.

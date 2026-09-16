# alias_free_convolutional — charge density → electron localization field

Convolutional Neural Operator (Raonić et al., NeurIPS 2023), alias-free formalism (Bartolucci et al., ReNO, NeurIPS 2023). Suite entry `test-suite.md` §2, I.2. See `IMPLEMENTATION.md` for the assembly.

## The block

Cubic block (`supercell_strains` and `defect_set`, 80³ charge density, full localization and potential), the same block and the same folds the flagship measures on: 261 runs across folds one through four train the floors, 76 runs in fold zero are the evaluation (kill) block. The member additionally holds out fold one (65 runs) for its own early stopping and trains on folds two through four (196 runs); this member trains at each run's own native 80³ grid rather than a fixed coarse trunk, so no truncate-early step and no processing-shape choice enter here.

## Floors, measured before training, on this exact block, in the card's own metrics

The same four floor recipes the flagship measures on this block (`operators.evaluation`'s ridge, per-shell filter, training-mean and nearest-run-copy builders), shared rather than reimplemented; a floor-reproduction test checks the pooled mean absolute error below against the flagship's own committed 0.0976 / 0.0830 / 0.0160 / 0.0062 (semilocal ridge, per-shell filter, training mean, nearest-run copy) instead of remeasuring the recipe from scratch.

```
group                                           metric                    units  runs  median    interquartile  mean_interval       
training_mean_trivial_floor                     mean_absolute_error       29     152   0.015957  0.009715       [0.014533, 0.024347]
training_mean_trivial_floor__defect_set         mean_absolute_error       21     84    0.020041  0.008650       [0.016943, 0.029456]
training_mean_trivial_floor__supercell_strains  mean_absolute_error       8      68    0.008638  0.003064       [0.008621, 0.011244]
training_mean_trivial_floor                     structural_similarity_3d  29     152   0.980505  0.026177       [0.956125, 0.983483]
training_mean_trivial_floor__defect_set         structural_similarity_3d  21     84    0.972170  0.016709       [0.941630, 0.976949]
training_mean_trivial_floor__supercell_strains  structural_similarity_3d  8      68    0.995883  0.000938       [0.994973, 0.995912]
training_mean_trivial_floor                     relative_l2               29     152   0.108952  0.076542       [0.092727, 0.139848]
training_mean_trivial_floor__defect_set         relative_l2               21     84    0.122575  0.044615       [0.115540, 0.167850]
training_mean_trivial_floor__supercell_strains  relative_l2               8      68    0.050444  0.005401       [0.050162, 0.055151]
nearest_run_copy_floor                          mean_absolute_error       29     152   0.006164  0.008750       [0.005945, 0.016482]
nearest_run_copy_floor__defect_set              mean_absolute_error       21     84    0.008199  0.009580       [0.007936, 0.021768]
nearest_run_copy_floor__supercell_strains       mean_absolute_error       8      68    0.001370  0.001366       [0.000906, 0.003155]
nearest_run_copy_floor                          structural_similarity_3d  29     152   0.996221  0.011146       [0.969391, 0.995315]
nearest_run_copy_floor__defect_set              structural_similarity_3d  21     84    0.993125  0.013094       [0.957748, 0.993262]
nearest_run_copy_floor__supercell_strains       structural_similarity_3d  8      68    0.999951  0.000106       [0.999606, 0.999975]
nearest_run_copy_floor                          relative_l2               29     152   0.049138  0.072021       [0.041470, 0.093111]
nearest_run_copy_floor__defect_set              relative_l2               21     84    0.065131  0.054201       [0.058479, 0.124469]
nearest_run_copy_floor__supercell_strains       relative_l2               8      68    0.005298  0.005426       [0.003474, 0.012532]
per_shell_linear_filter                         mean_absolute_error       29     152   0.083022  0.008000       [0.082713, 0.100953]
per_shell_linear_filter__defect_set             mean_absolute_error       21     84    0.085150  0.011337       [0.085110, 0.107730]
per_shell_linear_filter__supercell_strains      mean_absolute_error       8      68    0.077381  0.002724       [0.076549, 0.080373]
per_shell_linear_filter                         structural_similarity_3d  29     152   0.815885  0.037677       [0.763018, 0.815951]
per_shell_linear_filter__defect_set             structural_similarity_3d  21     84    0.807392  0.044549       [0.741961, 0.807188]
per_shell_linear_filter__supercell_strains      structural_similarity_3d  8      68    0.835137  0.008075       [0.826508, 0.837958]
per_shell_linear_filter                         relative_l2               29     152   0.303498  0.040453       [0.304127, 0.377033]
per_shell_linear_filter__defect_set             relative_l2               21     84    0.311577  0.051323       [0.313317, 0.404893]
per_shell_linear_filter__supercell_strains      relative_l2               8      68    0.285000  0.007036       [0.282651, 0.292622]
semilocal_ridge_floor                           mean_absolute_error       29     152   0.097618  0.002436       [0.097382, 0.098625]
semilocal_ridge_floor__defect_set               mean_absolute_error       21     84    0.098493  0.002166       [0.097950, 0.099363]
semilocal_ridge_floor__supercell_strains        mean_absolute_error       8      68    0.096165  0.000060       [0.096111, 0.096593]
semilocal_ridge_floor                           structural_similarity_3d  29     152   0.673623  0.008570       [0.669465, 0.674315]
semilocal_ridge_floor__defect_set               structural_similarity_3d  21     84    0.671689  0.008721       [0.667754, 0.673931]
semilocal_ridge_floor__supercell_strains        structural_similarity_3d  8      68    0.675335  0.002443       [0.672615, 0.676813]
semilocal_ridge_floor                           relative_l2               29     152   0.392865  0.008385       [0.392230, 0.403318]
semilocal_ridge_floor__defect_set               relative_l2               21     84    0.394206  0.008858       [0.394651, 0.408502]
semilocal_ridge_floor__supercell_strains        relative_l2               8      68    0.386917  0.002346       [0.385693, 0.389308]
```

### the claim ladder, pre-registered before the member has seen this block

Absolute mean absolute error, lower stricter, the same recipe as the flagship's own ladder (`test-suite.md` §2's pattern rule, this entry's own `IMPLEMENTATION.md` kill, then three levels added for scale):

1. **canon kill** (I.1's own bar, half the semilocal ridge): 0.048809
2. **canon pattern rule** (at least 20% better than the ridge or the task is left): 0.078094
3. **added, beat the training-mean template**: 0.015957
4. **added, beat the nearest-run copy**: 0.006164
5. **added, the stretch level** (half the template's error): 0.007978

### the identity check, pre-registered

Two bars this entry alone carries, neither measured yet. Against the trained pointwise twin (`activation="pointwise"`, same widths, same seeds, same augmentation, the canon's own width-matched plain U-Net stand-in): the CNO's own median error must match or beat the twin's, on both lower-is-better card metrics, at the native 80³ grid. And under the grid-shift probe below, the CNO's own error must inflate at most half as much as the twin's does when both answer on an axis-stretched input rather than the native grid. If the twin ties the CNO on both checks, the alias-free surcharge bought nothing and the entry is rejected regardless of how it scores against the floors above.

**The 21 axis-stretched grid-shift probe cells** (`test-suite.md` §2, I.2: "the 21 axis-stretched 72–84 cells"), fixed here before either model trains. Each cell is one evaluation-block run, apportioned across the two campaigns by their own population in that block, paired with a shape drawn independently per axis from {72, 76, 80, 84} — the only lengths in the canon's 72-84 band divisible by four, which is what this composition's own two halvings require of every axis (`Halved_Shape` raises on an odd intermediate; verified directly against this exact assembly, not assumed: an axis of 78 fails at the second halving, landing on `(39, 40, 40)`). The input will be sinc-resampled (`Spectral_Resampled`) to the listed shape before either model sees it; the target is the same run's own coarse localization field, sinc-resampled to that shape's own second scale for comparison. Not yet measured — this table is the pre-registration; the inflation numbers land in the result section once both models are trained.

```
identifier        campaign           shape   
00ce52c5ff6842d9  defect_set         76x80x72
01852d163e6ad1a0  supercell_strains  84x76x84
0c319e6bff1ac46e  defect_set         72x76x76
1f068b6abb829246  supercell_strains  72x72x72
34c5ebd36d43713f  defect_set         80x80x72
37eae386a8cee864  supercell_strains  80x80x84
4f92f5fc69bb6fba  defect_set         72x80x84
5a830b6fe01ad1d0  supercell_strains  84x76x76
730c8c6015bdcd05  supercell_strains  76x80x84
7d478332b1e567ff  defect_set         76x80x84
8a3b7663d7a75387  supercell_strains  76x84x72
8b72ca99d16e99bf  defect_set         80x72x72
a6abfcc5023b5c8e  supercell_strains  72x72x84
a849f55332313401  defect_set         84x72x84
bd21997b36bd2afe  supercell_strains  72x80x84
bd39ceefa779d83c  defect_set         72x72x84
d4282389a52c2112  supercell_strains  76x84x80
de13ca887e2b79d6  defect_set         76x76x72
e88774b3ed2f5e84  defect_set         72x72x80
f3a7432467d00a76  defect_set         76x84x72
fb5a962459358fda  defect_set         80x72x72
```

## The member's own result (electron localization, fold 0)

**pointwise twin** (`elf_fold0_pointwise_twin_<steps>`): training is not yet run; no checkpoint under `/Pool/VASP_DATA/_derived/_training/alias_free_convolutional` yet. This section fills in from a `Latest_Stage_Checkpoint_For_Prefix` lookup alone once one exists, no other change to this report needed.

**CNO (alias-free)** (`elf_fold0_cno_<steps>`): training is not yet run; no checkpoint under `/Pool/VASP_DATA/_derived/_training/alias_free_convolutional` yet. This section fills in from a `Latest_Stage_Checkpoint_For_Prefix` lookup alone once one exists, no other change to this report needed.

## Inspection

Every array `AliasFreeConvolutional.Inspect()` carries is listed in this package's own `IMPLEMENTATION.md`; drawn here on a freshly built (untrained, randomly initialized) member so the surface is confirmed end to end before either training run exists, not asserted from the table alone. 27 files written under `operators/alias_free_convolutional/figures/fold_0/alias_free/untrained`, arrays cached at `/Pool/VASP_DATA/_derived/_figures/alias_free_convolutional/fold_0/alias_free/untrained`. Once a checkpoint exists, this same call on the loaded member draws the trained state instead, no other change to this report needed.

## Standing

Built and tested (`operators.alias_free_convolutional`, its own test file green including the fused activation's gradient and accelerator-memory checks). Floors measured on the real block above and pre-registered before training; the identity check's grid-shift probe set is fixed (21 cells, listed above) before either model has seen it. `Train_Convolutional_Member` and `Cost_Probe` (this module) are written and ready; neither has been run. Card plan once granted: a 300-step cost probe for each activation, then the pointwise twin (cap 8 h), then the CNO (cap 12 h), both augmentation on, seed 20260916, batch one, validation every 100 steps on fold one, final-stage patience 15. Canon rungs on a miss, each tried once before a dead end: drop the Gram channels, then a per-campaign fallback.


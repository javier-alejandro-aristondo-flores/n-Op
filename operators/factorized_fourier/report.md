# factorized_fourier — measured against its floors

Regenerate with `python3 -m operators.factorized_fourier.report`.

Training is not yet run (the accelerator was held by another stream while this section was written);
this first commit records the block and the floors the member will be judged against, exactly as the
doctrine asks for before a single training step is taken. The member's own result, the per-campaign and
per-functional rows, the super-resolution self-consistency check and the figure suite land in a later
commit once training has run.

## The block

Cubic block (`supercell_strains` and `defect_set`, 80³ charge density, full localization and potential): 261 runs across folds one through four train the floors, 76 runs in fold zero are the evaluation (kill) block. The member additionally holds out fold one (65 runs) for its own early stopping and trains on folds two through four (196 runs); the floors keep stage zero's own folds one through four as their training role, so their numbers reproduce stage zero's exactly.

## Floors, measured before training, on this exact block, in the card's own metrics

The ridge fits on the first 80 training runs at 2,000 voxels each, per spin channel; the per-shell filter fits on the first 120, its gains taken from the up channel alone and applied to both; every floor is then scored per run on both spin channels, medians aggregated to the exchangeable split unit first.

```
group                        metric                    units  runs  median    interquartile  mean_interval       
training_mean_trivial_floor  mean_absolute_error       29     152   0.015957  0.009715       [0.014533, 0.024347]
training_mean_trivial_floor  structural_similarity_3d  29     152   0.980505  0.026177       [0.956125, 0.983483]
training_mean_trivial_floor  relative_l2               29     152   0.108952  0.076542       [0.092727, 0.139848]
per_shell_linear_filter      mean_absolute_error       29     152   0.083022  0.008000       [0.082713, 0.100953]
per_shell_linear_filter      structural_similarity_3d  29     152   0.815885  0.037677       [0.763018, 0.815951]
per_shell_linear_filter      relative_l2               29     152   0.303498  0.040453       [0.304127, 0.377033]
semilocal_ridge_floor        mean_absolute_error       29     152   0.097618  0.002436       [0.097382, 0.098625]
semilocal_ridge_floor        structural_similarity_3d  29     152   0.673623  0.008570       [0.669465, 0.674315]
semilocal_ridge_floor        relative_l2               29     152   0.392865  0.008385       [0.392230, 0.403318]
```

### the two bars, recorded before the member has seen this block

- semilocal ridge floor, unit-median mean absolute error: 0.097618
- pattern rule (test-suite.md section 2, at least 20% better or the task is left): 0.078094
- flagship's own bar (IMPLEMENTATION.md, half the floor's error or the member is killed): 0.048809


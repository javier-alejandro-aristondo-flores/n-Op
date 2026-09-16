# residual_correction — measured report

Regenerate with `python -m operators.residual_correction.report` (`--floors-only` to skip training and the conformal band).

## The block

Strain atlas, `cheap_to_accurate_charge` (test-suite.md IV.1), filtered to the campaign's common (40, 40, 40) grid. Train 608 pairs over 173 orbits, validation 83 pairs over 23 orbits, test 88 pairs over 22 orbits. Correction basis rank kept: 32 of 32 requested; cheap-density basis rank kept: 32 of 32 requested.

## Floors, pre-registered before training

```
group                     metric       units  runs  median    interquartile  mean_interval       
identity                  relative_l2  22     88    0.011131  0.000611       [0.010826, 0.011303]
global_affine             relative_l2  22     88    0.010466  0.000482       [0.010224, 0.010593]
ridge_cheap_coefficients  relative_l2  22     88    0.000005  0.000002       [0.000005, 0.000006]
ridge_strain_components   relative_l2  22     88    0.000049  0.000025       [0.000051, 0.000098]
rank_32_ceiling           relative_l2  22     88    0.000002  0.000001       [0.000002, 0.000003]
```

```
group                     floor     floor_median  member_median  improvement  required  verdict
global_affine             identity  0.011131      0.010466       6.0%         0.0%      pass   
ridge_cheap_coefficients  identity  0.011131      0.000005       100.0%       0.0%      pass   
ridge_strain_components   identity  0.011131      0.000049       99.6%        0.0%      pass   
rank_32_ceiling           identity  0.011131      0.000002       100.0%       0.0%      pass   
```

**Canon kill, fixed before training**: the trained member's test-orbit median relative L2 must be at or below `0.005565` (0.5 x the identity floor's `0.011131`), equivalently a delta-R-squared of at least 0.75. The affine and both ridge rows above are context (`required_improvement=0.0`), not kills.

Both ridge floors already sit within a few parts in a million of the rank-32 ceiling. The strain atlas's holdout removes exact symmetry orbits, not nearby strain magnitudes, so a held-out point typically sits a small interpolation step from its nearest training point on the same sweep (measured: about 0.005 in tensor-component units for the shear families) -- the ceiling and the ridge floors are this close because the task is an interpolation-strength holdout on a smooth, low-rank correction field, not because anything is leaking between splits (checked: zero orbit overlap across train, validation and test). The informative comparison for the trained member is therefore not the 50% kill margin, which every closed-form floor already clears by orders of magnitude, but how close its own error lands to the ridge floor and the ceiling.

For the record, unrelated to this member's own metric: the linear-scissor gap floor over 1340 eigenvalue pairs shifts by `1.2231 +/- 0.0572` eV with a `38.6` meV linear residual (r-squared `0.9980`). Any gap read-out is an auxiliary head, never this member, and must beat this scissor on orbit-held-out data.

## Standing

Floors only. Training is scheduled by the team lead and has not run in this worktree yet.


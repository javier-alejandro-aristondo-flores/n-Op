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

## Result (one seed, 20260916)

Divergence probe at `1.00e-03`, staged schedule (stage 0 at 1.00e-03 for 6000 of 6000 steps, stage 1 at 3.33e-04 for 6000 of 6000 steps, stage 2 at 1.11e-04 for 8000 of 8000 steps), validated every 100 steps, final-stage patience 15. 27 figures under `figures/projection_backbone/`.

```
group   metric       units  runs  median    interquartile  mean_interval       
member  relative_l2  22     88    0.002079  0.000094       [0.002051, 0.002137]
```

```
group   floor     floor_median  member_median  improvement  required  verdict
member  identity  0.011131      0.002079       81.3%        50.0%     pass   
```

```
group              metric       units  runs  median    interquartile  mean_interval       
biaxial            relative_l2  3      3     0.002023  0.000024       [0.001986, 0.002034]
isotropic          relative_l2  5      5     0.002050  0.000008       [0.001988, 0.002067]
one_angle_shear    relative_l2  2      9     0.002089  0.000014       [0.002075, 0.002102]
three_angle_shear  relative_l2  2      8     0.002196  0.000099       [0.002097, 0.002296]
triaxial           relative_l2  6      24    0.002133  0.000111       [0.002035, 0.002172]
two_angle_shear    relative_l2  2      36    0.002082  0.000007       [0.002075, 0.002089]
uniaxial           relative_l2  3      3     0.002123  0.000190       [0.001998, 0.002377]
```

```
group   metric           units  runs  median    interquartile  mean_interval       
member  delta_r_squared  22     88    0.964537  0.001376       [0.963332, 0.964882]
```

## Conformal band (IV.3)

Level 0.9, unit `symmetry_orbit`, calibrated on 23 validation orbits, offset `0.012270`. Test-orbit coverage (every voxel of the whole field inside the band, medianed per orbit then averaged): `0.977` against a guarantee of `[0.900, 0.942]`; the band over-covers, sitting `0.036` above the guarantee's upper end -- the calibrated offset is conservative on this test split rather than tight.

## Standing

Verdict: **pass** against the canon kill (`0.005565` relative L2, delta-R-squared >= 0.75), one seeded run (20260916). Per the sweep's own policy (seed sweeps deferred), no seed-spread is measured for this member, so a close result cannot be resolved further on this run alone; it is read at face value.

Against the closed-form ridge from the cheap density's own basis coefficients (`0.000005` relative L2, itself within a few parts in a million of the rank-32 ceiling), the trained member's own error is `406` times larger -- on this interpolation-strength holdout the network adds nothing over linear regression, and the pass above is a pass against the pre-registered canon bar only, not against this closed-form floor.

Caveats: one seed; the FiLM conditioning on campaign and exact-exchange fraction named in the canon entry is dropped here because the strain atlas is one campaign at one exact-exchange fraction, making it a no-op on this block (it is the canon's labeled ablation, not built here); the conditioned-model ablation itself is not run.


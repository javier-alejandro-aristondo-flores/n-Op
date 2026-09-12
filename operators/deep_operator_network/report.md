# deep_operator_network — measured report

Regenerate with `python -m operators.deep_operator_network.report`.
Relative L2 per run, aggregated over symmetry orbits rather than runs, because runs inside
one orbit are exact copies of each other. Two fixed-basis configurations, each on its own
basis: `principal_component` on the raw fields, `proper_orthogonal` on fields standardized
voxel by voxel before the decomposition. A third, `canonical`, replaces both fixed bases with
a learned coordinate trunk, trained point-sampled on every grid shape the campaign holds at
once. Trained on the accelerator in single precision.

Each number below is one training run. A twelve-run seed sweep of the two fixed-basis
configurations measured a seed spread of fourteen to thirty-five percent of the median, and
a difference between configurations of under two percent, so the ordering of any two rows
here is not a finding; the sweep is the finding, and it says they are indistinguishable.
`canonical` is reported from a single seeded run and should be read with the same caution.

## cheap functional, `principal_component` — strain to charge density, held-out test orbits

Train 608 runs, validation 83, test 88 over 22 orbits. Basis rank 32; branch widths (64, 64, 64); 32000 steps chosen on validation. 18 figures under `figures/cheap/principal_component/`.

```
group                       metric       units  runs  median    interquartile  mean_interval       
rank_32_projection_ceiling  relative_l2  22     88    0.000017  0.000009       [0.000018, 0.000029]
ridge_floor                 relative_l2  22     88    0.004140  0.002923       [0.003237, 0.005166]
nearest_neighbor_floor      relative_l2  22     88    0.008958  0.011493       [0.007580, 0.012349]
member                      relative_l2  22     88    0.000821  0.001255       [0.000944, 0.002064]
```

```
group  floor                  floor_median  member_median  improvement  required  verdict
all    ridge_to_coefficients  0.004140      0.000821       80.2%        25.0%     pass   
all    nearest_neighbor_copy  0.008958      0.000821       90.8%        50.0%     pass   
```

```
group              metric       units  runs  median    interquartile  mean_interval       
biaxial            relative_l2  3      3     0.001396  0.000341       [0.001122, 0.001804]
isotropic          relative_l2  5      5     0.003806  0.000600       [0.001845, 0.003913]
one_angle_shear    relative_l2  2      9     0.000462  0.000302       [0.000159, 0.000764]
three_angle_shear  relative_l2  2      8     0.000582  0.000204       [0.000378, 0.000786]
triaxial           relative_l2  6      24    0.000654  0.000782       [0.000505, 0.002470]
two_angle_shear    relative_l2  2      36    0.000564  0.000200       [0.000363, 0.000764]
uniaxial           relative_l2  3      3     0.000766  0.000452       [0.000334, 0.001238]
```

## cheap functional, `proper_orthogonal` — strain to charge density, held-out test orbits

Train 608 runs, validation 83, test 88 over 22 orbits. Basis rank 32; branch widths (64, 64, 64); 32000 steps chosen on validation. 21 figures under `figures/cheap/proper_orthogonal/`.

```
group                       metric       units  runs  median    interquartile  mean_interval       
rank_32_projection_ceiling  relative_l2  22     88    0.000018  0.000008       [0.000018, 0.000031]
ridge_floor                 relative_l2  22     88    0.004140  0.002923       [0.003237, 0.005166]
nearest_neighbor_floor      relative_l2  22     88    0.008958  0.011493       [0.007580, 0.012349]
member                      relative_l2  22     88    0.000819  0.001607       [0.001022, 0.002168]
```

```
group  floor                  floor_median  member_median  improvement  required  verdict
all    ridge_to_coefficients  0.004140      0.000819       80.2%        25.0%     pass   
all    nearest_neighbor_copy  0.008958      0.000819       90.9%        50.0%     pass   
```

```
group              metric       units  runs  median    interquartile  mean_interval       
biaxial            relative_l2  3      3     0.001587  0.000450       [0.001261, 0.002161]
isotropic          relative_l2  5      5     0.003829  0.000409       [0.001765, 0.003871]
one_angle_shear    relative_l2  2      9     0.000473  0.000296       [0.000176, 0.000769]
three_angle_shear  relative_l2  2      8     0.001251  0.000401       [0.000849, 0.001652]
triaxial           relative_l2  6      24    0.000499  0.001112       [0.000457, 0.002718]
two_angle_shear    relative_l2  2      36    0.000570  0.000200       [0.000370, 0.000769]
uniaxial           relative_l2  3      3     0.000642  0.000246       [0.000297, 0.000789]
```

## accurate functional, `principal_component` — strain to charge density, held-out test orbits

Train 608 runs, validation 83, test 88 over 22 orbits. Basis rank 32; branch widths (64, 64, 64); 32000 steps chosen on validation. 18 figures under `figures/accurate/principal_component/`.

```
group                       metric       units  runs  median    interquartile  mean_interval       
rank_32_projection_ceiling  relative_l2  22     88    0.000017  0.000009       [0.000018, 0.000031]
ridge_floor                 relative_l2  22     88    0.004111  0.002887       [0.003235, 0.005144]
nearest_neighbor_floor      relative_l2  22     88    0.008964  0.011493       [0.007578, 0.012347]
member                      relative_l2  22     88    0.001092  0.001182       [0.000965, 0.001785]
```

```
group  floor                  floor_median  member_median  improvement  required  verdict
all    ridge_to_coefficients  0.004111      0.001092       73.4%        25.0%     pass   
all    nearest_neighbor_copy  0.008964      0.001092       87.8%        50.0%     pass   
```

```
group              metric       units  runs  median    interquartile  mean_interval       
biaxial            relative_l2  3      3     0.001916  0.000409       [0.001227, 0.002044]
isotropic          relative_l2  5      5     0.002400  0.001269       [0.001225, 0.002680]
one_angle_shear    relative_l2  2      9     0.000358  0.000089       [0.000269, 0.000447]
three_angle_shear  relative_l2  2      8     0.001134  0.000210       [0.000924, 0.001344]
triaxial           relative_l2  6      24    0.000692  0.000247       [0.000523, 0.002444]
two_angle_shear    relative_l2  2      36    0.000648  0.000200       [0.000447, 0.000848]
uniaxial           relative_l2  3      3     0.001560  0.000696       [0.000220, 0.001613]
```

## accurate functional, `proper_orthogonal` — strain to charge density, held-out test orbits

Train 608 runs, validation 83, test 88 over 22 orbits. Basis rank 32; branch widths (64, 64, 64); 32000 steps chosen on validation. 21 figures under `figures/accurate/proper_orthogonal/`.

```
group                       metric       units  runs  median    interquartile  mean_interval       
rank_32_projection_ceiling  relative_l2  22     88    0.000021  0.000009       [0.000020, 0.000033]
ridge_floor                 relative_l2  22     88    0.004111  0.002887       [0.003235, 0.005144]
nearest_neighbor_floor      relative_l2  22     88    0.008964  0.011493       [0.007578, 0.012347]
member                      relative_l2  22     88    0.001122  0.000986       [0.000972, 0.001901]
```

```
group  floor                  floor_median  member_median  improvement  required  verdict
all    ridge_to_coefficients  0.004111      0.001122       72.7%        25.0%     pass   
all    nearest_neighbor_copy  0.008964      0.001122       87.5%        50.0%     pass   
```

```
group              metric       units  runs  median    interquartile  mean_interval       
biaxial            relative_l2  3      3     0.001497  0.000288       [0.001117, 0.001693]
isotropic          relative_l2  5      5     0.003094  0.002132       [0.001888, 0.003680]
one_angle_shear    relative_l2  2      9     0.000416  0.000215       [0.000201, 0.000631]
three_angle_shear  relative_l2  2      8     0.000645  0.000168       [0.000477, 0.000813]
triaxial           relative_l2  6      24    0.000814  0.000424       [0.000570, 0.002304]
two_angle_shear    relative_l2  2      36    0.000520  0.000111       [0.000408, 0.000631]
uniaxial           relative_l2  3      3     0.001176  0.000355       [0.000481, 0.001191]
```

## cheap functional, `canonical` — strain to charge density, learned coordinate trunk

Trained point-sampled on 928 runs across every grid shape the training role holds; test 88 over 22 orbits on the campaign's common (40, 40, 40) grid, scored exactly as the fixed-basis configurations are. Branch widths (256, 256, 256), latent 256, trunk widths (256, 256, 256), 403200 parameters. 23 figures under `figures/cheap/canonical/`.

This member beats the ridge floor on the common grid (54.2% improvement against a 25% requirement).

```
stage 0 (3e-03, up to 6000 steps): best unit-mean validation 0.000113 at step 3000
stage 1 (1e-03, up to 6000 steps): best unit-mean validation 0.000064 at step 5000
stage 2 (3e-04, up to 8000 steps): best unit-mean validation 0.000025 at step 2700 (stopped early)
```

```
group                   metric       units  runs  median    interquartile  mean_interval       
ridge_floor             relative_l2  22     88    0.004140  0.002923       [0.003237, 0.005166]
nearest_neighbor_floor  relative_l2  22     88    0.008958  0.011493       [0.007580, 0.012349]
member_on_common_grid   relative_l2  22     88    0.001896  0.001590       [0.002103, 0.003179]
```

```
group  floor                  floor_median  member_median  improvement  required  verdict
all    ridge_to_coefficients  0.004140      0.001896       54.2%        25.0%     pass   
all    nearest_neighbor_copy  0.008958      0.001896       78.8%        50.0%     pass   
```

### every shape the test set holds, 9 of them, 124 test runs (124 with a same-shape training neighbor to copy)

The table above restricts training and test to the campaign's single most common grid, because the
fixed-basis configurations cannot read any other. The branch and trunk take a fractional coordinate
regardless of the grid it came from, so this same member trained on every shape in the training role at once (232 MB resident), not only the common one, and is scored below across every shape its own test runs hold, which is the capability the other two configurations do not have.

```
group                               metric       units  runs  median    interquartile  mean_interval       
nearest_neighbor_floor_every_shape  relative_l2  30     124   0.009407  0.013018       [0.009393, 0.013826]
member_every_shape_full_test_set    relative_l2  30     124   0.002339  0.001437       [0.002262, 0.003072]
```

```
group        floor                  floor_median  member_median  improvement  required  verdict
every_shape  nearest_neighbor_copy  0.009407      0.002339       75.1%        50.0%     pass   
```

## accurate functional, `canonical` — strain to charge density, learned coordinate trunk

Trained point-sampled on 928 runs across every grid shape the training role holds; test 88 over 22 orbits on the campaign's common (40, 40, 40) grid, scored exactly as the fixed-basis configurations are. Branch widths (256, 256, 256), latent 256, trunk widths (256, 256, 256), 403200 parameters. 23 figures under `figures/accurate/canonical/`.

This member beats the ridge floor on the common grid (41.3% improvement against a 25% requirement).

```
stage 0 (3e-03, up to 6000 steps): best unit-mean validation 0.000120 at step 3000
stage 1 (1e-03, up to 6000 steps): best unit-mean validation 0.000040 at step 4700
stage 2 (3e-04, up to 8000 steps): best unit-mean validation 0.000027 at step 800 (stopped early)
```

```
group                   metric       units  runs  median    interquartile  mean_interval       
ridge_floor             relative_l2  22     88    0.004111  0.002887       [0.003235, 0.005144]
nearest_neighbor_floor  relative_l2  22     88    0.008964  0.011493       [0.007578, 0.012347]
member_on_common_grid   relative_l2  22     88    0.002413  0.001641       [0.002432, 0.003093]
```

```
group  floor                  floor_median  member_median  improvement  required  verdict
all    ridge_to_coefficients  0.004111      0.002413       41.3%        25.0%     pass   
all    nearest_neighbor_copy  0.008964      0.002413       73.1%        50.0%     pass   
```

### every shape the test set holds, 9 of them, 124 test runs (124 with a same-shape training neighbor to copy)

The table above restricts training and test to the campaign's single most common grid, because the
fixed-basis configurations cannot read any other. The branch and trunk take a fractional coordinate
regardless of the grid it came from, so this same member trained on every shape in the training role at once (232 MB resident), not only the common one, and is scored below across every shape its own test runs hold, which is the capability the other two configurations do not have.

```
group                               metric       units  runs  median    interquartile  mean_interval       
nearest_neighbor_floor_every_shape  relative_l2  30     124   0.009421  0.013016       [0.009389, 0.013822]
member_every_shape_full_test_set    relative_l2  30     124   0.002766  0.001392       [0.002607, 0.003190]
```

```
group        floor                  floor_median  member_median  improvement  required  verdict
every_shape  nearest_neighbor_copy  0.009421      0.002766       70.6%        50.0%     pass   
```

## Standing

- 14 of 14 floor comparisons pass
- the ridge floor is the binding one; the nearest-neighbor copy is roughly threefold weaker, against the suite's expectation that a factorial sweep would make copying brutal
- the basis reconstructs the same fields to a thousandth of the floor, so the error measured here is the parameter map's and none of it the representation's

Caveat: 4 of 4 fixed-basis blocks chose the largest budget offered (32000 steps), so the search did not settle inside its range. Quadrupling the budget moved the member by three to seven percent against a margin it clears by seventy, so the boundary is recorded rather than chased.


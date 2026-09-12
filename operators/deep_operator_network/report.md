# deep_operator_network — measured report

Regenerate with `python -m operators.deep_operator_network.report`.
Relative L2 per run, aggregated over symmetry orbits rather than runs, because runs inside
one orbit are exact copies of each other. Two fixed-basis configurations, each on its own
basis: `principal_component` on the raw fields, `proper_orthogonal` on fields standardized
voxel by voxel before the decomposition. A third, `canonical`, replaces both fixed bases with
a learned coordinate trunk, trained point-sampled on every grid shape the campaign holds at
once. A fourth, `energy_trunk`, is `canonical`'s sibling on the strain-to-states card: the
trunk runs over energy instead of position, both functionals pooled into one member, scored
by the card's own `curve_l1`, `wasserstein_1d` and `gap_edge_error` rather than relative L2.
Trained on the accelerator in single precision.

Each number below is one training run. A twelve-run seed sweep of the two fixed-basis
configurations measured a seed spread of fourteen to thirty-five percent of the median, and
a difference between configurations of under two percent, so the ordering of any two rows
here is not a finding; the sweep is the finding, and it says they are indistinguishable.
`canonical` and `energy_trunk` are each reported from a single seeded run and should be read
with the same caution. `energy_trunk` sets no kill margin and contributes no row to the
floor-comparison standing below: VI.1 fixes none, and a floor winning there is a reportable
result, not a failure.

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

## strain to states, `energy_trunk` — density of states over energy, both functionals pooled

Train 1856 runs, validation 256, test 248 over 30 orbits, cheap and accurate functionals pooled together with the functional as a seventh branch feature beside the six strain components. Branch widths (256, 256), latent 128, trunk widths (128, 128, 128), 4 Fourier orders, 151552 parameters. 22 figures under `figures/pooled/energy_trunk/`. One seeded run; a twelve-run sweep of the fixed-basis configurations measured fourteen to thirty-five percent seed spread, and this member should be read with the same caution.

The aligned window runs -28.0 to 8.0 eV from the valence-band maximum over 601 points at 0.06 eV; it stops short of the conduction band's own ceiling, so the mean curve's final bins are still rising rather than falling, an intentional property of the window and not a bug in the curve. The band-edge region scored separately below is -2 to 6 eV, 133 of 601 bins, where the strain signal was measured to concentrate before this member was trained: the valence band alone is nearly strain-invariant, and dominates the full-window integral roughly fivefold over the band edges.

Trained whole-curve: one fixed batch carrying every training run's full 601-point curve at once (under 5 MB), rather than sampling energies per step, because the whole block fits comfortably in memory and the energy grid is identical across every run; unlike position, there is no varying grid shape here for a point sampler to earn its cost against. The trunk's own feature map reads the energy coordinate after it is rescaled from the aligned window onto minus one to one; the branch's seven features are each standardized by their own spread across the training block. The loss trained here is the card's own `curve_l1`, made differentiable as each run's own L1 residual normalized by that run's own curve size and then averaged over runs, unweighted across the window, exactly as the card specifies.

The full-window `curve_l1` below is the headline the card mandates, and it is expected to look unimpressive regardless of model quality: 467 of 601 bins are valence-band states that are nearly strain-invariant, diluting real skill roughly fivefold. The band-edge score beside it, plus `wasserstein_1d` and `gap_edge_error`, carry the information this task actually turns on. No kill margin is set for this configuration, since the canon fixes none for VI.1, and a floor winning here is an informative, reportable outcome on a coarse spectral function, not a failure.

```
stage 0 (2e-03, up to 800 steps): best unit-mean validation 0.224747 at step 800
stage 1 (7e-04, up to 1200 steps): best unit-mean validation 0.180202 at step 1160
stage 2 (2e-04, up to 5000 steps): best unit-mean validation 0.141546 at step 5000
```

Caveat: the final stage's validation score was still improving at its last step, so the search did not settle inside its budget. Measured directly: extending that stage from 2000 to 5000 steps (2.5x the compute) moved the member's whole-window median from 0.217 to 0.206 (5.1%) and its band-edge median from 0.270 to 0.265 (1.9%) against a ridge floor it already cleared by over 40% at the shorter budget, so the boundary is recorded rather than chased further.

```
group                metric              units  runs  median    interquartile  mean_interval       
training_mean_floor  curve_l1_whole      30     248   0.392161  0.108072       [0.379294, 0.427156]
training_mean_floor  curve_l1_band_edge  30     248   0.756956  0.490013       [0.769093, 0.964555]
training_mean_floor  wasserstein_1d      30     248   1.231802  0.141469       [1.236388, 1.411393]
training_mean_floor  gap_edge_error      30     248   0.000000  0.000000       [0.000000, 0.019500]
ridge_floor          curve_l1_whole      30     248   0.368105  0.115723       [0.327978, 0.382238]
ridge_floor          curve_l1_band_edge  30     248   0.517723  0.124499       [0.470968, 0.555277]
ridge_floor          wasserstein_1d      30     248   0.408620  0.188192       [0.372466, 0.469092]
ridge_floor          gap_edge_error      30     248   0.000000  0.000000       [0.000000, 0.019500]
member               curve_l1_whole      30     248   0.206032  0.056304       [0.182025, 0.228441]
member               curve_l1_band_edge  30     248   0.264763  0.115160       [0.239503, 0.307909]
member               wasserstein_1d      30     248   0.156582  0.122827       [0.144733, 0.244455]
member               gap_edge_error      30     248   1.912500  0.735000       [1.538962, 1.994012]
```

`gap_edge_error` reads near zero for both floors and not for the member, and that is the metric's own limit, not a physics failure. `test-suite.md` already calls the support-edge read-out a diagnostic only, next to the trusted occupancy-walk gap, and this is why: measured directly, every one of the 248 test truths crosses one percent of its own peak at exactly +0.02 eV, one grid step past the valence-band maximum, with zero variance across every strain family — because the smearing that rebuilds every curve here bridges the sharp valence edge into a shoulder that crosses the threshold long before the true conduction band starts, for any curve shaped like a real one. A floor built from real curves inherits that shoulder and reads a near-zero gap error by sharing the artifact, not by finding the gap. The member's own curve is smoother — a handful of Fourier orders and a softplus head cannot fall back to exact zero the way a sharp, smeared feature does — so it clears one percent of its own peak further out, and its larger `gap_edge_error` is a property of that smoothness, not evidence the map is worse at the physics.

Ridge's skill over the training-mean floor: 6.1% on the whole window, 31.6% on the band-edge region. The member's skill over the same floor: 47.5% whole-window, 65.0% band-edge. The member against the ridge floor directly: 44.0% whole-window, 48.9% band-edge.

```
group     metric          units  runs  median    interquartile  mean_interval       
accurate  curve_l1_whole  30     124   0.214698  0.048480       [0.188695, 0.236576]
cheap     curve_l1_whole  30     124   0.194840  0.067638       [0.174497, 0.220788]
```

```
group              metric          units  runs  median    interquartile  mean_interval       
biaxial            curve_l1_whole  4      8     0.226831  0.019941       [0.211886, 0.247427]
isotropic          curve_l1_whole  5      10    0.212864  0.040797       [0.186638, 0.285032]
one_angle_shear    curve_l1_whole  2      24    0.085409  0.012633       [0.072776, 0.098041]
three_angle_shear  curve_l1_whole  2      24    0.127615  0.008053       [0.119562, 0.135668]
triaxial           curve_l1_whole  12     102   0.199236  0.033527       [0.191908, 0.237670]
two_angle_shear    curve_l1_whole  2      72    0.070845  0.001931       [0.068913, 0.072776]
uniaxial           curve_l1_whole  4      8     0.246609  0.034505       [0.234490, 0.302434]
```

### band-edge-weighted loss — ablation, not the card's loss and not a substitute for the row above

The same architecture and schedule, trained instead on a loss that weighs the -2 to 6 eV region 5x the rest of the window in both the residual and the normalizer.

```
stage 0 (2e-03, up to 800 steps): best unit-mean validation 0.236898 at step 800
stage 1 (7e-04, up to 1200 steps): best unit-mean validation 0.187834 at step 1160
stage 2 (2e-04, up to 5000 steps): best unit-mean validation 0.152676 at step 5000
```

```
group                               metric              units  runs  median    interquartile  mean_interval       
member_band_edge_weighted_ablation  curve_l1_whole      30     248   0.208393  0.059322       [0.186312, 0.232664]
member_band_edge_weighted_ablation  curve_l1_band_edge  30     248   0.193485  0.142184       [0.187545, 0.254465]
member_band_edge_weighted_ablation  wasserstein_1d      30     248   0.158520  0.152554       [0.146312, 0.238249]
member_band_edge_weighted_ablation  gap_edge_error      30     248   0.000000  0.000000       [0.081000, 0.470500]
```

The ablation's `gap_edge_error` lands back near zero, which is consistent with the mechanism above rather than against it: weighing the band-edge region five times over pushes this member to reproduce the smearing shoulder precisely enough to cross one percent of peak at the same point the floors do, at the cost of the valence band it no longer weighs as heavily.

## Standing

- 14 of 14 floor comparisons pass
- the ridge floor is the binding one; the nearest-neighbor copy is roughly threefold weaker, against the suite's expectation that a factorial sweep would make copying brutal
- the basis reconstructs the same fields to a thousandth of the floor, so the error measured here is the parameter map's and none of it the representation's

Caveat: 4 of 4 fixed-basis blocks chose the largest budget offered (32000 steps), so the search did not settle inside its range. Quadrupling the budget moved the member by three to seven percent against a margin it clears by seventy, so the boundary is recorded rather than chased.


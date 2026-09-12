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

## lattice_to_charge — perovskite grid, `test-suite.md` §3, II.1b

The same member as strain_to_charge, on a different campaign: the branch reads the six lattice
factors `(a, b, c, alpha, beta, gamma)` (`Lattice_Factors_Of`) instead of a strain tensor, split
`perovskite_folds` instead of the strain holdout, conservation `renormalize_to_electron_count`
mandated on the density output. `energy_trunk` does not apply: this card has no eigenvalue target.

The campaign splits into two strata by grid shape, measured directly: the angle stratum is 125
runs, every one on the shared 64-cubed grid; the length stratum is 124 runs on 124 distinct grid
shapes. The fixed-basis configurations (`principal_component`, `proper_orthogonal`) need one
common shape to stack fields into a basis, so they train and are scored on the angle stratum
alone — roughly 100 training runs per fold. `canonical` trains point-sampled across both strata
at once and is the only configuration that can read the length stratum's 124 distinct shapes at
all; that row is the number no fixed basis can produce.

The target's dynamic range is far wider than the strain atlas's: measured directly, the peak
density sits at 15.47 to 15.68 e/A^3 at the heavy-atom cores across the whole campaign, and the
angle stratum's own cell volume varies only 1.24x while the length stratum's varies 3.375x, even
though the electron count is fixed at 48.0 for every run. A plain mean-squared error in raw voxel
units would let the length stratum's smallest cells dominate canonical's point-sampled loss.
`canonical` therefore standardizes each sampled run's own target by that run's own reference
density — electron count over its own cell volume, the field's exact spatial mean, known from the
branch's own input and never from the truth — before the loss compares it to the branch's raw
output, and restores it by the same factor before any figure or metric sees it. The fixed-basis
pair keeps its existing coefficient-space loss unchanged: the angle stratum's 1.24x volume range
is mild, and its per-coefficient standardization already conditions that loss; `relative_l2` and
`frequency_split_relative_l2` are themselves invariant to a positive per-run rescaling applied
identically to a prediction and its truth, so this choice changes no reported number, only what
the loss optimizes toward.

`renormalize_to_electron_count` (`operators.wrappers.Conserving`) is applied to every reported
prediction on the whole-field path, never to a point batch, which carries no quadrature weight.
Ground truth integrates to 48.0 electrons to within a few parts in 10^8 on every run measured, so
the scale this law applies at inference is pure model error, reported as a free diagnostic beside
each block's own numbers.

Fold 0 is where the training budget is chosen, among the same five candidate step counts the
fixed-basis pair otherwise searches, for every configuration including `canonical`. Both
extrapolation holdouts reuse whichever budget fold 0 chose for that configuration rather than
re-searching, so nine trainings become three searches plus six fixed-budget runs. The two holdout
splits hold out every factor-0.8 run, separately every factor-1.2 run, and are labeled
`extrapolation` throughout; fold 0 is `interpolation`. One seeded run per block, as elsewhere in
this report.

## lattice_to_charge, `fold_0`, `principal_component` — perovskite angle stratum, interpolation

Train 80 runs, validation 20, test 25, all on the shared (64, 64, 64) grid. Basis rank 32; branch widths (64, 64, 64); 32000 steps (chosen on validation). Conservation scale (`renormalize_to_electron_count`), median: 0.998902. 17 figures under `figures/perovskite/fold_0/principal_component/`.

```
group                       metric                            units  runs  median    interquartile  mean_interval       
rank_32_projection_ceiling  relative_l2                       25     25    0.001316  0.000507       [0.001232, 0.002418]
training_mean_floor         relative_l2                       25     25    0.178087  0.045280       [0.168453, 0.207408]
ridge_floor                 relative_l2                       25     25    0.042314  0.013703       [0.042750, 0.059871]
nearest_neighbor_floor      relative_l2                       25     25    0.085278  0.006871       [0.084846, 0.089862]
member                      relative_l2                       25     25    0.018347  0.014993       [0.016950, 0.027453]
member                      frequency_split_relative_l2_low   25     25    0.016584  0.015236       [0.015140, 0.024223]
member                      frequency_split_relative_l2_high  25     25    0.122894  0.052096       [0.119235, 0.158320]
```

```
group   floor                  floor_median  member_median  improvement  required  verdict
fold_0  ridge_to_coefficients  0.042314      0.018347       56.6%        25.0%     pass   
fold_0  nearest_neighbor_copy  0.085278      0.018347       78.5%        50.0%     pass   
```

## lattice_to_charge, `fold_0`, `proper_orthogonal` — perovskite angle stratum, interpolation

Train 80 runs, validation 20, test 25, all on the shared (64, 64, 64) grid. Basis rank 32; branch widths (64, 64, 64); 32000 steps (chosen on validation). Conservation scale (`renormalize_to_electron_count`), median: 0.997344. 20 figures under `figures/perovskite/fold_0/proper_orthogonal/`.

```
group                       metric                            units  runs  median    interquartile  mean_interval       
rank_32_projection_ceiling  relative_l2                       25     25    0.001593  0.000737       [0.001542, 0.002909]
training_mean_floor         relative_l2                       25     25    0.178087  0.045280       [0.168453, 0.207408]
ridge_floor                 relative_l2                       25     25    0.042314  0.013703       [0.042750, 0.059871]
nearest_neighbor_floor      relative_l2                       25     25    0.085278  0.006871       [0.084846, 0.089862]
member                      relative_l2                       25     25    0.018911  0.004961       [0.016175, 0.022753]
member                      frequency_split_relative_l2_low   25     25    0.016705  0.005985       [0.014558, 0.020798]
member                      frequency_split_relative_l2_high  25     25    0.136821  0.033674       [0.130534, 0.160327]
```

```
group   floor                  floor_median  member_median  improvement  required  verdict
fold_0  ridge_to_coefficients  0.042314      0.018911       55.3%        25.0%     pass   
fold_0  nearest_neighbor_copy  0.085278      0.018911       77.8%        50.0%     pass   
```

## lattice_to_charge, `fold_0`, `canonical` — perovskite grid, interpolation, learned coordinate trunk

Trained point-sampled on 160 runs across both strata (39 held for validation); test on the angle stratum's 25 runs on the shared (64, 64, 64) grid, scored exactly as the fixed-basis configurations are. Branch widths (256, 256, 256), latent 256, trunk widths (256, 256, 256). 32000 steps (chosen on its own held-out training loss). Conservation scale on the angle stratum, median: 0.995138. 22 figures under `figures/perovskite/fold_0/canonical/`.

```
group                    metric                            units  runs  median    interquartile  mean_interval       
training_mean_floor      relative_l2                       25     25    0.178087  0.045280       [0.168453, 0.207408]
ridge_floor              relative_l2                       25     25    0.042314  0.013703       [0.042750, 0.059871]
nearest_neighbor_floor   relative_l2                       25     25    0.085278  0.006871       [0.084846, 0.089862]
member_on_angle_stratum  relative_l2                       25     25    0.023488  0.009614       [0.024011, 0.035745]
member_on_angle_stratum  frequency_split_relative_l2_low   25     25    0.020836  0.009498       [0.020865, 0.032098]
member_on_angle_stratum  frequency_split_relative_l2_high  25     25    0.867094  0.120034       [0.848296, 0.965985]
```

```
group   floor                  floor_median  member_median  improvement  required  verdict
fold_0  ridge_to_coefficients  0.042314      0.023488       44.5%        25.0%     pass   
fold_0  nearest_neighbor_copy  0.085278      0.023488       72.5%        50.0%     pass   
```

### every shape this split's test set holds, 26 of them, 50 test runs (25 on the length stratum's own unique grid, 25 on the angle stratum's shared one; 25 had a same-shape training neighbor to copy)

The table above restricts training and test to the angle stratum's one shared grid, because the
fixed-basis configurations cannot read any other. This same member trained on every shape the
training role holds at once (175 MB resident), including the
length stratum's own distinct grid per run, and is scored below across every shape its own test runs
hold — the capability the fixed-basis pair does not have. Every length-stratum run sits on a grid
shape unique to that one run, so it carries no same-shape training neighbor for the copy floor to
read; the conservation scale across every shape, median: 0.994713.

```
group                               metric       units  runs  median    interquartile  mean_interval       
nearest_neighbor_floor_every_shape  relative_l2  25     25    0.085278  0.006870       [0.084264, 0.089539]
member_every_shape_full_test_set    relative_l2  50     50    0.024837  0.009494       [0.025379, 0.032186]
angle                               relative_l2  25     25    0.023488  0.009614       [0.024011, 0.035745]
length                              relative_l2  25     25    0.026812  0.009136       [0.024638, 0.030993]
```

```
group               floor                  floor_median  member_median  improvement  required  verdict
fold_0_every_shape  nearest_neighbor_copy  0.085278      0.023488       72.5%        50.0%     pass   
```

## lattice_to_charge, `holdout_factor_0p8`, `principal_component` — perovskite angle stratum, extrapolation

Train 52 runs, validation 12, test 61, all on the shared (64, 64, 64) grid. Basis rank 32; branch widths (64, 64, 64); 32000 steps (reused from fold_0's own search). Conservation scale (`renormalize_to_electron_count`), median: 1.020491. 17 figures under `figures/perovskite/holdout_factor_0p8/principal_component/`.

```
group                       metric                            units  runs  median    interquartile  mean_interval       
rank_32_projection_ceiling  relative_l2                       61     61    0.005293  0.002190       [0.005997, 0.007667]
training_mean_floor         relative_l2                       61     61    0.239122  0.062842       [0.236621, 0.257973]
ridge_floor                 relative_l2                       61     61    0.075542  0.048902       [0.078398, 0.095413]
nearest_neighbor_floor      relative_l2                       61     61    0.087692  0.033546       [0.096885, 0.110390]
member                      relative_l2                       61     61    0.093658  0.083947       [0.101091, 0.126386]
member                      frequency_split_relative_l2_low   61     61    0.086908  0.074034       [0.092104, 0.114732]
member                      frequency_split_relative_l2_high  61     61    0.449357  0.204739       [0.457813, 0.530411]
```

```
group               floor                  floor_median  member_median  improvement  required  verdict
holdout_factor_0p8  ridge_to_coefficients  0.075542      0.093658       -24.0%       25.0%     kill   
holdout_factor_0p8  nearest_neighbor_copy  0.087692      0.093658       -6.8%        50.0%     kill   
```

## lattice_to_charge, `holdout_factor_0p8`, `proper_orthogonal` — perovskite angle stratum, extrapolation

Train 52 runs, validation 12, test 61, all on the shared (64, 64, 64) grid. Basis rank 32; branch widths (64, 64, 64); 32000 steps (reused from fold_0's own search). Conservation scale (`renormalize_to_electron_count`), median: 1.032354. 20 figures under `figures/perovskite/holdout_factor_0p8/proper_orthogonal/`.

```
group                       metric                            units  runs  median    interquartile  mean_interval       
rank_32_projection_ceiling  relative_l2                       61     61    0.009346  0.002666       [0.010055, 0.012280]
training_mean_floor         relative_l2                       61     61    0.239122  0.062842       [0.236621, 0.257973]
ridge_floor                 relative_l2                       61     61    0.075542  0.048902       [0.078398, 0.095413]
nearest_neighbor_floor      relative_l2                       61     61    0.087692  0.033546       [0.096885, 0.110390]
member                      relative_l2                       61     61    0.126383  0.067298       [0.118390, 0.143428]
member                      frequency_split_relative_l2_low   61     61    0.113577  0.051645       [0.106978, 0.129478]
member                      frequency_split_relative_l2_high  61     61    0.486244  0.201618       [0.502181, 0.577905]
```

```
group               floor                  floor_median  member_median  improvement  required  verdict
holdout_factor_0p8  ridge_to_coefficients  0.075542      0.126383       -67.3%       25.0%     kill   
holdout_factor_0p8  nearest_neighbor_copy  0.087692      0.126383       -44.1%       50.0%     kill   
```

## lattice_to_charge, `holdout_factor_0p8`, `canonical` — perovskite grid, extrapolation, learned coordinate trunk

Trained point-sampled on 102 runs across both strata (25 held for validation); test on the angle stratum's 61 runs on the shared (64, 64, 64) grid, scored exactly as the fixed-basis configurations are. Branch widths (256, 256, 256), latent 256, trunk widths (256, 256, 256). 32000 steps (reused from fold_0). Conservation scale on the angle stratum, median: 0.984415. 22 figures under `figures/perovskite/holdout_factor_0p8/canonical/`.

```
group                    metric                            units  runs  median    interquartile  mean_interval       
training_mean_floor      relative_l2                       61     61    0.239122  0.062842       [0.236621, 0.257973]
ridge_floor              relative_l2                       61     61    0.075542  0.048902       [0.078398, 0.095413]
nearest_neighbor_floor   relative_l2                       61     61    0.087692  0.033546       [0.096885, 0.110390]
member_on_angle_stratum  relative_l2                       61     61    0.043351  0.024903       [0.046445, 0.061855]
member_on_angle_stratum  frequency_split_relative_l2_low   61     61    0.037918  0.022202       [0.041764, 0.056512]
member_on_angle_stratum  frequency_split_relative_l2_high  61     61    1.047368  0.128302       [1.033511, 1.080486]
```

```
group               floor                  floor_median  member_median  improvement  required  verdict
holdout_factor_0p8  ridge_to_coefficients  0.075542      0.043351       42.6%        25.0%     pass   
holdout_factor_0p8  nearest_neighbor_copy  0.087692      0.043351       50.6%        50.0%     pass   
```

### every shape this split's test set holds, 62 of them, 122 test runs (61 on the length stratum's own unique grid, 61 on the angle stratum's shared one; 61 had a same-shape training neighbor to copy)

The table above restricts training and test to the angle stratum's one shared grid, because the
fixed-basis configurations cannot read any other. This same member trained on every shape the
training role holds at once (120 MB resident), including the
length stratum's own distinct grid per run, and is scored below across every shape its own test runs
hold — the capability the fixed-basis pair does not have. Every length-stratum run sits on a grid
shape unique to that one run, so it carries no same-shape training neighbor for the copy floor to
read; the conservation scale across every shape, median: 0.986439.

```
group                               metric       units  runs  median    interquartile  mean_interval       
nearest_neighbor_floor_every_shape  relative_l2  61     61    0.086880  0.044565       [0.097261, 0.113767]
member_every_shape_full_test_set    relative_l2  122    122   0.044311  0.022965       [0.051405, 0.067486]
angle                               relative_l2  61     61    0.043351  0.024903       [0.046445, 0.061855]
length                              relative_l2  61     61    0.046593  0.020091       [0.051879, 0.079571]
```

```
group                           floor                  floor_median  member_median  improvement  required  verdict
holdout_factor_0p8_every_shape  nearest_neighbor_copy  0.086880      0.043351       50.1%        50.0%     pass   
```

## lattice_to_charge, `holdout_factor_1p2`, `principal_component` — perovskite angle stratum, extrapolation

Train 52 runs, validation 12, test 61, all on the shared (64, 64, 64) grid. Basis rank 32; branch widths (64, 64, 64); 32000 steps (reused from fold_0's own search). Conservation scale (`renormalize_to_electron_count`), median: 1.024225. 17 figures under `figures/perovskite/holdout_factor_1p2/principal_component/`.

```
group                       metric                            units  runs  median    interquartile  mean_interval       
rank_32_projection_ceiling  relative_l2                       61     61    0.005771  0.002066       [0.006159, 0.007978]
training_mean_floor         relative_l2                       61     61    0.230601  0.048050       [0.234762, 0.255644]
ridge_floor                 relative_l2                       61     61    0.076563  0.032457       [0.076037, 0.091758]
nearest_neighbor_floor      relative_l2                       61     61    0.087692  0.024297       [0.094403, 0.107381]
member                      relative_l2                       61     61    0.058368  0.023621       [0.059225, 0.072413]
member                      frequency_split_relative_l2_low   61     61    0.053828  0.023102       [0.055058, 0.067739]
member                      frequency_split_relative_l2_high  61     61    0.331913  0.118799       [0.326123, 0.363857]
```

```
group               floor                  floor_median  member_median  improvement  required  verdict
holdout_factor_1p2  ridge_to_coefficients  0.076563      0.058368       23.8%        25.0%     kill   
holdout_factor_1p2  nearest_neighbor_copy  0.087692      0.058368       33.4%        50.0%     kill   
```

## lattice_to_charge, `holdout_factor_1p2`, `proper_orthogonal` — perovskite angle stratum, extrapolation

Train 52 runs, validation 12, test 61, all on the shared (64, 64, 64) grid. Basis rank 32; branch widths (64, 64, 64); 32000 steps (reused from fold_0's own search). Conservation scale (`renormalize_to_electron_count`), median: 1.027573. 20 figures under `figures/perovskite/holdout_factor_1p2/proper_orthogonal/`.

```
group                       metric                            units  runs  median    interquartile  mean_interval       
rank_32_projection_ceiling  relative_l2                       61     61    0.009129  0.003530       [0.009950, 0.012550]
training_mean_floor         relative_l2                       61     61    0.230601  0.048050       [0.234762, 0.255644]
ridge_floor                 relative_l2                       61     61    0.076563  0.032457       [0.076037, 0.091758]
nearest_neighbor_floor      relative_l2                       61     61    0.087692  0.024297       [0.094403, 0.107381]
member                      relative_l2                       61     61    0.060645  0.018741       [0.058528, 0.070677]
member                      frequency_split_relative_l2_low   61     61    0.054073  0.017369       [0.053000, 0.064557]
member                      frequency_split_relative_l2_high  61     61    0.335127  0.076257       [0.328560, 0.358500]
```

```
group               floor                  floor_median  member_median  improvement  required  verdict
holdout_factor_1p2  ridge_to_coefficients  0.076563      0.060645       20.8%        25.0%     kill   
holdout_factor_1p2  nearest_neighbor_copy  0.087692      0.060645       30.8%        50.0%     kill   
```

## lattice_to_charge, `holdout_factor_1p2`, `canonical` — perovskite grid, extrapolation, learned coordinate trunk

Trained point-sampled on 102 runs across both strata (25 held for validation); test on the angle stratum's 61 runs on the shared (64, 64, 64) grid, scored exactly as the fixed-basis configurations are. Branch widths (256, 256, 256), latent 256, trunk widths (256, 256, 256). 32000 steps (reused from fold_0). Conservation scale on the angle stratum, median: 1.002923. 22 figures under `figures/perovskite/holdout_factor_1p2/canonical/`.

```
group                    metric                            units  runs  median    interquartile  mean_interval       
training_mean_floor      relative_l2                       61     61    0.230601  0.048050       [0.234762, 0.255644]
ridge_floor              relative_l2                       61     61    0.076563  0.032457       [0.076037, 0.091758]
nearest_neighbor_floor   relative_l2                       61     61    0.087692  0.024297       [0.094403, 0.107381]
member_on_angle_stratum  relative_l2                       61     61    0.049944  0.034264       [0.054638, 0.070453]
member_on_angle_stratum  frequency_split_relative_l2_low   61     61    0.044784  0.034988       [0.049520, 0.064493]
member_on_angle_stratum  frequency_split_relative_l2_high  61     61    0.885487  0.113292       [0.868292, 0.910249]
```

```
group               floor                  floor_median  member_median  improvement  required  verdict
holdout_factor_1p2  ridge_to_coefficients  0.076563      0.049944       34.8%        25.0%     pass   
holdout_factor_1p2  nearest_neighbor_copy  0.087692      0.049944       43.0%        50.0%     kill   
```

### every shape this split's test set holds, 62 of them, 122 test runs (61 on the length stratum's own unique grid, 61 on the angle stratum's shared one; 61 had a same-shape training neighbor to copy)

The table above restricts training and test to the angle stratum's one shared grid, because the
fixed-basis configurations cannot read any other. This same member trained on every shape the
training role holds at once (104 MB resident), including the
length stratum's own distinct grid per run, and is scored below across every shape its own test runs
hold — the capability the fixed-basis pair does not have. Every length-stratum run sits on a grid
shape unique to that one run, so it carries no same-shape training neighbor for the copy floor to
read; the conservation scale across every shape, median: 1.001073.

```
group                               metric       units  runs  median    interquartile  mean_interval       
nearest_neighbor_floor_every_shape  relative_l2  61     61    0.087692  0.025596       [0.096210, 0.110031]
member_every_shape_full_test_set    relative_l2  122    122   0.046085  0.016869       [0.049903, 0.058541]
angle                               relative_l2  61     61    0.049944  0.034264       [0.054638, 0.070453]
length                              relative_l2  61     61    0.042804  0.014034       [0.042992, 0.048780]
```

```
group                           floor                  floor_median  member_median  improvement  required  verdict
holdout_factor_1p2_every_shape  nearest_neighbor_copy  0.087692      0.049944       43.0%        50.0%     kill   
```

`energy_trunk` does not apply to `lattice_to_charge`: the card has no eigenvalue target, so no
block for it appears in this section.

## Standing

- 25 of 35 floor comparisons pass
- the ridge floor is the binding one; the nearest-neighbor copy is roughly threefold weaker, against the suite's expectation that a factorial sweep would make copying brutal
- the basis reconstructs the same fields to a thousandth of the floor, so the error measured here is the parameter map's and none of it the representation's

Caveat: 4 of 4 fixed-basis blocks chose the largest budget offered (32000 steps), so the search did not settle inside its range. Quadrupling the budget moved the member by three to seven percent against a margin it clears by seventy, so the boundary is recorded rather than chased.


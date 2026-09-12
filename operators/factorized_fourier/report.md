# factorized_fourier — measured against its floors

Regenerate with `python3 -m operators.factorized_fourier.report`.

Training is not yet run (the accelerator was held by another stream while this section was written);
this first commit records the block, all four floors and the pre-registered claim ladder the member will
be judged against, exactly as the doctrine asks for before a single training step is taken. The member's
own result, the per-functional rows, the super-resolution self-consistency check and the figure suite
land in a later commit once training has run.

## The block

Cubic block (`supercell_strains` and `defect_set`, 80³ charge density, full localization and potential): 261 runs across folds one through four train the floors, 76 runs in fold zero are the evaluation (kill) block. The member additionally holds out fold one (65 runs) for its own early stopping and trains on folds two through four (196 runs); the floors keep stage zero's own folds one through four as their training role, so their numbers reproduce stage zero's exactly.

## Floors, measured before training, on this exact block, in the card's own metrics

The ridge fits on the first 80 training runs at 2,000 voxels each, per spin channel; the per-shell filter fits on the first 120, its gains taken from the up channel alone and applied to both; the nearest-run copy searches all 261 training runs by plain L2 distance over the member's own coarse representation (the two log-compressed spin densities at 40³, the reference density fixed from the ridge's own first-80 sample) and copies that run's localization fields verbatim. Every floor is scored per run on both spin channels, medians aggregated to the exchangeable split unit first, and broken out by campaign beside its pooled row, since a positional floor reads very differently on near-identical strains than on scattered defects.

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

Every level is absolute mean absolute error; a lower number is stricter. The first two are the canon's own bars (test-suite.md section 2's pattern rule and this entry's own IMPLEMENTATION.md kill), neither invented here. The rest are added before training, because the semilocal ridge turned out weaker than a purely positional floor on this block — the same mechanism as the Poisson climatology in stage0-report.md: a template beats a coordinate-blind fit on near-identical geometries, so the canon's own kill is, on this block, a weaker bar than the trivial template added here for scale.

1. **canon kill** (I.1, half the semilocal ridge): 0.048809
2. **canon pattern rule** (at least 20% better than the ridge or the task is left): 0.078094
3. **added, beat the training-mean template** (a member above this line has learned nothing beyond a positional average): 0.015957
4. **added, beat the nearest-run copy** (the memorization null this suite requires of every task): 0.006164
5. **added, the stretch level** (half the template's error — the level at which the member resolves the run-to-run variation, per-voxel spread 0.021, rather than reproducing the average): 0.007978

**Measured out of order**: level 4 (beat the nearest-run copy) is *stricter* than level 5 (the stretch level) on this block — the nearest training run is close enough, on both campaigns, that copying it verbatim beats even half the template's error. The memorization null was not expected to be harder than the stretch goal designed to demand genuine operator behavior; on this block it is, so passing level 5 without also passing level 4 is not possible here, and level 4 is the real hard bar to read as the stretch goal.

## The deep-equilibrium ladder (canon I.3), pre-registered before any rung is trained

Three configurations of the same factory (`operators.factorized_fourier.Factorized_Fourier_Network`, `configuration="explicit" | "weight_tied" | "fixed_point"`), differing only in composition and one design choice the weight-tied and fixed-point rungs share: their one applied-repeatedly layer carries no residual, unlike the explicit stack's twelve. A residual here would make repeated or iterated application drift rather than contract, since the fixed point would then need the correction term itself to vanish rather than the whole map to settle.

```
explicit (same width, 12 layers):       11552194 parameters
weight_tied (depth 12, one shared layer):     963330 parameters (11.99x fewer than the same-width explicit stack)
fixed_point (one shared layer):            963330 parameters (identical to weight_tied, same one layer)
explicit, matched params (1 layer):       963330 parameters (exact match to the tied block, not merely approximate: one explicit layer at this width has precisely the shared layer's own count)
```

**Stability escalation.** The primitive (`operators.compositions.fixed_point.FixedPoint`) implements damping and Anderson acceleration (history depth, regularization, a condition-number ceiling that declines a near-parallel history) and three backward rules (phantom at a chosen depth, jacobian-free as phantom depth one, and the exact implicit adjoint). It does **not** implement per-mode spectral clipping, a Hutchinson Jacobian penalty, or a monotone parametrization -- the canon's own further escalation. These are not built here, speculatively, against a convergence failure that has not happened: the toy audit below converges cleanly with damping and Anderson acceleration alone. If a real 80³ run fails to converge, that is the order to reach for them in.

**The mandatory 8³ gradient audit** ran on this member's own separable layer (width 2, one kept mode, nonzero local bias so the origin is not the map's only fixed point), not a generic one, in `Test_The_Mandatory_Gradient_Audit_On_This_Members_Own_Layer`: phantom depth 1, phantom depth 3, the exact implicit adjoint, central finite differences and the depth-matched full unroll all agree -- implicit within the finite-difference-versus-unroll disagreement itself, phantom depth 3 within an order of magnitude of that same disagreement. The convergence and health-metric tests (`Test_Fixed_Point_Inspect_Exposes_The_Health_Signals_After_A_Member_Call`, `Test_The_Health_Metric_Is_A_Fraction_Of_Inputs_Converged_Read_Off_Inspect`) confirm the health floor is readable off `Inspect()` after an ordinary member call, since the lifted forward path calls `Resolved` directly and the member records the solve itself -- `FixedPoint.Forward` alone never does.

### the two bars (test-suite.md, I.3), neither invented here

- **kill**: the explicit comparator, at *both* matchings above, beats fixed-point at matched seeds (3) and wall-clock (fixed-point is not judged the winner unless it is also at least 3x faster to train); the health floor kills below 80% of validation samples converging to 1e-3 within 32 iterations after tuning, and stands as a caution rather than a pass below 90%.
- **the honest deliverable is the decomposition curve** explicit → weight-tied → FNO-DEQ. "Weight-tying yes, DEQ no" -- the middle rung matching the explicit comparator while the fixed-point rung does not clear the wall-clock bar -- is a legitimate verdict and will be reported as such if that is what the runs show.

Every trained number below is the integrator's to schedule and this stream's to report once run: steps, wall-clock seconds, peak memory, the convergence rate (fraction of the evaluation block converging to 1e-3 within 32 iterations), and the seed -- for the explicit same-width comparator, the explicit matched-params comparator, weight-tied, and fixed-point, three seeds each.

```
rung                       | steps | wall_clock_s | peak_memory_MiB | convergence_rate | seed
explicit (same width)      |   --  |     --       |       --        |  n/a (not iterative)  |  --
explicit (matched params)  |   --  |     --       |       --        |  n/a (not iterative)  |  --
weight_tied                |   --  |     --       |       --        |  n/a (not iterative)  |  --
fixed_point                |   --  |     --       |       --        |          --           |  --
```

## The potential task (`charge_to_potential`), host-only work

**Truncation ceiling.** The target lives on the fine grid (80³), unlike the localization field's 40³, so truncate-early no longer matches the target as built for I.1. Measured on the evaluation block: each spin potential truncated to 40³ and zero-padded back to 80³, against its own untouched fine-grid original, mean-removed relative L2: median **2.13%**. This is the fraction of the potential a coarse trunk cannot carry by construction, before any model is judged.

This is at or above 1%: per the pre-registered rule, this stream stops here on the potential member and asks the integrator before building the fine-grid trunk, which is the canon's own 9 GB super-later ablation and not built as a default response to a failed ceiling check.

**Floors**, all three card metrics, per spin, unit-aggregated and broken out by campaign, following stage zero's recipes (`Poisson_Lines`, `Shell_Filter_Lines`) but on the full cubic block rather than the defect campaign alone, and per spin rather than on the spin-mean potential:

```
group                                               metric                            units  runs  median     interquartile  mean_interval         
hartree_only                                        mean_removed_relative_l2          29     152   1.541687   0.122568       [1.559398, 1.682830]  
hartree_only__defect_set                            mean_removed_relative_l2          21     84    1.589188   0.109431       [1.579744, 1.731626]  
hartree_only__supercell_strains                     mean_removed_relative_l2          8      68    1.516123   0.003739       [1.514971, 1.519291]  
hartree_only                                        mean_removed_mean_absolute_error  29     152   20.962231  0.848175       [21.106632, 22.343441]
hartree_only__defect_set                            mean_removed_mean_absolute_error  21     84    21.245708  1.013059       [21.230667, 22.882708]
hartree_only__supercell_strains                     mean_removed_mean_absolute_error  8      68    20.909806  0.124986       [20.718859, 20.926957]
hartree_only                                        mean_discrepancy                  29     152   12.055770  0.150489       [12.138172, 12.477054]
hartree_only__defect_set                            mean_discrepancy                  21     84    12.027126  0.145562       [12.000498, 12.061120]
hartree_only__supercell_strains                     mean_discrepancy                  8      68    13.200200  0.147737       [12.701920, 13.200465]
climatology_only                                    mean_removed_relative_l2          29     152   0.603281   0.051339       [0.593823, 0.644483]  
climatology_only__defect_set                        mean_removed_relative_l2          21     84    0.614358   0.038128       [0.611299, 0.671906]  
climatology_only__supercell_strains                 mean_removed_relative_l2          8      68    0.557831   0.006772       [0.555618, 0.574117]  
climatology_only                                    mean_removed_mean_absolute_error  29     152   8.596947   0.450681       [8.404736, 8.882341]  
climatology_only__defect_set                        mean_removed_mean_absolute_error  21     84    8.650301   0.251252       [8.598793, 9.152762]  
climatology_only__supercell_strains                 mean_removed_mean_absolute_error  8      68    8.012737   0.107785       [7.994488, 8.188530]  
climatology_only                                    mean_discrepancy                  29     152   12.055770  0.150489       [12.138172, 12.477054]
climatology_only__defect_set                        mean_discrepancy                  21     84    12.027126  0.145562       [12.000498, 12.061120]
climatology_only__supercell_strains                 mean_discrepancy                  8      68    13.200200  0.147737       [12.701920, 13.200465]
hartree_plus_climatology                            mean_removed_relative_l2          29     152   0.403326   0.439054       [0.375792, 0.650875]  
hartree_plus_climatology__defect_set                mean_removed_relative_l2          21     84    0.602769   0.406414       [0.478322, 0.803711]  
hartree_plus_climatology__supercell_strains         mean_removed_relative_l2          8      68    0.166285   0.008935       [0.164780, 0.179722]  
hartree_plus_climatology                            mean_removed_mean_absolute_error  29     152   3.934809   4.365773       [3.529815, 6.626013]  
hartree_plus_climatology__defect_set                mean_removed_mean_absolute_error  21     84    5.519786   3.185378       [4.514307, 8.255244]  
hartree_plus_climatology__supercell_strains         mean_removed_mean_absolute_error  8      68    1.478298   0.183963       [1.469124, 1.837148]  
hartree_plus_climatology                            mean_discrepancy                  29     152   12.055770  0.150489       [12.138172, 12.477054]
hartree_plus_climatology__defect_set                mean_discrepancy                  21     84    12.027126  0.145562       [12.000498, 12.061120]
hartree_plus_climatology__supercell_strains         mean_discrepancy                  8      68    13.200200  0.147737       [12.701920, 13.200465]
hartree_plus_semilocal_xc_ridge                     mean_removed_relative_l2          29     152   0.479646   0.237299       [0.459739, 0.669886]  
hartree_plus_semilocal_xc_ridge__defect_set         mean_removed_relative_l2          21     84    0.551568   0.140164       [0.515281, 0.763812]  
hartree_plus_semilocal_xc_ridge__supercell_strains  mean_removed_relative_l2          8      68    0.340906   0.001347       [0.340598, 0.347192]  
hartree_plus_semilocal_xc_ridge                     mean_removed_mean_absolute_error  29     152   5.455839   3.160442       [4.985915, 7.090915]  
hartree_plus_semilocal_xc_ridge__defect_set         mean_removed_mean_absolute_error  21     84    6.270380   2.002854       [5.692576, 8.259497]  
hartree_plus_semilocal_xc_ridge__supercell_strains  mean_removed_mean_absolute_error  8      68    3.548233   0.033961       [3.536147, 3.566967]  
hartree_plus_semilocal_xc_ridge                     mean_discrepancy                  29     152   12.167168  0.846892       [11.989958, 12.662590]
hartree_plus_semilocal_xc_ridge__defect_set         mean_discrepancy                  21     84    11.959188  0.806135       [11.619695, 12.125577]
hartree_plus_semilocal_xc_ridge__supercell_strains  mean_discrepancy                  8      68    13.383056  0.213636       [12.961424, 14.004092]
per_shell_linear_filter                             mean_removed_relative_l2          29     152   0.282422   0.112483       [0.252105, 0.355947]  
per_shell_linear_filter__defect_set                 mean_removed_relative_l2          21     84    0.296799   0.036377       [0.285400, 0.402708]  
per_shell_linear_filter__supercell_strains          mean_removed_relative_l2          8      68    0.191685   0.006597       [0.189326, 0.195902]  
per_shell_linear_filter                             mean_removed_mean_absolute_error  29     152   3.114532   0.804173       [2.988789, 4.045506]  
per_shell_linear_filter__defect_set                 mean_removed_mean_absolute_error  21     84    3.217335   0.684972       [3.244996, 4.491904]  
per_shell_linear_filter__supercell_strains          mean_removed_mean_absolute_error  8      68    2.520987   0.042438       [2.503691, 2.552112]  
per_shell_linear_filter                             mean_discrepancy                  29     152   12.055770  0.150489       [12.138172, 12.477054]
per_shell_linear_filter__defect_set                 mean_discrepancy                  21     84    12.027126  0.145562       [12.000498, 12.061120]
per_shell_linear_filter__supercell_strains          mean_discrepancy                  8      68    13.200200  0.147737       [12.701920, 13.200465]
training_mean_trivial_floor                         mean_removed_relative_l2          29     152   0.184317   0.158693       [0.152402, 0.233859]  
training_mean_trivial_floor__defect_set             mean_removed_relative_l2          21     84    0.199155   0.096206       [0.188115, 0.281508]  
training_mean_trivial_floor__supercell_strains      mean_removed_relative_l2          8      68    0.082671   0.008912       [0.081453, 0.091005]  
training_mean_trivial_floor                         mean_removed_mean_absolute_error  29     152   1.208247   0.849732       [1.091597, 1.763224]  
training_mean_trivial_floor__defect_set             mean_removed_mean_absolute_error  21     84    1.352306   0.621236       [1.254015, 2.108058]  
training_mean_trivial_floor__supercell_strains      mean_removed_mean_absolute_error  8      68    0.706755   0.125754       [0.679229, 0.848718]  
training_mean_trivial_floor                         mean_discrepancy                  29     152   12.055770  0.150489       [12.138172, 12.477054]
training_mean_trivial_floor__defect_set             mean_discrepancy                  21     84    12.027126  0.145562       [12.000498, 12.061120]
training_mean_trivial_floor__supercell_strains      mean_discrepancy                  8      68    13.200200  0.147737       [12.701920, 13.200465]
nearest_run_copy_floor                              mean_removed_relative_l2          29     152   0.075957   0.097941       [0.069485, 0.158503]  
nearest_run_copy_floor__defect_set                  mean_removed_relative_l2          21     84    0.105153   0.113429       [0.097321, 0.206297]  
nearest_run_copy_floor__supercell_strains           mean_removed_relative_l2          8      68    0.008943   0.012088       [0.005966, 0.023495]  
nearest_run_copy_floor                              mean_removed_mean_absolute_error  29     152   0.547114   0.831777       [0.485598, 1.199093]  
nearest_run_copy_floor__defect_set                  mean_removed_mean_absolute_error  21     84    0.637324   0.661405       [0.650334, 1.558522]  
nearest_run_copy_floor__supercell_strains           mean_removed_mean_absolute_error  8      68    0.096049   0.113399       [0.065197, 0.272698]  
nearest_run_copy_floor                              mean_discrepancy                  29     152   -0.004265  1.117168       [-0.470906, 0.053722] 
nearest_run_copy_floor__defect_set                  mean_discrepancy                  21     84    -0.004265  1.238290       [-0.564796, 0.132724] 
nearest_run_copy_floor__supercell_strains           mean_discrepancy                  8      68    -0.024846  0.051190       [-0.474399, -0.006653]
```

### sanity check against stage zero's own committed numbers

Stage zero (defect campaign only, spin-mean potential): Hartree + climatology 57.26%, Hartree + semilocal-XC ridge 56.20%. Recomputed here (defect campaign only, but per spin rather than spin-mean): Hartree + climatology 60.28%, Hartree + semilocal-XC ridge 55.16%. The difference is the per-spin-versus-spin-mean gap: a spin-mean potential already averages away the part of the exchange-correlation remainder that differs between the two spins, which a per-spin score cannot, so the two numbers are expected to differ by roughly that averaged-away spread rather than agree exactly.

### the ladder for this task, neither bar invented here

- **canon bar**: more than 2x better than the Hartree + semilocal-XC ridge floor (median 47.96% mean-removed relative L2) -- required absolute: **23.98%** -- or record that the physics floor suffices and keep this task as a pipeline unit test, a finding rather than a failure.
- **added, as for ELF**: beat the training-mean template; beat the nearest-run copy.
- **the per-shell linear filter is the linearity certificate, not a kill**: stage zero read 23.35% on the spin mean over cubic fold zero, 2.4x better than the physics floor; this recomputation's per-spin filter row (above) tests that same hypothesis on this block.
- **the DEQ cross-entry bar**: fixed-point's error on this task within 1.5x of I.1's own error on the same split.


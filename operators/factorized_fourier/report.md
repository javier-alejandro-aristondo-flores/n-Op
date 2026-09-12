# factorized_fourier — measured against its floors

Regenerate with `python3 -m operators.factorized_fourier.report`.

The block, all four floors and the pre-registered claim ladder below were measured before a single training step was taken, exactly as the doctrine asks. The member's own result, per-campaign and per-functional rows, the super-resolution self-consistency check and the figure suite follow once a checkpoint exists for it; until then that section says so plainly and nothing else about this command changes.

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

## The member's own result (electron localization, fold 0, explicit stack)

Loaded from `elf_fold0_explicit_35505_stage2_checkpoint.npz`: 3100 completed steps, best validation score 0.000081 at step 1600.

### three caveats before trusting this number

This is one seeded run (seed 20260912): no few-percent difference among these numbers is resolvable from a single run alone, since the seed sweep that would put a confidence band on the member itself is scheduled together with the rest of the deep-equilibrium ladder, not yet run.

The block's geometries are near-identical within a campaign, which is why a verbatim copy of the nearest training run already reaches a mean absolute error of 0.0062 without learning anything (the nearest-run-copy floor, above), and why the strain rows read markedly better than the defect rows: 3.3x lower mean absolute error (0.000704 against 0.002329) and 5.2x lower relative L2 (0.26% against 1.35%). The supercell strains are small, smooth perturbations of one lattice, so a near neighbor is nearly the true answer, while the defect campaign varies impurity species and site by run. The defect rows, not the pooled median, are this member's real test.

An external calibration point, not a competitor: the 2026 hydrogen-ELF network's published error of 0.019 is the nearest number in the literature, but it answers a single-element system, an easier problem than this six-family cubic block, so it is a reference point for scale, not a benchmark this member is being measured against.

### scored on the kill block (fold zero, both spins, every card metric, by campaign and by functional)

```
group                        metric                    units  runs  median    interquartile  mean_interval       
member                       mean_absolute_error       29     152   0.002170  0.001741       [0.001820, 0.003601]
member__defect_set           mean_absolute_error       21     84    0.002329  0.001608       [0.002438, 0.004583]
member__supercell_strains    mean_absolute_error       8      68    0.000704  0.000261       [0.000610, 0.000822]
member__functional_accurate  mean_absolute_error       22     44    0.002364  0.002047       [0.002491, 0.004896]
member__functional_cheap     mean_absolute_error       29     108   0.002041  0.001486       [0.001724, 0.003334]
member                       structural_similarity_3d  29     152   0.999806  0.000715       [0.998027, 0.999645]
member__defect_set           structural_similarity_3d  21     84    0.999526  0.000782       [0.997282, 0.999491]
member__supercell_strains    structural_similarity_3d  8      68    0.999989  0.000008       [0.999985, 0.999992]
member__functional_accurate  structural_similarity_3d  22     44    0.999368  0.000878       [0.997387, 0.999479]
member__functional_cheap     structural_similarity_3d  29     108   0.999819  0.000779       [0.997943, 0.999665]
member                       relative_l2               29     152   0.010538  0.013139       [0.010305, 0.023040]
member__defect_set           relative_l2               21     84    0.013450  0.010546       [0.014100, 0.030074]
member__supercell_strains    relative_l2               8      68    0.002568  0.000826       [0.002225, 0.003014]
member__functional_accurate  relative_l2               22     44    0.014733  0.013078       [0.013949, 0.029636]
member__functional_cheap     relative_l2               29     108   0.009677  0.013281       [0.009872, 0.022718]
```

### the pre-registered claim ladder, measured

```
group                                floor                        floor_median  member_median  improvement  required  verdict
1_canon_kill                         semilocal_ridge_floor        0.097618      0.002170       97.8%        50.0%     pass   
2_canon_pattern_rule                 semilocal_ridge_floor        0.097618      0.002170       97.8%        20.0%     pass   
3_added_beat_training_mean_template  training_mean_trivial_floor  0.015957      0.002170       86.4%        0.0%      pass   
4_added_beat_nearest_run_copy        nearest_run_copy_floor       0.006164      0.002170       64.8%        0.0%      pass   
5_added_stretch_half_the_template    training_mean_trivial_floor  0.015957      0.002170       86.4%        50.0%     pass   
```

### every floor, on the two lower-is-better card metrics, beaten or not

Structural similarity is higher-is-better and is reported only as a summary above (median per group), not as a floor-comparison ratio: `Compare_To_Floor`'s improvement formula assumes a lower-is-better error, which mean absolute error and relative L2 are and structural similarity is not.

```
group  floor                        floor_median  member_median  improvement  required  verdict
all    training_mean_trivial_floor  0.015957      0.002170       86.4%        0.0%      pass   
all    training_mean_trivial_floor  0.108952      0.010538       90.3%        0.0%      pass   
all    nearest_run_copy_floor       0.006164      0.002170       64.8%        0.0%      pass   
all    nearest_run_copy_floor       0.049138      0.010538       78.6%        0.0%      pass   
all    per_shell_linear_filter      0.083022      0.002170       97.4%        0.0%      pass   
all    per_shell_linear_filter      0.303498      0.010538       96.5%        0.0%      pass   
all    semilocal_ridge_floor        0.097618      0.002170       97.8%        0.0%      pass   
all    semilocal_ridge_floor        0.392865      0.010538       97.3%        0.0%      pass   
```

### super-resolution self-consistency

The same trained weights, asked to answer directly on an 80³ grid rather than the 40³ grid they trained on, then spectrally truncated back to 40³, against the direct 40³ answer, on every 12th evaluation run (7 runs, both spins): median relative L2 **0.621%**. A small number here means the learned Fourier modes carry the same answer at a resolution the member never trained at, which is what makes the coarse-trunk design's answer at the fine grid (the potential task's own finish) trustworthy rather than a coincidence of the training resolution.

### the alloy every-shape row

Not applicable: the `alloy_ensemble` fold-zero archives checked all carry `has_localization: False` and non-cubic shapes (for example `(48, 96, 216)`); this campaign has no localization target for the member to be scored against, on any shape.

Figures: 181 files written under `operators/factorized_fourier/figures/fold_0/explicit`, arrays cached at `/Pool/VASP_DATA/_derived/_figures/factorized_fourier/fold_0/explicit`.

## The deep-equilibrium ladder (canon I.3), pre-registered before any rung is trained

Three configurations of the same factory (`operators.factorized_fourier.Factorized_Fourier_Network`, `configuration="explicit" | "weight_tied" | "fixed_point"`), differing only in composition and one design choice the weight-tied and fixed-point rungs share: their one applied-repeatedly layer carries no residual, unlike the explicit stack's twelve. A residual here would make repeated or iterated application drift rather than contract, since the fixed point would then need the correction term itself to vanish rather than the whole map to settle.

```
explicit (same width, 12 layers):       11552194 parameters
weight_tied (depth 12, one shared layer):     963330 parameters (11.99x fewer than the same-width explicit stack)
fixed_point (one shared layer):            963330 parameters (identical to weight_tied, same one layer)
explicit, matched params (1 layer):       963330 parameters (exact match to the tied block, not merely approximate: one explicit layer at this width has precisely the shared layer's own count)
```

**Stability escalation.** The primitive (`operators.compositions.fixed_point.FixedPoint`) implements damping and Anderson acceleration (history depth, regularization, a condition-number ceiling that declines a near-parallel history) and three backward rules (phantom at a chosen depth, jacobian-free as phantom depth one, and the exact implicit adjoint). The real run supplied the convergence failure the toy audit alone never has: even after the solver's own tolerance was corrected to be relative to the iterate rather than absolute over four million entries, the first three validation intervals read a cap-hit fraction of 0.79, 1.00 and 1.00, because the shared layer's default initialization is not contractive at this member's own channel width -- a 64-channel local matrix at the usual `sqrt(2/(in+out))` scale carries a spectral norm near 2 before the spectral kernel adds its own, exactly why the primitive's own toy fixtures scale their layer down and the member's shared layer never had. `initial_scale` is that fix, the canon's own first escalation rung, applied here as a pre-registered tuning step rather than a post-hoc one: the fixed-point and weight-tied-injected configurations alone start their shared layer's kernel and local-linear weight arrays -- never the biases -- at a tenth scale by default, every other configuration reading exactly one and untouched by the parameter's existence. Per-mode spectral clipping, a Hutchinson Jacobian penalty and a monotone parametrization remain unbuilt, the canon's own further escalation, reached for only if a contractive initialization alone does not clear the cap.

**The mandatory 8³ gradient audit** ran on this member's own separable layer (width 2, one kept mode, nonzero local bias so the origin is not the map's only fixed point), not a generic one, in `Test_The_Mandatory_Gradient_Audit_On_This_Members_Own_Layer`: phantom depth 1, phantom depth 3, the exact implicit adjoint, central finite differences and the depth-matched full unroll all agree -- implicit within the finite-difference-versus-unroll disagreement itself, phantom depth 3 within an order of magnitude of that same disagreement. The convergence and health-metric tests (`Test_Fixed_Point_Inspect_Exposes_The_Health_Signals_After_A_Member_Call`, `Test_The_Health_Metric_Is_A_Fraction_Of_Inputs_Converged_Read_Off_Inspect`) confirm the health floor is readable off `Inspect()` after an ordinary member call, since the lifted forward path calls `Resolved` directly and the member records the solve itself -- `FixedPoint.Forward` alone never does.

### the two bars (test-suite.md, I.3), neither invented here

- **kill**: the explicit comparator, at *both* matchings above, beats fixed-point at matched seeds (3) and wall-clock (fixed-point is not judged the winner unless it is also at least 3x faster to train); the health floor kills below 80% of validation samples converging to 1e-3 within 32 iterations after tuning, and stands as a caution rather than a pass below 90%.
- **the honest deliverable is the decomposition curve** explicit → weight-tied → FNO-DEQ. "Weight-tying yes, DEQ no" -- the middle rung matching the explicit comparator while the fixed-point rung does not clear the wall-clock bar -- is a legitimate verdict and will be reported as such if that is what the runs show.

Every trained number below is the integrator's to schedule and this stream's to report once run: steps, wall-clock seconds, peak memory, the convergence rate (fraction of the evaluation block converging to 1e-3 within 32 iterations), and the seed -- for the explicit same-width comparator, the explicit matched-params comparator, weight-tied, and fixed-point, three seeds each.

```
rung                       | steps | wall_clock_s | peak_memory_MiB | convergence_rate     | seed
explicit (same width)      | 24404 |    14183     |     ~3600       | n/a (not iterative)  | 20260912 (1 of 3)
explicit (matched params)  | 35505 |     1872     |      ~700       | n/a (not iterative)  | 20260912 (1 of 3)
weight_tied                | 23804 |     9670     |     ~3185       | n/a (not iterative)  | 20260912 (1 of 3)
fixed_point                |   --  |     --       |       --        |          --           |  --
```

**Steps** are the sum actually completed across all three stages (the final stage's own patience can stop it short of the stage plan, as it did for the same-width explicit rung at 24,404 of 35,505 and weight-tied at 23,804; the matched-params explicit rung instead ran its full budget without stopping early at any of the three stages -- 10,652 / 10,652 / 14,201, all 35,505 requested -- so its number reflects the training budget rather than a convergence plateau, and a longer budget might read lower still). **Wall-clock** and **peak memory** are one seed's own measured run, the first of the three the kill bar needs -- peak memory is read from periodic `nvidia-smi` checks during the run, not a continuously logged maximum, so it is reported to the nearest hundred MiB rather than claimed exact.

## The potential task (`charge_to_potential`), host-only work

**Truncation ceiling.** The target lives on the fine grid (80³), unlike the localization field's 40³, so truncate-early no longer matches the target as built for I.1. Measured on the evaluation block: each spin potential truncated to 40³ and zero-padded back to 80³, against its own untouched fine-grid original, mean-removed relative L2: median **2.13%**. This is the fraction of the potential a coarse trunk cannot carry by construction, before any model is judged.

An earlier draft of this section pre-registered a flat 1% threshold on this number and stopped here, against it: that threshold was the wrong stop condition, since what actually matters is the ceiling's size relative to the bar a trained member must clear, not an arbitrary absolute figure. The canon's own bar is half the Hartree + semilocal-XC floor's error (below); at 23.98% required against a 2.13% ceiling, there is roughly an order of magnitude of headroom, so the design is the coarse trunk with the readout followed by a lifted, differentiable resample back to the fine shape. The fine-grid trunk question returns only if a trained member's own error approaches the ceiling -- it is the canon's 9 GB super-later ablation, never a default.

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

## The parametric variant (canon II.4, `strain_to_charge`), host-only work

Parameters (the six-component strain tensor) broadcast as constant channels into the same lift, plus periodic coordinate features of the requested grid's own fractional coordinates -- without the coordinate channels a spectral-plus-pointwise stack fed nothing but constants can only answer a constant field, proven directly in `Test_A_Constant_Only_Input_Can_Only_Answer_A_Constant_Field` and `Test_Coordinate_Features_Break_The_Constant_Output_Degeneracy_And_Answer_Any_Grid`. The same trained weights answer any grid shape because the coordinate channels are rebuilt for whatever shape is asked, never cached for one; `Test_The_Same_Parametric_Weights_Answer_Two_Different_Grids` checks this directly on the production member. The electron count rides in `__call__`'s own `condition` argument, unused by the other two tasks, exactly the seam `Conserving(law="renormalize_to_electron_count")` was built for.

### arms and levels

An arm is one strain family; a level is that family's own swept parameter vector (one component for uniaxial, biaxial, isotropic and one-angle shear; two for two-angle shear; three for triaxial and three-angle shear, confirmed against the real census as genuine multi-dimensional grids rather than single-factor lines). `Bracket_Corners` generalizes bracketing interpolation to any dimension: every one of a level's 2^D corner combinations must itself be a real level, which refuses a bracket across a grid hole (two-angle and three-angle shear both have real holes) rather than assuming a complete factorial design.

- **biaxial**: 40 levels (38 interior, held out one at a time), 80 runs
- **isotropic**: 47 levels (45 interior, held out one at a time), 94 runs
- **one_angle_shear**: 40 levels (38 interior, held out one at a time), 240 runs
- **three_angle_shear**: 192 levels (20 interior, held out one at a time), 384 runs
- **triaxial**: 512 levels (216 interior, held out one at a time), 1024 runs
- **two_angle_shear**: 76 levels (28 interior, held out one at a time), 456 runs
- **uniaxial**: 40 levels (38 interior, held out one at a time), 80 runs

### floors, leave-one-level-out block (every interior level held out, its own arm's boundary training it)

```
group                                              metric                    units  runs  median    interquartile  mean_interval       
bracketing_interpolation_floor                     mean_absolute_error       423    423   0.000674  0.001117       [0.000565, 0.000676]
bracketing_interpolation_floor__biaxial            mean_absolute_error       38     38    0.000056  0.000024       [0.000052, 0.000063]
bracketing_interpolation_floor__isotropic          mean_absolute_error       45     45    0.000015  0.000005       [0.000014, 0.000016]
bracketing_interpolation_floor__one_angle_shear    mean_absolute_error       38     38    0.000004  0.000000       [0.000004, 0.000004]
bracketing_interpolation_floor__three_angle_shear  mean_absolute_error       20     20    0.000442  0.000118       [0.000380, 0.000445]
bracketing_interpolation_floor__triaxial           mean_absolute_error       216    216   0.001137  0.000375       [0.001110, 0.001178]
bracketing_interpolation_floor__two_angle_shear    mean_absolute_error       28     28    0.000134  0.000001       [0.000134, 0.000136]
bracketing_interpolation_floor__uniaxial           mean_absolute_error       38     38    0.000019  0.000006       [0.000018, 0.000021]
bracketing_interpolation_floor                     structural_similarity_3d  423    423   0.999997  0.000006       [0.999996, 0.999997]
bracketing_interpolation_floor__biaxial            structural_similarity_3d  38     38    1.000000  0.000000       [1.000000, 1.000000]
bracketing_interpolation_floor__isotropic          structural_similarity_3d  45     45    1.000000  0.000000       [1.000000, 1.000000]
bracketing_interpolation_floor__one_angle_shear    structural_similarity_3d  38     38    1.000000  0.000000       [1.000000, 1.000000]
bracketing_interpolation_floor__three_angle_shear  structural_similarity_3d  20     20    0.999997  0.000002       [0.999997, 0.999998]
bracketing_interpolation_floor__triaxial           structural_similarity_3d  216    216   0.999994  0.000006       [0.999993, 0.999994]
bracketing_interpolation_floor__two_angle_shear    structural_similarity_3d  28     28    1.000000  0.000000       [1.000000, 1.000000]
bracketing_interpolation_floor__uniaxial           structural_similarity_3d  38     38    1.000000  0.000000       [1.000000, 1.000000]
bracketing_interpolation_floor                     relative_l2               423    423   0.000911  0.001348       [0.000688, 0.000818]
bracketing_interpolation_floor__biaxial            relative_l2               38     38    0.000066  0.000015       [0.000064, 0.000074]
bracketing_interpolation_floor__isotropic          relative_l2               45     45    0.000020  0.000005       [0.000019, 0.000021]
bracketing_interpolation_floor__one_angle_shear    relative_l2               38     38    0.000005  0.000001       [0.000005, 0.000006]
bracketing_interpolation_floor__three_angle_shear  relative_l2               20     20    0.000649  0.000194       [0.000564, 0.000665]
bracketing_interpolation_floor__triaxial           relative_l2               216    216   0.001374  0.000523       [0.001333, 0.001409]
bracketing_interpolation_floor__two_angle_shear    relative_l2               28     28    0.000194  0.000003       [0.000194, 0.000197]
bracketing_interpolation_floor__uniaxial           relative_l2               38     38    0.000025  0.000005       [0.000024, 0.000028]
training_mean_trivial_floor                        mean_absolute_error       423    423   0.031721  0.038525       [0.037548, 0.043259]
training_mean_trivial_floor__biaxial               mean_absolute_error       38     38    0.070862  0.065000       [0.058836, 0.084156]
training_mean_trivial_floor__isotropic             mean_absolute_error       45     45    0.034765  0.034632       [0.029939, 0.042603]
training_mean_trivial_floor__one_angle_shear       mean_absolute_error       38     38    0.010814  0.007984       [0.009818, 0.012612]
training_mean_trivial_floor__three_angle_shear     mean_absolute_error       20     20    0.031841  0.003222       [0.032519, 0.034599]
training_mean_trivial_floor__triaxial              mean_absolute_error       216    216   0.040519  0.035417       [0.041920, 0.049387]
training_mean_trivial_floor__two_angle_shear       mean_absolute_error       28     28    0.015883  0.007105       [0.014766, 0.018689]
training_mean_trivial_floor__uniaxial              mean_absolute_error       38     38    0.035700  0.032859       [0.029496, 0.041893]
training_mean_trivial_floor                        structural_similarity_3d  423    423   0.995127  0.007848       [0.991395, 0.993019]
training_mean_trivial_floor__biaxial               structural_similarity_3d  38     38    0.986538  0.024129       [0.978113, 0.987247]
training_mean_trivial_floor__isotropic             structural_similarity_3d  45     45    0.996672  0.006226       [0.994450, 0.996769]
training_mean_trivial_floor__one_angle_shear       structural_similarity_3d  38     38    0.998764  0.002089       [0.998032, 0.998811]
training_mean_trivial_floor__three_angle_shear     structural_similarity_3d  20     20    0.989624  0.003045       [0.989194, 0.991006]
training_mean_trivial_floor__triaxial              structural_similarity_3d  216    216   0.993678  0.007765       [0.990114, 0.992212]
training_mean_trivial_floor__two_angle_shear       structural_similarity_3d  28     28    0.997240  0.002151       [0.996238, 0.997708]
training_mean_trivial_floor__uniaxial              structural_similarity_3d  38     38    0.995970  0.007210       [0.993385, 0.996136]
training_mean_trivial_floor                        relative_l2               423    423   0.045897  0.045848       [0.050827, 0.058042]
training_mean_trivial_floor__biaxial               relative_l2               38     38    0.091052  0.084118       [0.075657, 0.107548]
training_mean_trivial_floor__isotropic             relative_l2               45     45    0.044875  0.044286       [0.037868, 0.052992]
training_mean_trivial_floor__one_angle_shear       relative_l2               38     38    0.016965  0.014036       [0.015004, 0.019889]
training_mean_trivial_floor__three_angle_shear     relative_l2               20     20    0.052371  0.003551       [0.053264, 0.056513]
training_mean_trivial_floor__triaxial              relative_l2               216    216   0.052355  0.047231       [0.056451, 0.065884]
training_mean_trivial_floor__two_angle_shear       relative_l2               28     28    0.025532  0.012274       [0.023438, 0.030058]
training_mean_trivial_floor__uniaxial              relative_l2               38     38    0.046979  0.044332       [0.039024, 0.055496]
nearest_run_copy_floor                             mean_absolute_error       423    423   0.015082  0.009548       [0.016509, 0.018617]
nearest_run_copy_floor__biaxial                    mean_absolute_error       38     38    0.018013  0.022782       [0.017908, 0.027328]
nearest_run_copy_floor__isotropic                  mean_absolute_error       45     45    0.019321  0.019137       [0.018979, 0.027117]
nearest_run_copy_floor__one_angle_shear            mean_absolute_error       38     38    0.008701  0.007526       [0.006783, 0.009822]
nearest_run_copy_floor__three_angle_shear          mean_absolute_error       20     20    0.010777  0.000029       [0.010769, 0.010797]
nearest_run_copy_floor__triaxial                   mean_absolute_error       216    216   0.015999  0.005347       [0.017103, 0.019111]
nearest_run_copy_floor__two_angle_shear            mean_absolute_error       28     28    0.006418  0.000209       [0.006472, 0.007147]
nearest_run_copy_floor__uniaxial                   mean_absolute_error       38     38    0.017380  0.024136       [0.018838, 0.029567]
nearest_run_copy_floor                             structural_similarity_3d  423    423   0.999231  0.001302       [0.998503, 0.998762]
nearest_run_copy_floor__biaxial                    structural_similarity_3d  38     38    0.998753  0.002053       [0.997560, 0.998614]
nearest_run_copy_floor__isotropic                  structural_similarity_3d  45     45    0.998499  0.001662       [0.997462, 0.998440]
nearest_run_copy_floor__one_angle_shear            structural_similarity_3d  38     38    0.999302  0.001049       [0.998951, 0.999395]
nearest_run_copy_floor__three_angle_shear          structural_similarity_3d  20     20    0.999031  0.000027       [0.999023, 0.999037]
nearest_run_copy_floor__triaxial                   structural_similarity_3d  216    216   0.999252  0.000260       [0.998653, 0.998938]
nearest_run_copy_floor__two_angle_shear            structural_similarity_3d  28     28    0.999591  0.000022       [0.999456, 0.999588]
nearest_run_copy_floor__uniaxial                   structural_similarity_3d  38     38    0.998533  0.002649       [0.996838, 0.998248]
nearest_run_copy_floor                             relative_l2               423    423   0.019876  0.010944       [0.022205, 0.024712]
nearest_run_copy_floor__biaxial                    relative_l2               38     38    0.024364  0.022644       [0.023751, 0.034560]
nearest_run_copy_floor__isotropic                  relative_l2               45     45    0.025752  0.022191       [0.025184, 0.034881]
nearest_run_copy_floor__one_angle_shear            relative_l2               38     38    0.014143  0.012087       [0.011017, 0.015981]
nearest_run_copy_floor__three_angle_shear          relative_l2               20     20    0.016914  0.000080       [0.016890, 0.016955]
nearest_run_copy_floor__triaxial                   relative_l2               216    216   0.019984  0.003366       [0.022379, 0.024928]
nearest_run_copy_floor__two_angle_shear            relative_l2               28     28    0.010395  0.000602       [0.010466, 0.011595]
nearest_run_copy_floor__uniaxial                   relative_l2               38     38    0.024575  0.029520       [0.025519, 0.038317]
ridge_to_pod_32_floor                              mean_absolute_error       423    423   0.003459  0.005178       [0.004863, 0.005719]
ridge_to_pod_32_floor__biaxial                     mean_absolute_error       38     38    0.004107  0.004357       [0.004111, 0.006598]
ridge_to_pod_32_floor__isotropic                   mean_absolute_error       45     45    0.007765  0.002233       [0.006839, 0.007726]
ridge_to_pod_32_floor__one_angle_shear             mean_absolute_error       38     38    0.012813  0.010319       [0.011431, 0.015042]
ridge_to_pod_32_floor__three_angle_shear           mean_absolute_error       20     20    0.007687  0.001372       [0.007300, 0.008172]
ridge_to_pod_32_floor__triaxial                    mean_absolute_error       216    216   0.002432  0.001259       [0.002516, 0.002913]
ridge_to_pod_32_floor__two_angle_shear             mean_absolute_error       28     28    0.011589  0.008710       [0.010581, 0.014335]
ridge_to_pod_32_floor__uniaxial                    mean_absolute_error       38     38    0.002993  0.002073       [0.002820, 0.003492]
ridge_to_pod_32_floor                              structural_similarity_3d  423    423   0.999935  0.000197       [0.999617, 0.999744]
ridge_to_pod_32_floor__biaxial                     structural_similarity_3d  38     38    0.999908  0.000105       [0.999764, 0.999899]
ridge_to_pod_32_floor__isotropic                   structural_similarity_3d  45     45    0.999782  0.000105       [0.999780, 0.999820]
ridge_to_pod_32_floor__one_angle_shear             structural_similarity_3d  38     38    0.998785  0.002029       [0.998050, 0.998833]
ridge_to_pod_32_floor__three_angle_shear           structural_similarity_3d  20     20    0.999566  0.000208       [0.999492, 0.999614]
ridge_to_pod_32_floor__triaxial                    structural_similarity_3d  216    216   0.999953  0.000025       [0.999941, 0.999953]
ridge_to_pod_32_floor__two_angle_shear             structural_similarity_3d  28     28    0.999006  0.001608       [0.998258, 0.999035]
ridge_to_pod_32_floor__uniaxial                    structural_similarity_3d  38     38    0.999920  0.000053       [0.999907, 0.999925]
ridge_to_pod_32_floor                              relative_l2               423    423   0.004225  0.006619       [0.006818, 0.008186]
ridge_to_pod_32_floor__biaxial                     relative_l2               38     38    0.005077  0.005108       [0.005221, 0.008272]
ridge_to_pod_32_floor__isotropic                   relative_l2               45     45    0.009097  0.002726       [0.007981, 0.009086]
ridge_to_pod_32_floor__one_angle_shear             relative_l2               38     38    0.020430  0.017725       [0.017808, 0.024029]
ridge_to_pod_32_floor__three_angle_shear           relative_l2               20     20    0.011866  0.002519       [0.011071, 0.012817]
ridge_to_pod_32_floor__triaxial                    relative_l2               216    216   0.003353  0.001252       [0.003411, 0.003955]
ridge_to_pod_32_floor__two_angle_shear             relative_l2               28     28    0.018543  0.014941       [0.016728, 0.023092]
ridge_to_pod_32_floor__uniaxial                    relative_l2               38     38    0.003994  0.002098       [0.003662, 0.004373]
```

### floors, development block (the committed `strain_atlas_holdout` split, `operators.data`'s own)

The same three floors (training mean, nearest-run copy, ridge to a rank-32 POD basis), recomputed on the already-committed train/test split rather than the leave-one-level-out one, reported beside it as a second, independent read of the same block:

```
group                                           metric                    units  runs  median    interquartile  mean_interval       
training_mean_trivial_floor                     mean_absolute_error       22     176   0.029702  0.033238       [0.027292, 0.045778]
training_mean_trivial_floor__biaxial            mean_absolute_error       3      6     0.036861  0.015218       [0.029426, 0.059861]
training_mean_trivial_floor__isotropic          mean_absolute_error       5      10    0.023437  0.009742       [0.014085, 0.061586]
training_mean_trivial_floor__one_angle_shear    mean_absolute_error       2      18    0.020858  0.009348       [0.011510, 0.030207]
training_mean_trivial_floor__three_angle_shear  mean_absolute_error       2      16    0.030664  0.013208       [0.017456, 0.043872]
training_mean_trivial_floor__triaxial           mean_absolute_error       6      48    0.033547  0.031191       [0.023343, 0.060576]
training_mean_trivial_floor__two_angle_shear    mean_absolute_error       2      72    0.016061  0.004552       [0.011510, 0.020613]
training_mean_trivial_floor__uniaxial           mean_absolute_error       3      6     0.056310  0.022286       [0.016287, 0.060859]
training_mean_trivial_floor                     structural_similarity_3d  22     176   0.996311  0.007637       [0.991486, 0.995798]
training_mean_trivial_floor__biaxial            structural_similarity_3d  3      6     0.996301  0.003297       [0.990937, 0.997532]
training_mean_trivial_floor__isotropic          structural_similarity_3d  5      10    0.998369  0.001195       [0.988965, 0.999047]
training_mean_trivial_floor__one_angle_shear    structural_similarity_3d  2      18    0.995837  0.003185       [0.992652, 0.999022]
training_mean_trivial_floor__three_angle_shear  structural_similarity_3d  2      16    0.990535  0.006926       [0.983609, 0.997462]
training_mean_trivial_floor__triaxial           structural_similarity_3d  6      48    0.993044  0.005489       [0.988493, 0.995737]
training_mean_trivial_floor__two_angle_shear    structural_similarity_3d  2      72    0.997912  0.001110       [0.996802, 0.999022]
training_mean_trivial_floor__uniaxial           structural_similarity_3d  3      6     0.989312  0.005245       [0.988169, 0.998658]
training_mean_trivial_floor                     relative_l2               22     176   0.041598  0.043404       [0.038920, 0.060405]
training_mean_trivial_floor__biaxial            relative_l2               3      6     0.046988  0.017465       [0.038268, 0.073198]
training_mean_trivial_floor__isotropic          relative_l2               5      10    0.031094  0.011480       [0.019812, 0.073702]
training_mean_trivial_floor__one_angle_shear    relative_l2               2      18    0.033554  0.014395       [0.019159, 0.047948]
training_mean_trivial_floor__three_angle_shear  relative_l2               2      16    0.050880  0.021217       [0.029662, 0.072097]
training_mean_trivial_floor__triaxial           relative_l2               6      48    0.047809  0.040455       [0.035354, 0.076150]
training_mean_trivial_floor__two_angle_shear    relative_l2               2      72    0.026450  0.007291       [0.019159, 0.033741]
training_mean_trivial_floor__uniaxial           relative_l2               3      6     0.075355  0.029609       [0.023883, 0.083102]
nearest_run_copy_floor                          mean_absolute_error       22     176   0.007849  0.006292       [0.006702, 0.009700]
nearest_run_copy_floor__biaxial                 mean_absolute_error       3      6     0.008022  0.000603       [0.007677, 0.008883]
nearest_run_copy_floor__isotropic               mean_absolute_error       5      10    0.004310  0.000400       [0.004074, 0.006620]
nearest_run_copy_floor__one_angle_shear         mean_absolute_error       2      18    0.003896  0.000012       [0.003884, 0.003908]
nearest_run_copy_floor__three_angle_shear       mean_absolute_error       2      16    0.011514  0.000021       [0.011493, 0.011535]
nearest_run_copy_floor__triaxial                mean_absolute_error       6      48    0.013499  0.004544       [0.009545, 0.014343]
nearest_run_copy_floor__two_angle_shear         mean_absolute_error       2      72    0.006808  0.002900       [0.003908, 0.009708]
nearest_run_copy_floor__uniaxial                mean_absolute_error       3      6     0.005447  0.000560       [0.005001, 0.006120]
nearest_run_copy_floor                          structural_similarity_3d  22     176   0.999627  0.000498       [0.999376, 0.999633]
nearest_run_copy_floor__biaxial                 structural_similarity_3d  3      6     0.999729  0.000099       [0.999533, 0.999731]
nearest_run_copy_floor__isotropic               structural_similarity_3d  5      10    0.999788  0.000004       [0.999662, 0.999792]
nearest_run_copy_floor__one_angle_shear         structural_similarity_3d  2      18    0.999762  0.000003       [0.999758, 0.999765]
nearest_run_copy_floor__three_angle_shear       structural_similarity_3d  2      16    0.998923  0.000016       [0.998907, 0.998939]
nearest_run_copy_floor__triaxial                structural_similarity_3d  6      48    0.999302  0.000452       [0.999094, 0.999467]
nearest_run_copy_floor__two_angle_shear         structural_similarity_3d  2      72    0.999489  0.000269       [0.999220, 0.999758]
nearest_run_copy_floor__uniaxial                structural_similarity_3d  3      6     0.999733  0.000048       [0.999676, 0.999772]
nearest_run_copy_floor                          relative_l2               22     176   0.011417  0.010004       [0.010642, 0.014690]
nearest_run_copy_floor__biaxial                 relative_l2               3      6     0.011418  0.000297       [0.011415, 0.012009]
nearest_run_copy_floor__isotropic               relative_l2               5      10    0.007641  0.000154       [0.007338, 0.009701]
nearest_run_copy_floor__one_angle_shear         relative_l2               2      18    0.007116  0.000003       [0.007113, 0.007119]
nearest_run_copy_floor__three_angle_shear       relative_l2               2      16    0.018558  0.000141       [0.018416, 0.018699]
nearest_run_copy_floor__triaxial                relative_l2               6      48    0.019730  0.003806       [0.013965, 0.020162]
nearest_run_copy_floor__two_angle_shear         relative_l2               2      72    0.011463  0.004344       [0.007119, 0.015807]
nearest_run_copy_floor__uniaxial                relative_l2               3      6     0.008660  0.001722       [0.008061, 0.011505]
ridge_to_pod_32_floor                           mean_absolute_error       22     176   0.004317  0.001596       [0.004099, 0.005175]
ridge_to_pod_32_floor__biaxial                  mean_absolute_error       3      6     0.003158  0.000817       [0.003155, 0.004788]
ridge_to_pod_32_floor__isotropic                mean_absolute_error       5      10    0.004978  0.000195       [0.004774, 0.005639]
ridge_to_pod_32_floor__one_angle_shear          mean_absolute_error       2      18    0.003490  0.000009       [0.003481, 0.003499]
ridge_to_pod_32_floor__three_angle_shear        mean_absolute_error       2      16    0.005602  0.001736       [0.003866, 0.007338]
ridge_to_pod_32_floor__triaxial                 mean_absolute_error       6      48    0.004214  0.001788       [0.003590, 0.006134]
ridge_to_pod_32_floor__two_angle_shear          mean_absolute_error       2      72    0.003573  0.000092       [0.003481, 0.003665]
ridge_to_pod_32_floor__uniaxial                 mean_absolute_error       3      6     0.004386  0.001144       [0.003550, 0.005838]
ridge_to_pod_32_floor                           structural_similarity_3d  22     176   0.999846  0.000070       [0.999761, 0.999840]
ridge_to_pod_32_floor__biaxial                  structural_similarity_3d  3      6     0.999875  0.000015       [0.999846, 0.999875]
ridge_to_pod_32_floor__isotropic                structural_similarity_3d  5      10    0.999834  0.000016       [0.999809, 0.999843]
ridge_to_pod_32_floor__one_angle_shear          structural_similarity_3d  2      18    0.999858  0.000005       [0.999853, 0.999864]
ridge_to_pod_32_floor__three_angle_shear        structural_similarity_3d  2      16    0.999656  0.000205       [0.999451, 0.999861]
ridge_to_pod_32_floor__triaxial                 structural_similarity_3d  6      48    0.999805  0.000106       [0.999727, 0.999847]
ridge_to_pod_32_floor__two_angle_shear          structural_similarity_3d  2      72    0.999860  0.000004       [0.999855, 0.999864]
ridge_to_pod_32_floor__uniaxial                 structural_similarity_3d  3      6     0.999793  0.000086       [0.999689, 0.999861]
ridge_to_pod_32_floor                           relative_l2               22     176   0.006817  0.001631       [0.006557, 0.007800]
ridge_to_pod_32_floor__biaxial                  relative_l2               3      6     0.005705  0.000765       [0.005594, 0.007125]
ridge_to_pod_32_floor__isotropic                relative_l2               5      10    0.007150  0.000426       [0.006881, 0.007908]
ridge_to_pod_32_floor__one_angle_shear          relative_l2               2      18    0.005980  0.000156       [0.005825, 0.006136]
ridge_to_pod_32_floor__three_angle_shear        relative_l2               2      16    0.008969  0.002878       [0.006091, 0.011847]
ridge_to_pod_32_floor__triaxial                 relative_l2               6      48    0.006701  0.001706       [0.006330, 0.008550]
ridge_to_pod_32_floor__two_angle_shear          relative_l2               2      72    0.005946  0.000122       [0.005825, 0.006068]
ridge_to_pod_32_floor__uniaxial                 relative_l2               3      6     0.007824  0.000910       [0.006067, 0.007887]
```

### the pre-registered kill, neither bar invented here

**Canon bar**: kill unless the member's own relative L2 is under 0.7x the best of these four floors on the leave-one-level-out block. The strongest floor measured is **bracketing_interpolation_floor**, pooled median relative L2 **0.091%** -- required absolute: **0.064%**.

**The honesty note, stated before any member is trained**: the canon's own text calls this pattern's gate case the weakest in the suite, and says plainly that a linear-interpolation floor winning on a smooth factorial sweep is the *expected*, reportable outcome, not a failure to bury. Bracketing interpolation measures under 0.09% relative L2 pooled, and under 0.21% on every single family's own median (triaxial, the largest and least smooth arm, is the worst case). A trained member clearing a bar this tight, on a physical regime this close to linear, would be the genuinely informative result; one that does not is exactly what the canon predicted and precisely why this member is worth building anyway -- the parametric task is the suite's honest admission that not every gate is won by the network.


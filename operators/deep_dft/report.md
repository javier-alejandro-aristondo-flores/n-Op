# deep_dft — measured against its floors

Regenerate with `python3 -m operators.deep_dft.report`.

The block, the three floors and the pre-registered claim ladder below were measured before a single training step was taken. The member's own result follows once training is possible; until then this section says so plainly and nothing else about this command changes.

## The block

Defect campaign, fold zero as the evaluation (kill) block: 42 runs across 21 units, folds one through four training the floors (147 runs). 18 of the 42 fold-zero runs carry an element absent from every training fold (held-out chemistry), scored as its own row beside the pooled one. Training vocabulary: 49 (element, pseudopotential title) pairs plus the trained unknown row.

## Floors, measured before training, on this exact block, normalized mean absolute error

The superposed-atomic-density floor reads `superposed_atomic_density` directly off the store, no fitting. The reduced-salted floor is a standardized ridge from per-species isotropic gaussian shells (eight widths, periodic images by cell height) onto density minus the atomic superposition, fit on 1,000 mixture-sampled probes per training run and scored on a fixed 5,000-point random subsample of each fold-zero run's own grid (a deliberate approximation for the floor's own cost, not for the member, which is scored on the true full grid); it stands in for the canon's own reduced density-fitting floor. The nearest-structure copy is context, not a gate: it copies the full charge density of the training run closest in per-element atom-count composition.

```
group                                        metric                          units  runs  median    interquartile  mean_interval       
superposed_atomic_density_floor_all_42       normalized_mean_absolute_error  21     42    0.154149  0.012129       [0.152565, 0.173254]
superposed_atomic_density_floor_held_out_18  normalized_mean_absolute_error  9      18    0.161438  0.015705       [0.156676, 0.200479]
reduced_salted_floor_all_42                  normalized_mean_absolute_error  21     42    0.111713  11.583332      [2.832035, 7.337816]
nearest_structure_copy_context_all_42        normalized_mean_absolute_error  21     42    0.067496  0.029246       [0.054986, 0.093563]
```

The reduced-salted floor's own spread is the one to read carefully: its interquartile (11.583332) and its 95% interval (2.832035 to 7.337816) both run roughly a hundred times its median (0.111713), unlike the other three floors' comparably tight spreads. That pattern means the ridge is badly conditioned on a handful of the 21 fold-zero units, most plausibly a rare-element shell fit, not that every unit scores near the reported number. Gate b is read against the median alone for exactly this reason; which units are the hard ones is left to the trained member's own per-unit evaluation, where the same units showing up as hard again would say something the floor alone cannot.

### the pre-registered ladder, absolute normalized mean absolute error

- **gate a** (>= 10x better than the superposed-atomic-density floor, `required_improvement=0.9`): pooled bar 0.015415, held-out-chemistry bar 0.016144
- **gate b** (>= 3x better than the reduced-salted floor, `required_improvement=2/3`): bar 0.037238
- **gate c** (spin row, member-local, not a floor comparison): on the 25 magnetic fold-zero runs (`|final_magnetization| > 0.001`), fraction with relative total-moment error <= 5% and the right sign, bar >= 0.9

Trilinear interpolation error, measured on a smooth synthetic field at the campaign's own 80-cubed grid resolution, 20,000 random query points: root-mean-square 0.001742.

**Not yet measured**: the member has not trained (floors are measured and pre-registered before training by policy, and the card is not this stream's yet), so no row above compares the member to these bars. The compact-support kernel and this composition's own caller-side seam both already differentiate on the foreign engine (`Test_Foreign_Engine_Forward_And_Gradient_Agree_On_A_Tiny_Structure`), so training itself is the only thing waiting. The figure suite below is the built, untrained architecture; this section will carry the member's own comparison against these bars and the gate c pass fraction once a checkpoint exists.

## Architecture, as built

Atom embedding (member-local unknown-row policy) into a 64-wide channel space; three atom-atom `ContinuousDisplacementKernel` layers (cutoff 4.0 angstrom, 20-function sinc basis) plus a local linear term and a smooth unit each; the atoms then join the probe points into one point set and three more identically shaped atom-probe layers carry the joint state, probes marked receive-only; a two-layer perceptron head reads each probe's own features onto density and magnetization.

Parameter count: 523,970 (about 94% of it the six kernels' own radial weight tensors, basis_count x hidden x hidden each).

Figure suite: 47 files written under `operators/deep_dft/figures/`, 0 inspection keys skipped (none). The atom-to-probe adjacency matrix (`composition__last_atom_to_probe_adjacency.png`) is this member's own figure: which probes fall inside which atoms' cutoff, on the demonstration structure `a241daf388f71072`.


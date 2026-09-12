# deep_operator_network — strain or lattice parameters → charge density field

Projection variants also map charge density → electron localization field, and the energy-trunk
variant maps parameters → density-of-states curve.

**Operator.** DeepONet — Lu, Jin, Pang, Zhang, Karniadakis, *Nature Machine Intelligence* 3, 218
(2021). Variants: POD-DeepONet (Lu et al., CMAME 393:114778, 2022) and PCA-Net (Bhattacharya,
Hosseini, Kovachki, Stuart, SMAI-JCM 7:121, 2021). Suite entries: `test-suite.md` §3, II.1 and
§7, VI.1.

## What it assembles

Sensor encoder (the branch) → dense layers on coefficients → basis-expansion readout (the trunk),
with integer-frequency Fourier features for exact periodicity. The energy-trunk configuration reads
its one coordinate through the raw-plus-Fourier feature map instead, because energy has no far face
to wrap onto, and closes with a softplus head because a density of states is non-negative and
unbounded above.

## Why it is shaped this way

**Zero kernel-integral layers, honestly.** For parameters → field there is no integral to take:
the input is already finite-dimensional. The framework permits a composition with no layers
rather than inventing a fake integral to satisfy the template.

**The trunk is why varying grids cost nothing.** Voxel centers are exact fractional coordinates,
so the fifteen grid shapes of the strain campaign and the per-cell grids of the perovskite length
sweep need no resampling anywhere in the pipeline. Grid shape touches only the sampler.

**Point-sampled training** makes memory a function of batch size rather than grid size — which is
why this family trains comfortably on the resident card even against 80³ targets.

**This is the interface shakedown.** Built first, with the correction operator, because between
them they exercise all three representations, the conditioning argument, the basis readout, and
the conservation wrapper. Either may amend the framework's abstract classes with a recorded
reason; the interface earns tenure by surviving two real implementations.

## Configurations

`canonical` (learned branch and trunk) · `proper_orthogonal` (basis fit on a per-voxel standardized
training block, with one learned offset added on top) · `principal_component` (fixed bases both
sides; its linear form is simultaneously the suite floor that kills unearned nonlinearity) ·
`energy_trunk` (the trunk runs over energy, giving the density-of-states operator).

**What actually tells `proper_orthogonal` apart from `principal_component` took two corrections to
find, and both are worth recording so the next person does not re-derive them.** First: modes and
the training mean are not the difference — `FixedModeExpansion` already adds the training mean back
on every call, and both configurations fit their basis on training-fold-only data by the identical
`Gram_Pod` call (verified empirically, not just read: a rank-32 ceiling computed independently
reproduces report.md's committed 0.000017 to all six digits). Second: the explicit learned bias
from the published POD-DeepONet form is real but measures as a structural zero here — `Gram_Pod`
centers on the mean, so the projection residual it leaves behind sums to exactly zero over the same
training block the basis was fit on, at any rank, whether or not the fields were standardized
first. The bias is kept (`BiasedModeExpansion`, and `output_bias` on the configuration's own
readout) because it is faithful to the published form and costs one scalar, not because it moves
the number. The actual difference is pointwise output standardization: each voxel's own mean and
spread across the training runs, computed because this configuration lives on a same-shape block
where per-voxel statistics exist (unlike `canonical`, which spans varying grids and is why decision
D5 chose global standardization there instead) — the fields are standardized voxel-by-voxel before
`Gram_Pod` ever runs, so the modes themselves are fit in a different space, not merely rescaled
after the fact.

**`canonical` replaces both fixed bases with a learned coordinate trunk, and that is what buys it a**
**reach the other two structurally cannot have.** `BasisExpansion` turns a fractional coordinate into
a feature vector and reads it against the branch's latent vector by inner product, so the member is a
genuine function, queryable at any point on any grid, not only the voxel centers a fixed basis was fit
on. Training is point-sampled — each step draws a handful of runs and a handful of points inside each,
so memory is a function of batch size and not of grid size — and that is exactly why this configuration
trains on every one of the strain campaign's fifteen grid shapes at once (`Functional_Field_Cache` and
`Canonical_Every_Shape_Predictions` in `report.py`), where the fixed-basis configurations are limited to
the single most common shape by construction. `report.py` scores it twice for exactly this reason: once
on the common grid, directly against the same ridge and nearest-neighbor floors the fixed-basis
configurations answer to, and once across every shape its own test runs hold, against a nearest-neighbor
floor computed within each shape (a fixed-rank basis has no such per-shape reading; a field copy does).
Decision D5 follows from this reach: per-voxel statistics like `proper_orthogonal`'s do not exist across
varying grids, so standardization here is one global mean and deviation for the whole campaign instead.
**A rank-32 linear projection was expected to be a very tight floor on a fixed shape, one a learned
trunk would likely pay for its generality against.** Measured, with a real budget, a three-stage
decreasing schedule and early stopping on the final stage, it was not: `canonical` beats the ridge
floor on the common grid by 54.2% (cheap) and 41.3% (accurate) against a 25% requirement, and clears
the every-shape nearest-neighbor floor too. See `report.md` for the full tables. The reach across
every shape the fixed-basis configurations cannot read remains this configuration's justification
regardless; the common-grid win is a bonus the untuned scratch drill did not predict.

**`energy_trunk` is `canonical`'s sibling with a different coordinate**: the same branch-trunk form,
except the trunk runs over a single energy axis instead of three fractional position axes, so the
member is a genuine function of energy, queryable anywhere in the aligned window and between its
601 grid points. Three choices distinguish it from `canonical`. First, the coordinate feature map
is `RampedCoordinateFeatures`, not the periodic one — energy has no far face to identify with its
near one, so the raw coordinate rides beside the Fourier waves rather than being replaced by a
constant. Second, the branch takes seven features, not six: the six strain components plus the
functional (cheap or accurate) as a numeric indicator, so one member is trained pooled across both
functionals rather than one member per functional the way `canonical` is. Third, the readout closes
with a softplus head, applied after the trunk's inner product and before anything else touches the
value, because the target is a density of states and a signed field has no physical meaning here.
`Aligned_Energy_Grid` (`operators/training/loader.py`) fixes the window at −28 to +8 eV from the
valence-band maximum, 601 points at 0.06 eV — the ceiling was measured, not guessed: the lowest
top-band minimum across all 2,680 strain-atlas runs sits 8.357 eV above the alignment, so +8.0 never
reaches a region some run left uncomputed. Because that grid is identical for every run, unlike
`canonical`'s varying grid shapes, training draws no per-step sample at all: the whole training role
(1,856 curves, under 5 MB) is one fixed batch, and the trunk's own features are computed once on the
window rescaled to minus one to one, then held as an engine constant for the whole run.

**The card's headline metric hides most of the signal, and the report says so rather than hiding
it in turn.** A pre-training measurement (both functionals pooled, orbit-weighted medians, ridge
from parameters to curve) found the strain signal concentrated almost entirely at the band edges:
ridge beats the training-mean floor by 6.1% over the whole −28…+8 eV window, by 0.7% over the
valence band alone (−28…0 eV, 467 of 601 bins), and by 31.6% over the −2…+6 eV band-edge region
(133 bins) — because the valence band is nearly strain-invariant and dominates the whole-window
integral roughly fivefold, diluting real skill by about the same factor. `report.py` trains on the
card's own loss (`curve_l1`, unweighted, over the whole window, because the card is canon-bound) and
reports both windows beside `wasserstein_1d` and `gap_edge_error` for exactly this reason, plus a
clearly labeled band-edge-weighted ablation. No kill margin is invented: VI.1 sets none, and its own
honesty clause calls a floor win on a coarse spectral function an informative, reportable outcome,
not a failure — so `report.md` states measured skill against both floors and writes neither `pass`
nor `kill` for this configuration.

## Floors and kill thresholds

Ridge from parameters to basis coefficients is the natural floor: kill any variant not at least
twenty-five percent better on held-out strain families. Nearest-neighbor field copy in parameter
space is brutal on factorial sweeps — require a factor of two. If the learned map beats the
linear one by ten to fifteen percent or less, keep the linear model and drop the neural claim.

The projection variants are gated before training by a measured basis-decay check: reconstruction
within three percent at rank ≤ N/2, per campaign. The defect campaign is the expected failure —
localized features that move are the classic weakness of a fixed basis — and a failing block goes
to the grid-native members instead.

**`energy_trunk` sets no numeric kill margin.** The suite's own VI.1 entry fixes none, and states
outright that on a coarse spectral function — 172 irreducible k, both functionals pooled — a floor
winning is an informative, reportable result rather than a failure. `report.md` therefore states the
member's measured skill against the training-mean and ridge floors on both the whole window and the
band-edge region, and prints neither `pass` nor `kill` for this configuration.

## Inspection

Everything this member computes, learns or holds is reachable as named plain-word arrays through
`Inspect()`, and the figure suite under `figures/` is drawn from that dict alone — if a plot ever
needs something the dict does not carry, the dict is what is wrong.

**The branch** publishes one weight matrix and one bias vector per layer
(`encoder.sensor_encoder_layer_<n>_weights` / `_biases`) and the latent vector it last produced
(`encoder.last_latent_vector`) — the quantity the whole member exists to make.

**The composition** holds no layers, and says so by publishing only the vector it carried through
(`composition.last_carried_vector`).

**The readout** depends on the configuration, and the two sets are disjoint. The fixed-basis
configurations publish the modes as fields (`readout.basis_modes`, shaped rank × grid), the
training mean as a field (`readout.basis_mean`), the spectrum (`readout.basis_singular_values`)
and the coefficients last predicted (`readout.last_coefficients`). `proper_orthogonal` additionally
publishes its learned offset (`readout.output_bias`) and the two arrays that carry its actual
distinction — the per-voxel mean and spread its basis was standardized against
(`readout.voxel_mean`, `readout.voxel_scale`), both fields. The coordinate-trunk configurations
publish the trunk's weights and biases instead, plus the features it last read
(`readout.last_trunk_features`), shaped as fields when the query was a grid and as a plain
points-by-features table when it was not.

**`canonical` carries a second inspection surface beside the member's**, because it is the only
configuration whose training path itself computes something worth naming: `CoordinateFeaturizedBatches`
(`report.py`) wraps the point sampler and publishes its own `last_trunk_features` — the feature array the
most recently drawn training step actually multiplied against the branch's coefficients, shaped
`(runs per batch, points per run, feature count)`. This is distinct from `readout.last_trunk_features`
above: the readout's own copy is set by a whole-grid or whole-point-set query through `__call__`, the kind
the report's evaluation and figures use; the batch source's copy is set by the lifted, point-sampled
forward the loss actually trains through, and is the only place that path's own inputs are named at all.

**`energy_trunk` carries its own captured output beside the parts' arrays**, because it is the only
configuration whose readout is a pre-activation rather than the physical quantity itself: the member
itself (not the readout) publishes `last_predicted_curve`, the softplus head's own output at the last
query, flattened to one row. This is what makes the non-negative head reachable by name rather than
only re-derivable by calling the member again — the same discipline `readout.last_trunk_features`
already gives the trunk's own feature map, applied to the one step the trunk does not itself own.

**Wrapped for inference**, the conservation law publishes what it did: `last_renormalization_scale`
under the electron-count law, `last_removed_mean` under the zero-mean law. Both are exact
diagnostics rather than corrections — ground truth already integrates to the archived electron
count within 2e-7, so any scale away from one is the model's own error.

**Beyond the parts**, training emits its loss curve, and the report emits the per-run errors it
tabulates. The suite renders the components, the best and worst test predictions against truth
with their signed difference, the error spread by strain family, and the member against its
floors with the level it had to reach drawn across each.

The inspection arrays are cached under `_derived/_figures/` on the corpus volume, because modes
and means are fields and a field never leaves it. Only the rendered images enter this repository,
which is exactly the egress the suite document permits.

## Implementation specification

Measured, and in `report.md`; regenerate both it and the figures with
`python -m operators.deep_operator_network.report`. `principal_component` and `proper_orthogonal`
are both built and both measured there, each on its own basis. `canonical` is built too, assembled
by `Canonical_Network`, trained point-sampled on every grid shape the strain campaign holds, and
measured in the same report — once on the common grid against the same floors the fixed-basis
configurations answer to, once across every shape its own test runs hold. `energy_trunk` is now
built too, assembled by `Energy_Trunk_Network` and measured on `strain_to_states`
(`test-suite.md` §7, VI.1): both functionals pooled into one member, trained whole-curve on a single
fixed batch rather than point-sampled, against the training-mean and ridge floors, on the whole
window and the band-edge region, with a band-edge-weighted loss reported alongside as a clearly
labeled ablation and never as a substitute for the card's own loss.

# deep_operator_network — strain or lattice parameters → charge density field

Projection variants also map charge density → electron localization field, and the energy-trunk
variant maps parameters → density-of-states curve.

**Operator.** DeepONet — Lu, Jin, Pang, Zhang, Karniadakis, *Nature Machine Intelligence* 3, 218
(2021). Variants: POD-DeepONet (Lu et al., CMAME 393:114778, 2022) and PCA-Net (Bhattacharya,
Hosseini, Kovachki, Stuart, SMAI-JCM 7:121, 2021). Suite entries: `test-suite.md` §3, II.1 and
§7, VI.1.

## What it assembles

Sensor encoder (the branch) → dense layers on coefficients → basis-expansion readout (the trunk),
with integer-frequency Fourier features for exact periodicity.

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

## Floors and kill thresholds

Ridge from parameters to basis coefficients is the natural floor: kill any variant not at least
twenty-five percent better on held-out strain families. Nearest-neighbor field copy in parameter
space is brutal on factorial sweeps — require a factor of two. If the learned map beats the
linear one by ten to fifteen percent or less, keep the linear model and drop the neural claim.

The projection variants are gated before training by a measured basis-decay check: reconstruction
within three percent at rank ≤ N/2, per campaign. The defect campaign is the expected failure —
localized features that move are the classic weakness of a fixed basis — and a failing block goes
to the grid-native members instead.

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
`python -m operators.deep_operator_network.report`. The `principal_component` configuration is
built and judged there. `proper_orthogonal` is now built too, assembled by
`Proper_Orthogonal_Network` on the same split and basis rank, but its measured numbers are not yet
folded into the committed report or figures — those are regenerated separately, as one deliberate
step. `canonical` and `energy_trunk` remain declared, not built.

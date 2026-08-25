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

**The trunk is why varying grids cost nothing.** Voxel centres are exact fractional coordinates,
so the fifteen grid shapes of the strain campaign and the per-cell grids of the perovskite length
sweep need no resampling anywhere in the pipeline. Grid shape touches only the sampler.

**Point-sampled training** makes memory a function of batch size rather than grid size — which is
why this family trains comfortably on the resident card even against 80³ targets.

**This is the interface shakedown.** Built first, with the correction operator, because between
them they exercise all three representations, the conditioning argument, the basis readout, and
the conservation wrapper. Either may amend the framework's abstract classes with a recorded
reason; the interface earns tenure by surviving two real implementations.

## Configurations

`canonical` (learned branch and trunk) · `proper_orthogonal` (output basis fixed from the
training fields) · `principal_component` (fixed bases both sides; its linear form is
simultaneously the suite floor that kills unearned nonlinearity) · `energy_trunk` (the trunk runs
over energy, giving the density-of-states operator).

## Floors and kill thresholds

Ridge from parameters to basis coefficients is the natural floor: kill any variant not at least
twenty-five percent better on held-out strain families. Nearest-neighbour field copy in parameter
space is brutal on factorial sweeps — require a factor of two. If the learned map beats the
linear one by ten to fifteen percent or less, keep the linear model and drop the neural claim.

The projection variants are gated before training by a measured basis-decay check: reconstruction
within three percent at rank ≤ N/2, per campaign. The defect campaign is the expected failure —
localized features that move are the classic weakness of a fixed basis — and a failing block goes
to the grid-native members instead.

## Implementation specification

To be written.

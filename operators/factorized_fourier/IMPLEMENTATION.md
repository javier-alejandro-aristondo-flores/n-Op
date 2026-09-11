# factorized_fourier — charge density → electron localization field

Also charge density → local potential, as a calibration probe.

**Operator.** Factorized Fourier Neural Operator — Tran, Mathews, Xie, Ong, ICLR 2023
(arXiv:2111.13802); parent architecture Li et al., ICLR 2021 (arXiv:2010.08895).
Suite entry: `test-suite.md` §2, I.1 — the flagship.

## What it assembles

Pointwise lift → spectral resampling to the coarse grid → explicit stack of spectral-kernel
layers with factorized per-axis mode weights at the full coarse Nyquist → pointwise projection
with the bounded electron-localization head.

## Why it is shaped this way

**Truncate early.** The localization field is written on the half-resolution grid, so the layers
run coarse: lift on the fine grid, one transform, truncate to the coarse Nyquist, and stay there.
Nothing the target could carry beyond its own Nyquist is discarded, and the cost falls by eight.
Super-resolving back to the fine grid is a zero-pad of the same weights — worth running as a
self-consistency check, but never as a headline, because no fine-grid localization ground truth
exists anywhere in the corpus.

**Factorized, not full.** Per-axis spectral weights are what make the full Nyquist affordable in
three dimensions; a full mode tensor at the same width costs an order of magnitude more.

**The bounded head.** The localization field lives in [0, 1], and the head 1/(1 + softplus²)
matches the quantity's own defining form rather than clamping a free output.

**Metric channels.** The integer mode index knows nothing about the physical cell. Six
Gram-matrix channels and per-mode physical-wavevector features carry it; for the potential task
they are mandatory, since the Hartree part is 4πρ(k)/|k|² and |k| is metric-dependent.

**The deep-equilibrium variant lives here**, as `composition = FixedPoint` — not a separate
package. That is what makes the explicit → weight-tied → implicit ladder a one-component change.

## Floors and kill thresholds

Kill unless the model reaches half the error of the pointwise semilocal floor (a ridge or small
network on density, gradient, and Laplacian) on held-out defect chemistry with sweep-arm splits.
For the potential task: if it is not twice as good as the canonical spectral-Poisson floor,
record that the physics floor suffices and keep the task as a pipeline unit test — a finding, not
a failure.

## Implementation specification

To be written. The substrate question that used to open this section is answered: the transform
is wrapped behind `operators/substrate/fourier.py`, priced by the canon in days against multi-week
for an own Stockham transform, and the seam means replacing its body later touches no member. The
separable kernel this entry is named for now exists and carries gradients; what remains is the
assembly. Superseded, kept for the reasoning: the Fourier-transform substrate (vendor-wrapped versus written in
house), which is this entry's largest cost lever and is shared with every other spectral member.

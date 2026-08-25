# deep_dft — atomic structure → charge density field (and magnetization)

Queryable at any point.

**Operator.** DeepDFT — Jørgensen & Bhowmik, *npj Computational Materials* 8, 183 (2022), with
the PaiNN-style vector-feature upgrade as the recorded stretch. Suite entry: `test-suite.md` §4,
III.1 — the structure-to-field anchor.

## What it assembles

Atom embedding → explicit stack of compact-support-kernel layers over atoms and probe points
together → pointwise projection, with a two-channel (density, magnetization) head.

## Why it is shaped this way

**The probe mechanism is the operator argument.** The input is the atomic configuration as an
empirical measure — a sum of delta functions carrying species — and the first layer is an
integral operator with a learned continuous kernel evaluated against it. Probe points placed
anywhere in the cell join the message graph but only receive, so the density is a function
queryable at any point and differentiable in position. Grids supply supervision only; the corpus
exercises the claim directly, since one model consumes 40³, 64³, 80³, and 48×96×216 supervision.

**One point set, with roles.** Probes receive messages at every layer, so the layer state is
atoms and probes together. This is what collapsed the framework's two point representations into
one carrying a `roles` field.

**Periodic images by cell height.** With a cutoff comparable to the shortest cell height, the
minimum-image shortcut silently drops neighbours; images are enumerated per direction from the
cell heights with an exact distance filter.

**The spin channel is this suite's own extension.** The literature predicts total density only;
here a second channel carries magnetization, its loss normalized by the integrated absolute
moment and masked where the calculation was spin-restricted.

**Probe sampling is importance-weighted.** Error mass concentrates in atom-centred volumes, so
the sampler mixes uniform and atom-centred draws and de-biases with inverse-proposal weights,
keeping the loss an unbiased estimate.

## Floors and kill thresholds

Three gates. Against the superposed-atomic-densities floor (already on disk for the paired-field
runs): a factor of ten. Against the reduced isotropic kernel-ridge floor: a factor of three, or
probe message passing is not earning its complexity. On the magnetic runs: moment error within
five percent and the correct total-moment sign on ninety percent. Any gate failed after the full
budget kills that task; two tasks killed removes the member.

## Implementation specification

To be written. The schedule risk is scatter-add throughput on the project's own autodiff
substrate — a five-fold slowdown against framework baselines turns the strain campaign from days
into weeks.

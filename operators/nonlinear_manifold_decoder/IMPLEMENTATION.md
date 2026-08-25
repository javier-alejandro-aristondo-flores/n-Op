# nonlinear_manifold_decoder — strain or lattice parameters → charge density field

Decoded point by point.

**Operator.** NOMAD — Seidman, Kissas, Perdikaris, Pappas, NeurIPS 2022 (arXiv:2206.03551).
Suite entry: `test-suite.md` §3, II.3.

## What it assembles

Sensor encoder → dense layers → nonlinear decoder: the output at a point is a nonlinear function
of (latent, position).

## Why it is shaped this way

**It breaks the linear-reconstruction ceiling.** Every basis-expansion readout writes the output
as a linear combination of fixed or learned modes, and that caps how well a solution manifold with
sharp parameter dependence can be represented. This decoder is the named alternative.

**It is also why readouts are plain operators.** Its output is not an integral and not a linear
combination — a stricter readout abstraction would have had to special-case it. The framework's
looser interface absorbs it without a seam.

**Restricted to parametric tasks.** Its global latent is a bottleneck for field-to-field maps
with half a million input points; the potential task is permitted only as a kill-gated baseline.

## Floors and kill thresholds

Beat radial-basis and linear interpolation in parameter space by a factor of one and a half. The
operator badge is earned on grid transfer: error inflation at most 1.3× when evaluated on the
strain campaign's off-dominant grid shapes.

## Implementation specification

To be written.

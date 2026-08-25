"""Compositions — the four chaining schemes.

Intended contents (implementation phase):
  - ExplicitStack — a chain of distinct layers
  - WeightTied — one layer, applied a fixed number of times
  - FixedPoint — one layer to convergence: damped Picard baseline, Anderson acceleration
    (small least squares on the processor), tolerance and iteration cap, per-sample solver
    telemetry; backward by phantom gradients (default), Jacobian-free (debug floor), or the
    implicit-function adjoint (audit tool) — the mandatory small-grid gradient audit runs
    before any full-size training, and after every anomaly
  - MultiScale — the U-shaped directed graph with skips and filtered resampling; designates
    the output scale (the electron-localization head lives at the coarse scale by the
    half-grid law)
"""

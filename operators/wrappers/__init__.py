"""Wrappers — Operators around Operators, plus one thing that is deliberately not.

Intended contents (implementation phase):
  - Residual — identity plus correction, with the correction head zero-initialized so
    training starts exactly at the identity floor
  - Conditioned — per-layer scale-and-shift modulation from the condition vector (the
    concat-at-encoder alternative needs no wrapper at all)
  - Conserving — exact, free constraints read from the task card and the quadrature:
    densities renormalized to the electron count; correction outputs projected to zero mean
    (both fidelities share the electron count, so ∫Δρ dV = 0 exactly); potential outputs
    with the uniform mode pinned. Attaches to task heads, never to operators as such.
  - ConformalCalibrator — NOT an Operator: takes a trained predictor and a calibration set
    (at the symmetry-orbit level — roughly 299 exchangeable units on the strain data, not
    1,291 points) and returns interval-valued predictions with guaranteed marginal coverage.
"""

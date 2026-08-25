"""Readouts — concrete Operators that carry channel space out to the answer.

Intended contents (implementation phase):
  - PointwiseProjection — narrow channels point by point; bounded heads live here (the
    electron-localization head is 1 / (1 + softplus²), matching that field's defining form)
  - BasisExpansion — the trunk: evaluate learned or fixed basis functions at any requested
    point and combine with the coefficients (integer-frequency Fourier features keep exact
    periodicity; an energy trunk makes the density-of-states operator)
  - NonlinearDecoder — output as a nonlinear function of (latent, position); the one readout
    that is not an integral, and the reason readouts are Operators rather than a stricter
    abstraction

No abstract class here: a readout is just an Operator.
"""

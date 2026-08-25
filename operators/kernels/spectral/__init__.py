"""SpectralKernel: translation-invariant κ on the torus, applied by Fourier multiplication.

Intended contents (implementation phase):
  - SpectralKernel — full and factorized (per-axis) complex mode weights; mode truncation;
    physical-wavevector features from the domain's reciprocal lattice (non-orthogonal cells)
  - spectral resampling — truncation and zero-padding between grid shapes; this is also the
    "truncate-early" step of the flagship and the resampler the alias-free activation rides
  - the batched three-dimensional real Fourier transform with autodiff through complex
    tensors — THE shared kernel of the package; its substrate (vendor-wrapped versus
    written in-house) is an open decision recorded in test-suite.md §0, and both cost
    figures are carried until it is made
"""

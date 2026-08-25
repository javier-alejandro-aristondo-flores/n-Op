"""CompactSupportKernel: small-support κ(x − y), integrated against either measure.

One class, two measures, two parametrizations:
  - on a uniform grid, κ tabulated at integer offsets → convolution (the convolutional
    operator learns the table directly)
  - on a point set, κ as a continuous function of displacement (filter-generating networks)
    → message passing (DeepDFT); directed edges honor PointSet roles (receive-only probes)

Periodic neighbor finding uses cell-height image enumeration — n_i = ceil(cutoff / height_i)
with an exact distance filter. The minimum-image shortcut is wrong in the skewed alloy cell;
this is a recorded corpus fact, not a style preference.

Also home to the alias-free activation machinery (upsample ×2 → nonlinearity → downsample ×2,
tile-streamed with a custom gradient rule — naive autodiff materializes the doubled grid and
runs out of memory on the 6 GB card).
"""

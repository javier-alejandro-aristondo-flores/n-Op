# alias_free_convolutional — charge density → electron localization field

Also the local potential and the defect-field slice.

**Operator.** Convolutional Neural Operator — Raonić, Molinaro, De Ryck, Rohner, Bartolucci,
Alaifari, Mishra, de Bézenac, NeurIPS 2023; alias-free formalism in Bartolucci et al. (ReNO),
NeurIPS 2023. Suite entry: `test-suite.md` §2, I.2.

## What it assembles

Pointwise lift → multi-scale composition (U-shaped, filtered resampling, output designated at the
coarse scale) of compact-support-kernel layers in the alias-free activation mode → pointwise
projection.

## Why it is shaped this way

**The hedge.** The Fourier lineage rings near discontinuities, and the density has sharp atomic
cores. This entry exists to measure whether an alias-free convolutional operator handles them
better on the same data.

**Alias-free is the whole claim.** Every resize is a filtered (sinc) resample and every
nonlinearity is applied at a doubled sampling rate, so each discrete operation is the exact
discretization of a continuous one. On a periodic cell the story is stronger than in the paper's
own setting, because the resampling is exact rather than windowed. Drop that and this is a U-Net,
which fails the operator gate.

**No three-dimensional version exists in the literature.** The paper and its code are
one- and two-dimensional; producing the three-dimensional case is part of this entry's value and
its risk.

**The localization head sits on the composition's own second scale**, which matches the
half-resolution target grid exactly — no extra machinery. The target is a coarse-grid pointwise
evaluation, not a filtered decimation of a fine field, so never train fine and downsample.

## Floors and kill thresholds

Two gates. Against the pointwise semilocal floor: at least twenty percent better, or the map was
effectively local and no operator was warranted. Against a width-matched plain U-Net: match or
beat it at native grids **and** degrade at most half as much under grid-shift probes. If the
U-Net ties on both, the alias-free surcharge is unearned and the entry is rejected.

## Implementation specification

To be written. The hardest kernel is the fused activation resampler with its own gradient rule;
naive autodiff materializes the doubled grid and exhausts the resident card.

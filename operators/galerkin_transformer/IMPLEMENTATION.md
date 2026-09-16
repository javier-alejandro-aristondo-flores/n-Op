# galerkin_transformer — charge density → electron localization (and → local potential)

**Operator.** Galerkin Transformer — Cao, NeurIPS 2021 — with the cross-attention decoder over
output-coordinate queries from OFormer — Li, Meidani, Farimani, TMLR 2023. Suite entry:
`test-suite.md` §2, I.4.

## What it assembles

Pointwise lift over the input channels and periodic coordinate features of the grid points →
explicit stack of softmax-free attention layers over grid tokens → a cross-attention decoder that
answers at any set of output coordinates → pointwise projection.

## Why it is shaped this way

**Tokens are grid points, and attention is linear in their number.** The softmax-free form is a
learnable projection whose cost is two matrix products per head, so a coarse grid's tens of
thousands of tokens are affordable where dense attention is not at any resolution in scope.

**The decoder is the operator claim.** Output coordinates are queries against the token grid, so
the same weights answer any grid, and the half-grid localization target needs no special machinery.

**Tokens live on the coarse Nyquist grid.** The canon's fine-grid trunk needs layer-granular
checkpointing and a loss scaler this substrate does not carry; the canon itself files that trunk
under its later tier, and the coarse grid is where the flagship already truncates.

## Floors and kill thresholds

Staged, cheap first: on the perovskite angle stratum the member must beat the nearest-angle field
copy and the linear-in-angle interpolation by a factor of two within about two hours of wall-clock,
or the entry dies before any fine-grid spend. Then the pattern rule on localization: twenty percent
better than the pointwise semilocal floor. The cross-entry bar on the potential task, within one
and a half times the flagship's error, is recorded when that task is run.

## Implementation specification

To be written.

# Training stages

How the operator is trained, in what order, and where the oracle attaches.

Canon owns the curriculum gating fractions: `residual-definitions §4.1`, settled as
`0.10 / 0.60 / 0.90` in `open-decisions`. Those fractions govern which residual
*categories* participate inside informed training. This file owns something the corpus did not
previously state: the **stage ordering**, the reason for it, and what happens at inference.

## The stages

**1 · Supervised epochs.** Train on VASP DFT data. This is the coarse work. It cuts the search
space for `Learnable_Structure` down to a region worth refining.

**2 · Informed epoch.** The oracle scores emitted states and returns keyed residuals with their
gradients. Those terms guide the final epoch. Curriculum gating within this stage follows
`residual-definitions §4.1`.

**3 · Inference.** The operator runs alone. It does not call an oracle.

## Why this order

The oracle refines. It does not search.

Residual terms are a local signal: they say how far a supplied candidate sits from satisfying each
law, and which direction reduces that. Over a large space that signal is not enough to find
anything. It becomes useful once the space is already small, which is what the supervised stage
buys.

So the DFT data does the searching and the oracle does the refining. Running the informed epoch
first would not work, and running it forever would not help.

## Consequences

- The oracle is **training-time machinery**. It is not part of the deployed model.
- Nothing in the inference path calls `Validate`. A trained operator is a standalone predictor.
- Any description of the system that draws the oracle as a permanent loop around the operator is
  wrong. It attaches for one stage.
- The four supervisory sources surveyed in `residual-loss-methodology.md` (cheap-compute, VASP,
  experiment, physics residuals) are weighted across training; this file fixes where the physics
  residuals sit in that order.

# residual_correction — cheap-functional charge density → accurate-functional charge density

From PBE to HSE, on the same geometry.

**Operators.** Δ-learning framing: Ramakrishnan, Dral, Rupp, von Lilienfeld, *JCTC* 11, 2087
(2015). Multifidelity operator form: Howard, Perego, Karniadakis, Stinis, *JCP* 493, 112462
(2023). Transfer protocol: Subramanian et al., NeurIPS 2023. Intervals: Romano, Patterson,
Candès, NeurIPS 2019. Suite entries: `test-suite.md` §5, IV.1 and IV.3.

## What it assembles

Not an architecture — a set of wrappers over a backbone. Residual, conditioned, and conserving,
plus the conformal calibrator alongside. Backbone: the projection form of the Deep Operator
Network first, the factorized Fourier operator later. Swapping it is a configuration change,
which is the framework paying for itself.

## Why it is shaped this way

**A precision task, not an accuracy task.** Submitting the input unchanged already scores about
1.1 percent relative error — the two fidelities differ by very little in the norm. Every metric
is therefore normalized by the correction itself, and the headline number is the fraction of the
correction's energy explained.

**The residual head is zero-initialized**, so training starts exactly at that identity floor and
can only be judged by how far past it the model gets.

**The correction integrates to zero, exactly.** Both fidelities are computed at the same electron
count, so the difference field has zero mean by construction — a free, exact constraint imposed by
projection rather than learned.

**Conditioning, not pooling.** Three exact-exchange fractions appear across the corpus and they
are three different targets. The default is per-campaign training; the single conditioned model is
a labelled ablation, never a pooled claim.

**Coverage is claimed at the orbit level.** Symmetry makes many strain points exactly equivalent,
so the exchangeable unit for calibration is the symmetry orbit — roughly 299 of them, not 1,291
points. Claims are marginal and orbit-level; never conditional.

## Floors and kill thresholds

Identity, global affine, and ridge on basis coefficients. Kill unless the model reaches half the
identity floor — that is, explains at least seventy-five percent of the correction's energy.

Any band-gap read-out rides as an auxiliary head, never as a member, and must beat the linear
scissor's 31.7 meV residual by a stated margin on orbit-held-out data. The scissor is brutally
good; matching it is the expected result and will be reported as such.

## Implementation specification

To be written.

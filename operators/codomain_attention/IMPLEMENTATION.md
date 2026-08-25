# codomain_attention — any subset of the fields → the missing fields

**Operator.** CoDA-NO — Rahman, George, Elleithy, Leibovici, Li, Bonev, White, Berner, Yeh,
Kossaifi, Azizzadenesheli, Anandkumar, NeurIPS 2024 (arXiv:2403.12553). Suite entry:
`test-suite.md` §6, V.1.

## What it assembles

Variable encoding → explicit stack of codomain-attention layers over spectral kernels with
weights shared across channel tokens → pointwise projection.

## Why it is shaped this way

**Tokens are fields, not grid points.** That single choice is what makes attention affordable
here: the attention map is at most eight by eight and costs a rounding error next to the spectral
convolutions, where a spatial-token transformer at 80³ would need a map with 2.6 × 10¹¹ entries.

**Variable channel counts are the point being tested.** Token counts run from five to eight across
this corpus under the spin-block law, and weight sharing across tokens is what permits it. Only a
variable-channel model can also consume the density-only campaigns as extra training material —
material no dedicated pairwise competitor can use.

**One model, many maps.** Training by masking fields and reconstructing them subsumes
density → localization, density → potential, and the inverse reads, and the deliverable includes
the full any-to-any matrix with untrained directions labeled exploratory.

**The alloy campaign is held out entirely** as the transfer test, with few-shot fine-tunes — the
counterpart of the paper's own transfer protocol, and the reason the corpus's heterogeneity is an
asset here rather than a nuisance.

**Half-grid handling introduces nothing.** The localization channel is zero-padded up at input and
its loss is evaluated on its own native coarse points. No cross-resolution attention is invented.

## Floors and kill thresholds

The competitor is a dedicated per-pair Fourier operator at equal total compute, trained on the
same block — the alloy stays held out on both sides, or the comparison is meaningless.

Three kills. If zero-shot completion is more than twice the dedicated model's error on two or
more pairwise tasks and still 1.25× worse after fine-tuning, the entry is rejected back to the
Fourier bank. If the pointwise semilocal floor lands within twenty percent on the localization
task, the completion flagship deflates. And if a low-data test on a quarter of the defect campaign
shows no pretraining advantage over a same-data dedicated model, the pretraining premise — this
entry's entire point — is dead here.

## Implementation specification

To be written.

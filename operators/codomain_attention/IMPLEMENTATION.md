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

Built 2026-09-16, against the minimal configuration the integrator pre-registered. This section
records what shipped and the engineering calls the build made where the canon left a choice open.

### The assembly

`CodomainAttention(NeuralOperator[GridFunction, GridFunction, GridFunction])`, built from framework
parts only:

- **Encoder**: `encoders.VariableEncoding(vocabulary=the six channel labels, hidden_channels=32,
  condition_width=4)`. The functional covariate (gga_pbe / hse06 / alloy_unpolarized / other, the
  fourth slot reserved for the alloy zero-shot transfer regime specifically) rides in the encoding's
  own condition slot, computed from the run's own path and campaign, never threaded through the
  wrapper-level electron-count convention (see "Two uses of `condition`," below).
- **Composition**: `compositions.ExplicitStack` of four `Layer(kernel=CodomainAttentionKernel(32,
  (19, 19, 19), head_count=2, mode_mixing="separable"), local_linear=TokenSharedLocalLinear(32),
  residual=True)` — the kernel and layer count `test-suite.md` and the integrator's brief both name.
- **Readout**: a new member-local part, `TokenSharedReadout` (`codomain_attention/readout.py`), not
  the shared `readouts.PointwiseProjection`. `PointwiseProjection` mixes the *whole* packed channel
  axis (every token's every hidden channel) into a fixed output width with one dense matrix, which
  is not token-count invariant and is not token-shared in the sense this member needs.
  `TokenSharedReadout` applies one hidden-channels-to-one linear map identically to every token,
  token count read off the shape exactly the way `TokenSharedLocalLinear` and
  `FunctionSpaceLayerNorm` already do, so it answers five tokens and six tokens with the same two
  arrays.
- **Per-token heads**, realized member-side after the shared readout (`codomain_attention/readout.py:
  Per_Token_Heads`): the bounded head `1/(1+softplus(x)²)` (the same formula `PointwiseProjection`'s
  own bounded mode uses) on every electron-localization token; the zero-mean pin (via `wrappers.
  Channel_Means`) on every local-potential token; every other token (charge density, magnetization)
  passes through untouched. Electron-count renormalization on the density token is *not* folded into
  this per-step head — see "Electron-count renormalization," below.

### The mask-token mechanism

Masked reconstruction needs the network to answer at a token position whose true content is
unknown. Because every layer here is endomorphic (a `Kernel[GridFunction, GridFunction]` with a
residual sum, token count in equals token count out), the model cannot *invent* an output token for
a channel that was never fed in — so hidden channels are not omitted, they are fed in place of their
own content, exactly as a masked-autoencoder feeds a mask token. A single new learned scalar,
`mask_flag` (initialized to 3.0, clearly off every channel's own transformed operating range so it
is never confusable with a visible channel that happens to sit near zero), is broadcast as a
constant field and substituted for every hidden channel's own values before the six-slot stack
reaches the encoder (`CodomainAttention.Forward_Tokens`). The channel's own `VariableEncoding` label
identity still rides through the encoding step even when its content is the mask flag, which is what
lets the shared attention weights tell "elf, currently masked" from "potential, currently masked."
`mask_flag` is one more entry in `Parameter_Values()`, trained like everything else.

### Five tokens and six tokens, one parameter set

`VariableEncoding`, `CodomainAttentionKernel`, `TokenSharedLocalLinear` and `TokenSharedReadout` are
all shape-derived from the channel axis at call time (`Token_Count(channel_axis, hidden_channels)`),
never from a stored token count, so the *same* trained arrays answer a run that structurally lacks a
channel (a genuinely spin-restricted archive, which would carry no magnetization block at all — the
164 unpolarized alloy runs, not this member's own six-channel training block, where every run
sampled carries all six). `Forward_Tokens` itself always presents six slots (using the mask flag for
whichever are hidden), since masked reconstruction needs a slot to answer into; the five-token path
is exercised directly through `member.channel_encoder` / `member.attention_stack` /
`member.token_readout` (own-named aliases onto the same encoder, composition and readout the base
class holds under its protocol-typed `encoder` / `composition` / `readout` attributes, needed since
`NeuralOperator.__init__` widens those to the bare `Operator` / `Composition` protocol and the
member-local parts, `TokenSharedReadout` chief among them, carry more than the protocol states), and
is covered by `Test_The_Shared_Parts_Answer_Five_And_Six_Tokens_With_The_Same_Parameters`.

### Channel preparation

Six labels: `charge_density`, `magnetization_density`, `electron_localization_up/down`,
`local_potential_up/down`. Truncation to the coarse 40³ processing grid is exact spectral
truncation (`framework.Spectral_Truncation_Resample`) for the four channels natively stored at 80³
(charge density, magnetization, both potential spins); the electron-localization channels are
already native at 40³ and pass straight through untouched — the "ELF half-grid" the canon names,
handled here by working at the coarse grid throughout rather than by zero-padding ELF up to the fine
one, which is a simplification of the original 80³/eight-token canon text explicitly authorized by
the integrator's own minimal-configuration brief.

**The ρ/m choice, decided.** The brief posed two options: log-compress through the flagship's own
spin-split machinery and keep magnetization as its own token, or lean on the sum/difference
reparametrization the canon names for the spin-pair channels. Built: charge density is log-compressed
directly (`log1p(ρ / reference_density)`, the flagship's own compression formula, reference density
the training block's own mean density) since ρ ≥ 0 always and needs no spin decomposition to be
compressed safely; magnetization is divided by one training-block scale and kept linear, no mean
removed, since it is already the corpus's own antisymmetric near-zero channel and needs no further
reparametrization. The two together *are* the sum/difference reparametrization of the physical spin
channels (ρ = spin-up + spin-down, m = spin-up − spin-down) — the corpus already stores it that way,
so nothing new is invented. The alternative (running both through the flagship's `Spin_Channels`
decomposition into two log-compressed spin channels) was rejected because it entangles ρ and m into
one joint two-channel representation, which breaks independent masking of density from magnetization
— exactly the axis the any-to-any completion matrix needs to probe.

**Local potential** is mean-removed per run (its own spatial mean, the gauge-arbitrary quantity a
DFT potential always carries) and divided by one training-block scalar (the pooled standard
deviation of the mean-removed spin channels across the pretraining population, mirroring the
flagship's own `target_scale`). Inversion back to physical volts always assumes a zero mean on the
*output* side, which the zero-mean conservation head guarantees exactly — a predicted run mean is
not recoverable, and is not physically meaningful to recover.

**Electron-count renormalization** on a predicted density is offered as an explicit, opt-in method
(`CodomainAttention.Renormalized_Density`), not automatic inside `__call__` or the training loss.
Two uses of `condition` collided: the encoder's own functional-covariate slot, and the wrapper
convention's electron-count target (`Conserving`'s `condition.vector[0]`). The framework gives an
operator exactly one `condition: Coefficients | None` argument, so this member spends it on the
functional covariate (what the encoder was built to consume) and leaves electron-count
renormalization to a second, explicit call the report and any downstream caller makes deliberately —
"at whole-field inference," per the brief, never inside the masked-reconstruction loss.

### The mask menu

Five patterns, drawn per training step: `density_to_elf_and_potential`, `density_and_potential_to_elf`,
`elf_to_density`, `potential_to_density` (the four named patterns, each an exact reveal of one of the
three physical groups — density carries magnetization with it, matching the *existing* pairwise task
cards `charge_to_localization`, `charge_to_potential` and `charge_and_potential_to_localization` input
sets exactly, checked directly against `operators.tasks.CARDS` in
`Test_Named_Mask_Patterns_Match_The_Canons_Own_Pairwise_Task_Cards`), and `random_subset` (every
channel independently visible with probability one half, redrawn until both sides are non-empty),
which is what actually exercises five-versus-six-token variability and channel-independent masking
during training. Exact grid augmentation (one of the 48 diamond-group operations, drawn fresh per
step) is applied to the raw fields *before* truncation, on the two native resolutions separately (the
four fine-grid channels stacked together, the two coarse ELF channels stacked together) under the
same operation, since the operations are stated in fractional coordinates and apply identically at
either resolution.

### Split

No committed artifact names the completion task's split yet (`operators.data.splits` promotion is
the integrator's own future step); `codomain_attention/splits.py` derives `CompletionBlock`
member-locally from the already-committed `paired_fields_fivefold.json`, restricted to
`supercell_strains` and `defect_set` (the alloy campaign is excluded from training and validation
entirely, reachable only through `Alloy_Transfer_Identifiers` for zero-shot evaluation). Fold 0
judges, fold 1 validates, folds 2–4 pretrain — the three roles the brief names, one fewer role than
the flagship's own `CubicBlock` carries since this member does not fit its own floors.
`CompletionBlock.Low_Data_Defect_Identifiers` adds a fourth, K3's own: a deterministic quarter of
the pretraining population's defect-only identifiers (hash-ordered on a member-local seed, the same
scheme the committed split engine uses for its own folds, so the draw is reproducible without
touching `operators.data.splits`), covered by
`Test_The_Low_Data_Defect_Slice_Is_A_Deterministic_Quarter_Of_The_Pretraining_Defect_Identifiers`.

### Measured

- **Parameters**: 3,838,762 at the pre-registered configuration (hidden_channels=32,
  kept_modes=(19,19,19), head_count=2, layer_count=4) — well above the suite's own rough ~1M
  estimate, which priced the *original* eight-token, 80³ design, not this minimal six-token, 40³
  one; reported plainly rather than reconciled to the stale figure. The dominant cost is the four
  spectral blocks (query/key/value/output) inside each attention layer (≈958K parameters per layer,
  ≈3.84M across four), not the encoder (384) or the readout (33). Master weights: 30.7 MB at double
  precision, 15.4 MB at the single-precision working width the card trains at.
- **Peak memory**: not yet measured. A forward-and-backward pass at this configuration needs the
  full 40³ grid at 32 hidden channels across six tokens, which this build deferred rather than run
  against a shared card already carrying other streams' live work at the time of this build (1.7-1.8
  GB free of 6 GB) — the house rule reserves that measurement for when the card is this member's own,
  alongside the 300-step cost probe the training section asks for.

## Inspection

Every array below is reachable through `CodomainAttention.Inspect()`. `NeuralOperator.Inspect()`
aggregates the three parts under `encoder.`, `composition.` and `readout.` prefixes;
`composition.layer_{n}.kernel...` and `composition.layer_{n}.local_linear...` carry a layer index
since the composition is an `ExplicitStack` of four layers. The unprefixed keys are this member's
own.

| Key | Shape | Drawn by |
|---|---|---|
| `encoder.token_lift_weights` / `_biases` | `(32,)` each | `Render_Bars` |
| `encoder.label_encodings` | `(6, 32)` | `Render_Matrix` |
| `encoder.condition_projection_weights` | `(32, 4)` | `Render_Matrix` |
| `composition.layer_{n}.kernel.{query,key,value,output}.{axis}_mode_weights_real` / `_imaginary` | `(39, 32, 32)` per named axis | `Render_Field_Slices` |
| `composition.layer_{n}.kernel.norm.scale` / `norm.bias` | `(32,)` each | `Render_Bars` |
| `composition.layer_{n}.kernel.temperature` | `(2,)` | `Render_Bars` |
| `composition.layer_{n}.kernel.last_attention_scores` | `(2, token_count, token_count)`, only once `Integrate()` is called directly on that kernel -- the member's own forward path never does | `Render_Field_Slices`, and the report's own bespoke attention-map figure (`Attention_Map_Figures`), one `Render_Matrix` panel per head, titled with the token order by field name |
| `composition.layer_{n}.local_linear.weights` / `biases` | `(32, 32)` / `(32,)` | `Render_Matrix` / `Render_Bars` |
| `composition.last_layer_norms` | `(4,)`, only once `Apply()` is called directly on the composition | `Render_Bars` |
| `readout.readout_weights` / `readout_biases` | `(1, 32)` / `(1,)` | `Render_Matrix` / `Render_Bars` |
| `mask_flag` | `()` | scalar panel |
| `reference_density` | `()` | scalar panel |
| `magnetization_scale` | `()` | scalar panel |
| `potential_scale` | `()` | scalar panel |
| `last_reconstruction` | `(6, *coarse_shape)`, after a `__call__` | `Render_Field_Sheet` |

Every key above is covered by the generic rank-dispatched renderer (`Render_Inspection_Suite`); no
key needs a bespoke renderer to avoid being skipped. `Test_Inspect_Renders_Every_Key` checks the
skipped list is empty on a toy member reached through its own `__call__`. The attention-map figure
is this member's own addition beyond the generic suite, since a bare `(head, token, token)` array
drawn as three unlabeled slices is not what "attention map, labeled by field name" asks for; the
report calls `Integrate()` directly on each layer's kernel to populate `last_attention_scores` before
drawing it.

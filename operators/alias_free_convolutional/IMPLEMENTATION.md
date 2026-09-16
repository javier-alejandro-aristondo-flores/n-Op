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

Built 2026-09-16. Gate class `AliasFreeConvolutional(NeuralOperator[GridFunction, GridFunction,
GridFunction])`. Owns exactly `operators/alias_free_convolutional/**`.

**Input convention, reused rather than reinvented.** The flagship's own `Log_Compressed_Channels`,
`Gram_Six`, `Standardized_Gram` and `Combined_Coarse_Input` (all exported from
`operators.factorized_fourier`) build the eight input channels: two log-compressed spin densities
plus six standardized Gram entries broadcast over the grid. The one difference from the flagship's
own use of them: `Combined_Coarse_Input` is called with `target_shape` set to the **input's own
native shape**, never a fixed coarse processing shape — this member has no truncate-early step, so
what the flagship calls "coarse" is, here, whatever grid the run actually carries (80³ on the
cubic block, 72–84 on the stretched probe grids). The FFT round trip this costs at an unchanged
shape is exact to floating-point noise and is the price of reusing one function instead of two.

**The three-scale multi-scale stack.** `PointwiseLift(32, 8)` lifts onto the fine grid, then
`MultiScale` descends two scales, bottoms out at a third, and ascends one — `output_scale=1`, so
the returned field sits at the middle scale (half the input's own resolution on every axis) with
no extra resampling machinery. Every layer is `TabulatedStencilKernel((1, 1, 1), out, in)` paired
with `PointwiseLift(out, in)` as the local linear term, `activation="alias_free"`. Channel widths
follow the canon's `32 / 64 / 128` across the three scales; residual carries the input forward only
at the one point a residual can apply exactly — the first descending layer, whose 32 → 32 map is
the sole place two consecutive scales share a width:

| Layer | in → out | scale | residual |
|---|---|---|---|
| `descending_0` | 32 → 32 | fine (n) | yes |
| `descending_1` | 32 → 64 | n/2 | no |
| `bottom` | 64 → 128 | n/4 | no |
| `ascending_0` | (128 + 64) → 32 | n/2 | no |

`ascending_0`'s input width is the upsampled bottom output concatenated with the `descending_1`
skip, exactly as `MultiScale.Scale_Outputs` wires it. The readout is `PointwiseProjection(2, 32,
bounded=True)`, the same `1 / (1 + softplus²)` head the flagship uses for the same channel pair
(`electron_localization_up`, `electron_localization_down`, both reused by name).

**Three scales, not four.** A fourth halving breaks on the 84-axis stretched probe cells
(84 → 42 → 21 → 10.5), and the grid-shift probe is load-bearing evidence this entry needs — a
config that cannot run on 84 cannot be evaluated on the probe that decides its identity check. Two
halvings clear every listed grid (72, 80, 84 all reach at least 18, 20, 21 before either stopping
or landing odd), so three scales is the largest U that never breaks.

**Parameter count, measured rather than assumed.** The canon widths give **488,034** parameters —
about half the "1–2M" estimate in the build brief. The gap is arithmetic, not a bug: with
`half_widths=(1,1,1)` every stencil holds 27 whole-voxel offsets, so a kernel alone costs
`27 × out × in`; the dominant terms are the bottom layer (27×128×64 = 221,184) and the ascending
layer (27×32×192 = 165,888). Reported here rather than silently widened to chase the estimate —
widening the channel sequence is a one-line change (`hidden_channel_widths=`) if the team wants to
spend more capacity, but that is a call for whoever owns the pre-registered configuration, not one
this build makes unilaterally.

**The pointwise twin.** `Alias_Free_Convolutional_Network(..., activation="pointwise")` builds the
identical U — same widths, same seeds, same everything — with the ordinary `Gaussian_Error_Linear_Unit`
in place of the fused kernel. This is the canon's own "width-matched plain U-Net" comparator the
identity check needs, produced by one shared builder rather than a second implementation that could
drift from the first.

**Augmentation.** `Random_Diamond_Operation` draws one of the 48 exact grid operations
(`Diamond_Grid_Operations`, `operators.framework`); `Augmented_Training_Pair` applies it identically
to an input field and its target before either reaches the lift. A pointwise lift cannot see a
spatial permutation, so augmentation commutes with it exactly (tested at every one of the 48
operations, not sampled).

**The entry's identity: the fused alias-free activation.** `activation.py`'s `Alias_Free_Activation`
streams the nonlinearity over channel chunks of four: upsample by two (`Upsampled_By_Two`), GELU,
downsample by two (`Downsampled_By_Two`), one chunk's doubled intermediate alive at a time. It is a
`CustomGradient`: the declared forward runs inside the foreign engine's own no-grad forward context,
so nothing beyond the chunk in flight and the two saved (non-doubled) arguments — the input and the
output — ever holds memory; the declared backward recomputes each chunk's doubled intermediate fresh
rather than reading it off a tape that was never built. The backward's closed form,
`∂x = D[GELU′(U·x) ⊙ U·g]`, falls out of the chain rule plus the measured transpose identities
`Uᵀ = 8D` and `Dᵀ = U/8` (both verified numerically, not assumed — the factor of eight cancels
exactly, which is why the rule has no stray scale in it). `Gaussian_Error_Linear_Unit_Derivative` is
written locally against the tanh-form constants in `operators/substrate/operations.py` and should be
deleted in favor of a dispatched substrate version the day one lands. Measured on this build's own
machine: peak accelerator memory for a fused forward-and-backward at 32³ with 16 channels is about
26% of the unfused (naive-autodiff) path's peak — comfortably "far under."

**The registration seam.** `operators/compositions/{multi_scale.py, __init__.py, fixed_point.py}`
each raise `NotImplementedError` on `activation == "alias_free"` — that seam is not owned by this
package and is not patched here. `Alias_Free_Activation` is built, tested and re-exported at this
package's root, ready for `operators.compositions` to reach for the moment it exports a lookup the
member can register into; see the stream's report to the team lead for the exact proposed patch.
Every test that needs the real composed seam (as opposed to the activation function alone, which is
fully tested on its own) is written now and gated on a runtime probe of the live seam, so it starts
passing the moment the patch lands with no test-file changes needed.

**Training and floors.** Not built yet: `operators.evaluation` does not yet export `CubicBlock`,
the localization floor builders, or `Write_Member_Results`, and `operators.substrate` does not yet
export `Periodic_Convolution_3d` (needed before an 80³ training run, not before anything this build
tests at 8³–16³). Once those land, the training protocol here follows the flagship's own
`Train_Flagship_Member` shape verbatim — staged 0.3/0.3/0.4 learning-rate schedule, validation every
100 steps, checkpoints, the coarse-input cache — with the CNO and the pointwise twin as two separate
card jobs, run names `elf_fold0_cno_<steps>` and `elf_fold0_pointwise_twin_<steps>`.

## Inspection

Every array below is reachable through `AliasFreeConvolutional.Inspect()`, aggregated by
`NeuralOperator.Inspect()` under the `encoder.` / `composition.` / `readout.` prefixes plus this
member's own unprefixed keys. `composition.` carries one of four scale names —
`descending_0`, `descending_1`, `bottom`, `ascending_0` — beneath it; `MultiScale`'s own
`*_output_norm` / `*_output_shape` keys appear only once `Apply()` is called directly on the
composition, which this member's own forward path never does (it calls `Forward` directly, exactly
as the flagship's `spectral_stack` does).

| Key | Shape | Drawn by |
|---|---|---|
| `encoder.lift_weights` | `(32, 8)` | `Render_Matrix` |
| `encoder.lift_biases` | `(32,)` | `Render_Bars` |
| `composition.{scale}.kernel.stencil_weights` | `(3, 3, 3, out, in)`, widths per the table above | `Render_Field_Sheet` |
| `composition.{scale}.kernel.stencil_magnitudes` | `(3, 3, 3)` | `Render_Field_Slices` |
| `composition.{scale}.kernel.stencil_offsets` | `(3, 3, 3, 3)` | `Render_Field_Sheet` |
| `composition.{scale}.kernel.last_output_values` | `(out, *scale_shape)`, only once `Integrate()` is called directly on that kernel -- the member's own forward path never does | `Render_Field_Sheet` |
| `composition.{scale}.local_linear.lift_weights` | `(out, in)` | `Render_Matrix` |
| `composition.{scale}.local_linear.lift_biases` | `(out,)` | `Render_Bars` |
| `readout.projection_weights` | `(2, 32)` | `Render_Matrix` |
| `readout.projection_biases` | `(2,)` | `Render_Bars` |
| `reference_density` | `()` | scalar panel |
| `gram_standardization_mean` | `(6,)` | `Render_Bars` |
| `gram_standardization_scale` | `(6,)` | `Render_Bars` |
| `last_gram_vector` | `(6,)`, after a numpy call | `Render_Bars` |
| `last_predicted_values` | `(2, *output_shape)`, after a numpy call | `Render_Field_Sheet` |

`{scale}` ranges over `descending_0`, `descending_1`, `bottom`, `ascending_0`. Every key above
dispatches through the generic rank-based renderer (`Render_Inspection_Suite`); none needs a
bespoke one, since the stencil kernel and the pointwise parts are shared framework code this member
only configures. The report's own figure suite (once `operators.evaluation` lands) additionally
draws the pointwise-twin comparator's own `Inspect()` beside this member's, so the identity check's
two models are browsable side by side rather than only compared in the metric table.

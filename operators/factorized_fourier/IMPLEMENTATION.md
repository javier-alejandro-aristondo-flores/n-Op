# factorized_fourier — charge density → electron localization field

Also charge density → local potential, as a calibration probe.

**Operator.** Factorized Fourier Neural Operator — Tran, Mathews, Xie, Ong, ICLR 2023
(arXiv:2111.13802); parent architecture Li et al., ICLR 2021 (arXiv:2010.08895).
Suite entry: `test-suite.md` §2, I.1 — the flagship.

## What it assembles

Pointwise lift → spectral resampling to the coarse grid → explicit stack of spectral-kernel
layers with factorized per-axis mode weights at the full coarse Nyquist → pointwise projection
with the bounded electron-localization head.

## Why it is shaped this way

**Truncate early.** The localization field is written on the half-resolution grid, so the layers
run coarse: lift on the fine grid, one transform, truncate to the coarse Nyquist, and stay there.
Nothing the target could carry beyond its own Nyquist is discarded, and the cost falls by eight.
Super-resolving back to the fine grid is a zero-pad of the same weights — worth running as a
self-consistency check, but never as a headline, because no fine-grid localization ground truth
exists anywhere in the corpus.

**Factorized, not full.** Per-axis spectral weights are what make the full Nyquist affordable in
three dimensions; a full mode tensor at the same width costs an order of magnitude more.

**The bounded head.** The localization field lives in [0, 1], and the head 1/(1 + softplus²)
matches the quantity's own defining form rather than clamping a free output.

**Metric channels.** The integer mode index knows nothing about the physical cell. Six
Gram-matrix channels and per-mode physical-wavevector features carry it; for the potential task
they are mandatory, since the Hartree part is 4πρ(k)/|k|² and |k| is metric-dependent.

**The deep-equilibrium variant lives here**, as `composition = FixedPoint` — not a separate
package. That is what makes the explicit → weight-tied → implicit ladder a one-component change.

## Floors and kill thresholds

Kill unless the model reaches half the error of the pointwise semilocal floor (a ridge or small
network on density, gradient, and Laplacian) on held-out defect chemistry with sweep-arm splits.
For the potential task: if it is not twice as good as the canonical spectral-Poisson floor,
record that the physics floor suffices and keep the task as a pipeline unit test — a finding, not
a failure.

## Implementation specification

The substrate question that used to open this section is answered: the transform is wrapped behind
`operators/substrate/fourier.py`, priced by the canon in days against multi-week for an own Stockham
transform, and the seam means replacing its body later touches no member. The separable kernel this
entry is named for now exists and carries gradients. The assembly built against `charge_to_localization`
(`operators/tasks`), explicit-stack configuration, is `operators.factorized_fourier.FactorizedFourier`,
built by the factory `Factorized_Fourier_Network`.

**Input transform.** Eight channels on the fine grid before anything is truncated: the up and down
spin densities, `(ρ ± m) / 2`, each passed through `log(1 + ρ_spin / ρ₀)` — nonlinear, so it must run
before any spectral truncation, unlike everything after it. `ρ₀` is chosen once as the training
block's own mean spin density (guarded above zero), recorded in `Inspect()` as `reference_density`.
Six constant channels carry the lattice's own Gram matrix `L·Lᵀ` (its six independent entries,
standardized by the training block's own mean and spread, recorded as `gram_standardization_mean`
and `gram_standardization_scale`) — built directly at the coarse resolution, never truncated,
because a spatially constant channel is unchanged by spectral truncation to round-off.

**Truncate-then-lift.** The two log-compressed channels are truncated from the fine grid to the
processing grid by `Resampled_To_Shape`, a local twin of `operators.compositions.multi_scale.
Spectral_Resampled` (not yet exported from that package's root — flagged to the integrator; every
other production module in this package still imports only through package roots). A pointwise
affine lift commutes exactly with spectral truncation — truncation acts on space, the lift on
channels, and the lift's bias is the field's own zero mode, which truncation always keeps — so
truncating the eight raw channels first and lifting after costs an eighth of lifting first and
truncating the wider hidden state. `Test_Truncate_Early_Equals_Lift_Then_Truncate` in the test
suite checks the two orders agree to round-off; `report.py` measured a maximum discrepancy of
`1.8e-15` on a toy grid.

**Stack.** `ExplicitStack` of 12 layers, each `SpectralKernel(kept_modes=(19, 19, 19),
mode_mixing="separable", output_channels=64, input_channels=64)` beside a `PointwiseLift(64, 64)`
local linear term, residual, GELU. `19` is not a round choice: it is the largest value
`SpectralKernel.Check_Modes_Fit` accepts at the coarse grid's own extent of 40 (`2·19 + 1 = 39 ≤
40`; `2·20 + 1 = 41 > 40` is refused) — the full coarse Nyquist, given the even-length axis's own
unpaired Nyquist bin is left out rather than aliased. Priced by `SpectralKernel.Parameter_Count_For`
before it was built: `958,464` real numbers per layer's kernel in the separable form, against
`485,941,248` the same modes would cost in the full (non-factorized) form — roughly five hundred
times more, the reason this member is named for the factorized kernel. With the local linear term
(`4,160`), the lift (`576`) and the readout (`130`), the whole assembly totals **11,552,194**
parameters (confirmed by construction, not only by the formula).

**Readout.** `PointwiseProjection(output_channels=2, hidden_channels=64, bounded=True)`, the head
`1 / (1 + softplus(x)²)` the readout package already implements.

**Composition is a constructor argument.** `FactorizedFourier.__init__` takes `composition:
ExplicitStack | WeightTied | FixedPoint` (the type alias `FourierComposition`), so the weight-tied
and deep-equilibrium rungs are the same member with a different composition object, not a different
codebase; both already satisfy the same lifted `Forward(lifted, input_values)` shape `ExplicitStack`
does.

**The operator claim.** `Forward_Field(lifted, log_density_values, gram_vector, target_shape)` takes
`target_shape` as an explicit, optional argument (falling back to the member's own configured
processing shape when omitted); `__call__` always passes the requested `GridSpec`'s own shape, so
the identical trained weights answer whatever grid is asked for. Verified on toy grids at two
unrelated resolutions in the same test.

**Batching.** The grid lineage's lifted parts (`PointwiseLift`, `PointwiseProjection`,
`ExplicitStack`) read `values.shape[0]` as the channel axis and the rest as the spatial shape, with
no batch axis anywhere — confirmed by reading `ExplicitStack.Layer_Outputs`, which reads
`current.shape[1:]` as the spatial shape. `SpectralKernel.Forward` and `Spectral_Resampled` /
`Resampled_To_Shape` would in isolation tolerate a leading batch axis (everything in them is
written against negative axis indices and einsum ellipses), but the lift and the stack would not,
so a step loops over the one or two examples of a batch in the loss closure and averages, rather
than carrying a batch axis through the member itself.

**Floors, recomputed.** `report.py` replicates `operators.data.stage0`'s `Eighty_Cubed_Block`,
`Elf_Ridge_Lines` and `Shell_Filter_Lines` recipes locally (two more names not exported from that
package's root for a caller outside `operators.data`: `Apply_Per_Shell_Filter` and
`Spectral_Gradient_Magnitude_And_Laplacian`), on the identical block (recounted at 261 train runs
across folds one through four, 76 evaluation runs in fold zero, matching stage zero exactly),
scored on all three of the card's metrics and on both spin channels, aggregated to the exchangeable
split unit before every median. Recomputed: ridge floor unit-median mean absolute error `0.0976`
(stage zero: `0.0964`, flat over run-channels rather than unit-aggregated); per-shell filter
`0.0830` (stage zero: `0.0816`, up channel only). A notable finding this recomputation surfaced:
the training block's own per-voxel mean field — a genuinely trivial floor added here for scale —
scores `0.0160` mean absolute error, beating both fitted floors; the per-voxel standard deviation
of the localization field across 120 training runs is `0.021`, against a field standard deviation
of `0.219` and a near-full `[0, 1]` range, meaning the block's dominant spatial pattern repeats
closely enough across strains and defects that a positional average is already most of the answer.
The pattern rule and the flagship's own bar remain anchored to the semilocal ridge, per doctrine;
this finding does not change either bar, only the context for reading them.

## Compute

Toy value-gradient-Adam steps, measured on the host (`TorchEngine(device_name="cpu")`, single
precision, width 64, 12 layers, `kept_modes` at each toy grid's own full Nyquist), report.py's
measurement script: fine 16³ → coarse 8³ (`K=3`, 2.1M parameters) `83.5 ms/step` at batch 1,
`168.3 ms/step` at batch 2; fine 32³ → coarse 16³ (`K=7`, 4.5M parameters) `413.3 ms/step` at batch
1, `805.8 ms/step` at batch 2 — batch cost is linear, as expected from the per-example loop. The
step cost does not scale linearly with grid volume alone (fixed per-call overhead is a larger share
of the smaller toy), so these numbers bound the real 80³ → 40³ cost only roughly; the real cost is
the first thing timed once the accelerator is available, before a training budget is fixed.

## Inspection

Every array below is reachable through `FactorizedFourier.Inspect()`. The prefixed arrays come from
`NeuralOperator.Inspect()` aggregating the three parts; the unprefixed ones are the member's own.
The `composition.` prefix carries a `layer_{n}.` segment beneath it only for the explicit-stack
configuration (twelve layers, each its own kernel and local linear map); `weight_tied` and
`fixed_point` share one layer, so their own keys read `composition.kernel...` and
`composition.local_linear...` with no layer index at all.

| Key | Shape | Drawn by |
|---|---|---|
| `encoder.lift_weights` | `(64, 8)` | `Render_Matrix` |
| `encoder.lift_biases` | `(64,)` | `Render_Bars` |
| `composition.layer_{n}.kernel.{axis}_mode_weights_real` / `_imaginary` | `(39, 64, 64)` per named axis | `Render_Field_Slices` |
| `composition.layer_{n}.kernel.{axis}_mode_magnitudes` / `_phases` | `(39, 64, 64)` per named axis | `Render_Field_Slices` |
| `composition.layer_{n}.kernel.gain_layer_0_weights` / `_biases` | `(8, 1)` / `(8,)`, metric-aware only (the potential task) | `Render_Matrix` / `Render_Bars` |
| `composition.layer_{n}.kernel.gain_layer_1_weights` / `_biases` | `(64, 8)` / `(64,)`, metric-aware only | `Render_Matrix` / `Render_Bars` |
| `composition.layer_{n}.kernel.last_output_values` | `(64, *output_shape)`, only once `Integrate()` is called directly on that kernel object -- the member's own forward path never does | `Render_Field_Sheet` |
| `composition.layer_{n}.kernel.last_mode_gains` | `(39, 39, 39, 64)`, metric-aware only, same direct-`Integrate()` caveat | `Render_Field_Sheet` |
| `composition.layer_{n}.kernel.last_mode_wavevector_features` | `(39, 39, 39)`, metric-aware only, same direct-`Integrate()` caveat | `Render_Field_Slices` |
| `composition.layer_{n}.local_linear.lift_weights` | `(64, 64)` | `Render_Matrix` |
| `composition.layer_{n}.local_linear.lift_biases` | `(64,)` | `Render_Bars` |
| `composition.last_layer_norms` (`weight_tied` / `fixed_point`: `last_application_norms`) | `(12,)`, only once `Apply()` is called directly on the composition -- the member's own forward path never does | `Render_Bars` (reference line at 1) |
| `readout.projection_weights` | `(2, 64)` | `Render_Matrix` |
| `readout.projection_biases` | `(2,)` | `Render_Bars` |
| `reference_density` | `()` | scalar panel |
| `gram_standardization_mean` | `(6,)` | `Render_Bars` |
| `gram_standardization_scale` | `(6,)` | `Render_Bars` |
| `last_gram_vector` | `(6,)`, after a numpy call | `Render_Bars` |
| `last_predicted_values` | `(2, *processing_shape)`, after a numpy call | `Render_Field_Sheet` |
| `target_scale` | `()`, potential task only | scalar panel |
| `last_fixed_point_iterations_taken` | `()`, `fixed_point` configuration only, after a numpy call | scalar panel |
| `last_fixed_point_final_residual` | `()`, `fixed_point` configuration only, after a numpy call | scalar panel |
| `last_fixed_point_cap_was_hit` | `()`, `fixed_point` configuration only, after a numpy call | scalar panel |
| `last_fixed_point_residual_history` | up to `(32,)`, `fixed_point` configuration only, after a numpy call | `Render_Bars` |

`{axis}` ranges over `first_axis`, `second_axis`, `third_axis` (the separable kernel's own three
per-axis weight tensors) and `{n}` over the twelve layer indices, explicit-stack configuration only.
Every key above is covered by the generic renderer dispatched on its rank alone
(`Render_Inspection_Suite`); no key needs a bespoke renderer. `Test_Inspection_Keys_Are_Covered_By_The_Generic_Renderer`
checks the skipped list is empty on a toy member reached through its own forward path, which is why
the direct-`Integrate()`-only and direct-`Apply()`-only keys above are not exercised by that
particular test -- they share the same rank-dispatched renderers as the keys it does cover, since
`Render_One_Array` dispatches on rank alone, blind to the name. The report's own figure suite
additionally draws a per-layer mode-magnitude spectrum through `Render_Spectrum`, radius-ordered
from the zero mode out to mode 19 — the last point on that plot is, by construction, the coarse
grid's own Nyquist edge, which is where the truncation from the 80³ input stops.

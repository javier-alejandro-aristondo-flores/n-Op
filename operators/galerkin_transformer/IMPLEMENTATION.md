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

**Attention core — `GalerkinAttentionKernel`, in `operators/galerkin_transformer/__init__.py`.** A
`Kernel[GridFunction, GridFunction]` whose `Forward(lifted, input_values, output_shape)` also
satisfies the framework's `LiftedKernel` shape structurally, exactly as `SpectralKernel` and
`CodomainAttentionKernel` already do, so `ExplicitStack` hosts it directly as a `Layer.kernel`. The
grid is flattened to `N = nx·ny·nz` tokens internally; query, key, value and output are each one
token-shared linear map (`encoders.PointwiseLift` reused at a square `hidden_channels →
hidden_channels` width, the same reuse the flagship already makes of `PointwiseLift` as a `Layer`'s
own local linear term). Key and value are standardized over the *token axis*, per channel
(`Token_Axis_Normalized`, a from-scratch normalizer — the codomain-attention package's
`FunctionSpaceLayerNorm` standardizes a token's own function over its channels and grid instead, the
wrong axis for a spatial-token attention). This is the Galerkin-type projection: normalizing K and V
rather than Q and K is what makes the map softmax-free. The score is never formed: per head,
`key_value = Einstein_Summation("hdn,hen->hde", key_heads, value_heads)` contracts over the
source-token axis first, producing a `(head_count, head_width, head_width)` block independent of
`N`; `attended = Einstein_Summation("hde,hdm->hem", key_value, query_heads) / N` is the second
matrix product. Both are linear in `N`; no `(N, N)` tensor is ever allocated. Four layers, four
heads, width 128, each wrapped by the framework's own local-linear-plus-GELU-plus-residual assembly
(`ExplicitStack.Layer_Outputs`) with a `PointwiseLift(128, 128)` as the local term, exactly the
flagship's `Explicit_Layers` idiom.

**Decoder — `QueryPointDecoder`.** An `Operator[GridFunction, GridFunction]` (not
`GridFunction | PointSet`: the gate class pins `Out = GridFunction`, so the decoder's own `__call__`
raises `TypeError` off a `PointSpec`, matching `FactorizedFourier.__call__`'s and
`CodomainAttentionKernel.Integrate`'s own precedent for a grid-pinned contract). Its `Forward(lifted,
token_values, query_features)` is discretization-blind: `query_features` is precomputed and passed
in, exactly as `NonlinearDecoder`/`BasisExpansion` externalize their own coordinate features, which
is what lets one `Forward` answer a grid and an explicit point list identically and is also what
keeps coordinate-feature construction (always plain numpy — coordinates are never trained) out of
any engine-lifted path where it could be handed to a foreign engine's tensor ops unconverted. Key and
value come from the encoder's own final tokens and are built once; queries are read in chunks of
`DECODER_QUERY_CHUNK_SIZE` rows, each chunk reusing the same `key_value` block, so decoder-side
memory never scales with the query count. `PointwiseProjection` finishes the head: bounded for
localization, unbounded for the perovskite density.

**Member — `GalerkinTransformer`.** Assembles `PointwiseLift` (encoder) → `ExplicitStack` of four
`GalerkinAttentionKernel` layers (composition) → `QueryPointDecoder` (readout), and owns the
task-specific input convention in `__call__` rather than in the parts, mirroring
`FactorizedFourier`'s own split between framework parts and a member-level `Forward_From_Coarse_Input`.
Two tasks:
- `"parametric"` (stage 1, `lattice_to_charge`): the six lattice factors broadcast as constant
  channels at `processing_shape` (`Constant_Channel_Field`, plain-numpy broadcast — there is no field
  input to truncate), concatenated with `Coordinate_Feature_Channels(processing_shape)`. Output is
  renormalized to the electron count via `wrappers.Conserving.Forward` (the lifted-array method, used
  directly rather than through `Conserving.__call__`, matching the flagship's own parametric task).
- `"localization"` (stage 2, `charge_to_localization`): a local from-scratch reimplementation of the
  flagship's own input convention (`Spin_Channels`, `Log_Compressed_Input_Channels`,
  `Lattice_Gram_Six`, `Standardized_Lattice_Gram`, `Lattice_Gram_Statistics`, `Reference_Density`) —
  not imported from `operators.factorized_fourier`,
  since this package's manifest declares no dependency on it and no other operator package imports a
  sibling operator package's root; the formulas are kept numerically identical to the flagship's by
  construction, for the cross-entry comparison the canon asks for. The fine input field is truncated
  to `processing_shape` by `compositions.Spectral_Resampled`, concatenated with the six standardized
  Gram channels and the coordinate features.

Both tasks answer queries at any grid shape the caller requests (64³ for the perovskite stage, 40³
for the cubic block, and whatever an invariance probe asks), independent of `processing_shape`,
because the decoder is the operator claim.

**Parameter count.** 374,145 (parametric task) / 373,762 (localization task) at width 128 / 4 heads /
4 layers (`GalerkinTransformer.Parameter_Count()`), inside the 0.3-0.5M pre-registration band the
integrator set before any card spend. The first build, at width 32 / 2 heads / 4 layers, reached only
25,761 parameters -- short of the canon's own ≈1M full-scale estimate -- and is kept here as a note:
the width was raised before pre-registration once that gap was seen, not discovered by a width search.
Head count and layer count are unchanged from the first build; only the hidden width moved. The
parametric task's own 768-parameter gap over the localization task's count is the decoder's lattice-
parameter condition channels ("Defect found and fixed" section below), added post-registration while
diagnosing why the gate was not learning.

## Compute

Attention is two GEMMs per head, `O(N · head_width²)`, never `O(N²)`. At 32³ tokens (stage 1) and
40³ tokens (stage 2) this stays well under the canon's own 64³-native ≈ 3.8 GB envelope; no
checkpointing is needed at this scale. The decoder's query chunking bounds cross-attention memory
independent of the query grid (64³ or 40³ queries, same per-chunk cost).

## Inspection

Every array below is reachable through `GalerkinTransformer.Inspect()`. The prefixed arrays come
from `NeuralOperator.Inspect()` aggregating the three parts; the unprefixed ones are the member's
own. `{n}` ranges over the four attention-layer indices.

| Key | Shape | Drawn by |
|---|---|---|
| `encoder.lift_weights` | `(128, input_channels)` | `Render_Matrix` |
| `encoder.lift_biases` | `(128,)` | `Render_Bars` |
| `composition.layer_{n}.kernel.key_norm_scale` / `_bias` | `(128,)` | `Render_Bars` |
| `composition.layer_{n}.kernel.value_norm_scale` / `_bias` | `(128,)` | `Render_Bars` |
| `composition.layer_{n}.kernel.query.lift_weights` / `key.lift_weights` / `value.lift_weights` / `output.lift_weights` | `(128, 128)` | `Render_Matrix` |
| `composition.layer_{n}.kernel.query.lift_biases` / `key.lift_biases` / `value.lift_biases` / `output.lift_biases` | `(128,)` | `Render_Bars` |
| `composition.layer_{n}.kernel.last_attended_norm` | `()`, only once `Integrate()` is called directly on that kernel object -- the member's own forward path never does | scalar panel |
| `composition.layer_{n}.local_linear.lift_weights` | `(128, 128)` | `Render_Matrix` |
| `composition.layer_{n}.local_linear.lift_biases` | `(128,)` | `Render_Bars` |
| `composition.last_layer_norms` | `(4,)`, only once `Apply()` is called directly on the composition -- the member's own forward path never does | `Render_Bars` (reference line at 1) |
| `readout.key_norm_scale` / `_bias`, `value_norm_scale` / `_bias` | `(128,)` | `Render_Bars` |
| `readout.query.lift_weights` | `(128, 25)` localization, `(128, 31)` parametric -- the last six columns are the lattice-parameter condition channels | `Render_Matrix` |
| `readout.query.lift_biases` | `(128,)` | `Render_Bars` |
| `readout.key.lift_weights` / `value.lift_weights` | `(128, 128)` | `Render_Matrix` |
| `readout.key.lift_biases` / `value.lift_biases` | `(128,)` | `Render_Bars` |
| `readout.final.projection_weights` | `(output_channels, 128)` | `Render_Matrix` |
| `readout.final.projection_biases` | `(output_channels,)` | `Render_Bars` |
| `readout.last_answered_query_count` | `()`, after a numpy call | scalar panel |
| `processing_shape` | `(3,)` | `Render_Bars` |
| `reference_density` | `()`, localization task only | scalar panel |
| `gram_standardization_mean` / `_scale` | `(6,)`, localization task only | `Render_Bars` |
| `last_predicted_values` | `(output_channels, *query_shape)`, after a numpy call | `Render_Field_Sheet` |

Every key above is covered by the generic renderer dispatched on its rank alone
(`Render_Inspection_Suite`); no key needs a bespoke renderer.
`Test_Inspection_Keys_Are_Covered_By_The_Generic_Renderer` checks the skipped list is empty on a
toy member reached through its own forward path, which is why the direct-`Integrate()`-only and
direct-`Apply()`-only keys above are not exercised by that particular test.

**What is not inspectable.** Attention is over grid points, so an attention "map" here would
naturally want to be an `(N, N)` object — exactly the tensor this kernel is built never to form.
What is exposed instead is per-head *projected* K/V/Q features (reachable by calling the kernel's
own parts directly) and the `(head_width, head_width)` `key_value` block, neither of which is stored
as a `last_*` array on the member's own forward path since it never leaves the lifted computation;
a caller wanting it calls `GalerkinAttentionKernel.Forward` directly, the same way the mandatory
dense-reference check in the test suite does.

## Defect found and fixed before the gate's verdict: the decoder never saw the lattice parameters

Diagnosed against the stopped, non-learning run `perovskite_gate_48840` (stage 0 complete at 14,652
steps, validation flat at 1.7422). Two lattice vectors 25% apart in parameter space, held-out
targets 48% apart, gave a fresh (untrained) member's output a 27.1% relative difference — the
network could see its input at initialization. After the stage-0 checkpoint the same pair's output
differed by 1.3e-6; after stage 1 (1,000 more steps), 4.4e-8. Training was driving the member
*toward* input-blindness, not away from it. Stage-by-stage tracing pinned the collapse to one place:
`QueryPointDecoder`'s query is built only from `query_features`, the output grid's own coordinate
features, identical for every example by construction — it carries no lattice channel at all. The
only path the token stream's own (still real, still nonzero) lattice-dependent signal had to reach
the output was the `key_value` block contracted against that fixed query, and training drove that
contraction toward numerical degeneracy: the encoder still disagreed by single-digit percent at the
decoder's own key/value even after their token-axis normalization, but the cross-attention output
built from them agreed to 1e-6–1e-8.

**Fix.** `QueryPointDecoder` gains `condition_channel_count` (0 by default, `PEROVSKITE_LATTICE_FACTOR_COUNT`
for the parametric task); `query_projection`'s own input width grows by that many columns, and
`Forward` takes an optional `condition_channels` vector, concatenated onto every query row *before*
`query_projection`, on the query branch alone -- the one branch `Token_Axis_Normalized` never
touches, so no per-channel mean-and-variance standardization over the token axis can wash a constant
per-example value back out regardless of what training does to the token pathway. `GalerkinTransformer.
Forward_From_Coarse_Input` reads the six lattice parameters straight off `combined_coarse_input`'s
own constant channels (they are already there, broadcast identically at every point) and hands them
through; +768 parameters (`hidden_channels · 6`) against ~373k, negligible. Regression coverage in
`operators/tests/test_galerkin_transformer.py`: `Test_The_Decoder_Query_Condition_Makes_A_Fresh_
Members_Output_Depend_On_The_Lattice_Parameters` (relative difference over 1e-3 at a fresh init) and
`Test_No_Token_By_Token_Tensor_With_The_Condition_Channels` (the conditioning is a concatenation, not
a contraction, so it introduces no `(N, N)`-shaped tensor). A second anomaly the conditioning fix
does not touch -- the trained run scored *worse* than the trivial training-mean-field baseline -- is
investigated separately below; one contributing defect is fixed, the dominant cause is diagnosed but
not yet fixed.

## Second anomaly: the run scored worse than the trivial mean-field baseline

An input-blind optimum is the training population's own pointwise mean field, MSE ≈ 0.109 on the
angle-stratum validation set; `perovskite_gate_48840` sat at 1.7422 from the probe onward, fifteen
times worse. Three things were checked and two fixed, on the host, card hidden throughout.

**Confirmed and fixed: `Conserving` was inside the training loss.** `Forward_From_Coarse_Input`
called `self.conservation.Forward` on every example, using each example's own known electron count
as the condition -- a whole-field, physical-units correction with no place inside a per-example loss
(the canon's own §A.4: "any scale it applies at inference is pure model error ... it belongs only on
the whole-field evaluation path"). Fixed: `Forward_From_Coarse_Input` no longer takes `weight_each`
or `condition_vector` and never renormalizes; `__call__` un-standardizes the raw forward's output
before handing it to `Conserving`, which now runs only at inference (the exact un-standardization is
the per-voxel one below). A 300-step host sanity run with a first attempt at un-standardization (one
pooled *scalar* standard deviation) showed this alone was **not** the dominant cause: the pre-fix
loss shape plateaued 15.3× worse than its own mean-field floor, the de-renormalized one 16.0× worse
-- no improvement, within one-seed noise. Kept anyway (required by §A.4 independent of this anomaly,
and it removes a real division-by-a-possibly-near-zero-or-sign-changing-integral risk), but the
search continued.

**Diagnosed: cusp-voxel domination of the mean squared error.** Measured directly on the training
population's own raw density (20,971,520 voxels): median 0.2566, MAD 0.1702, mean 0.7998, but max
15.61 (the canon's own §A.4 already names this: "dynamic range ≈420× with peaks at 15.56 e/Å³,
heavy-atom core cusps"). The top 5% of voxels by value carry **77%** of the total sum of squares; the
top 1% carry **38%**; the top 0.1% carry **7%**. A single pooled *scalar* standard deviation cannot
touch this: dividing every voxel by the same number leaves every voxel's *relative* contribution to
the squared-error sum exactly where it was, so squared-error gradient signal stays owned by a small
set of heavy-atom cusps whose height is set mostly by nuclear charge and barely moves under the
gate's own small angle perturbations -- consistent with the quick-partial-fit-then-stall shape both
sanity runs showed.

**Fixed: per-voxel target standardization, the canon's own recorded answer for exactly this corpus.**
§A.4 already prescribes it ("the perovskite target needs per-field standardization") and the built
branch-trunk member (`operators.deep_operator_network`) already carries the reusable helper,
`Pointwise_Statistics(training_fields) -> (voxel_mean, voxel_scale)` -- each voxel's own mean and
spread across the training runs, spread guarded to 1.0 where it is exactly zero -- already reused by
`residual_correction`. `GalerkinTransformer.density_voxel_mean`/`density_voxel_scale` replace the
scalar `density_scale` entirely (arrays shaped `(query_row_count, 1)`, the decoder's own row-per-
query-point layout, computed once by `report.py`'s `Perovskite_Voxel_Statistics` over the training
runs only); the training loss standardizes each target the same way up front
(`Perovskite_Gate_Example`); `GalerkinTransformer.Unstandardized_Target` inverts it at inference,
before `Conserving`. This removes the lattice-independent cusp-plus-bulk shape from the loss
entirely: predicting exactly zero in standardized space already *is* the training-mean field, so
every unit of gradient that moves the prediction away from zero is now working on the lattice-
dependent deviation the gate actually measures, not on reproducing a handful of cusp heights.
**Cost, stated plainly:** the query-anywhere property still holds for the network's own output in
standardized units, but `density_voxel_mean`/`density_voxel_scale` are grid-bound to the exact shape
they were measured on (the gate's own 64³ angle-stratum grid) -- `Unstandardized_Target` raises if
handed a different query row count, rather than silently applying statistics at the wrong resolution.

**Host sanity run, per-voxel standardization plus the decoder-conditioning fix, reported in the
gate's own metric** (median relative L2 on the raw density over the 20 held-out angle-stratum runs,
the same metric and population the two pre-registered floors use), 600 steps, seed 20260917, the full
population, `GATE_PEAK_LEARNING_RATE`:

| step | median relative L2 |
|---|---|
| 0 (untrained) | 0.2093 |
| 100 | 0.1787 |
| 200 | 0.1770 |
| 300 | 0.1779 |
| 600 | 0.1772 |

against the training-mean field's own median relative L2 on the same 20 runs, **0.1765**, and the two
pre-registered floors, nearest-angle copy **0.0853** and linear-in-angle interpolation **0.0264**.
Input-dependence at step 600 (relative difference between two validation runs' own predictions, full
physical-unit inference path): **3.87e-2**, comfortably over the 1e-3 floor -- the conditioning fix
holds through 600 steps of the fixed loss. The cusp-domination fix closed the gap from 15-16× worse
than the mean field to **within 1% of it, oscillating just above rather than below** (100-600: 1.2%,
0.3%, 0.8%, 0.4% worse) -- a qualitatively different, healthy shape (quick rise to the floor, then a
narrow, stable band around it) from the original bug's persistent 15× gap, but the integrator's own
criterion is "clearly below," which this does not yet satisfy on 600 stochastic single-example host
steps against a 9,000-14,000-step card run. Not yet asked for; the call on whether this is close
enough to schedule, or needs the criterion met first, is the integrator's.

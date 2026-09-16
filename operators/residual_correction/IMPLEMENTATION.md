# residual_correction — cheap-functional charge density → accurate-functional charge density

From PBE to HSE, on the same geometry.

**Operators.** Δ-learning framing: Ramakrishnan, Dral, Rupp, von Lilienfeld, *JCTC* 11, 2087
(2015). Multifidelity operator form: Howard, Perego, Karniadakis, Stinis, *JCP* 493, 112462
(2023). Transfer protocol: Subramanian et al., NeurIPS 2023. Intervals: Romano, Patterson,
Candès, NeurIPS 2019. Suite entries: `test-suite.md` §5, IV.1 and IV.3.

## What it assembles

Not an architecture — a set of wrappers over a backbone. Residual and conserving always;
conditioned is available but sits unused on the primary block, plus the conformal calibrator
alongside. Backbone: the projection form of the Deep Operator Network first, the factorized
Fourier operator later. Swapping it is a configuration change, which is the framework paying
for itself.

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
a labeled ablation, never a pooled claim.

**Coverage is claimed at the orbit level.** Symmetry makes many strain points exactly equivalent,
so the exchangeable unit for calibration is the symmetry orbit — roughly 299 of them, not 1,291
points. Claims are marginal and orbit-level; never conditional.

## Floors and kill thresholds

Identity, global affine, and ridge on basis coefficients. Kill unless the model reaches half the
identity floor — that is, explains at least seventy-five percent of the correction's energy.
Measured on the real block (`report.md`): identity 1.1131% relative L2, kill bar 0.5565%.

Both ridge floors (from the cheap density's own coefficients, and from context, from the six raw
strain components) land within a few parts in a million of the rank-32 ceiling — the strain
atlas's orbit holdout removes exact symmetry copies, not nearby strain magnitudes, so a held-out
point sits an interpolation step (about 0.005 in tensor-component units, measured) from its
nearest training point on the same sweep. The 50% kill margin is cleared by every closed-form
floor by orders of magnitude before training starts; the informative comparison for the trained
member is how close it lands to the ridge floor and the ceiling, not the kill margin itself. This
is stated plainly in `report.md` rather than treated as a surprise once training runs.

Any band-gap read-out rides as an auxiliary head, never as a member, and must beat the linear
scissor's 31.7 meV residual by a stated margin on orbit-held-out data. The scissor is brutally
good; matching it is the expected result and will be reported as such.

## Implementation specification

**Backbone (`ProjectionBackbone`, in `operators/residual_correction/__init__.py`).** Encoder
`BasisProjectionEncoder` on a rank-32 `Gram_Pod` basis of the cheap density (mean included — this
part carries no identity requirement). Branch `SensorEncoder` sized `(cheap_rank, 128, 128,
correction_rank)` — 128-128 fixed by design, the two rank endpoints read off whichever rank the
two `Gram_Pod` fits actually kept (32 on the real block; a small toy block keeps fewer, since a
mean-centered fit cannot exceed one less than its snapshot count). Readout
`PointwiseStandardizedExpansion` on a rank-32 `Gram_Pod` basis of the correction field
Δρ = ρ_accurate − ρ_cheap, fit on the training pairs.

**The zero-initialized start, exactly.** Two changes make the assembled member's output equal the
cheap density to floating-point round-off before any training step: (1) `Last_Layer_Zeroed`
replaces the branch's final weight matrix and bias vector with zeros right after construction, so
the branch outputs the zero vector for every input, regardless of the earlier layers' random
draw (`MultilayerPerceptron`'s last layer is already linear, so zero weights and a zero bias give
an exact zero, not an approximate one). (2) `Zero_Anchored` replaces the correction basis's fitted
ensemble mean with zeros before it reaches the readout, and the readout's own `voxel_mean` is
passed in as zeros too (`voxel_scale` stays the real per-voxel spread — multiplying a zero branch
output by any finite scale is still exactly zero). With both offsets at zero and the readout's own
learned `output_bias` starting at zero by construction, the raw correction is the exact zero array;
`Conserving(law="zero_mean")` then subtracts a zero mean from a zero field, unchanged; `Residual`
adds this exact zero back onto the cheap density. Every step is exact under IEEE 754 (`x - 0 = x`,
`x + 0 = x`), not approximately small — verified in
`Test_The_Step_Zero_Corrected_Density_Equals_The_Cheap_Density_To_Round_Off`
(`operators/tests/test_residual_correction.py`) via `np.array_equal`, not `np.allclose`.

This is a deliberate departure from `Gram_Pod`'s own convention (which centers a basis on the
corpus's measured average correction shape): a residual architecture's natural reference point is
zero correction, not the corpus's average correction shape, so the average shape is left for the
32 learned modes to reach through nonzero coefficients rather than baked in as a fixed offset. The
rank-32 ceiling reported in `report.md` uses the ordinary, mean-included `Gram_Pod` fit (the more
generous, standard capacity estimate); the operational, zero-anchored basis's own ceiling was not
separately measured, since the two share every mode and singular value and differ only in the
additive constant a trained model can reach on its own.

**A consequence worth naming.** A zero-initialized last layer means the loss gradient reaches only
that last layer and the readout's `output_bias` on the very first step — the chain rule multiplies
every earlier layer's gradient by the zeroed last-layer weight matrix, which is exactly zero.
Layers 0 and 1 of the branch wake up on the *second* step, once the first step has moved the last
layer away from zero. Measured directly (`Test_The_Zero_Initialized_Step_Reaches_Only_The_Last_Layer_And_The_Readout_Bias`,
`Test_Two_Adam_Steps_Move_Every_Parameter`): both are true on a toy block, exactly as this note
predicts, not merely approximately.

**Training path (`Forward_Correction`).** `ResidualCorrection.Forward_Correction(lifted,
cheap_coefficients)` — and the identical `ProjectionBackbone` method it delegates to — takes one
dict of named arrays (the branch's and readout's trained parameters *and* the backbone's fixed
constants: `input_scale`, `readout_basis_modes`, `readout_basis_mean`, `readout_voxel_mean`,
`readout_voxel_scale`, all listed by `Constant_Values()`) and one batch of the cheap density's own
basis coefficients, and returns the conserved correction field — never the identity-added density,
so a coefficient-space or field-space loss reads directly against Δρ. The constants merge cleanly
into a `TrainingBatch.arrays` dict alongside the true per-pair training data, because
`operators.training.Train` already lifts every batch array through `Lift_Constant`: no bespoke
lifting path was needed, and `Constant_Values()` was written to hand the trainer exactly what a
`TrainingBatch` wants. `__call__` (the inference path) recovers the plain, non-lifted computation
through the composed `Residual(Conserving(backbone, law="zero_mean"))` object graph, and both paths
are checked to agree to numerical round-off
(`Test_Forward_Correction_Agrees_With_The_Assembled_Call`).

**Conditioning.** Dropped from the primary build. The strain atlas is one campaign at one
exact-exchange fraction, so `Conditioned`'s per-channel scale and shift, driven off a covariate
vector that never varies across this block, would train to the identity map and add two unused
parameter arrays. `Conditioned` remains available in `operators/wrappers`, unedited, for the
canon's own labeled ablation (a pooled, multi-campaign model) if that is ever built; it is not
wired into `ResidualCorrection` here.

**IV.3, the conformal band.** `ConformalCalibrator(level=0.90, unit="symmetry_orbit")`, built from
`configs/projection_backbone.toml`'s `[conformal]` table exactly as
`Test_The_Calibrator_Is_Built_From_The_Configuration_As_It_Is_Written` (in the shared
`test_parts.py`) already exercises. The member has no native two-quantile head, so the calibrator
is driven in its degenerate point-prediction form: the corrected density stands in as both the
lower and the upper quantile, and `Calibrate`/`__call__` widen that zero-width band by the offset
a finite calibration set needs. `Nonconformity_Scores` already scores a whole field by its worst
voxel, so this is exactly the sup-norm field-band extension `test-suite.md` §5's IV.3 entry names,
reached through the existing wrapper machinery rather than new code. Calibrated on the validation
block's orbits, applied to the test block, coverage reported per orbit (a test orbit counts as
covered only if every one of its runs' whole fields sit inside the band everywhere).

**Escalation path, not built.** `configs/spectral_backbone.toml` names the factorized-Fourier
backbone (`PointwiseLift` → `ExplicitStack` of separable `SpectralKernel` layers at 40³ →
`PointwiseProjection`) that would replace `ProjectionBackbone` on a miss, plus the transfer
protocol to the defect set's 56 chained pairs. It stays a configuration file until the primary
run's verdict is in, per house policy: one miss is tried once, escalated once, then the entry is a
recorded dead end.

## Inspection

Every key `ResidualCorrection.Inspect()` exposes, and the renderer `Render_One_Array` reaches each
one through (rank and name decide the renderer; see `operators/inspection/plots/suite.py`):

| Key | Shape | Renderer |
|---|---|---|
| `backbone.encoder.basis_mean` | grid shape (once a field has been seen) | `Render_Field_Slices` |
| `backbone.encoder.basis_mode_norms` | `(cheap_rank,)` | `Render_Bars` (reference line at 1, since these are norms of an orthonormal basis) |
| `backbone.encoder.basis_modes` | `(cheap_rank, *grid_shape)` | `Render_Field_Sheet` |
| `backbone.encoder.last_coefficients` | `(cheap_rank,)` | `Render_Bars` |
| `backbone.branch.sensor_encoder_layer_0_weights` | `(128, cheap_rank)` | `Render_Matrix` |
| `backbone.branch.sensor_encoder_layer_0_biases` | `(128,)` | `Render_Bars` |
| `backbone.branch.sensor_encoder_layer_1_weights` | `(128, 128)` | `Render_Matrix` |
| `backbone.branch.sensor_encoder_layer_1_biases` | `(128,)` | `Render_Bars` |
| `backbone.branch.sensor_encoder_layer_2_weights` | `(correction_rank, 128)` | `Render_Matrix` |
| `backbone.branch.sensor_encoder_layer_2_biases` | `(correction_rank,)` | `Render_Bars` |
| `backbone.branch.last_latent_vector` | `(correction_rank,)` | `Render_Bars` |
| `backbone.readout.basis_modes` | `(correction_rank, *grid_shape)` | `Render_Field_Sheet` |
| `backbone.readout.basis_singular_values` | `(correction_rank,)` | `Render_Spectrum` |
| `backbone.readout.basis_mean` | grid shape | `Render_Field_Slices` (identically zero on the operational basis — see above) |
| `backbone.readout.voxel_mean` | grid shape | `Render_Field_Slices` (identically zero, by the same construction) |
| `backbone.readout.voxel_scale` | grid shape | `Render_Field_Slices` |
| `backbone.readout.output_bias` | `(1,)` | `Render_Bars` |
| `backbone.readout.last_coefficients` | `(correction_rank,)` | `Render_Bars` |
| `backbone.input_scale` | `(cheap_rank,)` | `Render_Bars` |
| `cheap_basis_singular_values` | `(cheap_rank,)` | `Render_Spectrum` |
| `correction_basis_singular_values` | `(correction_rank,)` | `Render_Spectrum` |
| `conservation.last_removed_mean` | scalar | `Render_Scalars` panel |
| `zero_initialized_at_construction` | scalar (fixed `True`, a construction-time record — stays `True` regardless of how far training later moves the weights) | `Render_Scalars` panel |
| `last_correction_scale` | scalar | `Render_Scalars` panel |

`Test_The_Inspection_Suite_Covers_Every_Key_The_Member_Exposes` runs `Render_Inspection_Suite`
over a toy member's `Inspect()` output and asserts `suite.skipped == ()` — the renderer is the
completeness test, and it currently reaches every key above with none left over.

# multiple_input_operator_network — (charge density, local potential) → electron localization field

**Operator.** MIONet — Jin, Meng, Lu, *SIAM Journal on Scientific Computing* 44(6), A3490 (2022).
Suite entry: `test-suite.md` §3, II.2.

## What it assembles

Two fixed-basis sensor branches — one reading the charge density and magnetization, one reading
the local potential — each a `BasisProjectionEncoder` onto a rank-32 proper-orthogonal basis
followed by a `SensorEncoder`, combined multiplicatively in the latent space, read out through one
shared trunk (`BasisExpansion`) over the localization grid's own coordinates. The composition
carries no integral layers.

## Corrections to the original manifest

The manifest this package started from named `composition = ExplicitStack` and
`kernel = kernels.low_rank.LowRankKernel (multiplicative latent combination)`. Both were wrong and
are corrected here, in the manifest, and in the record:

- **Composition.** A branch–trunk map takes no kernel integral, exactly as `deep_operator_network`
  states of itself. The composition is `compositions.WithoutIntegralLayers`, which carries the
  branch's combined latent vector through unchanged. `ExplicitStack` chains kernel-plus-local-linear
  layers over a `GridFunction`; nothing here is a `GridFunction` once it reaches the composition.
- **Kernel.** `kernels.low_rank.LowRankKernel` pairs a learned core matrix with a feature map over
  points or grids — a different shape entirely from a Hadamard product of two latent vectors. No
  framework kernel performs MIONet's multiplicative combination, so none is assembled; the product
  is member-owned code (`TwoBranchEncoder.__call__` / `Forward_Coefficients`, `__init__.py`).

## Why it is shaped this way

It rides the Deep Operator Network's stack entirely and exists as its own package for one reason:
it is its own literature name with its own question — does the potential carry information about
electron localization that the density does not? Channel labels do the work of answering which
input field is which; `Labeled_Channel` refuses a field that does not carry the label it is asked
for, so a mislabeled or reordered channel set fails loudly rather than silently mixing density into
the potential branch or vice versa.

**Input convention.** The density branch reads the flagship's own convention
(`factorized_fourier.Log_Compressed_Channels`, reused rather than reimplemented): the two spin
densities — up and down, not the total and the magnetization — each dynamic-range-compressed by
`log1p(spin / reference_density)`, the reference density fit on the same training block the basis
is. The potential branch reads the two spin potentials, `local_potential_up` and
`local_potential_down`, each with its own spatial mean removed (a potential's absolute gauge
carries no signal; its structure does).

**The two-branch product needs a per-channel split, and that is one small owned array pair.** The
canon states the branches as `SensorEncoder((32, 128, 128))` each, producing one 128-wide latent
per branch, and `BasisExpansion(latent_width=128, ...)` as the shared trunk. `BasisExpansion`'s own
multi-channel form (`readouts/__init__.py`) needs branch coefficients shaped
`(output_channel_count, latent_width)` — one 128-wide row per output channel — because the trunk's
own features are shared across channels and only the branch coefficients tell one predicted channel
from another. A single 128-wide product cannot carry two independent rows, so `TwoBranchEncoder`
owns one more small array pair beyond the two branches and the trunk: `channel_head_weights`
(128 → 256) and `channel_head_biases`, applied to the elementwise product and reshaped to
`(2, 128)` before the trunk reads it. This is the one addition beyond the parts named in the
manifest, and it is why the built member's own parameter count (below) reads a little above what
the two `SensorEncoder((32, 128, 128))` instances and the trunk alone would total.

**The density-alone twin is the multiplicative identity, not a literal ones vector.** Multiplying a
branch's latent by an engine-native constant ones array would need `engine.Lift_Constant` at every
call site to stay correct across both engines. Since multiplying by ones is the identity, the twin
is built by the same `TwoBranchEncoder` class with `potential=None`: the combined latent is simply
the density branch's own latent, unchanged, with no cross-engine constant ever created. The
channel-head weights, the trunk, and the density branch are seeded identically between a member and
its twin built from the same `seed`; only the potential branch's own arrays differ — one is present,
the other absent. `Test_The_Twin_And_The_Member_Share_Every_Array_Name_Except_The_Second_Branch` and
`Test_The_Product_Latent_Reduces_To_The_Branch_Trunk_Form_When_The_Potential_Latent_Is_Constant`
(`operators/tests/test_multiple_input_operator_network.py`) both hold this to account: the second
test forces a real potential branch's own last layer to output a constant ones vector by hand and
confirms the member then matches the twin exactly, which is the algebraic fact the twin's
construction relies on.

**`BasisProjectionEncoder.Inspect()` assumes a single-channel field, and this member's two branches
are both two-channel.** The shared encoder (`operators/encoders/__init__.py`, not owned here)
reshapes its basis mean and modes using `input_function.values.shape[1:]` — the spatial shape
alone — which is exactly right for `deep_operator_network`'s single-channel density field and wrong
here, where the flattened basis covers two spin channels at once and the reshape undercounts by a
factor of two. `Basis_Projection_Inspection` (`__init__.py`) rebuilds the same keys correctly,
splitting the mean and each mode back into one field per channel (`basis_mean_<label>`,
`basis_modes_<label>`) rather than calling the shared method, which would raise. This is a
limitation of a part this package does not own, worth a note to whoever owns `operators/encoders/`
for when another multi-channel POD projection is built; it is not something this package's own
build should silently route around without a record.

## Data and the cubic block

The card is `charge_and_potential_to_localization` (`operators/tasks/__init__.py`), split
`paired_fields_fivefold`. Its examples are not all on one grid: of the units this card can build an
example for, only the ones the canon calls the eighty-cube cubic block — `charge_density` at
`(80, 80, 80)`, `electron_localization_{up,down}` at `(40, 40, 40)` — carry every field this member
needs. Measured directly against the committed fold map: fold 0 (evaluation) 76 runs, fold 1
(validation) 65 runs, folds 2–4 (member training) 196 runs pooled, folds 1–4 pooled (floor and basis
training) 261 runs — the exact counts the canon states.
`operators.evaluation` is expected to promote a `CubicBlock` class carrying this same partition;
until it lands, `operators/multiple_input_operator_network/cache.py` carries its own minimal,
scoped stand-in (`Cubic_Block_Examples`, `EVALUATION_FOLDS`, `VALIDATION_FOLDS`,
`MEMBER_TRAIN_FOLDS`, `FLOOR_TRAIN_FOLDS`), built by calling the existing `Paired_Field_Examples`
once per fold and filtering to the cubic input shape — it duplicates no fold-matching logic, only
the shape guard `CubicBlock.__init__` will also apply. `Fitted_Bases` fits both proper-orthogonal
bases (`operators.data.Gram_Pod`, rank 32) on the pooled 261 floor-training snapshots and reports
the reconstruction-error decay at ranks 8, 16 and 32 beside `Basis_Decay_Gate`'s own verdict — the
POD gate the canon names.

**One cache serves both the member and its twin.** `Localization_Cache` reduces each run to its two
branch coefficient vectors (density basis projection, potential basis projection — the projection
paid once, offline, never inside the training loop) concatenated into one `CachedField.parameters`
vector, beside its `(2, 40, 40, 40)` localization target in single precision. This is a direct reuse
of `operators.training`'s existing `CachedField` / `FieldCache` / `PointSampledBatches` /
`Batch_Of_Fields` machinery, unmodified: `Forward_Point_Values`'s prediction is built by broadcasting
the trunk's per-point features against the branch's per-channel coefficient rows
(`trunk_values[:, :, None, :] * coefficients[:, None, :, :]`, summed over the last axis) rather than
by concatenating per-channel predictions together, which keeps the predicted shape
`(runs, points, channels)` — exactly `Batch_Of_Fields`'s own `target_values` convention — with no
wrapper needed around the shared batch source. Verified end to end against the live corpus during
this build: fitting both bases, building both caches, and drawing a point-sampled batch through a
member's own `Forward_Point_Values` all run unmodified on real archives.

## Floors and kill thresholds

Pre-registered here, before training, per house policy — one seeded run each of the two-branch
member and its density-alone twin, judged against the promoted localization floors on fold 0 of the
cubic block, with a one-seed caveat recorded rather than a false confidence: the built
branch–trunk family measured a 14–35% seed spread on its own floors, so a pass by a small margin is
reported as unresolved on one seed, not as a win.

| floor | mean absolute error |
|---|---|
| semilocal pointwise ridge | 0.0976 |
| per-shell isotropic filter | 0.0830 |
| training-block mean field | 0.0160 |
| nearest-training-run copy | 0.0062 |

**The decisive gate**, `test-suite.md`'s own words: if adding the potential improves on the
density-alone twin by five percent or less, the potential adds nothing and the task is dropped.
Bars, once the member is trained: `Compare_To_Floor(two_branch, density_alone_twin, "mean_absolute_error", "density_alone_twin", 0.05)`
decisive; `Compare_To_Floor(two_branch, semilocal_ridge, "mean_absolute_error", "semilocal_ridge_floor", 0.20)`
the pattern rule; the template (training mean) and copy (nearest run) rows carried as context at
0.0 required improvement, never as a kill.

## Inspection

Everything this member computes, learns or holds is reachable as named plain-word arrays through
`Inspect()`; `Test_Every_Inspect_Key_Renders` confirms every key the member currently produces
reaches a renderer with nothing skipped.

**Each branch** (`encoder.density_branch.*`, `encoder.potential_branch.*` when the potential branch
is present) publishes its own `SensorEncoder`'s weights and biases per layer and the latent vector
it last produced (`...last_latent_vector`). **Each projection**
(`encoder.density_projection.*`, `encoder.potential_projection.*`) publishes its mode norms, its
mean and modes split back into one field per channel (`basis_mean_<label>`,
`basis_modes_<label>` — see the workaround above) and the coefficients it last produced
(`...last_coefficients`). **The encoder itself** publishes the channel-head weights and biases
(`encoder.channel_head_weights`, `encoder.channel_head_biases`) and the combined latent the product
last produced (`encoder.last_combined_latent`) — absent the potential branch, this is the density
branch's own latent, unchanged, which is the twin's identity reduction made visible by name.

**The composition** holds no layers and publishes only the vector it carried through
(`composition.last_carried_vector`). **The readout** publishes the trunk's weights and biases and
the features it last read (`readout.last_trunk_features`), shaped as a field when the query was a
grid. **The member itself** publishes the bounded field it last produced
(`last_predicted_field`), flattened — the physical quantity the non-negative-but-bounded head
exists to make, named rather than only re-derivable by calling the member again, the same
discipline `deep_operator_network`'s `energy_trunk` gives its own non-negative head.

## Standing

Built and tested against synthetic data and, where marked `pool`, the live corpus: the assembly
(`TwoBranchEncoder`, `MultipleInputOperatorNetwork`, `Two_Branch_Member`, `Density_Alone_Twin`), the
basis fitting and the member-local cache (`cache.py`), and the full test suite in
`operators/tests/test_multiple_input_operator_network.py` — the gate contract, the product-reduces-
to-branch-trunk identity, the label-driven channel refusal, the POD round trip, two-path agreement,
gradients on both branches and the trunk on both engines, the twin/member shared-name property, a
deterministic two-step toy training run, the full inspection surface, and the exact 76/65/196 cubic-
block fold counts. The parameter count of the built configuration, measured directly: 245,632 for the
two-branch member, 224,896 for the density-alone twin — both below the canon's own rough estimate of
≈0.6M, the difference in the channel-head addition's own favor (128 → 256 is small next to the
trunk's 171,136).

**`report.py` and `results.json` are built**, now that `operators.evaluation` carries `CubicBlock`,
the four localization floor row builders and `Write_Member_Results`. The four floors are read live
through the promoted package on the cubic block's own evaluation fold — not copied from the table
above — and land within the stated precision (`Test_The_Reports_Own_Floors_Reproduce_The_Recorded_Ladder`,
`pool`); the pattern-rule and context bars are computed from them and written to `report.md` beside
the built configuration's own parameter counts; the four floor summaries are written to
`results.json` through `ResultRow`/`Write_Member_Results`, with no verdicts yet since neither the
member nor its twin has trained. Regenerating is a clean, byte-identical rerun
(`python -m operators.multiple_input_operator_network.report`).

**The staged training driver is written and gated, not run.** `Train_Configuration(step_count,
run_name, twin)` builds either configuration from one code path and trains it through
`operators.training.Staged_Training`, the shared probe-then-three-stage schedule every member now
runs (0.3/0.3/0.4 of the given step count at 1e-3, 3.3e-4, 1.1e-4, validation every hundred steps on
the validation fold, patience fifteen in the final stage, seed 20260916), point-sampled batches
through `PointSampledBatches` and `CoordinateFeaturizedBatches`, checkpoints under
`_training/multiple_input_operator_network/`, every stage resuming its own checkpoint so a power
loss costs the running stage its steps since its last validation pass rather than the whole run.
`Cost_Probe(twin)` (`report.py`, this package) runs a hundred steps on the real batch source and
writes seconds per step and peak accelerator bytes — measured through `operators.substrate`'s own
`Reset_Peak_Accelerator_Bytes`/`Peak_Accelerator_Bytes` facet, never by naming the foreign engine —
to a small json beside the checkpoints, the figure the card holder sizes each one-hour run's
`step_count` from.

**A defect, found and fixed 2026-09-17, before any verdict was written.** The first matched-budget
run (`elf_fold0_member_33650`, void, superseded) never had a working forward pass: its combined
latent (density branch latent times potential branch latent, elementwise) reached a std of 2441.6
against the twin's 1.98, driving the bounded head's pre-activation to the thousands and saturating
`Bounded_Values` to exactly 0.0 everywhere from step one, with zero gradient reaching the loss
through the saturated points — the recorded validation score (0.091299, unmoved to six digits
across all three stages) is what an all-zero prediction scores against this target, not a trained
member. Root cause: `Density_Channels` runs the flagship's `Log_Compressed_Channels`, dynamic-range
compression to O(1); `Potential_Channels` only removed each channel's own spatial mean, leaving the
potential basis's own coefficients in raw physical units — measured at roughly 48x the density
branch's own coefficient scale, which a `SensorEncoder` built and initialized identically to the
density branch (correctly, per this package's own shared-seed convention) carries straight through
to a correspondingly larger latent. **Fix**: `Potential_Coefficient_Statistics` (`cache.py`) fits
each of the potential basis's rank-32 coefficients' own mean and spread across the pooled
floor-training block (the `Parameter_Spreads` zero-spread guard's own idiom, `spread[spread ==
0.0] = 1.0`), and `Standardized_Potential_Coefficients` (`__init__.py`) centers and scales each
coefficient by those training-fold statistics before the potential branch ever reads them — in
`TwoBranchEncoder.__call__` for the numpy inference path and in `Localization_Cache` for the cached
coefficients training reads, so the fix reaches both from the same one change. The density path is
untouched by design, so the twin's already-trained checkpoint (`elf_fold0_twin_33650`) stands
unmodified and the two networks still share an identical density branch. The statistics are
constants fit once on the training folds and reproduced deterministically by `Fitted_Bases`,
exactly like the POD basis itself — no separate persistence needed.
`Test_A_Fresh_Init_Does_Not_Saturate_The_Bounded_Head_On_Real_Scale_Input`
(`test_multiple_input_operator_network.py`, `pool`) pins it: on real-scale input at a fresh init,
the bounded head lands strictly inside `(0, 1)`, the two branches' own latent scales stay within a
couple of orders of magnitude of each other (density's log-compressed-but-not-z-scored input and
potential's now-unit-variance-per-coefficient input are two different, both legitimate conventions,
so they do not land at the identical scale — the bound instead rules out the measured bug, a 55x
branch-latent gap that saturated the head), and gradient reaches both branches through
`Training_Engine`. A host sanity check (300 steps, `learning_rate=1e-3`, card hidden) confirmed the
fix trains: validation score 0.076946 at step 25, falling every checkpoint after (one wobble, step
150 to 175) to 0.015901 at step 300 — below the all-zero baseline (0.0913) from the first checkpoint
and still falling at the run's end, not a plateau. **Not yet run**: the member's own matched retrain
under the fix (`elf_fold0_member_v2_33650`) and therefore the decisive gate — scheduled on the card.

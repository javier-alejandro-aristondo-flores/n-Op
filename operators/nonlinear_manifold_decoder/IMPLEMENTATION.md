# nonlinear_manifold_decoder — strain or lattice parameters → charge density field

Decoded point by point.

**Operator.** NOMAD — Seidman, Kissas, Perdikaris, Pappas, NeurIPS 2022 (arXiv:2206.03551).
Suite entry: `test-suite.md` §3, II.3.

## What it assembles

Sensor encoder → dense layers → nonlinear decoder: the output at a point is a nonlinear function
of (latent, position).

## Why it is shaped this way

**It breaks the linear-reconstruction ceiling.** Every basis-expansion readout writes the output
as a linear combination of fixed or learned modes, and that caps how well a solution manifold with
sharp parameter dependence can be represented. This decoder is the named alternative.

**It is also why readouts are plain operators.** Its output is not an integral and not a linear
combination — a stricter readout abstraction would have had to special-case it. The framework's
looser interface absorbs it without a seam.

**Restricted to parametric tasks.** Its global latent is a bottleneck for field-to-field maps
with half a million input points; the potential task is permitted only as a kill-gated baseline.

## Floors and kill thresholds

Beat radial-basis and linear interpolation in parameter space by a factor of one and a half. The
operator badge is earned on grid transfer: error inflation at most 1.3× when evaluated on the
strain campaign's off-dominant grid shapes.

## Implementation specification

**Built.** `SensorEncoder((7, 256, 256, 128))` reads the six standardized strain components plus a
seventh branch feature (0.0 cheap, 1.0 accurate, both functionals pooled in one training set) into
a 128-wide latent → `WithoutIntegralLayers()` carries it unchanged (the branch-trunk family's own
zero-kernel composition, `operators/README.md` "Zero kernel layers is legitimate") →
`NonlinearDecoder(128, (256, 256, 256), PeriodicCoordinateFeatures(4))` reads a query point's own
25-wide coordinate features concatenated with the run's broadcast latent through a four-layer
perceptron, one channel, GELU between hidden layers. 272,001 parameters. Assembled as
`NonlinearManifoldDecoder`, whose `Forward_Point_Values(lifted, branch_input, trunk_features)`
broadcasts each batched run's own latent onto its own sampled points by concatenation along the
feature axis (`Concatenate_Channels` after swapping the feature axis to the front and back), never
a dot product — the seam that keeps the readout from collapsing into a basis expansion under a
different name (`Test_The_Decoder_Is_Not_Expressible_As_A_Linear_Map_Of_Its_Latent`).

**Task.** `strain_to_charge` (test-suite.md §3, II.1a) on the `strain_atlas_holdout` split, trained
point-sampled on every grid shape at once (`Build_Field_Cache` pools both functionals; each cached
field's own parameters gain the seventh branch feature before `PointSampledBatches` draws runs and
points, `CoordinateFeaturizedBatches` answering each drawn point's own trunk features). Loss: mean
squared error on globally standardized density values at the sampled points. Staged Adam schedule
(3e-3 → 1e-3 → 3e-4, 3000/3000/4000 steps, patience 15 on the final stage), seed 20260916, single
precision, checkpoints under `_training/nonlinear_manifold_decoder/`. Run cap 1.5 h.

**Floors, host-measured before training (`operators/nonlinear_manifold_decoder/report.py`).**
Reusing the parametric arm machinery (`Arm`, `All_Strain_Arms`, `Interior_Levels`,
`Bracket_Corners` transitively, `Strain_Level` transitively) exported from
`operators.factorized_fourier`: every strain-atlas level with a full bracket is an evaluation
point, every other level trains. Two kill floors, both scored at the level's own mean field over
whatever functional variants share it: **bracketing multilinear interpolation** between a level's
bracket corners (measured median 0.0911% relative L2 over 423 interior levels, seven families),
and a **member-local Gaussian radial-basis interpolant** on standardized six-vectors (bandwidth =
median pairwise distance between training centers, ridge-regularized solve; measured median
0.0991%). Both floors need beating by a third (the canon's 1.5× restated as a fractional
improvement). Ridge-to-tensor (0.4225%) and nearest-run copy (1.988%) are recorded for context,
not gated. **No canon escalation rung is defined for this entry**; a miss on the bracketing floor
is the terminal clause — the entry is marked a dead end, with the grid-transfer ratio still
reported regardless (the canon's own instruction). Grid transfer: the trained member's own error on
the strain atlas's off-dominant grid shapes against its own error on the dominant 40³ shape (248
pooled test runs, 176 at 40³, 72 spread over eight other shapes); improvement must not fall below
−0.3 (at most 1.3× inflation).

**Results.** `operators/nonlinear_manifold_decoder/results.json`, written by
`operators.evaluation.Write_Member_Results`: rows over three blocks (`arm_leave_one_level_out`,
`committed_test_split`, `every_shape_test_split`), verdicts for the two kill floors and the
transfer bar, keyed by `ResultKey(member, configuration="canonical", task="strain_to_charge",
split="strain_atlas_holdout", block, group)`.

## Inspection

`NonlinearManifoldDecoder.Inspect()` is the base `NeuralOperator` aggregation, three prefixes:
- `encoder.*` — `SensorEncoder`'s own perceptron weights and biases (`sensor_encoder_layer_*`), and
  `encoder.last_latent_vector` (the branch's own 128-wide output, after the last call).
- `composition.*` — `WithoutIntegralLayers.Inspect()`'s `composition.last_carried_vector` (the
  latent passed through unchanged, so the layerless seam is itself inspectable).
- `readout.*` — `NonlinearDecoder`'s own perceptron weights and biases (`decoder_layer_*`), and
  `readout.last_point_features` (the query's own 25-wide coordinate features, reshaped to the
  query grid's own shape when the query was a `GridSpec`).

Every key is a named plain-word array (weight matrices, bias vectors, the two capture vectors);
`Render_Inspection_Suite` draws the whole assembly from this dict alone
(`Test_Every_Inspection_Key_Has_A_Renderer`). Training curves and per-stage manifests are recorded
by the shared trainer (`operators.training.Train`) under `_training/nonlinear_manifold_decoder/`
and are not duplicated here.

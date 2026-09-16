"""the multiple-input member's assembly, its parameters and its path through the engine"""

import tomllib
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.data import Gram_Pod, Project
from operators.encoders import BasisProjectionEncoder, SensorEncoder
from operators.evaluation import Compare_To_Floor, CubicBlock, ScoredRun
from operators.framework import (
    Domain,
    Fractional_Grid_Coordinates,
    GridFunction,
    GridSpec,
    PointSet,
    PointSpec,
    UniformGridQuadrature,
)
from operators.inspection import Render_Inspection_Suite
from operators.multiple_input_operator_network import (
    Bounded_Values,
    Density_Alone_Twin,
    Density_Channels,
    INPUT_DENSITY_LABELS,
    INPUT_POTENTIAL_LABELS,
    Labeled_Channel,
    MultipleInputOperatorNetwork,
    OUTPUT_CHANNEL_LABELS,
    Potential_Channels,
    Two_Branch_Member,
    TwoBranchEncoder,
)
from operators.multiple_input_operator_network.cache import (
    Cubic_Block_Examples,
    EVALUATION_FOLDS,
    Fitted_Bases,
    Localization_Cache,
    MEMBER_TRAIN_FOLDS,
    VALIDATION_FOLDS,
)
from operators.multiple_input_operator_network.report import Floor_Summaries
from operators.readouts import BasisExpansion, PeriodicCoordinateFeatures
from operators.substrate import Accelerator_Is_Available, Adam_Step, Fresh_Adam_State, NumpyEngine, ParameterSet
from operators.tasks import Card_Named
from operators.training import PointSampledBatches, Training_Engine

CUBE = Domain(lattice=np.eye(3) * 3.57)

GRID = (4, 4, 4)

# the density and potential branches both read two stacked spin channels off this same small grid
GRID_FEATURE_COUNT = 2 * GRID[0] * GRID[1] * GRID[2]

MANIFEST_PATH = Path(__file__).resolve().parent.parent / "multiple_input_operator_network" / "manifest.toml"


def Small_Pod_Basis(feature_count: int, rank: int, seed: int) -> Any:
    """a basis fit on random snapshots, large enough to reach the requested rank"""
    generator = np.random.default_rng(seed)
    snapshots = np.asarray(generator.normal(size=(rank + 6, feature_count)), dtype=np.float64)
    return Gram_Pod(snapshots, rank=rank)


def Synthetic_Input_Field(seed: int, grid_shape: tuple[int, int, int] = GRID) -> GridFunction:
    """a small four-channel field carrying the labels the member's branches read"""
    generator = np.random.default_rng(seed)
    density = generator.random(grid_shape) + 0.5
    magnetization = generator.normal(size=grid_shape) * 0.01
    potential_up = generator.normal(size=grid_shape)
    potential_down = generator.normal(size=grid_shape)
    values = np.stack([density, magnetization, potential_up, potential_down])
    point_count = grid_shape[0] * grid_shape[1] * grid_shape[2]
    quadrature = UniformGridQuadrature(cell_volume=3.57**3, point_count=point_count)
    return GridFunction(values, INPUT_DENSITY_LABELS + INPUT_POTENTIAL_LABELS, CUBE, quadrature)


def Small_Two_Branch_Member(
    density_rank: int = 4, potential_rank: int = 3, latent_width: int = 5, seed: int = 0
) -> MultipleInputOperatorNetwork:
    """a tiny two-branch member, enough to assemble and differentiate quickly"""
    density_basis = Small_Pod_Basis(GRID_FEATURE_COUNT, density_rank, seed=101)
    potential_basis = Small_Pod_Basis(GRID_FEATURE_COUNT, potential_rank, seed=102)
    density_projection = BasisProjectionEncoder(density_basis.modes, density_basis.mean)
    density_branch = SensorEncoder((density_rank, 6, latent_width), seed=seed)
    potential_projection = BasisProjectionEncoder(potential_basis.modes, potential_basis.mean)
    # the potential branch is seeded one past the density branch, so the two draws never share a stream
    potential_branch = SensorEncoder((potential_rank, 6, latent_width), seed=seed + 1)
    potential = (potential_projection, potential_branch)
    encoder = TwoBranchEncoder(density_projection, density_branch, potential, reference_density=1.0, seed=seed + 2)
    readout = BasisExpansion(
        latent_width, (6,), PeriodicCoordinateFeatures(fourier_orders=1), OUTPUT_CHANNEL_LABELS, seed=seed + 3
    )
    return MultipleInputOperatorNetwork(encoder, readout)


def Small_Density_Alone_Twin(
    density_rank: int = 4, latent_width: int = 5, seed: int = 0
) -> MultipleInputOperatorNetwork:
    """a tiny density-alone twin, its density branch and trunk seeded exactly as a matching member's own"""
    density_basis = Small_Pod_Basis(GRID_FEATURE_COUNT, density_rank, seed=101)
    density_projection = BasisProjectionEncoder(density_basis.modes, density_basis.mean)
    density_branch = SensorEncoder((density_rank, 6, latent_width), seed=seed)
    encoder = TwoBranchEncoder(density_projection, density_branch, None, reference_density=1.0, seed=seed + 2)
    readout = BasisExpansion(
        latent_width, (6,), PeriodicCoordinateFeatures(fourier_orders=1), OUTPUT_CHANNEL_LABELS, seed=seed + 3
    )
    return MultipleInputOperatorNetwork(encoder, readout)


def Small_Point_Sampled_Batch(
    member: MultipleInputOperatorNetwork, input_width: int, runs: int, points_per_run: int, seed: int
) -> tuple[dict[str, Any], dict[str, Any]]:
    """a synthetic point-sampled batch and the trunk features the member's own coordinate map reads off it"""
    generator = np.random.default_rng(seed)
    parameter_vectors = np.asarray(generator.normal(size=(runs, input_width)), dtype=np.float64)
    raw_points = generator.random(size=(runs, points_per_run, 3))
    flat_features = member.trunk_readout.Coordinate_Features(raw_points.reshape(-1, 3))
    trunk_features = flat_features.reshape(runs, points_per_run, -1)
    targets = np.asarray(generator.random(size=(runs, points_per_run, len(OUTPUT_CHANNEL_LABELS))), dtype=np.float64)
    batch = {"parameters": parameter_vectors, "trunk_features": trunk_features, "targets": targets}
    return batch, batch


def Point_Loss(member: MultipleInputOperatorNetwork, lifted: dict[str, Any], batch: dict[str, Any]) -> Any:
    """the mean squared residual of the member's point-sampled forward against a batch's own targets"""
    predicted = member.Forward_Point_Values(lifted, batch["parameters"], batch["trunk_features"])
    residuals = predicted - batch["targets"]
    return (residuals * residuals).mean()


def Test_The_Member_Reads_Out_A_Field_On_The_Requested_Grid() -> None:
    """the four-channel field in, a two-channel bounded field of the asked-for shape out"""
    member = Small_Two_Branch_Member(seed=1)
    produced = member(Synthetic_Input_Field(1), GridSpec((3, 3, 3)))
    assert isinstance(produced, GridFunction)
    assert np.asarray(produced.values).shape == (2, 3, 3, 3)
    assert produced.channel_labels == OUTPUT_CHANNEL_LABELS


def Test_The_Bounded_Head_Never_Touches_Either_End_Of_Zero_To_One() -> None:
    """the localization head is a probability-shaped field, strictly inside its own range"""
    member = Small_Two_Branch_Member(seed=2)
    produced = member(Synthetic_Input_Field(2), GridSpec((3, 3, 3)))
    assert isinstance(produced, GridFunction)
    values = np.asarray(produced.values)
    assert np.all(values > 0.0) and np.all(values < 1.0)


def Test_Bounded_Values_Stays_Strictly_Between_Zero_And_One() -> None:
    """the bounded head's own formula never touches either end of its range, at ordinary pre-activation scales"""
    generator = np.random.default_rng(3)
    raw_values = generator.normal(scale=3.0, size=1000)
    bounded = Bounded_Values(raw_values)
    assert np.all(bounded > 0.0) and np.all(bounded < 1.0)


def Test_Labeled_Channel_Returns_The_Named_Channels_Own_Values() -> None:
    """the channel returned is exactly the one values row under the requested label, nothing reordered"""
    field = Synthetic_Input_Field(4)
    density_values = Labeled_Channel(field, "charge_density")
    assert np.array_equal(density_values, np.asarray(field.values)[0])
    potential_down_values = Labeled_Channel(field, "local_potential_down")
    assert np.array_equal(potential_down_values, np.asarray(field.values)[3])


def Test_Density_Channels_Refuses_A_Field_With_No_Charge_Density_Label() -> None:
    """a field missing the labeled density channels is refused rather than silently misread"""
    field = Synthetic_Input_Field(5)
    mislabeled = GridFunction(field.values, ("a", "b", "c", "d"), field.domain, field.quadrature)
    with pytest.raises(ValueError):
        Density_Channels(mislabeled, reference_density=1.0)


def Test_Potential_Channels_Refuses_A_Field_With_No_Potential_Labels() -> None:
    """a field missing the labeled potential channels is refused rather than silently misread"""
    field = Synthetic_Input_Field(6)
    mislabeled = GridFunction(
        field.values, ("charge_density", "magnetization_density", "x", "y"), field.domain, field.quadrature
    )
    with pytest.raises(ValueError):
        Potential_Channels(mislabeled)


def Test_The_Encoder_Refuses_Two_Branches_With_Different_Latent_Widths() -> None:
    """a product between mismatched latent widths has no defined meaning, and the encoder says so"""
    density_basis = Small_Pod_Basis(12, 4, seed=201)
    potential_basis = Small_Pod_Basis(12, 4, seed=202)
    density_projection = BasisProjectionEncoder(density_basis.modes, density_basis.mean)
    density_branch = SensorEncoder((4, 6, 5), seed=0)
    potential_projection = BasisProjectionEncoder(potential_basis.modes, potential_basis.mean)
    potential_branch = SensorEncoder((4, 6, 7), seed=1)
    with pytest.raises(ValueError):
        TwoBranchEncoder(
            density_projection, density_branch, (potential_projection, potential_branch), reference_density=1.0
        )


def Test_The_Member_Collects_Every_Learned_Array_Under_One_Namespace() -> None:
    """both branches, the channel head and the trunk all land in one flat dict with no name collisions"""
    member = Small_Two_Branch_Member(seed=7)
    collected = member.Parameter_Values()
    density_names = [name for name in collected if name.startswith("density_branch.")]
    potential_names = [name for name in collected if name.startswith("potential_branch.")]
    assert density_names and potential_names
    assert "channel_head_weights" in collected and "channel_head_biases" in collected
    assert any(name.startswith("trunk_") for name in collected)
    assert not np.allclose(collected["density_branch.sensor_encoder_layer_0_weights"], 0.0)
    assert not np.allclose(collected["potential_branch.sensor_encoder_layer_0_weights"], 0.0)


def Test_The_Member_Inspects_Under_Part_Prefixes() -> None:
    """an assembled member is one flat browsable namespace, each key naming its owner"""
    member = Small_Two_Branch_Member(seed=8)
    member(Synthetic_Input_Field(8), GridSpec((3, 3, 3)))
    inspected = member.Inspect()
    assert any(name.startswith("encoder.density_branch.") for name in inspected)
    assert any(name.startswith("encoder.potential_branch.") for name in inspected)
    assert any(name.startswith("readout.") for name in inspected)
    assert "composition.last_carried_vector" in inspected
    assert "last_predicted_field" in inspected


def Test_Every_Inspect_Key_Renders(tmp_path: Path) -> None:
    """nothing the member exposes for inspection is left without a renderer"""
    member = Small_Two_Branch_Member(seed=9)
    member(Synthetic_Input_Field(9), GridSpec((3, 3, 3)))
    inspected = member.Inspect()
    numeric = {name: np.asarray(value, dtype=np.float64) for name, value in inspected.items()}
    suite = Render_Inspection_Suite(numeric, tmp_path, "member")
    assert suite.skipped == ()
    assert len(suite.written) == len(inspected)


def Test_The_Twin_And_The_Member_Share_Every_Array_Name_Except_The_Second_Branch() -> None:
    """the density branch, the channel head and the trunk are named identically, only the potential branch differs"""
    member = Small_Two_Branch_Member(seed=10)
    twin = Small_Density_Alone_Twin(seed=10)
    member_names = set(member.Parameter_Values())
    twin_names = set(twin.Parameter_Values())
    only_in_member = member_names - twin_names
    assert twin_names <= member_names
    assert only_in_member and all(name.startswith("potential_branch.") for name in only_in_member)


def Test_The_Product_Latent_Reduces_To_The_Branch_Trunk_Form_When_The_Potential_Latent_Is_Constant() -> None:
    """forcing the potential branch to output a constant ones vector reproduces the density-alone twin exactly"""
    member = Small_Two_Branch_Member(seed=11)
    twin = Small_Density_Alone_Twin(seed=11)
    encoder = member.branch_encoder
    assert encoder.potential is not None
    _, potential_branch = encoder.potential
    last_layer_index = len(potential_branch.network.layer_widths) - 2
    potential_branch.parameter_values[f"sensor_encoder_layer_{last_layer_index}_weights"][...] = 0.0
    potential_branch.parameter_values[f"sensor_encoder_layer_{last_layer_index}_biases"][...] = 1.0
    field = Synthetic_Input_Field(11)
    member_result = member(field, GridSpec((3, 3, 3)))
    twin_result = twin(field, GridSpec((3, 3, 3)))
    assert isinstance(member_result, GridFunction)
    assert isinstance(twin_result, GridFunction)
    assert np.allclose(np.asarray(member_result.values), np.asarray(twin_result.values), atol=1e-9)


def Test_Pod_Projections_Round_Trip_At_The_Gates_Rank() -> None:
    """a coefficient vector the projection computes exactly matches the basis's own closed-form projection"""
    generator = np.random.default_rng(12)
    snapshots = np.asarray(generator.normal(size=(12, 40)), dtype=np.float64)
    basis = Gram_Pod(snapshots, rank=12)
    projection = BasisProjectionEncoder(basis.modes, basis.mean)
    for snapshot in snapshots[:3]:
        exact = Project(basis, snapshot[None, :])[0]
        field = GridFunction(snapshot.reshape(2, 4, 5), ("a", "b"), CUBE, UniformGridQuadrature(1.0, 20))
        produced = projection(field, GridSpec((4, 5, 1)))
        assert np.allclose(np.asarray(produced.vector), exact, atol=1e-8)


def Test_A_Grid_Query_Agrees_With_The_Same_Points_Asked_For_Explicitly() -> None:
    """the trunk answers a grid and the same points asked for explicitly with identical values"""
    member = Small_Two_Branch_Member(seed=13)
    field = Synthetic_Input_Field(13)
    shape = (3, 4, 2)
    grid_result = member(field, GridSpec(shape))
    point_result = member(field, PointSpec(points=Fractional_Grid_Coordinates(shape)))
    assert isinstance(grid_result, GridFunction)
    assert isinstance(point_result, PointSet)
    gridded_values = np.asarray(grid_result.values).reshape(2, -1).T
    assert point_result.values is not None
    assert np.allclose(np.asarray(point_result.values), gridded_values, atol=1e-10)


def Test_Gradients_Reach_Every_Branch_And_Trunk_Array_Through_The_Point_Sampled_Forward() -> None:
    """the point-sampled loss the trainer will use differentiates onto both branches and the trunk"""
    member = Small_Two_Branch_Member(seed=14)
    _, lifted_batch = Small_Point_Sampled_Batch(member, input_width=4 + 3, runs=3, points_per_run=4, seed=24)
    gradients = NumpyEngine().Gradients(
        ParameterSet(values=member.Parameter_Values()), lambda lifted: Point_Loss(member, lifted, lifted_batch)
    )
    assert set(gradients) == set(member.Parameter_Values())
    assert any(name.startswith("density_branch.") for name in gradients)
    assert any(name.startswith("potential_branch.") for name in gradients)
    assert any(name.startswith("trunk_") for name in gradients)
    assert all(np.isfinite(gradient).all() for gradient in gradients.values())
    assert all(np.abs(gradient).max() > 0.0 for gradient in gradients.values())


def Test_Gradients_Reach_The_Twins_Arrays_With_No_Potential_Branch_Present() -> None:
    """the twin differentiates on exactly its own arrays, with no second branch to reach"""
    twin = Small_Density_Alone_Twin(seed=15)
    _, lifted_batch = Small_Point_Sampled_Batch(twin, input_width=4, runs=3, points_per_run=4, seed=25)
    gradients = NumpyEngine().Gradients(
        ParameterSet(values=twin.Parameter_Values()), lambda lifted: Point_Loss(twin, lifted, lifted_batch)
    )
    assert set(gradients) == set(twin.Parameter_Values())
    assert not any(name.startswith("potential_branch.") for name in gradients)
    assert all(np.isfinite(gradient).all() for gradient in gradients.values())
    assert all(np.abs(gradient).max() > 0.0 for gradient in gradients.values())


@pytest.mark.skipif(not Accelerator_Is_Available(), reason="no card on this machine answers a lift")
def Test_Gradients_Reach_The_Member_On_The_Card() -> None:
    """the point-sampled loss differentiates onto the whole member through the accelerator, in single precision"""
    member = Small_Two_Branch_Member(seed=16)
    batch, _ = Small_Point_Sampled_Batch(member, input_width=4 + 3, runs=3, points_per_run=4, seed=26)
    engine = Training_Engine()
    lifted_batch = {name: engine.Lift_Constant(array) for name, array in batch.items()}

    loss_value, gradients = engine.Value_And_Gradients(
        ParameterSet(values=member.Parameter_Values()), lambda lifted: Point_Loss(member, lifted, lifted_batch)
    )
    assert np.isfinite(loss_value)
    assert set(gradients) == set(member.Parameter_Values())
    assert all(np.isfinite(gradient).all() for gradient in gradients.values())
    assert all(np.abs(gradient).max() > 0.0 for gradient in gradients.values())


def Toy_Training_Losses(seed: int) -> NDArray[np.float64]:
    """the loss after two Adam steps on a fixed synthetic batch, from a freshly built member"""
    member = Small_Two_Branch_Member(seed=seed)
    _, lifted_batch = Small_Point_Sampled_Batch(member, input_width=4 + 3, runs=2, points_per_run=3, seed=seed + 1)
    engine = NumpyEngine()
    parameters = ParameterSet(values=member.Parameter_Values())
    adam_state = Fresh_Adam_State(parameters)
    losses: list[float] = []
    for _ in range(2):
        loss_value, gradients = engine.Value_And_Gradients(
            parameters, lambda lifted: Point_Loss(member, lifted, lifted_batch)
        )
        losses.append(loss_value)
        parameters = Adam_Step(parameters, gradients, adam_state, learning_rate=0.01)
    return np.asarray(losses, dtype=np.float64)


def Test_A_Two_Step_Toy_Training_Run_Is_Deterministic() -> None:
    """the same seed reproduces the same loss curve bit for bit"""
    first = Toy_Training_Losses(seed=40)
    second = Toy_Training_Losses(seed=40)
    assert np.array_equal(first, second)
    assert np.isfinite(first).all()


def Test_The_Manifest_Names_The_Parts_The_Member_Actually_Assembles() -> None:
    """a manifest is a description of the code, and a description that drifts is fiction"""
    manifest = tomllib.loads(MANIFEST_PATH.read_text())
    assert "WithoutIntegralLayers" in manifest["parts"]["composition"]
    assert manifest["parts"]["kernel"].startswith("none")
    assert manifest["depends_on"]["kernels"] == []
    assert "BasisExpansion" in manifest["parts"]["readout"]
    assert "factorized_fourier" in manifest["depends_on"]["packages"]


def Test_The_Task_Card_Names_The_Inputs_And_Targets_The_Cache_Expects() -> None:
    """the committed task card still names the four inputs and two targets the cache and model assume"""
    card = Card_Named("charge_and_potential_to_localization")
    assert card.inputs == ("charge_density", "magnetization_density", "local_potential_up", "local_potential_down")
    assert card.targets == OUTPUT_CHANNEL_LABELS
    assert card.split == "paired_fields_fivefold"


def Test_The_Kill_Bar_Requires_More_Than_Five_Percent_Improvement_Over_The_Twin() -> None:
    """the canon's own kill: adding the potential must beat the density-alone twin by more than five percent"""
    two_branch_rows = [ScoredRun("a", "unit", "defect_set", "up", {"mean_absolute_error": 0.094})]
    density_alone_rows = [ScoredRun("b", "unit", "defect_set", "up", {"mean_absolute_error": 0.0976})]
    comparison = Compare_To_Floor(
        two_branch_rows, density_alone_rows, "mean_absolute_error", "density_alone_twin", 0.05
    )
    assert comparison.verdict == "kill"
    two_branch_strong_rows = [ScoredRun("a", "unit", "defect_set", "up", {"mean_absolute_error": 0.05})]
    comparison_pass = Compare_To_Floor(
        two_branch_strong_rows, density_alone_rows, "mean_absolute_error", "density_alone_twin", 0.05
    )
    assert comparison_pass.verdict == "pass"


@pytest.mark.pool
def Test_The_Cubic_Block_Filter_Keeps_Only_Eighty_Cube_Runs() -> None:
    """every yielded example carries the four-channel eighty-cube input shape the cache assumes"""
    examples = list(Cubic_Block_Examples((0,), limit=20))
    assert examples
    assert all(example.input_function.values.shape == (4, 80, 80, 80) for example in examples)
    assert all(example.target_function.values.shape == (2, 40, 40, 40) for example in examples)


@pytest.mark.pool
def Test_The_Cubic_Block_Fold_Counts_Match_The_Canon() -> None:
    """the eighty-cube cubic block splits into the exact fold sizes the canon records"""
    assert len(list(Cubic_Block_Examples(EVALUATION_FOLDS))) == 76
    assert len(list(Cubic_Block_Examples(VALIDATION_FOLDS))) == 65
    assert len(list(Cubic_Block_Examples(MEMBER_TRAIN_FOLDS))) == 196


@pytest.mark.pool
def Test_The_Built_Configurations_Match_Their_Own_Parameter_Counts() -> None:
    """the member and its twin, built from bases fit on the live corpus, carry the exact counts IMPLEMENTATION.md records"""
    density_basis, potential_basis, reference_density, _ = Fitted_Bases(limit=40)
    member = Two_Branch_Member(density_basis, potential_basis, reference_density, seed=0)
    twin = Density_Alone_Twin(density_basis, reference_density, seed=0)
    member_parameter_count = sum(value.size for value in member.Parameter_Values().values())
    twin_parameter_count = sum(value.size for value in twin.Parameter_Values().values())
    assert member_parameter_count == 245_632
    assert twin_parameter_count == 224_896


@pytest.mark.pool
def Test_The_Reports_Own_Floors_Reproduce_The_Recorded_Ladder() -> None:
    """report.py's floor rows, read live through operators.evaluation, land near IMPLEMENTATION.md's own table"""
    block = CubicBlock()
    ridge_summary, filter_summary, mean_summary, copy_summary, _ = Floor_Summaries(block)
    assert ridge_summary.median == pytest.approx(0.0976, rel=0.02)
    assert filter_summary.median == pytest.approx(0.0830, rel=0.02)
    assert mean_summary.median == pytest.approx(0.0160, rel=0.05)
    assert copy_summary.median == pytest.approx(0.0062, rel=0.05)


@pytest.mark.pool
def Test_Fitted_Bases_Reports_A_Decay_Curve_And_A_Gate_Verdict() -> None:
    """a small fit still returns a basis at the eighty-cube feature width and a well-formed decay report"""
    density_basis, potential_basis, reference_density, decay = Fitted_Bases(limit=10)
    assert density_basis.modes.shape[1] == 2 * 80 * 80 * 80
    assert potential_basis.modes.shape[1] == 2 * 80 * 80 * 80
    assert reference_density > 0.0
    for report in decay.values():
        assert 0.0 <= report["gate_passed"] <= 1.0
        assert report["gate_reached_rank"] >= 1.0


@pytest.mark.pool
def Test_The_Cache_Feeds_Point_Sampled_Batches_Of_The_Built_Members_Own_Shape() -> None:
    """the member-local cache is a drop-in FieldCache, and point-sampled batches come from it unmodified"""
    density_basis, potential_basis, reference_density, _ = Fitted_Bases(limit=10)
    train_cache = Localization_Cache(
        MEMBER_TRAIN_FOLDS, density_basis, potential_basis, reference_density, "training", limit=30
    )
    validation_cache = Localization_Cache(
        VALIDATION_FOLDS, density_basis, potential_basis, reference_density, "validation", limit=30
    )
    assert train_cache.fields and validation_cache.fields
    batch_source = PointSampledBatches(train_cache, validation_cache, runs_per_batch=2, points_per_run=8)
    batch = batch_source.Next_Batch(np.random.default_rng(1))
    density_rank = density_basis.modes.shape[0]
    potential_rank = potential_basis.modes.shape[0]
    assert batch.arrays["parameter_vectors"].shape == (2, density_rank + potential_rank)
    assert batch.arrays["point_coordinates"].shape == (2, 8, 3)
    assert batch.arrays["target_values"].shape == (2, 8, 2)
    assert batch_source.Validation_Batches()

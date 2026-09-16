"""the residual correction member: zero-initialization, conservation, gradients and the calibrator"""

from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.data import (
    Gram_Pod,
    Guard_Fresh_Archives,
    Identity_And_Affine_Floors,
    Load_Field,
    POOL_ROOT,
    Project,
    Read_Census,
    Strain_Pairs,
)
from operators.framework import Domain, GridFunction, GridSpec, Inspectable, Operator, UniformGridQuadrature
from operators.inspection import Render_Inspection_Suite
from operators.metrics import Delta_R_Squared, Median_And_Interquartile
from operators.residual_correction import (
    BASIS_RANK,
    Guarded_Spread,
    Projection_Backbone_Member,
    ResidualCorrection,
    Zero_Anchored,
)
from operators.substrate import Adam_Step, Fresh_Adam_State, NumpyEngine, ParameterSet, Torch_Is_Available, TorchEngine
from operators.wrappers import ConformalCalibrator, Coverage_Deviation, Coverage_Guarantee

CUBE = Domain(lattice=np.eye(3) * 3.57)
GRID_SHAPE = (4, 4, 4)
VOXEL_COUNT = 4 * 4 * 4
QUADRATURE = UniformGridQuadrature(cell_volume=45.5, point_count=VOXEL_COUNT)

# measured on the real strain atlas (operators/stage0-report.md), the target this toy-block test guards
STAGE0_IDENTITY_MEDIAN = 0.01117
STAGE0_AFFINE_MEDIAN = 0.01050


def Toy_Block(
    pair_count: int, seed: int, correction_scale: float = 0.01
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """flattened cheap fields beside a small, unrelated correction field, over one toy block"""
    generator = np.random.default_rng(seed)
    cheap_fields = generator.normal(size=(pair_count, VOXEL_COUNT))
    correction_fields = generator.normal(size=(pair_count, VOXEL_COUNT)) * correction_scale
    return cheap_fields, correction_fields


def Toy_Member(
    pair_count: int = 20, seed: int = 5, correction_scale: float = 0.01
) -> tuple[ResidualCorrection, NDArray[np.float64], NDArray[np.float64]]:
    """a member built on a toy block, beside the block it was fit from"""
    cheap_fields, correction_fields = Toy_Block(pair_count, seed, correction_scale)
    member = Projection_Backbone_Member(cheap_fields, correction_fields, GRID_SHAPE, seed=seed)
    return member, cheap_fields, correction_fields


def Grid_Function_Of(values: NDArray[np.float64]) -> GridFunction:
    """one flat field wrapped as a single-channel grid function on the toy cell"""
    return GridFunction(values.reshape(1, *GRID_SHAPE), ("charge_density",), CUBE, QUADRATURE)


def Lone_Orbits(count: int) -> list[str]:
    """one exchangeable unit per run, the loosest the calibrator is ever given"""
    return [f"orbit_{place}" for place in range(count)]


def Lifted_Loss(
    member: ResidualCorrection, engine: Any, cheap_coefficients: Any, true_correction: Any
) -> Any:
    """a coefficient-regression loss closed over one engine's own lifted constants"""
    lifted_constants = {name: engine.Lift_Constant(value) for name, value in member.Constant_Values().items()}

    def Loss(lifted: dict[str, Any]) -> Any:
        full_lifted = dict(lifted)
        full_lifted.update(lifted_constants)
        predicted = member.Forward_Correction(full_lifted, cheap_coefficients)
        residuals = predicted - true_correction
        return (residuals * residuals).mean()

    return Loss


def Test_The_Member_Answers_The_Inspection_Contract() -> None:
    """a constructed member is no longer the stub, and inherits both behavioral contracts"""
    member, _, _ = Toy_Member()
    assert Operator in type(member).__mro__
    assert Inspectable in type(member).__mro__
    inspected = member.Inspect()
    assert bool(np.asarray(inspected["zero_initialized_at_construction"]))
    assert "backbone.branch.sensor_encoder_layer_2_weights" in inspected
    assert "cheap_basis_singular_values" in inspected
    assert "correction_basis_singular_values" in inspected


def Test_Zero_Anchored_Keeps_The_Modes_And_Forces_The_Mean_To_The_Origin() -> None:
    """the operational basis differs from the fitted one in exactly one field"""
    _, correction_fields = Toy_Block(20, 11)
    fitted = Gram_Pod(correction_fields, rank=BASIS_RANK)
    anchored = Zero_Anchored(fitted)
    assert np.allclose(anchored.modes, fitted.modes)
    assert np.allclose(anchored.singular_values, fitted.singular_values)
    assert np.allclose(anchored.mean, 0.0)
    assert not np.allclose(fitted.mean, 0.0)


def Test_The_Last_Layer_Alone_Starts_At_Zero() -> None:
    """the branch's earlier layers keep their random draw, only its final layer is zeroed"""
    member, _, _ = Toy_Member()
    branch = member.backbone.branch
    assert not np.allclose(branch.parameter_values["sensor_encoder_layer_0_weights"], 0.0)
    assert not np.allclose(branch.parameter_values["sensor_encoder_layer_1_weights"], 0.0)
    assert np.allclose(branch.parameter_values["sensor_encoder_layer_2_weights"], 0.0)
    assert np.allclose(branch.parameter_values["sensor_encoder_layer_2_biases"], 0.0)


def Test_The_Step_Zero_Corrected_Density_Equals_The_Cheap_Density_To_Round_Off() -> None:
    """a zero-initialized branch can only reproduce the identity floor exactly, everywhere in the grid"""
    member, cheap_fields, _ = Toy_Member()
    cheap_grid = Grid_Function_Of(cheap_fields[0])
    corrected = member(cheap_grid, GridSpec(GRID_SHAPE))
    assert np.array_equal(np.asarray(corrected.values), np.asarray(cheap_grid.values))
    assert float(np.asarray(member.last_correction_scale)) == 0.0


def Test_The_Zero_Mean_Law_Holds_On_The_Assembled_Member() -> None:
    """the correction the residual adds back integrates to zero, exactly, once it is not the zero field"""
    member, cheap_fields, _ = Toy_Member(seed=12)
    # nudged off the degenerate construction point, so the correction has a real shape to check
    for value in member.Parameter_Values().values():
        value[...] = value + 0.05 * np.random.default_rng(2).normal(size=value.shape)
    cheap_grid = Grid_Function_Of(cheap_fields[0])
    corrected = member(cheap_grid, GridSpec(GRID_SHAPE))
    correction = np.asarray(corrected.values) - np.asarray(cheap_grid.values)
    assert not np.allclose(correction, 0.0)
    assert abs(float(correction.mean())) < 1e-12


def Test_Delta_R_Squared_Is_Zero_At_Identity_And_One_At_A_Perfect_Correction() -> None:
    """the card's own headline metric, at its two defining points"""
    generator = np.random.default_rng(13)
    cheap = generator.normal(size=64)
    accurate = cheap + generator.normal(size=64) * 0.01
    assert abs(Delta_R_Squared(cheap, accurate, cheap)) < 1e-12
    assert abs(Delta_R_Squared(accurate, accurate, cheap) - 1.0) < 1e-12


def Test_Forward_Correction_Agrees_With_The_Assembled_Call() -> None:
    """the lifted path a trainer drives and the numpy path inference uses answer the same field"""
    member, cheap_fields, _ = Toy_Member(seed=14)
    for value in member.Parameter_Values().values():
        value[...] = value + 0.05 * np.random.default_rng(3).normal(size=value.shape)
    cheap_coefficients = Project(member.backbone.cheap_basis, cheap_fields)
    cheap_grid = Grid_Function_Of(cheap_fields[0])
    corrected = member(cheap_grid, GridSpec(GRID_SHAPE))
    correction_through_call = np.asarray(corrected.values).reshape(-1) - cheap_fields[0]
    full_lifted = dict(member.Parameter_Values())
    full_lifted.update(member.Constant_Values())
    correction_through_forward = np.asarray(
        member.Forward_Correction(full_lifted, cheap_coefficients[0:1])
    ).reshape(-1)
    assert np.abs(correction_through_call - correction_through_forward).max() < 1e-10


def Test_Every_Parameter_Receives_A_Gradient_On_The_Reference_Engine() -> None:
    """the reference engine's finite differences, over every array the trainer is handed"""
    member, cheap_fields, correction_fields = Toy_Member(seed=15, pair_count=8)
    # off the degenerate zero point, so the earliest layers have something to differentiate through
    for value in member.Parameter_Values().values():
        value[...] = value + 0.05 * np.random.default_rng(4).normal(size=value.shape)
    cheap_coefficients = Project(member.backbone.cheap_basis, cheap_fields)
    engine = NumpyEngine()
    parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})
    gradients = engine.Gradients(parameters, Lifted_Loss(member, engine, cheap_coefficients, correction_fields))
    assert set(gradients) == set(member.Parameter_Values())
    assert all(np.isfinite(gradient).all() for gradient in gradients.values())
    assert all(float(np.abs(gradient).max()) > 0.0 for gradient in gradients.values())


def Test_The_Zero_Initialized_Step_Reaches_Only_The_Last_Layer_And_The_Readout_Bias() -> None:
    """the chain rule multiplies every earlier gradient by the zeroed last layer's weights"""
    member, cheap_fields, correction_fields = Toy_Member(seed=16, pair_count=8)
    cheap_coefficients = Project(member.backbone.cheap_basis, cheap_fields)
    engine = NumpyEngine()
    parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})
    gradients = engine.Gradients(parameters, Lifted_Loss(member, engine, cheap_coefficients, correction_fields))
    assert float(np.abs(gradients["sensor_encoder_layer_0_weights"]).max()) == 0.0
    assert float(np.abs(gradients["sensor_encoder_layer_1_weights"]).max()) == 0.0
    assert float(np.abs(gradients["sensor_encoder_layer_2_weights"]).max()) > 0.0
    assert float(np.abs(gradients["output_bias"]).max()) > 0.0


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Torch_Engine_Agrees_With_The_Reference_On_A_Tiny_Toy() -> None:
    """the differentiable engine is a way of differentiating this member, not a different member"""
    member, cheap_fields, correction_fields = Toy_Member(seed=17, pair_count=8)
    for value in member.Parameter_Values().values():
        value[...] = value + 0.05 * np.random.default_rng(5).normal(size=value.shape)
    cheap_coefficients = Project(member.backbone.cheap_basis, cheap_fields)
    parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})
    numpy_engine = NumpyEngine()
    torch_engine = TorchEngine()
    numpy_loss = Lifted_Loss(member, numpy_engine, cheap_coefficients, correction_fields)
    torch_loss = Lifted_Loss(
        member, torch_engine, torch_engine.Lift_Constant(cheap_coefficients), torch_engine.Lift_Constant(correction_fields)
    )
    numpy_value, reference_gradients = numpy_engine.Value_And_Gradients(parameters, numpy_loss)
    torch_value, torch_gradients = torch_engine.Value_And_Gradients(parameters, torch_loss)
    assert abs(numpy_value - torch_value) < 1e-10
    assert set(torch_gradients) == set(reference_gradients)
    for name, gradient in torch_gradients.items():
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-5, atol=1e-6), name


def Test_Two_Adam_Steps_Move_Every_Parameter() -> None:
    """the pre-registration proof: the first step wakes the last layer, the second reaches every array"""
    member, cheap_fields, correction_fields = Toy_Member(seed=18, pair_count=12)
    cheap_coefficients = Project(member.backbone.cheap_basis, cheap_fields)
    engine = NumpyEngine()
    loss = Lifted_Loss(member, engine, cheap_coefficients, correction_fields)
    parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})
    initial = {name: value.copy() for name, value in parameters.values.items()}
    adam_state = Fresh_Adam_State(parameters)
    for _ in range(2):
        _, gradients = engine.Value_And_Gradients(parameters, loss)
        parameters = Adam_Step(parameters, gradients, adam_state, learning_rate=1e-2)
    for name in initial:
        assert float(np.abs(parameters.values[name] - initial[name]).max()) > 0.0, name


def Test_Two_Adam_Steps_Are_Deterministic_From_One_Seed() -> None:
    """the same seed retraces the same two steps, a different seed does not"""

    def Trained_Twice(seed: int) -> dict[str, NDArray[np.float64]]:
        member, cheap_fields, correction_fields = Toy_Member(seed=seed, pair_count=12)
        cheap_coefficients = Project(member.backbone.cheap_basis, cheap_fields)
        engine = NumpyEngine()
        loss = Lifted_Loss(member, engine, cheap_coefficients, correction_fields)
        parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})
        adam_state = Fresh_Adam_State(parameters)
        for _ in range(2):
            _, gradients = engine.Value_And_Gradients(parameters, loss)
            parameters = Adam_Step(parameters, gradients, adam_state, learning_rate=1e-2)
        return parameters.values

    first_run = Trained_Twice(19)
    repeated_run = Trained_Twice(19)
    other_seed_run = Trained_Twice(20)
    for name in first_run:
        assert np.array_equal(first_run[name], repeated_run[name])
    assert any(
        not np.array_equal(first_run[name], other_seed_run[name]) for name in first_run
    )


def Test_The_Calibrator_Covers_A_Degenerate_Point_Prediction_At_Its_Level() -> None:
    """a zero-width interval built from a point prediction still meets its stated coverage once calibrated"""
    generator = np.random.default_rng(2026)
    unit_count = 300
    calibration_truth = generator.normal(scale=0.02, size=unit_count)
    calibration_prediction = np.zeros(unit_count)
    calibrator = ConformalCalibrator(level=0.90)
    calibrator.Calibrate(
        calibration_prediction, calibration_prediction, calibration_truth, Lone_Orbits(unit_count)
    )
    held_out_truth = generator.normal(scale=0.02, size=4000)
    held_out_prediction = np.zeros(4000)
    widened = calibrator(held_out_prediction, held_out_prediction)
    covered = float(np.mean((widened.lower <= held_out_truth) & (held_out_truth <= widened.upper)))
    guarantee_low, guarantee_high = Coverage_Guarantee(unit_count, 0.90)
    assert guarantee_low - 3.0 * Coverage_Deviation(unit_count, 0.90) <= covered <= guarantee_high + 0.03


def Test_The_Inspection_Suite_Covers_Every_Key_The_Member_Exposes(tmp_path: Path) -> None:
    """the renderer is the completeness test: no key the member reports may go unrendered"""
    member, cheap_fields, _ = Toy_Member(seed=21)
    member(Grid_Function_Of(cheap_fields[0]), GridSpec(GRID_SHAPE))
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    suite = Render_Inspection_Suite(inspected, tmp_path / "residual_correction_toy", "residual correction toy")
    assert suite.skipped == ()
    assert len(suite.written) > 0
    # twenty mean-centered toy snapshots span at most nineteen directions, short of the requested rank
    correction_rank = member.backbone.correction_basis.modes.shape[0]
    assert correction_rank <= BASIS_RANK
    assert inspected["backbone.readout.basis_modes"].shape == (correction_rank, *GRID_SHAPE)
    assert inspected["backbone.readout.voxel_mean"].shape == GRID_SHAPE
    assert inspected["cheap_basis_singular_values"].ndim == 1


def Test_Guarded_Spread_Never_Divides_By_A_Silent_Zero() -> None:
    """a column that never varies across the training block would otherwise divide by zero downstream"""
    values = np.zeros((10, 4))
    values[:, 0] = np.arange(10.0)
    spread = Guarded_Spread(values)
    assert spread[0] > 0.0
    assert np.array_equal(spread[1:], np.ones(3))


@pytest.mark.pool
def Test_The_Identity_And_Affine_Floors_Reproduce_Stage_Zero_On_The_Real_Corpus() -> None:
    """the same computation stage0-report.md recorded, read fresh off the mounted corpus"""
    census_rows = Read_Census(POOL_ROOT)
    functional_pairs = Strain_Pairs(census_rows)
    Guard_Fresh_Archives(
        identifier
        for functional_pair in functional_pairs
        for identifier in (functional_pair.cheap_identifier, functional_pair.accurate_identifier)
    )
    identity, affine, _ = Identity_And_Affine_Floors(
        functional_pairs, lambda identifier: Load_Field("strain_atlas", identifier, "charge_density")
    )
    identity_median, _ = Median_And_Interquartile(identity)
    affine_median, _ = Median_And_Interquartile(affine)
    assert abs(identity_median - STAGE0_IDENTITY_MEDIAN) < 2e-4
    assert abs(affine_median - STAGE0_AFFINE_MEDIAN) < 2e-4

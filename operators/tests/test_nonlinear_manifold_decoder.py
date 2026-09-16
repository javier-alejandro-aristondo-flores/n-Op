"""the manifold decoder's assembly, its nonlinearity, its path through both engines and a toy training run"""

from pathlib import Path
from typing import Any

import numpy as np
import pytest

from operators.framework import (
    Coefficients,
    Domain,
    Fractional_Grid_Coordinates,
    GridFunction,
    GridSpec,
    PointSet,
    PointSpec,
)
from operators.inspection import Render_Inspection_Suite
from operators.nonlinear_manifold_decoder import Manifold_Network, NonlinearManifoldDecoder
from operators.readouts import NonlinearDecoder
from operators.substrate import NumpyEngine, ParameterSet, Torch_Is_Available, TorchEngine
from operators.training import CachedField, CoordinateFeaturizedBatches, FieldCache, PointSampledBatches, Train

CUBE = Domain(lattice=np.eye(3) * 3.57)


def Small_Manifold_Network(seed: int = 0) -> NonlinearManifoldDecoder:
    """a tiny branch and decoder, enough to assemble and differentiate"""
    return Manifold_Network(
        parameter_width=7,
        branch_hidden_widths=(6,),
        latent_width=4,
        decoder_hidden_widths=(6,),
        fourier_orders=2,
        seed=seed,
    )


def Test_The_Factory_Collects_Both_Branch_And_Decoder_Arrays() -> None:
    """the trainer is handed both the branch's and the decoder's arrays, under one namespace"""
    member = Small_Manifold_Network()
    collected = member.Parameter_Values()
    assert any(name.startswith("sensor_encoder_") for name in collected)
    assert any(name.startswith("decoder_") for name in collected)
    # the two parts draw from different seeds, so neither part's arrays are all zero or identical
    assert not np.allclose(collected["sensor_encoder_layer_0_weights"], 0.0)
    assert not np.allclose(collected["decoder_layer_0_weights"], 0.0)


def Test_The_Member_Inspects_Under_Part_Prefixes() -> None:
    """an assembled member is one flat browsable namespace, each key naming its owner"""
    member = Small_Manifold_Network(seed=1)
    member(Coefficients(vector=np.zeros(7), domain=CUBE), GridSpec((3, 4, 5)))
    inspected = member.Inspect()
    assert any(name.startswith("encoder.") for name in inspected)
    assert any(name.startswith("readout.") for name in inspected)
    assert "readout.last_point_features" in inspected
    assert "encoder.last_latent_vector" in inspected


def Test_The_Member_Reads_Out_A_Field_On_The_Requested_Grid() -> None:
    """parameters in, a field of the asked-for shape out"""
    member = Small_Manifold_Network(seed=2)
    produced = member(Coefficients(vector=np.ones(7), domain=CUBE), GridSpec((3, 4, 5)))
    assert isinstance(produced, GridFunction)
    assert np.asarray(produced.values).shape == (1, 3, 4, 5)


def Test_A_Grid_Query_Agrees_With_The_Same_Points_Asked_For_Explicitly() -> None:
    """the decoder answers a grid and the same points asked for explicitly with identical values"""
    member = Small_Manifold_Network(seed=3)
    coefficients = Coefficients(vector=np.linspace(-1.0, 1.0, 7), domain=CUBE)
    shape = (3, 4, 5)
    grid_result = member(coefficients, GridSpec(shape))
    point_result = member(coefficients, PointSpec(points=Fractional_Grid_Coordinates(shape)))
    assert isinstance(grid_result, GridFunction)
    assert isinstance(point_result, PointSet)
    gridded_values = np.asarray(grid_result.values).reshape(1, -1).T
    assert point_result.values is not None
    assert np.allclose(np.asarray(point_result.values), gridded_values, atol=1e-12)


def Test_The_Decoder_Is_Not_Expressible_As_A_Linear_Map_Of_Its_Latent() -> None:
    """doubling or summing latents does not double or sum the decoder's answer, unlike a basis expansion"""
    member = Small_Manifold_Network(seed=4)
    readout = member.decoder
    assert isinstance(readout, NonlinearDecoder)
    generator = np.random.default_rng(40)
    point_features = generator.normal(size=(9, readout.coordinate_features.feature_count))
    lifted = member.Parameter_Values()
    first_latent = generator.normal(size=4)
    second_latent = generator.normal(size=4)

    def Decoder_Answer(latent: Any) -> Any:
        """this latent row's field over the fixed point set, through the decoder's own single-run path"""
        return np.asarray(readout.Channel_Values(lifted, latent, point_features))

    first_answer = Decoder_Answer(first_latent)
    second_answer = Decoder_Answer(second_latent)
    summed_answer = Decoder_Answer(first_latent + second_latent)
    doubled_answer = Decoder_Answer(2.0 * first_latent)
    assert not np.allclose(summed_answer, first_answer + second_answer)
    assert not np.allclose(doubled_answer, 2.0 * first_answer)


def Test_Forward_Point_Values_Matches_A_Manual_Per_Run_Concatenation() -> None:
    """the sampled prediction is the decoder answered on each run's own points concatenated with its own latent"""
    member = Small_Manifold_Network(seed=5)
    readout = member.decoder
    assert isinstance(readout, NonlinearDecoder)
    generator = np.random.default_rng(41)
    branch_input = generator.normal(size=(4, 7))
    trunk_features = generator.normal(size=(4, 6, readout.coordinate_features.feature_count))
    lifted = member.Parameter_Values()
    produced = np.asarray(member.Forward_Point_Values(lifted, branch_input, trunk_features))
    coefficients = np.asarray(member.Forward_Coefficients(lifted, branch_input))

    def Manual_Run_Answer(run: int) -> Any:
        broadcast_latent = np.tile(coefficients[run][None, :], (trunk_features.shape[1], 1))
        combined = np.concatenate([trunk_features[run], broadcast_latent], axis=1)
        return np.asarray(readout.network.Forward(lifted, combined))[:, 0]

    expected = np.stack([Manual_Run_Answer(run) for run in range(branch_input.shape[0])])
    assert produced.shape == (4, 6)
    assert np.allclose(produced, expected, atol=1e-10)


def Test_Forward_Point_Values_Keeps_Each_Runs_Points_And_Coefficients_Together() -> None:
    """moving one run's branch input moves only that run's own predicted points, never another run's"""
    member = Small_Manifold_Network(seed=6)
    readout = member.decoder
    assert isinstance(readout, NonlinearDecoder)
    generator = np.random.default_rng(42)
    branch_input = generator.normal(size=(4, 7))
    trunk_features = generator.normal(size=(4, 5, readout.coordinate_features.feature_count))
    lifted = member.Parameter_Values()
    original = np.asarray(member.Forward_Point_Values(lifted, branch_input, trunk_features))
    perturbed_input = branch_input.copy()
    perturbed_input[2] += 10.0
    perturbed = np.asarray(member.Forward_Point_Values(lifted, perturbed_input, trunk_features))
    assert np.allclose(perturbed[[0, 1, 3]], original[[0, 1, 3]])
    assert not np.allclose(perturbed[2], original[2])


def Test_Gradients_Reach_Every_Array_Through_The_Point_Sampled_Forward() -> None:
    """the point-sampled loss the trainer will use differentiates onto both the branch and the decoder"""
    member = Small_Manifold_Network(seed=7)
    readout = member.decoder
    assert isinstance(readout, NonlinearDecoder)
    generator = np.random.default_rng(43)
    lifted_batch = {
        "branch_input": np.asarray(generator.normal(size=(4, 7)), dtype=np.float64),
        "trunk_features": np.asarray(
            generator.normal(size=(4, 5, readout.coordinate_features.feature_count)), dtype=np.float64
        ),
        "targets": np.asarray(generator.normal(size=(4, 5)), dtype=np.float64),
    }

    def Point_Loss(lifted: dict[str, Any], batch: dict[str, Any]) -> Any:
        predicted = member.Forward_Point_Values(lifted, batch["branch_input"], batch["trunk_features"])
        residuals = predicted - batch["targets"]
        return (residuals * residuals).mean()

    gradients = NumpyEngine().Gradients(
        ParameterSet(values=member.Parameter_Values()), lambda lifted: Point_Loss(lifted, lifted_batch)
    )
    assert set(gradients) == set(member.Parameter_Values())
    assert any(name.startswith("decoder_") for name in gradients)
    assert all(np.isfinite(gradient).all() for gradient in gradients.values())
    assert all(np.abs(gradient).max() > 0.0 for gradient in gradients.values())


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Both_Engines_Agree_On_The_Point_Sampled_Gradient() -> None:
    """the foreign engine's gradient matches the finite-difference reference on the same loss"""
    member = Small_Manifold_Network(seed=8)
    readout = member.decoder
    assert isinstance(readout, NonlinearDecoder)
    generator = np.random.default_rng(44)
    branch_input = np.asarray(generator.normal(size=(3, 7)), dtype=np.float64)
    trunk_features = np.asarray(
        generator.normal(size=(3, 4, readout.coordinate_features.feature_count)), dtype=np.float64
    )
    targets = np.asarray(generator.normal(size=(3, 4)), dtype=np.float64)
    parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})

    def Loss_Of(
        lifted: dict[str, Any], lifted_branch_input: Any, lifted_trunk_features: Any, lifted_targets: Any
    ) -> Any:
        predicted = member.Forward_Point_Values(lifted, lifted_branch_input, lifted_trunk_features)
        residuals = predicted - lifted_targets
        return (residuals * residuals).mean()

    torch_engine = TorchEngine()
    numpy_engine = NumpyEngine()
    lifted_branch_input = torch_engine.Lift_Constant(branch_input)
    lifted_trunk_features = torch_engine.Lift_Constant(trunk_features)
    lifted_targets = torch_engine.Lift_Constant(targets)

    def Torch_Loss(lifted: dict[str, Any]) -> Any:
        """the same loss with this run's arrays already lifted onto the foreign engine"""
        return Loss_Of(lifted, lifted_branch_input, lifted_trunk_features, lifted_targets)

    def Numpy_Loss(lifted: dict[str, Any]) -> Any:
        """the same loss read straight off the reference engine's own arrays"""
        return Loss_Of(lifted, branch_input, trunk_features, targets)

    torch_value, torch_gradients = torch_engine.Value_And_Gradients(parameters, Torch_Loss)
    numpy_value = numpy_engine.Evaluate(parameters, Numpy_Loss)
    assert abs(float(torch_value) - float(numpy_value)) < 1e-8
    numpy_gradients = numpy_engine.Gradients(parameters, Numpy_Loss)
    assert set(torch_gradients) == set(numpy_gradients)
    for name, gradient in torch_gradients.items():
        assert np.allclose(np.asarray(gradient), numpy_gradients[name], rtol=1e-4, atol=1e-5), name


def Toy_Field_Cache(role: str, seed: int) -> FieldCache:
    """a handful of synthetic runs, small enough for a deterministic training test to run in a heartbeat"""
    generator = np.random.default_rng(seed)
    fields = tuple(
        CachedField(
            identifier=f"{role}_{run}",
            run_path=f"strain_atlas/toy/{role}_{run}",
            unit_key=f"unit_{run}",
            parameters=generator.normal(size=7),
            values=generator.normal(size=(1, 3, 3, 3)).astype(np.float32),
            grid_shape=(3, 3, 3),
            lattice=np.eye(3, dtype=np.float64) * 3.57,
            cell_volume=45.5,
            covariate_values={"functional": "cheap" if run % 2 == 0 else "accurate"},
        )
        for run in range(5)
    )
    return FieldCache("strain_to_charge", role, fields)


def Toy_Batches(seed: int) -> CoordinateFeaturizedBatches:
    """a point-sampled source over the toy cache, its trunk features precomputed the way training draws them"""
    member = Small_Manifold_Network(seed=9)
    training_cache = Toy_Field_Cache("train", seed)
    validation_cache = Toy_Field_Cache("validation", seed + 1)
    sampler = PointSampledBatches(training_cache, validation_cache, runs_per_batch=3, points_per_run=8)
    return CoordinateFeaturizedBatches(sampler, member.decoder.coordinate_features)


def Toy_Training_Result(seed: int) -> Any:
    """one short deterministic run over the toy source, for the determinism test to run twice"""
    member = Small_Manifold_Network(seed=9)
    batches = Toy_Batches(seed=100)

    def Loss_Of(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        branch_input = lifted_batch["parameter_vectors"]
        predicted = member.Forward_Point_Values(lifted, branch_input, lifted_batch["trunk_features"])
        target = lifted_batch["target_values"][:, :, 0]
        residuals = predicted - target
        return (residuals * residuals).mean()

    return Train(
        NumpyEngine(),
        ParameterSet(values=member.Parameter_Values()),
        Loss_Of,
        batches,
        step_count=5,
        learning_rate=1e-2,
        seed=seed,
        validation_interval=5,
    )


def Test_A_Toy_Training_Run_Is_Deterministic_Under_The_Same_Seed() -> None:
    """the same seed on the same source reaches the same parameters and the same curve, twice"""
    first = Toy_Training_Result(20260916)
    second = Toy_Training_Result(20260916)
    assert np.allclose(first.loss_curve, second.loss_curve)
    for name, value in first.parameters.values.items():
        assert np.allclose(value, second.parameters.values[name])


def Test_Every_Inspection_Key_Has_A_Renderer(tmp_path: Path) -> None:
    """the generic suite renders every key the assembled member exposes, none skipped for want of a drawer"""
    member = Small_Manifold_Network(seed=10)
    member(Coefficients(vector=np.linspace(-1.0, 1.0, 7), domain=CUBE), GridSpec((3, 3, 3)))
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    suite = Render_Inspection_Suite(inspected, tmp_path, "nonlinear_manifold_decoder toy")
    assert suite.skipped == ()

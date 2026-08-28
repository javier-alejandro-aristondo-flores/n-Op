"""Checks the trainer against closed forms and threads the whole stack on live pairs."""

from pathlib import Path
from typing import Any

import numpy
import pytest

from operators.data.store import POOL_ROOT
from operators.substrate import NumpyEngine, ParameterSet, Torch_Is_Available, TorchEngine
from operators.substrate.engine import Engine
from operators.substrate.linear_algebra import Least_Squares_Solution
from operators.tasks import Card_Named
from operators.training import Paired_Field_Examples, Strain_Charge_Pairs, Train

ENGINE_CASES = [
    pytest.param(NumpyEngine(), id="numpy_reference"),
    pytest.param(
        TorchEngine(),
        id="torch",
        marks=pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet"),
    ),
]


def Regression_Loss(lifted: dict[str, Any], batch: Any) -> Any:
    """Mean squared error of a two-feature linear model against the batch's last column."""
    predictions = batch[:, :2] @ lifted["coefficients"] + lifted["offset"]
    residuals = predictions - batch[:, 2]
    return (residuals * residuals).mean()


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_Training_Recovers_Linear_Regression(engine: Engine, tmp_path: Path) -> None:
    """Asserts the loop reaches the closed-form regression and stores its artifacts."""
    generator = numpy.random.default_rng(9)
    features = generator.random((40, 2))
    targets = features @ numpy.asarray([2.0, -1.0]) + 0.5
    batch = numpy.concatenate([features, targets[:, None]], axis=1)
    parameters = ParameterSet(values={"coefficients": numpy.zeros(2), "offset": numpy.zeros(1)})
    result = Train(
        engine,
        parameters,
        Regression_Loss,
        [batch],
        step_count=600,
        learning_rate=0.05,
        artifact_directory=tmp_path,
        run_name="regression_thread",
    )
    assert numpy.allclose(result.parameters.values["coefficients"], [2.0, -1.0], atol=2e-2)
    assert abs(float(result.parameters.values["offset"][0]) - 0.5) < 2e-2
    assert (tmp_path / "regression_thread_curves.npz").is_file()
    assert (tmp_path / "regression_thread_manifest.json").is_file()
    assert (tmp_path / "regression_thread_curves.png").stat().st_size > 1000


@pytest.mark.pool
def Test_The_Thread_Reproduces_The_Affine_Floor() -> None:
    """Trains the two-parameter affine map on live pairs and matches the closed form."""
    if not POOL_ROOT.exists():
        pytest.fail("the corpus at /Pool/VASP_DATA is not mounted on this machine")
    sampled_rows: list[Any] = []
    for _, cheap_field, accurate_field in Strain_Charge_Pairs("validation", limit=24):
        cheap_values = numpy.asarray(cheap_field.values, dtype=numpy.float64).reshape(-1)[::977]
        accurate_values = numpy.asarray(accurate_field.values, dtype=numpy.float64).reshape(-1)[::977]
        sampled_rows.append(numpy.stack([cheap_values, accurate_values], axis=1))
    batch = numpy.concatenate(sampled_rows)
    assert batch.shape[0] > 1000

    design = numpy.stack([batch[:, 0], numpy.ones(batch.shape[0])], axis=1)
    closed_coefficients = Least_Squares_Solution(design, batch[:, 1])
    closed_error = float(
        numpy.linalg.norm(design @ closed_coefficients - batch[:, 1]) / numpy.linalg.norm(batch[:, 1])
    )

    def Affine_Loss(lifted: dict[str, Any], lifted_batch: Any) -> Any:
        predictions = lifted_batch[:, 0] * lifted["scale"] + lifted["offset"]
        residuals = predictions - lifted_batch[:, 1]
        return (residuals * residuals).mean()

    parameters = ParameterSet(values={"scale": numpy.asarray([1.0]), "offset": numpy.asarray([0.0])})
    result = Train(NumpyEngine(), parameters, Affine_Loss, [batch], step_count=300, learning_rate=0.004)
    trained = result.parameters.values
    trained_error = float(
        numpy.linalg.norm(batch[:, 0] * trained["scale"][0] + trained["offset"][0] - batch[:, 1])
        / numpy.linalg.norm(batch[:, 1])
    )
    assert 0.004 < closed_error < 0.025
    assert trained_error < closed_error * 1.1
    assert abs(float(trained["scale"][0]) - float(closed_coefficients[0])) < 0.01


@pytest.mark.pool
def Test_The_Paired_Loader_Assembles_Channels_Across_The_Half_Grid() -> None:
    """Asserts the loader builds spin-doubled inputs and half-grid localization targets."""
    if not POOL_ROOT.exists():
        pytest.fail("the corpus at /Pool/VASP_DATA is not mounted on this machine")
    card = Card_Named("charge_to_localization")
    example = next(iter(Paired_Field_Examples(card, role="evaluation", limit=1)))
    assert example.input_function.channel_labels == ("charge_density", "magnetization_density")
    assert example.target_function.channel_labels == ("electron_localization_up", "electron_localization_down")
    input_shape = numpy.asarray(example.input_function.values).shape
    target_shape = numpy.asarray(example.target_function.values).shape
    assert input_shape[0] == 2 and target_shape[0] == 2
    assert tuple(extent // 2 for extent in input_shape[1:]) == target_shape[1:]

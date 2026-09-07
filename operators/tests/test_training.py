"""the trainer against closed forms, and the whole stack threaded on live pairs"""

from pathlib import Path
from typing import Any

import numpy as np
import pytest

from operators.substrate import (
    Engine,
    Least_Squares_Solution,
    NumpyEngine,
    ParameterSet,
    Torch_Is_Available,
    TorchEngine,
)
from operators.data import Strain_Tensor_Of
from operators.tasks import Card_Named
from operators.training import (
    AUXILIARY_PROBE_ROLE,
    Aligned_Energy_Grid,
    Lattice_Factors_Of,
    Paired_Field_Examples,
    Parameter_Field_Examples,
    State_Density_Examples,
    Strain_Charge_Pairs,
    Train,
)

ENGINE_CASES = [
    pytest.param(NumpyEngine(), id="numpy_reference"),
    pytest.param(
        TorchEngine(),
        id="torch",
        marks=pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet"),
    ),
]


def Regression_Loss(lifted: dict[str, Any], batch: Any) -> Any:
    """mean squared error of a two-feature linear model against the batch's last column"""
    predictions = batch[:, :2] @ lifted["coefficients"] + lifted["offset"]
    residuals = predictions - batch[:, 2]
    return (residuals * residuals).mean()


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_Training_Recovers_Linear_Regression(engine: Engine, tmp_path: Path) -> None:
    """the loop reaches the closed-form regression, and stores its artifacts"""
    generator = np.random.default_rng(9)
    features = generator.random((40, 2))
    targets = features @ np.asarray([2.0, -1.0]) + 0.5
    batch = np.concatenate([features, targets[:, None]], axis=1)
    parameters = ParameterSet(values={"coefficients": np.zeros(2), "offset": np.zeros(1)})
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
    assert np.allclose(result.parameters.values["coefficients"], [2.0, -1.0], atol=2e-2)
    assert abs(float(result.parameters.values["offset"][0]) - 0.5) < 2e-2
    assert (tmp_path / "regression_thread_curves.npz").is_file()
    assert (tmp_path / "regression_thread_manifest.json").is_file()
    assert (tmp_path / "regression_thread_curves.png").stat().st_size > 1000


@pytest.mark.pool
def Test_The_Thread_Reproduces_The_Affine_Floor() -> None:
    """the two-parameter affine map, trained on live pairs, against the closed form"""
    sampled_rows: list[Any] = []
    for _, cheap_field, accurate_field in Strain_Charge_Pairs("validation", limit=24):
        cheap_values = np.asarray(cheap_field.values, dtype=np.float64).reshape(-1)[::977]
        accurate_values = np.asarray(accurate_field.values, dtype=np.float64).reshape(-1)[::977]
        sampled_rows.append(np.stack([cheap_values, accurate_values], axis=1))
    batch = np.asarray(np.concatenate(sampled_rows), dtype=np.float64)
    assert batch.shape[0] > 1000

    design = np.stack([batch[:, 0], np.ones(batch.shape[0])], axis=1)
    closed_coefficients = Least_Squares_Solution(design, batch[:, 1])
    closed_error = float(
        np.linalg.norm(design @ closed_coefficients - batch[:, 1]) / np.linalg.norm(batch[:, 1])
    )

    def Affine_Loss(lifted: dict[str, Any], lifted_batch: Any) -> Any:
        predictions = lifted_batch[:, 0] * lifted["scale"] + lifted["offset"]
        residuals = predictions - lifted_batch[:, 1]
        return (residuals * residuals).mean()

    parameters = ParameterSet(values={"scale": np.asarray([1.0]), "offset": np.asarray([0.0])})
    result = Train(NumpyEngine(), parameters, Affine_Loss, [batch], step_count=300, learning_rate=0.004)
    trained = result.parameters.values
    predicted = np.asarray(batch[:, 0] * trained["scale"][0] + trained["offset"][0], dtype=np.float64)
    trained_error = float(np.linalg.norm(predicted - batch[:, 1]) / np.linalg.norm(batch[:, 1]))
    assert 0.004 < closed_error < 0.025
    assert trained_error < closed_error * 1.1
    assert abs(float(trained["scale"][0]) - float(closed_coefficients[0])) < 0.01


@pytest.mark.pool
def Test_The_Paired_Loader_Assembles_Channels_Across_The_Half_Grid() -> None:
    """spin-doubled inputs, and half-grid localization targets"""
    card = Card_Named("charge_to_localization")
    example = next(iter(Paired_Field_Examples(card, role="evaluation", limit=1)))
    assert example.input_function.channel_labels == ("charge_density", "magnetization_density")
    assert example.target_function.channel_labels == ("electron_localization_up", "electron_localization_down")
    input_shape = np.asarray(example.input_function.values).shape
    target_shape = np.asarray(example.target_function.values).shape
    assert input_shape[0] == 2 and target_shape[0] == 2
    assert tuple(extent // 2 for extent in input_shape[1:]) == target_shape[1:]


def Test_The_Lattice_Factors_Parse_From_The_Run_Name() -> None:
    """asserts the six perovskite factors come off the name with p as the decimal point"""
    parsed = Lattice_Factors_Of("ggapbe/length_distortions/a_0p8_b_1_c_1p2_alpha_1_beta_0p9_gamma_1")
    assert parsed == (0.8, 1.0, 1.2, 1.0, 0.9, 1.0)


def Test_The_Parameter_Loader_Rejects_A_Card_Split_By_Fields() -> None:
    """asserts a field-to-field card is not served as a parameter sweep"""
    with pytest.raises(ValueError):
        Parameter_Field_Examples(Card_Named("charge_to_localization"), "train")


@pytest.mark.pool
def Test_The_Parameter_Loader_Serves_The_Strain_Atlas() -> None:
    """asserts the validation assignment loads whole, on both functionals"""
    examples = list(Parameter_Field_Examples(Card_Named("strain_to_charge"), "validation"))
    assert len(examples) == 256
    assert {example.covariate_values["functional"] for example in examples} == {"accurate", "cheap"}
    for example in examples:
        assert np.asarray(example.parameters.vector).shape == (6,)
        assert np.asarray(example.target_function.values).shape[0] == 1


@pytest.mark.pool
def Test_The_Parameter_Vectors_Are_The_Runs_Own_Tensors() -> None:
    """asserts each vector is the run's own strain, not its orbit's canonical image"""
    checked = 0
    away_from_canonical = 0
    for example in Parameter_Field_Examples(Card_Named("strain_to_charge"), "validation"):
        point = example.run_path.split("/")[-2]
        # an isotropic point reads its strain back off the cell, so the name alone cannot rebuild it
        if point.startswith("Vol_"):
            continue
        expected = Strain_Tensor_Of(point, None)
        assert np.allclose(np.asarray(example.parameters.vector), expected)
        canonical = [float(component) for component in example.unit_key.split("_")]
        if not np.allclose(expected, canonical):
            away_from_canonical += 1
        checked += 1
    assert checked > 200
    assert away_from_canonical > 0


@pytest.mark.pool
def Test_The_Auxiliary_Sweep_Reaches_Only_The_Probe() -> None:
    """asserts the reserved rotational copies appear under the probe role and nowhere else"""
    card = Card_Named("strain_to_charge")
    probe = list(Parameter_Field_Examples(card, AUXILIARY_PROBE_ROLE))
    assert len(probe) == 320
    assert all("/new/" in example.run_path for example in probe)
    for role in ("train", "validation", "test"):
        assert not any("/new/" in example.run_path for example in Parameter_Field_Examples(card, role))


@pytest.mark.pool
def Test_The_Perovskite_Loader_Splits_By_Fold_And_By_Factor() -> None:
    """asserts the fold map and both factor holdouts select the committed unit counts"""
    card = Card_Named("lattice_to_charge")
    assert len(list(Parameter_Field_Examples(card, "evaluation"))) == 50
    assert len(list(Parameter_Field_Examples(card, "train"))) == 199
    for holdout_tag in ("holdout_factor_0p8", "holdout_factor_1p2"):
        held = list(Parameter_Field_Examples(card, "evaluation", extrapolation_holdout=holdout_tag))
        assert len(held) == 122
        assert all(holdout_tag.removeprefix("holdout_factor_") in example.run_path for example in held)


@pytest.mark.pool
def Test_The_State_Density_Curves_Rebuild_On_The_Aligned_Window() -> None:
    """asserts curves are non-negative on the shared window and empty across the gap"""
    grid = Aligned_Energy_Grid("strain_atlas")
    assert (float(grid[0]), float(grid[-1])) == (-28.0, 8.0)
    for example in State_Density_Examples(Card_Named("strain_to_states"), "validation", limit=8):
        assert example.state_density.shape == grid.shape
        assert bool((example.state_density >= 0.0).all())
        assert example.occupancy_walk_gap > 1.0
        across_the_gap = (example.energy_grid > 0.2) & (example.energy_grid < example.occupancy_walk_gap - 0.2)
        below_the_edge = example.energy_grid < -1.0
        assert float(example.state_density[across_the_gap].mean()) < 0.01
        assert float(example.state_density[below_the_edge].mean()) > 0.05


@pytest.mark.pool
def Test_The_Rebuilt_Gaps_Reproduce_The_Recorded_Scissor() -> None:
    """asserts the occupancy walk through the curve loader lands on the Stage-0 scissor"""
    by_point: dict[str, dict[str, float]] = {}
    for example in State_Density_Examples(Card_Named("strain_to_states"), "validation"):
        point = example.run_path.rsplit("/", 1)[0]
        by_point.setdefault(point, {})[example.covariate_values["functional"]] = example.occupancy_walk_gap
    differences = np.asarray(
        [sides["accurate"] - sides["cheap"] for sides in by_point.values() if len(sides) == 2]
    )
    assert differences.shape[0] > 100
    # the report records 1.223 +/- 0.057 eV over all pairs, reached by a different route
    assert 1.19 < float(differences.mean()) < 1.25
    assert float(differences.std()) < 0.07

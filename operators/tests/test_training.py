"""the trainer against closed forms, and the whole stack threaded on live pairs"""

from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.framework import Array
from operators.substrate import (
    ACCELERATOR_DEVICE_NAME,
    Accelerator_Is_Available,
    Engine,
    HOST_DEVICE_NAME,
    Least_Squares_Solution,
    NumpyEngine,
    ParameterSet,
    Precision,
    Torch_Is_Available,
    TorchEngine,
)
from operators.data import Strain_Tensor_Of
from operators.tasks import Card_Named
from operators.training import (
    AUXILIARY_PROBE_ROLE,
    Aligned_Energy_Grid,
    BatchSource,
    FixedBatches,
    Lattice_Factors_Of,
    Paired_Field_Examples,
    Parameter_Field_Examples,
    Resolved_Device_Name,
    State_Density_Examples,
    Strain_Charge_Pairs,
    Train,
    TrainingBatch,
    TrainingHook,
    TrainingProgress,
)

ENGINE_CASES = [
    pytest.param(NumpyEngine(), id="numpy_reference"),
    pytest.param(
        TorchEngine(),
        id="torch",
        marks=pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet"),
    ),
]


def Regression_Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
    """mean squared error of a two-feature linear model against the batch's last column"""
    rows = lifted_batch["rows"]
    predictions = rows[:, :2] @ lifted["coefficients"] + lifted["offset"]
    residuals = predictions - rows[:, 2]
    return (residuals * residuals).mean()


def Distance_Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
    """mean squared distance from one moving position to the target the batch carries"""
    residuals = lifted["position"] - lifted_batch["rows"][:, 0]
    return (residuals * residuals).mean()


def Rows_Batch(rows: NDArray[np.float64]) -> TrainingBatch:
    """one made-up batch holding a single table of rows under a plain name"""
    return TrainingBatch({"rows": rows})


def Targets_At(target: float, row_count: int) -> NDArray[np.float64]:
    """a one-column table every row of which asks for the same target"""
    return np.full((row_count, 1), target, dtype=np.float64)


class DrawnRowBatches(BatchSource):
    """rows drawn out of one table every step, over validation units the caller hands in whole"""


    def __init__(
        self,
        rows: NDArray[np.float64],
        validation_units: tuple[tuple[str, NDArray[np.float64]], ...],
        rows_per_batch: int = 8,
    ) -> None:
        self.rows = rows
        self.rows_per_batch = rows_per_batch
        self.held: tuple[tuple[str, TrainingBatch], ...] = tuple(
            (unit_key, Rows_Batch(unit_rows)) for unit_key, unit_rows in validation_units
        )


    def Next_Batch(self, generator: np.random.Generator) -> TrainingBatch:
        """one draw with replacement out of the table, spending the generator the trainer owns"""
        return Rows_Batch(self.rows[generator.integers(0, self.rows.shape[0], size=self.rows_per_batch)])


    def Validation_Batches(self) -> tuple[tuple[str, TrainingBatch], ...]:
        """the units the caller held out, each one whole"""
        return self.held


    def Inspect(self) -> dict[str, Array]:
        """the table drawn from, and how many rows a step takes out of it"""
        return {
            "rows": self.rows,
            "rows_per_batch": np.asarray([self.rows_per_batch], dtype=np.float64),
            "validation_unit_count": np.asarray([len(self.held)], dtype=np.float64),
        }


class CountingEngine:
    """an engine wrapping another and counting which of its calls the loop actually makes"""


    def __init__(self, inner: Engine) -> None:
        self.inner = inner
        self.working_precision: Precision = inner.working_precision
        self.evaluate_calls = 0
        self.gradient_calls = 0
        self.fused_calls = 0
        self.lifted_arrays: list[Any] = []


    def Evaluate(self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]) -> float:
        self.evaluate_calls += 1
        return self.inner.Evaluate(parameters, forward)


    def Gradients(
        self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]
    ) -> dict[str, NDArray[np.float64]]:
        self.gradient_calls += 1
        return self.inner.Gradients(parameters, forward)


    def Value_And_Gradients(
        self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]
    ) -> tuple[float, dict[str, NDArray[np.float64]]]:
        self.fused_calls += 1
        return self.inner.Value_And_Gradients(parameters, forward)


    def Lift_Constant(self, value: NDArray[np.float64]) -> Any:
        lifted = self.inner.Lift_Constant(value)
        self.lifted_arrays.append(lifted)
        return lifted


def Linear_Regression_Setup(seed: int = 9) -> tuple[NDArray[np.float64], ParameterSet]:
    """a two-feature table whose closed form is known, and the zeroed parameters to reach it from"""
    generator = np.random.default_rng(seed)
    features = generator.random((40, 2))
    targets = features @ np.asarray([2.0, -1.0]) + 0.5
    rows = np.asarray(np.concatenate([features, targets[:, None]], axis=1), dtype=np.float64)
    return rows, ParameterSet(values={"coefficients": np.zeros(2), "offset": np.zeros(1)})


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_Training_Recovers_Linear_Regression(engine: Engine, tmp_path: Path) -> None:
    """the loop reaches the closed-form regression, and stores its artifacts"""
    rows, parameters = Linear_Regression_Setup()
    result = Train(
        engine,
        parameters,
        Regression_Loss,
        FixedBatches(Rows_Batch(rows)),
        step_count=600,
        learning_rate=0.05,
        artifact_directory=tmp_path,
        run_name="regression_thread",
        validation_interval=50,
    )
    assert np.allclose(result.parameters.values["coefficients"], [2.0, -1.0], atol=2e-2)
    assert abs(float(result.parameters.values["offset"][0]) - 0.5) < 2e-2
    assert (tmp_path / "regression_thread_curves.npz").is_file()
    assert (tmp_path / "regression_thread_manifest.json").is_file()
    assert (tmp_path / "regression_thread_curves.png").stat().st_size > 1000
    assert (tmp_path / "regression_thread_checkpoint.npz").is_file()


def Test_A_Fixed_Source_Hands_Back_The_One_Batch_It_Holds() -> None:
    """asserts the trivial source repeats its batch and offers it as the single held-out unit"""
    rows, _ = Linear_Regression_Setup()
    held_out = Rows_Batch(rows[:5])
    source = FixedBatches(Rows_Batch(rows), held_out)
    generator = np.random.default_rng(3)
    assert source.Next_Batch(generator) is source.Next_Batch(generator)
    assert [unit_key for unit_key, _ in source.Validation_Batches()] == ["whole_batch"]
    assert source.Validation_Batches()[0][1] is held_out
    assert "batch_rows" in source.Inspect() and "validation_rows" in source.Inspect()


def Test_One_Seed_Is_What_Replays_A_Whole_Run() -> None:
    """asserts the seed reaches the draw, so one number replays a run and another number does not"""
    rows, parameters = Linear_Regression_Setup()
    units = (("unit_one", rows[:20]),)
    drawn_runs = [
        Train(
            NumpyEngine(),
            parameters,
            Regression_Loss,
            DrawnRowBatches(rows, units),
            step_count=40,
            learning_rate=0.05,
            seed=chosen_seed,
            validation_interval=40,
        )
        for chosen_seed in (101, 101, 202)
    ]
    assert np.array_equal(drawn_runs[0].loss_curve, drawn_runs[1].loss_curve)
    assert not np.array_equal(drawn_runs[0].loss_curve, drawn_runs[2].loss_curve)


def Test_The_Validation_Score_Is_A_Mean_Over_Units_And_Not_Over_Points() -> None:
    """asserts a unit holding a hundred times the points weighs exactly as much as one holding two"""
    parameters = ParameterSet(values={"position": np.zeros(1)})
    source = DrawnRowBatches(
        Targets_At(1.0, 4),
        (("small_unit", Targets_At(1.0, 2)), ("large_unit", Targets_At(3.0, 200))),
    )
    result = Train(NumpyEngine(), parameters, Distance_Loss, source, step_count=0, learning_rate=0.1)
    over_units = (1.0 + 9.0) / 2.0
    over_points = (2 * 1.0 + 200 * 9.0) / 202.0
    assert result.validation_curve.shape == (1,)
    assert abs(float(result.validation_curve[0]) - over_units) < 1e-12
    assert abs(over_units - over_points) > 3.0


def Test_Early_Stopping_Keeps_The_Best_Parameters_And_Not_The_Last() -> None:
    """asserts a run whose validation turns around stops, and hands back the pass that scored best"""
    parameters = ParameterSet(values={"position": np.zeros(1)})
    source = DrawnRowBatches(Targets_At(5.0, 4), (("only_unit", Targets_At(1.0, 4)),), rows_per_batch=4)
    result = Train(
        NumpyEngine(),
        parameters,
        Distance_Loss,
        source,
        step_count=400,
        learning_rate=0.05,
        validation_interval=5,
        patience=3,
    )
    completed = cast(int, result.manifest["completed_steps"])
    best_step = cast(int, result.manifest["best_step"])
    assert result.manifest["stopped_early"] is True
    assert 0 < best_step < completed < 400
    # the run walks past the validation target on its way to the training target and never turns back
    assert abs(float(result.parameters.values["position"][0]) - 1.0) < 0.2
    assert float(result.validation_curve[-1]) > float(result.validation_curve.min())


def Test_Patience_Left_Unset_Runs_The_Whole_Budget() -> None:
    """asserts a run with no patience count spends every step it was given and still keeps the best"""
    parameters = ParameterSet(values={"position": np.zeros(1)})
    source = DrawnRowBatches(Targets_At(5.0, 4), (("only_unit", Targets_At(1.0, 4)),), rows_per_batch=4)
    result = Train(
        NumpyEngine(),
        parameters,
        Distance_Loss,
        source,
        step_count=120,
        learning_rate=0.05,
        validation_interval=5,
    )
    assert result.manifest["stopped_early"] is False
    assert result.manifest["completed_steps"] == 120
    assert cast(int, result.manifest["best_step"]) < 120
    assert abs(float(result.parameters.values["position"][0]) - 1.0) < 0.2


def Test_A_Run_Resumes_Where_The_Checkpoint_Left_It(tmp_path: Path) -> None:
    """asserts a run cut in half and carried on lands exactly where the uninterrupted one did"""
    rows, parameters = Linear_Regression_Setup()
    units = (("unit_one", rows[:20]), ("unit_two", rows[20:]))
    interrupted = tmp_path / "interrupted"
    whole = Train(
        NumpyEngine(),
        parameters,
        Regression_Loss,
        DrawnRowBatches(rows, units),
        step_count=120,
        learning_rate=0.05,
        artifact_directory=tmp_path / "straight_through",
        run_name="thread",
        validation_interval=20,
    )
    Train(
        NumpyEngine(),
        parameters,
        Regression_Loss,
        DrawnRowBatches(rows, units),
        step_count=60,
        learning_rate=0.05,
        artifact_directory=interrupted,
        run_name="thread",
        validation_interval=20,
    )
    carried = Train(
        NumpyEngine(),
        parameters,
        Regression_Loss,
        DrawnRowBatches(rows, units),
        step_count=120,
        learning_rate=0.05,
        artifact_directory=interrupted,
        run_name="thread",
        validation_interval=20,
        resume=True,
    )
    assert whole.manifest["resumed_from_step"] == 0
    assert carried.manifest["resumed_from_step"] == 60
    assert carried.manifest["best_step"] == whole.manifest["best_step"]
    for name, value in whole.parameters.values.items():
        assert np.allclose(carried.parameters.values[name], value, atol=1e-12)
    assert np.allclose(carried.loss_curve, whole.loss_curve, atol=1e-12)
    assert np.array_equal(carried.validation_steps, whole.validation_steps)
    # the archive is renamed into place, so a directory that holds a half-written one is a bug
    assert not list(interrupted.glob("*.partial.npz"))


def Test_A_Checkpoint_Is_Refused_By_A_Run_It_Was_Not_Written_For(tmp_path: Path) -> None:
    """asserts a resume onto different parameter names says so rather than half-restoring"""
    rows, parameters = Linear_Regression_Setup()
    Train(
        NumpyEngine(),
        parameters,
        Regression_Loss,
        FixedBatches(Rows_Batch(rows)),
        step_count=20,
        learning_rate=0.05,
        artifact_directory=tmp_path,
        run_name="thread",
        validation_interval=20,
    )
    with pytest.raises(ValueError):
        Train(
            NumpyEngine(),
            ParameterSet(values={"position": np.zeros(1)}),
            Distance_Loss,
            FixedBatches(Rows_Batch(Targets_At(1.0, 4))),
            step_count=20,
            learning_rate=0.05,
            artifact_directory=tmp_path,
            run_name="thread",
            validation_interval=20,
            resume=True,
        )


class ClippingHook(TrainingHook):
    """clips every named parameter into a symmetric box after each Adam step, and counts its own calls"""


    def __init__(self, bound: float) -> None:
        self.bound = bound
        self.step_calls = 0


    def After_Step(self, progress: TrainingProgress) -> None:
        self.step_calls += 1
        progress.parameters = ParameterSet(
            values={
                name: np.clip(value, -self.bound, self.bound)
                for name, value in progress.parameters.values.items()
            }
        )


    def After_Validation(self, progress: TrainingProgress) -> dict[str, float]:
        return {}


class ProbeHook(TrainingHook):
    """no per-step projection, and a validation-scored probe naming the step it was taken at"""


    def After_Step(self, progress: TrainingProgress) -> None:
        return None


    def After_Validation(self, progress: TrainingProgress) -> dict[str, float]:
        return {"probe": float(progress.completed_steps)}


def Test_A_Hook_Clips_Every_Step_And_The_Manifest_Records_Its_Presence() -> None:
    """a hook projecting the parameters into a box every step leaves the trained result sitting on that box"""
    rows, parameters = Linear_Regression_Setup()
    hook = ClippingHook(bound=0.3)
    result = Train(
        NumpyEngine(),
        parameters,
        Regression_Loss,
        FixedBatches(Rows_Batch(rows)),
        step_count=200,
        learning_rate=0.05,
        validation_interval=50,
        hook=hook,
    )
    assert hook.step_calls == 200
    for value in result.parameters.values.values():
        assert bool(np.all(value >= -0.3 - 1e-9))
        assert bool(np.all(value <= 0.3 + 1e-9))
    # the unconstrained closed form wants coefficients near [2.0, -1.0], well outside this box
    assert float(np.max(np.abs(result.parameters.values["coefficients"]))) > 0.29
    assert result.manifest["hook_present"] is True


def Test_A_Hook_With_No_Hook_Leaves_The_Manifest_Unflagged() -> None:
    """asserts the manifest's own flag answers false, not merely absent, when no hook was passed"""
    rows, parameters = Linear_Regression_Setup()
    result = Train(
        NumpyEngine(), parameters, Regression_Loss, FixedBatches(Rows_Batch(rows)), step_count=5, learning_rate=0.05
    )
    assert result.manifest["hook_present"] is False
    assert cast(float, result.manifest["wall_clock_seconds"]) >= 0.0


def Test_A_Hooks_Validation_Curve_Survives_A_Checkpoint_And_A_Resume(tmp_path: Path) -> None:
    """a hook's own named curve rebuilds exactly across an interrupted-and-resumed run, and Inspect carries it"""
    rows, parameters = Linear_Regression_Setup()
    interrupted = tmp_path / "interrupted"
    Train(
        NumpyEngine(),
        parameters,
        Regression_Loss,
        FixedBatches(Rows_Batch(rows)),
        step_count=40,
        learning_rate=0.05,
        artifact_directory=interrupted,
        run_name="probed",
        validation_interval=20,
        hook=ProbeHook(),
    )
    carried = Train(
        NumpyEngine(),
        parameters,
        Regression_Loss,
        FixedBatches(Rows_Batch(rows)),
        step_count=100,
        learning_rate=0.05,
        artifact_directory=interrupted,
        run_name="probed",
        validation_interval=20,
        hook=ProbeHook(),
        resume=True,
    )
    assert len(carried.validation_curve) == 5
    assert carried.auxiliary_curves["probe"].tolist() == [20.0, 40.0, 60.0, 80.0, 100.0]
    inspected = carried.Inspect()
    assert "probe_curve" in inspected
    assert np.array_equal(inspected["probe_curve"], carried.auxiliary_curves["probe"])
    with np.load(interrupted / "probed_curves.npz") as archive:
        assert "probe_curve" in archive.files
        assert np.asarray(archive["probe_curve"]).tolist() == [20.0, 40.0, 60.0, 80.0, 100.0]


def Test_The_Loop_Makes_One_Fused_Call_A_Step_And_No_Bare_Gradient_Call() -> None:
    """asserts a step spends one fused forward, where a value and a gradient asked for apart spend two"""
    rows, parameters = Linear_Regression_Setup()
    engine = CountingEngine(NumpyEngine())
    source = DrawnRowBatches(rows, (("unit_one", rows[:10]), ("unit_two", rows[10:20])))
    Train(engine, parameters, Regression_Loss, source, step_count=10, learning_rate=0.05, validation_interval=10)
    assert engine.fused_calls == 10
    assert engine.gradient_calls == 0
    assert engine.evaluate_calls == 2
    # ten drawn batches of one array each, and the two held-out units lifted once before the loop
    assert len(engine.lifted_arrays) == 12


def Test_Every_Array_The_Loss_Sees_Crossed_The_Lift() -> None:
    """asserts no array reaches the loss without the engine having carried it there"""
    rows, parameters = Linear_Regression_Setup()
    engine = CountingEngine(NumpyEngine())
    never_lifted: list[str] = []

    def Watching_Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        for name, array in lifted_batch.items():
            if not any(carried is array for carried in engine.lifted_arrays):
                never_lifted.append(name)
        return Regression_Loss(lifted, lifted_batch)

    Train(
        engine,
        parameters,
        Watching_Loss,
        DrawnRowBatches(rows, (("unit_one", rows[:10]),)),
        step_count=6,
        learning_rate=0.05,
        validation_interval=3,
    )
    assert engine.lifted_arrays
    assert never_lifted == []


def Test_A_Plain_Table_Is_Not_A_Source_Of_Batches() -> None:
    """asserts a bare table handed in where a source belongs is refused before any step runs"""
    rows, parameters = Linear_Regression_Setup()
    with pytest.raises(AttributeError):
        Train(
            NumpyEngine(),
            parameters,
            Regression_Loss,
            cast(BatchSource, rows),
            step_count=4,
            learning_rate=0.05,
        )


def Test_A_Validation_Schedule_Of_No_Steps_Is_Refused() -> None:
    """asserts a schedule that would never score the held-out units is refused rather than run"""
    rows, parameters = Linear_Regression_Setup()
    with pytest.raises(ValueError):
        Train(
            NumpyEngine(),
            parameters,
            Regression_Loss,
            FixedBatches(Rows_Batch(rows)),
            step_count=4,
            learning_rate=0.05,
            validation_interval=0,
        )


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Device_And_The_Width_Are_Chosen_By_Word_And_Recorded() -> None:
    """asserts the trainer builds its own engine out of house words, and writes down what it built"""
    rows, parameters = Linear_Regression_Setup()
    result = Train(
        None,
        parameters,
        Regression_Loss,
        FixedBatches(Rows_Batch(rows)),
        step_count=200,
        learning_rate=0.05,
        device="host",
        precision="single",
        validation_interval=200,
    )
    assert Resolved_Device_Name("host") == HOST_DEVICE_NAME
    assert result.manifest["device"] == HOST_DEVICE_NAME
    assert result.manifest["working_precision"] == "single"
    assert result.manifest["engine"] != "NumpyEngine"
    assert np.allclose(result.parameters.values["coefficients"], [2.0, -1.0], atol=5e-2)


@pytest.mark.skipif(not Accelerator_Is_Available(), reason="no card on this machine answers a lift")
def Test_The_Card_Is_What_The_Automatic_Choice_Reaches() -> None:
    """asserts the unasked-for choice lands on the card, at the width the store already holds"""
    rows, parameters = Linear_Regression_Setup()
    result = Train(
        None,
        parameters,
        Regression_Loss,
        FixedBatches(Rows_Batch(rows)),
        step_count=200,
        learning_rate=0.05,
        validation_interval=200,
    )
    assert Resolved_Device_Name("automatic") == ACCELERATOR_DEVICE_NAME
    assert result.manifest["device"] == ACCELERATOR_DEVICE_NAME
    assert result.manifest["working_precision"] == "single"
    assert np.allclose(result.parameters.values["coefficients"], [2.0, -1.0], atol=5e-2)


def Test_The_Result_Reports_Its_Curves_As_Named_Arrays(tmp_path: Path) -> None:
    """asserts the run's own surface is plain-word arrays, and that both curves reach the artifacts"""
    rows, parameters = Linear_Regression_Setup()
    result = Train(
        NumpyEngine(),
        parameters,
        Regression_Loss,
        FixedBatches(Rows_Batch(rows)),
        step_count=30,
        learning_rate=0.05,
        artifact_directory=tmp_path,
        run_name="named_arrays",
        validation_interval=10,
    )
    reported = result.Inspect()
    assert set(reported) == {
        "loss_curve",
        "validation_curve",
        "validation_steps",
        "parameter_coefficients",
        "parameter_offset",
    }
    for name, reported_array in reported.items():
        assert name == name.lower() and " " not in name
        assert np.asarray(reported_array).size > 0
    with np.load(tmp_path / "named_arrays_curves.npz") as archive:
        assert sorted(archive.files) == ["loss_curve", "validation_curve", "validation_steps"]
        assert np.asarray(archive["validation_steps"]).tolist() == [10.0, 20.0, 30.0]
    assert (tmp_path / "named_arrays_validation_curve.png").stat().st_size > 1000


@pytest.mark.pool
def Test_The_Thread_Reproduces_The_Affine_Floor() -> None:
    """the two-parameter affine map, trained on live pairs, against the closed form"""
    sampled_rows: list[Any] = []
    for _, cheap_field, accurate_field in Strain_Charge_Pairs("validation", limit=24):
        cheap_values = np.asarray(cheap_field.values, dtype=np.float64).reshape(-1)[::977]
        accurate_values = np.asarray(accurate_field.values, dtype=np.float64).reshape(-1)[::977]
        sampled_rows.append(np.stack([cheap_values, accurate_values], axis=1))
    rows = np.asarray(np.concatenate(sampled_rows), dtype=np.float64)
    assert rows.shape[0] > 1000

    design = np.stack([rows[:, 0], np.ones(rows.shape[0])], axis=1)
    closed_coefficients = Least_Squares_Solution(design, rows[:, 1])
    closed_error = float(
        np.linalg.norm(design @ closed_coefficients - rows[:, 1]) / np.linalg.norm(rows[:, 1])
    )

    def Affine_Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        predictions = lifted_batch["rows"][:, 0] * lifted["scale"] + lifted["offset"]
        residuals = predictions - lifted_batch["rows"][:, 1]
        return (residuals * residuals).mean()

    parameters = ParameterSet(values={"scale": np.asarray([1.0]), "offset": np.asarray([0.0])})
    result = Train(
        NumpyEngine(),
        parameters,
        Affine_Loss,
        FixedBatches(Rows_Batch(rows)),
        step_count=300,
        learning_rate=0.004,
        validation_interval=300,
    )
    trained = result.parameters.values
    predicted = np.asarray(rows[:, 0] * trained["scale"][0] + trained["offset"][0], dtype=np.float64)
    trained_error = float(np.linalg.norm(predicted - rows[:, 1]) / np.linalg.norm(rows[:, 1]))
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

"""the training loop on the engine facet, scored over exchangeable units and resumable from its own archive"""

import json
import time
from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, cast

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array
from operators.inspection import Render_Curves
from operators.substrate import (
    Adam_Step,
    AdamState,
    Device_Name_Of,
    Engine,
    Fresh_Adam_State,
    ParameterSet,
    Precision,
)
from operators.training.hardware import DeviceChoice, Training_Engine
from operators.training.sampling import BatchSource, TrainingBatch

type LiftedArrays = dict[str, Any]

type ForwardLoss = Callable[[LiftedArrays, LiftedArrays], Any]

CHECKPOINT_SUFFIX = "_checkpoint.npz"


@dataclass(frozen=True, slots=True)
class TrainingResult:
    """the best parameters the run reached, the curves it drew and the manifest that replays it"""

    parameters: ParameterSet
    loss_curve: NDArray[np.float64]
    validation_curve: NDArray[np.float64]
    validation_steps: NDArray[np.float64]
    manifest: dict[str, object]
    auxiliary_curves: dict[str, NDArray[np.float64]] = field(default_factory=dict[str, NDArray[np.float64]])


    def Inspect(self) -> dict[str, Array]:
        """the curves the run drew and the parameters it kept, under plain-word names"""
        reported: dict[str, Array] = {
            "loss_curve": self.loss_curve,
            "validation_curve": self.validation_curve,
            "validation_steps": self.validation_steps,
        }
        for name, value in self.parameters.values.items():
            reported[f"parameter_{name}"] = value
        for name, curve in self.auxiliary_curves.items():
            reported[f"{name}_curve"] = curve
        return reported


@dataclass(slots=True)
class TrainingProgress:
    """everything a run must carry across a machine dying, which is everything a checkpoint holds"""

    parameters: ParameterSet
    adam_state: AdamState
    best_parameters: ParameterSet
    best_score: float
    best_step: int
    completed_steps: int
    passes_without_gain: int
    losses: list[float]
    validation_scores: list[float]
    validation_steps: list[int]
    generator_state: str
    auxiliary_curves: dict[str, list[float]] = field(default_factory=dict[str, list[float]])


class TrainingHook(Protocol):
    """a per-step parameter projection and a per-validation named report, both folded into the run it hooks"""


    @abstractmethod
    def After_Step(self, progress: TrainingProgress) -> None: ...


    @abstractmethod
    def After_Validation(self, progress: TrainingProgress) -> dict[str, float]: ...


def Copied_Parameters(parameters: ParameterSet) -> ParameterSet:
    """a parameter set no later step can reach back into"""
    return ParameterSet(values={name: value.copy() for name, value in parameters.values.items()})


def Fresh_Progress(parameters: ParameterSet, generator: np.random.Generator) -> TrainingProgress:
    """a run that has taken no steps yet, sitting on the parameters it was handed"""
    return TrainingProgress(
        parameters=Copied_Parameters(parameters),
        adam_state=Fresh_Adam_State(parameters),
        best_parameters=Copied_Parameters(parameters),
        best_score=float("inf"),
        best_step=0,
        completed_steps=0,
        passes_without_gain=0,
        losses=[],
        validation_scores=[],
        validation_steps=[],
        generator_state=json.dumps(generator.bit_generator.state),
        auxiliary_curves={},
    )


def Lifted_Batch(engine: Engine, batch: TrainingBatch) -> LiftedArrays:
    """one batch's arrays carried onto the engine, which is the only road a batch has to a loss"""
    return {
        name: engine.Lift_Constant(cast(NDArray[np.float64], array)) for name, array in batch.arrays.items()
    }


def Loss_On(forward_loss: ForwardLoss, lifted_batch: LiftedArrays) -> Callable[[LiftedArrays], Any]:
    """the loss in the one-argument shape the engine differentiates, with a batch already bound in"""

    def Loss_Of(lifted: LiftedArrays) -> Any:
        return forward_loss(lifted, lifted_batch)

    return Loss_Of


def Unit_Scores(
    engine: Engine,
    parameters: ParameterSet,
    forward_loss: ForwardLoss,
    held_units: tuple[tuple[str, LiftedArrays], ...],
) -> dict[str, float]:
    """each held-out unit's own loss, which is what a unit-mean score is taken over"""
    return {
        unit_key: engine.Evaluate(parameters, Loss_On(forward_loss, lifted_batch))
        for unit_key, lifted_batch in held_units
    }


def Unit_Mean_Score(unit_scores: dict[str, float]) -> float:
    """the mean over exchangeable units, so a unit holding many runs cannot outvote one holding few"""
    if not unit_scores:
        raise ValueError("a validation pass needs at least one held-out unit to score over")
    return float(np.mean(np.asarray(list(unit_scores.values()), dtype=np.float64)))


def Record_Validation_Pass(
    engine: Engine,
    forward_loss: ForwardLoss,
    held_units: tuple[tuple[str, LiftedArrays], ...],
    progress: TrainingProgress,
) -> float:
    """one score over the held-out units, put on the curve and kept as the best when it is the best"""
    score = Unit_Mean_Score(Unit_Scores(engine, progress.parameters, forward_loss, held_units))
    progress.validation_scores.append(score)
    progress.validation_steps.append(progress.completed_steps)
    if score < progress.best_score:
        progress.best_score = score
        progress.best_step = progress.completed_steps
        progress.best_parameters = Copied_Parameters(progress.parameters)
        progress.passes_without_gain = 0
    else:
        progress.passes_without_gain += 1
    return score


def After_Validation_Curves(hook: TrainingHook | None, progress: TrainingProgress) -> None:
    """the hook's own named scalars for this pass, folded onto the curves they belong to"""
    if hook is None:
        return
    for name, value in hook.After_Validation(progress).items():
        progress.auxiliary_curves.setdefault(name, []).append(value)


def Write_Checkpoint(path: Path, progress: TrainingProgress) -> None:
    """the whole run to one archive, renamed into place so a death mid-write leaves the pass before it"""
    stored: dict[str, Any] = {
        "parameter_names": np.asarray(sorted(progress.parameters.values)),
        "best_validation_score": np.asarray([progress.best_score], dtype=np.float64),
        "best_step": np.asarray([progress.best_step], dtype=np.float64),
        "completed_steps": np.asarray([progress.completed_steps], dtype=np.float64),
        "passes_without_gain": np.asarray([progress.passes_without_gain], dtype=np.float64),
        "adam_step_count": np.asarray([progress.adam_state.step_count], dtype=np.float64),
        "loss_curve": np.asarray(progress.losses, dtype=np.float64),
        "validation_curve": np.asarray(progress.validation_scores, dtype=np.float64),
        "validation_steps": np.asarray(progress.validation_steps, dtype=np.float64),
        "generator_state": np.asarray(progress.generator_state),
    }
    for name in progress.parameters.values:
        stored[f"live_parameter_{name}"] = progress.parameters.values[name]
        stored[f"best_parameter_{name}"] = progress.best_parameters.values[name]
        stored[f"first_moment_{name}"] = progress.adam_state.first_moments[name]
        stored[f"second_moment_{name}"] = progress.adam_state.second_moments[name]
    for name, curve in progress.auxiliary_curves.items():
        stored[f"auxiliary_{name}"] = np.asarray(curve, dtype=np.float64)
    beside = path.parent / f"{path.name}.partial.npz"
    np.savez(beside, **stored)
    beside.replace(path)


def Read_Checkpoint(path: Path, parameters: ParameterSet) -> TrainingProgress:
    """a run back off the archive it was written to, refusing parameters it was not written for"""
    with np.load(path) as archive:
        stored_names = [str(name) for name in archive["parameter_names"]]
        if stored_names != sorted(parameters.values):
            raise ValueError(f"the checkpoint at {path} was written for {stored_names}, not for these parameters")
        held: dict[str, NDArray[np.float64]] = {
            name: np.asarray(archive[name], dtype=np.float64)
            for name in archive.files
            if name not in ("parameter_names", "generator_state")
        }
        generator_state = str(archive["generator_state"])
    # optional: a checkpoint written before a hook carried one names no auxiliary_ keys at all
    auxiliary_curves = {
        name.removeprefix("auxiliary_"): [float(recorded) for recorded in held[name]]
        for name in held
        if name.startswith("auxiliary_")
    }
    return TrainingProgress(
        parameters=ParameterSet(values={name: held[f"live_parameter_{name}"] for name in stored_names}),
        adam_state=AdamState(
            first_moments={name: held[f"first_moment_{name}"] for name in stored_names},
            second_moments={name: held[f"second_moment_{name}"] for name in stored_names},
            step_count=int(held["adam_step_count"][0]),
        ),
        best_parameters=ParameterSet(values={name: held[f"best_parameter_{name}"] for name in stored_names}),
        best_score=float(held["best_validation_score"][0]),
        best_step=int(held["best_step"][0]),
        completed_steps=int(held["completed_steps"][0]),
        passes_without_gain=int(held["passes_without_gain"][0]),
        losses=[float(recorded) for recorded in held["loss_curve"]],
        validation_scores=[float(recorded) for recorded in held["validation_curve"]],
        validation_steps=[int(recorded) for recorded in held["validation_steps"]],
        generator_state=generator_state,
        auxiliary_curves=auxiliary_curves,
    )


def Train(
    engine: Engine | None,
    parameters: ParameterSet,
    forward_loss: ForwardLoss,
    batch_source: BatchSource,
    step_count: int,
    learning_rate: float,
    seed: int = 20260828,
    artifact_directory: Path | None = None,
    run_name: str = "training_run",
    validation_interval: int = 50,
    patience: int = 0,
    device: DeviceChoice = "automatic",
    precision: Precision = "single",
    resume: bool = False,
    hook: TrainingHook | None = None,
) -> TrainingResult:
    """the Adam loop over drawn batches, keeping the parameters that scored best over the held-out units"""
    if validation_interval < 1:
        raise ValueError(f"a validation pass every {validation_interval} steps is not a schedule")
    chosen_engine = Training_Engine(device, precision) if engine is None else engine
    generator = np.random.default_rng(seed)
    held_units = tuple(
        (unit_key, Lifted_Batch(chosen_engine, batch)) for unit_key, batch in batch_source.Validation_Batches()
    )
    checkpoint_path: Path | None = None
    if artifact_directory is not None:
        artifact_directory.mkdir(parents=True, exist_ok=True)
        checkpoint_path = artifact_directory / f"{run_name}{CHECKPOINT_SUFFIX}"
    progress = Fresh_Progress(parameters, generator)
    resumed_from = 0
    if resume and checkpoint_path is not None and checkpoint_path.is_file():
        progress = Read_Checkpoint(checkpoint_path, parameters)
        resumed_from = progress.completed_steps
    # the draw is replayed from where the checkpoint left it, so one seed still stands for the whole run
    generator.bit_generator.state = json.loads(progress.generator_state)

    stopped_early = False
    loop_started_at = time.perf_counter()
    while progress.completed_steps < step_count:
        lifted_batch = Lifted_Batch(chosen_engine, batch_source.Next_Batch(generator))
        # the fused call spends one forward where a value and a gradient asked for apart spend two
        loss_value, gradients = chosen_engine.Value_And_Gradients(
            progress.parameters, Loss_On(forward_loss, lifted_batch)
        )
        progress.parameters = Adam_Step(
            progress.parameters, gradients, progress.adam_state, learning_rate=learning_rate
        )
        if hook is not None:
            hook.After_Step(progress)
        # the loss on the curve is the one the gradient was taken at, which is the one the fused call hands back
        progress.losses.append(loss_value)
        progress.completed_steps += 1
        if progress.completed_steps % validation_interval and progress.completed_steps != step_count:
            continue
        progress.generator_state = json.dumps(generator.bit_generator.state)
        Record_Validation_Pass(chosen_engine, forward_loss, held_units, progress)
        After_Validation_Curves(hook, progress)
        if checkpoint_path is not None:
            Write_Checkpoint(checkpoint_path, progress)
        if patience > 0 and progress.passes_without_gain >= patience:
            stopped_early = True
            break
    if not progress.validation_scores:
        Record_Validation_Pass(chosen_engine, forward_loss, held_units, progress)
        After_Validation_Curves(hook, progress)
    wall_clock_seconds = time.perf_counter() - loop_started_at

    loss_curve = np.asarray(progress.losses, dtype=np.float64)
    validation_curve = np.asarray(progress.validation_scores, dtype=np.float64)
    validation_steps = np.asarray(progress.validation_steps, dtype=np.float64)
    manifest: dict[str, object] = {
        "run_name": run_name,
        "step_count": step_count,
        "completed_steps": progress.completed_steps,
        "resumed_from_step": resumed_from,
        "learning_rate": learning_rate,
        "seed": seed,
        "engine": type(chosen_engine).__name__,
        "device": Device_Name_Of(chosen_engine),
        "working_precision": chosen_engine.working_precision,
        "validation_interval": validation_interval,
        "patience": patience,
        "stopped_early": stopped_early,
        "validation_unit_count": len(held_units),
        "best_validation_score": progress.best_score,
        "best_step": progress.best_step,
        "final_loss": float(loss_curve[-1]) if loss_curve.size else None,
        "parameter_names": sorted(progress.best_parameters.values),
        "wall_clock_seconds": wall_clock_seconds,
        "hook_present": hook is not None,
    }
    auxiliary_curves = {
        name: np.asarray(curve, dtype=np.float64) for name, curve in progress.auxiliary_curves.items()
    }
    if artifact_directory is not None:
        # a plain dict, typed loosely, so an arbitrary hook-chosen name never collides with a keyword savez owns
        curve_arrays: dict[str, Any] = {
            "loss_curve": loss_curve,
            "validation_curve": validation_curve,
            "validation_steps": validation_steps,
        }
        for name, curve in auxiliary_curves.items():
            curve_arrays[f"{name}_curve"] = curve
        np.savez(artifact_directory / f"{run_name}_curves.npz", **curve_arrays)
        (artifact_directory / f"{run_name}_manifest.json").write_text(json.dumps(manifest, indent=1))
        Render_Curves(
            np.arange(loss_curve.shape[0], dtype=np.float64),
            {"training_loss": loss_curve},
            artifact_directory / f"{run_name}_curves.png",
            run_name,
            "step",
            "loss",
        )
        Render_Curves(
            validation_steps,
            {"validation_score": validation_curve},
            artifact_directory / f"{run_name}_validation_curve.png",
            run_name,
            "step",
            "unit mean loss",
        )
    return TrainingResult(
        parameters=progress.best_parameters,
        loss_curve=loss_curve,
        validation_curve=validation_curve,
        validation_steps=validation_steps,
        manifest=manifest,
        auxiliary_curves=auxiliary_curves,
    )

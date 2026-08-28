"""the training loop on the engine facet, emitting inspectable curve artifacts"""

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from operators.inspection.plots import Render_Curves
from operators.substrate.engine import Engine, ParameterSet
from operators.substrate.optimize import Adam_Step, Fresh_Adam_State


@dataclass(frozen=True, slots=True)
class TrainingResult:
    """the trained parameters, the loss curve and the run manifest"""

    parameters: ParameterSet
    loss_curve: NDArray[np.float64]
    manifest: dict[str, object]


def Train(
    engine: Engine,
    parameters: ParameterSet,
    forward_loss: Callable[[dict[str, Any], Any], Any],
    batches: Sequence[Any],
    step_count: int,
    learning_rate: float,
    seed: int = 20260828,
    artifact_directory: Path | None = None,
    run_name: str = "training_run",
) -> TrainingResult:
    """the Adam loop over the batches, its loss curve stored as inspectable artifacts"""
    state = Fresh_Adam_State(parameters)
    losses: list[float] = []
    for training_step in range(step_count):
        # the batches cycle, so a step count past their number is another pass over them
        batch = batches[training_step % len(batches)]
        # a plain array is lifted onto the engine, anything already lifted is left alone
        if isinstance(batch, np.ndarray):
            lifted_batch = engine.Lift_Constant(cast(NDArray[np.float64], batch))
        else:
            lifted_batch = batch

        def Loss_Of(lifted: dict[str, Any]) -> Any:
            return forward_loss(lifted, lifted_batch)

        gradients = engine.Gradients(parameters, Loss_Of)
        parameters = Adam_Step(parameters, gradients, state, learning_rate=learning_rate)
        # the recorded loss is the one after the step, so the curve shows what was gained
        losses.append(engine.Evaluate(parameters, Loss_Of))
    loss_curve = np.asarray(losses, dtype=np.float64)
    manifest: dict[str, object] = {
        "run_name": run_name,
        "step_count": step_count,
        "learning_rate": learning_rate,
        "seed": seed,
        "engine": type(engine).__name__,
        "final_loss": float(loss_curve[-1]) if loss_curve.size else None,
        "parameter_names": sorted(parameters.values),
    }
    if artifact_directory is not None:
        artifact_directory.mkdir(parents=True, exist_ok=True)
        np.savez(artifact_directory / f"{run_name}_curves.npz", loss_curve=loss_curve)
        (artifact_directory / f"{run_name}_manifest.json").write_text(json.dumps(manifest, indent=1))
        Render_Curves(
            np.arange(loss_curve.shape[0], dtype=np.float64),
            {"training_loss": loss_curve},
            artifact_directory / f"{run_name}_curves.png",
            run_name,
            "step",
            "loss",
        )
    return TrainingResult(parameters=parameters, loss_curve=loss_curve, manifest=manifest)

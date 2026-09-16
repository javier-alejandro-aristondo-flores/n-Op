"""the staged training protocol every member runs: a divergence probe, then three stages at decaying rates, each resumable"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.substrate import Engine, ParameterSet
from operators.training.loop import Read_Checkpoint, Train, TrainingHook
from operators.training.sampling import BatchSource

DEFAULT_STAGE_FRACTIONS = (0.3, 0.3, 0.4)
DEFAULT_PEAK_LEARNING_RATE = 1e-3
DEFAULT_PROBE_STEPS = 200
DEFAULT_VALIDATION_INTERVAL = 100
DEFAULT_FINAL_STAGE_PATIENCE = 15


def Staged_Step_Counts(
    step_count: int, fractions: tuple[float, float, float] = DEFAULT_STAGE_FRACTIONS
) -> tuple[int, int, int]:
    """a step budget split across three stages, the last absorbing whatever rounding leaves behind"""
    first_stage = round(fractions[0] * step_count)
    second_stage = round(fractions[1] * step_count)
    return first_stage, second_stage, step_count - first_stage - second_stage


def Sane_Loss_Curve(loss_curve: NDArray[np.float64], validation_curve: NDArray[np.float64]) -> bool:
    """every recorded loss and validation score stayed finite, and neither run away from where it started"""
    if loss_curve.size == 0 or validation_curve.size == 0:
        return False
    if not (bool(np.all(np.isfinite(loss_curve))) and bool(np.all(np.isfinite(validation_curve)))):
        return False
    # a single-example batch is noisy, so this asks only that nothing blew up, not that every step improved
    return bool(loss_curve[-1] < 10.0 * loss_curve[0] + 1.0) and bool(validation_curve[-1] < 10.0 * validation_curve[0] + 1.0)


def Staged_Training(
    engine: Engine,
    parameters: ParameterSet,
    fresh_parameters: Callable[[], ParameterSet],
    forward_loss: Any,
    batches: BatchSource,
    step_count: int,
    run_name: str,
    seed: int,
    artifact_directory: Path,
    hook: TrainingHook | None = None,
    stage_fractions: tuple[float, float, float] = DEFAULT_STAGE_FRACTIONS,
    peak_learning_rate: float = DEFAULT_PEAK_LEARNING_RATE,
    probe_steps: int = DEFAULT_PROBE_STEPS,
    validation_interval: int = DEFAULT_VALIDATION_INTERVAL,
    final_stage_patience: int = DEFAULT_FINAL_STAGE_PATIENCE,
) -> tuple[ParameterSet, dict[str, object]]:
    """the divergence probe then three stages at decaying rates, every piece resuming from its own checkpoint"""
    stage_step_counts = Staged_Step_Counts(step_count, stage_fractions)
    probe_step_count = min(probe_steps, stage_step_counts[0])
    probe_name = f"{run_name}_probe"
    probe_manifest_path = artifact_directory / f"{probe_name}_manifest.json"
    if probe_manifest_path.is_file():
        # a probe that already ran is not run again after a power loss, its verdict and rate are read back instead
        chosen_peak_rate = float(json.loads(probe_manifest_path.read_text())["learning_rate"])
        probe_checkpoint = artifact_directory / f"{probe_name}_checkpoint.npz"
        if probe_checkpoint.is_file():
            parameters = Read_Checkpoint(probe_checkpoint, parameters).parameters
    else:
        chosen_peak_rate = peak_learning_rate
        probe_result = Train(
            engine, parameters, forward_loss, batches, step_count=probe_step_count, learning_rate=chosen_peak_rate,
            seed=seed, artifact_directory=artifact_directory, run_name=probe_name,
            validation_interval=probe_step_count, patience=0, hook=hook,
        )
        if not Sane_Loss_Curve(probe_result.loss_curve, probe_result.validation_curve):
            chosen_peak_rate = peak_learning_rate * 0.3
            probe_result = Train(
                engine, fresh_parameters(), forward_loss, batches, step_count=probe_step_count,
                learning_rate=chosen_peak_rate, seed=seed, artifact_directory=artifact_directory,
                run_name=probe_name, validation_interval=probe_step_count, patience=0, resume=False, hook=hook,
            )
            if not Sane_Loss_Curve(probe_result.loss_curve, probe_result.validation_curve):
                raise RuntimeError(
                    "the loss is non-finite or diverging at both the peak and the reduced rate within the probe"
                )
        parameters = probe_result.parameters
    stage_rates = (chosen_peak_rate, chosen_peak_rate / 3.0, chosen_peak_rate / 9.0)
    manifest: dict[str, object] = {"probe_learning_rate": chosen_peak_rate, "probe_steps": probe_step_count}
    for stage_index, (rate, stage_steps) in enumerate(zip(stage_rates, stage_step_counts, strict=True)):
        is_final_stage = stage_index == len(stage_step_counts) - 1
        # every stage resumes its own checkpoint, so a relaunch skips finished stages and continues a partial one
        result = Train(
            engine, parameters, forward_loss, batches, step_count=stage_steps, learning_rate=rate,
            seed=seed + stage_index, artifact_directory=artifact_directory,
            run_name=f"{run_name}_stage{stage_index}", validation_interval=validation_interval,
            patience=final_stage_patience if is_final_stage else 0, resume=True, hook=hook,
        )
        parameters = result.parameters
        manifest[f"stage_{stage_index}"] = result.manifest
    return parameters, manifest

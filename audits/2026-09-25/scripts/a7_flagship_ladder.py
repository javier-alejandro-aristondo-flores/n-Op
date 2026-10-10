"""A7, the flagship's rungs: each saved run re-scored on fold 0 by its own inference path and this audit's own scoring, the explicit rung first as the control"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

BASELINE = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
sys.path.insert(0, str(BASELINE))

import operators.training  # noqa: E402
import operators.factorized_fourier.report as flagship_report  # noqa: E402


def Tripwire(name: str):
    """a stand-in that refuses, so nothing in this job can train or write"""
    def Refuse(*_: object, **__: object) -> None:
        raise RuntimeError(f"A7 tripwire: {name} was called")
    return Refuse


for module in (operators.training, flagship_report):
    for name in dir(module):
        # the Write_Back_ names only copy saved weights into the in-memory member, so they are let through
        if name.startswith("Write_Back_"):
            continue
        if name in ("Train", "Staged_Training", "Main") or name.startswith(("Write_", "Train_", "Probe_")):
            setattr(module, name, Tripwire(f"{module.__name__}.{name}"))

from operators.evaluation import CubicBlock  # noqa: E402
from operators.framework import GridSpec  # noqa: E402
from operators.training import Field_From_Archive  # noqa: E402

TRAINING = Path("/Pool/VASP_DATA/_derived/_training/factorized_fourier")
STORE = Path("/Pool/VASP_DATA/_derived")
CHANNELS = ("electron_localization_up", "electron_localization_down")
RUNGS = (("explicit", "elf_fold0_explicit_35505", 0.002170), ("explicit_matched", "elf_fold0_explicit_matched_35505", 0.01004),
         ("weight_tied", "elf_fold0_weight_tied_35505", 0.002966), ("weight_tied_injected", "elf_fold0_weight_tied_injected_35505", 0.002706))
STARTED = time.time()


def Log(message: str) -> None:
    """a timestamped line, flushed at once"""
    print(f"[{time.time() - STARTED:7.1f}s] {message}", flush=True)


def Unit_Median(rows: list[tuple[str, float]]) -> tuple[float, int]:
    """the median over units of each unit's median, and the unit count"""
    by_unit: dict[str, list[float]] = defaultdict(list)
    for unit, value in rows:
        by_unit[unit].append(value)
    medians = [float(np.median(values)) for _, values in sorted(by_unit.items())]
    return float(np.median(medians)), len(medians)


def Main() -> None:
    """scores every rung and prints each against its reported value"""
    block = CubicBlock()
    Log(f"block: {len(block.evaluation)} evaluation runs in {len({block.unit_of[i] for i in block.evaluation})} units")
    truths = {}
    inputs = {}
    for identifier in block.evaluation:
        with np.load(STORE / block.campaign_of[identifier] / f"{identifier}.npz") as archive:
            inputs[identifier] = Field_From_Archive(archive, ("charge_density", "magnetization_density"))
            truths[identifier] = {channel: np.asarray(archive[channel], dtype=np.float64) for channel in CHANNELS}
    results = {}
    for configuration, run_name, reported in [rung for rung in RUNGS if rung[0] == sys.argv[2]]:
        checkpoint = flagship_report.Latest_Stage_Checkpoint(TRAINING, run_name)
        member, progress = flagship_report.Load_Trained_Member(checkpoint, block, "localization", configuration)
        manifest = json.loads((TRAINING / checkpoint.name.replace("_checkpoint.npz", "_manifest.json")).read_text())
        names_match = sorted(manifest.get("parameter_names", [])) == sorted(progress.best_parameters.values)
        Log(f"{configuration}: {checkpoint.name}, best step {progress.best_step}, best validation {progress.best_score:.4e},"
            f" parameter names match the manifest: {names_match}")
        mae_rows, l2_rows = [], []
        for count, identifier in enumerate(block.evaluation, start=1):
            predicted = np.asarray(member(inputs[identifier], GridSpec((40, 40, 40))).values, dtype=np.float64)
            for index, channel in enumerate(CHANNELS):
                truth = truths[identifier][channel]
                mae_rows.append((block.unit_of[identifier], float(np.mean(np.abs(predicted[index] - truth)))))
                l2_rows.append((block.unit_of[identifier], float(np.linalg.norm(predicted[index] - truth) / np.linalg.norm(truth))))
            if count == 3 and configuration == "explicit":
                # determinism: the same three runs predicted again must match to the last bit
                again = [np.asarray(member(inputs[i], GridSpec((40, 40, 40))).values) for i in block.evaluation[:3]]
                first = [np.asarray(member(inputs[i], GridSpec((40, 40, 40))).values) for i in block.evaluation[:3]]
                Log(f"  determinism on three runs: max difference {max(float(np.max(np.abs(a - b))) for a, b in zip(again, first)):.3e}")
        mae, units = Unit_Median(mae_rows)
        l2, _ = Unit_Median(l2_rows)
        results[configuration] = {"run": run_name, "checkpoint": checkpoint.name, "best_step": progress.best_step,
                                  "best_validation": progress.best_score, "mae": mae, "relative_l2": l2, "units": units,
                                  "rows": len(mae_rows), "reported_mae": reported}
        Log(f"  {configuration}: MAE {mae:.6f} (reported {reported}), relative L2 {l2:.6f}, {units} units, {len(mae_rows)} rows")
    Path(sys.argv[1]).write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    Main()

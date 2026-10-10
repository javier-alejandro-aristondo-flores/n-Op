"""A7, the two-input network and its density-alone twin: each saved run re-scored on fold 0 by its own inference path and this audit's own scoring"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

BASELINE = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
sys.path.insert(0, str(BASELINE))

import operators.training  # noqa: E402
import operators.multiple_input_operator_network.report as member_report  # noqa: E402

for module in (operators.training, member_report):
    for name in dir(module):
        if name.startswith("Write_Back_"):
            continue
        if name in ("Train", "Staged_Training", "Main", "Cost_Probe") or name.startswith(("Write_", "Train_", "Probe_")):
            def Refuse(*_: object, __name: str = f"{module.__name__}.{name}", **__: object) -> None:
                raise RuntimeError(f"A7 tripwire: {__name} was called")
            setattr(module, name, Refuse)

from operators.evaluation import CubicBlock  # noqa: E402
from operators.framework import GridFunction  # noqa: E402

STARTED = time.time()
REPORTED = {"member": {"mae": 0.016454, "relative_l2": 0.069531}, "twin": {"mae": 0.014553, "relative_l2": 0.070017}}


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
    """scores the member and the twin and prints each against its reported values"""
    block = CubicBlock()
    results = {}
    for label, run_name, twin in (("twin", member_report.TWIN_RUN_NAME, True), ("member", member_report.MEMBER_RUN_NAME, False)):
        member = member_report.Load_Trained_Member(run_name, twin)
        Log(f"{label}: loaded {run_name}")
        mae_rows, l2_rows = [], []
        for example in member_report.Cubic_Block_Examples(member_report.EVALUATION_FOLDS):
            shape = example.target_function.values.shape[1:]
            produced = member(example.input_function, member_report.GridSpec((int(shape[0]), int(shape[1]), int(shape[2]))))
            assert isinstance(produced, GridFunction)
            predicted = np.asarray(produced.values, dtype=np.float64)
            truth = np.asarray(example.target_function.values, dtype=np.float64)
            unit = block.unit_of[example.identifier]
            for channel in range(predicted.shape[0]):
                difference = predicted[channel] - truth[channel]
                mae_rows.append((unit, float(np.mean(np.abs(difference)))))
                l2_rows.append((unit, float(np.linalg.norm(difference) / np.linalg.norm(truth[channel]))))
        mae, units = Unit_Median(mae_rows)
        l2, _ = Unit_Median(l2_rows)
        results[label] = {"run": run_name, "mae": mae, "relative_l2": l2, "units": units, "rows": len(mae_rows), "reported": REPORTED[label]}
        Log(f"  {label}: MAE {mae:.6f} (reported {REPORTED[label]['mae']}), relative L2 {l2:.6f} (reported {REPORTED[label]['relative_l2']}), {units} units, {len(mae_rows)} rows")
    improvement = 1.0 - results["member"]["mae"] / results["twin"]["mae"]
    Log(f"member against twin on MAE: {100 * improvement:.1f}% (reported -13.1%); on relative L2: {100 * (1 - results['member']['relative_l2'] / results['twin']['relative_l2']):.2f}%")
    Path(sys.argv[1]).write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    Main()

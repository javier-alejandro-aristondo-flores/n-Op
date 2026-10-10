"""A7, the Galerkin transformer's gate run: re-scored by its own evaluation path against its two stage-one floors, medians recomputed here"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

BASELINE = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
sys.path.insert(0, str(BASELINE))

import operators.training  # noqa: E402
import operators.galerkin_transformer.report as gate_report  # noqa: E402

for module in (operators.training, gate_report):
    for name in dir(module):
        if name.startswith("Write_Back_"):
            continue
        if name in ("Train", "Staged_Training", "Main", "Cost_Probe") or name.startswith(("Write_", "Train_", "Probe_")):
            def Refuse(*_: object, __name: str = f"{module.__name__}.{name}", **__: object) -> None:
                raise RuntimeError(f"A7 tripwire: {__name} was called")
            setattr(module, name, Refuse)

STARTED = time.time()


def Log(message: str) -> None:
    """a timestamped line, flushed at once"""
    print(f"[{time.time() - STARTED:7.1f}s] {message}", flush=True)


def Unit_Median(rows: list, metric: str = "relative_l2") -> tuple[float, int]:
    """the median over units of each unit's median"""
    by_unit: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_unit[row.unit_key].append(float(row.errors[metric]))
    medians = [float(np.median(values)) for _, values in sorted(by_unit.items())]
    return float(np.median(medians)), len(medians)


def Main() -> None:
    """prints the floors, the member's two comparison medians, the mean field and the input dependence"""
    copy_rows = gate_report.Nearest_Angle_Copy_Rows(evaluation_fold=0)
    interpolation_rows = gate_report.Linear_In_Angle_Interpolation_Rows()
    Log(f"floors: nearest-angle copy {Unit_Median(copy_rows)[0]:.4f} (reported 0.0853), interpolation {Unit_Median(interpolation_rows)[0]:.4f} (reported 0.0264)")
    data = gate_report.FloorData(copy_rows=copy_rows, interpolation_rows=interpolation_rows, ridge_rows=[])
    evaluation = gate_report.Evaluated_Gate_Run("perovskite_gate_v2_52283", data)
    copy_median, copy_units = Unit_Median(evaluation.copy_comparison_rows)
    interpolation_median, interpolation_units = Unit_Median(evaluation.interpolation_comparison_rows)
    result = {"member_on_copy_population": copy_median, "copy_units": copy_units,
              "member_on_interpolation_levels": interpolation_median, "interpolation_units": interpolation_units,
              "mean_field": evaluation.mean_field_relative_l2_median, "input_dependence": evaluation.input_dependence,
              "copy_verdict": evaluation.copy_verdict.verdict, "interpolation_verdict": evaluation.interpolation_verdict.verdict}
    Log(f"member: {copy_median:.4f} on {copy_units} copy units (reported 0.1780), {interpolation_median:.4f} on {interpolation_units} levels (reported 0.1191);"
        f" mean field {result['mean_field']:.4f} (reported 0.1755); input dependence {result['input_dependence']:.3g} (reported 1.4e-1);"
        f" verdicts {result['copy_verdict']} and {result['interpolation_verdict']}")
    Path(sys.argv[1]).write_text(json.dumps(result, indent=1))


if __name__ == "__main__":
    Main()

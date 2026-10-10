"""A7, the correction network: rebuilt from its bases and its final stage's checkpoint without the training driver, scored on the test orbits here"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

BASELINE = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
sys.path.insert(0, str(BASELINE))

import operators.training  # noqa: E402
import operators.residual_correction.report as correction_report  # noqa: E402
from operators.training import Read_Checkpoint  # noqa: E402

for module in (operators.training, correction_report):
    for name in dir(module):
        if name.startswith("Write_Back_"):
            continue
        if name in ("Train", "Staged_Training", "Main", "Trained_Member_Predictions") or name.startswith(("Write_", "Train_", "Probe_")):
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
    """the member's test median against identity and the coefficient ridge, as the report computes them"""
    report = correction_report
    train, validation, test = report.CorrectionBlock("train"), report.CorrectionBlock("validation"), report.CorrectionBlock("test")
    _, floor_comparisons, _, correction_basis, cheap_basis, kill_bar = report.Floor_Lines(train, validation, test)
    Log(f"blocks: train {len(train.unit_keys)}, validation {len(validation.unit_keys)}, test {len(test.unit_keys)} entries; kill bar {kill_bar}")
    _, voxel_scale = report.Pointwise_Statistics(train.correction)
    input_scale = report.Guarded_Spread(report.Project(cheap_basis, train.cheap))
    backbone = report.ProjectionBackbone(cheap_basis, correction_basis, report.COMMON_GRID_SHAPE, voxel_scale, input_scale, report.SEED)
    member = report.ResidualCorrection(backbone)
    constants = member.Constant_Values()
    checkpoint = report.TRAINING_ARTIFACT_PATH / f"{report.RUN_NAME_PREFIX}_stage2_checkpoint.npz"
    progress = Read_Checkpoint(checkpoint, report.ParameterSet(values=member.Parameter_Values()))
    values = {**progress.best_parameters.values, **constants}
    Log(f"checkpoint {checkpoint.name}: best step {progress.best_step}, best validation {progress.best_score:.4e}")
    correction = np.asarray(member.Forward_Correction(values, report.Project(cheap_basis, test.cheap)), dtype=np.float64)
    member_rows = test.Scored(test.cheap + correction)
    identity_rows = test.Scored(report.Identity_Predictions(test))
    member_median, units = Unit_Median(member_rows)
    identity_median, _ = Unit_Median(identity_rows)
    ridge = {c.group_name: c.member_median for c in floor_comparisons}
    result = {"member": member_median, "units": units, "identity": identity_median, "improvement": 1 - member_median / identity_median,
              "ridge_cheap_coefficients": ridge.get("ridge_cheap_coefficients"), "floor_medians": ridge}
    if result["ridge_cheap_coefficients"]:
        result["ratio_to_ridge"] = member_median / result["ridge_cheap_coefficients"]
    Log(f"member {member_median:.6f} (reported 0.002079), identity {identity_median:.6f} (reported 0.011131), improvement {100 * result['improvement']:.1f}% (reported 81.3%),"
        f" ratio to the coefficient ridge {result.get('ratio_to_ridge', float('nan')):.0f}x (reported 406x), {units} units")
    Path(sys.argv[1]).write_text(json.dumps(result, indent=1, default=str))


if __name__ == "__main__":
    Main()

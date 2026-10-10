"""A7, the manifold decoder: rebuilt from its training caches and its final stage's checkpoint without the training driver, scored on its three populations"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

BASELINE = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
sys.path.insert(0, str(BASELINE))

import operators.training  # noqa: E402
import operators.nonlinear_manifold_decoder.report as manifold_report  # noqa: E402
from operators.training import Read_Checkpoint  # noqa: E402
from operators.substrate import ParameterSet  # noqa: E402

for module in (operators.training, manifold_report):
    for name in dir(module):
        if name.startswith("Write_Back_"):
            continue
        if name in ("Train", "Staged_Training", "Main", "Trained_Manifold_Member") or name.startswith(("Write_", "Train_", "Probe_")):
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
    """the member's arm, headline and every-shape medians and its transfer ratio"""
    report = manifold_report
    card = report.Card_Named("strain_to_charge")
    training_cache = report.Field_Cache_With_Functional_Feature(report.Build_Field_Cache(card, "train"))
    parameter_width = int(training_cache.fields[0].parameters.shape[0])
    spreads = report.Parameter_Spreads(training_cache)
    channel_mean, channel_deviation = report.Global_Statistics(training_cache)
    member = report.Manifold_Network(parameter_width, report.BRANCH_HIDDEN_WIDTHS, report.LATENT_WIDTH,
                                     report.DECODER_HIDDEN_WIDTHS, report.FOURIER_ORDERS, seed=report.SEED)
    checkpoint = report.TRAINING_ARTIFACT_PATH / "manifold_stage2_checkpoint.npz"
    progress = Read_Checkpoint(checkpoint, ParameterSet(values=member.Parameter_Values()))
    for name, value in progress.best_parameters.values.items():
        if name in member.branch.parameter_values:
            member.branch.parameter_values[name] = value
        if name in member.decoder.parameter_values:
            member.decoder.parameter_values[name] = value
    Log(f"checkpoint {checkpoint.name}: best step {progress.best_step}, best validation {progress.best_score:.4e}")
    population = report.Arm_Floor_Population(report.All_Strain_Arms())
    arm_runs = report.Manifold_Member_Arm_Predictions(member, spreads, channel_mean, channel_deviation, population,
                                                     report.Strain_Tensor_By_Run_Path())
    arm_median, arm_units = Unit_Median(arm_runs)
    bracketing_median, _ = Unit_Median(population.bracketing_rows)
    Log(f"arm levels: member {arm_median:.6f} on {arm_units} levels (reported 0.002452); bracketing floor {bracketing_median:.6f} (reported 0.000911)")
    # the shear arms' levels average three differently oriented fields, so the comparison is repeated without them
    mixed_arms = ("one_angle_shear", "two_angle_shear")
    clean_member, clean_units = Unit_Median([row for row in arm_runs if row.family not in mixed_arms])
    clean_floor, _ = Unit_Median([row for row in population.bracketing_rows if row.family not in mixed_arms])
    shear_member, shear_units = Unit_Median([row for row in arm_runs if row.family in mixed_arms])
    shear_floor, _ = Unit_Median([row for row in population.bracketing_rows if row.family in mixed_arms])
    Log(f"without the shear arms: member {clean_member:.6f} vs floor {clean_floor:.6f} on {clean_units} levels,"
        f" improvement {100 * (1 - clean_member / clean_floor):.1f}% (bar 33.3%); shear arms alone: member {shear_member:.6f}"
        f" vs floor {shear_floor:.6f} on {shear_units} levels")
    in_training = set()
    for unit in __import__("json").load(open(BASELINE / "operators/data/splits/strain_atlas_holdout.json")).values():
        if unit["assignment"] == "train":
            in_training.update(unit["run_paths"])
    held_out_levels = {f"{name}_{level}" for name, level in population.eval_keys
                       if not any(run in in_training for run in population.arm_by_name[name].runs_by_level[level])}
    out_member, out_units = Unit_Median([row for row in arm_runs if row.unit_key in held_out_levels])
    out_floor, _ = Unit_Median([row for row in population.bracketing_rows if row.unit_key in held_out_levels])
    Log(f"levels holding no training run: member {out_member:.6f} vs floor {out_floor:.6f} on {out_units} levels,"
        f" improvement {100 * (1 - out_member / out_floor):.1f}%")
    test_block = report.ManifoldBlock("test")
    headline_runs = test_block.Scored(report.Manifold_Grid_Predictions(member, spreads, channel_mean, channel_deviation, test_block))
    headline_median, headline_units = Unit_Median(headline_runs)
    every_shape_cache = report.Field_Cache_With_Functional_Feature(report.Build_Field_Cache(card, "test"))
    every_shape_runs = report.Manifold_Every_Shape_Predictions(member, spreads, channel_mean, channel_deviation, every_shape_cache)
    every_median, every_units = Unit_Median(every_shape_runs)
    transfer = report.Transfer_Comparison(every_shape_runs)
    result = {"arm": arm_median, "arm_units": arm_units, "bracketing": bracketing_median, "headline": headline_median,
              "headline_units": headline_units, "every_shape": every_median, "every_shape_units": every_units,
              "transfer_off": transfer.member_median, "transfer_on": transfer.floor_median, "transfer_verdict": transfer.verdict}
    Log(f"headline {headline_median:.6f} on {headline_units} units (reported 0.002424); every shape {every_median:.6f} on {every_units} units (reported 0.002795);"
        f" transfer {transfer.member_median:.6f} vs {transfer.floor_median:.6f} = {transfer.member_median / transfer.floor_median:.3f}x (reported 1.316x), {transfer.verdict}")
    Path(sys.argv[1]).write_text(json.dumps(result, indent=1))


if __name__ == "__main__":
    Main()

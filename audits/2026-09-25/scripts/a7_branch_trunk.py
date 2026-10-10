"""A7, the branch-trunk network: the canonical configuration for both functionals and the energy trunk with its ablation, rebuilt from their final stages' checkpoints and scored by the report's own prediction paths"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

BASELINE = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
sys.path.insert(0, str(BASELINE))

import operators.training  # noqa: E402
import operators.deep_operator_network.report as trunk_report  # noqa: E402
from operators.training import Read_Checkpoint  # noqa: E402
from operators.substrate import ParameterSet  # noqa: E402

for module in (operators.training, trunk_report):
    for name in dir(module):
        if name.startswith("Write_Back_"):
            continue
        if name in ("Train", "Staged_Training", "Main") or name.startswith(("Write_", "Train_", "Trained_", "Probe_")):
            def Refuse(*_: object, __name: str = f"{module.__name__}.{name}", **__: object) -> None:
                raise RuntimeError(f"A7 tripwire: {__name} was called")
            setattr(module, name, Refuse)

STARTED = time.time()
REPORTED = {"cheap": (0.001896, 0.002339), "accurate": (0.002413, 0.002766)}


def Log(message: str) -> None:
    """a timestamped line, flushed at once"""
    print(f"[{time.time() - STARTED:7.1f}s] {message}", flush=True)


def Unit_Median(rows: list, metric: str) -> tuple[float, int]:
    """the median over units of each unit's median"""
    by_unit: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_unit[row.unit_key].append(float(row.errors[metric]))
    medians = [float(np.median(values)) for _, values in sorted(by_unit.items())]
    return float(np.median(medians)), len(medians)


def Loaded(member, readout, checkpoint: Path):
    """the checkpoint's best parameters folded into the branch and the readout, as the training function does"""
    progress = Read_Checkpoint(checkpoint, ParameterSet(values=member.Parameter_Values()))
    for name, value in progress.best_parameters.values.items():
        if name in member.branch.parameter_values:
            member.branch.parameter_values[name] = value
        if name in readout.parameter_values:
            readout.parameter_values[name] = value
    return progress


def Main() -> None:
    """the canonical rows then the energy-trunk rows, each against its reported value"""
    report = trunk_report
    results: dict[str, object] = {}
    card = report.Card_Named("strain_to_charge")
    for functional in ("cheap", "accurate"):
        training_cache = report.Functional_Field_Cache(card, "train", functional)
        spreads = report.Parameter_Spreads(training_cache)
        mean, deviation = report.Global_Statistics(training_cache)
        member = report.Canonical_Network(int(training_cache.fields[0].parameters.shape[0]), report.CANONICAL_BRANCH_HIDDEN_WIDTHS,
                                          report.CANONICAL_LATENT_WIDTH, report.CANONICAL_TRUNK_HIDDEN_WIDTHS)
        progress = Loaded(member, member.basis_readout, report.TRAINING_ARTIFACT_PATH / f"canonical_{functional}_stage2_checkpoint.npz")
        test_common = report.StrainBlock("test", functional)
        common_rows = test_common.Scored(report.Canonical_Common_Grid_Predictions(member, spreads, mean, deviation, test_common))
        common, common_units = Unit_Median(common_rows, "relative_l2")
        every_rows = report.Canonical_Every_Shape_Predictions(member, spreads, mean, deviation,
                                                              report.Functional_Field_Cache(card, "test", functional), functional)
        every, every_units = Unit_Median(every_rows, "relative_l2")
        results[f"canonical_{functional}"] = {"best_step": progress.best_step, "common_grid": common, "common_units": common_units,
                                              "every_shape": every, "every_shape_units": every_units, "every_shape_runs": len(every_rows),
                                              "reported": REPORTED[functional]}
        Log(f"canonical {functional}: common grid {common:.6f} on {common_units} units (reported {REPORTED[functional][0]}),"
            f" every shape {every:.6f} on {every_units} units, {len(every_rows)} runs (reported {REPORTED[functional][1]})")
    train, test = report.StateDensityBlock("train"), report.StateDensityBlock("test")
    spacing = float(test.energy_grid[1] - test.energy_grid[0])
    mask = report.Band_Edge_Mask(test.energy_grid)
    floors = {"training_mean": report.Training_Mean_Predictions(train, test.curves.shape[0]), "ridge": report.Ridge_Curve_Predictions(train, test)}
    for name, predicted in floors.items():
        rows = test.Scored(predicted, mask, spacing)
        results[f"energy_{name}"] = {metric: Unit_Median(rows, metric)[0] for metric in ("curve_l1_whole", "curve_l1_band_edge")}
    spreads = report.Parameter_Feature_Spreads(train)
    features = report.Energy_Trunk_Features(train.energy_grid, report.ENERGY_TRUNK_FOURIER_ORDERS)
    for prefix in ("energy_trunk_primary", "energy_trunk_bandedge_ablation"):
        member = report.Energy_Trunk_Network(int(train.parameters.shape[1]), report.ENERGY_TRUNK_BRANCH_HIDDEN_WIDTHS,
                                             report.ENERGY_TRUNK_LATENT_WIDTH, report.ENERGY_TRUNK_TRUNK_HIDDEN_WIDTHS,
                                             report.ENERGY_TRUNK_FOURIER_ORDERS)
        Loaded(member, member.basis_readout, report.TRAINING_ARTIFACT_PATH / f"{prefix}_stage2_checkpoint.npz")
        rows = test.Scored(report.Energy_Trunk_Predictions(member, spreads, features, test), mask, spacing)
        results[prefix] = {metric: Unit_Median(rows, metric) for metric in ("curve_l1_whole", "curve_l1_band_edge", "wasserstein_1d", "gap_edge_error")}
    Log("energy trunk (reported member 0.206 / 0.265, ablation 0.208 / 0.193, mean floor 0.392 / 0.757, ridge 0.368 / 0.518): "
        + json.dumps({k: v for k, v in results.items() if k.startswith("energy")}, default=lambda x: round(x, 4) if isinstance(x, float) else x))
    Path(sys.argv[1]).write_text(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    Main()

"""A7, the branch-trunk fixed-basis headline: the member rebuilt from the branch weights and basis its figure cache holds, since no checkpoint was kept"""

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

for module in (operators.training, trunk_report):
    for name in dir(module):
        if name.startswith("Write_Back_"):
            continue
        if name in ("Train", "Staged_Training", "Main") or name.startswith(("Write_", "Train_", "Trained_", "Probe_")):
            def Refuse(*_: object, __name: str = f"{module.__name__}.{name}", **__: object) -> None:
                raise RuntimeError(f"A7 tripwire: {__name} was called")
            setattr(module, name, Refuse)

CACHE = Path("/Pool/VASP_DATA/_derived/_figures/deep_operator_network")
REPORTED = {("cheap", "principal_component"): 0.000821, ("cheap", "proper_orthogonal"): 0.000819,
            ("accurate", "principal_component"): 0.001092, ("accurate", "proper_orthogonal"): 0.001122}
STARTED = time.time()


def Log(message: str) -> None:
    """a timestamped line, flushed at once"""
    print(f"[{time.time() - STARTED:7.1f}s] {message}", flush=True)


def Main() -> None:
    """each of the four fixed-basis rows rebuilt and scored on the 40-cubed test block, orbit medians"""
    report = trunk_report
    results = {}
    for functional in ("cheap", "accurate"):
        train, test = report.StrainBlock("train", functional), report.StrainBlock("test", functional)
        voxel_mean, voxel_scale = report.Pointwise_Statistics(train.fields)
        spreads = train.parameters.std(axis=0)
        spreads[spreads == 0.0] = 1.0
        for configuration in ("principal_component", "proper_orthogonal"):
            with np.load(CACHE / functional / configuration / "inspection.npz") as archive:
                cached = {name: np.asarray(archive[name]) for name in archive.files}
            fitted_on = report.Standardized_Fields(train, voxel_mean, voxel_scale) if configuration == "proper_orthogonal" else train.fields
            basis = report.Gram_Pod(fitted_on, rank=report.BASIS_RANK)
            modes_gap = float(np.max(np.abs(np.abs(basis.modes.reshape(cached["readout.basis_modes"].shape)) - np.abs(cached["readout.basis_modes"]))))
            coefficients = report.Project(basis, fitted_on)
            coefficient_mean, coefficient_scale = coefficients.mean(axis=0), coefficients.std(axis=0)
            if configuration == "proper_orthogonal":
                member = report.Proper_Orthogonal_Network(basis, report.COMMON_GRID_SHAPE, voxel_mean, voxel_scale,
                                                          train.parameters.shape[1], report.HIDDEN_WIDTHS)
            else:
                member = report.Principal_Component_Network(basis, report.COMMON_GRID_SHAPE, train.parameters.shape[1], report.HIDDEN_WIDTHS)
            values = dict(member.Parameter_Values())
            loaded = 0
            for name in list(values):
                key = f"encoder.{name}"
                if key in cached:
                    values[name] = cached[key]
                    loaded += 1
            predicted = np.asarray(member.Forward_Coefficients(values, test.parameters / spreads), dtype=np.float64)
            rebuilt = report.Reconstruct(basis, predicted * coefficient_scale + coefficient_mean)
            if configuration == "proper_orthogonal":
                rebuilt = rebuilt * voxel_scale + voxel_mean
            rows = test.Scored(rebuilt)
            by_unit = defaultdict(list)
            for row in rows:
                by_unit[row.unit_key].append(float(row.errors["relative_l2"]))
            median = float(np.median([np.median(values_) for _, values_ in sorted(by_unit.items())]))
            reported = REPORTED[(functional, configuration)]
            results[f"{functional}_{configuration}"] = {"median": median, "units": len(by_unit), "reported": reported,
                                                        "branch_arrays_loaded": loaded, "basis_modes_gap_up_to_sign": modes_gap}
            Log(f"{functional} {configuration}: {median:.6f} on {len(by_unit)} units (reported {reported}); {loaded} branch arrays from the cache;"
                f" basis refit vs cached modes, largest gap up to sign {modes_gap:.2e}")
    Path(sys.argv[1]).write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    Main()

"""read-only checks run on 2 October 2026 for the study guide: perovskite symmetry copies, the energy-trunk copy floor, the frequency-split metric"""

import collections
import itertools
import json
import re
import sys
from collections import defaultdict

import numpy as np

BASELINE = "/home/javier/Projects/Physics/Programs/n-Op-audit-baseline"
sys.path.insert(0, BASELINE)

import operators.training  # noqa: E402
import operators.deep_operator_network.report as trunk_report  # noqa: E402
from operators.metrics import Frequency_Split_Relative_L2, Relative_L2  # noqa: E402

for module in (operators.training, trunk_report):
    for name in dir(module):
        if name.startswith("Write_Back_"):
            continue
        if name in ("Train", "Staged_Training", "Main") or name.startswith(("Write_", "Train_", "Trained_", "Probe_")):
            def Refuse(*_: object, __name: str = f"{module.__name__}.{name}", **__: object) -> None:
                raise RuntimeError(f"tripwire: {__name} was called")
            setattr(module, name, Refuse)


FOLDS = json.load(open(f"{BASELINE}/operators/data/splits/perovskite_folds.json"))
ANGLE = {name: entry for name, entry in FOLDS.items() if entry["stratum"] == "angle"}
FIELD_CACHE: dict[str, np.ndarray] = {}


def Field(name: str) -> np.ndarray:
    """one perovskite run's stored charge density as a three-dimensional array"""
    if name not in FIELD_CACHE:
        with np.load(f"/Pool/VASP_DATA/_derived/perovskite_grid/{FOLDS[name]['run_identifiers'][0]}.npz") as archive:
            values = np.asarray(archive["charge_density"], dtype=float)
        FIELD_CACHE[name] = values.reshape(values.shape[-3:])
    return FIELD_CACHE[name]


def Best_Match(first: np.ndarray, second: np.ndarray) -> float:
    """smallest relative L2 between first and second over the 48 axis permutations and reversals of second"""
    best = np.inf
    for order in itertools.permutations(range(3)):
        moved = np.transpose(second, order)
        if moved.shape != first.shape:
            continue
        for flips in itertools.product((False, True), repeat=3):
            candidate = moved
            for axis, flip in enumerate(flips):
                if flip:
                    candidate = np.take(candidate, (-np.arange(candidate.shape[axis])) % candidate.shape[axis], axis=axis)
            best = min(best, float(np.linalg.norm(candidate - first) / np.linalg.norm(first)))
    return best


def Angle_Factors(name: str) -> tuple[float, float, float]:
    """the three angle factors written in a run's name"""
    return tuple(float(re.search(axis + r"_([0-9p]+)", name).group(1).replace("p", ".")) for axis in ("alpha", "beta", "gamma"))


def Crystal(triple: tuple[float, float, float]) -> tuple[tuple[float, ...], int]:
    """the crystal a triple names, up to axis swaps and one-edge reversals (which flip two angles to their supplements)"""
    deviations = [round(value - 1.0, 6) for value in triple]
    magnitudes = tuple(sorted(abs(value) for value in deviations))
    if any(value == 0 for value in deviations):
        return magnitudes, 0
    sign = 1
    for value in deviations:
        sign *= 1 if value > 0 else -1
    return magnitudes, sign


def Name(alpha: str, beta: str, gamma: str) -> str:
    """an angle-stratum run name"""
    return f"perovskite_a_1_b_1_c_1_alpha_{alpha}_beta_{beta}_gamma_{gamma}_angle"


def Perovskite() -> None:
    """sample pairs with a control, the crystal count, and a symmetry-aware copy floor over fold 0"""
    print("== perovskite symmetry copies ==")
    pairs = (("supplement pair (alpha 0.8 against alpha 1.2)", Name("0p8", "1", "1"), Name("1p2", "1", "1")),
             ("swap pair (alpha 0.8 beta 0.9 against alpha 0.9 beta 0.8)", Name("0p8", "0p9", "1"), Name("0p9", "0p8", "1")),
             ("control, different crystals (alpha 0.8 against alpha 0.9)", Name("0p8", "1", "1"), Name("0p9", "1", "1")))
    for label, first, second in pairs:
        as_stored = float(np.linalg.norm(Field(second) - Field(first)) / np.linalg.norm(Field(first)))
        print(f"{label}: as stored {as_stored:.2e}, best over 48 transforms {Best_Match(Field(first), Field(second)):.2e}")
    classes: dict[tuple[tuple[float, ...], int], list[str]] = defaultdict(list)
    for name in ANGLE:
        classes[Crystal(Angle_Factors(name))].append(name)
    fold_zero = [name for name, entry in ANGLE.items() if entry["fold"] == 0]
    print(f"angle-stratum runs {len(ANGLE)}, distinct crystals {len(classes)}")
    print(f"fold-0 angle runs {len(fold_zero)}, with a same-crystal run in folds 1-4: "
          f"{sum(1 for name in fold_zero if any(ANGLE[other]['fold'] != 0 for other in classes[Crystal(Angle_Factors(name))]))}, "
          f"distinct fold-0 crystals {len({Crystal(Angle_Factors(name)) for name in fold_zero})}")
    for tag in ("holdout_factor_0p8", "holdout_factor_1p2"):
        held = [name for name, entry in ANGLE.items() if tag in (entry.get("extrapolation_tags") or [])]
        covered = sum(1 for name in held if any(tag not in (ANGLE[other].get("extrapolation_tags") or []) for other in classes[Crystal(Angle_Factors(name))]))
        print(f"{tag}: angle runs held out {len(held)}, whose crystal also sits among runs not held out {covered}")
    errors = []
    for name in fold_zero:
        partners = [other for other in classes[Crystal(Angle_Factors(name))] if ANGLE[other]["fold"] != 0]
        errors.append(min(Best_Match(Field(name), Field(other)) for other in partners))
    print(f"symmetry-aware copy floor on fold 0 (each run's same-crystal training run, best transform): "
          f"median {np.median(errors):.1e}, worst {np.max(errors):.1e} over {len(errors)} runs")


def Unit_Median(rows: list, metric: str) -> float:
    """the median over units of each unit's median"""
    by_unit: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_unit[row.unit_key].append(float(row.errors[metric]))
    return float(np.median([np.median(values) for _, values in sorted(by_unit.items())]))


def Energy_Trunk_Copy() -> None:
    """the nearest-training-curve copy floor on the energy trunk's test block, with the ridge floor as the control"""
    print("== energy trunk copy floor ==")
    report = trunk_report
    train, test = report.StateDensityBlock("train"), report.StateDensityBlock("test")
    spacing = float(test.energy_grid[1] - test.energy_grid[0])
    mask = report.Band_Edge_Mask(test.energy_grid)
    ridge_rows = test.Scored(report.Ridge_Curve_Predictions(train, test), mask, spacing)
    print(f"control, ridge floor: whole window {Unit_Median(ridge_rows, 'curve_l1_whole'):.3f}, band edges {Unit_Median(ridge_rows, 'curve_l1_band_edge'):.3f}")
    spreads = np.asarray(report.Parameter_Feature_Spreads(train), dtype=float)
    distances = (((test.parameters / spreads)[:, None, :] - (train.parameters / spreads)[None, :, :]) ** 2).sum(axis=2)
    rows = test.Scored(train.curves[np.argmin(distances, axis=1)], mask, spacing)
    print(f"nearest-neighbor curve copy: whole window {Unit_Median(rows, 'curve_l1_whole'):.3f}, band edges {Unit_Median(rows, 'curve_l1_band_edge'):.3f}, "
          f"{len({row.unit_key for row in rows})} units, {train.parameters.shape[0]} training runs")


def Frequency_Split() -> None:
    """the same error along x and along z must score the same; a whole-field band must equal plain relative L2"""
    print("== frequency-split metric ==")
    size = 16
    coordinates = np.arange(size) / size
    x, y, z = np.meshgrid(coordinates, coordinates, coordinates, indexing="ij")
    truth = 2.0 + np.cos(2 * np.pi * x) + np.cos(2 * np.pi * y) + np.cos(2 * np.pi * z)
    along_x = Frequency_Split_Relative_L2(truth + 0.1 * np.cos(2 * np.pi * x), truth, 2.0)[0]
    along_z = Frequency_Split_Relative_L2(truth + 0.1 * np.cos(2 * np.pi * z), truth, 2.0)[0]
    print(f"low band, error along x {along_x:.6f}, along z {along_z:.6f}, ratio {along_x / along_z:.4f}")
    generator = np.random.default_rng(7)
    first = generator.normal(size=(size, size, size))
    second = first + 0.3 * generator.normal(size=(size, size, size))
    print(f"whole field as the low band {Frequency_Split_Relative_L2(second, first, 1e9)[0]:.6f}, plain relative L2 {Relative_L2(second, first):.6f}")


if __name__ == "__main__":
    Frequency_Split()
    Perovskite()
    Energy_Trunk_Copy()

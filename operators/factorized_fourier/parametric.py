"""the parametric variant's own arms: one strain family or one perovskite stratum, swept over levels"""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from operators.data import Perovskite_Units, POOL_ROOT, Read_Census, SplitUnit, StrainAssignment
from operators.training import Lattice_Factors_Of, Strain_Assignments_Of_Pool

type Level = tuple[float, ...]

STRAIN_ARM_NAMES = (
    "biaxial",
    "isotropic",
    "one_angle_shear",
    "three_angle_shear",
    "triaxial",
    "two_angle_shear",
    "uniaxial",
)

PEROVSKITE_ARM_NAMES = ("angle", "length")


def Strain_Level(point: str, family: str) -> Level:
    """the family's own swept parameter vector this point encodes, parsed the same way Strain_Tensor_Of reads it"""
    if family == "reference":
        return ()
    if family == "isotropic":
        return (float(point.removeprefix("Vol_")),)
    if family == "uniaxial":
        _, value = point.removeprefix("uniax_").split("_eps")
        return (float(value),)
    if family == "biaxial":
        _, value = point.removeprefix("biax_").split("_eps")
        return (float(value),)
    if family == "triaxial":
        tokens = point.split("_ex_")[1].replace("_ey_", " ").replace("_ez_", " ").split()
        return tuple(float(token) for token in tokens)
    if family == "one_angle_shear":
        _, value = point.removeprefix("shear_").split("_g")
        return (float(value),)
    if family == "two_angle_shear":
        _, remainder = point.removeprefix("shear_").split("_", 1)
        _, values = remainder.split("_g1_")
        first_value, second_value = values.split("_g2_")
        return (float(first_value), float(second_value))
    if family == "three_angle_shear":
        tokens = point.split("_g1_")[1].replace("_g2_", " ").replace("_g3_", " ").split()
        return tuple(float(token) for token in tokens)
    raise ValueError(f"{family!r} is not one of the strain atlas's own families")


def Perovskite_Level(run_path: str, stratum: str) -> Level:
    """the three lattice factors one perovskite stratum sweeps, the other three sitting at reference"""
    factors = Lattice_Factors_Of(run_path)
    return factors[:3] if stratum == "length" else factors[3:]


@dataclass(frozen=True, slots=True)
class Arm:
    """one parametric arm: every training-population run path, grouped by the level it sits at"""

    name: str
    runs_by_level: dict[Level, tuple[str, ...]]


def Strain_Arms(assignments: Sequence[StrainAssignment]) -> tuple[Arm, ...]:
    """every strain family as its own arm, the reference point and the later auxiliary sweep excluded"""
    by_family: dict[str, dict[Level, list[str]]] = {}
    for assignment in assignments:
        if assignment.family == "reference" or assignment.auxiliary:
            continue
        level = Strain_Level(assignment.point, assignment.family)
        by_family.setdefault(assignment.family, {}).setdefault(level, []).append(assignment.run_path)
    return tuple(
        Arm(family, {level: tuple(sorted(paths)) for level, paths in levels.items()})
        for family, levels in sorted(by_family.items())
    )


def Perovskite_Arms(units: Sequence[SplitUnit]) -> tuple[Arm, ...]:
    """the length and angle strata as the two perovskite arms"""
    by_stratum: dict[str, dict[Level, list[str]]] = {}
    for unit in units:
        level = Perovskite_Level(unit.run_paths[0], unit.stratum)
        by_stratum.setdefault(unit.stratum, {}).setdefault(level, []).append(unit.run_paths[0])
    return tuple(
        Arm(stratum, {level: tuple(sorted(paths)) for level, paths in levels.items()})
        for stratum, levels in sorted(by_stratum.items())
    )


def All_Strain_Arms(pool_root: Path = POOL_ROOT) -> tuple[Arm, ...]:
    """every strain-atlas arm, off the same cached assignment map the training loader already reads"""
    return Strain_Arms(Strain_Assignments_Of_Pool(pool_root))


def All_Perovskite_Arms(pool_root: Path = POOL_ROOT) -> tuple[Arm, ...]:
    """every perovskite arm, read fresh off this pool's own census"""
    units = Perovskite_Units(Read_Census(pool_root), pool_root)
    return Perovskite_Arms(units)


def Bracket_Corners(level: Level, levels: Sequence[Level]) -> tuple[Level, ...] | None:
    """the level's own 2^D bracketing corners if every one is an actual level in this arm, otherwise nothing"""
    level_set = set(levels)
    dimension = len(level)
    bounds: list[tuple[float, float]] = []
    for axis in range(dimension):
        axis_values = {candidate[axis] for candidate in level_set}
        smaller = [value for value in axis_values if value < level[axis]]
        larger = [value for value in axis_values if value > level[axis]]
        if not smaller or not larger:
            return None
        bounds.append((max(smaller), min(larger)))
    corners: list[Level] = [()]
    for axis in range(dimension):
        low, high = bounds[axis]
        corners = [corner + (low,) for corner in corners] + [corner + (high,) for corner in corners]
    resolved = tuple(corner for corner in corners if corner in level_set)
    return resolved if len(resolved) == 2**dimension else None


def Interior_Levels(arm: Arm) -> dict[Level, tuple[Level, ...]]:
    """every level in this arm with a full bracket, mapped to the corner levels its floor interpolates between"""
    levels = tuple(arm.runs_by_level)
    interior: dict[Level, tuple[Level, ...]] = {}
    for level in levels:
        corners = Bracket_Corners(level, levels)
        if corners is not None:
            interior[level] = corners
    return interior

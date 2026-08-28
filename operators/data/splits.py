"""The split engine: co-split units, deterministic fold maps, and their committed artifacts."""

import hashlib
import json
import re
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from operators.data.exclusions import Resolve_Exclusion
from operators.data.orbits import Canonical_Orbit, Orbit_Map, OrbitError, Strain_Tensor_Of
from operators.data.store import Campaign_Of, CensusRow, Run_Identifier

SPLIT_SEED = "n-op-canonical-folds-v1"

FOLD_COUNT = 5

ARTIFACT_DIRECTORY = Path(__file__).parent / "splits"

FIELD_FILE_NAMES = ("CHGCAR", "ELFCAR", "LOCPOT")


@dataclass(frozen=True, slots=True)
class SplitUnit:
    """One co-split unit: runs that must always land in the same fold."""

    key: str
    campaign: str
    stratum: str
    run_paths: tuple[str, ...]


def Stable_Fraction(split_key: str) -> float:
    """Maps a key to a deterministic fraction of one via a seeded hash."""
    digest = hashlib.sha256(f"{SPLIT_SEED}:{split_key}".encode()).digest()
    return int.from_bytes(digest[:8]) / 2.0**64


def Hard_Excluded_Paths(census_rows: Sequence[CensusRow], pool_root: Path) -> frozenset[str]:
    """Returns the runs excluded from every task before any unit is built."""
    excluded: set[str] = set()
    for identifier in ("E1", "E2", "E3", "E10"):
        excluded.update(Resolve_Exclusion(identifier, census_rows, pool_root))
    return frozenset(excluded)


def Has_Full_Fields(census_row: CensusRow) -> bool:
    """Returns whether the run carries charge, localization, and potential files."""
    return all(census_row.file_sizes.get(name, 0) > 0 for name in FIELD_FILE_NAMES)


def Alloy_Composition_Of(census_row: CensusRow) -> str:
    """Reads the composition fraction from the POSCAR title, never the directory name."""
    matched = re.search(r"x=([0-9.]+)", str(census_row.record.get("p_title", "")))
    if matched is None:
        raise ValueError(f"no composition in the title of {census_row.path}")
    return f"{float(matched.group(1)):.5f}"


def Alloy_Units(census_rows: Sequence[CensusRow], excluded: frozenset[str]) -> list[SplitUnit]:
    """Groups alloy runs by configuration, with satellites joining their seed config."""
    alloy_rows = [census_row for census_row in census_rows if Campaign_Of(census_row.path) == "alloy_ensemble" and census_row.path not in excluded]
    seed_configuration: dict[str, str] = {}
    for census_row in alloy_rows:
        if "GGA-PBE-relaxation" in census_row.path:
            matched = re.search(r"cfg=(\d+)", str(census_row.record.get("p_title", "")))
            if matched is not None:
                seed_configuration[Alloy_Composition_Of(census_row)] = f"{int(matched.group(1)):03d}"
    members: dict[str, list[str]] = {}
    for census_row in alloy_rows:
        composition = Alloy_Composition_Of(census_row)
        matched = re.search(r"cfg(\d+)", census_row.path.rsplit("/", 1)[-1])
        if matched is not None:
            configuration = f"{int(matched.group(1)):03d}"
        else:
            configuration = seed_configuration.get(composition, "pipeline")
        members.setdefault(f"alloy_x{composition}_cfg{configuration}", []).append(census_row.path)
    return [
        SplitUnit(key, "alloy_ensemble", f"x{key.split('_x')[1].split('_')[0]}", tuple(sorted(paths)))
        for key, paths in members.items()
    ]


def Supercell_Point_Key(path: str) -> tuple[str, str]:
    """Returns a supercell run's co-split key and its deformation-family stratum."""
    segments = path.split("/")
    if "New_files" not in segments:
        return "supercell_pristine_reference", "pristine_reference"
    family = segments[segments.index("New_files") + 1]
    point = segments[-1]
    try:
        orbit = Canonical_Orbit(Strain_Tensor_Of(point, None))
        return f"supercell_{orbit}", family
    except OrbitError:
        return f"supercell_{family}_{point}", family


def Supercell_Units(census_rows: Sequence[CensusRow], excluded: frozenset[str]) -> list[SplitUnit]:
    """Groups full-field supercell runs by exact shear orbit or by point."""
    members: dict[str, tuple[str, list[str]]] = {}
    for census_row in census_rows:
        if Campaign_Of(census_row.path) != "supercell_strains" or census_row.path in excluded or not Has_Full_Fields(census_row):
            continue
        key, stratum = Supercell_Point_Key(census_row.path)
        members.setdefault(key, (stratum, []))[1].append(census_row.path)
    return [
        SplitUnit(key, "supercell_strains", stratum, tuple(sorted(paths)))
        for key, (stratum, paths) in members.items()
    ]


def Non_Geometry_Segment(segment: str) -> bool:
    """Returns whether a segment names a functional or smearing variant, not a geometry."""
    lowered = segment.lower()
    return (
        re.fullmatch(r"(\d+-)?(gga-pbe|hse06)", lowered) is not None
        or re.fullmatch(r"sigma-?[0-9.]+", lowered) is not None
    )


def Defect_Unit_Key(path: str) -> tuple[str, str]:
    """Returns a defect run's same-geometry key and its tree stratum."""
    segments = path.split("/")
    geometry = "_".join(segment for segment in segments[2:] if not Non_Geometry_Segment(segment))
    if "new-only" in segments[1]:
        return f"defect_new_only_{geometry}", "new_only"
    tree = segments[1].split("_")[0]
    return f"defect_{tree}_{geometry}", tree


def Defect_Units(census_rows: Sequence[CensusRow], excluded: frozenset[str]) -> list[SplitUnit]:
    """Groups defect runs into same-geometry functional pairs."""
    members: dict[str, tuple[str, list[str]]] = {}
    for census_row in census_rows:
        if Campaign_Of(census_row.path) != "defect_set" or census_row.path in excluded:
            continue
        key, stratum = Defect_Unit_Key(census_row.path)
        members.setdefault(key, (stratum, []))[1].append(census_row.path)
    return [
        SplitUnit(key, "defect_set", stratum, tuple(sorted(paths)))
        for key, (stratum, paths) in members.items()
    ]


def Paired_Fields_Units(census_rows: Sequence[CensusRow], pool_root: Path) -> list[SplitUnit]:
    """Assembles the co-split units of the three full-field campaigns."""
    excluded = Hard_Excluded_Paths(census_rows, pool_root)
    units = Alloy_Units(census_rows, excluded) + Supercell_Units(census_rows, excluded) + Defect_Units(census_rows, excluded)
    return sorted(units, key=lambda unit: unit.key)


def Fold_Assignment(units: Sequence[SplitUnit], fold_count: int = FOLD_COUNT) -> dict[str, int]:
    """Assigns folds round-robin in seeded-hash order within each stratum."""
    assignment: dict[str, int] = {}
    by_stratum: dict[str, list[SplitUnit]] = {}
    for unit in units:
        by_stratum.setdefault(f"{unit.campaign}:{unit.stratum}", []).append(unit)
    for stratum_units in by_stratum.values():
        ordered = sorted(stratum_units, key=lambda unit: (Stable_Fraction(unit.key), unit.key))
        for index, unit in enumerate(ordered):
            assignment[unit.key] = index % fold_count
    return assignment


@dataclass(slots=True)
class OrbitHoldout:
    """One orbit's holdout assignment with its runs."""

    family: str
    assignment: str
    runs: list[str]
    auxiliary_runs: list[str]
    auxiliary_only: bool


def Strain_Holdout_Assignment(census_rows: Sequence[CensusRow]) -> dict[str, OrbitHoldout]:
    """Assigns strain orbits to train, validation, test, or the reserved probe."""
    atlas = Orbit_Map(census_rows)
    by_orbit: dict[str, OrbitHoldout] = {}
    for entry in atlas:
        record = by_orbit.setdefault(entry.orbit, OrbitHoldout(entry.family, "train", [], [], True))
        record.runs.append(entry.run_path)
        if entry.auxiliary:
            record.auxiliary_runs.append(entry.run_path)
        else:
            record.auxiliary_only = False
    by_family: dict[str, list[str]] = {}
    for orbit, record in by_orbit.items():
        by_family.setdefault(record.family, []).append(orbit)
    for family, orbits in by_family.items():
        ordered = sorted(orbits, key=lambda orbit: (Stable_Fraction(orbit), orbit))
        validation_count = max(1, round(0.1 * len(ordered)))
        test_count = max(1, round(0.1 * len(ordered)))
        for index, orbit in enumerate(ordered):
            if family == "reference":
                by_orbit[orbit].assignment = "train"
            elif index < validation_count:
                by_orbit[orbit].assignment = "validation"
            elif index < validation_count + test_count:
                by_orbit[orbit].assignment = "test"
            else:
                by_orbit[orbit].assignment = "train"
        for orbit in orbits:
            if by_orbit[orbit].auxiliary_only:
                by_orbit[orbit].assignment = "reserved_probe"
    for record in by_orbit.values():
        record.runs.sort()
        record.auxiliary_runs.sort()
    return by_orbit


def Perovskite_Units(census_rows: Sequence[CensusRow], pool_root: Path) -> list[SplitUnit]:
    """Returns one unit per perovskite run, with the duplicated center removed."""
    excluded = Hard_Excluded_Paths(census_rows, pool_root)
    units: list[SplitUnit] = []
    for census_row in census_rows:
        if Campaign_Of(census_row.path) != "perovskite_grid" or census_row.path in excluded:
            continue
        sweep = "angle" if "angle_distortions" in census_row.path else "length"
        units.append(SplitUnit(f"perovskite_{census_row.path.rsplit('/', 1)[-1]}_{sweep}", "perovskite_grid", sweep, (census_row.path,)))
    return sorted(units, key=lambda unit: unit.key)


def Perovskite_Extrapolation_Tags(unit: SplitUnit) -> tuple[str, ...]:
    """Tags a perovskite unit with the factor holdouts it belongs to."""
    name = unit.run_paths[0].rsplit("/", 1)[-1]
    tags: list[str] = []
    if "0p8" in name:
        tags.append("holdout_factor_0p8")
    if "1p2" in name:
        tags.append("holdout_factor_1p2")
    return tuple(tags)


def Twin_Shear_Map(census_rows: Sequence[CensusRow], pool_root: Path) -> dict[str, dict[str, list[str]]]:
    """Maps each shear orbit to its strain-atlas and supercell runs."""
    atlas = Orbit_Map(census_rows)
    twins: dict[str, dict[str, list[str]]] = {}
    for entry in atlas:
        if entry.family == "one_angle_shear":
            twins.setdefault(entry.orbit, {"strain_atlas": [], "supercell_strains": []})["strain_atlas"].append(entry.run_path)
    for unit in Supercell_Units(census_rows, Hard_Excluded_Paths(census_rows, pool_root)):
        orbit = unit.key.removeprefix("supercell_")
        if orbit in twins:
            twins[orbit]["supercell_strains"].extend(unit.run_paths)
    for record in twins.values():
        record["strain_atlas"].sort()
        record["supercell_strains"].sort()
    return twins


def Write_Split_Artifacts(census_rows: Sequence[CensusRow], pool_root: Path, out_directory: Path = ARTIFACT_DIRECTORY) -> None:
    """Writes the committed fold maps and twin map as deterministic identifier lists."""
    out_directory.mkdir(parents=True, exist_ok=True)
    paired_units = Paired_Fields_Units(census_rows, pool_root)
    paired_folds = Fold_Assignment(paired_units)
    paired_payload = {
        unit.key: {
            "fold": paired_folds[unit.key],
            "campaign": unit.campaign,
            "stratum": unit.stratum,
            "run_identifiers": [Run_Identifier(path) for path in unit.run_paths],
            "run_paths": list(unit.run_paths),
        }
        for unit in paired_units
    }
    perovskite_units = Perovskite_Units(census_rows, pool_root)
    perovskite_folds = Fold_Assignment(perovskite_units)
    perovskite_payload = {
        unit.key: {
            "fold": perovskite_folds[unit.key],
            "stratum": unit.stratum,
            "extrapolation_tags": list(Perovskite_Extrapolation_Tags(unit)),
            "run_identifiers": [Run_Identifier(path) for path in unit.run_paths],
            "run_paths": list(unit.run_paths),
        }
        for unit in perovskite_units
    }
    strain_payload = {
        orbit: {
            "assignment": record.assignment,
            "family": record.family,
            "run_identifiers": [Run_Identifier(path) for path in record.runs],
            "run_paths": record.runs,
            "auxiliary_run_paths": record.auxiliary_runs,
        }
        for orbit, record in sorted(Strain_Holdout_Assignment(census_rows).items())
    }
    twin_payload = Twin_Shear_Map(census_rows, pool_root)
    for name, payload in (
        ("paired_fields_fivefold.json", paired_payload),
        ("perovskite_folds.json", perovskite_payload),
        ("strain_atlas_holdout.json", strain_payload),
        ("twin_shear_map.json", twin_payload),
    ):
        (out_directory / name).write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")


def Unit_Report(census_rows: Sequence[CensusRow], pool_root: Path) -> dict[str, object]:
    """Summarizes unit counts and size patterns for verification."""
    paired = Paired_Fields_Units(census_rows, pool_root)
    sizes: dict[str, dict[int, int]] = {}
    for unit in paired:
        campaign_sizes = sizes.setdefault(unit.campaign, {})
        campaign_sizes[len(unit.run_paths)] = campaign_sizes.get(len(unit.run_paths), 0) + 1
    return {
        "paired_units": len(paired),
        "size_patterns": sizes,
        "paired_runs": sum(len(unit.run_paths) for unit in paired),
    }


def Regenerated_Artifacts_Match(census_rows: Sequence[CensusRow], pool_root: Path, artifact_directory: Path = ARTIFACT_DIRECTORY) -> bool:
    """Returns whether regenerating the artifacts reproduces the committed files."""
    with tempfile.TemporaryDirectory() as scratch:
        scratch_directory = Path(scratch)
        Write_Split_Artifacts(census_rows, pool_root, scratch_directory)
        for artifact in scratch_directory.iterdir():
            committed = artifact_directory / artifact.name
            if not committed.exists() or committed.read_text() != artifact.read_text():
                return False
    return True

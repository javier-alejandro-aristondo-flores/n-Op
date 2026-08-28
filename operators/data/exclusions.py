"""the ten recorded exclusions, resolved against the census"""

import csv
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from operators.data.parsers import Read_Eigenvalues
from operators.data.store import Campaign_Of, CensusRow


@dataclass(frozen=True, slots=True)
class Exclusion:
    """one recorded exclusion with its scope tags"""

    identifier: str
    reason: str
    scopes: frozenset[str]


EXCLUSIONS: tuple[Exclusion, ...] = (
    Exclusion("E1", "defect triad branch C8-C55-C1 is a byte-copy of C8-C53-C1", frozenset({"all_tasks"})),
    Exclusion("E2", "the new-only zirconium accurate-functional run repeats the cheap-functional bytes", frozenset({"all_tasks"})),
    Exclusion("E3", "the perovskite length-sweep center duplicates the angle-sweep center", frozenset({"all_tasks"})),
    Exclusion("E4", "shear_xy_g0.010 lacks charge density and potential", frozenset({"density_and_potential_fields"})),
    Exclusion("E5", "shear_xy_g0.015 lacks its eigenvalue file", frozenset({"eigenvalue_labels"})),
    Exclusion("E6", "relaxation-pool runs that never produced a converged step", frozenset({"label_tasks"})),
    Exclusion("E7", "perovskite exact metals have no gap", frozenset({"gap_labels"})),
    Exclusion("E8", "perovskite fractional-occupancy runs; gap labels reported both ways", frozenset({"gap_labels_reported_both_ways"})),
    Exclusion("E9", "defect relaxations that hit the step cap", frozenset({"relaxed_geometry_labels"})),
    Exclusion("E10", "the stray test run at the diamond root", frozenset({"all_tasks"})),
)


def Read_Byte_Alias_Groups(pool_root: Path) -> tuple[tuple[str, ...], ...]:
    """groups of byte-identical run paths, from the census duplicates file"""
    groups: set[tuple[str, ...]] = set()
    with (pool_root / "_census/duplicates.csv").open() as stream:
        for record in csv.DictReader(stream):
            members = tuple(sorted(member for member in record["run_dirs"].split(";") if member))
            if len(members) > 1:
                groups.add(members)
    return tuple(sorted(groups))


def Fractional_Occupancy_Paths(census_rows: Sequence[CensusRow], pool_root: Path) -> tuple[str, ...]:
    """perovskite runs whose occupancies sit strictly between filled and empty"""
    flagged: list[str] = []
    for census_row in census_rows:
        if Campaign_Of(census_row.path) != "perovskite_grid" or census_row.file_sizes.get("EIGENVAL", 0) == 0:
            continue
        occupancies = Read_Eigenvalues(pool_root / census_row.path / "EIGENVAL").occupancies
        ceiling = float(occupancies.max())
        # the margin clears smearing noise while keeping real partial occupancies
        interior = (occupancies > 0.005) & (occupancies < ceiling - 0.005)
        if bool(interior.any()):
            flagged.append(census_row.path)
    return tuple(flagged)


def Resolve_Exclusion(identifier: str, census_rows: Sequence[CensusRow], pool_root: Path) -> tuple[str, ...]:
    """the run paths one exclusion names, resolved against the census"""
    paths = [census_row.path for census_row in census_rows]
    # the byte-alias groups decide this one, the name alone matches an unrelated branch too
    if identifier == "E1":
        copies: list[str] = []
        for group in Read_Byte_Alias_Groups(pool_root):
            copies.extend(member for member in group if "C8-C55-C1" in member)
        return tuple(sorted(set(copies)))
    if identifier == "E2":
        return tuple(path for path in paths if "new-only-HSE06" in path and "/Zr" in path)
    if identifier == "E3":
        for group in Read_Byte_Alias_Groups(pool_root):
            if all(member.startswith("ggapbe/") for member in group):
                return tuple(member for member in group if "length_distortions" in member)
        return tuple(path for path in paths if path == "ggapbe/length_distortions/a_1_b_1_c_1_alpha_1_beta_1_gamma_1")
    if identifier == "E4":
        return tuple(path for path in paths if Campaign_Of(path) == "supercell_strains" and path.endswith("shear_xy_g0.010"))
    if identifier == "E5":
        return tuple(path for path in paths if Campaign_Of(path) == "supercell_strains" and path.endswith("shear_xy_g0.015"))
    if identifier == "E6":
        return tuple(census_row.path for census_row in census_rows if Campaign_Of(census_row.path) == "relaxation_pool" and not census_row.record.get("o_complete"))
    if identifier == "E7":
        return tuple(census_row.path for census_row in census_rows if Campaign_Of(census_row.path) == "perovskite_grid" and census_row.record.get("eig_gap") == 0.0)
    if identifier == "E8":
        return Fractional_Occupancy_Paths(census_rows, pool_root)
    if identifier == "E9":
        selected: list[str] = []
        for census_row in census_rows:
            if Campaign_Of(census_row.path) != "defect_set":
                continue
            step_cap = int(str(census_row.record.get("o_nsw", 0) or 0))
            steps_taken = int(str(census_row.record.get("o_ionic_steps", 0) or 0))
            converged = census_row.record.get("o_ionic_conv")
            if step_cap > 1 and steps_taken >= step_cap and not converged:
                selected.append(census_row.path)
        return tuple(selected)
    if identifier == "E10":
        return tuple(path for path in paths if Campaign_Of(path) == "uncatalogued" and path.startswith("diamond"))
    raise KeyError(f"unknown exclusion {identifier}")


def Excluded_Paths_For_Scope(scope: str, census_rows: Sequence[CensusRow], pool_root: Path) -> frozenset[str]:
    """every exclusion whose scope tags cover this scope, or all tasks, unioned"""
    excluded: set[str] = set()
    for exclusion in EXCLUSIONS:
        if "all_tasks" in exclusion.scopes or scope in exclusion.scopes:
            excluded.update(Resolve_Exclusion(exclusion.identifier, census_rows, pool_root))
    return frozenset(excluded)

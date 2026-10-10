"""A12: whether any byte-identical copy group, run or unit crosses roles in the committed split files"""

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

BASELINE = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
SPLITS = BASELINE / "operators/data/splits"
sys.path.insert(0, str(BASELINE))

from operators.data.exclusions import Resolve_Exclusion  # noqa: E402
from operators.data.store import POOL_ROOT, Read_Census  # noqa: E402


def Copy_Groups() -> list[set[str]]:
    """the run folders that share one byte-identical file, one set per duplicate row"""
    with open("/Pool/VASP_DATA/_census/duplicates.csv") as stream:
        return [set(row["run_dirs"].split(";")) for row in csv.DictReader(stream)]


def Roles_Of(split_name: str) -> dict[str, list[str]]:
    """each run path's roles in one split file (a run listed twice gets two entries)"""
    payload = json.loads((SPLITS / f"{split_name}.json").read_text())
    roles: dict[str, list[str]] = defaultdict(list)
    for key, unit in payload.items():
        role = str(unit.get("fold", unit.get("assignment")))
        for path in unit.get("run_paths", []):
            roles[path].append(f"{role}@{key}")
        for path in unit.get("auxiliary_run_paths", []):
            roles[path].append(f"auxiliary@{key}")
    return roles


def Main() -> None:
    """prints each check's count, with the offending entries"""
    census = Read_Census(POOL_ROOT)
    groups = Copy_Groups()
    excluded = {identifier: set(Resolve_Exclusion(identifier, census, POOL_ROOT)) for identifier in ("E1", "E2", "E3", "E10")}
    report: dict[str, object] = {"copy_groups": len(groups)}
    for split_name in ("paired_fields_fivefold", "strain_atlas_holdout", "perovskite_folds"):
        roles = Roles_Of(split_name)
        listed_twice = {path: entries for path, entries in roles.items() if len(entries) > 1}
        crossing = []
        for group in groups:
            present = {path: roles[path] for path in group if path in roles}
            role_names = {entry.split("@")[0] for entries in present.values() for entry in entries}
            if len(present) > 1 and len(role_names) > 1:
                crossing.append({path: entries for path, entries in present.items()})
        leaked_exclusions = {identifier: sorted(paths & set(roles)) for identifier, paths in excluded.items() if paths & set(roles)}
        report[split_name] = {"runs": len(roles), "listed_twice": listed_twice, "copy_groups_present": sum(1 for g in groups if len(g & set(roles)) > 1),
                              "copy_groups_crossing_roles": crossing, "excluded_runs_present": leaked_exclusions}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    Main()

"""A2: the split files regenerate, the store is fresh against the census, the census matches the disk, and the exclusions resolve"""

import json
import os
import sys
from pathlib import Path

BASELINE = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
sys.path.insert(0, str(BASELINE))

from operators.data.exclusions import Resolve_Exclusion  # noqa: E402
from operators.data.splits import ARTIFACT_DIRECTORY, Regenerated_Artifacts_Match  # noqa: E402
from operators.data.store import POOL_ROOT, Read_Census, Stale_Report  # noqa: E402

SKIPPED_TOP_LEVEL = {"_derived", "_census", ".claude"}


def Run_Folders_On_Disk(pool_root: Path) -> set[str]:
    """every folder holding an OUTCAR, by the read-me's rule that such a folder is a run"""
    runs: set[str] = set()
    for directory, subdirectories, files in os.walk(pool_root, followlinks=False):
        if Path(directory) == pool_root:
            subdirectories[:] = [name for name in subdirectories if name not in SKIPPED_TOP_LEVEL]
        if "OUTCAR" in files:
            runs.add(str(Path(directory).relative_to(pool_root)))
    return runs


def Main() -> None:
    """prints each check with its control"""
    report: dict[str, object] = {}
    census = Read_Census(POOL_ROOT)
    report["census_rows"] = len(census)
    report["splits_regenerate"] = Regenerated_Artifacts_Match(census, POOL_ROOT)
    report["split_directory_checked"] = str(ARTIFACT_DIRECTORY)
    stale = Stale_Report(POOL_ROOT)
    report["store"] = {condition: len(names) for condition, names in stale.items()}
    on_disk = Run_Folders_On_Disk(POOL_ROOT)
    census_paths = {row.path for row in census}
    report["run_folders_on_disk"] = len(on_disk)
    report["on_disk_not_in_census"] = sorted(on_disk - census_paths)[:20]
    report["in_census_not_on_disk"] = sorted(census_paths - on_disk)[:20]
    report["census_path_form_example"] = sorted(census_paths)[0]
    exclusions: dict[str, int] = {}
    for number in range(1, 11):
        identifier = f"E{number}"
        try:
            exclusions[identifier] = len(Resolve_Exclusion(identifier, census, POOL_ROOT))
        except Exception as error:
            exclusions[identifier] = -1
            report[f"{identifier}_error"] = repr(error)
    report["exclusion_path_counts"] = exclusions
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    Main()

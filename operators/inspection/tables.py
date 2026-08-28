"""the orbit map, fold balance and exclusions summarized as plain tables"""

import json
from collections import Counter
from pathlib import Path

from operators.data import ARTIFACT_DIRECTORY, EXCLUSIONS, Orbit_Map, POOL_ROOT, Read_Census, Resolve_Exclusion

type Table = tuple[dict[str, object], ...]


def Orbit_Summary(pool_root: Path = POOL_ROOT) -> Table:
    """points, orbits and runs per strain sweep family"""
    atlas = Orbit_Map(Read_Census(pool_root))
    rows: list[dict[str, object]] = []
    for family in sorted({entry.family for entry in atlas}):
        members = [entry for entry in atlas if entry.family == family]
        rows.append(
            {
                "family": family,
                "points": len({entry.point for entry in members}),
                "orbits": len({entry.orbit for entry in members}),
                "runs": len(members),
            }
        )
    rows.append(
        {
            "family": "all",
            "points": len({entry.point for entry in atlas}),
            "orbits": len({entry.orbit for entry in atlas}),
            "runs": len(atlas),
        }
    )
    return tuple(rows)


def Fold_Balance(artifact_directory: Path = ARTIFACT_DIRECTORY) -> Table:
    """unit counts per fold, for every campaign and stratum"""
    payload = json.loads((artifact_directory / "paired_fields_fivefold.json").read_text())
    counts: dict[str, Counter[int]] = {}
    for unit in payload.values():
        counts.setdefault(f"{unit['campaign']}:{unit['stratum']}", Counter())[int(unit["fold"])] += 1
    rows: list[dict[str, object]] = []
    for stratum in sorted(counts):
        per_fold = counts[stratum]
        rows.append(
            {
                "stratum": stratum,
                "units": sum(per_fold.values()),
                "folds": " ".join(str(per_fold.get(fold, 0)) for fold in range(5)),
            }
        )
    return tuple(rows)


def Exclusion_Summary(pool_root: Path = POOL_ROOT) -> Table:
    """every exclusion with its resolved run count"""
    census_rows = Read_Census(pool_root)
    rows: list[dict[str, object]] = []
    for exclusion in EXCLUSIONS:
        resolved = Resolve_Exclusion(exclusion.identifier, census_rows, pool_root)
        rows.append(
            {
                "identifier": exclusion.identifier,
                "runs": len(resolved),
                "scopes": ", ".join(sorted(exclusion.scopes)),
                "reason": exclusion.reason,
            }
        )
    return tuple(rows)


def Render_Table(rows: Table) -> str:
    """table rows as aligned plain text"""
    if not rows:
        return ""
    # the first row's keys are the columns, in the order it names them
    names = list(rows[0])
    cells = [[str(row[name]) for name in names] for row in rows]
    widths = [max(len(name), *(len(line[column]) for line in cells)) for column, name in enumerate(names)]
    header = "  ".join(name.ljust(widths[column]) for column, name in enumerate(names))
    body = [
        "  ".join(line[column].ljust(widths[column]) for column in range(len(names)))
        for line in cells
    ]
    return "\n".join([header, *body])

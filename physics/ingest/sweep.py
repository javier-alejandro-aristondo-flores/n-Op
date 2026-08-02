"""Reading a family of runs as one series.

A single frame answers *is this calculation self-consistent*. A **series** answers
questions no single frame can: where the energy is stationary, where the stress vanishes,
and whether those two agree. This module is the smallest thing that turns a directory of
runs into such a series.

It adds no parsing. Every point goes through `read_frame`, which is already exercised
against real output; this only walks, orders and labels.

**Extraction is a prerequisite, not a code path.** The archives live on `/Pool` and are
tens of gigabytes with licensed pseudopotentials inside; nothing here unpacks them. Use
`tools/extract_sweep_family.sh`, which takes the family and the sub-run and writes only
the machine-readable XML.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..state import Frame
from .vasp import find_vasprun, read_frame

#: The two sub-run names every point in the strain sweep carries.
PBE = "1-cheap-pbe-atoms-relaxed"
HSE06 = "2-accurate-hse06-atoms-fixed"


@dataclass(frozen=True)
class SeriesPoint:
    """One frame, with the label the directory gave it.

    The label is carried verbatim and never parsed for physics. A directory named
    `cell-volume-11.40-cubic-angstroms` is a human convenience; the volume that counts is
    the one the calculation reported, and the two are checked against each other by the
    `det(A) = V` invariant rather than assumed equal.
    """

    label: str
    frame: Frame

    @property
    def volume(self) -> float:
        return self.frame.reported_volume


def read_family(family_dir: str | Path, sub_run: str = PBE) -> list[SeriesPoint]:
    """Every point of one strain family, ordered by the volume the calculation reported.

    Points whose sub-run directory is missing or carries no parseable output are skipped
    rather than raising: a family with a hole is still a usable series, and the hole is
    visible as a gap in the returned volumes. The strain sweep is documented to have such
    holes -- 12 absent family-4 points and 24 absent family-5 combinations.

    Raises if the directory itself is absent, which is a setup error rather than a datum.
    """
    family_dir = Path(family_dir)
    if not family_dir.is_dir():
        raise FileNotFoundError(
            f"{family_dir} is not a directory; extract a family first "
            "(tools/extract_sweep_family.sh)"
        )

    points: list[SeriesPoint] = []
    for point_dir in sorted(p for p in family_dir.iterdir() if p.is_dir()):
        vasprun = find_vasprun(point_dir / sub_run)
        if vasprun is None:
            continue
        points.append(SeriesPoint(label=point_dir.name, frame=read_frame(vasprun)))

    return sorted(points, key=lambda p: p.volume)


def energy_volume_curve(points: list[SeriesPoint]) -> tuple[list[float], list[float]]:
    """Volumes and total energies, for the points that reported an energy."""
    have = [p for p in points if p.frame.total_energy is not None]
    return [p.volume for p in have], [p.frame.total_energy for p in have]


def pressure_volume_curve(points: list[SeriesPoint]) -> tuple[list[float], list[float]]:
    """Volumes and hydrostatic pressures, for the points that reported a stress.

    Pressure is `-tr(sigma)/3` in the continuum convention the frame carries, so it is
    **positive under compression**. `ingest.vasp` has already flipped VASP's opposite sign
    and converted kB to GPa, so this is one trace and nothing else.
    """
    import numpy as np

    have = [p for p in points if p.frame.stress is not None]
    pressures = [-float(np.trace(p.frame.stress)) / 3.0 for p in have]
    return [p.volume for p in have], pressures

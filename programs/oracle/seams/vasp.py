"""VASP ingest: a run directory in, a `Frame` out.

Parses `vasprun.xml` only. Never OUTCAR -- OUTCAR embeds a substantial POTCAR header and
POTCAR is VASP-licensed material that must never leave `/Pool`; `vasprun.xml` carries only
POTCAR *titles* and PAW metadata. The strain-sweep archives rename the file to
`everything-machine-readable.xml`, so both names are accepted.

Channels the run did not report come back as `None`, and that `None` is load-bearing: it
is what makes a check refuse rather than silently score zero.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np

from ..state.state import CrystalState, Frame
from ..units import VASP_STRESS_SIGN, stress_kbar_to_gpa

#: The two names the same file goes by in this project's data.
VASPRUN_NAMES = ("vasprun.xml", "everything-machine-readable.xml")


def find_vasprun(run_dir: str | Path) -> Path | None:
    run_dir = Path(run_dir)
    for name in VASPRUN_NAMES:
        candidate = run_dir / name
        if candidate.is_file():
            return candidate
    return None


def read_frame(path: str | Path) -> Frame:
    """Parse one `vasprun.xml` into a `Frame`.

    Reads the *final* ionic step. Uses pymatgen; `parse_potcar_file=False` is not merely a
    speed choice -- it keeps the licensed pseudopotential data out of the process entirely.
    """
    from pymatgen.io.vasp.outputs import Vasprun

    path = Path(path)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        vr = Vasprun(
            str(path),
            parse_potcar_file=False,
            parse_dos=False,
            parse_eigen=True,
            exception_on_bad_xml=False,
        )

    structure = vr.final_structure
    state = CrystalState(
        cell=np.array(structure.lattice.matrix, dtype=np.float64),
        positions=np.array(structure.cart_coords, dtype=np.float64),
        species=np.array([site.specie.Z for site in structure], dtype=np.int32),
    )

    last = vr.ionic_steps[-1] if vr.ionic_steps else {}

    forces = last.get("forces")
    forces = np.asarray(forces, dtype=np.float64) if forces is not None else None

    stress = last.get("stress")
    if stress is not None:
        # VASP reports kB and uses the opposite sign to the continuum convention.
        stress = stress_kbar_to_gpa(np.asarray(stress, dtype=np.float64)) * VASP_STRESS_SIGN

    occupations, weights = None, None
    if vr.eigenvalues:
        # pymatgen: {Spin: array(n_kpoints, n_bands, 2)} where [..., 1] is occupancy.
        occupations = [
            np.asarray(arr, dtype=np.float64)[..., 1] for arr in vr.eigenvalues.values()
        ]
        weights = np.asarray(vr.actual_kpoints_weights, dtype=np.float64)

    ispin = int(vr.parameters.get("ISPIN", 1))
    moment = _net_moment(occupations, weights) if ispin == 2 else None

    return Frame(
        state=state,
        forces=forces,
        stress=stress,
        occupations=occupations,
        kpoint_weights=weights,
        n_electrons=_float_or_none(vr.parameters.get("NELECT")),
        magnetic_moment=moment,
        reported_volume=float(structure.volume),
        total_energy=_float_or_none(vr.final_energy),
        provenance={
            "path": str(path),
            "ispin": ispin,
            "nsw": int(vr.parameters.get("NSW", 0)),
            "converged_electronic": bool(vr.converged_electronic),
            "converged_ionic": bool(vr.converged_ionic),
            "n_ionic_steps": len(vr.ionic_steps),
        },
    )


def _float_or_none(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _net_moment(occupations, weights) -> float | None:
    """Net moment as (spin-up electrons) - (spin-down electrons), in bohr magnetons.

    Computed from occupations rather than read from a summary line, so the check is
    self-contained: it tests the same numbers it derives the moment from. Returns `None`
    unless there are exactly two spin channels -- with one channel there is no moment to
    speak of, and inventing 0.0 would be the exact lie `INPUT_CHANNEL_ABSENT` exists to
    prevent.
    """
    if occupations is None or weights is None or len(occupations) != 2:
        return None
    up, down = occupations
    return float(np.sum(weights[:, None] * up) - np.sum(weights[:, None] * down))

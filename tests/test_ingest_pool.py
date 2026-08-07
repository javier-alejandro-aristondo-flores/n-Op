"""The parser, against real VASP output.

`test_invariants.py` proves the checks are correct on synthetic frames. This proves the
*parser* reads real output correctly, which is the half that can silently rot: a changed
tag name or a unit convention drifting produces plausible numbers, not an exception.

**No VASP output is committed here, and none may be.** Every run directory on `/Pool`
carries a licensed pseudopotential and this remote is public
(`data/diamond-strain-sweep/01-what-this-data-is.md`). So this test reads from an
extracted run outside the repository and skips when there is not one.

To produce one::

    P=/Pool/Diamond_Stretch_And_Skew_Sweep/renamed-archives
    R=1-scale-all-axes-uniformly/cell-volume-11.40-cubic-angstroms/1-cheap-pbe-atoms-relaxed
    mkdir -p ~/.cache/n-op-vasp && tar -xzf $P/1-scale-all-axes-uniformly.tar.gz \\
        -C ~/.cache/n-op-vasp "$R/everything-machine-readable.xml"
    export NOP_VASP_RUN=~/.cache/n-op-vasp/$R
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

from physics.cert import RefusalMode
from physics.checks.invariants import run_invariants
from physics.residual import ResidualMap
from physics.state import CrystalState  # noqa: F401  (documents what a Frame carries)

pytest.importorskip("pymatgen", reason="the VASP reader needs pymatgen")

from physics.cert import CertEvidence  # noqa: E402
from physics.ingest.vasp import find_vasprun, read_frame  # noqa: E402

#: Conventional extraction target, overridable. Deliberately outside the repository.
DEFAULT_RUN = Path.home() / ".cache" / "n-op-vasp" / (
    "1-scale-all-axes-uniformly/cell-volume-11.40-cubic-angstroms/1-cheap-pbe-atoms-relaxed"
)


def _run_dir() -> Path:
    candidate = Path(os.environ.get("NOP_VASP_RUN", DEFAULT_RUN))
    if find_vasprun(candidate) is None:
        pytest.skip(
            f"no extracted VASP run at {candidate}; see this module's docstring. "
            "The dataset is on /Pool and is never committed."
        )
    return candidate


@pytest.fixture(scope="module")
def frame():
    return read_frame(find_vasprun(_run_dir()))


def test_geometry_parses_to_the_documented_cell(frame):
    """Two carbon atoms, and the volume the directory name advertises."""
    assert frame.state.n_ions == 2
    assert list(frame.state.species) == [6, 6]
    assert frame.reported_volume == pytest.approx(11.40, abs=5e-3)
    assert frame.n_electrons == pytest.approx(8.0), "four occupied bands, eight valence electrons"


def test_reported_volume_agrees_with_the_lattice_determinant(frame):
    """Independent routes to the same number -- the cheapest parser-bug detector there is."""
    assert frame.state.volume == pytest.approx(frame.reported_volume, abs=1e-9)


def test_stress_is_in_gpa_not_kbar(frame):
    """A silent factor of ten. VASP reports kB; `units.KBAR_TO_GPA` converts.

    Near equilibrium diamond sits within a fraction of a GPa. If the conversion were
    dropped the same run would read tens of GPa, which is still a plausible-looking
    number -- which is exactly why it needs a test rather than an eyeball.
    """
    assert np.all(np.abs(frame.stress) < 5.0), f"stress looks like kB, not GPa:\n{frame.stress}"


def test_the_invariants_on_a_real_relaxed_frame(frame):
    """The end-to-end result, pinned: every channel-complete check near zero, one refused."""
    residuals, cert = ResidualMap(), CertEvidence()
    run_invariants(frame, residuals, cert)

    by_name = {k.producer.name: v for k, v in residuals.values.items()}
    assert set(by_name) == {
        "net-force-vanishes",
        "stress-tensor-symmetric",
        "occupations-sum-to-electron-count",
        "lattice-determinant-equals-volume",
        "occupations-within-unit-interval",
        "kpoint-weights-sum-to-one",
    }
    # Pauli is exact in the file: occupancies are printed with room to spare.
    assert by_name["occupations-within-unit-interval"] < 1e-9

    # The zone measure is exact in mathematics and *not* in the file. VASP prints the
    # weights to eight decimals, so 172 irreducible points accumulate ~6.5e-7 of
    # truncation. The tolerance is the file's precision, not the calculation's; see
    # `_kpoint_weight_normalisation`. Asserting machine epsilon here would be asserting
    # something about VASP's output formatting.
    assert by_name["kpoint-weights-sum-to-one"] < 1e-5

    # Tolerances are the run's own convergence settings, not round numbers:
    # EDIFFG = -0.001 caps the residual force at 1 meV/A per ion.
    assert by_name["net-force-vanishes"] < 2e-3
    assert by_name["stress-tensor-symmetric"] < 1e-6
    assert by_name["occupations-sum-to-electron-count"] < 1e-4
    assert by_name["lattice-determinant-equals-volume"] < 1e-9

    # Non-spin-polarized run: no moment reported, so the parity check must refuse.
    assert len(cert.refusals) == 1
    assert cert.refusals[0].mode is RefusalMode.INPUT_CHANNEL_ABSENT
    assert cert.refusals[0].key.producer.name == "spin-parity"
    cert.assert_absence_discipline(set(residuals.values))

"""the reads that fill the training stream, and what each of them costs"""

import json
from pathlib import Path

import numpy as np

from operators.training import (
    Field_From_Archive,
    Strain_Assignments_By_Run,
    Strain_Assignments_Of_Pool,
)

REFERENCE_RUN = "diamond/2_atoms_4-10-2026/reference_2_atoms/GGA-PBE"

STRAINED_RUN = "diamond/2_atoms_4-10-2026/uniax_x_eps0.01/GGA-PBE"


def Synthetic_Census(pool_root: Path) -> None:
    """the smallest census the orbit map accepts, a reference run and one strained run"""
    census_directory = pool_root / "_census"
    census_directory.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps({"path": REFERENCE_RUN, "p_abc": [3.57, 3.57, 3.57], "files": {}}),
        json.dumps({"path": STRAINED_RUN, "p_abc": [3.6057, 3.57, 3.57], "files": {}}),
    ]
    (census_directory / "runs.jsonl").write_text("\n".join(lines) + "\n")


def Test_The_Orbit_Map_Is_Read_Once_Per_Pool(tmp_path: Path) -> None:
    """asserts a second call reuses the assignments of the first rather than walking the census again"""
    Synthetic_Census(tmp_path)
    first = Strain_Assignments_By_Run(tmp_path)
    second = Strain_Assignments_By_Run(tmp_path)
    assert set(first) == {REFERENCE_RUN, STRAINED_RUN}
    assert first is not second
    assert all(first[run_path] is second[run_path] for run_path in first)
    assert Strain_Assignments_Of_Pool(tmp_path) is Strain_Assignments_Of_Pool(tmp_path)


def Test_The_Shared_Orbit_Map_Cannot_Be_Emptied_By_A_Caller(tmp_path: Path) -> None:
    """asserts clearing what one call returned leaves the next call whole"""
    Synthetic_Census(tmp_path)
    Strain_Assignments_By_Run(tmp_path).clear()
    assert set(Strain_Assignments_By_Run(tmp_path)) == {REFERENCE_RUN, STRAINED_RUN}
    assert isinstance(Strain_Assignments_Of_Pool(tmp_path), tuple)


def Test_The_Precision_Word_Changes_Residency_And_Not_The_Numbers(tmp_path: Path) -> None:
    """asserts a single-precision read is the same numbers in half the bytes"""
    generator = np.random.default_rng(7)
    written = generator.random((3, 4, 5)).astype(np.float32)
    archive_path = tmp_path / "made_up.npz"
    np.savez(archive_path, charge_density=written, lattice=np.eye(3), cell_volume=np.asarray(8.0))
    with np.load(archive_path) as archive:
        single = Field_From_Archive(archive, ("charge_density",), "single")
        double = Field_From_Archive(archive, ("charge_density",))
        spin_pair = Field_From_Archive(archive, ("charge_density", "magnetization_density"), "single")
    assert single is not None and double is not None and spin_pair is not None
    single_values = np.asarray(single.values)
    double_values = np.asarray(double.values)
    assert single_values.dtype == np.float32 and double_values.dtype == np.float64
    assert np.array_equal(single_values.astype(np.float64), double_values)
    assert single_values.nbytes * 2 == double_values.nbytes
    # the standing-in magnetization follows the word the caller asked for
    assert np.asarray(spin_pair.values).dtype == np.float32
    assert not np.asarray(spin_pair.values)[1].any()

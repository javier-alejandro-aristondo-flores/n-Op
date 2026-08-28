"""Checks the corpus readers on synthetic files and on recorded live-corpus invariants."""

from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.data import (
    Read_Eigenvalues,
    Read_Field_File,
    Read_Final_Magnetization,
    Read_Geometry,
    Read_Outcar_Echoes,
)

POOL = Path("/Pool/VASP_DATA")

ARSENIC_DEFECT = POOL / "diamond/single_defect/VA-element-single-impurity/As/GGA-PBE"

MAGNESIUM_DEFECT = POOL / "diamond/single_defect/IIA-element-single-impurity/Mg/gga-pbe"

ALLOY_PIPELINE = POOL / "alloy/1-Alloy/1-Alloy/3-HSE06/8-x-82.5"

STRAIN_REFERENCE = POOL / "diamond/2_atoms_4-10-2026/reference_2_atoms/GGA-PBE"

SYNTHETIC_TWO_BLOCK = """synthetic
   1.0
  2.0 0.0 0.0
  0.0 2.0 0.0
  0.0 0.0 2.0
   X Y
   1 1
Direct
  0.0 0.0 0.0
  0.5 0.5 0.5

    2    2    2
 0.0 1.0 2.0 3.0 4.0
 5.0 6.0 -.7E+01
augmentation occupancies   1  4
  0.1E+00 0.2E+00 0.3E+00 0.4E+00
augmentation occupancies   2  2
  0.5E+00 0.6E+00
    2    2    2
 8.0 9.0 10.0 11.0 12.0
 13.0 14.0 15.0
"""

SYNTHETIC_CARTESIAN = """cartesian
   1.0
  2.0 0.0 0.0
  0.0 2.0 0.0
  0.0 0.0 2.0
   X
   1
Selective dynamics
Cartesian
  1.0 1.0 1.0 T T T
"""

SYNTHETIC_EIGENVALUES = """   2   2   1    2
  0.0 0.0 0.0 0.0 0.0
  0.0001
  CAR
 comment
    8      1      2

  0.0 0.0 0.0 1.0
    1      -5.0    -4.0   1.0   1.0
    2       3.0     2.0   0.0   0.0
"""


def Require_The_Pool() -> None:
    """Fails the calling test when the corpus partition is not mounted."""
    if not POOL.exists():
        pytest.fail("the corpus at /Pool/VASP_DATA is not mounted on this machine")


def Normalized_Mean_Absolute_Error(candidate: NDArray[np.float64], reference: NDArray[np.float64]) -> float:
    """Returns mean absolute error divided by the mean absolute reference value."""
    return float(np.mean(np.abs(candidate - reference)) / np.mean(np.abs(reference)))


def Test_A_Two_Block_File_Parses_Past_Augmentation(tmp_path: Path) -> None:
    """Reads a synthetic spin-doubled file and checks x-fastest grid ordering."""
    file_path = tmp_path / "CHGCAR"
    file_path.write_text(SYNTHETIC_TWO_BLOCK)
    field = Read_Field_File(file_path)
    assert field.dimensions == (2, 2, 2)
    assert len(field.blocks) == 2
    assert field.blocks[0][1, 0, 0] == 1.0
    assert field.blocks[0][0, 1, 0] == 2.0
    assert field.blocks[0][0, 0, 1] == 4.0
    assert field.blocks[0][1, 1, 1] == -7.0
    assert field.blocks[1][0, 0, 0] == 8.0


def Test_Cartesian_Selective_Geometry_Converts_To_Fractional(tmp_path: Path) -> None:
    """Reads a Cartesian header behind a selective-dynamics line."""
    geometry, _ = Read_Geometry(SYNTHETIC_CARTESIAN.splitlines())
    assert geometry.species == ("X",)
    assert np.allclose(geometry.positions, [[0.5, 0.5, 0.5]])


def Test_Eigenvalues_Read_The_Spin_Polarized_Layout(tmp_path: Path) -> None:
    """Reads a synthetic two-spin EIGENVAL and checks both channels."""
    file_path = tmp_path / "EIGENVAL"
    file_path.write_text(SYNTHETIC_EIGENVALUES)
    eigenvalues = Read_Eigenvalues(file_path)
    assert eigenvalues.electron_count == 8.0
    assert eigenvalues.energies.shape == (2, 1, 2)
    assert eigenvalues.energies[0, 0, 0] == -5.0
    assert eigenvalues.energies[1, 0, 1] == 2.0
    assert eigenvalues.occupancies[1, 0, 0] == 1.0


@pytest.mark.pool
def Test_Charge_Mean_Equals_The_Electron_Count() -> None:
    """Asserts grid-mean of raw charge equals the NELECT echo on two recorded runs."""
    Require_The_Pool()
    for run in (ARSENIC_DEFECT, STRAIN_REFERENCE):
        field = Read_Field_File(run / "CHGCAR")
        echoes = Read_Outcar_Echoes(run / "OUTCAR")
        assert abs(float(np.mean(field.blocks[0])) - echoes.electron_count) < 1e-3


@pytest.mark.pool
def Test_The_Half_Grid_Law_Holds() -> None:
    """Asserts the ELF grid is exactly half the charge grid per axis on two campaigns."""
    Require_The_Pool()
    for run in (ARSENIC_DEFECT, ALLOY_PIPELINE):
        charge = Read_Field_File(run / "CHGCAR")
        localization = Read_Field_File(run / "ELFCAR")
        halved = tuple(axis // 2 for axis in charge.dimensions)
        assert localization.dimensions == halved


@pytest.mark.pool
def Test_The_Spin_Block_Law_Holds() -> None:
    """Asserts spin doubling on a magnetic run and single blocks on the controls."""
    Require_The_Pool()
    for name in ("CHGCAR", "ELFCAR", "LOCPOT"):
        assert len(Read_Field_File(ARSENIC_DEFECT / name).blocks) == 2
    assert len(Read_Field_File(ARSENIC_DEFECT / "AECCAR1").blocks) == 1
    assert len(Read_Field_File(STRAIN_REFERENCE / "CHGCAR").blocks) == 1


@pytest.mark.pool
def Test_The_Magnetization_Calibration_Replicates() -> None:
    """Asserts the magnetization block integrates to the recorded two-magneton moment."""
    Require_The_Pool()
    field = Read_Field_File(MAGNESIUM_DEFECT / "CHGCAR")
    moment = float(np.mean(field.blocks[1]))
    assert abs(moment - 2.000000) < 1e-3
    final = Read_Final_Magnetization(MAGNESIUM_DEFECT / "OSZICAR")
    assert final is not None and abs(moment - final) < 1e-3


@pytest.mark.pool
def Test_The_Superposed_Atomic_Density_Floor_Replicates() -> None:
    """Asserts the recorded atomic-superposition error levels on the arsenic run."""
    Require_The_Pool()
    charge = Read_Field_File(ARSENIC_DEFECT / "CHGCAR").blocks[0]
    superposed = Read_Field_File(ARSENIC_DEFECT / "AECCAR1").blocks[0]
    valence_reference = Read_Field_File(ARSENIC_DEFECT / "AECCAR2").blocks[0]
    assert abs(Normalized_Mean_Absolute_Error(superposed, charge) - 0.148) < 0.005
    assert abs(Normalized_Mean_Absolute_Error(valence_reference, charge) - 0.0156) < 0.002


@pytest.mark.pool
def Test_Eigenvalue_Headers_Match_The_Recorded_Run() -> None:
    """Asserts the arsenic run's eigenvalue header against the census row."""
    Require_The_Pool()
    eigenvalues = Read_Eigenvalues(ARSENIC_DEFECT / "EIGENVAL")
    assert eigenvalues.electron_count == 257.0
    assert eigenvalues.kpoints.shape == (8, 3)
    assert eigenvalues.energies.shape == (2, 8, 200)

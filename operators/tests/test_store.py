"""the store builder on a synthetic corpus and one live run, writing nothing to the corpus"""

import json
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.data import POOL_ROOT, Campaign_Of, Extract_Run, Read_Census, Run_Identifier, Stale_Report, StoreError
from operators.data.store import Guard_Volumetric_Destination, StoreArray, Write_Manifests, Write_Run

SYNTHETIC_CHGCAR = """synthetic
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
    2    2    2
 8.0 9.0 10.0 11.0 12.0
 13.0 14.0 15.0
"""

SYNTHETIC_OUTCAR = """   TITEL  = PAW_FAKE X 01Jan2000
   TITEL  = PAW_FAKE Y 01Jan2000
   NELECT =       1.7500    total number of electrons
"""

SYNTHETIC_OSZICAR = "   1 F= -1.0 E0= -1.0  d E =0.0  mag=     0.2500\n"

SYNTHETIC_CONTCAR = """bare
   1.0
  3.0 0.0 0.0
  0.0 3.0 0.0
  0.0 0.0 3.0
   Z
   1
Direct
  0.1 0.2 0.3
"""


def As_Float_Array(value: StoreArray) -> NDArray[np.float64]:
    """a stored array in double precision, for assertions"""
    return np.asarray(value, dtype=np.float64)


def Fake_Pool(tmp_path: Path) -> Path:
    """a two-run synthetic corpus with a census, under a temporary root"""
    pool = tmp_path / "pool"
    field_run = pool / "diamond/single_defect/fake/run"
    field_run.mkdir(parents=True)
    (field_run / "CHGCAR").write_text(SYNTHETIC_CHGCAR)
    (field_run / "OUTCAR").write_text(SYNTHETIC_OUTCAR)
    (field_run / "OSZICAR").write_text(SYNTHETIC_OSZICAR)
    bare_run = pool / "j-dataset/fake/bare"
    bare_run.mkdir(parents=True)
    (bare_run / "CONTCAR").write_text(SYNTHETIC_CONTCAR)
    census = pool / "_census"
    census.mkdir()
    census_records = [
        {
            "path": "diamond/single_defect/fake/run",
            "corpus": "T",
            "files": {"CHGCAR": 999, "OUTCAR": 99, "OSZICAR": 9, "CONTCAR": 0},
        },
        {"path": "j-dataset/fake/bare", "corpus": "T", "files": {"CONTCAR": 99}},
    ]
    (census / "runs.jsonl").write_text("\n".join(json.dumps(census_record) for census_record in census_records) + "\n")
    return pool


def Test_Campaign_Names_Map_From_Paths() -> None:
    """the path-prefix campaign mapping, new-only defect trees included"""
    assert Campaign_Of("alloy/1-Alloy/x") == "alloy_ensemble"
    assert Campaign_Of("diamond/2_atoms_4-10-2026/x") == "strain_atlas"
    assert Campaign_Of("diamond/Pure/x") == "supercell_strains"
    assert Campaign_Of("diamond/single_defects_new-only-HSE06/x") == "defect_set"
    assert Campaign_Of("ggapbe/x") == "perovskite_grid"
    assert Campaign_Of("j-dataset/x") == "relaxation_pool"
    assert Campaign_Of("CHGCAR") == "uncatalogued"


def Test_The_Egress_Guard_Refuses_Foreign_Destinations(tmp_path: Path) -> None:
    """volumetric writes outside the corpus partition are refused"""
    pool = tmp_path / "pool"
    pool.mkdir()
    Guard_Volumetric_Destination(pool / "_derived" / "x", pool)
    with pytest.raises(StoreError):
        Guard_Volumetric_Destination(tmp_path / "elsewhere", pool)


def Test_A_Synthetic_Run_Extracts_Writes_And_Freshens(tmp_path: Path) -> None:
    """extract, write, reload and staleness on the synthetic corpus"""
    pool = Fake_Pool(tmp_path)
    census_rows = Read_Census(pool)
    arrays, sidecar = Extract_Run(census_rows[0], pool)
    assert arrays["charge_density"].dtype == np.float32
    assert abs(float(np.mean(As_Float_Array(arrays["charge_density"]))) * 8.0 - 1.75) < 1e-6
    assert "magnetization_density" in arrays
    assert float(As_Float_Array(arrays["final_magnetization"])) == 0.25
    assert sidecar["campaign"] == "defect_set"
    assert sidecar["pseudopotential_titles"] == ["PAW_FAKE X 01Jan2000", "PAW_FAKE Y 01Jan2000"]
    archive_path = Write_Run(arrays, sidecar, pool)
    reloaded = np.load(archive_path)
    assert reloaded["charge_density"].shape == (2, 2, 2)
    bare_arrays, bare_sidecar = Extract_Run(census_rows[1], pool)
    assert "charge_density" not in bare_arrays
    assert abs(float(As_Float_Array(bare_arrays["cell_volume"])) - 27.0) < 1e-9
    Write_Run(bare_arrays, bare_sidecar, pool)
    Write_Manifests(pool)
    report = Stale_Report(pool)
    assert sorted(report["fresh"]) == sorted(Run_Identifier(census_row.path) for census_row in census_rows)
    assert report["stale"] == [] and report["missing"] == []
    census_path = pool / "_census/runs.jsonl"
    lines = census_path.read_text().splitlines()
    edited = json.loads(lines[0])
    edited["mtime"] = 1
    census_path.write_text("\n".join([json.dumps(edited), lines[1]]) + "\n")
    report = Stale_Report(pool)
    assert report["stale"] == [Run_Identifier(census_rows[0].path)]


@pytest.mark.pool
def Test_The_Arsenic_Run_Extracts_Faithfully() -> None:
    """the recorded arsenic defect run extracted in memory, channel by channel"""
    if not POOL_ROOT.exists():
        pytest.fail("the corpus at /Pool/VASP_DATA is not mounted on this machine")
    census_rows = [census_row for census_row in Read_Census(POOL_ROOT) if census_row.path.endswith("VA-element-single-impurity/As/GGA-PBE")]
    assert len(census_rows) == 1
    arrays, sidecar = Extract_Run(census_rows[0], POOL_ROOT)
    for name in (
        "charge_density",
        "magnetization_density",
        "electron_localization_up",
        "electron_localization_down",
        "local_potential_up",
        "local_potential_down",
        "superposed_atomic_density",
        "all_electron_valence_density",
    ):
        assert name in arrays
    assert arrays["charge_density"].dtype == np.float32
    volume = float(As_Float_Array(arrays["cell_volume"]))
    integrated = float(np.mean(As_Float_Array(arrays["charge_density"]))) * volume
    assert abs(integrated - 257.0) < 1e-2
    assert As_Float_Array(arrays["local_potential_mean"]).shape == (2,)
    assert sidecar["campaign"] == "defect_set"

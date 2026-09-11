"""the inspection catalog, the summary tables, the renderers and the rendering seam"""

import ast
import hashlib
from pathlib import Path

import numpy as np
import pytest

from operators.inspection import (
    Describe_Run,
    Exclusion_Summary,
    Find_Runs,
    Fold_Balance,
    List_Campaigns,
    List_Runs,
    Load_Run_Field,
    Orbit_Summary,
    Render_Curves,
    Render_Error_Spread,
    Render_Field_Slices,
    Render_Floor_Comparison,
    Render_Inspection_Suite,
    Render_Prediction_Against_Truth,
    Render_Table,
)

PACKAGE_ROOT = Path(__file__).resolve().parent.parent

RENDERING_SEAM = PACKAGE_ROOT / "inspection" / "plots"


def Test_The_Rendering_Seam_Holds() -> None:
    """the plotting library is imported inside the one rendering package alone"""
    for source_path in PACKAGE_ROOT.rglob("*.py"):
        if RENDERING_SEAM in source_path.parents or ".pytest_cache" in source_path.parts:
            continue
        tree = ast.parse(source_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                assert not name.startswith("matplotlib"), f"{source_path} imports {name}"


def Test_The_Renderers_Write_Images(tmp_path: Path) -> None:
    """a synthetic field and a synthetic curve reach files"""
    generator = np.random.default_rng(2)
    field = generator.random((12, 12, 12))
    slices_path = Render_Field_Slices(field, tmp_path / "slices.png", "synthetic")
    assert slices_path.is_file() and slices_path.stat().st_size > 1000
    horizontal = np.linspace(-1.0, 1.0, 50)
    curves_path = Render_Curves(
        horizontal,
        {"first": np.sin(horizontal), "second": np.cos(horizontal)},
        tmp_path / "curves.png",
        "synthetic curves",
        "energy",
        "states",
    )
    assert curves_path.is_file() and curves_path.stat().st_size > 1000


def Test_Fold_Balance_Reads_The_Committed_Artifact() -> None:
    """the fold table covers every stratum, with balanced folds"""
    rows = Fold_Balance()
    assert len(rows) >= 5
    for row in rows:
        counts = [int(token) for token in str(row["folds"]).split()]
        assert max(counts) - min(counts) <= 1
    assert "campaign" not in Render_Table(rows)
    assert "stratum" in Render_Table(rows)


@pytest.mark.pool
def Test_The_Catalog_Browses_The_Store() -> None:
    """campaigns, runs, descriptions and field loading against the live store"""
    campaigns = List_Campaigns()
    assert {"defect_set", "strain_atlas", "supercell_strains", "alloy_ensemble"} <= set(campaigns)
    assert len(List_Runs("defect_set")) == 196
    found = Find_Runs("VA-element-single-impurity/As/GGA-PBE")
    assert len(found) == 1
    campaign, identifier = found[0]
    description = Describe_Run(campaign, identifier)
    shapes = description["shapes"]
    assert isinstance(shapes, dict)
    assert shapes["charge_density"] == [80, 80, 80]
    assert description["units"]
    field = Load_Run_Field(campaign, identifier, "charge_density")
    assert field.shape == (80, 80, 80)


@pytest.mark.pool
def Test_The_Summary_Tables_Match_The_Records() -> None:
    """the orbit and exclusion tables reproduce the measured counts"""
    orbit_rows = Orbit_Summary()
    totals = [row for row in orbit_rows if row["family"] == "all"]
    assert totals[0]["orbits"] == 296 and totals[0]["runs"] == 2680
    exclusion_rows = Exclusion_Summary()
    by_identifier = {str(row["identifier"]): int(str(row["runs"])) for row in exclusion_rows}
    assert by_identifier["E1"] == 6 and by_identifier["E6"] == 73 and by_identifier["E10"] == 1


def Test_The_Suite_Draws_Every_Rank_The_Package_Produces(tmp_path: Path) -> None:
    """each rank an inspection dict can hold reaches a renderer, and none is skipped"""
    generator = np.random.default_rng(31)
    inspected = {
        "part.a_scalar": np.asarray(2.5),
        "part.layer_0_biases": np.zeros(8),
        "part.basis_singular_values": np.asarray([9.0, 4.0, 1.0, 0.25]),
        "part.basis_mode_norms": np.ones(4),
        "part.layer_0_weights": generator.normal(size=(8, 5)),
        "part.basis_mean": generator.normal(size=(6, 6, 6)),
        "part.basis_modes": generator.normal(size=(4, 6, 6, 6)),
        "part.mode_weights_real": generator.normal(size=(3, 3, 3, 2, 2)),
    }
    suite = Render_Inspection_Suite(inspected, tmp_path, "part")
    assert suite.skipped == ()
    # one figure per array, plus the one panel every scalar shares
    assert len(suite.written) == len(inspected)
    for path in suite.written:
        assert path.is_file() and path.stat().st_size > 1000


def Test_A_Constant_Array_Does_Not_Break_The_Colour_Scale(tmp_path: Path) -> None:
    """every bias in the package initializes to exactly zero, and a flat colour bar is degenerate"""
    inspected = {"part.layer_0_weights": np.zeros((4, 4)), "part.flat_field": np.zeros((5, 5, 5))}
    suite = Render_Inspection_Suite(inspected, tmp_path, "part")
    assert suite.skipped == ()
    assert all(path.stat().st_size > 1000 for path in suite.written)


def Test_The_Suite_Is_Byte_Deterministic(tmp_path: Path) -> None:
    """committed figures are only cheap if unchanged arrays re-render to the same bytes"""
    generator = np.random.default_rng(32)
    inspected = {"part.basis_modes": generator.normal(size=(3, 6, 6, 6))}
    digests: list[str] = []
    for attempt in ("first", "second"):
        suite = Render_Inspection_Suite(inspected, tmp_path / attempt, "part")
        digests.append(hashlib.sha256(suite.written[0].read_bytes()).hexdigest())
    assert digests[0] == digests[1]
    moved = {"part.basis_modes": np.asarray(inspected["part.basis_modes"]) * 2.0}
    changed = Render_Inspection_Suite(moved, tmp_path / "changed", "part")
    assert hashlib.sha256(changed.written[0].read_bytes()).hexdigest() != digests[0]


def Test_An_Owner_Path_Survives_Into_The_File_Name(tmp_path: Path) -> None:
    """a key nested under its owner must not collide with the same name under another"""
    inspected = {
        "encoder.last_coefficients": np.arange(4.0),
        "readout.last_coefficients": np.arange(4.0) + 1.0,
    }
    suite = Render_Inspection_Suite(inspected, tmp_path, "member")
    assert len(suite.written) == 2
    assert {path.name for path in suite.written} == {
        "encoder__last_coefficients.png",
        "readout__last_coefficients.png",
    }


def Test_An_Unrenderable_Key_Is_Reported_Rather_Than_Dropped(tmp_path: Path) -> None:
    """a key with no renderer is a missing renderer, and the suite has to say so"""
    inspected = {"part.six_dimensional": np.zeros((2, 2, 2, 2, 2, 2))}
    suite = Render_Inspection_Suite(inspected, tmp_path, "part")
    assert suite.written == ()
    assert suite.skipped == ("part.six_dimensional",)


def Test_A_One_Sided_Difference_Is_Not_Drawn_As_A_Sign_Change(tmp_path: Path) -> None:
    """a diverging map over a range that never crosses zero reads as a sign change that is not there"""
    from operators.inspection.plots import Centred_On_Zero

    assert Centred_On_Zero(np.asarray([-0.006, -0.001])) == (-0.006, 0.006)
    assert Centred_On_Zero(np.asarray([0.2, 0.5])) == (-0.5, 0.5)
    truth = np.abs(np.random.default_rng(41).normal(size=(8, 8, 8))) + 1.0
    # a prediction that is low everywhere, which is exactly the one-sided case
    written = Render_Prediction_Against_Truth(truth - 0.01, truth, tmp_path / "one_sided.png", "low everywhere")
    assert written.is_file() and written.stat().st_size > 1000


def Test_The_Result_Figures_Draw_From_Scored_Numbers(tmp_path: Path) -> None:
    """the error spread and the floor comparison render from the same numbers the report tabulates"""
    generator = np.random.default_rng(42)
    spread = Render_Error_Spread(
        {"uniaxial": np.abs(generator.normal(size=6)), "isotropic": np.abs(generator.normal(size=3))},
        tmp_path / "spread.png",
        "test error by family",
    )
    floors = Render_Floor_Comparison(
        {"ridge_to_coefficients": 0.0041, "nearest_neighbor_copy": 0.0090},
        0.0011,
        {"ridge_to_coefficients": 0.25, "nearest_neighbor_copy": 0.5},
        tmp_path / "floors.png",
        "against its floors",
    )
    for path in (spread, floors):
        assert path.is_file() and path.stat().st_size > 1000

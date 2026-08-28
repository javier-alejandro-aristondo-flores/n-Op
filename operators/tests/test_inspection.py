"""the inspection catalog, the summary tables, the renderers and the rendering seam"""

import ast
from pathlib import Path

import numpy as np
import pytest

from operators.data.store import POOL_ROOT
from operators.inspection import (
    Describe_Run,
    Exclusion_Summary,
    Find_Runs,
    Fold_Balance,
    List_Campaigns,
    List_Runs,
    Load_Run_Field,
    Orbit_Summary,
    Render_Table,
)
from operators.inspection.plots import Render_Curves, Render_Field_Slices

PACKAGE_ROOT = Path(__file__).resolve().parent.parent

RENDERING_SEAM = PACKAGE_ROOT / "inspection" / "plots.py"


def Test_The_Rendering_Seam_Holds() -> None:
    """the plotting library is imported by the one rendering module alone"""
    for source_path in PACKAGE_ROOT.rglob("*.py"):
        if source_path == RENDERING_SEAM or ".pytest_cache" in source_path.parts:
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
    if not POOL_ROOT.exists():
        pytest.fail("the corpus at /Pool/VASP_DATA is not mounted on this machine")
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
    if not POOL_ROOT.exists():
        pytest.fail("the corpus at /Pool/VASP_DATA is not mounted on this machine")
    orbit_rows = Orbit_Summary()
    totals = [row for row in orbit_rows if row["family"] == "all"]
    assert totals[0]["orbits"] == 296 and totals[0]["runs"] == 2680
    exclusion_rows = Exclusion_Summary()
    by_identifier = {str(row["identifier"]): int(str(row["runs"])) for row in exclusion_rows}
    assert by_identifier["E1"] == 6 and by_identifier["E6"] == 73 and by_identifier["E10"] == 1

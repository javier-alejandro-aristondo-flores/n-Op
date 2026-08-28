"""Checks the orbit map's symmetry algebra and its recorded collapses on the live census."""

import pytest

from operators.data.orbits import Canonical_Orbit, Orbit_Map, Strain_Tensor_Of, StrainAssignment
from operators.data.store import POOL_ROOT, Read_Census


def Require_The_Pool() -> None:
    """Fails the calling test when the corpus partition is not mounted."""
    if not POOL_ROOT.exists():
        pytest.fail("the corpus at /Pool/VASP_DATA is not mounted on this machine")


def Atlas() -> tuple[StrainAssignment, ...]:
    """Builds the orbit map from the live census."""
    return Orbit_Map(Read_Census(POOL_ROOT))


def Test_Signed_Permutations_Collapse_Known_Equalities() -> None:
    """Asserts the byte-verified duplicate triple and textbook symmetries share orbits."""
    one_angle = Canonical_Orbit(Strain_Tensor_Of("shear_xz_g-0.100", None))
    assert one_angle == Canonical_Orbit(Strain_Tensor_Of("shear_xy_xz_g1_0.000_g2_-0.1", None))
    assert one_angle == Canonical_Orbit(Strain_Tensor_Of("shear_xz_yz_g1_-0.1_g2_0.000", None))
    assert one_angle == Canonical_Orbit(Strain_Tensor_Of("shear_xy_g0.100", None))
    assert Canonical_Orbit(Strain_Tensor_Of("uniax_x_eps0.050", None)) == Canonical_Orbit(
        Strain_Tensor_Of("uniax_z_eps0.050", None)
    )
    assert Canonical_Orbit(Strain_Tensor_Of("uniax_x_eps0.050", None)) != Canonical_Orbit(
        Strain_Tensor_Of("uniax_x_eps-0.050", None)
    )
    assert Canonical_Orbit(Strain_Tensor_Of("vol_3D_ex_-0.02_ey_0.04_ez_0.06", None)) == Canonical_Orbit(
        Strain_Tensor_Of("vol_3D_ex_0.06_ey_-0.02_ez_0.04", None)
    )


@pytest.mark.pool
def Test_The_Atlas_Has_The_Recorded_Point_And_Pair_Structure() -> None:
    """Asserts 2,680 runs form 1,340 points, each with one cheap and one accurate run."""
    Require_The_Pool()
    atlas = Atlas()
    assert len(atlas) == 2680
    by_point: dict[str, set[str]] = {}
    for assignment in atlas:
        by_point.setdefault(f"{assignment.run_path.rsplit('/', 1)[0]}", set()).add(assignment.functional)
    assert len(by_point) == 1340
    assert all(functionals == {"cheap", "accurate"} for functionals in by_point.values())


@pytest.mark.pool
def Test_The_Recorded_Orbit_Collapses_Replicate() -> None:
    """Asserts the measured family collapses: 512 to 120, 120 to 20, and 40 apiece."""
    Require_The_Pool()
    atlas = Atlas()

    def Family_Counts(family: str) -> tuple[int, int]:
        """Returns distinct points and distinct orbits in one family."""
        members = [a for a in atlas if a.family == family]
        return len({a.point for a in members}), len({a.orbit for a in members})

    assert Family_Counts("triaxial") == (512, 120)
    assert Family_Counts("one_angle_shear") == (120, 20)
    assert Family_Counts("uniaxial") == (120, 40)
    assert Family_Counts("biaxial") == (120, 40)
    assert Family_Counts("isotropic")[0] == 47


@pytest.mark.pool
def Test_The_Auxiliary_Sweep_Adds_No_Orbits() -> None:
    """Asserts the 160-point auxiliary sweep contributes zero new orbit units."""
    Require_The_Pool()
    atlas = Atlas()
    with_auxiliary = {a.orbit for a in atlas}
    without_auxiliary = {a.orbit for a in atlas if not a.auxiliary}
    assert with_auxiliary == without_auxiliary
    assert sum(1 for a in atlas if a.auxiliary) == 320


@pytest.mark.pool
def Test_The_Label_Unit_Count_Is_Near_The_Recorded_Number() -> None:
    """Asserts the exact-symmetry label units land near the recorded two hundred ninety-nine."""
    Require_The_Pool()
    orbit_count = len({a.orbit for a in Atlas()})
    print(f"exact orbit unit count: {orbit_count}")
    assert 260 <= orbit_count <= 340

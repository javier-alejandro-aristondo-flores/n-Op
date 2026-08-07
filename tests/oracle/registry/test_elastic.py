"""Elastic constants: against a published fit, and against a second physical route.

Two oracles, and they check different things.

The **published fit** in `apparatus/data/diamond-strain-sweep/02-how-to-read-and-derive.md` §C2 gives
C11/C12/C44 at three strain windows, with and without the linear term. Reproducing the
*contrast* between those rows is the strongest part: it is a claim about how the method
fails, not just where it lands, and a fit that reproduces one number by luck will not
reproduce a 98 GPa swing in C44 in the right direction.

The **equation-of-state route** is fully independent -- a Birch-Murnaghan fit at PBE's own
equilibrium plus a pressure correction back to the experimental reference. It shares no
code path and no strain algebra with the energy-curvature fit, so agreement between them
is evidence neither can manufacture alone.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

from programs.oracle.registry.elastic import (
    ElasticFit,
    fit_elastic_constants,
    green_lagrange_voigt,
    reference_cell,
)
from programs.oracle.units import EV_PER_ANGSTROM3_TO_GPA

DEFAULT_CACHE = Path.home() / ".cache" / "n-op-vasp"

# The dataset's §C2 table: (window, linear included) -> (C11, C12, C44, B, RMS meV)
PUBLISHED = {
    (0.021, False): (1073.1, 141.4, 570.3, 451.9, 7.450),
    (0.021, True): (1077.4, 140.4, 574.7, 452.7, 1.045),
    (0.011, False): (1057.0, 133.9, 554.9, 441.6, 2.817),
    (0.011, True): (1071.2, 138.3, 570.5, 449.3, 0.129),
    (0.006, False): (1017.3, 124.2, 492.7, 421.9, 1.641),
    (0.006, True): (1078.5, 139.9, 590.7, 452.8, 0.027),
}


# ---------------------------------------------------------------------------
# Strain algebra. No data required.
# ---------------------------------------------------------------------------

def test_undeformed_cell_has_zero_strain():
    cell = reference_cell(3.567)
    assert np.allclose(green_lagrange_voigt(cell, cell), 0.0, atol=1e-15)


def test_uniform_dilation_is_pure_normal_strain():
    """A cell scaled by (1+d) gives e1=e2=e3=d+d^2/2 exactly, and no shear.

    The quadratic piece is not a rounding artifact -- Green-Lagrange strain is finite, and
    a fit that assumed the linear form would be wrong in the third significant figure at
    the windows used here.
    """
    a0, d = 3.567, 0.01
    e = green_lagrange_voigt(reference_cell(a0) * (1 + d), reference_cell(a0))
    expected = d + d * d / 2.0
    assert np.allclose(e[:3], expected, rtol=1e-12)
    assert np.allclose(e[3:], 0.0, atol=1e-14)


def test_a_simple_shear_lands_in_the_shear_components_only():
    """Guards the transpose in the deformation gradient.

    Getting `F` transposed is invisible on every symmetric strain -- which is every normal
    family -- and wrong on exactly the sheared half that determines C44.
    """
    a0, g = 3.567, 0.02
    shear = np.array([[1.0, g, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    e = green_lagrange_voigt(reference_cell(a0) @ shear.T, reference_cell(a0))
    assert abs(e[5]) == pytest.approx(g, rel=1e-9)      # e6 = 2*E12
    assert np.allclose([e[3], e[4]], 0.0, atol=1e-14)
    assert e[1] == pytest.approx(g * g / 2.0, rel=1e-9)  # the finite-strain companion


# ---------------------------------------------------------------------------
# The fitter against its own basis. No data required.
# ---------------------------------------------------------------------------

def _synthetic(c11=1071.2, c12=138.3, c44=570.5, sigma0=2.0, v0=11.3462, n=120, amp=0.010):
    rng = np.random.default_rng(20260802)
    strains = rng.uniform(-amp, amp, size=(n, 6))
    k = EV_PER_ANGSTROM3_TO_GPA
    density = (
        (sigma0 / k) * strains[:, :3].sum(axis=1)
        + 0.5 * (c11 / k) * (strains[:, :3] ** 2).sum(axis=1)
        + (c12 / k) * (strains[:, 0] * strains[:, 1] + strains[:, 1] * strains[:, 2]
                       + strains[:, 2] * strains[:, 0])
        + 0.5 * (c44 / k) * (strains[:, 3:] ** 2).sum(axis=1)
    )
    return strains, density * v0 - 18.18, v0


def test_fit_recovers_the_constants_it_was_generated_from():
    strains, energies, v0 = _synthetic()
    fit = fit_elastic_constants(strains, energies, v0, strain_window=0.011)
    assert fit.c11 == pytest.approx(1071.2, rel=1e-8)
    assert fit.c12 == pytest.approx(138.3, rel=1e-8)
    assert fit.c44 == pytest.approx(570.5, rel=1e-8)
    assert fit.reference_stress == pytest.approx(2.0, rel=1e-6)
    assert fit.rms_residual_mev < 1e-6


def test_omitting_the_linear_term_biases_a_curve_that_has_one():
    """The whole reason the linear term is mandatory, in one assertion."""
    strains, energies, v0 = _synthetic(sigma0=2.0)
    with_linear = fit_elastic_constants(strains, energies, v0, 0.011, with_linear=True)
    without = fit_elastic_constants(strains, energies, v0, 0.011, with_linear=False)
    assert with_linear.c44 == pytest.approx(570.5, rel=1e-8)
    assert abs(without.c44 - 570.5) > 1.0
    assert without.rms_residual_mev > 100 * with_linear.rms_residual_mev


def test_too_few_points_refuses_rather_than_returning_a_number():
    strains, energies, v0 = _synthetic(n=4)
    with pytest.raises(ValueError, match="cannot determine"):
        fit_elastic_constants(strains, energies, v0, strain_window=0.011)


def test_derived_quantities():
    fit = ElasticFit(c11=1065.3, c12=132.7, c44=570.0, reference_stress=2.1,
                     rms_residual_mev=0.07, n_points=35, strain_window=0.011)
    assert fit.bulk_modulus == pytest.approx((1065.3 + 2 * 132.7) / 3)
    assert fit.tetragonal_shear == pytest.approx(1065.3 - 132.7)
    assert all(fit.born_stable().values()), "diamond is mechanically stable"


def test_born_criteria_catch_an_unstable_tensor():
    unstable = ElasticFit(c11=100.0, c12=200.0, c44=50.0, reference_stress=None,
                          rms_residual_mev=0.0, n_points=10, strain_window=0.011)
    assert unstable.born_stable()["C11 - C12 > 0"] is False


# ---------------------------------------------------------------------------
# Real data.
# ---------------------------------------------------------------------------

pytest.importorskip("pymatgen", reason="the VASP reader needs pymatgen")


@pytest.fixture(scope="module")
def sweep():
    from programs.oracle.seams.sweep import read_all_families

    cache = Path(os.environ.get("NOP_SWEEP_CACHE", DEFAULT_CACHE))
    if not cache.is_dir():
        pytest.skip(f"no extracted sweep at {cache}; run apparatus/tools/extract_sweep_family.sh")
    points = read_all_families(cache)
    if len(points) < 500:
        pytest.skip(f"only {len(points)} points extracted; the elastic fit wants all families")

    a0 = reference_cell(3.567)
    strains = np.array([green_lagrange_voigt(p.frame.state.cell, a0) for p in points])
    energies = np.array([p.frame.total_energy for p in points])
    return strains, energies, float(abs(np.linalg.det(a0)))


def test_shear_constants_match_the_published_fit(sweep):
    """C44 and C11-C12 are the combinations both routes determine independently."""
    fit = fit_elastic_constants(*sweep, strain_window=0.011)
    assert fit.c44 == pytest.approx(PUBLISHED[(0.011, True)][2], abs=3.0)
    assert fit.tetragonal_shear == pytest.approx(932.9, abs=3.0)


def test_the_difference_from_the_published_fit_is_purely_hydrostatic(sweep):
    """Stated as it is, not hidden -- and it has structure worth pinning.

    C11 and C12 both land about 5.7 GPa under the published values, by the *same absolute
    amount*, while C11-C12 and C44 match. That is the algebraic signature of a difference
    living entirely in the hydrostatic combination: if `dC11 = dC12 = d` then C11-C12 is
    untouched and `d(C11+2C12) = 3d`, so the whole discrepancy is `3d` in `3B`.

    Which value is right is settled by the independent equation-of-state route below, and
    it favors the one computed here. So this is pinned as a known, structured difference
    rather than asserted away or silently accepted.
    """
    fit = fit_elastic_constants(*sweep, strain_window=0.011)
    published_c11, published_c12, _, published_b, _ = PUBLISHED[(0.011, True)]

    shift_c11 = fit.c11 - published_c11
    shift_c12 = fit.c12 - published_c12
    assert shift_c11 < 0 and shift_c12 < 0
    assert shift_c11 == pytest.approx(shift_c12, abs=1.0), "the shift is common to both"
    assert abs(shift_c11) < 8.0

    # ...and it is exactly the bulk-modulus difference, three times over.
    assert (fit.bulk_modulus - published_b) == pytest.approx(shift_c11, abs=0.5)


def test_the_linear_term_contrast_reproduces_on_real_data(sweep):
    """The published table's own claim: omitting it costs ~15% on C44 at |e| <= 0.006.

    This is the sharpest test in the file, because it is a prediction about a failure
    mode. Reproducing a 96 GPa swing in the right direction cannot happen by accident.
    """
    strains, energies, v0 = sweep
    included = fit_elastic_constants(strains, energies, v0, 0.006, with_linear=True)
    omitted = fit_elastic_constants(strains, energies, v0, 0.006, with_linear=False)

    assert omitted.c44 < included.c44
    shortfall = (included.c44 - omitted.c44) / included.c44
    assert 0.12 < shortfall < 0.20, f"expected ~15% shortfall in C44, got {shortfall:.1%}"
    assert omitted.rms_residual_mev > 50 * included.rms_residual_mev


def test_residual_falls_as_the_window_tightens(sweep):
    """Anharmonicity is real, so a quadratic form must fit better on a smaller window.

    A fit whose residual did *not* fall would be dominated by something other than the
    physics it claims to model.
    """
    strains, energies, v0 = sweep
    rms = [fit_elastic_constants(strains, energies, v0, w).rms_residual_mev
           for w in (0.021, 0.011, 0.006)]
    assert rms == sorted(rms, reverse=True)
    assert rms[-1] < 0.05


def test_two_independent_routes_agree_on_the_bulk_modulus(sweep):
    """Energy curvature about the experimental reference, against an equation-of-state fit
    at PBE's own equilibrium corrected back by `B0' * dP`.

    These share no strain algebra and no fitting code. The dataset calls this
    reconciliation "the strongest single validation in the dataset".
    """
    from programs.oracle.registry.eos import fit_energy_volume
    from programs.oracle.seams.sweep import (energy_volume_curve, pressure_volume_curve,
                                      read_family)

    cache = Path(os.environ.get("NOP_SWEEP_CACHE", DEFAULT_CACHE))
    family_one = read_family(cache / "1-scale-all-axes-uniformly")
    eos = fit_energy_volume(*energy_volume_curve(family_one))

    volumes, pressures = pressure_volume_curve(family_one)
    near = [(v, p) for v, p in zip(volumes, pressures) if abs(p) < 5.0]
    slope, intercept = np.polyfit([v for v, _ in near], [p for _, p in near], 1)

    reference_volume = sweep[2]
    pressure_at_reference = slope * reference_volume + intercept
    predicted = eos.bulk_modulus + eos.bulk_modulus_pressure_derivative * pressure_at_reference

    elastic = fit_elastic_constants(*sweep, strain_window=0.011).bulk_modulus
    assert elastic == pytest.approx(predicted, rel=0.01), (
        f"elastic route {elastic:.1f} vs EOS route corrected to the same reference "
        f"{predicted:.1f} GPa"
    )


def test_the_elastic_ledger_target_is_met_for_c11_and_c44_and_missed_for_c12(sweep):
    """Regime #36 is +/-5% on the elastic tensor. Two of three constants meet it.

    C12 is the one that does not, under either this fit or the published one, and it is a
    property of the functional rather than of the fit: PBE overestimates diamond's C12.
    Recorded as a measured outcome, not smoothed over.
    """
    fit = fit_elastic_constants(*sweep, strain_window=0.011)
    experiment = {"C11": 1079.0, "C12": 124.0, "C44": 578.0}
    deviation = {
        "C11": abs(fit.c11 - experiment["C11"]) / experiment["C11"],
        "C12": abs(fit.c12 - experiment["C12"]) / experiment["C12"],
        "C44": abs(fit.c44 - experiment["C44"]) / experiment["C44"],
    }
    assert deviation["C11"] < 0.05
    assert deviation["C44"] < 0.05
    assert deviation["C12"] > 0.05, "if PBE's C12 now meets +/-5%, this finding has changed"
    assert deviation["C12"] < 0.12

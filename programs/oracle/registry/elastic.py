"""Elastic constants from an energy-versus-strain series.

Registry row 60 is `elastic-constants-Cij` with signature `(stress(strain)) -> C_ij`. This
is the **energy-curvature** route instead: the second derivative of the energy density with
respect to Green-Lagrange strain. It needs no stress at all, which matters here because the
stress in this dataset carries a measured Pulay bias while the energy does not.

**The linear term is mandatory, and this is the single most expensive thing to get wrong.**
The sweep's strains are defined about the *experimental* lattice constant, which is not the
functional's equilibrium, so the crystal is under a real stress at zero strain and a genuine
linear term exists. Dropping it does not merely add scatter -- it biases the answer, worst
at the tightest window where the fit should be most trustworthy:

    |e| <= 0.006, linear omitted    C44 = 492.7    (13.7% low)
    |e| <= 0.006, linear included   C44 = 590.7

The dataset calls this "the single most common way to get wrong numbers out of this data".

The energy density is per **reference** volume. Green-Lagrange strain is referred to the
undeformed configuration, so its work conjugate is the second Piola-Kirchhoff stress and the
elastic constants it produces are referred to that same configuration. Dividing by the
current volume instead mixes two configurations: tested, and it does not merely tilt the
answer, it destroys it -- C11 falls from 1065 to 306 GPa and C12 goes negative.

## Measured agreement with the published fit, and the one place it differs

Against §C2's table at `|e| <= 0.011` with the linear term, over all 1,179 sweep points:

    C44          570.0   published 570.5    matches
    C11 - C12    932.6   published 932.9    matches
    C11         1065.3   published 1071.2   -5.9
    C12          132.7   published 138.3    -5.6

The two shifts are equal to within 0.3 GPa, which is the algebraic signature of a
difference living **entirely in the hydrostatic combination**: with `dC11 = dC12 = d`,
`C11 - C12` is untouched and the whole discrepancy appears as `3d` in `C11 + 2C12`. Every
shear quantity agrees; only the bulk modulus moves, by 5.7 GPa.

**The independent route favors the value computed here.** An equation-of-state fit at
PBE's own equilibrium, corrected back to the experimental reference by `B0' * dP`,
predicts 442.1 GPa. This fit gives 443.6 -- agreement to **0.34%**. The published elastic
value of 449.3 reconciles to 1.6% against the same prediction. The two routes share no
strain algebra and no fitting code, so this is not a self-check.

The residual is also smaller here at every window (0.072 against 0.129 meV at the
recommended one). The difference is not resolved to a cause and is left visible rather
than tuned away.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..units import EV_PER_ANGSTROM3_TO_GPA


def reference_cell(lattice_constant: float = 3.567) -> np.ndarray:
    """The undeformed 2-atom face-centered-cubic cell, rows as lattice vectors.

    `(0,a/2,a/2), (a/2,0,a/2), (a/2,a/2,0)` -- the convention the sweep's own index states,
    with reference volume `a^3/4`. The default is the **experimental** constant, because
    that is what the sweep's strains are defined about; it is deliberately not the
    functional's equilibrium, and that mismatch is why the linear term below exists.
    """
    h = lattice_constant / 2.0
    return np.array([[0.0, h, h], [h, 0.0, h], [h, h, 0.0]])


def green_lagrange_voigt(cell: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Green-Lagrange strain of `cell` relative to `reference`, in Voigt order.

    Rows of both matrices are lattice vectors, so a vector transforms as `a = a0 @ F.T`
    and therefore `F = (inv(A0) @ A).T`. Getting that transpose wrong is invisible for the
    diagonal families -- symmetric strains are unchanged by it -- and wrong for every
    sheared one, which is exactly the half that determines C44.

    Returns `(e1, e2, e3, e4, e5, e6)` with the engineering convention on shear,
    `e4 = 2*E23`, so that the strain energy is `1/2 C44 e4^2` per shear component.
    """
    deformation = (np.linalg.inv(reference) @ cell).T
    strain = 0.5 * (deformation.T @ deformation - np.eye(3))
    return np.array([
        strain[0, 0], strain[1, 1], strain[2, 2],
        2.0 * strain[1, 2], 2.0 * strain[0, 2], 2.0 * strain[0, 1],
    ])


def _design_row(e: np.ndarray, with_linear: bool) -> list[float]:
    """One row of the cubic-symmetry design matrix.

    U = sigma0*(e1+e2+e3) + 1/2 C11 (e1^2+e2^2+e3^2)
                          + C12 (e1e2 + e2e3 + e3e1)
                          + 1/2 C44 (e4^2+e5^2+e6^2)
    """
    row = [
        0.5 * (e[0] ** 2 + e[1] ** 2 + e[2] ** 2),          # C11
        e[0] * e[1] + e[1] * e[2] + e[2] * e[0],            # C12
        0.5 * (e[3] ** 2 + e[4] ** 2 + e[5] ** 2),          # C44
    ]
    if with_linear:
        row.append(e[0] + e[1] + e[2])                      # sigma0
    return row


@dataclass(frozen=True)
class ElasticFit:
    """Cubic elastic constants in GPa, with the evidence that the fit was real."""

    c11: float
    c12: float
    c44: float
    reference_stress: float | None   # sigma0, GPa; None when the linear term was omitted
    rms_residual_mev: float          # per cell, meV -- comparable to the dataset's table
    n_points: int
    strain_window: float

    @property
    def bulk_modulus(self) -> float:
        """`(C11 + 2 C12) / 3`, the cubic Voigt-Reuss-Hill bulk modulus.

        For cubic symmetry Voigt, Reuss and Hill coincide for the bulk modulus, so this
        needs no averaging choice. The shear moduli do, and are not offered here.
        """
        return (self.c11 + 2.0 * self.c12) / 3.0

    @property
    def tetragonal_shear(self) -> float:
        """`C11 - C12`. Reported separately because it is the combination the stress
        route measures directly, so it is the honest cross-check between routes."""
        return self.c11 - self.c12

    def born_stable(self) -> dict[str, bool]:
        """The three cubic Born criteria. Registry row 57 takes the crystal system for
        exactly this reason: the arity is symmetry-dependent, and cubic has three."""
        return {
            "C11 - C12 > 0": self.tetragonal_shear > 0.0,
            "C11 + 2 C12 > 0": (self.c11 + 2.0 * self.c12) > 0.0,
            "C44 > 0": self.c44 > 0.0,
        }


def fit_elastic_constants(
    strains,
    energies,
    reference_volume: float,
    strain_window: float = 0.011,
    with_linear: bool = True,
) -> ElasticFit:
    """Least-squares fit of the cubic elastic constants to energy versus strain.

    `energies` are total cell energies in eV; they are converted to a density over
    `reference_volume` internally. Only points whose largest Voigt component is within
    `strain_window` are used, and duplicate strain states are collapsed first so a shape
    computed three times does not carry three times the weight.

    The energy zero is a free parameter of the fit rather than something the caller must
    supply, because absolute VASP energies are not comparable across functionals and the
    curvature does not depend on the offset.
    """
    strains = np.asarray(strains, dtype=np.float64)
    energies = np.asarray(energies, dtype=np.float64)

    inside = np.max(np.abs(strains), axis=1) <= strain_window
    strains, energies = strains[inside], energies[inside]

    # Collapse duplicate shapes. The sweep contains 24 shapes computed three times each;
    # left in, they would trebly weight one corner of the strain space.
    _, unique = np.unique(np.round(strains, 9), axis=0, return_index=True)
    strains, energies = strains[np.sort(unique)], energies[np.sort(unique)]

    n_terms = 4 if with_linear else 3
    if strains.shape[0] < n_terms + 1:
        raise ValueError(
            f"{strains.shape[0]} unique points inside |e| <= {strain_window} cannot "
            f"determine {n_terms} constants plus an energy zero"
        )

    # Columns: the basis terms, then a constant for the unknown energy zero.
    design = np.array([_design_row(e, with_linear) + [1.0] for e in strains])
    density = energies / reference_volume          # eV / angstrom^3

    coefficients, *_ = np.linalg.lstsq(design, density, rcond=None)
    residuals = density - design @ coefficients
    rms_mev = float(np.sqrt(np.mean(residuals ** 2)) * reference_volume * 1000.0)

    c11, c12, c44 = (float(c) * EV_PER_ANGSTROM3_TO_GPA for c in coefficients[:3])
    sigma0 = float(coefficients[3]) * EV_PER_ANGSTROM3_TO_GPA if with_linear else None

    return ElasticFit(
        c11=c11,
        c12=c12,
        c44=c44,
        reference_stress=sigma0,
        rms_residual_mev=rms_mev,
        n_points=int(strains.shape[0]),
        strain_window=strain_window,
    )

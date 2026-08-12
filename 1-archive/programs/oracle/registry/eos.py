"""The equation of state, and the two independent routes to the equilibrium volume.

The oracle scores; it does not solve. So it never *relaxes* a structure -- the caller
supplies candidates and the oracle says how far each sits from stationarity. Given a
series of candidates at different volumes, two independent readouts locate the volume at
which the structural residual vanishes:

    energy route     V0 is where dE/dV = 0        -- the minimum of E(V)
    stress route     V0 is where P(V) = 0         -- the zero of the mean stress

**They must agree, and they do not.** Their gap is a real, understood quantity: the Pulay
stress, an incomplete-basis-set artifact of computing stress at fixed plane-wave cutoff
while the cell changes. It is not noise and not a bug in either route. On the diamond
sweep it is measured at **+0.109% (PBE) and +0.122% (HSE06)**, and the agreement between
two very different functionals is what shows it to be a property of the shared 550 eV
cutoff rather than of the physics.

That disagreement is exactly an `Algebraic/MethodEquivalence` residual, and it is worth
more than either route alone: a residual that grades the *calculation's convergence*
rather than the structure. Neither route can report it by itself, which is why both are
here.

No registry row emits an equilibrium geometry ([accuracy-ledger] carries that as
anchor-met, path-open), so these are named readouts rather than registry formulas.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..units import EV_PER_ANGSTROM3_TO_GPA


@dataclass(frozen=True)
class EquationOfState:
    """A third-order Birch-Murnaghan fit, with the residual that shows it fitted."""

    equilibrium_volume: float      # angstrom^3
    bulk_modulus: float            # GPa
    bulk_modulus_pressure_derivative: float   # dimensionless
    energy_at_minimum: float       # eV
    max_residual_ev: float         # largest |E_fit - E_data| over the fitted points
    n_points: int

    @property
    def cubic_lattice_constant(self) -> float:
        """Conventional cubic `a` from the primitive volume: `V = a^3 / 4` for fcc.

        Only meaningful for a face-centered-cubic primitive cell, which the diamond
        structure has. The caller is responsible for that being true; nothing here can
        check it, and a wrong answer would be plausible rather than obviously wrong.
        """
        return float((4.0 * self.equilibrium_volume) ** (1.0 / 3.0))




def birch_murnaghan_energy(volume, energy_min, volume_0, bulk_modulus, bulk_prime):
    """Third-order Birch-Murnaghan `E(V)`, with `bulk_modulus` in GPa.

    Written in the standard eta = (V0/V)^(2/3) form. The bulk modulus is converted to
    eV/angstrom^3 inside, so every argument and the return value are in the module's
    canonical units and no caller has to remember a conversion.
    """
    volume = np.asarray(volume, dtype=np.float64)
    b0 = bulk_modulus / EV_PER_ANGSTROM3_TO_GPA
    eta = (volume_0 / volume) ** (2.0 / 3.0)
    return energy_min + (9.0 * volume_0 * b0 / 16.0) * (
        (eta - 1.0) ** 3 * bulk_prime + (eta - 1.0) ** 2 * (6.0 - 4.0 * eta)
    )


def fit_energy_volume(volumes, energies) -> EquationOfState:
    """Fit `E(V)`, returning the equilibrium volume, bulk modulus and its derivative.

    The initial guess comes from a parabola through the data rather than from constants,
    so the fit does not need to be told roughly where the answer is -- which matters
    because being told would let it succeed on data that does not support the answer.

    The reported residual is the largest absolute deviation, not the root-mean-square:
    an average hides a single bad point, and a single bad point is what a parse error
    looks like.
    """
    from scipy.optimize import curve_fit

    volumes = np.asarray(volumes, dtype=np.float64)
    energies = np.asarray(energies, dtype=np.float64)
    if volumes.size < 4:
        raise ValueError(
            f"a third-order fit has four parameters; {volumes.size} points cannot determine it"
        )

    # Parabolic seed: E = aV^2 + bV + c gives V0 = -b/2a and B0 = 2a*V0 (in eV/A^3).
    a, b, _ = np.polyfit(volumes, energies, 2)
    v0_seed = -b / (2.0 * a)
    b0_seed = 2.0 * a * v0_seed * EV_PER_ANGSTROM3_TO_GPA
    seed = (float(energies.min()), float(v0_seed), float(b0_seed), 4.0)

    params, _ = curve_fit(birch_murnaghan_energy, volumes, energies, p0=seed, maxfev=20000)
    energy_min, volume_0, bulk_modulus, bulk_prime = (float(p) for p in params)

    residuals = energies - birch_murnaghan_energy(volumes, *params)
    return EquationOfState(
        equilibrium_volume=volume_0,
        bulk_modulus=bulk_modulus,
        bulk_modulus_pressure_derivative=bulk_prime,
        energy_at_minimum=energy_min,
        max_residual_ev=float(np.max(np.abs(residuals))),
        n_points=int(volumes.size),
    )


def equilibrium_volume_from_pressure(volumes, pressures, window_gpa: float = 3.0) -> float:
    """The volume at which the mean stress vanishes, by interpolation.

    Fits a line to the points within `window_gpa` of zero pressure and returns its root.
    A line is the right model near the crossing, where `dP/dV = -B0/V0`; on the diamond
    series the two points bracketing zero give a slope of -37.85 GPa/angstrom^3 against a
    predicted -38.04, so the local linearity is real.

    **The window is calibrated, not chosen.** `P(V)` is convex, so a wide window biases
    the root upward in volume and the bias is monotonic. Measured on the 47-point diamond
    series, against an energy-route equilibrium of 11.4133 angstrom^3::

        window (GPa)    3     4     7.5    10     15     20
        Pulay bias %  +0.103 +0.096 +0.082 +0.069 +0.010 -0.058

    The published value is +0.109%, so only the narrow windows recover it and 20 GPa
    inverts the sign of a physical effect. The default sits at 3 GPa, where the estimate
    is flat -- 2.0, 2.5 and 3.0 GPa all return the same three points and the same root.
    A caller widening it past about 5 GPa is measuring curvature, not the crossing.

    Raises if the series does not bracket zero pressure. Extrapolating to a crossing the
    data never reaches would return a number with nothing behind it, and a plausible
    number where a refusal belongs is the failure this project keeps finding.
    """
    volumes = np.asarray(volumes, dtype=np.float64)
    pressures = np.asarray(pressures, dtype=np.float64)

    if not (pressures.min() <= 0.0 <= pressures.max()):
        raise ValueError(
            f"pressures span [{pressures.min():.3f}, {pressures.max():.3f}] GPa and do not "
            "bracket zero; the equilibrium volume is outside the sampled range"
        )

    near = np.abs(pressures) <= window_gpa
    if near.sum() < 2:
        near = np.argsort(np.abs(pressures))[:4]

    slope, intercept = np.polyfit(volumes[near], pressures[near], 1)
    return float(-intercept / slope)


def pulay_bias_percent(energy_route_volume: float, stress_route_volume: float) -> float:
    """The disagreement between the two routes, as a percentage of the energy-route volume.

    Positive means the energy route sits at a larger volume than the stress route, which
    is the sign an incomplete basis set produces. The diamond sweep measures +0.109% at
    PBE and +0.122% at the hybrid; a value near zero would mean the basis is converged
    for stress, and a much larger one that it is not.
    """
    return 100.0 * (energy_route_volume - stress_route_volume) / energy_route_volume

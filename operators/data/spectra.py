"""Spectral derivations: the density-of-states rebuild and the occupancy-walk gap."""

import numpy
from numpy.typing import NDArray

SMEARING_WIDTH_BY_CAMPAIGN: dict[str, float] = {
    "strain_atlas": 0.175,
    "perovskite_grid": 0.125,
    "supercell_strains": 0.2,
    "defect_set": 0.2,
    "relaxation_pool": 0.2,
}


def Occupancy_Walk_Gap(
    energies: NDArray[numpy.float64],
    occupancies: NDArray[numpy.float64],
    minimum_occupied_fraction: float = 0.5,
) -> float:
    """Returns the gap between the highest occupied and lowest empty state, floored at zero."""
    ceiling = float(occupancies.max())
    occupied = occupancies >= minimum_occupied_fraction * ceiling
    highest_occupied = float(energies[occupied].max())
    empty = ~occupied
    if not bool(empty.any()):
        return 0.0
    lowest_empty = float(energies[empty].min())
    return max(lowest_empty - highest_occupied, 0.0)


def Valence_Band_Maximum(
    energies: NDArray[numpy.float64],
    occupancies: NDArray[numpy.float64],
    minimum_occupied_fraction: float = 0.5,
) -> float:
    """Returns the highest occupied eigenvalue."""
    ceiling = float(occupancies.max())
    return float(energies[occupancies >= minimum_occupied_fraction * ceiling].max())


def Rebuild_Density_Of_States(
    energies: NDArray[numpy.float64],
    kpoint_weights: NDArray[numpy.float64],
    smearing_width: float,
    energy_grid: NDArray[numpy.float64],
) -> NDArray[numpy.float64]:
    """Rebuilds a Gaussian-smeared, spin-summed, weight-normalized state-density curve."""
    weights = kpoint_weights / kpoint_weights.sum()
    curve = numpy.zeros_like(energy_grid)
    prefactor = 1.0 / (smearing_width * numpy.sqrt(2.0 * numpy.pi))
    for spin_index in range(energies.shape[0]):
        for kpoint_index in range(energies.shape[1]):
            offsets = energy_grid[:, None] - energies[spin_index, kpoint_index][None, :]
            gaussians = prefactor * numpy.exp(-0.5 * (offsets / smearing_width) ** 2)
            curve = curve + weights[kpoint_index] * gaussians.sum(axis=1)
    return curve

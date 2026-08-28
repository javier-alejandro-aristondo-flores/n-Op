"""Proper orthogonal decomposition by the Gram method in double precision."""

from dataclasses import dataclass

import numpy
from numpy.typing import NDArray

type Snapshots = NDArray[numpy.float64]


@dataclass(frozen=True, slots=True)
class PodBasis:
    """A mean field with orthonormal modes and their singular values."""

    mean: NDArray[numpy.float64]
    modes: NDArray[numpy.float64]
    singular_values: NDArray[numpy.float64]


def Gram_Pod(snapshots: Snapshots, rank: int | None = None) -> PodBasis:
    """Builds the decomposition from the snapshot Gram matrix."""
    mean = snapshots.mean(axis=0)
    centered = snapshots - mean
    gram = centered @ centered.T
    solution = numpy.linalg.eigh(gram)
    descending_order = numpy.argsort(solution.eigenvalues)[::-1]
    eigenvalues = numpy.maximum(numpy.asarray(solution.eigenvalues, dtype=numpy.float64)[descending_order], 0.0)
    eigenvectors = numpy.asarray(solution.eigenvectors, dtype=numpy.float64)[:, descending_order]
    keep = eigenvalues > (float(eigenvalues[0]) * 1e-14 if float(eigenvalues[0]) > 0 else -1.0)
    if rank is not None:
        keep = keep & (numpy.arange(eigenvalues.shape[0], dtype=numpy.int64) < rank)
    singular_values = numpy.sqrt(eigenvalues[keep])
    modes = (centered.T @ eigenvectors[:, keep]) / singular_values
    return PodBasis(mean=mean, modes=modes.T, singular_values=singular_values)


def Project(basis: PodBasis, fields: Snapshots) -> NDArray[numpy.float64]:
    """Returns the mode coefficients of fields under the basis."""
    return (fields - basis.mean) @ basis.modes.T


def Reconstruct(basis: PodBasis, coefficients: NDArray[numpy.float64]) -> Snapshots:
    """Returns fields rebuilt from mode coefficients."""
    return coefficients @ basis.modes + basis.mean


def Reconstruction_Error_Curve(snapshots: Snapshots) -> NDArray[numpy.float64]:
    """Returns the relative reconstruction error of the block at every rank."""
    basis = Gram_Pod(snapshots)
    energies = basis.singular_values**2
    residual_energy = energies.sum() - numpy.cumsum(energies)
    total = float(numpy.linalg.norm(snapshots))
    return numpy.sqrt(numpy.clip(residual_energy, 0.0, None)) / total


def Basis_Decay_Gate(snapshots: Snapshots, error_bound: float = 0.03) -> tuple[bool, int]:
    """Returns whether some rank at or below half the block reaches the error bound."""
    curve = Reconstruction_Error_Curve(snapshots)
    half = snapshots.shape[0] // 2
    reachable = numpy.where(curve[:half] <= error_bound)[0]
    if reachable.size == 0:
        return False, half
    return True, int(reachable[0]) + 1

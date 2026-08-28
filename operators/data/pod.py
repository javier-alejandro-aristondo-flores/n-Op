"""proper orthogonal decomposition by the Gram method, in double precision"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

type Snapshots = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class PodBasis:
    """a mean field with orthonormal modes and their singular values"""

    mean: NDArray[np.float64]
    modes: NDArray[np.float64]
    singular_values: NDArray[np.float64]


def Gram_Pod(snapshots: Snapshots, rank: int | None = None) -> PodBasis:
    """the decomposition, built from the snapshot Gram matrix"""
    mean = snapshots.mean(axis=0)
    centered = snapshots - mean
    # the Gram matrix is one per snapshot pair, far smaller than one per voxel pair
    gram = centered @ centered.T
    solution = np.linalg.eigh(gram)
    descending_order = np.argsort(solution.eigenvalues)[::-1]
    # a Gram eigenvalue is a square, so rounding can only push it below zero
    eigenvalues = np.maximum(np.asarray(solution.eigenvalues, dtype=np.float64)[descending_order], 0.0)
    eigenvectors = np.asarray(solution.eigenvectors, dtype=np.float64)[:, descending_order]
    keep = eigenvalues > (float(eigenvalues[0]) * 1e-14 if float(eigenvalues[0]) > 0 else -1.0)
    if rank is not None:
        keep = keep & (np.arange(eigenvalues.shape[0], dtype=np.int64) < rank)
    singular_values = np.sqrt(eigenvalues[keep])
    # the snapshots carry the eigenvectors back into field space
    modes = (centered.T @ eigenvectors[:, keep]) / singular_values
    return PodBasis(mean=mean, modes=modes.T, singular_values=singular_values)


def Project(basis: PodBasis, fields: Snapshots) -> NDArray[np.float64]:
    """mode coefficients of fields under the basis"""
    return (fields - basis.mean) @ basis.modes.T


def Reconstruct(basis: PodBasis, coefficients: NDArray[np.float64]) -> Snapshots:
    """fields rebuilt from mode coefficients"""
    return coefficients @ basis.modes + basis.mean


def Reconstruction_Error_Curve(snapshots: Snapshots) -> NDArray[np.float64]:
    """relative reconstruction error of the block at every rank"""
    basis = Gram_Pod(snapshots)
    # the energy left after a rank is what that rank fails to reconstruct
    energies = basis.singular_values**2
    residual_energy = energies.sum() - np.cumsum(energies)
    total = float(np.linalg.norm(snapshots))
    return np.sqrt(np.clip(residual_energy, 0.0, None)) / total


def Basis_Decay_Gate(snapshots: Snapshots, error_bound: float = 0.03) -> tuple[bool, int]:
    """whether some rank at or below half the block reaches the error bound"""
    curve = Reconstruction_Error_Curve(snapshots)
    # past half the snapshots a basis is memorizing rather than compressing
    half = snapshots.shape[0] // 2
    reachable = np.where(curve[:half] <= error_bound)[0]
    if reachable.size == 0:
        return False, half
    return True, int(reachable[0]) + 1

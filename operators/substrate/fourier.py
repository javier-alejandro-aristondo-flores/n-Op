"""the Fourier facet, three-dimensional transforms and reciprocal-cell geometry"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.substrate.operations import Is_Engine_Native
from operators.substrate.torch_engine import Torch_Module


def Fourier_Transform_3d(value: Any) -> Any:
    """the last three axes to their complex spectrum"""
    if Is_Engine_Native(value):
        return Torch_Module().fft.fftn(value, dim=(-3, -2, -1))
    return np.fft.fftn(value, axes=(-3, -2, -1))


def Inverse_Fourier_Transform_3d(value: Any) -> Any:
    """the last three spectral axes back to real space"""
    if Is_Engine_Native(value):
        return Torch_Module().fft.ifftn(value, dim=(-3, -2, -1))
    return np.fft.ifftn(value, axes=(-3, -2, -1))


def Real_Part(value: Any) -> Any:
    """the real component of a complex array"""
    return Torch_Module().real(value) if Is_Engine_Native(value) else np.real(value)


def Reciprocal_Rows(lattice: NDArray[np.float64]) -> NDArray[np.float64]:
    """reciprocal lattice vectors as rows, in inverse angstrom times two pi"""
    return np.asarray(2.0 * np.pi * np.linalg.inv(lattice).T, dtype=np.float64)


def Centered_Modes(extent: int) -> NDArray[np.int64]:
    """each spectral index as its signed centered mode number"""
    indices = np.arange(extent, dtype=np.int64)
    # everything past the halfway point is a negative mode
    return np.where(indices <= extent // 2, indices, indices - extent)


def Cartesian_Wavevectors(lattice: NDArray[np.float64], shape: tuple[int, ...]) -> NDArray[np.float64]:
    """the Cartesian wavevector at every full-spectrum entry"""
    reciprocal = Reciprocal_Rows(lattice)
    modes = np.meshgrid(*[Centered_Modes(extent) for extent in shape], indexing="ij")
    stacked = np.stack([np.asarray(grid, dtype=np.float64) for grid in modes], axis=-1)
    return stacked @ reciprocal

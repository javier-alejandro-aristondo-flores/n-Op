"""The Fourier facet: three-dimensional transforms and reciprocal-cell geometry."""

from typing import Any

import numpy
from numpy.typing import NDArray

from operators.substrate.operations import Is_Engine_Native
from operators.substrate.torch_engine import Torch_Module


def Fourier_Transform_3d(value: Any) -> Any:
    """Transforms the last three axes to their complex spectrum."""
    if Is_Engine_Native(value):
        return Torch_Module().fft.fftn(value, dim=(-3, -2, -1))
    return numpy.fft.fftn(value, axes=(-3, -2, -1))


def Inverse_Fourier_Transform_3d(value: Any) -> Any:
    """Transforms the last three spectral axes back to real space."""
    if Is_Engine_Native(value):
        return Torch_Module().fft.ifftn(value, dim=(-3, -2, -1))
    return numpy.fft.ifftn(value, axes=(-3, -2, -1))


def Real_Part(value: Any) -> Any:
    """Returns the real component of a complex array."""
    return Torch_Module().real(value) if Is_Engine_Native(value) else numpy.real(value)


def Reciprocal_Rows(lattice: NDArray[numpy.float64]) -> NDArray[numpy.float64]:
    """Returns the reciprocal lattice vectors as rows, in inverse angstrom times two pi."""
    return numpy.asarray(2.0 * numpy.pi * numpy.linalg.inv(lattice).T, dtype=numpy.float64)


def Centered_Modes(extent: int) -> NDArray[numpy.int64]:
    """Returns each spectral index as its signed centered mode number."""
    indices = numpy.arange(extent, dtype=numpy.int64)
    return numpy.where(indices <= extent // 2, indices, indices - extent)


def Cartesian_Wavevectors(lattice: NDArray[numpy.float64], shape: tuple[int, ...]) -> NDArray[numpy.float64]:
    """Returns the Cartesian wavevector at every full-spectrum entry."""
    reciprocal = Reciprocal_Rows(lattice)
    modes = numpy.meshgrid(*[Centered_Modes(extent) for extent in shape], indexing="ij")
    stacked = numpy.stack([numpy.asarray(grid, dtype=numpy.float64) for grid in modes], axis=-1)
    return stacked @ reciprocal

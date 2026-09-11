"""the Fourier facet, a wrapped vendor transform behind the seam, plus reciprocal-cell geometry"""

# the wrapper is a decision, not an accident: the canon prices an adjoint wrapper over a vendor
# transform in days and an own Stockham transform in multi-week, calling it the suite's largest
# single kernel, so the lineage is unblocked now and that cost lever is spent elsewhere
# the direction of travel remains fully in house, and the named successor is that own Stockham
# transform, written later against exactly the signatures below
# no member imports a transform directly, so replacing these bodies touches no member at all

from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from operators.substrate.arrays import NUMPY_DTYPE_BY_PRECISION, Precision
from operators.substrate.operations import Is_Engine_Native
from operators.substrate.torch_engine import Torch_Module

GRID_AXIS_COUNT = 3

GRID_AXES = (-3, -2, -1)

COMPLEX_DTYPE_BY_PRECISION: dict[Precision, np.dtype[Any]] = {
    "single": np.dtype(np.complex64),
    "double": np.dtype(np.complex128),
}


def Split_Batch_From_Grid(field: Any) -> tuple[tuple[int, ...], tuple[int, int, int]]:
    """the leading batch-and-channel extents and the three trailing grid extents of a field"""
    extents = tuple(int(extent) for extent in field.shape)
    if len(extents) < GRID_AXIS_COUNT + 1:
        raise ValueError(f"a field carries at least one channel axis before its three grid axes, not {extents}")
    return extents[:-GRID_AXIS_COUNT], (extents[-3], extents[-2], extents[-1])


def Half_Spectrum_Extent(extent: int) -> int:
    """how many modes of the last grid axis a real field's half spectrum stores"""
    return extent // 2 + 1


def Component_Bits(value: Any) -> int:
    """the bit width of one real component of the array's entries, on either engine"""
    if Is_Engine_Native(value):
        return int(Torch_Module().finfo(value.dtype).bits)
    return int(np.finfo(value.dtype).bits)


def Effective_Precision(value: Any, working_precision: Precision) -> Precision:
    """the declared width, narrowed further when the array arrived narrow, so no transform ever promotes"""
    if working_precision == "single" or Component_Bits(value) <= 32:
        return "single"
    return "double"


def Torch_Complex_Dtype(precision: Precision) -> Any:
    """the foreign engine's complex type for a working precision"""
    torch = Torch_Module()
    return torch.complex64 if precision == "single" else torch.complex128


def Torch_Real_Dtype(precision: Precision) -> Any:
    """the foreign engine's real type for a working precision"""
    torch = Torch_Module()
    return torch.float32 if precision == "single" else torch.float64


def Real_Fourier_Transform_3d(field: Any, working_precision: Precision = "double") -> Any:
    """the three grid axes of a batched channel field to the half spectrum a real field needs"""
    Split_Batch_From_Grid(field)
    precision = Effective_Precision(field, working_precision)
    if Is_Engine_Native(field):
        return Torch_Module().fft.rfftn(field, dim=GRID_AXES).to(Torch_Complex_Dtype(precision))
    # the reference transform is overloaded on an output argument, so the kind of array it answers is spelled here
    spectrum = cast(NDArray[np.complexfloating], np.fft.rfftn(field, axes=GRID_AXES))
    return spectrum.astype(COMPLEX_DTYPE_BY_PRECISION[precision])


def Inverse_Real_Fourier_Transform_3d(
    half_spectrum: Any, grid_shape: tuple[int, int, int], working_precision: Precision = "double"
) -> Any:
    """a half spectrum back to the real batched channel field of the grid shape named here"""
    Split_Batch_From_Grid(half_spectrum)
    precision = Effective_Precision(half_spectrum, working_precision)
    if Is_Engine_Native(half_spectrum):
        returned = Torch_Module().fft.irfftn(half_spectrum, s=grid_shape, dim=GRID_AXES)
        return returned.to(Torch_Real_Dtype(precision))
    return np.fft.irfftn(half_spectrum, s=grid_shape, axes=GRID_AXES).astype(NUMPY_DTYPE_BY_PRECISION[precision])


def Fourier_Transform_3d(value: Any, working_precision: Precision = "double") -> Any:
    """the three grid axes of a batched channel field to their whole complex spectrum"""
    Split_Batch_From_Grid(value)
    precision = Effective_Precision(value, working_precision)
    if Is_Engine_Native(value):
        return Torch_Module().fft.fftn(value, dim=GRID_AXES).to(Torch_Complex_Dtype(precision))
    return np.fft.fftn(value, axes=GRID_AXES).astype(COMPLEX_DTYPE_BY_PRECISION[precision])


def Inverse_Fourier_Transform_3d(value: Any, working_precision: Precision = "double") -> Any:
    """the three trailing spectral axes of a whole complex spectrum back to real space"""
    Split_Batch_From_Grid(value)
    precision = Effective_Precision(value, working_precision)
    if Is_Engine_Native(value):
        return Torch_Module().fft.ifftn(value, dim=GRID_AXES).to(Torch_Complex_Dtype(precision))
    return np.fft.ifftn(value, axes=GRID_AXES).astype(COMPLEX_DTYPE_BY_PRECISION[precision])


def Real_Part(value: Any) -> Any:
    """the real component of a complex array"""
    return Torch_Module().real(value) if Is_Engine_Native(value) else np.real(value)


def Conjugate(value: Any) -> Any:
    """the complex conjugate of an array"""
    return Torch_Module().conj(value) if Is_Engine_Native(value) else np.conj(value)


def Complex_From_Parts(real_part: Any, imaginary_part: Any) -> Any:
    """one complex array out of the two real arrays every engine can differentiate"""
    if Is_Engine_Native(real_part):
        return Torch_Module().complex(real_part, imaginary_part)
    return real_part + 1j * imaginary_part


def Reverse_Axes(value: Any, axes: tuple[int, ...]) -> Any:
    """the array with the named axes run backwards"""
    return Torch_Module().flip(value, dims=axes) if Is_Engine_Native(value) else np.flip(value, axis=axes)


def Sliced_Along_Axis(value: Any, axis: int, start: int, stop: int) -> Any:
    """the array cut to a half-open range on one axis, every other axis left whole"""
    cutter: list[slice] = [slice(None)] * len(value.shape)
    cutter[axis] = slice(start, stop)
    return value[tuple(cutter)]


def Join_Along_Axis(pieces: list[Any], axis: int) -> Any:
    """the pieces laid end to end along one axis"""
    if any(Is_Engine_Native(piece) for piece in pieces):
        return Torch_Module().cat(pieces, dim=axis)
    return np.concatenate(pieces, axis=axis)


def Zeros_Beside(reference: Any, shape: tuple[int, ...]) -> Any:
    """zeros of the given shape, in the reference array's own width and on its own engine"""
    if Is_Engine_Native(reference):
        return Torch_Module().zeros(shape, dtype=reference.dtype, device=reference.device)
    return np.zeros(shape, dtype=reference.dtype)


def Einstein_Summation(subscripts: str, first: Any, second: Any) -> Any:
    """one Einstein summation over two arrays, on whichever engine they belong to"""
    if Is_Engine_Native(first) or Is_Engine_Native(second):
        return Torch_Module().einsum(subscripts, first, second)
    return np.einsum(subscripts, first, second)


def Hermitian_Mode_Part(block: Any, mode_axes: tuple[int, ...]) -> Any:
    """every mode averaged with the conjugate of its negative, which is all a real field can carry"""
    # reversing a centered axis of odd extent sends each mode to its own negative, which is the pairing wanted
    return (block + Conjugate(Reverse_Axes(block, mode_axes))) / 2.0


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

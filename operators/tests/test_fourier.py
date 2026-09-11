"""the real transform facet, on the reference engine and the foreign one"""

import numpy as np
import pytest

from operators.substrate import (
    Engine,
    Fourier_Transform_3d,
    Half_Spectrum_Extent,
    Inverse_Real_Fourier_Transform_3d,
    NumpyEngine,
    Real_Fourier_Transform_3d,
    Split_Batch_From_Grid,
    Torch_Is_Available,
    TorchEngine,
)

ENGINE_CASES = [
    pytest.param(NumpyEngine(), id="numpy_reference"),
    pytest.param(
        TorchEngine(),
        id="torch",
        marks=pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet"),
    ),
]


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_The_Real_Transform_Round_Trips_On_Every_Engine(engine: Engine) -> None:
    """the half spectrum carries a real field back unchanged, on an odd last axis and on an even one"""
    generator = np.random.default_rng(31)
    for grid in ((4, 5, 6), (3, 4, 7)):
        field = generator.random((2, *grid))
        spectrum = Real_Fourier_Transform_3d(engine.Lift_Constant(field), engine.working_precision)
        assert tuple(spectrum.shape) == (2, grid[0], grid[1], Half_Spectrum_Extent(grid[2]))
        returned = np.asarray(Inverse_Real_Fourier_Transform_3d(spectrum, grid, engine.working_precision))
        assert np.allclose(returned, field, atol=1e-12)


def Test_The_Real_Transform_Holds_Only_What_A_Real_Field_Needs() -> None:
    """the half spectrum agrees entry for entry with the whole one, and costs five eighths of it here"""
    generator = np.random.default_rng(32)
    field = generator.random((3, 6, 6, 8))
    half = np.asarray(Real_Fourier_Transform_3d(field))
    whole = np.asarray(Fourier_Transform_3d(field))
    assert half.shape == (3, 6, 6, 5) and whole.shape == (3, 6, 6, 8)
    assert np.allclose(half, whole[..., :5], atol=1e-12)
    # a little over half, because the zero mode and the Nyquist mode are each their own conjugate
    assert half.nbytes / whole.nbytes == 5 / 8


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_The_Transform_Never_Widens_What_An_Engine_Narrowed(engine: Engine) -> None:
    """a declared width governs, except that an array which arrived narrow is never promoted back"""
    generator = np.random.default_rng(33)
    wide = engine.Lift_Constant(generator.random((1, 4, 4, 4)))
    assert Real_Fourier_Transform_3d(wide, "double").dtype == Real_Fourier_Transform_3d(wide).dtype
    narrowed = Real_Fourier_Transform_3d(wide, "single")
    assert "complex64" in str(narrowed.dtype)
    assert "complex128" in str(Real_Fourier_Transform_3d(wide, "double").dtype)
    # the hazard this rule exists for: a narrowed engine's array meeting a double declaration, promoted back
    assert "complex64" in str(Real_Fourier_Transform_3d(narrowed.real, "double").dtype)


def Test_The_Transform_Names_Its_Grid_Axes_Apart_From_Its_Channels() -> None:
    """three loose axes are not a field, and any number of leading axes is carried through untouched"""
    generator = np.random.default_rng(34)
    with pytest.raises(ValueError):
        Real_Fourier_Transform_3d(generator.random((4, 4, 4)))
    batched = generator.random((3, 2, 4, 4, 4))
    leading, grid = Split_Batch_From_Grid(batched)
    assert leading == (3, 2) and grid == (4, 4, 4)
    assert np.asarray(Real_Fourier_Transform_3d(batched)).shape == (3, 2, 4, 4, 3)

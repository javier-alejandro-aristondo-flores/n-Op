"""the structural array contract every engine's arrays satisfy, and the precision they carry it in"""

from typing import Any, Literal, Protocol, runtime_checkable

import numpy as np


type Precision = Literal["single", "double"]

NUMPY_DTYPE_BY_PRECISION: dict[Precision, np.dtype[Any]] = {
    "single": np.dtype(np.float32),
    "double": np.dtype(np.float64),
}


@runtime_checkable
class ArrayLike(Protocol):
    """anything with a shape and a numpy view, which both engines' arrays have"""

    @property
    def shape(self) -> tuple[int, ...]: ...


    def __array__(self) -> np.ndarray[tuple[int, ...], np.dtype[Any]]: ...

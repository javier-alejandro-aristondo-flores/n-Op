"""The structural array contract every engine's arrays satisfy."""

from typing import Any, Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class ArrayLike(Protocol):
    """Anything with a shape and a numpy view; both engines' arrays qualify."""

    @property
    def shape(self) -> tuple[int, ...]: ...


    def __array__(self) -> np.ndarray[tuple[int, ...], np.dtype[Any]]: ...

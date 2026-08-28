"""in-house facets over interchangeable array and gradient engines"""

from operators.substrate.arrays import ArrayLike
from operators.substrate.engine import Engine, NumpyEngine, ParameterSet
from operators.substrate.fourier import (
    Cartesian_Wavevectors,
    Centered_Modes,
    Inverse_Fourier_Transform_3d,
    Fourier_Transform_3d,
    Reciprocal_Rows,
)
from operators.substrate.linear_algebra import Least_Squares_Solution, Solve_Linear_System
from operators.substrate.operations import (
    Concatenate_Channels,
    Exponential,
    Gaussian_Error_Linear_Unit,
    Mean_Over_Last_Axis,
    Softplus,
    Sum_Over_Last_Axis,
)
from operators.substrate.optimize import AdamState, Adam_Step, Fresh_Adam_State
from operators.substrate.torch_engine import Torch_Is_Available, TorchEngine

__all__ = [
    "ArrayLike",
    "Engine",
    "NumpyEngine",
    "ParameterSet",
    "Cartesian_Wavevectors",
    "Centered_Modes",
    "Fourier_Transform_3d",
    "Inverse_Fourier_Transform_3d",
    "Reciprocal_Rows",
    "Least_Squares_Solution",
    "Solve_Linear_System",
    "Concatenate_Channels",
    "Exponential",
    "Gaussian_Error_Linear_Unit",
    "Mean_Over_Last_Axis",
    "Softplus",
    "Sum_Over_Last_Axis",
    "AdamState",
    "Adam_Step",
    "Fresh_Adam_State",
    "Torch_Is_Available",
    "TorchEngine",
]

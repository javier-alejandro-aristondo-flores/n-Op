"""in-house facets over interchangeable array and gradient engines"""

# pyright: reportUnusedImport=false

from operators.substrate.arrays import ArrayLike
from operators.substrate.engine import Engine, NumpyEngine, ParameterSet
from operators.substrate.fourier import (
    Cartesian_Wavevectors,
    Centered_Modes,
    Inverse_Fourier_Transform_3d,
    Fourier_Transform_3d,
    Real_Part,
    Reciprocal_Rows,
)
from operators.substrate.linear_algebra import Least_Squares_Solution, Solve_Linear_System
from operators.substrate.network import MultilayerPerceptron
from operators.substrate.operations import (
    Concatenate_Channels,
    Exponential,
    Gaussian_Error_Linear_Unit,
    Hyperbolic_Tangent,
    Mean_Over_Last_Axis,
    Softplus,
    Sum_Over_Last_Axis,
)
from operators.substrate.optimize import AdamState, Adam_Step, Fresh_Adam_State
from operators.substrate.torch_engine import Torch_Is_Available, TorchEngine

"""in-house facets over interchangeable array and gradient engines"""

# pyright: reportUnusedImport=false

from operators.substrate.arrays import NUMPY_DTYPE_BY_PRECISION, ArrayLike, Precision
from operators.substrate.custom_gradient import CustomGradient, Vector_Jacobian_Product
from operators.substrate.devices import (
    ACCELERATOR_DEVICE_NAME,
    Accelerator_Is_Available,
    Device_Name_Of,
    HOST_DEVICE_NAME,
    Preferred_Device_Name,
)
from operators.substrate.engine import Engine, NumpyEngine, ParameterSet
from operators.substrate.fourier import (
    COMPLEX_DTYPE_BY_PRECISION,
    GRID_AXES,
    GRID_AXIS_COUNT,
    Cartesian_Wavevectors,
    Centered_Modes,
    Complex_From_Parts,
    Conjugate,
    Effective_Precision,
    Einstein_Summation,
    Half_Spectrum_Extent,
    Hermitian_Mode_Part,
    Inverse_Fourier_Transform_3d,
    Inverse_Real_Fourier_Transform_3d,
    Fourier_Transform_3d,
    Join_Along_Axis,
    Real_Fourier_Transform_3d,
    Real_Part,
    Reciprocal_Rows,
    Reverse_Axes,
    Sliced_Along_Axis,
    Split_Batch_From_Grid,
    Zeros_Beside,
)
from operators.substrate.linear_algebra import (
    Largest_Singular_Values_Of_Stack,
    Least_Squares_Solution,
    Singular_Values_Clipped,
    Solve_Linear_System,
)
from operators.substrate.network import MultilayerPerceptron
from operators.substrate.operations import (
    Clipped_Above,
    Concatenate_Channels,
    Contract_Channel_Axis,
    Detached,
    Peak_Accelerator_Bytes,
    Recomputed_In_Backward,
    Reset_Peak_Accelerator_Bytes,
    Exponential,
    Gaussian_Error_Linear_Unit,
    Gaussian_Error_Linear_Unit_Derivative,
    Host_Array,
    Hyperbolic_Tangent,
    Largest_Singular_Values,
    Maximum_Over_Last_Axis,
    Mean_Over_Last_Axis,
    Periodic_Convolution_3d,
    Roll_Along_Axes,
    Scatter_Add,
    Softplus,
    Sum_Over_Last_Axis,
)
from operators.substrate.optimize import AdamState, Adam_Step, Fresh_Adam_State
from operators.substrate.torch_engine import Torch_Is_Available, TorchEngine

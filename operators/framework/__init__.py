"""the integral transform's contracts and the objects they are written in"""

# pyright: reportUnusedImport=false

from operators.framework.composition import Composition
from operators.framework.domain import Array, Discretization, Domain, GridSpec, PointSpec
from operators.framework.inspectable import Inspectable
from operators.framework.integral import (
    Dense_Reference_Integral,
    Fractional_Grid_Coordinates,
    Output_Points,
    Quadrature_Weights,
    Source_Points_And_Values,
)
from operators.framework.invariance import (
    Apply_Grid_Operation,
    Block_Gap_Null,
    Diamond_Grid_Operations,
    Discretization_Invariance_Report,
    Equivariance_Errors,
    K_Quality_Tier,
    Spectral_Truncation_Resample,
)
from operators.framework.kernel import Kernel
from operators.framework.layer import Layer
from operators.framework.operator import NeuralOperator, Operator
from operators.framework.representation import (
    Coefficients,
    CountingQuadrature,
    GridFunction,
    PointSet,
    Quadrature,
    Representation,
    UniformGridQuadrature,
)

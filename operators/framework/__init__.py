"""The shared anatomy: four abstract classes and the concrete objects they speak in.

    Operator        input Representation -> output Representation, on a requested
                    Discretization, with an optional conditioning vector
    Representation  a typed function object carrying its Quadrature (the measure, as data)
    Kernel          the learned kernel plus its fused integration
    Composition     how layers chain; each implementation owns topology and backward strategy

Concrete: Domain, Discretization, Quadrature, Layer, and the NeuralOperator template.
``integral.py`` holds the dense reference integral — the correctness oracle every fused
kernel implementation must match on small problems before any full-size run.
"""

from operators.framework.domain import Array, Domain, GridSpec, PointSpec
from operators.framework.representation import (
    Coefficients,
    CountingQuadrature,
    GridFunction,
    PointSet,
    Quadrature,
    Representation,
    UniformGridQuadrature,
)
from operators.framework.operator import NeuralOperator, Operator
from operators.framework.kernel import Kernel
from operators.framework.composition import Composition
from operators.framework.layer import Layer

__all__ = [
    "Array", "Domain", "GridSpec", "PointSpec",
    "Representation", "Quadrature", "UniformGridQuadrature", "CountingQuadrature",
    "GridFunction", "PointSet", "Coefficients",
    "Operator", "NeuralOperator", "Kernel", "Composition", "Layer",
]

"""strain or lattice parameters to charge density, decoded point by point"""

from operators.framework import Coefficients, GridFunction, NeuralOperator, PointSet


class NonlinearManifoldDecoder(NeuralOperator[Coefficients, Coefficients, GridFunction | PointSet]):
    """sensor encoder, dense layers, nonlinear decoder"""


    def __init__(self) -> None:
        raise NotImplementedError

"""strain or lattice parameters to charge density, by branch and trunk"""

from operators.framework import Coefficients, GridFunction, NeuralOperator, PointSet


class DeepOperatorNetwork(NeuralOperator[Coefficients | GridFunction, Coefficients, GridFunction | PointSet]):
    """sensor encoder, dense layers, basis-expansion readout"""


    def __init__(self) -> None:
        raise NotImplementedError

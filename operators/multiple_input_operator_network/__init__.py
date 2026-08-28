"""charge density and local potential to electron localization"""

from operators.framework import Coefficients, GridFunction, NeuralOperator, PointSet


class MultipleInputOperatorNetwork(NeuralOperator[GridFunction, Coefficients, GridFunction | PointSet]):
    """two sensor encoders, a low-rank product, a shared trunk"""


    def __init__(self) -> None:
        raise NotImplementedError

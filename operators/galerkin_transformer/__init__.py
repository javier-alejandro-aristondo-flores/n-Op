"""charge density to electron localization, by softmax-free attention over grid points"""

from operators.framework import GridFunction, NeuralOperator


class GalerkinTransformer(NeuralOperator[GridFunction, GridFunction, GridFunction]):
    """coordinate-featured grid tokens, linear attention layers, a cross-attention decoder over query points"""


    def __init__(self) -> None:
        raise NotImplementedError

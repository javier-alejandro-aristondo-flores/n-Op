"""charge density to electron localization, by factorized Fourier convolution"""

from operators.framework import GridFunction, NeuralOperator


class FactorizedFourier(NeuralOperator[GridFunction, GridFunction, GridFunction]):
    """pointwise lift, factorized spectral layers, bounded head"""


    def __init__(self) -> None:
        raise NotImplementedError

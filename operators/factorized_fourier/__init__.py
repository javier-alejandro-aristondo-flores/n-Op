"""Charge density to electron localization field, by factorized Fourier convolution."""

from operators.framework import GridFunction, NeuralOperator


class FactorizedFourier(NeuralOperator[GridFunction, GridFunction, GridFunction]):
    """Assembles a pointwise lift, factorized spectral layers, and a bounded head."""


    def __init__(self) -> None:
        raise NotImplementedError

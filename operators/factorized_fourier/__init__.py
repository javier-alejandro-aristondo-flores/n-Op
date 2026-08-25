"""Charge density to electron localization field, by factorized Fourier convolution."""

from operators.framework import NeuralOperator


class FactorizedFourier(NeuralOperator):
    """Assembles a pointwise lift, factorized spectral layers, and a bounded head."""


    def __init__(self) -> None:
        raise NotImplementedError

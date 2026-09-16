"""strain or lattice parameters to charge density, decoded point by point"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.compositions import WithoutIntegralLayers
from operators.encoders import SensorEncoder
from operators.framework import Coefficients, Discretization, GridFunction, NeuralOperator, PointSet
from operators.readouts import NonlinearDecoder, PeriodicCoordinateFeatures
from operators.substrate import Concatenate_Channels


class NonlinearManifoldDecoder(NeuralOperator[Coefficients, Coefficients, GridFunction | PointSet]):
    """a branch latent read against a nonlinear decoder at any requested point, no integral between them"""


    def __init__(self, branch: SensorEncoder, decoder: NonlinearDecoder) -> None:
        super().__init__(branch, WithoutIntegralLayers(), decoder)
        self.branch = branch
        self.decoder = decoder


    def __call__(
        self,
        input_function: Coefficients,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction | PointSet:
        latent = self.encoder(input_function, output_discretization, condition)
        carried = self.composition.Apply(latent, condition)
        return self.readout(carried, output_discretization, condition)


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every learned array of the assembly under one namespace, ready for the trainer"""
        collected = dict(self.branch.parameter_values)
        collected.update(self.decoder.parameter_values)
        return collected


    def Forward_Coefficients(self, lifted: dict[str, Any], branch_input: Any) -> Any:
        """the branch's latent coefficients, differentiable through whichever engine lifted them"""
        return self.branch.network.Forward(lifted, branch_input)


    def Forward_Point_Values(self, lifted: dict[str, Any], branch_input: Any, trunk_features: Any) -> Any:
        """each run's own points read against that run's own latent, broadcast onto every one of its points"""
        coefficients = self.Forward_Coefficients(lifted, branch_input)
        # a zeroed feature column plus the latent row broadcasts one run's latent onto every one of its points
        broadcast_latent = trunk_features[:, :, :1] * 0.0 + coefficients[:, None, :]
        combined = Concatenate_Channels(
            [trunk_features.swapaxes(0, 2), broadcast_latent.swapaxes(0, 2)]
        ).swapaxes(0, 2)
        return self.decoder.network.Forward(lifted, combined)[:, :, 0]


def Manifold_Network(
    parameter_width: int,
    branch_hidden_widths: tuple[int, ...],
    latent_width: int,
    decoder_hidden_widths: tuple[int, ...],
    fourier_orders: int = 4,
    seed: int = 0,
) -> NonlinearManifoldDecoder:
    """the member's one configuration: a branch latent read by a nonlinear decoder at any point"""
    branch = SensorEncoder((parameter_width, *branch_hidden_widths, latent_width), seed=seed)
    coordinate_features = PeriodicCoordinateFeatures(fourier_orders)
    # the decoder is seeded one past the branch, so the two draws never share a stream
    decoder = NonlinearDecoder(latent_width, decoder_hidden_widths, coordinate_features, seed=seed + 1)
    return NonlinearManifoldDecoder(branch, decoder)

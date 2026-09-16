"""the displacement parametrization, a radial profile inside a cutoff over a periodic radius graph"""

from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.framework import (
    Array,
    Coefficients,
    CountingQuadrature,
    Discretization,
    Domain,
    GridFunction,
    GridSpec,
    Kernel,
    Output_Points,
    PointSet,
    Quadrature_Weights,
    Representation,
    Source_Points_And_Values,
    UniformGridQuadrature,
)
from operators.kernels.compact_support.geometry import (
    Folded_Fractional_Gaps,
    Grid_Offsets,
    Image_Reach,
    Lattice_Images,
    Offset_Reach,
    Periodic_Radius_Graph,
    Vector_Lengths,
)
from operators.kernels.compact_support.tabulated import Stencil_From_Weights, TabulatedStencilKernel
from operators.substrate import Einstein_Summation, Scatter_Add

PROFILE_SAMPLE_COUNT = 64

REFERENCE_IMAGE_MARGIN = 1


def Radial_Profile_Features(
    distances: NDArray[np.float64], cutoff_radius: float, basis_count: int
) -> NDArray[np.float64]:
    """the sine radial basis under a cosine cutoff, one column per basis order"""
    orders = np.arange(1, basis_count + 1, dtype=np.float64)
    lengths = np.asarray(distances, dtype=np.float64)
    # the sine over the radius is that multiple of the normalized sinc, which stays finite at zero
    basis = (np.pi * orders / cutoff_radius)[None, :] * np.sinc(
        lengths[:, None] * orders[None, :] / cutoff_radius
    )
    envelope = 0.5 * (np.cos(np.pi * lengths / cutoff_radius) + 1.0)
    return np.asarray(basis * envelope[:, None], dtype=np.float64)


def Sending_Points(input_function: Representation) -> NDArray[np.bool_] | None:
    """which points send messages, a zero role marking a probe that only receives"""
    if isinstance(input_function, PointSet) and input_function.roles is not None:
        return np.asarray(np.asarray(input_function.roles) != 0, dtype=np.bool_)
    return None


class ContinuousDisplacementKernel(Kernel[Representation, Representation]):
    """a learned radial profile vanishing at a cutoff, integrated against whatever measure carries the sources"""

    supported_representations = (GridFunction, PointSet)


    def __init__(
        self,
        cutoff_radius: float,
        basis_count: int,
        output_channels: int,
        input_channels: int,
        seed: int = 0,
    ) -> None:
        self.cutoff_radius = cutoff_radius
        self.basis_count = basis_count
        self.output_channels = output_channels
        self.input_channels = input_channels
        generator = np.random.default_rng(seed)
        scale = 1.0 / (input_channels * np.sqrt(float(basis_count)))
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "radial_weights": generator.normal(
                0.0, scale, size=(basis_count, output_channels, input_channels)
            )
        }
        self.last_output_values: NDArray[np.float64] | None = None
        self.last_edge_distances: NDArray[np.float64] | None = None


    def Profile_Matrices(self, lifted: dict[str, Any], distances: NDArray[np.float64]) -> Any:
        """the channel-mixing block this profile carries at each separation"""
        features = Radial_Profile_Features(distances, self.cutoff_radius, self.basis_count)
        return Einstein_Summation("eb,boc->eoc", features, lifted["radial_weights"])


    def Forward(
        self,
        lifted: dict[str, Any],
        profile_features: Any,
        sent_values: Any,
        receiving_points: NDArray[np.int64],
        receiving_count: int,
    ) -> Any:
        # a message is held in basis space so the learned weights are contracted once, after the sum
        per_edge = profile_features[:, :, None] * sent_values[:, None, :]
        accumulated = Scatter_Add(receiving_count, receiving_points, per_edge)
        return Einstein_Summation("tbc,boc->to", accumulated, lifted["radial_weights"])


    def Integrate(
        self,
        input_function: Representation,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Representation:
        lattice = np.asarray(input_function.domain.lattice, dtype=np.float64)
        source_points, source_values = Source_Points_And_Values(input_function)
        quadrature_weights = Quadrature_Weights(input_function)
        target_points = Output_Points(output_discretization)
        graph = Periodic_Radius_Graph(target_points, source_points, lattice, self.cutoff_radius)
        receiving_points = graph.receiving_points
        sending_points = graph.sending_points
        distances = graph.distances
        sending = Sending_Points(input_function)
        if sending is not None:
            # an edge survives only when the point it leaves is one that sends
            kept = sending[sending_points]
            receiving_points = receiving_points[kept]
            sending_points = sending_points[kept]
            distances = distances[kept]
        features = Radial_Profile_Features(distances, self.cutoff_radius, self.basis_count)
        weighted = np.asarray(source_values, dtype=np.float64) * quadrature_weights[:, None]
        produced = np.asarray(
            self.Forward(
                self.parameter_values,
                features,
                weighted[sending_points],
                receiving_points,
                int(target_points.shape[0]),
            ),
            dtype=np.float64,
        )
        self.last_edge_distances = distances
        output_labels = tuple(f"channel_{output_channel}" for output_channel in range(self.output_channels))
        if isinstance(output_discretization, GridSpec):
            shaped = produced.T.reshape(self.output_channels, *output_discretization.shape)
            self.last_output_values = shaped
            return GridFunction(
                values=shaped,
                channel_labels=output_labels,
                domain=input_function.domain,
                quadrature=UniformGridQuadrature(
                    float(abs(np.linalg.det(lattice))), int(np.prod(output_discretization.shape))
                ),
            )
        self.last_output_values = produced
        return PointSet(
            positions=target_points,
            domain=input_function.domain,
            values=produced,
            quadrature=CountingQuadrature(),
        )


    def Dense_Kernel_Function(
        self, lattice: NDArray[np.float64], sending_sources: NDArray[np.bool_] | None = None
    ) -> Callable[[NDArray[np.float64], NDArray[np.float64]], NDArray[np.float64]]:
        """the closed-form pair kernel this radius graph integrates"""
        reach = Image_Reach(lattice, self.cutoff_radius)
        # the reference looks a margin further out than the fused path does, so too short a reach shows here
        images = Lattice_Images(
            (
                reach[0] + REFERENCE_IMAGE_MARGIN,
                reach[1] + REFERENCE_IMAGE_MARGIN,
                reach[2] + REFERENCE_IMAGE_MARGIN,
            )
        )

        def Pair_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
            folded = Folded_Fractional_Gaps(targets, sources)
            values = np.zeros(
                (targets.shape[0], sources.shape[0], self.output_channels, self.input_channels)
            )
            for image in images:
                length = Vector_Lengths((folded + image) @ lattice)
                inside = length <= self.cutoff_radius
                # every image of a pair adds its own contribution to that one pair's kernel value
                values[inside] += self.Profile_Matrices(self.parameter_values, length[inside])
            if sending_sources is not None:
                values[:, ~sending_sources] = 0.0
            return values

        return Pair_Kernel


    def Tabulate_On_Grid(
        self, domain: Domain, grid: GridSpec, quadrature: UniformGridQuadrature
    ) -> TabulatedStencilKernel:
        """the same profile written out as stencil weights at one grid's whole-voxel offsets"""
        lattice = np.asarray(domain.lattice, dtype=np.float64)
        half_widths = Offset_Reach(lattice, grid.shape, self.cutoff_radius)
        for extent, half_width in zip(grid.shape, half_widths):
            if 2 * half_width + 1 > extent:
                raise ValueError("the cutoff reaches past half this grid, so its offsets would wrap onto each other")
        offsets = Grid_Offsets(half_widths)
        # a box that does not wrap holds the cutoff under half of every height, so only the home cell reaches
        fractional = offsets / np.asarray(grid.shape, dtype=np.float64)
        length = Vector_Lengths(fractional @ lattice)
        inside = length <= self.cutoff_radius
        table = np.zeros((offsets.shape[0], self.output_channels, self.input_channels))
        table[inside] = self.Profile_Matrices(self.parameter_values, length[inside])
        offset_extents = tuple(2 * half_width + 1 for half_width in half_widths)
        # the stencil sum carries no quadrature, so the weight the measure would have paid is folded in
        paid = table * (quadrature.cell_volume / quadrature.point_count)
        return Stencil_From_Weights(
            paid.reshape(*offset_extents, self.output_channels, self.input_channels)
        )


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        radii = np.linspace(0.0, self.cutoff_radius, PROFILE_SAMPLE_COUNT)
        state["profile_radii"] = radii
        state["basis_over_radius"] = Radial_Profile_Features(radii, self.cutoff_radius, self.basis_count)
        state["profile_over_radius"] = np.asarray(
            self.Profile_Matrices(self.parameter_values, radii), dtype=np.float64
        )
        if self.last_edge_distances is not None:
            state["last_edge_distances"] = self.last_edge_distances
        if self.last_output_values is not None:
            state["last_output_values"] = self.last_output_values
        return state

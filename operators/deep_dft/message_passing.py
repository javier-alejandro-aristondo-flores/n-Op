"""atom-atom then atom-probe message passing, over one point set carrying both"""

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.compositions import Sliced_Lifted
from operators.framework import Array, Coefficients, Composition, PointSet
from operators.kernels.compact_support import (
    ContinuousDisplacementKernel,
    Periodic_Radius_Graph,
    Radial_Profile_Features,
)
from operators.substrate import Concatenate_Channels, Gaussian_Error_Linear_Unit, MultilayerPerceptron, Zeros_Beside

ATOM_ROLE = 1

PROBE_ROLE = 0


@dataclass(slots=True)
class MessagePassingLayer:
    """one kernel integral beside its own local linear term"""

    kernel: ContinuousDisplacementKernel
    local_linear: MultilayerPerceptron


def New_Message_Passing_Layer(
    cutoff_radius: float, basis_count: int, hidden_channels: int, name_prefix: str, seed: int
) -> MessagePassingLayer:
    """a fresh kernel-plus-local-linear layer at the given hidden width"""
    kernel = ContinuousDisplacementKernel(cutoff_radius, basis_count, hidden_channels, hidden_channels, seed=seed)
    local_linear = MultilayerPerceptron((hidden_channels, hidden_channels), name_prefix, seed + 1)
    return MessagePassingLayer(kernel, local_linear)


def Layer_Parameter_Values(layer: MessagePassingLayer, prefix: str) -> dict[str, NDArray[np.float64]]:
    """one layer's kernel and local-linear arrays, prefixed so no two layers collide"""
    collected: dict[str, NDArray[np.float64]] = {}
    for name, value in layer.kernel.parameter_values.items():
        collected[f"{prefix}kernel.{name}"] = value
    for name, value in layer.local_linear.parameter_values.items():
        collected[f"{prefix}local_linear.{name}"] = value
    return collected


def Layer_Step(
    layer: MessagePassingLayer,
    lifted: dict[str, Any],
    prefix: str,
    profile_features: Any,
    values: Any,
    sending_points: NDArray[np.int64],
    receiving_points: NDArray[np.int64],
    receiving_count: int,
) -> Any:
    """one activated layer output, the kernel sum and the local linear term added under one activation"""
    kernel_lifted = Sliced_Lifted(lifted, f"{prefix}kernel.")
    local_lifted = Sliced_Lifted(lifted, f"{prefix}local_linear.")
    sent_values = values[sending_points]
    kernel_output = layer.kernel.Forward(
        kernel_lifted, profile_features, sent_values, receiving_points, receiving_count
    )
    local_output = layer.local_linear.Forward(local_lifted, values)
    return Gaussian_Error_Linear_Unit(kernel_output + local_output)


class MessagePassingStack(Composition[PointSet]):
    """three atom-atom layers, then three atom-probe layers over the joined point set"""


    def __init__(
        self,
        atom_atom_layers: tuple[MessagePassingLayer, ...],
        atom_probe_layers: tuple[MessagePassingLayer, ...],
        cutoff_radius: float,
        basis_count: int,
    ) -> None:
        self.atom_atom_layers = atom_atom_layers
        self.atom_probe_layers = atom_probe_layers
        self.cutoff_radius = cutoff_radius
        self.basis_count = basis_count
        self.last_atom_count: int | None = None
        self.last_probe_count: int | None = None
        self.last_atom_atom_edge_count: int | None = None
        self.last_atom_probe_edge_count: int | None = None
        self.last_atom_to_probe_adjacency: NDArray[np.float64] | None = None


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every layer's own arrays, prefixed by its phase and position so no two layers collide"""
        collected: dict[str, NDArray[np.float64]] = {}
        for layer_index, layer in enumerate(self.atom_atom_layers):
            collected.update(Layer_Parameter_Values(layer, f"atom_atom_layer_{layer_index}."))
        for layer_index, layer in enumerate(self.atom_probe_layers):
            collected.update(Layer_Parameter_Values(layer, f"atom_probe_layer_{layer_index}."))
        return collected


    def Forward(
        self,
        lifted: dict[str, Any],
        lattice: NDArray[np.float64],
        atom_positions: NDArray[np.float64],
        atom_values: Any,
        probe_positions: NDArray[np.float64],
    ) -> tuple[Any, Any]:
        """the final atom and probe features, differentiable through whichever engine lifted the dict"""
        atom_count = atom_positions.shape[0]
        atom_graph = Periodic_Radius_Graph(atom_positions, atom_positions, lattice, self.cutoff_radius)
        atom_features = Radial_Profile_Features(atom_graph.distances, self.cutoff_radius, self.basis_count)
        atom_only_values = atom_values
        for layer_index, layer in enumerate(self.atom_atom_layers):
            atom_only_values = Layer_Step(
                layer,
                lifted,
                f"atom_atom_layer_{layer_index}.",
                atom_features,
                atom_only_values,
                atom_graph.sending_points,
                atom_graph.receiving_points,
                atom_count,
            )

        probe_count = probe_positions.shape[0]
        combined_positions = np.concatenate([atom_positions, probe_positions], axis=0)
        combined_roles = np.concatenate(
            [np.full(atom_count, ATOM_ROLE, dtype=np.int64), np.full(probe_count, PROBE_ROLE, dtype=np.int64)]
        )
        combined_graph = Periodic_Radius_Graph(combined_positions, combined_positions, lattice, self.cutoff_radius)
        sending_mask = combined_roles != PROBE_ROLE
        kept_edges = sending_mask[combined_graph.sending_points]
        receiving_points = combined_graph.receiving_points[kept_edges]
        sending_points = combined_graph.sending_points[kept_edges]
        combined_features = Radial_Profile_Features(
            combined_graph.distances[kept_edges], self.cutoff_radius, self.basis_count
        )
        probe_initial_values = Zeros_Beside(atom_values, (probe_count, atom_only_values.shape[1]))
        combined_values = Concatenate_Channels([atom_only_values, probe_initial_values])
        for layer_index, layer in enumerate(self.atom_probe_layers):
            combined_values = Layer_Step(
                layer,
                lifted,
                f"atom_probe_layer_{layer_index}.",
                combined_features,
                combined_values,
                sending_points,
                receiving_points,
                atom_count + probe_count,
            )
        self.last_atom_count = atom_count
        self.last_probe_count = probe_count
        self.last_atom_atom_edge_count = int(atom_graph.distances.shape[0])
        self.last_atom_probe_edge_count = int(kept_edges.sum())
        return combined_values[:atom_count], combined_values[atom_count:]


    def Atom_To_Probe_Adjacency(
        self,
        lattice: NDArray[np.float64],
        atom_positions: NDArray[np.float64],
        probe_positions: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """the zero-one matrix of which probes sit inside the cutoff of which atoms, periodic images included"""
        atom_count = atom_positions.shape[0]
        combined_positions = np.concatenate([atom_positions, probe_positions], axis=0)
        graph = Periodic_Radius_Graph(combined_positions, combined_positions, lattice, self.cutoff_radius)
        atom_to_probe = (graph.sending_points < atom_count) & (graph.receiving_points >= atom_count)
        adjacency = np.zeros((atom_count, probe_positions.shape[0]), dtype=np.float64)
        adjacency[graph.sending_points[atom_to_probe], graph.receiving_points[atom_to_probe] - atom_count] = 1.0
        return adjacency


    def Apply(self, input_function: PointSet, condition: Coefficients | None = None) -> PointSet:
        if input_function.values is None or input_function.roles is None:
            raise ValueError("the message-passing stack needs point values and roles to run")
        positions = np.asarray(input_function.positions, dtype=np.float64)
        roles = np.asarray(input_function.roles, dtype=np.int64)
        values = np.asarray(input_function.values, dtype=np.float64)
        lattice = np.asarray(input_function.domain.lattice, dtype=np.float64)
        atom_mask = roles != PROBE_ROLE
        atom_positions = positions[atom_mask]
        probe_positions = positions[~atom_mask]
        atom_values, probe_values = self.Forward(
            self.Parameter_Values(), lattice, atom_positions, values[atom_mask], probe_positions
        )
        combined_values = np.zeros_like(values)
        combined_values[atom_mask] = np.asarray(atom_values, dtype=np.float64)
        combined_values[~atom_mask] = np.asarray(probe_values, dtype=np.float64)
        if atom_positions.shape[0] > 0 and probe_positions.shape[0] > 0:
            self.last_atom_to_probe_adjacency = self.Atom_To_Probe_Adjacency(lattice, atom_positions, probe_positions)
        return PointSet(
            positions=input_function.positions,
            domain=input_function.domain,
            values=combined_values,
            species=input_function.species,
            roles=input_function.roles,
            quadrature=input_function.quadrature,
        )


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {}
        for layer_index, layer in enumerate(self.atom_atom_layers):
            prefix = f"atom_atom_layer_{layer_index}."
            for name, value in layer.kernel.Inspect().items():
                state[f"{prefix}kernel.{name}"] = value
            for name, value in layer.local_linear.parameter_values.items():
                state[f"{prefix}local_linear.{name}"] = value
        for layer_index, layer in enumerate(self.atom_probe_layers):
            prefix = f"atom_probe_layer_{layer_index}."
            for name, value in layer.kernel.Inspect().items():
                state[f"{prefix}kernel.{name}"] = value
            for name, value in layer.local_linear.parameter_values.items():
                state[f"{prefix}local_linear.{name}"] = value
        if self.last_atom_count is not None:
            state["last_atom_count"] = np.asarray(self.last_atom_count)
        if self.last_probe_count is not None:
            state["last_probe_count"] = np.asarray(self.last_probe_count)
        if self.last_atom_atom_edge_count is not None:
            state["last_atom_atom_edge_count"] = np.asarray(self.last_atom_atom_edge_count)
        if self.last_atom_probe_edge_count is not None:
            state["last_atom_probe_edge_count"] = np.asarray(self.last_atom_probe_edge_count)
        if self.last_atom_to_probe_adjacency is not None:
            state["last_atom_to_probe_adjacency"] = self.last_atom_to_probe_adjacency
        return state

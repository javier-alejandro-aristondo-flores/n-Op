"""atomic structure to charge density and magnetization, queried anywhere"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.deep_dft.message_passing import (
    ATOM_ROLE,
    MessagePassingStack,
    New_Message_Passing_Layer,
    PROBE_ROLE,
)
from operators.deep_dft.readout import OUTPUT_CHANNEL_LABELS, ProbeHead
from operators.encoders import AtomEmbedding
from operators.framework import (
    Array,
    Coefficients,
    Discretization,
    GridFunction,
    GridSpec,
    NeuralOperator,
    Output_Points,
    PointSet,
    PointSpec,
    UniformGridQuadrature,
)

HIDDEN_CHANNELS = 64

CUTOFF_RADIUS = 4.0

BASIS_COUNT = 20

ATOM_ATOM_LAYER_COUNT = 3

ATOM_PROBE_LAYER_COUNT = 3

UNKNOWN_RELABEL_PROBABILITY = 0.1


def Renormalized_To_Electron_Count(
    values: NDArray[np.float64], weight_each: float, electron_count: float
) -> NDArray[np.float64]:
    """the density channel scaled onto the electron count, the magnetization channel left untouched"""
    # the shared Conserving wrapper flattens every channel together, which is wrong once magnetization
    # rides beside density -- scaling a moment by a density-derived factor has no physical meaning
    density_integral = float(values[0].sum()) * weight_each
    scale = electron_count / density_integral
    renormalized = values.copy()
    renormalized[0] = values[0] * scale
    return renormalized


class DeepDft(NeuralOperator[PointSet, PointSet, GridFunction | PointSet]):
    """atom embedding and message passing over atoms and probes"""


    def __init__(self, encoder: AtomEmbedding, composition: MessagePassingStack, readout: ProbeHead) -> None:
        super().__init__(encoder, composition, readout)
        self.atom_embedding = encoder
        self.message_passing = composition
        self.probe_head = readout
        self.last_predicted_grid: NDArray[np.float64] | None = None
        self.last_renormalized_grid: NDArray[np.float64] | None = None


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every part's own arrays under one namespace, ready for the trainer"""
        collected = dict(self.atom_embedding.parameter_values)
        collected.update(self.message_passing.Parameter_Values())
        collected.update(self.probe_head.parameter_values)
        return collected


    def Forward(
        self,
        lifted: dict[str, Any],
        lattice: NDArray[np.float64],
        atom_positions: NDArray[np.float64],
        atom_vocabulary_indices: NDArray[np.intp],
        probe_positions: NDArray[np.float64],
    ) -> Any:
        """embed, pass messages atom-atom then atom-probe, and read the probe head, one lifted dict throughout"""
        atom_values = self.atom_embedding.Forward(lifted, atom_vocabulary_indices)
        _, probe_values = self.message_passing.Forward(lifted, lattice, atom_positions, atom_values, probe_positions)
        return self.probe_head.Forward(lifted, probe_values)


    def __call__(
        self,
        input_function: PointSet,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction | PointSet:
        if input_function.species is None:
            raise ValueError("deep_dft reads an atomic structure, which needs a species column")
        atom_positions = np.asarray(input_function.positions, dtype=np.float64)
        probe_points = Output_Points(output_discretization)
        atom_point_set = PointSet(
            positions=atom_positions, domain=input_function.domain, species=input_function.species
        )
        embedded_atoms = self.atom_embedding(atom_point_set, PointSpec(atom_positions))
        atom_count = atom_positions.shape[0]
        probe_count = probe_points.shape[0]
        combined_positions = np.concatenate([atom_positions, probe_points], axis=0)
        combined_roles = np.concatenate(
            [np.full(atom_count, ATOM_ROLE, dtype=np.int64), np.full(probe_count, PROBE_ROLE, dtype=np.int64)]
        )
        atom_values = np.asarray(embedded_atoms.values, dtype=np.float64)
        combined_values = np.concatenate([atom_values, np.zeros((probe_count, atom_values.shape[1]))], axis=0)
        joint_point_set = PointSet(
            positions=combined_positions,
            domain=input_function.domain,
            values=combined_values,
            roles=combined_roles,
        )
        updated = self.message_passing.Apply(joint_point_set)
        probe_values = np.asarray(updated.values, dtype=np.float64)[atom_count:]
        predicted = self.probe_head(
            PointSet(positions=probe_points, domain=input_function.domain, values=probe_values),
            output_discretization,
        )
        predicted_values = np.asarray(predicted.values, dtype=np.float64)
        if isinstance(output_discretization, GridSpec):
            shape = output_discretization.shape
            produced = predicted_values.T.reshape(len(OUTPUT_CHANNEL_LABELS), *shape)
            self.last_predicted_grid = produced
            lattice = np.asarray(input_function.domain.lattice, dtype=np.float64)
            cell_volume = float(abs(np.linalg.det(lattice)))
            quadrature = UniformGridQuadrature(cell_volume, shape[0] * shape[1] * shape[2])
            if condition is not None:
                electron_count = float(np.asarray(condition.vector, dtype=np.float64)[0])
                weight_each = cell_volume / (shape[0] * shape[1] * shape[2])
                produced = Renormalized_To_Electron_Count(produced, weight_each, electron_count)
                self.last_renormalized_grid = produced
            grid_function = GridFunction(produced, OUTPUT_CHANNEL_LABELS, input_function.domain, quadrature)
            return grid_function
        return PointSet(positions=probe_points, domain=input_function.domain, values=predicted_values)


    def Inspect(self) -> dict[str, Array]:
        """every part's own arrays, plus the member's last predicted and renormalized grids"""
        state = super().Inspect()
        if self.last_predicted_grid is not None:
            state["last_predicted_grid"] = self.last_predicted_grid
        if self.last_renormalized_grid is not None:
            state["last_renormalized_grid"] = self.last_renormalized_grid
        return state


def Deep_Dft_Network(
    training_vocabulary: tuple[tuple[str, str], ...],
    seed: int = 0,
    hidden_channels: int = HIDDEN_CHANNELS,
    cutoff_radius: float = CUTOFF_RADIUS,
    basis_count: int = BASIS_COUNT,
    atom_atom_layer_count: int = ATOM_ATOM_LAYER_COUNT,
    atom_probe_layer_count: int = ATOM_PROBE_LAYER_COUNT,
) -> DeepDft:
    """the minimal configuration: atom embedding, six message-passing layers, a per-probe head"""
    encoder = AtomEmbedding(training_vocabulary, hidden_channels, seed=seed)
    atom_atom_layers = tuple(
        New_Message_Passing_Layer(
            cutoff_radius,
            basis_count,
            hidden_channels,
            f"atom_atom_layer_{layer_index}_local_linear",
            seed + 10 * layer_index + 1,
        )
        for layer_index in range(atom_atom_layer_count)
    )
    atom_probe_layers = tuple(
        New_Message_Passing_Layer(
            cutoff_radius,
            basis_count,
            hidden_channels,
            f"atom_probe_layer_{layer_index}_local_linear",
            seed + 10 * (layer_index + atom_atom_layer_count) + 1,
        )
        for layer_index in range(atom_probe_layer_count)
    )
    composition = MessagePassingStack(atom_atom_layers, atom_probe_layers, cutoff_radius, basis_count)
    readout = ProbeHead(hidden_channels, seed=seed + 1000)
    return DeepDft(encoder, composition, readout)

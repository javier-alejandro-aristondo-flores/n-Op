"""the deep_dft member: structure loading, message passing, the probe sampler and its floors"""

import json
from pathlib import Path

import numpy as np
import pytest

from operators.data import ARTIFACT_DIRECTORY
from operators.deep_dft import Deep_Dft_Network
from operators.deep_dft.floors import (
    Deep_Dft_Superposed_Atomic_Density_Errors,
    Moment_Gate_Row,
    Total_Moment,
)
from operators.deep_dft.sampling import ATOM_CENTERED_SIGMA, Drawn_Probe_Points, Trilinear_Interpolate
from operators.deep_dft.species import (
    Loaded_Structure,
    Relabeled_Species_Keys,
    Species_Keys_Of,
    SpeciesKeys,
    Structure,
    UNKNOWN_SPECIES_KEY,
)
from operators.framework import (
    Coefficients,
    Discretization,
    Domain,
    GridSpec,
    Inspectable,
    Operator,
    PointSet,
    PointSpec,
)
from operators.inspection import Render_Inspection_Suite
from operators.kernels.compact_support import Periodic_Radius_Graph
from operators.substrate import NumpyEngine, ParameterSet, Torch_Is_Available, TorchEngine

CARBON_KEY = ("C", "PAW_PBE C 08Apr2002")

NITROGEN_KEY = ("N", "PAW_PBE N 08Apr2002")

TINY_VOCABULARY = (CARBON_KEY, NITROGEN_KEY, UNKNOWN_SPECIES_KEY)


def Small_Structure(atom_count: int, lattice_length: float, seed: int) -> PointSet:
    """a random small carbon structure inside a cubic cell, for cheap end-to-end checks"""
    generator = np.random.default_rng(seed)
    positions = generator.random((atom_count, 3))
    domain = Domain(lattice=np.eye(3) * lattice_length)
    species = np.asarray([list(CARBON_KEY) for _ in range(atom_count)])
    return PointSet(positions=positions, domain=domain, species=species)


def Test_The_Gate_Contract() -> None:
    """a fresh member instantiates, satisfies operator and inspectable, and predicts at any point"""
    member = Deep_Dft_Network(TINY_VOCABULARY, seed=1, hidden_channels=4, basis_count=3, cutoff_radius=5.0)
    assert Operator in type(member).__mro__
    assert Inspectable in type(member).__mro__
    structure = Small_Structure(3, 5.0, seed=0)
    query_points = np.random.default_rng(2).random((4, 3))
    predicted = member(structure, PointSpec(query_points))
    assert isinstance(predicted, PointSet)
    assert np.asarray(predicted.values).shape == (4, 2)


@pytest.mark.pool
def Test_The_Structure_Loader_Keys_Every_Atom_On_Every_Defect_Sidecar() -> None:
    """every atom in every defect run gets a resolvable (element, title) key, unknowns routed rather than raised"""
    payload = json.loads((ARTIFACT_DIRECTORY / "paired_fields_fivefold.json").read_text())
    identifiers = [
        identifier
        for unit in payload.values()
        if unit["campaign"] == "defect_set"
        for identifier in unit["run_identifiers"]
    ]
    checked_run_count = 0
    for identifier in identifiers:
        structure = Loaded_Structure("defect_set", identifier)
        if structure is None:
            continue
        assert len(structure.species_keys) == len(structure.species_symbols) == structure.positions.shape[0]
        for key in structure.species_keys:
            assert len(key) == 2
        checked_run_count += 1
    assert checked_run_count > 100


def Test_Unresolvable_Titles_Route_To_The_Unknown_Row() -> None:
    """an element with no matching title among this run's own titles becomes the unknown key"""
    keys = Species_Keys_Of(("C", "H"), ("PAW_PBE C 08Apr2002",))
    assert keys == (CARBON_KEY, UNKNOWN_SPECIES_KEY)


def Test_Unseen_Pairs_Resolve_To_The_Unknown_Row() -> None:
    """a pair the training vocabulary never saw is sent to the unknown row instead of raising"""
    species_keys = SpeciesKeys((CARBON_KEY, UNKNOWN_SPECIES_KEY))
    resolved = species_keys.Resolved((CARBON_KEY, ("Fr", "PAW_PBE Fr_sv 29May2007")))
    assert resolved == (CARBON_KEY, UNKNOWN_SPECIES_KEY)


def Test_Held_Out_Chemistry_Flags_An_Unseen_Element() -> None:
    """a structure carrying an element the vocabulary never trained on is flagged as held-out chemistry"""
    species_keys = SpeciesKeys((CARBON_KEY, UNKNOWN_SPECIES_KEY))
    francium_structure = Structure(
        identifier="synthetic",
        campaign="defect_set",
        lattice=np.eye(3),
        positions=np.zeros((1, 3)),
        species_symbols=("Fr",),
        species_keys=(UNKNOWN_SPECIES_KEY,),
        electron_count=1.0,
    )
    assert species_keys.Held_Out_Chemistry(francium_structure)
    carbon_structure = Structure(
        identifier="synthetic_carbon",
        campaign="defect_set",
        lattice=np.eye(3),
        positions=np.zeros((1, 3)),
        species_symbols=("C",),
        species_keys=(CARBON_KEY,),
        electron_count=1.0,
    )
    assert not species_keys.Held_Out_Chemistry(carbon_structure)


def Test_Relabeled_Species_Keys_Sends_Roughly_The_Requested_Fraction_To_Unknown() -> None:
    """a large batch of keys relabels close to the requested probability to the unknown row"""
    keys = tuple(CARBON_KEY for _ in range(4000))
    generator = np.random.default_rng(13)
    relabeled = Relabeled_Species_Keys(keys, 0.1, generator)
    fraction = sum(1 for key in relabeled if key == UNKNOWN_SPECIES_KEY) / len(relabeled)
    assert 0.07 < fraction < 0.13


def Test_Probes_Never_Send() -> None:
    """every message-passing edge the atom-probe phase keeps originates at an atom, never at a probe"""
    generator = np.random.default_rng(3)
    atom_positions = generator.random((4, 3))
    probe_positions = generator.random((6, 3))
    lattice = np.eye(3) * 3.0
    combined = np.concatenate([atom_positions, probe_positions], axis=0)
    roles = np.concatenate([np.ones(4), np.zeros(6)])
    graph = Periodic_Radius_Graph(combined, combined, lattice, 6.0)
    sending_roles = roles[graph.sending_points]
    assert np.any(sending_roles == 0.0), "the unfiltered graph should contain some probe-sourced edges to filter away"
    kept = sending_roles != 0.0
    assert np.all(roles[graph.sending_points[kept]] == 1.0)


def Test_Probes_Never_Influence_Atom_Features() -> None:
    """moving or resizing the probe set leaves the final atom features unchanged"""
    member = Deep_Dft_Network(TINY_VOCABULARY, seed=4, hidden_channels=4, basis_count=3, cutoff_radius=4.0)
    generator = np.random.default_rng(5)
    lattice = np.eye(3) * 4.0
    atom_positions = generator.random((5, 3))
    atom_values = generator.normal(size=(5, 4))
    parameters = member.message_passing.Parameter_Values()
    probes_a = generator.random((7, 3))
    probes_b = generator.random((11, 3))
    final_atoms_a, _ = member.message_passing.Forward(parameters, lattice, atom_positions, atom_values, probes_a)
    final_atoms_b, _ = member.message_passing.Forward(parameters, lattice, atom_positions, atom_values, probes_b)
    assert np.allclose(np.asarray(final_atoms_a), np.asarray(final_atoms_b), atol=1e-12)


def Test_The_Probe_Sampler_Weights_Integrate_A_Known_Field_Without_Bias() -> None:
    """the self-normalized importance-weighted mean of a known field matches its true cell average"""
    generator = np.random.default_rng(6)
    lattice = np.eye(3) * 5.0
    atom_positions = generator.random((6, 3))
    points, weights = Drawn_Probe_Points(atom_positions, lattice, 30000, ATOM_CENTERED_SIGMA, generator)
    # a nonzero-frequency fourier mode integrates to exactly zero over a periodic cell
    oscillating_field = np.cos(2.0 * np.pi * points[:, 0])
    estimate = float(np.sum(weights * oscillating_field) / np.sum(weights))
    assert abs(estimate) < 0.02
    # a constant field's weighted mean must reproduce that same constant exactly
    constant_estimate = float(np.sum(weights * np.ones_like(oscillating_field)) / np.sum(weights))
    assert abs(constant_estimate - 1.0) < 1e-9


def Test_Trilinear_Interpolation_Matches_The_Grid_At_Grid_Points() -> None:
    """interpolating exactly at a grid point reproduces the value stored there"""
    generator = np.random.default_rng(7)
    grid = generator.random((6, 5, 4, 1))
    axes = [np.arange(extent, dtype=np.float64) / extent for extent in (6, 5, 4)]
    axis_grids = np.meshgrid(*axes, indexing="ij")
    grid_points = np.stack([axis_grid.reshape(-1) for axis_grid in axis_grids], axis=1)
    interpolated = Trilinear_Interpolate(grid, grid_points)
    assert np.allclose(interpolated[:, 0], grid.reshape(-1), atol=1e-12)


def Synthetic_Field(points: np.ndarray) -> np.ndarray:
    """a smooth periodic scalar field with three fourier components"""
    return np.sin(2.0 * np.pi * points[:, 0]) * np.cos(4.0 * np.pi * points[:, 1]) + 0.3 * np.sin(
        6.0 * np.pi * points[:, 2]
    )


def Test_Trilinear_Interpolation_Error_On_A_Synthetic_Field() -> None:
    """the interpolation error on a smooth periodic field, at the defect campaign's own grid resolution"""
    shape = (80, 80, 80)
    axes = [np.arange(extent, dtype=np.float64) / extent for extent in shape]
    axis_grids = np.meshgrid(*axes, indexing="ij")
    grid_points = np.stack([axis_grid.reshape(-1) for axis_grid in axis_grids], axis=1)
    grid_values = Synthetic_Field(grid_points).reshape(*shape, 1)
    generator = np.random.default_rng(8)
    query_points = generator.random((5000, 3))
    interpolated = Trilinear_Interpolate(grid_values, query_points)[:, 0]
    truth = Synthetic_Field(query_points)
    root_mean_square_error = float(np.sqrt(np.mean((interpolated - truth) ** 2)))
    # measured and recorded in the report: trilinear interpolation on an 80-cubed grid of a smooth field
    assert root_mean_square_error < 0.01


def Test_Two_Path_Agreement_And_A_Gradient_On_Every_Parameter() -> None:
    """the numpy call and the lifted forward agree, and every named parameter carries a nonzero gradient"""
    member = Deep_Dft_Network(TINY_VOCABULARY, seed=9, hidden_channels=3, basis_count=2, cutoff_radius=3.0)
    generator = np.random.default_rng(10)
    lattice = np.eye(3) * 3.0
    positions = generator.random((3, 3))
    species = np.asarray([list(CARBON_KEY), list(NITROGEN_KEY), list(CARBON_KEY)])
    domain = Domain(lattice=lattice)
    structure = PointSet(positions=positions, domain=domain, species=species)
    probe_points = generator.random((5, 3))

    from_call = np.asarray(member(structure, PointSpec(probe_points)).values)
    vocabulary_indices = member.atom_embedding.Vocabulary_Indices(species)
    parameters = member.Parameter_Values()
    from_forward = np.asarray(member.Forward(parameters, lattice, positions, vocabulary_indices, probe_points))
    assert np.allclose(from_call, from_forward, atol=1e-10)

    def Loss_Of(lifted: dict[str, object]) -> float:
        """the summed squared prediction, a scalar any engine can differentiate"""
        predicted = member.Forward(lifted, lattice, positions, vocabulary_indices, probe_points)
        return float(np.sum(np.asarray(predicted) ** 2))

    engine = NumpyEngine(step_size=1e-4)
    parameter_set = ParameterSet(values=parameters)
    value, gradients = engine.Value_And_Gradients(parameter_set, Loss_Of)
    assert np.isfinite(value)
    assert set(gradients) == set(parameters)
    for name, gradient in gradients.items():
        assert bool(np.all(np.isfinite(gradient))), name
        assert bool(np.any(gradient != 0.0)), name


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Foreign_Engine_Forward_And_Gradient_Agree_On_A_Tiny_Structure() -> None:
    """the whole member differentiates through the lifted kernel on the foreign engine, matching every other path"""
    member = Deep_Dft_Network(TINY_VOCABULARY, seed=9, hidden_channels=3, basis_count=2, cutoff_radius=3.0)
    generator = np.random.default_rng(11)
    lattice = np.eye(3) * 3.0
    positions = generator.random((3, 3))
    species = np.asarray([list(CARBON_KEY), list(NITROGEN_KEY), list(CARBON_KEY)])
    domain = Domain(lattice=lattice)
    structure = PointSet(positions=positions, domain=domain, species=species)
    probe_points = generator.random((5, 3))
    vocabulary_indices = member.atom_embedding.Vocabulary_Indices(species)
    parameters = member.Parameter_Values()

    from_call = np.asarray(member(structure, PointSpec(probe_points)).values)

    def Squared_Sum_Loss(lifted: dict[str, object]) -> object:
        """the summed squared prediction, written only with dunders so either engine can carry it"""
        predicted = member.Forward(lifted, lattice, positions, vocabulary_indices, probe_points)
        return (predicted * predicted).sum()

    parameter_set = ParameterSet(values=parameters)
    torch_engine = TorchEngine()
    torch_lifted = torch_engine.Lift(parameter_set.values, requires_gradient=False)
    foreign_forward = member.Forward(torch_lifted, lattice, positions, vocabulary_indices, probe_points)
    from_foreign_forward = np.asarray(foreign_forward)
    assert np.allclose(from_call, from_foreign_forward, atol=1e-8)

    reference_engine = NumpyEngine(step_size=1e-4)
    reference_value = reference_engine.Evaluate(parameter_set, Squared_Sum_Loss)
    reference_gradients = reference_engine.Gradients(parameter_set, Squared_Sum_Loss)
    torch_value, torch_gradients = torch_engine.Value_And_Gradients(parameter_set, Squared_Sum_Loss)
    assert abs(reference_value - torch_value) < 1e-8
    assert set(torch_gradients) == set(parameters)
    for name, gradient in torch_gradients.items():
        assert bool(np.all(np.isfinite(gradient))), name
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-4, atol=1e-5), name


def Test_The_Moment_Row_On_A_Synthetic_Magnetic_Field() -> None:
    """the gate-c moment row passes runs within tolerance and the right sign, and fails the rest"""
    cell_volume = 27.0
    true_totals = np.asarray([2.0, -1.0, 0.5, 3.0])
    predicted_totals = np.asarray([2.01, -1.5, -0.5, 3.02])
    row = Moment_Gate_Row(predicted_totals, true_totals)
    # runs zero and three are within five percent and share the true sign, one and two are not
    assert row["pass_fraction"] == 0.5
    assert row["run_count"] == 4.0
    magnetization_grid = np.full((4, 4, 4), 0.25)
    assert abs(Total_Moment(magnetization_grid, cell_volume) - 0.25 * cell_volume) < 1e-9


@pytest.mark.pool
def Test_The_Sad_Floor_Reproduces_Stage_Zeros_Number() -> None:
    """the superposed-atomic-density floor over the whole defect campaign matches the committed stage-0 figure"""
    payload = json.loads((ARTIFACT_DIRECTORY / "paired_fields_fivefold.json").read_text())
    identifiers = [
        identifier
        for unit in payload.values()
        if unit["campaign"] == "defect_set"
        for identifier in unit["run_identifiers"]
    ]
    structures = tuple(
        structure
        for structure in (Loaded_Structure("defect_set", identifier) for identifier in identifiers)
        if structure is not None
    )
    errors = Deep_Dft_Superposed_Atomic_Density_Errors(structures)
    assert len(errors) > 180
    median_percent = 100.0 * float(np.median(list(errors.values())))
    assert 14.5 < median_percent < 15.5


def Test_Every_Inspect_Key_Renders(tmp_path: Path) -> None:
    """the generic inspection suite draws every key deep_dft exposes, skipping none"""
    member = Deep_Dft_Network(TINY_VOCABULARY, seed=11, hidden_channels=4, basis_count=3, cutoff_radius=5.0)
    structure = Small_Structure(4, 4.0, seed=12)
    domain = structure.domain
    grid_discretization: Discretization = GridSpec((4, 4, 4))
    member(structure, grid_discretization, Coefficients(vector=np.asarray([8.0]), domain=domain))
    inspected = {key: np.asarray(value, dtype=np.float64) for key, value in member.Inspect().items()}
    suite = Render_Inspection_Suite(inspected, tmp_path, "deep_dft")
    assert suite.skipped == ()
    assert len(suite.written) > 0

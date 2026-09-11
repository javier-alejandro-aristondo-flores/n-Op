"""the branch-trunk member's assembly, its parameters and its path through the engine"""

import tomllib
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from operators.compositions import WithoutIntegralLayers
from operators.data import Gram_Pod, Project
from operators.deep_operator_network import (
    CONFIGURATIONS,
    DeepOperatorNetwork,
    Pointwise_Statistics,
    Principal_Component_Network,
    Proper_Orthogonal_Network,
)
from operators.framework import Coefficients, Domain, GridFunction, GridSpec
from operators.readouts import BiasedModeExpansion, FixedModeExpansion, PointwiseStandardizedExpansion
from operators.substrate import NumpyEngine, ParameterSet

CUBE = Domain(lattice=np.eye(3) * 3.57)

MANIFEST_PATH = Path(__file__).resolve().parent.parent / "deep_operator_network" / "manifest.toml"


def Small_Basis(rank: int = 6) -> Any:
    """a basis over a tiny grid, enough to assemble the member against"""
    generator = np.random.default_rng(5)
    return Gram_Pod(np.asarray(generator.normal(size=(20, 64)), dtype=np.float64), rank=rank)


def Voxel_Statistics(seed: int = 9) -> tuple[Any, Any]:
    """a per-voxel mean and a spread that varies from voxel to voxel on purpose"""
    generator = np.random.default_rng(seed)
    mean = generator.normal(size=64)
    # a spread that is not the same everywhere is what a global rescaling could not stand in for
    scale = 0.5 + generator.random(64)
    return mean, scale


def Test_The_Layerless_Composition_Carries_Its_Vector_Through() -> None:
    """a map with no integral to take passes its latent vector along unchanged"""
    composition = WithoutIntegralLayers()
    latent = Coefficients(vector=np.arange(5.0), domain=CUBE)
    carried = composition.Apply(latent)
    assert np.allclose(np.asarray(carried.vector), np.arange(5.0))
    assert np.allclose(composition.Inspect()["last_carried_vector"], np.arange(5.0))


def Test_The_Member_Collects_Every_Learned_Array_Under_One_Namespace() -> None:
    """the trainer is handed the branch's arrays, and the fixed basis contributes none"""
    member = Principal_Component_Network(Small_Basis(), (4, 4, 4), parameter_width=6, hidden_widths=(16, 16))
    collected = member.Parameter_Values()
    assert all(name.startswith("sensor_encoder_") for name in collected)
    assert len(collected) == 6
    # the basis is given rather than learned, so it owns nothing the optimizer should touch
    assert member.basis_readout.parameter_values == {}


def Test_The_Member_Inspects_Under_Part_Prefixes() -> None:
    """an assembled member is one flat browsable namespace, each key naming its owner"""
    member = Principal_Component_Network(Small_Basis(), (4, 4, 4), parameter_width=6, hidden_widths=(16,))
    member(Coefficients(vector=np.zeros(6), domain=CUBE), GridSpec((4, 4, 4)))
    inspected = member.Inspect()
    assert any(name.startswith("encoder.") for name in inspected)
    assert any(name.startswith("readout.") for name in inspected)
    assert "readout.basis_modes" in inspected


def Test_The_Member_Refuses_A_Configuration_It_Does_Not_Have() -> None:
    """a misspelled configuration is a mistake, not a silently different model"""
    basis = Small_Basis()
    branch = Principal_Component_Network(basis, (4, 4, 4), 6, (8,)).branch
    with pytest.raises(ValueError):
        DeepOperatorNetwork(branch, FixedModeExpansion(basis, (4, 4, 4)), "canonical_but_misspelled")
    assert "principal_component" in CONFIGURATIONS


def Test_The_Member_Reads_Out_A_Field_On_The_Requested_Grid() -> None:
    """parameters in, a field of the asked-for shape out"""
    member = Principal_Component_Network(Small_Basis(), (4, 4, 4), parameter_width=6, hidden_widths=(16,))
    produced = member(Coefficients(vector=np.ones(6), domain=CUBE), GridSpec((4, 4, 4)))
    assert isinstance(produced, GridFunction)
    assert np.asarray(produced.values).shape == (1, 4, 4, 4)


def Test_Gradients_Reach_Every_Branch_Array_Through_The_Engine() -> None:
    """the loss the trainer will use differentiates onto all of the member's parameters"""
    basis = Small_Basis(rank=4)
    member = Principal_Component_Network(basis, (4, 4, 4), parameter_width=6, hidden_widths=(8,))
    generator = np.random.default_rng(6)
    parameters = np.asarray(generator.normal(size=(10, 6)), dtype=np.float64)
    targets = np.asarray(generator.normal(size=(10, 4)), dtype=np.float64)
    batch = np.concatenate([parameters, targets], axis=1)

    def Coefficient_Loss(lifted: dict[str, Any], lifted_batch: Any) -> Any:
        predicted = member.Forward_Coefficients(lifted, lifted_batch[:, :6])
        residuals = predicted - lifted_batch[:, 6:]
        return (residuals * residuals).mean()

    gradients = NumpyEngine().Gradients(
        ParameterSet(values=member.Parameter_Values()), lambda lifted: Coefficient_Loss(lifted, batch)
    )
    assert set(gradients) == set(member.Parameter_Values())
    assert all(np.isfinite(gradient).all() for gradient in gradients.values())
    assert all(np.abs(gradient).max() > 0.0 for gradient in gradients.values())


def Test_Exact_Coefficients_Rebuild_The_Field_They_Came_From() -> None:
    """the readout is the inverse of the projection, so a perfect branch would be exact"""
    generator = np.random.default_rng(7)
    snapshots = np.asarray(generator.normal(size=(12, 64)), dtype=np.float64)
    basis = Gram_Pod(snapshots, rank=12)
    readout = FixedModeExpansion(basis, (4, 4, 4))
    for snapshot in snapshots[:3]:
        exact = Project(basis, snapshot[None, :])[0]
        rebuilt = readout(Coefficients(vector=exact, domain=CUBE), GridSpec((4, 4, 4)))
        assert isinstance(rebuilt, GridFunction)
        assert np.allclose(np.asarray(rebuilt.values).reshape(-1), snapshot, atol=1e-10)


def Test_The_Manifest_Names_The_Parts_The_Member_Actually_Assembles() -> None:
    """a manifest is a description of the code, and a description that drifts is fiction"""
    manifest = tomllib.loads(MANIFEST_PATH.read_text())
    member = Principal_Component_Network(Small_Basis(), (4, 4, 4), parameter_width=6, hidden_widths=(16,))
    for part_name, assembled in (
        ("encoder", member.branch),
        ("composition", member.composition),
        ("readout", member.basis_readout),
    ):
        assert type(assembled).__name__ in manifest["parts"][part_name], part_name
    # the branch-trunk map takes no integral, so claiming a kernel would be inventing one
    assert manifest["parts"]["kernel"].startswith("none")
    assert manifest["depends_on"]["kernels"] == []
    assert member.configuration in manifest["assembled"]


def Test_The_Biased_Mode_Expansion_Matches_The_Fixed_Expansion_Until_Its_Offset_Moves() -> None:
    """the learned offset is the one thing that tells this general-purpose variant from the plain one"""
    basis = Small_Basis(rank=5)
    plain = FixedModeExpansion(basis, (4, 4, 4))
    offset = BiasedModeExpansion(basis, (4, 4, 4))
    coefficients = Coefficients(vector=np.linspace(-1.0, 1.0, 5), domain=CUBE)
    plain_field = np.asarray(plain(coefficients, GridSpec((4, 4, 4))).values)
    zero_offset_field = np.asarray(offset(coefficients, GridSpec((4, 4, 4))).values)
    assert np.allclose(zero_offset_field, plain_field, atol=1e-12)
    offset.parameter_values["output_bias"] = np.asarray([0.25])
    shifted_field = np.asarray(offset(coefficients, GridSpec((4, 4, 4))).values)
    assert np.allclose(shifted_field - plain_field, 0.25, atol=1e-12)


def Test_The_Pointwise_Standardized_Readout_Matches_Its_Published_Formula() -> None:
    """modes weighted by the branch, the standardized-space mean and the offset, then carried onto the block"""
    basis = Small_Basis(rank=5)
    voxel_mean, voxel_scale = Voxel_Statistics()
    readout = PointwiseStandardizedExpansion(basis, (4, 4, 4), voxel_mean, voxel_scale)
    readout.parameter_values["output_bias"] = np.asarray([0.3])
    coefficients_vector = np.linspace(-1.0, 1.0, 5)
    produced = np.asarray(
        readout(Coefficients(vector=coefficients_vector, domain=CUBE), GridSpec((4, 4, 4))).values
    ).reshape(-1)
    standardized = coefficients_vector @ basis.modes + basis.mean + 0.3
    expected = standardized * voxel_scale + voxel_mean
    assert np.allclose(produced, expected, atol=1e-10)


def Test_The_Pointwise_Standardized_Readout_Is_Not_A_Global_Rescaling_In_Disguise() -> None:
    """a spread that differs by voxel must move voxels by different amounts than one shared spread would"""
    basis = Small_Basis(rank=5)
    voxel_mean, varying_scale = Voxel_Statistics()
    uniform_scale = np.full(64, float(varying_scale.mean()))
    coefficients = Coefficients(vector=np.linspace(-1.0, 1.0, 5), domain=CUBE)
    varying = PointwiseStandardizedExpansion(basis, (4, 4, 4), voxel_mean, varying_scale)
    uniform = PointwiseStandardizedExpansion(basis, (4, 4, 4), voxel_mean, uniform_scale)
    varying_field = np.asarray(varying(coefficients, GridSpec((4, 4, 4))).values)
    uniform_field = np.asarray(uniform(coefficients, GridSpec((4, 4, 4))).values)
    assert not np.allclose(varying_field, uniform_field)


def Test_A_Constant_Voxel_Does_Not_Make_The_Readout_Non_Finite() -> None:
    """a voxel with no spread across the training block is guarded rather than divided by zero"""
    generator = np.random.default_rng(11)
    training_fields = np.asarray(generator.normal(size=(20, 64)), dtype=np.float64)
    # one voxel that never moves across every training run, the case the guard exists for
    training_fields[:, 0] = 3.0
    voxel_mean, voxel_scale = Pointwise_Statistics(training_fields)
    assert voxel_scale[0] == 1.0
    basis = Gram_Pod((training_fields - voxel_mean) / voxel_scale, rank=6)
    readout = PointwiseStandardizedExpansion(basis, (4, 4, 4), voxel_mean, voxel_scale)
    produced = readout(Coefficients(vector=np.ones(6), domain=CUBE), GridSpec((4, 4, 4)))
    assert np.isfinite(np.asarray(produced.values)).all()


def Test_The_Proper_Orthogonal_Member_Collects_Its_Offset_Beside_The_Branch_Arrays() -> None:
    """the learned offset is the one array the fixed basis now contributes to the trainer"""
    voxel_mean, voxel_scale = Voxel_Statistics()
    member = Proper_Orthogonal_Network(
        Small_Basis(), (4, 4, 4), voxel_mean, voxel_scale, parameter_width=6, hidden_widths=(16, 16)
    )
    collected = member.Parameter_Values()
    assert sum(1 for name in collected if name.startswith("sensor_encoder_")) == 6
    assert member.basis_readout.parameter_values.keys() == {"output_bias"}
    assert collected.keys() >= {"output_bias"}
    assert len(collected) == 7


def Test_The_Proper_Orthogonal_Member_Inspects_Its_Offset_And_Its_Pointwise_Statistics() -> None:
    """the offset and the per-voxel statistics are reachable by name under the readout prefix"""
    voxel_mean, voxel_scale = Voxel_Statistics()
    member = Proper_Orthogonal_Network(
        Small_Basis(), (4, 4, 4), voxel_mean, voxel_scale, parameter_width=6, hidden_widths=(16,)
    )
    member(Coefficients(vector=np.zeros(6), domain=CUBE), GridSpec((4, 4, 4)))
    inspected = member.Inspect()
    assert "readout.output_bias" in inspected
    assert "readout.voxel_mean" in inspected
    assert "readout.voxel_scale" in inspected
    assert "readout.basis_modes" in inspected
    assert "readout.last_coefficients" in inspected


def Test_The_Proper_Orthogonal_Member_Reads_Out_A_Field_On_The_Requested_Grid() -> None:
    """parameters in, a field of the asked-for shape out, exactly as the fixed-basis sibling does"""
    voxel_mean, voxel_scale = Voxel_Statistics()
    member = Proper_Orthogonal_Network(
        Small_Basis(), (4, 4, 4), voxel_mean, voxel_scale, parameter_width=6, hidden_widths=(16,)
    )
    produced = member(Coefficients(vector=np.ones(6), domain=CUBE), GridSpec((4, 4, 4)))
    assert isinstance(produced, GridFunction)
    assert np.asarray(produced.values).shape == (1, 4, 4, 4)


def Test_Gradients_Reach_The_Proper_Orthogonal_Offset_Too() -> None:
    """a field-space loss differentiates onto the offset exactly as it does onto the branch"""
    basis = Small_Basis(rank=4)
    voxel_mean, voxel_scale = Voxel_Statistics()
    member = Proper_Orthogonal_Network(
        basis, (4, 4, 4), voxel_mean, voxel_scale, parameter_width=6, hidden_widths=(8,)
    )
    generator = np.random.default_rng(8)
    parameters = np.asarray(generator.normal(size=(10, 6)), dtype=np.float64)
    targets = np.asarray(generator.normal(size=(10, 64)), dtype=np.float64)
    batch = np.concatenate([parameters, targets], axis=1)
    engine = NumpyEngine()
    # the union narrows here, since only this configuration's readout carries an offset to reach
    readout = member.basis_readout
    assert isinstance(readout, PointwiseStandardizedExpansion)
    modes_constant, mean_constant, voxel_mean_constant, voxel_scale_constant = readout.Lifted_Constants(engine)

    def Field_Loss(lifted: dict[str, Any], lifted_batch: Any) -> Any:
        predicted_coefficients = member.Forward_Coefficients(lifted, lifted_batch[:, :6])
        predicted_fields = readout.Forward(
            lifted, predicted_coefficients, modes_constant, mean_constant, voxel_mean_constant, voxel_scale_constant
        )
        residuals = predicted_fields - lifted_batch[:, 6:]
        return (residuals * residuals).mean()

    gradients = engine.Gradients(
        ParameterSet(values=member.Parameter_Values()), lambda lifted: Field_Loss(lifted, batch)
    )
    assert set(gradients) == set(member.Parameter_Values())
    assert "output_bias" in gradients
    assert all(np.isfinite(gradient).all() for gradient in gradients.values())
    assert all(np.abs(gradient).max() > 0.0 for gradient in gradients.values())

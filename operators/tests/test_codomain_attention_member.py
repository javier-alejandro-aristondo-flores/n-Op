"""the assembled codomain-attention member: masking, heads, split derivation and both-engine agreement"""

import json
from pathlib import Path
from typing import cast

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.codomain_attention import (
    CANONICAL_LABEL_INDICES,
    CodomainAttention,
    HIDDEN_CHANNELS,
)
from operators.codomain_attention.channels import (
    CHANNEL_VOCABULARY,
    CHARGE_DENSITY,
    ChannelStatistics,
    DENSITY_GROUP,
    ELECTRON_LOCALIZATION_UP,
    ELF_GROUP,
    FUNCTIONAL_COVARIATE_WIDTH,
    Invert_Channel,
    LOCAL_POTENTIAL_UP,
    MAGNETIZATION_DENSITY,
    POTENTIAL_GROUP,
    Transform_Channel,
)
from operators.codomain_attention.masking import (
    Augmented_Channels,
    DIAMOND_GRID_OPERATIONS,
    Drawn_Grid_Operation,
    Visible_Labels,
)
from operators.codomain_attention.readout import Bounded_Unit_Interval, Per_Token_Heads
from operators.codomain_attention.report import Completion_Loss
from operators.codomain_attention.splits import ALLOY_CAMPAIGN, CompletionBlock, CUBIC_CAMPAIGNS
from operators.data import ARTIFACT_DIRECTORY
from operators.framework import Domain, GridFunction, GridSpec, Spectral_Truncation_Resample, UniformGridQuadrature
from operators.inspection.plots import Render_Inspection_Suite
from operators.substrate import NumpyEngine, ParameterSet, Torch_Is_Available, TorchEngine
from operators.tasks import Card_Named
from operators.training import TrainingBatch

TOY_COARSE_SHAPE = (4, 4, 4)


def Toy_Statistics() -> ChannelStatistics:
    """a fixed, physically plausible set of transform constants for tests that never touch the corpus"""
    return ChannelStatistics(reference_density=0.5, magnetization_scale=0.2, potential_scale=1.5)


def Toy_Member(seed: int = 42) -> CodomainAttention:
    """a small member, fast to construct and to differentiate, at the toy coarse grid every test below shares"""
    return CodomainAttention(
        Toy_Statistics(),
        hidden_channels=2,
        kept_modes=(1, 1, 1),
        head_count=1,
        layer_count=2,
        seed=seed,
        coarse_shape=TOY_COARSE_SHAPE,
    )


def Test_The_Default_Configuration_Constructs_And_Reports_A_Positive_Parameter_Count() -> None:
    """the pre-registered minimal configuration builds cleanly at its real width, depth and mode count"""
    member = CodomainAttention(Toy_Statistics())
    assert member.hidden_channels == HIDDEN_CHANNELS
    assert member.Parameter_Count() > 0
    assert "mask_flag" in member.Parameter_Values()


def Test_The_Default_Configuration_Recomputes_Its_Layers() -> None:
    """this member trades a second forward per layer for the room by default, the measured reason it must"""
    member = CodomainAttention(Toy_Statistics())
    assert member.recompute_layers is True
    assert member.attention_stack.recompute_layers is True
    built_off = CodomainAttention(Toy_Statistics(), recompute_layers=False)
    assert built_off.recompute_layers is False
    assert built_off.attention_stack.recompute_layers is False


def Test_The_Member_Answers_A_Toy_Grid_With_Every_Channel_Present() -> None:
    """all six channels visible in, all six channels out, on the coarse grid the member was built for"""
    member = Toy_Member()
    generator = np.random.default_rng(1)
    values = generator.random((len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE))
    input_function = GridFunction(
        values=values,
        channel_labels=CHANNEL_VOCABULARY,
        domain=Domain(lattice=np.eye(3) * 2.0),
        quadrature=UniformGridQuadrature(cell_volume=8.0, point_count=64),
    )
    produced = member(input_function, GridSpec(TOY_COARSE_SHAPE))
    assert produced.channel_labels == CHANNEL_VOCABULARY
    assert np.asarray(produced.values).shape == (len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE)
    assert np.all(np.isfinite(np.asarray(produced.values)))


def Test_Any_Subset_Present_At_Call_Time_Still_Answers_All_Six() -> None:
    """the mask-flag substitution lets any subset of channels in and still returns the full vocabulary"""
    member = Toy_Member()
    generator = np.random.default_rng(2)
    present_labels = (CHARGE_DENSITY, LOCAL_POTENTIAL_UP)
    values = generator.random((len(present_labels), *TOY_COARSE_SHAPE))
    input_function = GridFunction(
        values=values,
        channel_labels=present_labels,
        domain=Domain(lattice=np.eye(3) * 2.0),
        quadrature=UniformGridQuadrature(cell_volume=8.0, point_count=64),
    )
    produced = member(input_function, GridSpec(TOY_COARSE_SHAPE))
    assert produced.channel_labels == CHANNEL_VOCABULARY
    assert np.asarray(produced.values).shape == (len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE)


def Test_The_Shared_Parts_Answer_Five_And_Six_Tokens_With_The_Same_Parameters() -> None:
    """the encoder, the attention stack and the readout all accept a run that structurally lacks one channel"""
    member = Toy_Member()
    parameters = member.Parameter_Values()
    generator = np.random.default_rng(3)
    six_values = generator.random((len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE))
    condition = np.zeros(FUNCTIONAL_COVARIATE_WIDTH)

    six_tokens = member.channel_encoder.Forward(parameters, six_values, CANONICAL_LABEL_INDICES, condition)
    six_hidden = member.attention_stack.Forward(parameters, six_tokens)
    six_output = member.token_readout.Forward(parameters, six_hidden)
    assert np.asarray(six_output).shape == (len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE)

    five_labels = tuple(label for label in CHANNEL_VOCABULARY if label != MAGNETIZATION_DENSITY)
    five_indices = np.asarray([CHANNEL_VOCABULARY.index(label) for label in five_labels], dtype=np.intp)
    five_values = np.stack([six_values[channel_index] for channel_index in five_indices])
    five_tokens = member.channel_encoder.Forward(parameters, five_values, five_indices, condition)
    five_hidden = member.attention_stack.Forward(parameters, five_tokens)
    five_output = member.token_readout.Forward(parameters, five_hidden)
    assert np.asarray(five_output).shape == (len(five_labels), *TOY_COARSE_SHAPE)
    # the same instance answered both, so nothing about its own stored arrays moved between the two calls
    assert set(member.Parameter_Values()) == set(parameters)
    for name, value in parameters.items():
        assert np.array_equal(value, member.Parameter_Values()[name])


def Test_Per_Token_Heads_Touch_Only_Their_Own_Token() -> None:
    """the bounded head on elf, the zero-mean pin on potential, identity elsewhere, and never a cross-token effect"""
    generator = np.random.default_rng(4)
    reconstruction = generator.normal(0.0, 2.0, size=(len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE))
    heads_output = np.asarray(Per_Token_Heads(reconstruction, CHANNEL_VOCABULARY))
    for position, label in enumerate(CHANNEL_VOCABULARY):
        if label in ELF_GROUP:
            expected = np.asarray(Bounded_Unit_Interval(reconstruction[position]))
            assert np.allclose(heads_output[position], expected)
            assert np.all(heads_output[position] > 0.0)
            assert np.all(heads_output[position] < 1.0)
        elif label in POTENTIAL_GROUP:
            assert abs(float(heads_output[position].mean())) < 1e-8
        else:
            assert np.array_equal(heads_output[position], reconstruction[position])

    perturbed = reconstruction.copy()
    elf_position = CHANNEL_VOCABULARY.index(ELECTRON_LOCALIZATION_UP)
    perturbed[elf_position] = perturbed[elf_position] + 5.0
    perturbed_output = np.asarray(Per_Token_Heads(perturbed, CHANNEL_VOCABULARY))
    for position in range(len(CHANNEL_VOCABULARY)):
        if position == elf_position:
            continue
        assert np.array_equal(perturbed_output[position], heads_output[position])


def Test_The_Masked_Loss_Ignores_Visible_Tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    """changing the ground truth at a visible position never moves the loss, only a hidden position's own gap does"""
    # the model's own reconstruction legitimately depends on what the visible tokens carry, through attention --
    # what must not depend on it is the loss's own masking arithmetic, so the forward is stubbed to a fixed answer
    member = Toy_Member()
    generator = np.random.default_rng(5)
    fixed_reconstruction = generator.random((len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE))

    def Stub_Forward_Tokens(lifted: object, full_stack: object, visible_mask: object, condition_vector: object) -> object:
        del lifted, full_stack, visible_mask, condition_vector
        return fixed_reconstruction

    monkeypatch.setattr(member, "Forward_Tokens", Stub_Forward_Tokens)
    forward_loss = Completion_Loss(member)
    full_stack = generator.random((len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE)).astype(np.float32)
    visible_mask = np.asarray([1.0, 0.0, 1.0, 0.0, 1.0, 0.0], dtype=np.float32)
    condition_vector = np.zeros(FUNCTIONAL_COVARIATE_WIDTH)

    def Batch_Arrays(stack: np.ndarray) -> dict[str, np.ndarray]:
        return {
            "full_transformed_stack": stack[None],
            "visible_mask": visible_mask[None],
            "condition_vector": condition_vector[None],
        }

    baseline = float(forward_loss(member.Parameter_Values(), Batch_Arrays(full_stack)))

    # only the visible entries move, by an amount large enough that a leak into the loss could not hide
    perturbed_stack = full_stack.copy()
    perturbed_stack[0] = perturbed_stack[0] + 100.0
    perturbed_stack[2] = perturbed_stack[2] - 100.0
    perturbed = float(forward_loss(member.Parameter_Values(), Batch_Arrays(perturbed_stack)))
    assert abs(baseline - perturbed) < 1e-9

    # the same perturbation applied to a hidden channel instead does move the loss, or the mask is not load-bearing
    hidden_perturbed_stack = full_stack.copy()
    hidden_perturbed_stack[1] = hidden_perturbed_stack[1] + 100.0
    hidden_perturbed = float(forward_loss(member.Parameter_Values(), Batch_Arrays(hidden_perturbed_stack)))
    assert abs(baseline - hidden_perturbed) > 1.0


def Test_Truncation_Commutes_With_Exact_Grid_Augmentation() -> None:
    """truncating then augmenting and augmenting then truncating land on the same coarse field"""
    generator = np.random.default_rng(6)
    fine_shape = (8, 8, 8)
    coarse_shape = (4, 4, 4)
    stack = generator.random((3, *fine_shape))
    for operation_index in (0, 5, 20, 47):
        matrix, translation = DIAMOND_GRID_OPERATIONS[operation_index]
        truncate_then_augment = Augmented_Channels(
            Spectral_Truncation_Resample(stack, coarse_shape), matrix, translation
        )
        augment_then_truncate = Spectral_Truncation_Resample(
            Augmented_Channels(stack, matrix, translation), coarse_shape
        )
        assert np.allclose(truncate_then_augment, augment_then_truncate, atol=1e-8)


def Test_Augmentation_Commutes_With_Building_The_Token_Stack() -> None:
    """encoding a channel stack after an exact grid operation equals applying that operation to the tokens afterward"""
    hidden_channels = 2
    member = Toy_Member()
    generator = np.random.default_rng(7)
    raw_stack = generator.random((len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE))
    matrix, translation = Drawn_Grid_Operation(np.random.default_rng(8))
    augmented_stack = Augmented_Channels(raw_stack, matrix, translation)
    condition = np.zeros(FUNCTIONAL_COVARIATE_WIDTH)
    parameters = member.Parameter_Values()

    tokens_from_augmented = np.asarray(
        member.channel_encoder.Forward(parameters, augmented_stack, CANONICAL_LABEL_INDICES, condition)
    )
    tokens_unaugmented = np.asarray(
        member.channel_encoder.Forward(parameters, raw_stack, CANONICAL_LABEL_INDICES, condition)
    )
    reshaped = tokens_unaugmented.reshape(len(CHANNEL_VOCABULARY) * hidden_channels, *TOY_COARSE_SHAPE)
    augmented_tokens_afterward = Augmented_Channels(reshaped, matrix, translation)
    assert np.allclose(tokens_from_augmented.reshape(-1, *TOY_COARSE_SHAPE), augmented_tokens_afterward, atol=1e-10)


def Test_Forward_Tokens_Agrees_On_Both_Engines() -> None:
    """the lifted masked-reconstruction forward answers the same numbers plain and on the foreign engine"""
    member = Toy_Member()
    generator = np.random.default_rng(9)
    full_stack = generator.random((len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE))
    visible_mask = np.asarray([1.0, 1.0, 0.0, 0.0, 1.0, 0.0])
    condition_vector = np.zeros(FUNCTIONAL_COVARIATE_WIDTH)
    parameters = member.Parameter_Values()
    numpy_output = np.asarray(member.Forward_Tokens(parameters, full_stack, visible_mask, condition_vector))
    assert numpy_output.shape == (len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE)

    if Torch_Is_Available():
        engine = TorchEngine()
        lifted_parameters = engine.Lift(parameters, requires_gradient=False)
        lifted_stack = engine.Lift_Constant(full_stack)
        lifted_mask = engine.Lift_Constant(visible_mask)
        lifted_condition = engine.Lift_Constant(condition_vector)
        torch_output = member.Forward_Tokens(lifted_parameters, lifted_stack, lifted_mask, lifted_condition)
        torch_array = np.asarray(torch_output.detach().cpu().numpy(), dtype=np.float64)
        assert np.allclose(torch_array, numpy_output, atol=1e-6)


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Gradient_Reaches_Every_Parameter_On_Both_Engines() -> None:
    """a tape severed anywhere in the encoder, the four layers, the readout or the mask flag shows as a zero gradient"""
    member = Toy_Member()
    generator = np.random.default_rng(10)
    full_stack = generator.random((len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE)).astype(np.float32)
    visible_mask = np.asarray([1.0, 0.0, 1.0, 0.0, 1.0, 0.0], dtype=np.float32)
    condition_vector = generator.random(FUNCTIONAL_COVARIATE_WIDTH)
    parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})
    batch = TrainingBatch(
        {
            "full_transformed_stack": full_stack[None],
            "visible_mask": visible_mask[None],
            "condition_vector": condition_vector[None],
        }
    )
    forward_loss = Completion_Loss(member)
    engine = TorchEngine()
    lifted_batch = {
        name: engine.Lift_Constant(cast(NDArray[np.float64], array)) for name, array in batch.arrays.items()
    }

    def Lifted_Loss(lifted_parameters: dict[str, object]) -> object:
        return forward_loss(lifted_parameters, lifted_batch)

    def Reference_Loss(lifted_parameters: dict[str, object]) -> object:
        return forward_loss(lifted_parameters, batch.arrays)

    value, gradients = engine.Value_And_Gradients(parameters, Lifted_Loss)
    reference = NumpyEngine()
    assert abs(value - reference.Evaluate(parameters, Reference_Loss)) < 1e-6
    reference_gradients = reference.Gradients(parameters, Reference_Loss)
    assert set(gradients) == set(reference_gradients)
    for name, gradient in gradients.items():
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-2, atol=1e-3), name
    # every logical group receives a nonzero gradient somewhere within it -- encoder, both layers' own kernel and
    # local linear term, the readout and the mask flag; a severed tape shows as an all-zero group here. checked by
    # group rather than by individual array, since the spectral kernel's own Hermitian symmetry legitimately zeros
    # specific individual sub-arrays (test_codomain_attention.py's own gradient test uses the same grouping)
    expected_groups = (
        "token_lift_weights", "token_lift_biases", "label_encodings", "condition_projection_weights",
        "layer_0.kernel.", "layer_0.local_linear.", "layer_1.kernel.", "layer_1.local_linear.",
        "readout_weights", "readout_biases", "mask_flag",
    )
    for group in expected_groups:
        matching = [name for name in gradients if name.startswith(group)]
        assert matching, group
        assert any(float(np.abs(gradients[name]).max()) > 1e-8 for name in matching), group


def Test_Inspect_Renders_Every_Key(tmp_path: Path) -> None:
    """everything the member exposes after a call is drawn by the generic renderer, nothing skipped"""
    member = Toy_Member()
    generator = np.random.default_rng(11)
    values = generator.random((len(CHANNEL_VOCABULARY), *TOY_COARSE_SHAPE))
    input_function = GridFunction(
        values=values,
        channel_labels=CHANNEL_VOCABULARY,
        domain=Domain(lattice=np.eye(3) * 2.0),
        quadrature=UniformGridQuadrature(cell_volume=8.0, point_count=64),
    )
    member(input_function, GridSpec(TOY_COARSE_SHAPE))
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    suite = Render_Inspection_Suite(inspected, tmp_path)
    assert suite.skipped == ()


def Test_Channel_Transform_Round_Trips() -> None:
    """every channel's own transform undoes exactly, a potential channel read back against its own zero-mean version"""
    statistics = Toy_Statistics()
    generator = np.random.default_rng(12)
    density = generator.random((4, 4, 4)) * 2.0
    recovered_density = Invert_Channel(CHARGE_DENSITY, Transform_Channel(CHARGE_DENSITY, density, statistics), statistics)
    assert np.allclose(recovered_density, density, atol=1e-8)

    magnetization = generator.normal(0.0, 0.2, size=(4, 4, 4))
    recovered_magnetization = Invert_Channel(
        MAGNETIZATION_DENSITY, Transform_Channel(MAGNETIZATION_DENSITY, magnetization, statistics), statistics
    )
    assert np.allclose(recovered_magnetization, magnetization, atol=1e-8)

    elf = generator.random((4, 4, 4))
    assert np.array_equal(Transform_Channel(ELECTRON_LOCALIZATION_UP, elf, statistics), elf)
    assert np.array_equal(Invert_Channel(ELECTRON_LOCALIZATION_UP, elf, statistics), elf)

    potential = generator.normal(5.0, 1.0, size=(4, 4, 4))
    transformed_potential = Transform_Channel(LOCAL_POTENTIAL_UP, potential, statistics)
    assert abs(float(transformed_potential.mean())) < 1e-8
    recovered_potential = Invert_Channel(LOCAL_POTENTIAL_UP, transformed_potential, statistics)
    assert np.allclose(recovered_potential, potential - potential.mean(), atol=1e-8)


def Test_Named_Mask_Patterns_Match_The_Canons_Own_Pairwise_Task_Cards() -> None:
    """the four named patterns reveal exactly what the dedicated pairwise task cards already declare as their own inputs"""
    generator = np.random.default_rng(13)
    localization_card = Card_Named("charge_to_localization")
    potential_card = Card_Named("charge_to_potential")
    joint_card = Card_Named("charge_and_potential_to_localization")
    assert set(localization_card.inputs) == set(DENSITY_GROUP)
    assert set(localization_card.targets) == set(ELF_GROUP)
    assert set(potential_card.inputs) == set(DENSITY_GROUP)
    assert set(potential_card.targets) == set(POTENTIAL_GROUP)
    assert set(joint_card.inputs) == set(DENSITY_GROUP) | set(POTENTIAL_GROUP)
    assert set(joint_card.targets) == set(ELF_GROUP)
    assert Visible_Labels("density_to_elf_and_potential", CHANNEL_VOCABULARY, generator) == DENSITY_GROUP
    assert Visible_Labels("density_and_potential_to_elf", CHANNEL_VOCABULARY, generator) == (
        DENSITY_GROUP + POTENTIAL_GROUP
    )
    assert Visible_Labels("elf_to_density", CHANNEL_VOCABULARY, generator) == ELF_GROUP
    assert Visible_Labels("potential_to_density", CHANNEL_VOCABULARY, generator) == POTENTIAL_GROUP


@pytest.mark.pool
def Test_The_Completion_Split_Holds_Out_Every_Alloy_Unit_And_Keeps_Fold_Membership() -> None:
    """every judged identifier comes from the cubic campaigns, matches the committed fold map, and alloy never trains"""
    block = CompletionBlock()
    payload = json.loads((ARTIFACT_DIRECTORY / "paired_fields_fivefold.json").read_text())
    checked = 0
    for fold, identifiers in block.by_fold.items():
        for identifier in identifiers:
            assert block.campaign_of[identifier] in CUBIC_CAMPAIGNS
            unit_key = block.unit_of[identifier]
            assert payload[unit_key]["fold"] == fold
            checked += 1
    assert checked > 0
    assert len(block.evaluation) > 0
    assert len(block.validation) > 0
    assert len(block.member_train) > 0
    assert set(block.evaluation).isdisjoint(block.validation)
    assert set(block.evaluation).isdisjoint(block.member_train)
    transfer_identifiers = block.Alloy_Transfer_Identifiers()
    assert transfer_identifiers
    for identifier in transfer_identifiers:
        assert identifier not in block.campaign_of
        unit_key, run_path = block.alloy_membership[identifier]
        assert payload[unit_key]["campaign"] == ALLOY_CAMPAIGN
        assert run_path


@pytest.mark.pool
def Test_The_Low_Data_Defect_Slice_Is_A_Deterministic_Quarter_Of_The_Pretraining_Defect_Identifiers() -> None:
    """k3's own low-data draw is reproducible, a genuine subset of the pretraining population, and near a quarter"""
    block = CompletionBlock()
    low_data_identifiers = block.Low_Data_Defect_Identifiers()
    defect_pretrain_identifiers = [
        identifier for identifier in block.member_train if block.campaign_of[identifier] == "defect_set"
    ]
    assert low_data_identifiers == block.Low_Data_Defect_Identifiers()
    assert set(low_data_identifiers).issubset(set(defect_pretrain_identifiers))
    assert abs(len(low_data_identifiers) / len(defect_pretrain_identifiers) - 0.25) < 0.05

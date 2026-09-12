"""the metric-aware spectral kernel: one gain, a function of the physical wavevector, across metrics"""

from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.framework import Dense_Reference_Integral, Domain, GridFunction, GridSpec, UniformGridQuadrature
from operators.inspection.plots import Render_Inspection_Suite
from operators.kernels.spectral import (
    GAIN_NAME_PREFIX,
    GAIN_NETWORK_HIDDEN_WIDTH,
    MODE_WAVEVECTOR_FEATURES_KEY,
    Mode_Wavevector_Features,
    Mode_Wavevector_Norms_Squared,
    SpectralKernel,
    WAVEVECTOR_FEATURE_EPSILON,
)
from operators.substrate import (
    Adam_Step,
    Cartesian_Wavevectors,
    Fresh_Adam_State,
    NumpyEngine,
    ParameterSet,
    Real_Fourier_Transform_3d,
    Reciprocal_Rows,
    Torch_Is_Available,
    TorchEngine,
)

CUBE = Domain(lattice=np.eye(3) * 2.0)

SHEARED = Domain(lattice=np.asarray([[3.0, 0.0, 0.0], [0.9, 2.6, 0.0], [0.4, -0.6, 3.3]]))

POISSON_GAIN_SCALE = 4.0 * np.pi

POISSON_KEPT_MODES = (2, 2, 2)

POISSON_GRID_SHAPE = (6, 6, 6)

POISSON_CUBE = Domain(lattice=np.eye(3) * 3.0)

POISSON_SHEARED = Domain(lattice=np.asarray([[3.0, 0.0, 0.0], [0.9, 2.6, 0.0], [0.4, -0.6, 3.3]]))


def Single_Channel_Field(domain: Domain, grid_shape: tuple[int, int, int], seed: int) -> GridFunction:
    """a random single-channel field on the given domain, its own cell volume included"""
    generator = np.random.default_rng(seed)
    lattice = np.asarray(domain.lattice, dtype=np.float64)
    cell_volume = float(abs(np.linalg.det(lattice)))
    return GridFunction(
        values=generator.random((1, *grid_shape)),
        channel_labels=("charge_density",),
        domain=domain,
        quadrature=UniformGridQuadrature(cell_volume=cell_volume, point_count=int(np.prod(grid_shape))),
    )


def Perturbed_Gain_Parameters(kernel: SpectralKernel, seed: int, spread: float = 0.3) -> None:
    """the gain network's own parameters nudged off their zero-initialized last layer, in place"""
    generator = np.random.default_rng(seed)
    for name in list(kernel.parameter_values):
        if name.startswith(f"{GAIN_NAME_PREFIX}_layer_"):
            shape = kernel.parameter_values[name].shape
            kernel.parameter_values[name] = kernel.parameter_values[name] + generator.normal(0.0, spread, size=shape)


def Test_Default_Construction_Is_Unchanged_By_The_Metric_Aware_Flag() -> None:
    """a plain kernel, built without the flag, still lands on the exact numbers it always has"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=1, input_channels=1, seed=40)
    assert set(kernel.parameter_values) == {"mode_weights_real", "mode_weights_imaginary"}
    assert kernel.gain_network is None
    field = Single_Channel_Field(CUBE, (4, 4, 4), seed=41)
    produced = np.asarray(kernel.Integrate(field, GridSpec((4, 4, 4))).values, dtype=np.float64)
    # pinned once against this exact seed and grid, so an accidental change to the default path is caught
    assert produced[0, 0, 0, 0] == pytest.approx(-0.09159337701110103, abs=1e-12)
    assert produced[0, 2, 1, 3] == pytest.approx(-0.10700982646385136, abs=1e-12)


def Test_A_Metric_Aware_Kernel_Starts_Exactly_At_Its_Metric_Blind_Twin() -> None:
    """an untrained feature moves nothing, so the two constructions agree to round-off"""
    blind = SpectralKernel(kept_modes=(1, 1, 2), output_channels=2, input_channels=2, seed=42)
    aware = SpectralKernel(kept_modes=(1, 1, 2), output_channels=2, input_channels=2, seed=42, metric_aware=True)
    for name, value in blind.parameter_values.items():
        assert np.array_equal(value, aware.parameter_values[name])
    single = Single_Channel_Field(SHEARED, (4, 4, 6), seed=43)
    # a two-channel field needs two channels of input, so widen what the single-channel helper built
    field = GridFunction(
        values=np.concatenate([np.asarray(single.values), np.asarray(single.values) * 0.5], axis=0),
        channel_labels=("first_channel", "second_channel"),
        domain=single.domain,
        quadrature=single.quadrature,
    )
    blind_output = np.asarray(blind.Integrate(field, GridSpec((4, 4, 6))).values, dtype=np.float64)
    aware_output = np.asarray(aware.Integrate(field, GridSpec((4, 4, 6))).values, dtype=np.float64)
    assert np.allclose(blind_output, aware_output, atol=1e-12)


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Gradients_Reach_The_Gain_Parameters_And_Agree_With_Finite_Differences() -> None:
    """a tape severed anywhere inside the gain perceptron would leave it untrainable"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=2, input_channels=2, seed=44, metric_aware=True)
    Perturbed_Gain_Parameters(kernel, seed=45)
    lattice = np.asarray(SHEARED.lattice, dtype=np.float64)
    feature = Mode_Wavevector_Features(lattice, kernel.kept_modes)
    generator = np.random.default_rng(46)
    field_values = generator.random((2, 4, 4, 4))
    target = generator.random((2, 4, 4, 4))
    parameters = ParameterSet(values={name: value.copy() for name, value in kernel.parameter_values.items()})

    def Loss_Over(lifted_field: Any, lifted_target: Any, lifted_feature: Any):
        def Loss(lifted: dict[str, Any]) -> Any:
            merged = {**lifted, MODE_WAVEVECTOR_FEATURES_KEY: lifted_feature}
            difference = kernel.Forward(merged, lifted_field, (4, 4, 4)) - lifted_target
            return (difference * difference).sum()

        return Loss

    engine = TorchEngine()
    value, gradients = engine.Value_And_Gradients(
        parameters,
        Loss_Over(engine.Lift_Constant(field_values), engine.Lift_Constant(target), engine.Lift_Constant(feature)),
    )
    reference = NumpyEngine()
    reference_loss = Loss_Over(field_values, target, feature)
    reference_value = reference.Evaluate(parameters, reference_loss)
    reference_gradients = reference.Gradients(parameters, reference_loss)
    assert abs(value - reference_value) < 1e-10
    assert set(gradients) == set(kernel.parameter_values)
    gain_names = [name for name in gradients if name.startswith(f"{GAIN_NAME_PREFIX}_layer_")]
    assert gain_names
    for name, gradient in gradients.items():
        # a tape severed anywhere between the parameter and the loss shows up here as an exactly zero gradient
        assert float(np.abs(gradient).max()) > 1e-6, name
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-5, atol=1e-6), name


def Test_The_Same_Weights_Answer_Differently_For_Different_Lattices() -> None:
    """handed two different lattices the same weights disagree, handed one lattice twice they agree exactly"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=1, input_channels=1, seed=47, metric_aware=True)
    Perturbed_Gain_Parameters(kernel, seed=48)
    field = Single_Channel_Field(CUBE, (4, 4, 4), seed=49)
    cube_output = kernel.Integrate(field, GridSpec((4, 4, 4)))
    same_cube_output = kernel.Integrate(field, GridSpec((4, 4, 4)))
    assert np.array_equal(np.asarray(cube_output.values), np.asarray(same_cube_output.values))
    sheared_field = GridFunction(field.values, field.channel_labels, SHEARED, field.quadrature)
    sheared_output = kernel.Integrate(sheared_field, GridSpec((4, 4, 4)))
    assert not np.allclose(np.asarray(cube_output.values), np.asarray(sheared_output.values))


def Test_The_Metric_Aware_Kernel_Matches_The_Dense_Oracle_With_Its_Gain_Folded_In() -> None:
    """the fused path and the closed-form pair kernel agree exactly once the gain is folded into the latter"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=2, input_channels=2, seed=50, metric_aware=True)
    Perturbed_Gain_Parameters(kernel, seed=51)
    kernel.Hermitian_Symmetrize()
    lattice = np.asarray(SHEARED.lattice, dtype=np.float64)
    cell_volume = float(abs(np.linalg.det(lattice)))
    field = GridFunction(
        values=np.random.default_rng(52).random((2, 6, 6, 6)),
        channel_labels=("first_channel", "second_channel"),
        domain=SHEARED,
        quadrature=UniformGridQuadrature(cell_volume=cell_volume, point_count=216),
    )
    reference = Dense_Reference_Integral(kernel.Dense_Kernel_Function(cell_volume, lattice), field, GridSpec((6, 6, 6)))
    produced = kernel.Integrate(field, GridSpec((6, 6, 6)))
    # a real field in, a real field out, even with the gain multiplying every mode
    assert np.asarray(produced.values).dtype.kind == "f"
    assert np.allclose(np.asarray(produced.values), reference, atol=1e-9)


def Test_Dense_Kernel_Function_Refuses_A_Metric_Aware_Kernel_Without_A_Lattice() -> None:
    """the dense form cannot fold in a gain it has no lattice to evaluate"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=1, input_channels=1, seed=53, metric_aware=True)
    with pytest.raises(ValueError):
        kernel.Dense_Kernel_Function(8.0)


def Test_Mode_Wavevector_Features_Matches_Gathered_Modes_Layout() -> None:
    """the feature block is exactly the kept-mode shape, ascending order, and the origin mode is finite"""
    kept_modes = (2, 1, 1)
    lattice = np.asarray(CUBE.lattice, dtype=np.float64)
    features = Mode_Wavevector_Features(lattice, kept_modes)
    mode_extents = tuple(2 * kept + 1 for kept in kept_modes)
    assert features.shape == mode_extents
    assert np.isfinite(features).all()
    # the cube's reciprocal rows are simply pi times the identity, so a hand-picked mode checks the convention directly
    reciprocal = Reciprocal_Rows(lattice)
    assert np.allclose(reciprocal, np.pi * np.eye(3))
    origin_position = kept_modes
    assert features[origin_position] == pytest.approx(np.log(WAVEVECTOR_FEATURE_EPSILON))
    first_axis_unit_position = (kept_modes[0] + 1, kept_modes[1], kept_modes[2])
    expected_squared = float(np.pi**2)
    assert features[first_axis_unit_position] == pytest.approx(np.log(expected_squared + WAVEVECTOR_FEATURE_EPSILON))
    norms_squared = Mode_Wavevector_Norms_Squared(lattice, kept_modes)
    assert norms_squared[origin_position] == pytest.approx(0.0, abs=1e-12)
    assert norms_squared[first_axis_unit_position] == pytest.approx(expected_squared)


def Test_Parameter_Count_Accounts_For_The_Gain_Network() -> None:
    """the built kernel's own count matches what the pricing function predicts before it is built"""
    kernel = SpectralKernel(kept_modes=(2, 1, 3), output_channels=3, input_channels=2, seed=65, metric_aware=True)
    priced = SpectralKernel.Parameter_Count_For((2, 1, 3), 3, 2, "full", metric_aware=True)
    assert kernel.Parameter_Count() == priced
    blind_priced = SpectralKernel.Parameter_Count_For((2, 1, 3), 3, 2, "full", metric_aware=False)
    assert priced > blind_priced


def Test_Inspect_Exposes_The_Gain_And_The_Renderer_Draws_Every_Key(tmp_path: Path) -> None:
    """every key Inspect publishes is shaped like what it names, and the generic renderer covers all of them"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=2, input_channels=1, seed=63, metric_aware=True)
    field = Single_Channel_Field(SHEARED, (4, 4, 4), seed=64)
    kernel.Integrate(field, GridSpec((4, 4, 4)))
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in kernel.Inspect().items()}
    assert inspected[f"{GAIN_NAME_PREFIX}_layer_0_weights"].shape == (GAIN_NETWORK_HIDDEN_WIDTH, 1)
    assert inspected[f"{GAIN_NAME_PREFIX}_layer_0_biases"].shape == (GAIN_NETWORK_HIDDEN_WIDTH,)
    assert inspected[f"{GAIN_NAME_PREFIX}_layer_1_weights"].shape == (2, GAIN_NETWORK_HIDDEN_WIDTH)
    assert inspected[f"{GAIN_NAME_PREFIX}_layer_1_biases"].shape == (2,)
    assert inspected["last_mode_gains"].shape == (3, 3, 3, 2)
    assert inspected["last_mode_wavevector_features"].shape == (3, 3, 3)
    suite = Render_Inspection_Suite(inspected, tmp_path)
    assert suite.skipped == ()


def Band_Limited_Density_And_Target(domain: Domain, seed: int) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """a random density confined to the fit's own kept modes, and its exact epsilon-regularized Poisson potential"""
    identity_kernel = SpectralKernel(POISSON_KEPT_MODES, output_channels=1, input_channels=1)
    identity_shape = identity_kernel.parameter_values["mode_weights_real"].shape
    identity_kernel.parameter_values["mode_weights_real"] = np.ones(identity_shape)
    identity_kernel.parameter_values["mode_weights_imaginary"] = np.zeros(identity_shape)
    generator = np.random.default_rng(seed)
    # zero-mean: the origin mode's gain is metric-independent and would otherwise swamp every other mode's norm
    centered_values = generator.random((1, *POISSON_GRID_SHAPE))
    centered_values = centered_values - centered_values.mean()
    raw = GridFunction(
        values=centered_values,
        channel_labels=("charge_density",),
        domain=domain,
        quadrature=UniformGridQuadrature(cell_volume=1.0, point_count=int(np.prod(POISSON_GRID_SHAPE))),
    )
    density = np.asarray(identity_kernel.Integrate(raw, GridSpec(POISSON_GRID_SHAPE)).values, dtype=np.float64)
    lattice = np.asarray(domain.lattice, dtype=np.float64)
    wavevectors = Cartesian_Wavevectors(lattice, POISSON_GRID_SHAPE)
    squared = np.sum(wavevectors**2, axis=-1)
    density_modes = np.fft.fftn(density[0])
    potential_modes = POISSON_GAIN_SCALE * density_modes / (squared + WAVEVECTOR_FEATURE_EPSILON)
    target = np.real(np.fft.ifftn(potential_modes))[None, ...]
    return density, target


def Relative_Error(produced: NDArray[np.float64], target: NDArray[np.float64]) -> float:
    """the norm of the gap over the norm of the target"""
    return float(np.linalg.norm(produced - target) / np.linalg.norm(target))


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Gain_Represents_The_Poisson_Kernel_Across_Two_Metrics_Better_Than_A_Metric_Blind_Kernel() -> None:
    """one set of weights, fit jointly, tracks 4 pi rho(k) / k_phys^2 on two differently metric'd cells"""
    domains = (POISSON_CUBE, POISSON_SHEARED)
    training_data = [Band_Limited_Density_And_Target(domain, seed=70 + domain_index)
                     for domain_index, domain in enumerate(domains)]

    aware = SpectralKernel(POISSON_KEPT_MODES, output_channels=1, input_channels=1, seed=71, metric_aware=True)
    identity_shape = aware.parameter_values["mode_weights_real"].shape
    aware.parameter_values["mode_weights_real"] = np.ones(identity_shape)
    aware.parameter_values["mode_weights_imaginary"] = np.zeros(identity_shape)
    fixed_names = {"mode_weights_real", "mode_weights_imaginary"}
    trainable_names = [name for name in aware.parameter_values if name not in fixed_names]

    engine = TorchEngine()
    fixed_lifted = {name: engine.Lift_Constant(aware.parameter_values[name]) for name in fixed_names}
    lifted_training_data: list[tuple[Any, Any, Any]] = []
    for domain, (density, target) in zip(domains, training_data):
        lattice = np.asarray(domain.lattice, dtype=np.float64)
        feature = Mode_Wavevector_Features(lattice, POISSON_KEPT_MODES)
        lifted_training_data.append(
            (engine.Lift_Constant(density), engine.Lift_Constant(target), engine.Lift_Constant(feature))
        )

    def Joint_Loss(trainable_lifted: dict[str, Any]) -> Any:
        total: Any = 0.0
        for density, target, feature in lifted_training_data:
            merged = {**fixed_lifted, **trainable_lifted, MODE_WAVEVECTOR_FEATURES_KEY: feature}
            produced = aware.Forward(merged, density, POISSON_GRID_SHAPE)
            difference = produced - target
            total = total + (difference * difference).sum()
        return total

    parameters = ParameterSet(values={name: aware.parameter_values[name].copy() for name in trainable_names})
    state = Fresh_Adam_State(parameters)
    for _ in range(400):
        _, gradients = engine.Value_And_Gradients(parameters, Joint_Loss)
        parameters = Adam_Step(parameters, gradients, state, learning_rate=0.05)
    aware.parameter_values.update(parameters.values)

    aware_errors: list[float] = []
    for domain, (density, target) in zip(domains, training_data):
        field = GridFunction(
            density, ("charge_density",), domain, UniformGridQuadrature(1.0, int(np.prod(POISSON_GRID_SHAPE)))
        )
        produced = np.asarray(aware.Integrate(field, GridSpec(POISSON_GRID_SHAPE)).values, dtype=np.float64)
        aware_errors.append(Relative_Error(produced, target))

    # the best a single per-integer-mode complex scalar can do, fit jointly, in closed form
    blind = SpectralKernel(POISSON_KEPT_MODES, output_channels=1, input_channels=1, seed=72)
    gathered_shape = blind.mode_extents
    cross_term = np.zeros(gathered_shape, dtype=np.complex128)
    power_term = np.zeros(gathered_shape, dtype=np.float64)
    for density, target in training_data:
        density_modes = blind.Gathered_Modes(Real_Fourier_Transform_3d(density), POISSON_GRID_SHAPE)[0]
        target_modes = blind.Gathered_Modes(Real_Fourier_Transform_3d(target), POISSON_GRID_SHAPE)[0]
        cross_term = cross_term + np.conj(density_modes) * target_modes
        power_term = power_term + np.abs(density_modes) ** 2
    best_weight = np.zeros(gathered_shape, dtype=np.complex128)
    nonzero = power_term > 0
    best_weight[nonzero] = cross_term[nonzero] / power_term[nonzero]
    blind.parameter_values["mode_weights_real"] = np.real(best_weight)[..., None, None]
    blind.parameter_values["mode_weights_imaginary"] = np.imag(best_weight)[..., None, None]

    blind_errors: list[float] = []
    for domain, (density, target) in zip(domains, training_data):
        field = GridFunction(
            density, ("charge_density",), domain, UniformGridQuadrature(1.0, int(np.prod(POISSON_GRID_SHAPE)))
        )
        produced = np.asarray(blind.Integrate(field, GridSpec(POISSON_GRID_SHAPE)).values, dtype=np.float64)
        blind_errors.append(Relative_Error(produced, target))

    assert max(aware_errors) < 0.1
    assert max(aware_errors) < 0.25 * min(blind_errors)

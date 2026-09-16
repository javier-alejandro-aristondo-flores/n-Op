"""the substrate facets, engine conformance and the optimizer and transforms and the seam"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.substrate import (
    ACCELERATOR_DEVICE_NAME,
    Accelerator_Is_Available,
    Adam_Step,
    Clipped_Above,
    Contract_Channel_Axis,
    CustomGradient,
    Device_Name_Of,
    Engine,
    Fourier_Transform_3d,
    Fresh_Adam_State,
    Gaussian_Error_Linear_Unit,
    Gaussian_Error_Linear_Unit_Derivative,
    HOST_DEVICE_NAME,
    Inverse_Fourier_Transform_3d,
    Largest_Singular_Values,
    Largest_Singular_Values_Of_Stack,
    MultilayerPerceptron,
    NumpyEngine,
    ParameterSet,
    Periodic_Convolution_3d,
    Preferred_Device_Name,
    Roll_Along_Axes,
    Scatter_Add,
    Singular_Values_Clipped,
    Softplus,
    Torch_Is_Available,
    TorchEngine,
)

PACKAGE_ROOT = Path(__file__).resolve().parent.parent

ENGINE_CASES = [
    pytest.param(NumpyEngine(), id="numpy_reference"),
    pytest.param(
        TorchEngine(),
        id="torch",
        marks=pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet"),
    ),
]


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_A_Parameter_The_Loss_Never_Touches_Gets_A_Zero_Gradient(engine: Engine) -> None:
    """asserts an untouched parameter comes back as zeros rather than crashing on an absent gradient"""
    parameters = ParameterSet(values={"reached": np.full(3, 2.0), "untouched": np.full(4, 5.0)})

    def Loss_Touching_One(lifted: dict[str, Any]) -> Any:
        """a loss that mentions one parameter and never the other"""
        return (lifted["reached"] * lifted["reached"]).sum()

    gradients = engine.Gradients(parameters, Loss_Touching_One)
    assert set(gradients) == {"reached", "untouched"}
    assert gradients["untouched"].shape == (4,)
    assert np.array_equal(gradients["untouched"], np.zeros(4))
    assert np.allclose(gradients["reached"], 2.0 * parameters.values["reached"])


def Quadratic_Loss(lifted: dict[str, Any]) -> Any:
    """a two-parameter quadratic with its minimum at three and minus one"""
    return ((lifted["scale"] - 3.0) ** 2).sum() + ((lifted["offset"] + 1.0) ** 2).sum()


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_Engine_Gradients_Match_The_Analytic_Quadratic(engine: Engine) -> None:
    """each engine differentiates the quadratic exactly"""
    parameters = ParameterSet(values={"scale": np.asarray([1.0]), "offset": np.asarray([2.0])})
    gradients = engine.Gradients(parameters, Quadratic_Loss)
    assert abs(float(gradients["scale"][0]) - 2.0 * (1.0 - 3.0)) < 1e-4
    assert abs(float(gradients["offset"][0]) - 2.0 * (2.0 + 1.0)) < 1e-4
    assert abs(engine.Evaluate(parameters, Quadratic_Loss) - (4.0 + 9.0)) < 1e-12


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_Adam_Descends_The_Quadratic(engine: Engine) -> None:
    """the in-house optimizer reaches the minimum on each engine"""
    parameters = ParameterSet(values={"scale": np.asarray([0.0]), "offset": np.asarray([0.0])})
    state = Fresh_Adam_State(parameters)
    for _ in range(400):
        gradients = engine.Gradients(parameters, Quadratic_Loss)
        parameters = Adam_Step(parameters, gradients, state, learning_rate=0.05)
    assert abs(float(parameters.values["scale"][0]) - 3.0) < 1e-2
    assert abs(float(parameters.values["offset"][0]) + 1.0) < 1e-2


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_Every_Engine_Works_In_Double_Until_It_Is_Asked_Otherwise(engine: Engine) -> None:
    """no engine narrows on its own, so every conformance row above still means what it meant"""
    assert engine.working_precision == "double"


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_The_Fused_Value_And_Gradients_Answers_Both_Separate_Calls(engine: Engine) -> None:
    """the loss and its gradients arrive together as the numbers each call gives on its own"""
    parameters = ParameterSet(values={"scale": np.asarray([1.0]), "offset": np.asarray([2.0])})
    value, gradients = engine.Value_And_Gradients(parameters, Quadratic_Loss)
    assert abs(value - engine.Evaluate(parameters, Quadratic_Loss)) < 1e-12
    separately = engine.Gradients(parameters, Quadratic_Loss)
    assert set(gradients) == set(separately)
    for name, gradient in gradients.items():
        assert np.allclose(gradient, separately[name], atol=1e-12)


def Cubed_Forward(arguments: tuple[Any, ...]) -> Any:
    """the one argument, cubed"""
    (value,) = arguments
    return value * value * value


def Cubed_Backward_Correct(cotangent: Any, output: Any, arguments: tuple[Any, ...]) -> tuple[Any, ...]:
    """the cube's own derivative, three times the square, carried by the cotangent"""
    (value,) = arguments
    return (cotangent * 3.0 * value * value,)


def Cubed_Backward_Missing_Factor(cotangent: Any, output: Any, arguments: tuple[Any, ...]) -> tuple[Any, ...]:
    """the correct rule with its leading factor of three dropped"""
    (value,) = arguments
    return (cotangent * value * value,)


def Backward_That_Must_Not_Run(cotangent: Any, output: Any, arguments: tuple[Any, ...]) -> tuple[Any, ...]:
    """a backward that fails the test outright if the reference engine ever reaches it"""
    raise AssertionError("the reference engine reached the declared backward instead of ignoring it")


def Analytic_Gradient_Of_The_Cubed_Loss(value: float, scale: float) -> float:
    """the closed-form derivative of the squared distance from eight through the cube of a scaled parameter"""
    transformed = scale * value
    return 2.0 * (transformed**3 - 8.0) * 3.0 * transformed**2 * scale


def Loss_Through_A_Custom_Cube(rule: CustomGradient, scale: float = 1.0) -> Callable[[dict[str, Any]], Any]:
    """the squared distance from eight, through the given rule cubing a scaled copy of the one parameter"""

    def Loss_Of(lifted: dict[str, Any]) -> Any:
        return ((rule.Apply(lifted["value"] * scale) - 8.0) ** 2).sum()

    return Loss_Of


def Test_The_Reference_Engine_Never_Reaches_The_Declared_Backward() -> None:
    """plain arrays take the forward alone, so a backward built to raise never runs"""
    rule = CustomGradient(forward=Cubed_Forward, backward=Backward_That_Must_Not_Run)
    produced = rule.Apply(np.asarray([2.0, 3.0]))
    assert np.allclose(produced, np.asarray([8.0, 27.0]))


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_A_Correct_Custom_Backward_Agrees_With_Finite_Differences() -> None:
    """the foreign engine's declared rule and the reference engine's numeric derivative land on the same number"""
    parameters = ParameterSet(values={"value": np.asarray([1.7])})
    rule = CustomGradient(forward=Cubed_Forward, backward=Cubed_Backward_Correct)
    loss = Loss_Through_A_Custom_Cube(rule)
    numeric_gradient = float(NumpyEngine().Gradients(parameters, loss)["value"][0])
    foreign_gradient = float(TorchEngine().Gradients(parameters, loss)["value"][0])
    analytic_gradient = Analytic_Gradient_Of_The_Cubed_Loss(1.7, scale=1.0)
    assert abs(foreign_gradient - numeric_gradient) < 1e-4
    assert abs(foreign_gradient - analytic_gradient) < 1e-4


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_A_Wrong_Custom_Backward_Is_Caught_Against_The_Reference() -> None:
    """a declared rule missing its leading factor is caught by disagreeing with the numeric derivative"""
    parameters = ParameterSet(values={"value": np.asarray([1.7])})
    rule = CustomGradient(forward=Cubed_Forward, backward=Cubed_Backward_Missing_Factor)
    loss = Loss_Through_A_Custom_Cube(rule)
    numeric_gradient = float(NumpyEngine().Gradients(parameters, loss)["value"][0])
    foreign_gradient = float(TorchEngine().Gradients(parameters, loss)["value"][0])
    # the dropped factor of three leaves the declared rule at a third of the true slope, never within noise
    assert abs(foreign_gradient - numeric_gradient) > 0.5 * abs(numeric_gradient)


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_Gradients_Reach_A_Parameter_Standing_Before_A_Custom_Rule(engine: Engine) -> None:
    """an ordinary rescaling before the custom node still carries a gradient back to the parameter behind it"""
    parameters = ParameterSet(values={"value": np.asarray([0.85])})
    rule = CustomGradient(forward=Cubed_Forward, backward=Cubed_Backward_Correct)
    gradient = engine.Gradients(parameters, Loss_Through_A_Custom_Cube(rule, scale=2.0))["value"]
    analytic_gradient = Analytic_Gradient_Of_The_Cubed_Loss(0.85, scale=2.0)
    assert abs(float(gradient[0]) - analytic_gradient) < 1e-3


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_A_Single_Precision_Engine_Never_Promotes_To_Double() -> None:
    """everything a narrowed engine lifts stays narrow, parameters and constants and what a network makes of them"""
    engine = TorchEngine(working_precision="single")
    network = MultilayerPerceptron(layer_widths=(3, 8, 2), name_prefix="probe", seed=5)
    lifted = engine.Lift(network.parameter_values, requires_gradient=True)
    assert {str(tensor.dtype) for tensor in lifted.values()} == {"torch.float32"}
    lifted_inputs = engine.Lift_Constant(np.zeros((4, 3)))
    assert str(lifted_inputs.dtype) == "torch.float32"
    produced = network.Forward(lifted, lifted_inputs)
    assert str(produced.dtype) == "torch.float32"
    # the hazard this design exists for: a double constant meeting the graph promotes it back, and nothing raises
    promoted = produced - TorchEngine().Lift_Constant(np.zeros((4, 2)))
    assert str(promoted.dtype) == "torch.float64"


def Forward_Devices_And_Widths(engine: TorchEngine) -> tuple[set[str], set[str]]:
    """the devices and the widths every tensor of one whole forward actually lands on"""
    network = MultilayerPerceptron(layer_widths=(3, 8, 2), name_prefix="probe", seed=5)
    lifted = engine.Lift(network.parameter_values, requires_gradient=True)
    produced = network.Forward(lifted, engine.Lift_Constant(np.zeros((4, 3))))
    reached = [*lifted.values(), produced]
    return {tensor.device.type for tensor in reached}, {str(tensor.dtype) for tensor in reached}


def Test_No_Card_Answering_Means_The_Host_Is_What_Is_Preferred() -> None:
    """asserts the preference is the card exactly when this machine has one, and the host otherwise"""
    available = Accelerator_Is_Available()
    assert Preferred_Device_Name() == (ACCELERATOR_DEVICE_NAME if available else HOST_DEVICE_NAME)
    # a machine without the foreign package has no card either, whatever else it may have
    assert not available or Torch_Is_Available()
    assert Device_Name_Of(NumpyEngine()) == HOST_DEVICE_NAME


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_A_Device_Name_Is_Obeyed_And_Not_Merely_Accepted() -> None:
    """asserts the host word keeps a whole forward on the host, which nothing would otherwise raise about"""
    engine = TorchEngine(device_name=HOST_DEVICE_NAME)
    devices, widths = Forward_Devices_And_Widths(engine)
    assert devices == {HOST_DEVICE_NAME}
    assert widths == {"torch.float64"}
    assert Device_Name_Of(engine) == HOST_DEVICE_NAME


@pytest.mark.skipif(not Accelerator_Is_Available(), reason="this machine reports no accelerator")
def Test_The_Preferred_Device_Is_Where_The_Forward_Actually_Lands() -> None:
    """asserts the preferred name is the device the graph reaches, at the narrow width it was asked for"""
    preferred = Preferred_Device_Name()
    assert preferred != HOST_DEVICE_NAME
    engine = TorchEngine(device_name=preferred, working_precision="single")
    devices, widths = Forward_Devices_And_Widths(engine)
    assert devices == {preferred}
    # the silent failure this guards: a graph that reverts to double on the card raises nothing at all
    assert widths == {"torch.float32"}
    assert Device_Name_Of(engine) == preferred


def Test_The_Nonlinearities_Have_Their_Known_Values() -> None:
    """the softplus and the smooth unit at anchor points"""
    assert abs(float(Softplus(np.asarray(0.0))) - np.log(2.0)) < 1e-12
    assert float(Gaussian_Error_Linear_Unit(np.asarray(0.0))) == 0.0
    assert abs(float(Gaussian_Error_Linear_Unit(np.asarray(3.0))) - 3.0) < 2e-2


def Test_Gaussian_Error_Linear_Unit_Derivative_Matches_Central_Differences() -> None:
    """the analytic derivative lands beside a central-difference estimate at a spread of points"""
    points = np.asarray([-2.5, -0.75, 0.0, 0.4, 1.3, 3.0])
    step_size = 1e-5
    numeric = (
        Gaussian_Error_Linear_Unit(points + step_size) - Gaussian_Error_Linear_Unit(points - step_size)
    ) / (2.0 * step_size)
    assert np.allclose(Gaussian_Error_Linear_Unit_Derivative(points), numeric, atol=1e-6)


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Gaussian_Error_Linear_Unit_Derivative_Agrees_Between_Engines() -> None:
    """the derivative lands on the same numbers whether numpy or the foreign engine carries the array"""
    points = np.asarray([-2.5, -0.75, 0.0, 0.4, 1.3, 3.0])
    reference = Gaussian_Error_Linear_Unit_Derivative(points)
    lifted = TorchEngine().Lift_Constant(points)
    produced = Gaussian_Error_Linear_Unit_Derivative(lifted)
    assert np.allclose(np.asarray(produced, dtype=np.float64), reference, atol=1e-12)


def Test_Roll_Along_Axes_Matches_Plain_Numpy() -> None:
    """the dispatched roll lands on exactly what a plain numpy roll returns"""
    generator = np.random.default_rng(40)
    values = generator.random((2, 4, 5, 6))
    reference = np.roll(values, shift=(1, -2, 3), axis=(1, 2, 3))
    assert np.allclose(Roll_Along_Axes(values, (1, -2, 3), (1, 2, 3)), reference)


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Roll_Along_Axes_Agrees_Between_Engines() -> None:
    """the periodic shift lands on the same numbers whether numpy or the foreign engine carries the array"""
    generator = np.random.default_rng(40)
    values = generator.random((2, 4, 5, 6))
    reference = Roll_Along_Axes(values, (1, -2, 3), (1, 2, 3))
    lifted = TorchEngine().Lift_Constant(values)
    produced = Roll_Along_Axes(lifted, (1, -2, 3), (1, 2, 3))
    assert np.allclose(np.asarray(produced, dtype=np.float64), reference)


def Test_Contract_Channel_Axis_Matches_Plain_Numpy() -> None:
    """the dispatched contraction lands on exactly what a plain numpy tensordot returns"""
    generator = np.random.default_rng(41)
    block = generator.random((3, 2))
    values = generator.random((2, 4, 5, 6))
    reference = np.tensordot(block, values, axes=([1], [0]))
    assert np.allclose(Contract_Channel_Axis(block, values), reference)


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Contract_Channel_Axis_Agrees_Between_Engines() -> None:
    """the channel contraction lands on the same numbers whether numpy or the foreign engine carries the arrays"""
    generator = np.random.default_rng(41)
    block = generator.random((3, 2))
    values = generator.random((2, 4, 5, 6))
    reference = Contract_Channel_Axis(block, values)
    engine = TorchEngine()
    produced = Contract_Channel_Axis(engine.Lift_Constant(block), engine.Lift_Constant(values))
    assert np.allclose(np.asarray(produced, dtype=np.float64), reference)


def Test_Scatter_Add_Matches_Plain_Numpy_Add_At() -> None:
    """the dispatched scatter lands on exactly what a plain numpy add-at returns"""
    generator = np.random.default_rng(50)
    per_edge = generator.random((6, 3))
    receiving_points = np.asarray([0, 2, 1, 2, 0, 3], dtype=np.int64)
    reference = np.zeros((4, 3))
    np.add.at(reference, receiving_points, per_edge)
    assert np.allclose(Scatter_Add(4, receiving_points, per_edge), reference)


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Scatter_Add_Gradient_Is_The_Gather_Of_The_Cotangent() -> None:
    """the torch gradient with respect to per_edge matches both the reference engine and its own closed form"""
    receiving_points = np.asarray([0, 2, 1, 2, 0, 3], dtype=np.int64)
    row_count = 4

    def Loss(lifted: dict[str, Any]) -> Any:
        accumulated = Scatter_Add(row_count, receiving_points, lifted["per_edge"])
        return (accumulated * accumulated).sum()

    generator = np.random.default_rng(51)
    parameters = ParameterSet(values={"per_edge": generator.random((6, 3))})
    numeric_gradient = NumpyEngine().Gradients(parameters, Loss)["per_edge"]
    foreign_gradient = TorchEngine().Gradients(parameters, Loss)["per_edge"]
    assert np.allclose(foreign_gradient, numeric_gradient, atol=1e-4)
    # the closed form the finite-difference check confirms: a gather of the accumulated output's own cotangent
    accumulated = Scatter_Add(row_count, receiving_points, parameters.values["per_edge"])
    expected = (2.0 * accumulated)[receiving_points]
    assert np.allclose(foreign_gradient, expected, atol=1e-8)


def Independent_Roll_And_Accumulate(values: NDArray[np.float64], stencil_weights: NDArray[np.float64]) -> Any:
    """the stencil sum written out with plain numpy roll and tensordot, independent of the dispatched facet"""
    offset_extents = stencil_weights.shape[:3]
    half_widths = tuple((extent - 1) // 2 for extent in offset_extents)
    produced = np.zeros((stencil_weights.shape[3], *values.shape[1:]))
    for offset_index in np.ndindex(offset_extents):
        shift = (
            offset_index[0] - half_widths[0],
            offset_index[1] - half_widths[1],
            offset_index[2] - half_widths[2],
        )
        shifted = np.roll(values, shift=shift, axis=(1, 2, 3))
        produced += np.tensordot(stencil_weights[offset_index], shifted, axes=([1], [0]))
    return produced


def Test_Periodic_Convolution_3d_Matches_An_Independent_Roll_And_Accumulate() -> None:
    """the numpy path lands on exactly what a hand-written roll-and-tensordot loop returns"""
    generator = np.random.default_rng(60)
    values = generator.random((2, 6, 6, 6))
    weights = generator.random((3, 3, 3, 4, 2))
    reference = Independent_Roll_And_Accumulate(values, weights)
    assert np.allclose(Periodic_Convolution_3d(values, weights), reference, atol=1e-12)


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
@pytest.mark.parametrize(
    "grid_extent,half_widths",
    [
        pytest.param(6, (1, 1, 1), id="six_cubed_symmetric"),
        pytest.param(8, (1, 1, 1), id="eight_cubed_symmetric"),
        pytest.param(8, (1, 2, 1), id="eight_cubed_asymmetric"),
    ],
)
def Test_Periodic_Convolution_3d_Agrees_Between_Engines(grid_extent: int, half_widths: tuple[int, int, int]) -> None:
    """the circular convolution lands on the same numbers as the roll-and-accumulate loop on the foreign engine"""
    offset_extents = tuple(2 * half_width + 1 for half_width in half_widths)
    generator = np.random.default_rng(61)
    values = generator.random((2, grid_extent, grid_extent, grid_extent))
    weights = generator.random((*offset_extents, 3, 2))
    reference = Periodic_Convolution_3d(values, weights)
    engine = TorchEngine()
    produced = Periodic_Convolution_3d(engine.Lift_Constant(values), engine.Lift_Constant(weights))
    assert np.allclose(np.asarray(produced, dtype=np.float64), reference, atol=1e-10)


def Loss_Through_The_Convolution_Facet(values: Any, target: Any) -> Callable[[dict[str, Any]], Any]:
    """the summed squared gap between the convolution facet's output and a fixed target"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = Periodic_Convolution_3d(values, lifted["stencil_weights"]) - target
        return (difference * difference).sum()

    return Loss


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Periodic_Convolution_3d_Gradient_Agrees_With_The_Reference_Engine() -> None:
    """the convolution facet's gradient with respect to the stencil weights matches the finite-difference oracle"""
    generator = np.random.default_rng(62)
    values = generator.random((2, 6, 6, 6))
    target = generator.random((3, 6, 6, 6))
    parameters = ParameterSet(values={"stencil_weights": generator.random((3, 3, 3, 3, 2))})
    engine = TorchEngine()
    numeric_gradient = NumpyEngine().Gradients(parameters, Loss_Through_The_Convolution_Facet(values, target))[
        "stencil_weights"
    ]
    foreign_gradient = engine.Gradients(
        parameters, Loss_Through_The_Convolution_Facet(engine.Lift_Constant(values), engine.Lift_Constant(target))
    )["stencil_weights"]
    assert np.allclose(foreign_gradient, numeric_gradient, atol=1e-4)


def Test_The_Transform_Round_Trips() -> None:
    """the three-dimensional transform inverts on the reference arrays"""
    generator = np.random.default_rng(4)
    field = generator.random((2, 6, 6, 6))
    spectrum = Fourier_Transform_3d(field)
    returned = np.real(Inverse_Fourier_Transform_3d(spectrum))
    assert np.allclose(returned, field, atol=1e-12)


def Test_Singular_Values_Clipped_Caps_The_Largest_Singular_Value() -> None:
    """no matrix in the stack carries a singular value past the ceiling once clipped"""
    generator = np.random.default_rng(70)
    stack = generator.normal(0.0, 3.0, size=(5, 4, 3))
    ceiling = 1.0
    clipped = Singular_Values_Clipped(stack, ceiling)
    assert float(Largest_Singular_Values_Of_Stack(clipped).max()) <= ceiling + 1e-8


def Test_Singular_Values_Clipped_Leaves_A_Narrow_Stack_Unchanged() -> None:
    """a stack already under the ceiling is reassembled to the numbers it started with"""
    generator = np.random.default_rng(71)
    stack = generator.normal(0.0, 0.01, size=(4, 3, 3))
    clipped = Singular_Values_Clipped(stack, ceiling=10.0)
    assert np.allclose(clipped, stack, atol=1e-12)


def Test_Singular_Values_Clipped_Is_Idempotent() -> None:
    """clipping an already-clipped stack a second time changes nothing further"""
    generator = np.random.default_rng(72)
    stack = generator.normal(0.0, 3.0, size=(5, 4, 3))
    ceiling = 1.0
    once = Singular_Values_Clipped(stack, ceiling)
    twice = Singular_Values_Clipped(once, ceiling)
    assert np.allclose(once, twice, atol=1e-8)


def Test_Singular_Values_Clipped_Preserves_A_Complex_Dtype() -> None:
    """a complex stack comes back at its own width, not promoted or demoted"""
    generator = np.random.default_rng(73)
    real_part = generator.normal(0.0, 3.0, size=(3, 3, 3))
    imaginary_part = generator.normal(0.0, 3.0, size=(3, 3, 3))
    stack = (real_part + 1j * imaginary_part).astype(np.complex64)
    clipped = Singular_Values_Clipped(stack, ceiling=1.0)
    assert clipped.dtype == np.complex64
    assert float(Largest_Singular_Values_Of_Stack(clipped).max()) <= 1.0 + 1e-4


def Test_Largest_Singular_Values_Matches_The_Reference_Helper() -> None:
    """the dispatched primitive lands on exactly what the batched numpy helper returns"""
    generator = np.random.default_rng(74)
    stack = generator.normal(0.0, 2.0, size=(4, 3, 3))
    assert np.allclose(Largest_Singular_Values(stack), Largest_Singular_Values_Of_Stack(stack))


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Largest_Singular_Values_Agrees_Between_Engines() -> None:
    """the largest singular value lands on the same number whether numpy or the foreign engine carries the stack"""
    generator = np.random.default_rng(75)
    stack = generator.normal(0.0, 2.0, size=(4, 3, 3))
    reference = Largest_Singular_Values(stack)
    lifted = TorchEngine().Lift_Constant(stack)
    produced = Largest_Singular_Values(lifted)
    assert np.allclose(np.asarray(produced, dtype=np.float64), reference, atol=1e-8)


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Largest_Singular_Values_Gradient_Agrees_With_The_Reference_Engine() -> None:
    """the torch gradient of the largest singular value matches the finite-difference oracle on one 3x3 matrix"""

    def Loss(lifted: dict[str, Any]) -> Any:
        return (Largest_Singular_Values(lifted["matrix"]) ** 2).sum()

    generator = np.random.default_rng(78)
    parameters = ParameterSet(values={"matrix": generator.normal(0.0, 1.0, size=(3, 3))})
    numeric_gradient = NumpyEngine().Gradients(parameters, Loss)["matrix"]
    foreign_gradient = TorchEngine().Gradients(parameters, Loss)["matrix"]
    assert np.allclose(foreign_gradient, numeric_gradient, atol=1e-4)


def Test_Clipped_Above_Matches_Plain_Numpy_Minimum() -> None:
    """the dispatched ceiling lands on exactly what a plain numpy minimum returns"""
    generator = np.random.default_rng(76)
    values = generator.normal(0.0, 2.0, size=(5, 5))
    assert np.allclose(Clipped_Above(values, 1.0), np.minimum(values, 1.0))


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Clipped_Above_Agrees_Between_Engines() -> None:
    """the ceiling lands on the same numbers whether numpy or the foreign engine carries the array"""
    generator = np.random.default_rng(77)
    values = generator.normal(0.0, 2.0, size=(5, 5))
    reference = Clipped_Above(values, 1.0)
    lifted = TorchEngine().Lift_Constant(values)
    produced = Clipped_Above(lifted, 1.0)
    assert np.allclose(np.asarray(produced, dtype=np.float64), reference, atol=1e-12)


def Test_The_Torch_Seam_Holds() -> None:
    """no module outside the substrate mentions the foreign engine at all"""
    for source_path in PACKAGE_ROOT.rglob("*.py"):
        parts = source_path.parts
        if ".pytest_cache" in parts or "substrate" in parts or "tests" in parts:
            continue
        assert "torch" not in source_path.read_text(), f"{source_path} mentions the foreign engine"

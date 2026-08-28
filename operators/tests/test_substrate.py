"""Checks the substrate facets: engine conformance, the optimizer, transforms, and the torch seam."""

from pathlib import Path
from typing import Any

import numpy as np
import pytest

from operators.substrate import (
    Adam_Step,
    Fresh_Adam_State,
    Fourier_Transform_3d,
    Gaussian_Error_Linear_Unit,
    Inverse_Fourier_Transform_3d,
    NumpyEngine,
    ParameterSet,
    Softplus,
    Torch_Is_Available,
    TorchEngine,
)
from operators.substrate.engine import Engine

PACKAGE_ROOT = Path(__file__).resolve().parent.parent

ENGINE_CASES = [
    pytest.param(NumpyEngine(), id="numpy_reference"),
    pytest.param(
        TorchEngine(),
        id="torch",
        marks=pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet"),
    ),
]


def Quadratic_Loss(lifted: dict[str, Any]) -> Any:
    """A two-parameter quadratic with its minimum at three and negative one."""
    return ((lifted["scale"] - 3.0) ** 2).sum() + ((lifted["offset"] + 1.0) ** 2).sum()


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_Engine_Gradients_Match_The_Analytic_Quadratic(engine: Engine) -> None:
    """Asserts each engine differentiates the quadratic exactly."""
    parameters = ParameterSet(values={"scale": np.asarray([1.0]), "offset": np.asarray([2.0])})
    gradients = engine.Gradients(parameters, Quadratic_Loss)
    assert abs(float(gradients["scale"][0]) - 2.0 * (1.0 - 3.0)) < 1e-4
    assert abs(float(gradients["offset"][0]) - 2.0 * (2.0 + 1.0)) < 1e-4
    assert abs(engine.Evaluate(parameters, Quadratic_Loss) - (4.0 + 9.0)) < 1e-12


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_Adam_Descends_The_Quadratic(engine: Engine) -> None:
    """Asserts the in-house optimizer reaches the quadratic's minimum on each engine."""
    parameters = ParameterSet(values={"scale": np.asarray([0.0]), "offset": np.asarray([0.0])})
    state = Fresh_Adam_State(parameters)
    for _ in range(400):
        gradients = engine.Gradients(parameters, Quadratic_Loss)
        parameters = Adam_Step(parameters, gradients, state, learning_rate=0.05)
    assert abs(float(parameters.values["scale"][0]) - 3.0) < 1e-2
    assert abs(float(parameters.values["offset"][0]) + 1.0) < 1e-2


def Test_The_Nonlinearities_Have_Their_Known_Values() -> None:
    """Asserts the softplus and the smooth unit at anchor points."""
    assert abs(float(Softplus(np.asarray(0.0))) - np.log(2.0)) < 1e-12
    assert float(Gaussian_Error_Linear_Unit(np.asarray(0.0))) == 0.0
    assert abs(float(Gaussian_Error_Linear_Unit(np.asarray(3.0))) - 3.0) < 2e-2


def Test_The_Transform_Round_Trips() -> None:
    """Asserts the three-dimensional transform inverts on the reference arrays."""
    generator = np.random.default_rng(4)
    field = generator.random((2, 6, 6, 6))
    spectrum = Fourier_Transform_3d(field)
    returned = np.real(Inverse_Fourier_Transform_3d(spectrum))
    assert np.allclose(returned, field, atol=1e-12)


def Test_The_Torch_Seam_Holds() -> None:
    """Asserts no module outside the substrate mentions the foreign engine at all."""
    for source_path in PACKAGE_ROOT.rglob("*.py"):
        parts = source_path.parts
        if ".pytest_cache" in parts or "substrate" in parts or "tests" in parts:
            continue
        assert "torch" not in source_path.read_text(), f"{source_path} mentions the foreign engine"

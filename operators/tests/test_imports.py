"""Checks that every package imports and that the framework's contracts hold their shape."""

import importlib
import inspect
import shutil
import subprocess
from pathlib import Path
from typing import Any, cast, is_protocol

import pytest

PACKAGES = [
    "operators",
    "operators.framework",
    "operators.kernels",
    "operators.kernels.spectral",
    "operators.kernels.compact_support",
    "operators.kernels.low_rank",
    "operators.kernels.codomain_attention",
    "operators.encoders",
    "operators.compositions",
    "operators.readouts",
    "operators.wrappers",
    "operators.data",
    "operators.inspection",
    "operators.metrics",
    "operators.tasks",
    "operators.factorized_fourier",
    "operators.alias_free_convolutional",
    "operators.deep_operator_network",
    "operators.multiple_input_operator_network",
    "operators.nonlinear_manifold_decoder",
    "operators.deep_dft",
    "operators.residual_correction",
    "operators.codomain_attention",
]

ASSEMBLIES = {
    "operators.factorized_fourier": "FactorizedFourier",
    "operators.alias_free_convolutional": "AliasFreeConvolutional",
    "operators.deep_operator_network": "DeepOperatorNetwork",
    "operators.multiple_input_operator_network": "MultipleInputOperatorNetwork",
    "operators.nonlinear_manifold_decoder": "NonlinearManifoldDecoder",
    "operators.deep_dft": "DeepDft",
    "operators.residual_correction": "ResidualCorrection",
    "operators.codomain_attention": "CodomainAttention",
}


def Test_Every_Package_Imports() -> None:
    """Imports every package listed in PACKAGES."""
    for package_name in PACKAGES:
        importlib.import_module(package_name)


def Test_The_Behavioral_Classes_Are_Protocols() -> None:
    """Asserts that the behavioral contracts are abstract protocols."""
    from operators.framework import Composition, Inspectable, Kernel, Operator

    contracts: tuple[type[Any], ...] = (Operator, Kernel, Composition, Inspectable)
    for contract in contracts:
        assert is_protocol(contract)
        assert inspect.isabstract(contract)
        with pytest.raises(TypeError):
            cast(type[object], contract)()


def Test_Representation_Has_Exactly_Three_Forms() -> None:
    """Asserts that the three function objects derive from Representation."""
    from operators.framework import Coefficients, GridFunction, PointSet, Representation

    for concrete_form in (GridFunction, PointSet, Coefficients):
        assert issubclass(concrete_form, Representation)


def Test_Each_Operator_Package_Exposes_One_Assembly() -> None:
    """Asserts that every operator package exports its assembly implementing Operator."""
    from operators.framework import Operator

    for package_name, class_name in ASSEMBLIES.items():
        module = importlib.import_module(package_name)
        assembly = getattr(module, class_name)
        assert Operator in assembly.__mro__


def Test_Every_Assembly_Carries_The_Inspection_Contract() -> None:
    """Asserts every assembly inherits Inspectable and answers Inspect."""
    from operators.framework import Inspectable

    for package_name, class_name in ASSEMBLIES.items():
        module = importlib.import_module(package_name)
        assembly = getattr(module, class_name)
        assert Inspectable in assembly.__mro__
        assert callable(getattr(assembly, "Inspect"))


def Test_The_Package_Type_Checks_Strictly() -> None:
    """Runs pyright strict over the package and fails on any error or a missing binary."""
    pyright_binary = shutil.which("pyright")
    assert pyright_binary is not None
    package_root = Path(__file__).resolve().parent.parent
    finished = subprocess.run(
        [pyright_binary, "--project", str(package_root), str(package_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert finished.returncode == 0, finished.stdout

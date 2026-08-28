"""Checks that every package imports and that the framework's contracts hold their shape."""

import ast
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
    "operators.substrate",
    "operators.tasks",
    "operators.training",
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


def Test_The_Names_Are_Prosaic() -> None:
    """Asserts no cryptic identifiers and no placeholder counters anywhere in the package."""
    allowed_short_names = {"_", "In"}
    placeholder_names = {
        "index",
        "row_index",
        "column_index",
        "item_index",
        "entry_index",
        "element_index",
        "value_index",
        "idx",
        "tmp",
        "val",
        "arr",
        "res",
        "obj",
    }
    package_root = Path(__file__).resolve().parent.parent
    offenses: list[str] = []
    for source_path in sorted(package_root.rglob("*.py")):
        if ".pytest_cache" in source_path.parts:
            continue
        tree = ast.parse(source_path.read_text())
        for node in ast.walk(tree):
            found: list[str] = []
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                found.append(node.id)
            elif isinstance(node, ast.arg):
                found.append(node.arg)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                found.append(node.name)
            elif isinstance(node, ast.TypeVar):
                found.append(node.name)
            for name in found:
                line = getattr(node, "lineno", 0)
                if len(name) <= 2 and name not in allowed_short_names:
                    offenses.append(f"{source_path.name}:{line} name {name!r}")
                elif name in placeholder_names:
                    offenses.append(f"{source_path.name}:{line} placeholder {name!r}")
    assert offenses == [], offenses


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

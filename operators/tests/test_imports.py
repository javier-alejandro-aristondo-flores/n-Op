"""every package imports, and the framework's contracts hold their shape"""

import ast
import importlib
import inspect
import io
import shutil
import subprocess
import sys
import tokenize
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
    "operators.evaluation",
    "operators.inspection.plots",
    "operators.factorized_fourier",
    "operators.alias_free_convolutional",
    "operators.deep_operator_network",
    "operators.multiple_input_operator_network",
    "operators.nonlinear_manifold_decoder",
    "operators.deep_dft",
    "operators.residual_correction",
    "operators.codomain_attention",
    "operators.galerkin_transformer",
    "operators.gaussian_plane_wave",
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
    "operators.galerkin_transformer": "GalerkinTransformer",
    "operators.gaussian_plane_wave": "GaussianPlaneWave",
}


def Test_Every_Package_Imports() -> None:
    """every package in the list, imported"""
    for package_name in PACKAGES:
        importlib.import_module(package_name)


def Test_The_Behavioral_Classes_Are_Protocols() -> None:
    """the behavioral contracts are abstract protocols"""
    from operators.framework import Composition, Inspectable, Kernel, Operator

    contracts: tuple[type[Any], ...] = (Operator, Kernel, Composition, Inspectable)
    for contract in contracts:
        assert is_protocol(contract)
        assert inspect.isabstract(contract)
        with pytest.raises(TypeError):
            cast(type[object], contract)()


def Test_Representation_Has_Exactly_Three_Forms() -> None:
    """the three function objects derive from Representation"""
    from operators.framework import Coefficients, GridFunction, PointSet, Representation

    for concrete_form in (GridFunction, PointSet, Coefficients):
        assert issubclass(concrete_form, Representation)


def Test_Each_Operator_Package_Exposes_One_Assembly() -> None:
    """every operator package exports one assembly, implementing Operator"""
    from operators.framework import Operator

    for package_name, class_name in ASSEMBLIES.items():
        module = importlib.import_module(package_name)
        assembly = getattr(module, class_name)
        assert Operator in assembly.__mro__


def Test_Every_Assembly_Carries_The_Inspection_Contract() -> None:
    """every assembly inherits Inspectable and answers Inspect"""
    from operators.framework import Inspectable

    for package_name, class_name in ASSEMBLIES.items():
        module = importlib.import_module(package_name)
        assembly = getattr(module, class_name)
        assert Inspectable in assembly.__mro__
        assert callable(getattr(assembly, "Inspect"))


def Inspection_Section(document_text: str) -> str | None:
    """the prose between an Inspection heading and the next heading, or none when there is no such heading"""
    marker = "\n## Inspection"
    start = document_text.find(marker)
    if start == -1:
        return None
    body_start = start + len(marker)
    next_heading = document_text.find("\n## ", body_start)
    return document_text[body_start:] if next_heading == -1 else document_text[body_start:next_heading]


def Test_Every_Built_Assembly_Specifies_Its_Inspection_Surface() -> None:
    """a package whose assembly no longer raises NotImplementedError on construction documents its inspection"""
    package_root = Path(__file__).resolve().parent.parent
    offenses: list[str] = []
    for package_name, class_name in ASSEMBLIES.items():
        module = importlib.import_module(package_name)
        assembly = getattr(module, class_name)
        try:
            assembly()
        except NotImplementedError:
            continue
        except Exception:
            pass
        doc_path = package_root / package_name.split(".")[-1] / "IMPLEMENTATION.md"
        section = Inspection_Section(doc_path.read_text()) if doc_path.is_file() else None
        if section is None:
            offenses.append(f"{package_name}: no Inspection heading in {doc_path.name}")
        elif len(section.strip()) < 200 or "TODO" in section or "to be written" in section:
            offenses.append(f"{package_name}: Inspection section in {doc_path.name} reads as a placeholder")
    assert offenses == [], offenses


def Test_The_Names_Are_Prosaic() -> None:
    """no cryptic identifiers and no placeholder counters, package-wide"""
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


def Test_Cross_Package_Imports_Use_The_Root() -> None:
    """imports crossing a package boundary land on an init, never on a part"""
    package_root = Path(__file__).resolve().parent.parent
    offenses: list[str] = []
    for source_path in sorted(package_root.rglob("*.py")):
        if ".pytest_cache" in source_path.parts or source_path.parent.name == "tests":
            continue
        tree = ast.parse(source_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module is not None and node.module.startswith("operators."):
                targets = [node.module]
                import_line = node.lineno
            elif isinstance(node, ast.Import):
                targets = [alias.name for alias in node.names if alias.name.startswith("operators.")]
                import_line = node.lineno
            else:
                continue
            for target in targets:
                relative = Path(*target.split(".")[1:])
                if (package_root / relative / "__init__.py").is_file():
                    continue
                part_file = package_root / relative.with_suffix(".py")
                owning_package = (package_root / relative).parent
                if part_file.is_file() and owning_package not in source_path.parents:
                    offenses.append(f"{source_path.name}:{import_line} reaches into {target}")
    assert offenses == [], offenses


def Test_The_Comments_Describe_The_Code() -> None:
    """every docstring and comment is one lowercase line, with no closing period"""
    pragma_prefixes = ("#!", "# type:", "# pyright:", "# noqa")
    package_root = Path(__file__).resolve().parent.parent
    offenses: list[str] = []
    for source_path in sorted(package_root.rglob("*.py")):
        if ".pytest_cache" in source_path.parts:
            continue
        source = source_path.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            written = ast.get_docstring(node, clean=False)
            if written is None:
                continue
            line = getattr(node, "lineno", 0)
            if "\n" in written:
                offenses.append(f"{source_path.name}:{line} docstring runs past one line")
            if written[:1].isupper():
                offenses.append(f"{source_path.name}:{line} docstring starts capitalized")
            if written.rstrip().endswith("."):
                offenses.append(f"{source_path.name}:{line} docstring ends in a period")
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type != tokenize.COMMENT or token.string.startswith(pragma_prefixes):
                continue
            written = token.string.lstrip("#").strip()
            if token.line[: token.start[1]].strip():
                offenses.append(f"{source_path.name}:{token.start[0]} comment sits beside code")
            if written[:1].isupper():
                offenses.append(f"{source_path.name}:{token.start[0]} comment starts capitalized")
            if written.endswith("."):
                offenses.append(f"{source_path.name}:{token.start[0]} comment ends in a period")
    assert offenses == [], offenses


def Type_Checker_Beside_The_Interpreter() -> Path | None:
    """the checker installed alongside the running interpreter, before any on the wider path"""
    # resolving through the path alone lets the caller's shell decide which version grades the package
    beside_interpreter = Path(sys.executable).parent / "pyright"
    if beside_interpreter.is_file():
        return beside_interpreter
    found_on_path = shutil.which("pyright")
    return Path(found_on_path) if found_on_path is not None else None


def Test_The_Package_Type_Checks_Strictly() -> None:
    """pyright strict over the package, failing on any error or a missing binary"""
    type_checker = Type_Checker_Beside_The_Interpreter()
    assert type_checker is not None, "no type checker beside the interpreter or on the path"
    package_root = Path(__file__).resolve().parent.parent
    finished = subprocess.run(
        [str(type_checker), "--project", str(package_root), str(package_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert finished.returncode == 0, f"{type_checker}\n{finished.stdout}"

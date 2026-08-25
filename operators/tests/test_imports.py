"""The scaffold's only test: everything imports, and the abstract classes are abstract.

Run from the repository root: python -m pytest operators/tests
"""

import importlib
import inspect

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


def test_every_package_imports():
    for name in PACKAGES:
        importlib.import_module(name)


def test_the_behavioral_abstract_classes_are_abstract():
    from operators.framework import Composition, Kernel, Operator

    for abstract_class in (Operator, Kernel, Composition):
        assert inspect.isabstract(abstract_class), f"{abstract_class.__name__} must be abstract"


def test_representation_is_a_behavior_free_base_with_exactly_three_forms():
    from operators.framework import Coefficients, GridFunction, PointSet, Representation

    for form in (GridFunction, PointSet, Coefficients):
        assert issubclass(form, Representation)


def test_each_operator_package_exposes_one_assembly():
    from operators.framework import Operator

    expected = {
        "operators.factorized_fourier": "FactorizedFourier",
        "operators.alias_free_convolutional": "AliasFreeConvolutional",
        "operators.deep_operator_network": "DeepOperatorNetwork",
        "operators.multiple_input_operator_network": "MultipleInputOperatorNetwork",
        "operators.nonlinear_manifold_decoder": "NonlinearManifoldDecoder",
        "operators.deep_dft": "DeepDft",
        "operators.residual_correction": "ResidualCorrection",
        "operators.codomain_attention": "CodomainAttention",
    }
    for package, class_name in expected.items():
        module = importlib.import_module(package)
        assembly = getattr(module, class_name)
        assert issubclass(assembly, Operator)

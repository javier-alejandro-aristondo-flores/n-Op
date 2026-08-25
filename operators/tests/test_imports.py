"""Checks that every package imports and that the framework's classes stay abstract."""

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


def Test_Every_Package_Imports():
    """Imports every package listed in PACKAGES."""
    for package_name in PACKAGES:
        importlib.import_module(package_name)


def Test_The_Behavioural_Classes_Are_Abstract():
    """Asserts that Operator, Kernel, and Composition cannot be instantiated."""
    from operators.framework import Composition, Kernel, Operator

    for abstract_class in (Operator, Kernel, Composition):
        assert inspect.isabstract(abstract_class)


def Test_Representation_Has_Exactly_Three_Forms():
    """Asserts that the three function objects derive from Representation."""
    from operators.framework import Coefficients, GridFunction, PointSet, Representation

    for concrete_form in (GridFunction, PointSet, Coefficients):
        assert issubclass(concrete_form, Representation)


def Test_Each_Operator_Package_Exposes_One_Assembly():
    """Asserts that every operator package exports its assembly as an Operator."""
    from operators.framework import Operator

    for package_name, class_name in ASSEMBLIES.items():
        module = importlib.import_module(package_name)
        assembly = getattr(module, class_name)
        assert issubclass(assembly, Operator)

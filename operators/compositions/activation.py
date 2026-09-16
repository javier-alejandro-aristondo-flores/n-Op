"""the activation a composition applies under the name its layer carries, handed in rather than registered"""

from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any

from operators.substrate import Gaussian_Error_Linear_Unit

type ActivationTable = Mapping[str, Callable[[Any], Any]]

POINTWISE_ACTIVATIONS: ActivationTable = MappingProxyType({"pointwise": Gaussian_Error_Linear_Unit})


def Activation_Table(handed: ActivationTable | None) -> ActivationTable:
    """the pointwise default joined with whatever a member hands its composition, the member's names winning"""
    if handed is None:
        return POINTWISE_ACTIVATIONS
    return MappingProxyType({**POINTWISE_ACTIVATIONS, **handed})


def Activated(activations: ActivationTable, name: str, summed: Any) -> Any:
    """the named activation over a layer's summed value, refusing a name the composition was never handed"""
    if name not in activations:
        raise NotImplementedError(
            f"no activation named {name!r} was handed to this composition, "
            "the alias-free one is the convolutional entry's own build and travels with its member"
        )
    return activations[name](summed)

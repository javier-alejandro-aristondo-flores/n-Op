"""which compute devices this machine has, asked of the foreign engine on the inside of the seam"""

from functools import cache
from typing import cast

from operators.substrate.engine import Engine
from operators.substrate.torch_engine import Torch_Is_Available, Torch_Module

HOST_DEVICE_NAME = "cpu"

ACCELERATOR_DEVICE_NAME = "cuda"


@cache
def Accelerator_Is_Available() -> bool:
    """whether this machine has a card the foreign engine can compute on, false when it has none"""
    if not Torch_Is_Available():
        return False
    return bool(Torch_Module().cuda.is_available())


def Preferred_Device_Name() -> str:
    """the card when this machine has one, and the host when it does not"""
    return ACCELERATOR_DEVICE_NAME if Accelerator_Is_Available() else HOST_DEVICE_NAME


def Device_Name_Of(engine: Engine) -> str:
    """the device an engine computes on, the host for one that has no notion of leaving it"""
    return cast(str, getattr(engine, "device_name", HOST_DEVICE_NAME))

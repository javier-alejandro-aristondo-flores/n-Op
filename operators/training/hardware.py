"""the card a run trains on and the width it carries, chosen by house word and recorded in the manifest"""

from functools import cache
from typing import Literal, cast

import numpy as np

from operators.substrate import Engine, Precision, TorchEngine

type DeviceChoice = Literal["automatic", "host", "accelerator"]

HOST_DEVICE_NAME = "cpu"

ACCELERATOR_DEVICE_NAME = "cuda"


@cache
def Accelerator_Is_Available() -> bool:
    """whether a card answers a trial lift, asked by making the substrate try rather than by asking a library"""
    try:
        Probe_Engine().Lift_Constant(np.zeros(1))
    except Exception:
        return False
    return True


def Probe_Engine() -> Engine:
    """an engine pointed at the card, built only to be asked whether the card is there"""
    return TorchEngine(device_name=ACCELERATOR_DEVICE_NAME)


def Resolved_Device_Name(device: DeviceChoice) -> str:
    """the house word turned into the device name the substrate engine takes"""
    if device == "host":
        return HOST_DEVICE_NAME
    if device == "accelerator":
        if not Accelerator_Is_Available():
            raise ValueError("an accelerator was asked for and no card on this machine answers")
        return ACCELERATOR_DEVICE_NAME
    return ACCELERATOR_DEVICE_NAME if Accelerator_Is_Available() else HOST_DEVICE_NAME


def Training_Engine(device: DeviceChoice = "automatic", precision: Precision = "single") -> Engine:
    """the engine a run trains on, on the card when one answers and at the width the store already holds"""
    return TorchEngine(device_name=Resolved_Device_Name(device), working_precision=precision)


def Device_Name_Of(engine: Engine) -> str:
    """the device an engine is pointed at, the host for one that never leaves it"""
    return cast(str, getattr(engine, "device_name", HOST_DEVICE_NAME))

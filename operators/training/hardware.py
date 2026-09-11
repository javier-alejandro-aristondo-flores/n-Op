"""the card a run trains on and the width it carries, chosen by house word and recorded in the manifest"""

from typing import Literal

from operators.substrate import (
    ACCELERATOR_DEVICE_NAME,
    Accelerator_Is_Available,
    Engine,
    HOST_DEVICE_NAME,
    Precision,
    Preferred_Device_Name,
    TorchEngine,
)

type DeviceChoice = Literal["automatic", "host", "accelerator"]


def Resolved_Device_Name(device: DeviceChoice) -> str:
    """the house word turned into the device name the substrate engine takes"""
    if device == "host":
        return HOST_DEVICE_NAME
    if device == "accelerator":
        if not Accelerator_Is_Available():
            raise ValueError("an accelerator was asked for and this machine reports none")
        return ACCELERATOR_DEVICE_NAME
    return Preferred_Device_Name()


def Training_Engine(device: DeviceChoice = "automatic", precision: Precision = "single") -> Engine:
    """the engine a run trains on, on the card when this machine has one and at the width the store holds"""
    return TorchEngine(device_name=Resolved_Device_Name(device), working_precision=precision)

"""Browsing the derived store: campaigns, runs, fields, shapes, and provenance."""

import json
from pathlib import Path
from typing import cast

import numpy as np
from numpy.typing import NDArray

from operators.data.store import POOL_ROOT, STORE_NAME


def List_Campaigns(pool_root: Path = POOL_ROOT) -> tuple[str, ...]:
    """Lists every campaign the store holds a manifest for."""
    store = pool_root / STORE_NAME
    if not store.exists():
        return ()
    return tuple(sorted(entry.name for entry in store.iterdir() if (entry / "manifest.json").is_file()))


def Read_Manifest(campaign: str, pool_root: Path = POOL_ROOT) -> dict[str, dict[str, object]]:
    """Reads one campaign manifest mapping identifiers to their entries."""
    manifest_path = pool_root / STORE_NAME / campaign / "manifest.json"
    return cast(dict[str, dict[str, object]], json.loads(manifest_path.read_text()))


def List_Runs(campaign: str, pool_root: Path = POOL_ROOT) -> tuple[str, ...]:
    """Lists the run identifiers of one campaign."""
    return tuple(sorted(Read_Manifest(campaign, pool_root)))


def Find_Runs(path_fragment: str, pool_root: Path = POOL_ROOT) -> tuple[tuple[str, str], ...]:
    """Finds runs whose corpus path contains the fragment, as campaign and identifier pairs."""
    found: list[tuple[str, str]] = []
    for campaign in List_Campaigns(pool_root):
        for identifier, entry in Read_Manifest(campaign, pool_root).items():
            if path_fragment in cast(str, entry["run_path"]):
                found.append((campaign, identifier))
    return tuple(sorted(found))


def Describe_Run(campaign: str, identifier: str, pool_root: Path = POOL_ROOT) -> dict[str, object]:
    """Returns a run's sidecar record with the shape of every stored array added."""
    base = pool_root / STORE_NAME / campaign / identifier
    sidecar = cast(dict[str, object], json.loads(base.with_suffix(".json").read_text()))
    shapes: dict[str, list[int]] = {}
    with np.load(base.with_suffix(".npz")) as archive:
        for name in archive.files:
            shapes[name] = list(archive[name].shape)
    sidecar["shapes"] = shapes
    return sidecar


def Load_Run_Field(
    campaign: str, identifier: str, name: str, pool_root: Path = POOL_ROOT
) -> NDArray[np.float64] | NDArray[np.str_]:
    """Loads one named array of one run, numeric arrays as float64."""
    base = pool_root / STORE_NAME / campaign / identifier
    with np.load(base.with_suffix(".npz")) as archive:
        value = archive[name]
        if value.dtype.kind in ("U", "S"):
            return np.asarray(value, dtype=np.str_)
        return np.asarray(value, dtype=np.float64)

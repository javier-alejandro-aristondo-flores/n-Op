"""browsing the derived store, campaigns and runs and fields and provenance"""

import json
from pathlib import Path
from typing import cast

import numpy as np
from numpy.typing import NDArray

from operators.data import Archive_Path, POOL_ROOT, STORE_NAME


def List_Campaigns(pool_root: Path = POOL_ROOT) -> tuple[str, ...]:
    """every campaign the store holds a manifest for"""
    store = pool_root / STORE_NAME
    if not store.exists():
        return ()
    return tuple(sorted(entry.name for entry in store.iterdir() if (entry / "manifest.json").is_file()))


def Read_Manifest(campaign: str, pool_root: Path = POOL_ROOT) -> dict[str, dict[str, object]]:
    """one campaign manifest, identifiers to their entries"""
    manifest_path = pool_root / STORE_NAME / campaign / "manifest.json"
    return cast(dict[str, dict[str, object]], json.loads(manifest_path.read_text()))


def List_Runs(campaign: str, pool_root: Path = POOL_ROOT) -> tuple[str, ...]:
    """the run identifiers of one campaign"""
    return tuple(sorted(Read_Manifest(campaign, pool_root)))


def Find_Runs(path_fragment: str, pool_root: Path = POOL_ROOT) -> tuple[tuple[str, str], ...]:
    """runs whose corpus path contains the fragment, as campaign and identifier"""
    found: list[tuple[str, str]] = []
    for campaign in List_Campaigns(pool_root):
        for identifier, entry in Read_Manifest(campaign, pool_root).items():
            if path_fragment in cast(str, entry["run_path"]):
                found.append((campaign, identifier))
    return tuple(sorted(found))


def Describe_Run(campaign: str, identifier: str, pool_root: Path = POOL_ROOT) -> dict[str, object]:
    """a run's sidecar record, with the shape of every stored array added"""
    archive_path = Archive_Path(campaign, identifier, pool_root)
    sidecar = cast(dict[str, object], json.loads(archive_path.with_suffix(".json").read_text()))
    shapes: dict[str, list[int]] = {}
    with np.load(archive_path) as archive:
        for name in archive.files:
            shapes[name] = list(archive[name].shape)
    sidecar["shapes"] = shapes
    return sidecar


def Load_Run_Field(
    campaign: str, identifier: str, name: str, pool_root: Path = POOL_ROOT
) -> NDArray[np.float64] | NDArray[np.str_]:
    """one named array of one run, numbers in double precision"""
    with np.load(Archive_Path(campaign, identifier, pool_root)) as archive:
        value = archive[name]
        # the species array holds text, and text does not convert to a number
        if value.dtype.kind in ("U", "S"):
            return np.asarray(value, dtype=np.str_)
        return np.asarray(value, dtype=np.float64)

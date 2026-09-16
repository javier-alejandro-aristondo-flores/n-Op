"""per-atom (element, pseudopotential title) keys, the unknown row and the structure loader"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import numpy as np
from numpy.typing import NDArray

from operators.data import Archive_Path, POOL_ROOT

UNKNOWN_ELEMENT = "unknown"

UNKNOWN_TITLE = "unknown"

UNKNOWN_SPECIES_KEY = (UNKNOWN_ELEMENT, UNKNOWN_TITLE)


def Stripped_Element(title: str) -> str:
    """the title's second token with any paw-style suffix removed"""
    element_token = title.split()[1]
    return element_token.split("_")[0]


def Title_By_Element(titles: tuple[str, ...]) -> dict[str, str]:
    """the first title seen for each element the titles name"""
    resolved: dict[str, str] = {}
    for title in titles:
        element = Stripped_Element(title)
        resolved.setdefault(element, title)
    return resolved


def Species_Keys_Of(species_symbols: tuple[str, ...], titles: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    """one (element, title) key per atom, the unknown key standing in where no title matches"""
    title_by_element = Title_By_Element(titles)
    return tuple(
        (symbol, title_by_element[symbol]) if symbol in title_by_element else UNKNOWN_SPECIES_KEY
        for symbol in species_symbols
    )


@dataclass(frozen=True, slots=True)
class Structure:
    """one run's atomic configuration, ready for the encoder and the message-passing stack"""

    identifier: str
    campaign: str
    lattice: NDArray[np.float64]
    positions: NDArray[np.float64]
    species_symbols: tuple[str, ...]
    species_keys: tuple[tuple[str, str], ...]
    electron_count: float


def Structure_From_Archive(
    identifier: str, campaign: str, archive: "np.lib.npyio.NpzFile", titles: tuple[str, ...]
) -> Structure:
    """the structure one archive and its sidecar titles describe"""
    species_symbols = tuple(str(symbol) for symbol in archive["species"])
    return Structure(
        identifier=identifier,
        campaign=campaign,
        lattice=np.asarray(archive["lattice"], dtype=np.float64),
        positions=np.asarray(archive["positions"], dtype=np.float64),
        species_symbols=species_symbols,
        species_keys=Species_Keys_Of(species_symbols, titles),
        electron_count=float(np.asarray(archive["electron_count"])),
    )


def Loaded_Structure(campaign: str, identifier: str, pool_root: Path = POOL_ROOT) -> Structure | None:
    """one run's structure read off the store, or nothing when the archive lacks what it needs"""
    archive_path = Archive_Path(campaign, identifier, pool_root)
    if not archive_path.exists():
        return None
    with np.load(archive_path) as archive:
        if "positions" not in archive or "species" not in archive or "electron_count" not in archive:
            return None
        sidecar = json.loads(archive_path.with_suffix(".json").read_text())
        titles = tuple(cast(list[str], sidecar.get("pseudopotential_titles", [])))
        return Structure_From_Archive(identifier, campaign, archive, titles)


def Training_Vocabulary(structures: tuple[Structure, ...]) -> tuple[tuple[str, str], ...]:
    """every distinct (element, title) key the given structures carry, sorted, the unknown key appended"""
    seen: set[tuple[str, str]] = set()
    for structure in structures:
        seen.update(structure.species_keys)
    seen.discard(UNKNOWN_SPECIES_KEY)
    return tuple(sorted(seen)) + (UNKNOWN_SPECIES_KEY,)


@dataclass(frozen=True, slots=True)
class SpeciesKeys:
    """the training vocabulary, and the map from any run's own keys onto it"""

    vocabulary: tuple[tuple[str, str], ...]


    def Resolved(self, species_keys: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
        """every key the vocabulary holds unchanged, and every other key sent to the unknown row"""
        known = set(self.vocabulary)
        return tuple(key if key in known else UNKNOWN_SPECIES_KEY for key in species_keys)


    def Held_Out_Chemistry(self, structure: Structure) -> bool:
        """whether this structure carries an element the vocabulary's own training run never saw"""
        known_elements = {element for element, _ in self.vocabulary}
        return not set(structure.species_symbols).issubset(known_elements)


def Relabeled_Species_Keys(
    species_keys: tuple[tuple[str, str], ...], relabel_probability: float, generator: np.random.Generator
) -> tuple[tuple[str, str], ...]:
    """every key with a chance of standing in for the unknown row, so training touches it too"""
    draws = generator.random(len(species_keys))
    return tuple(
        UNKNOWN_SPECIES_KEY if draw < relabel_probability else key for key, draw in zip(species_keys, draws)
    )

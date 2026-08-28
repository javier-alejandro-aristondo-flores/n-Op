"""Readers for the corpus's VASP text files, returning typed NumPy records."""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


class ParseError(Exception):
    """Raised when a corpus file deviates from the format the reader expects."""


@dataclass(frozen=True, slots=True)
class Geometry:
    """A periodic cell with its species, per-species counts, and fractional positions."""

    comment: str
    lattice: NDArray[np.float64]
    species: tuple[str, ...]
    species_counts: tuple[int, ...]
    positions: NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class FieldFile:
    """The grid blocks of one volumetric file, raw values in file units."""

    geometry: Geometry
    dimensions: tuple[int, int, int]
    blocks: tuple[NDArray[np.float64], ...]


@dataclass(frozen=True, slots=True)
class EigenvalueSet:
    """Eigenvalues and occupancies indexed by spin, k-point, and band."""

    electron_count: float
    kpoints: NDArray[np.float64]
    kpoint_weights: NDArray[np.float64]
    energies: NDArray[np.float64]
    occupancies: NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class OutcarEchoes:
    """Scalars echoed by OUTCAR: electron count and pseudopotential titles."""

    electron_count: float
    pseudopotential_titles: tuple[str, ...]


def Cell_Volume(lattice: NDArray[np.float64]) -> float:
    """Returns the absolute determinant of the lattice rows in cubic angstrom."""
    return float(abs(np.linalg.det(lattice)))


def Read_Geometry(lines: Sequence[str], start: int = 0) -> tuple[Geometry, int]:
    """Reads one POSCAR-style header and returns it with the index of the next line."""
    comment = lines[start].strip()
    scale = float(lines[start + 1].split()[0])
    lattice_rows = [[float(token) for token in lines[start + 2 + row_index].split()[:3]] for row_index in range(3)]
    lattice = np.asarray(lattice_rows, dtype=np.float64)
    if scale < 0.0:
        scale = (-scale / float(abs(np.linalg.det(lattice)))) ** (1.0 / 3.0)
    lattice = lattice * scale
    species = tuple(lines[start + 5].split())
    species_counts = tuple(int(token) for token in lines[start + 6].split())
    cursor = start + 7
    if lines[cursor].strip().lower().startswith("s"):
        cursor += 1
    mode = lines[cursor].strip().lower()
    cursor += 1
    total = sum(species_counts)
    coordinate_rows = [[float(token) for token in lines[cursor + position_index].split()[:3]] for position_index in range(total)]
    positions = np.asarray(coordinate_rows, dtype=np.float64)
    if mode.startswith(("c", "k")):
        positions = positions @ np.linalg.inv(lattice)
    return Geometry(comment, lattice, species, species_counts, positions), cursor + total


def Grid_Dimensions_On_Line(line: str) -> tuple[int, int, int] | None:
    """Returns the line's three integer grid dimensions, or None for any other line."""
    tokens = line.split()
    if len(tokens) != 3 or not all(token.isdigit() for token in tokens):
        return None
    return int(tokens[0]), int(tokens[1]), int(tokens[2])


def Read_Grid_Block(lines: Sequence[str], start: int, value_count: int) -> tuple[NDArray[np.float64], int]:
    """Reads value_count whitespace-separated floats beginning at the start line."""
    first_width = len(lines[start].split())
    if first_width == 0:
        raise ParseError(f"empty line where grid data was expected at line {start + 1}")
    line_count = -(-value_count // first_width)
    tokens = " ".join(lines[start : start + line_count]).split()
    if len(tokens) < value_count:
        raise ParseError(f"grid block at line {start + 1} holds {len(tokens)} of {value_count} values")
    values = np.asarray(tokens[:value_count], dtype=np.float64)
    return values, start + line_count


def Read_Field_File(path: Path) -> FieldFile:
    """Reads a CHGCAR-family volumetric file into its geometry and grid blocks."""
    lines = path.read_text().splitlines()
    geometry, cursor = Read_Geometry(lines)
    dimensions: tuple[int, int, int] | None = None
    blocks: list[NDArray[np.float64]] = []
    while cursor < len(lines):
        found = Grid_Dimensions_On_Line(lines[cursor])
        if found is None or (dimensions is not None and found != dimensions):
            cursor += 1
            continue
        dimensions = found
        count = dimensions[0] * dimensions[1] * dimensions[2]
        flat, cursor = Read_Grid_Block(lines, cursor + 1, count)
        blocks.append(flat.reshape((dimensions[2], dimensions[1], dimensions[0])).transpose(2, 1, 0))
    if dimensions is None or not blocks:
        raise ParseError(f"no grid block found in {path}")
    return FieldFile(geometry, dimensions, tuple(blocks))


def Read_Eigenvalues(path: Path) -> EigenvalueSet:
    """Reads EIGENVAL into per-spin, per-k-point, per-band energies and occupancies."""
    lines = path.read_text().splitlines()
    spin_count = int(lines[0].split()[3])
    header = lines[5].split()
    electron_count = float(header[0])
    kpoint_count = int(header[1])
    band_count = int(header[2])
    kpoints = np.zeros((kpoint_count, 3), dtype=np.float64)
    kpoint_weights = np.zeros(kpoint_count, dtype=np.float64)
    energies = np.zeros((spin_count, kpoint_count, band_count), dtype=np.float64)
    occupancies = np.zeros((spin_count, kpoint_count, band_count), dtype=np.float64)
    cursor = 6
    for kpoint_index in range(kpoint_count):
        while lines[cursor].strip() == "":
            cursor += 1
        kpoint_tokens = lines[cursor].split()
        kpoints[kpoint_index] = [float(token) for token in kpoint_tokens[:3]]
        kpoint_weights[kpoint_index] = float(kpoint_tokens[3])
        cursor += 1
        for band_index in range(band_count):
            row = lines[cursor].split()
            for spin_index in range(spin_count):
                energies[spin_index, kpoint_index, band_index] = float(row[1 + spin_index])
                occupancies[spin_index, kpoint_index, band_index] = float(row[1 + spin_count + spin_index])
            cursor += 1
    return EigenvalueSet(electron_count, kpoints, kpoint_weights, energies, occupancies)


def Read_Outcar_Echoes(path: Path) -> OutcarEchoes:
    """Reads the NELECT echo and the pseudopotential titles from OUTCAR."""
    electron_count: float | None = None
    titles: list[str] = []
    with path.open() as stream:
        for line in stream:
            if "TITEL" in line:
                titles.append(line.split("=", 1)[1].strip())
            elif "NELECT" in line and electron_count is None:
                electron_count = float(line.split()[2])
    if electron_count is None:
        raise ParseError(f"no NELECT echo in {path}")
    return OutcarEchoes(electron_count, tuple(dict.fromkeys(titles)))


def Read_Final_Magnetization(path: Path) -> float | None:
    """Reads the last per-step magnetization from OSZICAR, or None when absent."""
    magnetization: float | None = None
    with path.open() as stream:
        for line in stream:
            if "mag=" in line:
                magnetization = float(line.rsplit("mag=", 1)[1].split()[0])
    return magnetization

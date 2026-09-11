"""the periodic geometry a cutoff needs, cell heights and the images they admit"""

from dataclasses import dataclass
from math import ceil, floor

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class RadiusGraph:
    """the edges inside a cutoff, one entry per receiving point, sending point and image"""

    receiving_points: NDArray[np.int64]
    sending_points: NDArray[np.int64]
    distances: NDArray[np.float64]
    displacements: NDArray[np.float64]


def Cell_Heights(lattice: NDArray[np.float64]) -> NDArray[np.float64]:
    """perpendicular distance between the two faces each lattice direction crosses"""
    volume = float(abs(np.linalg.det(lattice)))
    heights: list[float] = []
    for crossed_direction in range(3):
        spanning = [other_direction for other_direction in range(3) if other_direction != crossed_direction]
        face_area = float(np.linalg.norm(np.cross(lattice[spanning[0]], lattice[spanning[1]])))
        heights.append(volume / face_area)
    return np.asarray(heights, dtype=np.float64)


def Image_Reach(lattice: NDArray[np.float64], cutoff_radius: float) -> tuple[int, int, int]:
    """how many whole cells a folded displacement can still reach along each direction"""
    # a cutoff crosses the height between faces, which a sheared cell makes shorter than the vector
    spans = [int(ceil(cutoff_radius / float(height))) for height in Cell_Heights(lattice)]
    return spans[0], spans[1], spans[2]


def Lattice_Images(reach: tuple[int, int, int]) -> NDArray[np.float64]:
    """every whole-cell translation inside the reach, as fractional triples"""
    axes = [np.arange(-span, span + 1, dtype=np.float64) for span in reach]
    grids = np.meshgrid(*axes, indexing="ij")
    return np.stack([np.asarray(grid).reshape(-1) for grid in grids], axis=1)


def Vector_Lengths(displacements: NDArray[np.float64]) -> NDArray[np.float64]:
    """the Cartesian length of every displacement carried in the last axis"""
    return np.sqrt((displacements**2).sum(axis=-1))


def Folded_Fractional_Gaps(
    target_points: NDArray[np.float64], source_points: NDArray[np.float64]
) -> NDArray[np.float64]:
    """every target-minus-source fractional gap, folded into the unit box around zero"""
    gaps = target_points[:, None, :] - source_points[None, :, :]
    # subtracting the nearest whole cell is the fold onto the torus
    return np.asarray(gaps - np.round(gaps), dtype=np.float64)


def Periodic_Radius_Graph(
    target_points: NDArray[np.float64],
    source_points: NDArray[np.float64],
    lattice: NDArray[np.float64],
    cutoff_radius: float,
) -> RadiusGraph:
    """every pair and image whose Cartesian separation falls inside the cutoff"""
    folded = Folded_Fractional_Gaps(target_points, source_points)
    receiving: list[NDArray[np.int64]] = []
    sending: list[NDArray[np.int64]] = []
    separations: list[NDArray[np.float64]] = []
    lengths: list[NDArray[np.float64]] = []
    for image in Lattice_Images(Image_Reach(lattice, cutoff_radius)):
        displacement = (folded + image) @ lattice
        length = Vector_Lengths(displacement)
        inside = length <= cutoff_radius
        found_receiving, found_sending = np.nonzero(inside)
        receiving.append(np.asarray(found_receiving, dtype=np.int64))
        sending.append(np.asarray(found_sending, dtype=np.int64))
        separations.append(displacement[inside])
        lengths.append(length[inside])
    return RadiusGraph(
        receiving_points=np.concatenate(receiving),
        sending_points=np.concatenate(sending),
        distances=np.concatenate(lengths),
        displacements=np.concatenate(separations),
    )


def Offset_Reach(
    lattice: NDArray[np.float64], shape: tuple[int, int, int], cutoff_radius: float
) -> tuple[int, int, int]:
    """the stencil half-width, in whole voxels, that a cutoff radius reaches on a grid"""
    # a voxel step along a direction crosses that direction's height divided by the extent
    spans = [
        floor(cutoff_radius * extent / float(height))
        for extent, height in zip(shape, Cell_Heights(lattice))
    ]
    return spans[0], spans[1], spans[2]


def Grid_Offsets(half_widths: tuple[int, int, int]) -> NDArray[np.int64]:
    """every whole-voxel offset the stencil box holds, in the order its weights are stored"""
    axes = [np.arange(-span, span + 1, dtype=np.int64) for span in half_widths]
    grids = np.meshgrid(*axes, indexing="ij")
    return np.stack([np.asarray(grid).reshape(-1) for grid in grids], axis=1)


def Voxel_Indices(fractional_points: NDArray[np.float64], shape: tuple[int, int, int]) -> NDArray[np.int64]:
    """the whole-voxel position each fractional grid coordinate names"""
    scaled = np.asarray(fractional_points, dtype=np.float64) * np.asarray(shape, dtype=np.float64)
    return np.asarray(np.rint(scaled), dtype=np.int64)

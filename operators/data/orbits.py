"""The strain-atlas orbit map: exact symmetry classes of the two-atom strain points."""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from itertools import permutations, product
from typing import cast

from operators.data.store import Campaign_Of, CensusRow

AXIS_INDEX = {"x": 0, "y": 1, "z": 2}

type StrainTensor = tuple[float, float, float, float, float, float]


class OrbitError(Exception):
    """Raised when a strain-atlas run path cannot be interpreted."""


@dataclass(frozen=True, slots=True)
class StrainAssignment:
    """One strain-atlas run resolved to its point, family, functional, and orbit."""

    run_path: str
    point: str
    family: str
    functional: str
    auxiliary: bool
    orbit: str


def Strain_Functional(path: str) -> str:
    """Names the run's functional from its last path segment."""
    return "accurate" if "HSE" in path.rsplit("/", 1)[-1] else "cheap"


def Strain_Point_Name(path: str) -> str:
    """Returns the point directory naming the strain applied."""
    segments = path.split("/")
    return "reference" if "reference_2_atoms" in path else segments[-2]


def Strain_Family(point: str) -> str:
    """Classifies a point name into its sweep family."""
    if point == "reference":
        return "reference"
    if point.startswith("uniax_"):
        return "uniaxial"
    if point.startswith("biax_"):
        return "biaxial"
    if point.startswith("Vol_"):
        return "isotropic"
    if point.startswith("vol_"):
        return "triaxial"
    if point.startswith("shear_3D_"):
        return "three_angle_shear"
    if point.startswith("shear_") and "_g1_" in point:
        return "two_angle_shear"
    if point.startswith("shear_"):
        return "one_angle_shear"
    raise OrbitError(f"unrecognized strain point {point}")


def Strain_Tensor_Of(point: str, isotropic_strain: float | None) -> StrainTensor:
    """Builds the six-component strain tensor a point name encodes."""
    family = Strain_Family(point)
    diagonal = [0.0, 0.0, 0.0]
    shear = {"xy": 0.0, "xz": 0.0, "yz": 0.0}
    if family == "reference":
        pass
    elif family == "isotropic":
        if isotropic_strain is None:
            raise OrbitError(f"isotropic point {point} needs a lattice-derived strain")
        diagonal = [isotropic_strain] * 3
    elif family == "uniaxial":
        axis, value = point.removeprefix("uniax_").split("_eps")
        diagonal[AXIS_INDEX[axis]] = float(value)
    elif family == "biaxial":
        pair, value = point.removeprefix("biax_").split("_eps")
        for axis in pair:
            diagonal[AXIS_INDEX[axis]] = float(value)
    elif family == "triaxial":
        tokens = point.split("_ex_")[1].replace("_ey_", " ").replace("_ez_", " ").split()
        diagonal = [float(token) for token in tokens]
    elif family == "one_angle_shear":
        pair, value = point.removeprefix("shear_").split("_g")
        shear[pair] = float(value)
    elif family == "two_angle_shear":
        first_pair, remainder = point.removeprefix("shear_").split("_", 1)
        second_pair, values = remainder.split("_g1_")
        first_value, second_value = values.split("_g2_")
        shear[first_pair] = float(first_value)
        shear[second_pair] = float(second_value)
    elif family == "three_angle_shear":
        tokens = point.split("_g1_")[1].replace("_g2_", " ").replace("_g3_", " ").split()
        shear = {"xy": float(tokens[0]), "xz": float(tokens[1]), "yz": float(tokens[2])}
    return (diagonal[0], diagonal[1], diagonal[2], shear["xy"], shear["xz"], shear["yz"])


def Tensor_Images(tensor: StrainTensor) -> Iterator[StrainTensor]:
    """Yields the tensor's images under the 48 signed axis permutations."""
    matrix = [
        [tensor[0], tensor[3], tensor[4]],
        [tensor[3], tensor[1], tensor[5]],
        [tensor[4], tensor[5], tensor[2]],
    ]
    for permutation in permutations((0, 1, 2)):
        for signs in product((1.0, -1.0), repeat=3):
            image = [
        [
            signs[row_index] * signs[column_index] * matrix[permutation[row_index]][permutation[column_index]]
            for column_index in range(3)
        ]
        for row_index in range(3)
    ]
            yield (image[0][0], image[1][1], image[2][2], image[0][1], image[0][2], image[1][2])


def Rounded(tensor: StrainTensor) -> StrainTensor:
    """Rounds every component to four decimals and normalizes negative zero."""
    values = tuple(round(component, 4) + 0.0 for component in tensor)
    return cast(StrainTensor, values)


def Canonical_Orbit(tensor: StrainTensor) -> str:
    """Formats the lexicographically largest signed-permutation image of the tensor."""
    canonical = max(Rounded(image) for image in Tensor_Images(Rounded(tensor)))
    return "_".join(f"{component:+.4f}" for component in canonical)


def Reference_Axis_Length(census_rows: Sequence[CensusRow]) -> float:
    """Reads the unstrained axis length from the reference runs' census geometry."""
    for census_row in census_rows:
        if "reference_2_atoms" in census_row.path:
            return cast(list[float], census_row.record["p_abc"])[0]
    raise OrbitError("no reference run in the census rows")


def Orbit_Map(census_rows: Sequence[CensusRow]) -> tuple[StrainAssignment, ...]:
    """Assigns every strain-atlas run to its point, family, functional, and orbit."""
    strain_rows = [census_row for census_row in census_rows if Campaign_Of(census_row.path) == "strain_atlas"]
    reference_length = Reference_Axis_Length(strain_rows)
    assignments: list[StrainAssignment] = []
    for census_row in strain_rows:
        point = Strain_Point_Name(census_row.path)
        isotropic_strain: float | None = None
        if Strain_Family(point) == "isotropic":
            axis_length = cast(list[float], census_row.record["p_abc"])[0]
            isotropic_strain = round(axis_length / reference_length - 1.0, 4)
        tensor = Strain_Tensor_Of(point, isotropic_strain)
        assignments.append(
            StrainAssignment(
                run_path=census_row.path,
                point=point,
                family=Strain_Family(point),
                functional=Strain_Functional(census_row.path),
                auxiliary="/new/" in census_row.path,
                orbit=Canonical_Orbit(tensor),
            )
        )
    return tuple(assignments)

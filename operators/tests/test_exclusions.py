"""every exclusion resolves to its recorded count on the live census"""

import pytest

from operators.data import Campaign_Of, POOL_ROOT, Read_Byte_Alias_Groups, Read_Census, Resolve_Exclusion


@pytest.mark.pool
def Test_The_Exclusion_Counts_Match_The_Registry() -> None:
    """each cheap-to-resolve exclusion names exactly its recorded runs"""
    census_rows = Read_Census(POOL_ROOT)
    expected = {"E1": 6, "E2": 1, "E3": 1, "E4": 1, "E5": 1, "E6": 73, "E7": 4, "E9": 12, "E10": 1}
    for identifier, count in expected.items():
        resolved = Resolve_Exclusion(identifier, census_rows, POOL_ROOT)
        assert len(resolved) == count, f"{identifier}: {len(resolved)} != {count}: {resolved[:4]}"


@pytest.mark.pool
def Test_The_Fractional_Occupancy_Counts_Match() -> None:
    """the perovskite fractional-occupancy flags split 106 angle and 22 length"""
    census_rows = Read_Census(POOL_ROOT)
    flagged = Resolve_Exclusion("E8", census_rows, POOL_ROOT)
    angle = sum(1 for path in flagged if "angle_distortions" in path)
    length = sum(1 for path in flagged if "length_distortions" in path)
    assert (angle, length) == (106, 22), (angle, length)


@pytest.mark.pool
def Test_The_Byte_Alias_Triples_Count_Twenty_Four() -> None:
    """the strain atlas holds exactly twenty-four byte-alias triples"""
    groups = Read_Byte_Alias_Groups(POOL_ROOT)
    strain_triples = [
        group
        for group in groups
        if len(group) == 3 and all(Campaign_Of(member) == "strain_atlas" for member in group)
    ]
    assert len(strain_triples) == 24

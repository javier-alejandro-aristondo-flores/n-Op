"""the split engine's units, folds and artifacts against the recorded structure"""

from collections import Counter

import pytest

from operators.data import (
    Fold_Assignment,
    POOL_ROOT,
    Paired_Fields_Units,
    Read_Census,
    Regenerated_Artifacts_Match,
    SplitUnit,
    Strain_Holdout_Assignment,
    Twin_Shear_Map,
)
from operators.data.splits import Alloy_Units, Defect_Units, Hard_Excluded_Paths, Stable_Fraction, Supercell_Units


def Require_The_Pool() -> None:
    """fails the calling test when the corpus partition is not mounted"""
    if not POOL_ROOT.exists():
        pytest.fail("the corpus at /Pool/VASP_DATA is not mounted on this machine")


def Has_Both_Functionals(unit: SplitUnit) -> bool:
    """whether a unit holds at least one cheap and one accurate run"""
    accurate = any("hse" in path.lower() for path in unit.run_paths)
    cheap = any("hse" not in path.lower() for path in unit.run_paths)
    return accurate and cheap


def Test_Stable_Fractions_Are_Deterministic_And_Distinct() -> None:
    """the seeded hash is reproducible, and separates keys"""
    assert Stable_Fraction("a") == Stable_Fraction("a")
    assert Stable_Fraction("a") != Stable_Fraction("b")
    assert 0.0 <= Stable_Fraction("anything") < 1.0


def Test_Fold_Assignment_Balances_Within_Strata() -> None:
    """synthetic units spread evenly over the five folds"""
    units = [SplitUnit(f"unit_{unit_number}", "campaign", "stratum", (f"run_{unit_number}",)) for unit_number in range(10)]
    folds = Fold_Assignment(units)
    counts = Counter(folds.values())
    assert sorted(counts) == [0, 1, 2, 3, 4]
    assert all(count == 2 for count in counts.values())


@pytest.mark.pool
def Test_The_Defect_Pairing_Matches_The_Record() -> None:
    """56 chained pairs, 37 new-only pairs, zirconium alone unpaired"""
    Require_The_Pool()
    census_rows = Read_Census(POOL_ROOT)
    units = Defect_Units(census_rows, Hard_Excluded_Paths(census_rows, POOL_ROOT))
    chained = [unit for unit in units if unit.stratum in ("single", "pair", "triads")]
    new_only = [unit for unit in units if unit.stratum == "new_only"]
    assert len(chained) == 56 and all(Has_Both_Functionals(unit) for unit in chained)
    assert len(new_only) == 38 and sum(map(Has_Both_Functionals, new_only)) == 37
    unpaired = [unit.key for unit in units if not Has_Both_Functionals(unit)]
    assert unpaired == ["defect_new_only_Transition-Metals_Zr"]
    assert sum(len(unit.run_paths) for unit in units) == 189


@pytest.mark.pool
def Test_The_Alloy_Units_Cover_The_Ensemble() -> None:
    """76 configuration units over all 182 runs, in the measured pattern"""
    Require_The_Pool()
    census_rows = Read_Census(POOL_ROOT)
    units = Alloy_Units(census_rows, Hard_Excluded_Paths(census_rows, POOL_ROOT))
    assert len(units) == 76
    assert sum(len(unit.run_paths) for unit in units) == 182
    sizes = Counter(len(unit.run_paths) for unit in units)
    assert sizes == Counter({1: 67, 19: 5, 3: 3, 11: 1})


@pytest.mark.pool
def Test_The_Supercell_Units_See_The_Full_Field_Block() -> None:
    """169 full-field runs grouped into shear orbits, with the E4 gap visible"""
    Require_The_Pool()
    census_rows = Read_Census(POOL_ROOT)
    units = Supercell_Units(census_rows, Hard_Excluded_Paths(census_rows, POOL_ROOT))
    assert sum(len(unit.run_paths) for unit in units) == 169
    sizes = Counter(len(unit.run_paths) for unit in units)
    assert sizes[6] == 19 and sizes[5] == 1 and sizes[3] == 16 and sizes[2] == 1


@pytest.mark.pool
def Test_The_Twin_Map_Covers_Both_Campaigns() -> None:
    """twenty shear orbits with both sides, and 119 usable supercell runs"""
    Require_The_Pool()
    census_rows = Read_Census(POOL_ROOT)
    twins = Twin_Shear_Map(census_rows, POOL_ROOT)
    assert len(twins) == 20
    assert all(record["strain_atlas"] and record["supercell_strains"] for record in twins.values())
    assert sum(len(record["supercell_strains"]) for record in twins.values()) == 119


@pytest.mark.pool
def Test_The_Strain_Holdout_Partitions_Every_Orbit() -> None:
    """296 orbits split into train, validation and test, the anchor in train"""
    Require_The_Pool()
    census_rows = Read_Census(POOL_ROOT)
    holdout = Strain_Holdout_Assignment(census_rows)
    assert len(holdout) == 296
    assignments = Counter(record.assignment for record in holdout.values())
    assert assignments["validation"] >= 25 and assignments["test"] >= 25
    assert sum(assignments.values()) == 296
    reference = [record for record in holdout.values() if record.family == "reference"]
    assert len(reference) == 1 and reference[0].assignment == "train"


@pytest.mark.pool
def Test_The_Paired_Fields_Folds_Balance_And_The_Artifacts_Regenerate() -> None:
    """per-stratum fold balance, and bit-for-bit artifact reproduction"""
    Require_The_Pool()
    census_rows = Read_Census(POOL_ROOT)
    units = Paired_Fields_Units(census_rows, POOL_ROOT)
    folds = Fold_Assignment(units)
    by_stratum: dict[str, Counter[int]] = {}
    for unit in units:
        by_stratum.setdefault(f"{unit.campaign}:{unit.stratum}", Counter())[folds[unit.key]] += 1
    for stratum, counts in by_stratum.items():
        spread = max(counts.values()) - min(list(counts.values()) + [0] * (5 - len(counts)))
        assert spread <= 1, (stratum, counts)
    assert Regenerated_Artifacts_Match(census_rows, POOL_ROOT)

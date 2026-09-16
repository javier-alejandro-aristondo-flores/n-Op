"""the field-completion split, derived locally against the committed paired-fields fold map since no artifact names it yet"""

import hashlib
import json
from pathlib import Path

import numpy as np

from operators.codomain_attention.channels import CHANNEL_VOCABULARY, FINE_SHAPE
from operators.data import ARTIFACT_DIRECTORY, Archive_Path, Guard_Fresh_Archives, POOL_ROOT

# the cubic block this member trains and is judged on: the alloy campaign is the zero-shot transfer set, held out here
CUBIC_CAMPAIGNS = ("supercell_strains", "defect_set")

ALLOY_CAMPAIGN = "alloy_ensemble"

DEFECT_CAMPAIGN = "defect_set"

FOLD_COUNT = 5

# k3's own low-data fraction, the canon's quarter-of-the-defect-set test
LOW_DATA_FRACTION = 0.25

# a seed local to this member's own low-data draw, distinct from the committed split engine's own seed
LOW_DATA_SEED = "codomain-attention-k3-low-data-v1"


def Stable_Fraction(identifier: str) -> float:
    """an identifier hashed to a fraction of one, so the same identifier always lands in the same place"""
    digest = hashlib.sha256(f"{LOW_DATA_SEED}:{identifier}".encode()).digest()
    return int.from_bytes(digest[:8]) / 2.0**64


def Fold_Membership() -> dict[str, tuple[int, str, str, str]]:
    """every cubic-campaign run identifier with its fold, campaign, owning split unit and own run path"""
    payload = json.loads((ARTIFACT_DIRECTORY / "paired_fields_fivefold.json").read_text())
    membership: dict[str, tuple[int, str, str, str]] = {}
    for unit_key, unit in payload.items():
        if unit["campaign"] not in CUBIC_CAMPAIGNS:
            continue
        for identifier, run_path in zip(unit["run_identifiers"], unit["run_paths"], strict=True):
            membership[identifier] = (int(unit["fold"]), str(unit["campaign"]), unit_key, str(run_path))
    return membership


def Alloy_Membership() -> dict[str, tuple[str, str]]:
    """every alloy-campaign run identifier with its owning split unit and own run path, the transfer set"""
    payload = json.loads((ARTIFACT_DIRECTORY / "paired_fields_fivefold.json").read_text())
    membership: dict[str, tuple[str, str]] = {}
    for unit_key, unit in payload.items():
        if unit["campaign"] != ALLOY_CAMPAIGN:
            continue
        for identifier, run_path in zip(unit["run_identifiers"], unit["run_paths"], strict=True):
            membership[identifier] = (unit_key, str(run_path))
    return membership


def Has_Every_Channel(archive: "np.lib.npyio.NpzFile") -> bool:
    """whether an archive carries all six of this member's channels at the fine grid this member expects"""
    keys = frozenset(archive.files)
    if not all(label in keys for label in CHANNEL_VOCABULARY):
        return False
    return tuple(int(extent) for extent in archive["charge_density"].shape) == FINE_SHAPE


class CompletionBlock:
    """the completion task's own identifiers, grouped by fold, restricted to runs this member's vocabulary fits"""


    def __init__(self, pool_root: Path = POOL_ROOT) -> None:
        membership = Fold_Membership()
        by_fold: dict[int, list[str]] = {fold: [] for fold in range(FOLD_COUNT)}
        campaign_of: dict[str, str] = {}
        unit_of: dict[str, str] = {}
        run_path_of: dict[str, str] = {}
        for identifier, (fold, campaign, unit_key, run_path) in membership.items():
            archive_path = Archive_Path(campaign, identifier, pool_root)
            if not archive_path.exists():
                continue
            with np.load(archive_path) as archive:
                complete = Has_Every_Channel(archive)
            if not complete:
                continue
            by_fold[fold].append(identifier)
            campaign_of[identifier] = campaign
            unit_of[identifier] = unit_key
            run_path_of[identifier] = run_path
        Guard_Fresh_Archives(
            (identifier for fold_identifiers in by_fold.values() for identifier in fold_identifiers), pool_root
        )
        self.by_fold = {fold: sorted(identifiers) for fold, identifiers in by_fold.items()}
        self.campaign_of = campaign_of
        self.unit_of = unit_of
        self.run_path_of = run_path_of
        self.alloy_membership = Alloy_Membership()
        self.pool_root = pool_root


    @property
    def evaluation(self) -> list[str]:
        """fold zero, the block this member and every dedicated competitor is finally judged against"""
        return self.by_fold[0]


    @property
    def validation(self) -> list[str]:
        """fold one, held out for early stopping and the fixed validation-mask patterns"""
        return self.by_fold[1]


    @property
    def member_train(self) -> list[str]:
        """folds two through four, the pretraining population"""
        return sorted(identifier for fold in (2, 3, 4) for identifier in self.by_fold[fold])


    def Alloy_Transfer_Identifiers(self) -> list[str]:
        """every alloy identifier whose archive is present on disk, the zero-shot transfer set"""
        return sorted(
            identifier
            for identifier in self.alloy_membership
            if Archive_Path(ALLOY_CAMPAIGN, identifier, self.pool_root).exists()
        )


    def Low_Data_Defect_Identifiers(self, fraction: float = LOW_DATA_FRACTION) -> list[str]:
        """a deterministic quarter of the pretraining defect-only identifiers, k3's own low-data slice"""
        defect_identifiers = [identifier for identifier in self.member_train if self.campaign_of[identifier] == DEFECT_CAMPAIGN]
        # hash order rather than identifier order, so the quarter is not an accident of how the archives were named
        ordered = sorted(defect_identifiers, key=lambda identifier: (Stable_Fraction(identifier), identifier))
        kept_count = max(1, round(fraction * len(ordered)))
        return sorted(ordered[:kept_count])

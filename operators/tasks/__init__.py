"""task cards naming the inputs, targets, loss, metrics and split of one suite task"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaskCard:
    """one suite task stated as data"""

    name: str
    suite_card: str
    inputs: tuple[str, ...]
    targets: tuple[str, ...]
    loss: str
    metrics: tuple[str, ...]
    conservation: str | None
    covariates: tuple[str, ...]
    split: str


CARDS: tuple[TaskCard, ...] = (
    TaskCard(
        name="charge_to_localization",
        suite_card="test-suite.md §2, pattern I",
        inputs=("charge_density", "magnetization_density"),
        targets=("electron_localization_up", "electron_localization_down"),
        loss="mean_squared_error",
        metrics=("mean_absolute_error", "structural_similarity_3d", "relative_l2"),
        conservation=None,
        covariates=("functional",),
        split="paired_fields_fivefold",
    ),
    TaskCard(
        name="charge_to_potential",
        suite_card="test-suite.md §2, pattern I (calibration probe)",
        inputs=("charge_density", "magnetization_density"),
        targets=("local_potential_up", "local_potential_down"),
        loss="mean_removed_mean_squared_error",
        metrics=("mean_removed_relative_l2", "mean_absolute_error", "mean_discrepancy"),
        conservation="pin_uniform_mode",
        covariates=("functional",),
        split="paired_fields_fivefold",
    ),
    TaskCard(
        name="strain_to_charge",
        suite_card="test-suite.md §3, II.1a",
        inputs=("strain_parameters",),
        targets=("charge_density",),
        loss="mean_squared_error",
        metrics=("relative_l2", "frequency_split_relative_l2"),
        conservation="renormalize_to_electron_count",
        covariates=("functional",),
        split="strain_atlas_holdout",
    ),
    TaskCard(
        name="lattice_to_charge",
        suite_card="test-suite.md §3, II.1b",
        inputs=("lattice_parameters",),
        targets=("charge_density",),
        loss="mean_squared_error",
        metrics=("relative_l2", "frequency_split_relative_l2"),
        conservation="renormalize_to_electron_count",
        covariates=(),
        split="perovskite_folds",
    ),
    TaskCard(
        name="charge_and_potential_to_localization",
        suite_card="test-suite.md §3, II.2",
        inputs=("charge_density", "magnetization_density", "local_potential_up", "local_potential_down"),
        targets=("electron_localization_up", "electron_localization_down"),
        loss="mean_squared_error",
        metrics=("mean_absolute_error", "structural_similarity_3d", "relative_l2"),
        conservation=None,
        covariates=("functional",),
        split="paired_fields_fivefold",
    ),
    TaskCard(
        name="structure_to_charge_defects",
        suite_card="test-suite.md §4, III.1a",
        inputs=("positions", "species", "lattice"),
        targets=("charge_density", "magnetization_density"),
        loss="mean_squared_error_with_moment_normalized_magnetization",
        metrics=("normalized_mean_absolute_error", "relative_l2"),
        conservation="renormalize_to_electron_count",
        covariates=("pseudopotential_titles",),
        split="paired_fields_fivefold",
    ),
    TaskCard(
        name="structure_to_charge_alloy",
        suite_card="test-suite.md §4, III.1b",
        inputs=("positions", "species", "lattice"),
        targets=("charge_density",),
        loss="mean_squared_error",
        metrics=("normalized_mean_absolute_error", "relative_l2"),
        conservation="renormalize_to_electron_count",
        covariates=("pseudopotential_titles",),
        split="paired_fields_fivefold",
    ),
    TaskCard(
        name="structure_to_charge_strain",
        suite_card="test-suite.md §4, III.1c",
        inputs=("positions", "species", "lattice"),
        targets=("charge_density",),
        loss="mean_squared_error",
        metrics=("normalized_mean_absolute_error", "relative_l2"),
        conservation="renormalize_to_electron_count",
        covariates=("functional", "pseudopotential_titles"),
        split="strain_atlas_holdout",
    ),
    TaskCard(
        name="cheap_to_accurate_charge",
        suite_card="test-suite.md §5, IV.1",
        inputs=("charge_density",),
        targets=("charge_density",),
        loss="delta_mean_squared_error",
        metrics=("delta_r_squared", "relative_l2"),
        conservation="zero_mean_correction",
        covariates=("campaign", "exact_exchange_fraction"),
        split="strain_atlas_holdout",
    ),
    TaskCard(
        name="field_completion",
        suite_card="test-suite.md §6, V.1",
        inputs=("any_field_subset",),
        targets=("the_masked_fields",),
        loss="masked_mean_squared_error",
        metrics=("mean_absolute_error", "mean_removed_relative_l2", "relative_l2"),
        conservation="per_task_head",
        covariates=("functional",),
        split="supercell_defect_train_alloy_holdout",
    ),
    TaskCard(
        name="strain_to_states",
        suite_card="test-suite.md §7, VI.1",
        inputs=("strain_parameters",),
        targets=("density_of_states_curve",),
        loss="curve_l1",
        metrics=("curve_l1", "wasserstein_1d", "gap_edge_error"),
        conservation=None,
        covariates=("functional",),
        split="strain_atlas_holdout",
    ),
)


def Card_Named(name: str) -> TaskCard:
    """the one card with the given name"""
    for card in CARDS:
        if card.name == name:
            return card
    raise KeyError(f"no task card named {name}")

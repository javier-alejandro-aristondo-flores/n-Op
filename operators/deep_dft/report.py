"""the member measured against its floors, written as one committed markdown artifact"""

import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.data import ARTIFACT_DIRECTORY, POOL_ROOT, STORE_NAME
from operators.deep_dft import Deep_Dft_Network
from operators.deep_dft.floors import (
    Deep_Dft_Superposed_Atomic_Density_Errors,
    Element_Vocabulary,
    Fitted_Salted_Floor,
    Magnetic_Identifiers,
    Nearest_Copy_Errors,
    Salted_Floor_Errors,
)
from operators.deep_dft.sampling import Trilinear_Interpolate
from operators.deep_dft.species import Loaded_Structure, SpeciesKeys, Structure, Training_Vocabulary
from operators.evaluation import ScoredRun, Summarize, Summary_Table
from operators.framework import Coefficients, Domain, GridSpec, PointSet
from operators.inspection import Render_Inspection_Suite, Render_Table

REPORT_PATH = Path(__file__).parent / "report.md"

FIGURES_PATH = Path(__file__).parent / "figures"

# the inspection arrays are derived from corpus fields, and a derived array never leaves the pool either
ARRAY_CACHE_PATH = POOL_ROOT / STORE_NAME / "_figures" / "deep_dft"

TRAINING_ARTIFACT_PATH = POOL_ROOT / STORE_NAME / "_training" / "deep_dft"

DEFECT_CAMPAIGN = "defect_set"

METRIC_NAME = "normalized_mean_absolute_error"

# gate a: ten times better than the superposed-atomic-density floor
GATE_A_REQUIRED_IMPROVEMENT = 0.9

# gate b: three times better than the reduced-salted floor
GATE_B_REQUIRED_IMPROVEMENT = 2.0 / 3.0

GATE_C_BAR = 0.90

MAGNETIC_TOTAL_MOMENT_EPSILON = 1e-3

DEMONSTRATION_GRID_SHAPE = (16, 16, 16)


def Defect_Fold_Identifiers() -> tuple[dict[str, str], list[str], list[str]]:
    """each defect run's own exchangeable unit key, and the training and fold-zero identifier lists"""
    payload = json.loads((ARTIFACT_DIRECTORY / "paired_fields_fivefold.json").read_text())
    unit_key_of: dict[str, str] = {}
    train_identifiers: list[str] = []
    fold_zero_identifiers: list[str] = []
    for unit_key, unit in payload.items():
        if unit["campaign"] != DEFECT_CAMPAIGN:
            continue
        for identifier in unit["run_identifiers"]:
            unit_key_of[identifier] = unit_key
        destination = fold_zero_identifiers if unit["fold"] == 0 else train_identifiers
        destination.extend(unit["run_identifiers"])
    return unit_key_of, train_identifiers, fold_zero_identifiers


def Loaded_Structures(identifiers: list[str]) -> tuple[Structure, ...]:
    """every identifier's own structure, skipping runs the store cannot answer for"""
    return tuple(
        structure
        for structure in (Loaded_Structure(DEFECT_CAMPAIGN, identifier) for identifier in identifiers)
        if structure is not None
    )


def Scored_Rows(
    errors: dict[str, float], unit_key_of: dict[str, str], family: str, held_out_identifiers: frozenset[str]
) -> list[ScoredRun]:
    """error values as scored rows under one metric name, held-out-chemistry runs tagged as extrapolation"""
    return [
        ScoredRun(
            identifier=identifier,
            unit_key=unit_key_of[identifier],
            campaign=DEFECT_CAMPAIGN,
            family=family,
            errors={METRIC_NAME: error},
            extrapolation="extrapolation" if identifier in held_out_identifiers else "interpolation",
        )
        for identifier, error in errors.items()
    ]


def Interpolation_Error_On_A_Synthetic_Field(seed: int = 20260916) -> float:
    """the trilinear interpolator's own root-mean-square error on a smooth field, at the campaign's grid shape"""

    def Field(points: NDArray[np.float64]) -> NDArray[np.float64]:
        """a smooth periodic scalar field with three fourier components"""
        return np.sin(2.0 * np.pi * points[:, 0]) * np.cos(4.0 * np.pi * points[:, 1]) + 0.3 * np.sin(
            6.0 * np.pi * points[:, 2]
        )

    shape = (80, 80, 80)
    axes = [np.arange(extent, dtype=np.float64) / extent for extent in shape]
    axis_grids = np.meshgrid(*axes, indexing="ij")
    grid_points = np.stack([axis_grid.reshape(-1) for axis_grid in axis_grids], axis=1)
    grid_values = Field(grid_points).reshape(*shape, 1)
    generator = np.random.default_rng(seed)
    query_points = generator.random((20000, 3))
    interpolated = Trilinear_Interpolate(grid_values, query_points)[:, 0]
    truth = Field(query_points)
    return float(np.sqrt(np.mean((interpolated - truth) ** 2)))


class LoadedBlock:
    """the defect campaign's own folds, loaded once and shared by the floors and the architecture sections"""


    def __init__(self) -> None:
        self.unit_key_of, train_identifiers, fold_zero_identifiers = Defect_Fold_Identifiers()
        self.train_structures = Loaded_Structures(train_identifiers)
        self.fold_zero_structures = Loaded_Structures(fold_zero_identifiers)
        self.training_vocabulary = Training_Vocabulary(self.train_structures)
        self.species_keys = SpeciesKeys(self.training_vocabulary)
        self.held_out_identifiers = frozenset(
            structure.identifier
            for structure in self.fold_zero_structures
            if self.species_keys.Held_Out_Chemistry(structure)
        )


def Floor_Block_Lines(block: LoadedBlock) -> tuple[list[str], dict[str, float]]:
    """the block counts, the three floors and the pre-registered claim ladder, measured before any training"""
    unit_key_of = block.unit_key_of
    train_structures = block.train_structures
    fold_zero_structures = block.fold_zero_structures
    training_vocabulary = block.training_vocabulary
    held_out_identifiers = block.held_out_identifiers

    sad_errors = Deep_Dft_Superposed_Atomic_Density_Errors(fold_zero_structures)
    element_vocabulary = Element_Vocabulary(train_structures)
    salted_floor = Fitted_Salted_Floor(train_structures, element_vocabulary)
    salted_errors = Salted_Floor_Errors(salted_floor, fold_zero_structures)
    copy_errors = Nearest_Copy_Errors(train_structures, fold_zero_structures)

    sad_rows = Scored_Rows(sad_errors, unit_key_of, "superposed_atomic_density", held_out_identifiers)
    salted_rows = Scored_Rows(salted_errors, unit_key_of, "reduced_salted", held_out_identifiers)
    copy_rows = Scored_Rows(copy_errors, unit_key_of, "nearest_structure_copy", held_out_identifiers)
    sad_rows_held_out = [row for row in sad_rows if row.identifier in held_out_identifiers]
    magnetic_identifiers = Magnetic_Identifiers(fold_zero_structures, epsilon=MAGNETIC_TOTAL_MOMENT_EPSILON)

    sad_summary_all = Summarize(sad_rows, METRIC_NAME, "superposed_atomic_density_floor_all_42")
    sad_summary_held_out = Summarize(sad_rows_held_out, METRIC_NAME, "superposed_atomic_density_floor_held_out_18")
    salted_summary = Summarize(salted_rows, METRIC_NAME, "reduced_salted_floor_all_42")
    copy_summary = Summarize(copy_rows, METRIC_NAME, "nearest_structure_copy_context_all_42")

    bars = {
        "gate_a_bar_all_42": sad_summary_all.median * (1.0 - GATE_A_REQUIRED_IMPROVEMENT),
        "gate_a_bar_held_out_18": sad_summary_held_out.median * (1.0 - GATE_A_REQUIRED_IMPROVEMENT),
        "gate_b_bar_all_42": salted_summary.median * (1.0 - GATE_B_REQUIRED_IMPROVEMENT),
    }
    interpolation_error = Interpolation_Error_On_A_Synthetic_Field()

    lines = [
        "## The block",
        "",
        f"Defect campaign, fold zero as the evaluation (kill) block: {len(fold_zero_structures)} runs across"
        f" {len({unit_key_of[structure.identifier] for structure in fold_zero_structures})} units, folds one"
        f" through four training the floors ({len(train_structures)} runs). {len(held_out_identifiers)} of the"
        f" {len(fold_zero_structures)} fold-zero runs carry an element absent from every training fold"
        " (held-out chemistry), scored as its own row beside the pooled one. Training vocabulary: "
        f"{len(training_vocabulary) - 1} (element, pseudopotential title) pairs plus the trained unknown row.",
        "",
        "## Floors, measured before training, on this exact block, normalized mean absolute error",
        "",
        "The superposed-atomic-density floor reads `superposed_atomic_density` directly off the store, no"
        " fitting. The reduced-salted floor is a standardized ridge from per-species isotropic gaussian shells"
        " (eight widths, periodic images by cell height) onto density minus the atomic superposition, fit on"
        " 1,000 mixture-sampled probes per training run and scored on a fixed 5,000-point random subsample of"
        " each fold-zero run's own grid (a deliberate approximation for the floor's own cost, not for the"
        " member, which is scored on the true full grid); it stands in for the canon's own reduced"
        " density-fitting floor. The nearest-structure copy is context, not a gate: it copies the full charge"
        " density of the training run closest in per-element atom-count composition.",
        "",
        "```",
        Render_Table(Summary_Table((sad_summary_all, sad_summary_held_out, salted_summary, copy_summary))),
        "```",
        "",
        "### the pre-registered ladder, absolute normalized mean absolute error",
        "",
        f"- **gate a** (>= 10x better than the superposed-atomic-density floor, `required_improvement=0.9`):"
        f" pooled bar {bars['gate_a_bar_all_42']:.6f}, held-out-chemistry bar {bars['gate_a_bar_held_out_18']:.6f}",
        f"- **gate b** (>= 3x better than the reduced-salted floor, `required_improvement=2/3`):"
        f" bar {bars['gate_b_bar_all_42']:.6f}",
        f"- **gate c** (spin row, member-local, not a floor comparison): on the {len(magnetic_identifiers)}"
        f" magnetic fold-zero runs (`|final_magnetization| > {MAGNETIC_TOTAL_MOMENT_EPSILON}`), fraction with"
        f" relative total-moment error <= 5% and the right sign, bar >= {GATE_C_BAR}",
        "",
        f"Trilinear interpolation error, measured on a smooth synthetic field at the campaign's own 80-cubed"
        f" grid resolution, 20,000 random query points: root-mean-square {interpolation_error:.6f}.",
        "",
        "**Not yet measured**: the member has not trained (the card is not this stream's yet, and the"
        " compact-support kernel's own scatter-add has not been lifted onto a differentiating engine), so no"
        " row above compares the member to these bars. This section will carry that comparison, the gate c"
        " pass fraction, and the figure suite once a checkpoint exists.",
        "",
    ]
    return lines, bars


def Architecture_Lines(block: LoadedBlock) -> list[str]:
    """the built configuration, its parameter count, and the figure suite rendered from a demonstration structure"""
    member = Deep_Dft_Network(block.training_vocabulary, seed=20260916)
    parameter_count = sum(value.size for value in member.Parameter_Values().values())

    demonstration = block.train_structures[0]
    resolved_keys = block.species_keys.Resolved(demonstration.species_keys)
    domain = Domain(lattice=demonstration.lattice)
    structure_point_set = PointSet(
        positions=demonstration.positions, domain=domain, species=np.asarray(resolved_keys)
    )
    condition = Coefficients(vector=np.asarray([demonstration.electron_count]), domain=domain)
    member(structure_point_set, GridSpec(DEMONSTRATION_GRID_SHAPE), condition)

    inspected: dict[str, NDArray[np.float64]] = {
        key: np.asarray(value, dtype=np.float64) for key, value in member.Inspect().items()
    }
    inspected_for_saving: dict[str, Any] = dict(inspected)
    cache_directory = ARRAY_CACHE_PATH / demonstration.identifier
    cache_directory.mkdir(parents=True, exist_ok=True)
    np.savez(cache_directory / "inspect.npz", **inspected_for_saving)
    suite = Render_Inspection_Suite(inspected, FIGURES_PATH, "deep_dft")

    return [
        "## Architecture, as built",
        "",
        "Atom embedding (member-local unknown-row policy) into a 64-wide channel space; three atom-atom"
        " `ContinuousDisplacementKernel` layers (cutoff 4.0 angstrom, 20-function sinc basis) plus a local"
        " linear term and a smooth unit each; the atoms then join the probe points into one point set and three"
        " more identically shaped atom-probe layers carry the joint state, probes marked receive-only; a"
        " two-layer perceptron head reads each probe's own features onto density and magnetization.",
        "",
        f"Parameter count: {parameter_count:,} (about 94% of it the six kernels' own radial weight tensors,"
        " basis_count x hidden x hidden each).",
        "",
        f"Figure suite: {len(suite.written)} files written under `operators/deep_dft/figures/`, "
        f"{len(suite.skipped)} inspection keys skipped ({', '.join(suite.skipped) if suite.skipped else 'none'})."
        " The atom-to-probe adjacency matrix (`composition__last_atom_to_probe_adjacency.png`) is this member's"
        " own figure: which probes fall inside which atoms' cutoff, on the demonstration structure"
        f" `{demonstration.identifier}`.",
        "",
    ]


def Main() -> int:
    """the block, its floors and pre-registered ladder, and the built architecture, written to report.md"""
    block = LoadedBlock()
    floor_lines, bars = Floor_Block_Lines(block)
    architecture_lines = Architecture_Lines(block)
    header = [
        "# deep_dft — measured against its floors",
        "",
        "Regenerate with `python3 -m operators.deep_dft.report`.",
        "",
        "The block, the three floors and the pre-registered claim ladder below were measured before a single"
        " training step was taken. The member's own result follows once training is possible; until then this"
        " section says so plainly and nothing else about this command changes.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(header + floor_lines + architecture_lines) + "\n")
    print(f"wrote {REPORT_PATH}")
    print(bars)
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())

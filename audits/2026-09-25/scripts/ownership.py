"""assigns every tracked file at the audited commit to its audit slices and proves none is left without one"""

import fnmatch
import json
import subprocess
import sys
from pathlib import Path


REPOSITORY = Path("/home/javier/Projects/Physics/Programs/n-Op")
AUDITED_COMMIT = "485a7d9"
OUT_OF_SCOPE = ("1-archive/*", "2-pnp-op/*")

FLAGSHIP_CODE = ["operators/factorized_fourier/__init__.py", "operators/factorized_fourier/report.py",
                 "operators/factorized_fourier/report.md", "operators/factorized_fourier/IMPLEMENTATION.md",
                 "operators/factorized_fourier/manifest.toml"]
BRANCH_TRUNK_CODE = ["operators/deep_operator_network/__init__.py", "operators/deep_operator_network/report.py",
                     "operators/deep_operator_network/report.md", "operators/deep_operator_network/IMPLEMENTATION.md",
                     "operators/deep_operator_network/manifest.toml"]

SLICE_PATTERNS: dict[str, list[str]] = {
    "D1-raw-data": ["operators/data/parsers.py", "operators/data/store.py", "operators/data/stage0.py",
                    "operators/data/spectra.py", "operators/data/__init__.py", "operators/stage0-report.md",
                    "operators/tests/test_parsers.py", "operators/tests/test_store.py"],
    "D2-grouping-and-splits": ["operators/data/exclusions.py", "operators/data/orbits.py", "operators/data/splits.py",
                               "operators/data/pod.py", "operators/data/__init__.py", "operators/data/splits/*.json",
                               "operators/tests/test_exclusions.py", "operators/tests/test_orbits.py",
                               "operators/tests/test_splits.py"],
    "T-training": ["operators/training/*", "operators/tests/test_training.py", "operators/tests/test_sampling.py"],
    "S1-metrics-intervals-pooling": ["operators/metrics/*", "operators/evaluation/scoring.py",
                                     "operators/evaluation/__init__.py", "operators/tests/test_metrics.py",
                                     "operators/tests/test_evaluation.py"],
    "S2-floors-and-verdicts": ["operators/data/floors.py", "operators/evaluation/localization_block.py",
                               "operators/evaluation/perovskite_block.py", "operators/evaluation/every_shape.py",
                               "operators/evaluation/results.py", "operators/evaluation/cross_member.py",
                               "operators/evaluation/cross_member.md", "operators/evaluation/__init__.py",
                               "operators/tasks/*", "operators/tests/test_floors.py",
                               "operators/tests/test_evaluation.py"],
    "P-pictures": ["operators/inspection/*", "operators/inspection/plots/*", "operators/tests/test_inspection.py"],
    "N1-substrate-and-framework": ["operators/substrate/*", "operators/framework/*", "operators/tests/test_substrate.py",
                                   "operators/tests/test_fourier.py", "operators/tests/test_integral.py",
                                   "operators/tests/test_invariance.py"],
    "N2-kernels": ["operators/kernels/*", "operators/kernels/*/*", "operators/tests/test_kernels.py",
                   "operators/tests/test_codomain_attention.py", "operators/tests/test_spectral_metric.py"],
    "N3-compositions": ["operators/compositions/*", "operators/tests/test_fixed_point.py",
                        "operators/tests/test_contraction.py", "operators/tests/test_multi_scale.py"],
    "N4-encoders-readouts-wrappers": ["operators/encoders/*", "operators/readouts/*", "operators/wrappers/*",
                                      "operators/tests/test_parts.py"],
    "M1-flagship-localization": [*FLAGSHIP_CODE, "operators/tests/test_factorized_fourier.py",
                                 "operators/factorized_fourier/figures/fold_0/explicit/*",
                                 "operators/factorized_fourier/figures/fold_0/explicit/*/*"],
    "M2-flagship-ladder-potential-parametric": [*FLAGSHIP_CODE, "operators/factorized_fourier/parametric.py",
                                                "operators/tests/test_factorized_fourier.py",
                                                "operators/tests/test_factorized_fourier_parametric.py",
                                                "operators/factorized_fourier/figures/*"],
    "M3-branch-trunk-parameters-to-charge": [*BRANCH_TRUNK_CODE, "operators/deep_operator_network/configs/canonical.toml",
                                             "operators/deep_operator_network/configs/principal_component.toml",
                                             "operators/deep_operator_network/configs/proper_orthogonal.toml",
                                             "operators/tests/test_deep_operator_network.py",
                                             "operators/deep_operator_network/figures/*"],
    "M4-branch-trunk-energy-trunk": [*BRANCH_TRUNK_CODE, "operators/deep_operator_network/configs/energy_trunk.toml",
                                     "operators/tests/test_deep_operator_network.py",
                                     "operators/deep_operator_network/figures/*energy_trunk*"],
    "M5-correction": ["operators/residual_correction/*", "operators/tests/test_residual_correction.py"],
    "M6-two-input": ["operators/multiple_input_operator_network/*",
                     "operators/tests/test_multiple_input_operator_network.py"],
    "M7-manifold-decoder": ["operators/nonlinear_manifold_decoder/*", "operators/tests/test_nonlinear_manifold_decoder.py"],
    "M8-galerkin": ["operators/galerkin_transformer/*", "operators/tests/test_galerkin_transformer.py"],
    "M9-codomain-member": ["operators/codomain_attention/*", "operators/tests/test_codomain_attention_member.py"],
    "M10-structure-to-density": ["operators/deep_dft/*", "operators/tests/test_deep_dft.py"],
    "M11-convolutional-and-plane-wave": ["operators/alias_free_convolutional/*", "operators/gaussian_plane_wave/*",
                                         "operators/tests/test_alias_free_convolutional.py"],
    "R-results-page": ["operator-results.md"],
    "G-gates-and-package": ["operators/tests/test_imports.py", "operators/tests/conftest.py", "operators/pyproject.toml",
                            "operators/__init__.py", "operators/README.md", ".gitattributes", ".gitignore"],
    "L-ledger": ["test-suite.md"],
}


def Tracked_Files() -> list[str]:
    """every file at the audited commit outside the out-of-scope folders"""
    listing = subprocess.run(["git", "-C", str(REPOSITORY), "ls-tree", "-r", "--name-only", AUDITED_COMMIT],
                             capture_output=True, text=True, check=True).stdout.split()
    return [name for name in listing if not any(fnmatch.fnmatch(name, pattern) for pattern in OUT_OF_SCOPE)]


def Owners_Of(name: str) -> list[str]:
    """the slices whose patterns match a file, with fnmatch's star crossing folder separators"""
    return [slice_name for slice_name, patterns in SLICE_PATTERNS.items()
            if any(fnmatch.fnmatch(name, pattern) for pattern in patterns)]


def Line_Count(name: str) -> int:
    """lines in a text file at the audited commit, zero for images"""
    if name.endswith(".png"):
        return 0
    text = subprocess.run(["git", "-C", str(REPOSITORY), "show", f"{AUDITED_COMMIT}:{name}"],
                          capture_output=True, text=True, errors="replace").stdout
    return text.count("\n")


def Main() -> None:
    """writes the slice map and exits nonzero when any tracked file has no owner"""
    files = Tracked_Files()
    owners = {name: Owners_Of(name) for name in files}
    orphans = [name for name, slices in owners.items() if not slices]
    slice_files: dict[str, list[str]] = {slice_name: [] for slice_name in SLICE_PATTERNS}
    for name, slices in owners.items():
        for slice_name in slices:
            slice_files[slice_name].append(name)
    lines = {name: Line_Count(name) for name in files}
    for slice_name, names in slice_files.items():
        text_files = [name for name in names if not name.endswith(".png")]
        images = len(names) - len(text_files)
        print(f"{slice_name:44s} {len(text_files):4d} text files {sum(lines[n] for n in text_files):6d} lines {images:4d} images")
    shared = {name: slices for name, slices in owners.items() if len(slices) > 1 and not name.endswith(".png")}
    print(f"{len(files)} files in scope, {len(orphans)} without an owner, {len(shared)} text files shared by two or more slices")
    for name in orphans:
        print(f"orphan\t{name}")
    Path(sys.argv[1]).write_text(json.dumps({"files": slice_files, "shared": shared, "orphans": orphans}, indent=1))
    sys.exit(1 if orphans else 0)


if __name__ == "__main__":
    Main()

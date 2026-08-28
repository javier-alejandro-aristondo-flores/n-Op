"""The derived tensor store: census-driven extraction of runs into per-run archives."""

import argparse
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from operators.data.parsers import (
    Cell_Volume,
    FieldFile,
    Geometry,
    ParseError,
    Read_Eigenvalues,
    Read_Field_File,
    Read_Final_Magnetization,
    Read_Geometry,
    Read_Outcar_Echoes,
)

EXTRACTOR_VERSION = 1

POOL_ROOT = Path("/Pool/VASP_DATA")

CENSUS_NAME = "_census/runs.jsonl"

STORE_NAME = "_derived"

CAMPAIGN_PREFIXES: tuple[tuple[str, str], ...] = (
    ("alloy/", "alloy_ensemble"),
    ("diamond/2_atoms_4-10-2026/", "strain_atlas"),
    ("diamond/Pure/", "supercell_strains"),
    ("diamond/single_defect/", "defect_set"),
    ("diamond/pair_defects/", "defect_set"),
    ("diamond/triads_defects/", "defect_set"),
    ("diamond/single_defects_new-only-GGA-PBE/", "defect_set"),
    ("diamond/single_defects_new-only-HSE06/", "defect_set"),
    ("ggapbe/", "perovskite_grid"),
    ("j-dataset/", "relaxation_pool"),
)

UNIT_BY_FIELD: dict[str, str] = {
    "charge_density": "electrons per cubic angstrom",
    "magnetization_density": "bohr magnetons per cubic angstrom",
    "all_electron_core_density": "electrons per cubic angstrom",
    "superposed_atomic_density": "electrons per cubic angstrom",
    "all_electron_valence_density": "electrons per cubic angstrom",
    "electron_localization": "dimensionless in [0, 1]",
    "local_potential": "electronvolts",
    "local_potential_mean": "electronvolts",
    "lattice": "angstrom rows",
    "positions": "fractional coordinates",
    "cell_volume": "cubic angstrom",
    "electron_count": "electrons",
    "final_magnetization": "bohr magnetons",
    "kpoints": "fractional reciprocal coordinates",
    "kpoint_weights": "dimensionless",
    "eigenvalue_energies": "electronvolts",
    "eigenvalue_occupancies": "dimensionless",
    "eigenvalue_electron_count": "electrons",
}

type StoreArray = NDArray[np.float32] | NDArray[np.float64] | NDArray[np.str_]


class StoreError(Exception):
    """Raised when the store is asked to do something its rules forbid."""


@dataclass(frozen=True, slots=True)
class CensusRow:
    """One run from the census, with its raw record and line hash."""

    path: str
    corpus: str
    row_hash: str
    file_sizes: dict[str, int]
    record: dict[str, object]


def Read_Census(pool_root: Path) -> tuple[CensusRow, ...]:
    """Reads runs.jsonl into census rows with per-line hashes."""
    census_rows: list[CensusRow] = []
    for line in (pool_root / CENSUS_NAME).read_text().splitlines():
        if not line.strip():
            continue
        record = cast(dict[str, object], json.loads(line))
        sizes = {name: int(cast(int, size)) for name, size in cast(dict[str, object], record.get("files", {})).items()}
        census_rows.append(
            CensusRow(
                path=cast(str, record["path"]),
                corpus=cast(str, record.get("corpus", "?")),
                row_hash=hashlib.sha1(line.strip().encode()).hexdigest(),
                file_sizes=sizes,
                record=record,
            )
        )
    return tuple(census_rows)


def Campaign_Of(path: str) -> str:
    """Maps a run path to its campaign name, or uncatalogued."""
    for prefix, campaign in CAMPAIGN_PREFIXES:
        if path.startswith(prefix):
            return campaign
    return "uncatalogued"


def Run_Identifier(path: str) -> str:
    """Returns the sixteen-character content identifier of a run path."""
    return hashlib.sha1(path.encode()).hexdigest()[:16]


def Guard_Volumetric_Destination(destination: Path, pool_root: Path) -> None:
    """Raises unless the destination resolves inside the corpus partition."""
    if not destination.resolve().is_relative_to(pool_root.resolve()):
        raise StoreError(f"volumetric write outside the corpus partition refused: {destination}")


def Spin_Pair_Entries(name: str, field: FieldFile, divisor: float) -> dict[str, NDArray[np.float32]]:
    """Names one block plainly or two blocks as up and down channels."""
    blocks = [(block / divisor).astype(np.float32) for block in field.blocks]
    if len(blocks) == 1:
        return {name: blocks[0]}
    return {f"{name}_up": blocks[0], f"{name}_down": blocks[1]}


def Charge_Entries(field: FieldFile, volume: float) -> dict[str, NDArray[np.float32]]:
    """Names the charge block and, when present, the magnetization block."""
    entries = {"charge_density": (field.blocks[0] / volume).astype(np.float32)}
    if len(field.blocks) > 1:
        entries["magnetization_density"] = (field.blocks[1] / volume).astype(np.float32)
    return entries


def Geometry_Entries(geometry: Geometry) -> dict[str, StoreArray]:
    """Returns the lattice, fractional positions, and per-atom species symbols."""
    symbols = [symbol for symbol, count in zip(geometry.species, geometry.species_counts) for _ in range(count)]
    return {
        "lattice": geometry.lattice,
        "positions": geometry.positions,
        "species": np.asarray(symbols),
    }


def Extract_Run(census_row: CensusRow, pool_root: Path) -> tuple[dict[str, StoreArray], dict[str, object]]:
    """Extracts one run's arrays and sidecar record from its corpus files."""
    run_directory = pool_root / census_row.path
    arrays: dict[str, StoreArray] = {}
    geometry: Geometry | None = None

    def Present(name: str) -> bool:
        """Returns whether the census and the filesystem agree the file is usable."""
        return census_row.file_sizes.get(name, 0) > 0 and (run_directory / name).is_file()

    if Present("CHGCAR"):
        field = Read_Field_File(run_directory / "CHGCAR")
        geometry = field.geometry
        arrays.update(Charge_Entries(field, Cell_Volume(field.geometry.lattice)))
    aeccar_names = {
        "AECCAR0": "all_electron_core_density",
        "AECCAR1": "superposed_atomic_density",
        "AECCAR2": "all_electron_valence_density",
    }
    for file_name, field_name in aeccar_names.items():
        if Present(file_name):
            field = Read_Field_File(run_directory / file_name)
            geometry = geometry or field.geometry
            arrays[field_name] = (field.blocks[0] / Cell_Volume(field.geometry.lattice)).astype(np.float32)
    if Present("ELFCAR"):
        field = Read_Field_File(run_directory / "ELFCAR")
        geometry = geometry or field.geometry
        arrays.update(Spin_Pair_Entries("electron_localization", field, 1.0))
    if Present("LOCPOT"):
        field = Read_Field_File(run_directory / "LOCPOT")
        geometry = geometry or field.geometry
        arrays.update(Spin_Pair_Entries("local_potential", field, 1.0))
        arrays["local_potential_mean"] = np.asarray([float(np.mean(block)) for block in field.blocks], dtype=np.float64)
    if geometry is None:
        for geometry_file in ("CONTCAR", "POSCAR"):
            if Present(geometry_file):
                geometry, _ = Read_Geometry((run_directory / geometry_file).read_text().splitlines())
                break
    if geometry is None:
        raise StoreError(f"no geometry source in {census_row.path}")
    arrays.update(Geometry_Entries(geometry))
    arrays["cell_volume"] = np.asarray(Cell_Volume(geometry.lattice), dtype=np.float64)
    unreadable: list[str] = []
    if Present("EIGENVAL"):
        try:
            eigenvalues = Read_Eigenvalues(run_directory / "EIGENVAL")
            arrays["kpoints"] = eigenvalues.kpoints
            arrays["kpoint_weights"] = eigenvalues.kpoint_weights
            arrays["eigenvalue_energies"] = eigenvalues.energies
            arrays["eigenvalue_occupancies"] = eigenvalues.occupancies
            arrays["eigenvalue_electron_count"] = np.asarray(eigenvalues.electron_count, dtype=np.float64)
        except (ParseError, ValueError, IndexError):
            unreadable.append("EIGENVAL")
    titles: tuple[str, ...] = ()
    if Present("OUTCAR"):
        try:
            echoes = Read_Outcar_Echoes(run_directory / "OUTCAR")
            arrays["electron_count"] = np.asarray(echoes.electron_count, dtype=np.float64)
            titles = echoes.pseudopotential_titles
        except (ParseError, ValueError, IndexError):
            unreadable.append("OUTCAR")
    if Present("OSZICAR"):
        magnetization = Read_Final_Magnetization(run_directory / "OSZICAR")
        if magnetization is not None:
            arrays["final_magnetization"] = np.asarray(magnetization, dtype=np.float64)
    sidecar: dict[str, object] = {
        "run_path": census_row.path,
        "run_identifier": Run_Identifier(census_row.path),
        "campaign": Campaign_Of(census_row.path),
        "corpus": census_row.corpus,
        "row_hash": census_row.row_hash,
        "extractor_version": EXTRACTOR_VERSION,
        "fields": sorted(arrays),
        "units": {name: UNIT_BY_FIELD.get(name.removesuffix("_up").removesuffix("_down"), "") for name in sorted(arrays)},
        "pseudopotential_titles": list(titles),
        "unreadable_files": unreadable,
        "row": census_row.record,
    }
    return arrays, sidecar


def Write_Run(arrays: dict[str, StoreArray], sidecar: dict[str, object], pool_root: Path) -> Path:
    """Writes one run's archive and sidecar into the store, returning the archive path."""
    campaign_directory = pool_root / STORE_NAME / cast(str, sidecar["campaign"])
    Guard_Volumetric_Destination(campaign_directory, pool_root)
    campaign_directory.mkdir(parents=True, exist_ok=True)
    identifier = cast(str, sidecar["run_identifier"])
    archive_path = campaign_directory / f"{identifier}.npz"
    np.savez(archive_path, **cast(dict[str, Any], arrays))
    (campaign_directory / f"{identifier}.json").write_text(json.dumps(sidecar, indent=1))
    return archive_path


def Sidecar_Paths(pool_root: Path) -> tuple[Path, ...]:
    """Lists every sidecar file currently in the store."""
    store_directory = pool_root / STORE_NAME
    if not store_directory.exists():
        return ()
    return tuple(sorted(path for path in store_directory.glob("*/*.json") if path.name != "manifest.json"))


def Stale_Report(pool_root: Path) -> dict[str, list[str]]:
    """Compares the store against the census and the extractor version."""
    expected: dict[str, str] = {}
    for census_row in Read_Census(pool_root):
        expected[Run_Identifier(census_row.path)] = census_row.row_hash
    fresh: list[str] = []
    stale: list[str] = []
    orphaned: list[str] = []
    seen: set[str] = set()
    for sidecar_path in Sidecar_Paths(pool_root):
        sidecar = cast(dict[str, object], json.loads(sidecar_path.read_text()))
        identifier = cast(str, sidecar["run_identifier"])
        seen.add(identifier)
        if identifier not in expected:
            orphaned.append(identifier)
        elif sidecar.get("row_hash") != expected[identifier] or sidecar.get("extractor_version") != EXTRACTOR_VERSION:
            stale.append(identifier)
        else:
            fresh.append(identifier)
    missing = sorted(set(expected) - seen)
    return {"fresh": fresh, "stale": stale, "missing": missing, "orphaned": orphaned}


def Build_One(census_row: CensusRow, pool_root: Path) -> tuple[str, str | None]:
    """Extracts and writes one run, returning its identifier and any error text."""
    try:
        arrays, sidecar = Extract_Run(census_row, pool_root)
        Write_Run(arrays, sidecar, pool_root)
        return Run_Identifier(census_row.path), None
    except (ParseError, StoreError, OSError, ValueError, IndexError) as error:
        return Run_Identifier(census_row.path), f"{census_row.path}: {error}"


def Write_Manifests(pool_root: Path) -> None:
    """Writes one manifest per campaign mapping identifiers to run paths and fields."""
    by_campaign: dict[str, dict[str, object]] = {}
    for sidecar_path in Sidecar_Paths(pool_root):
        sidecar = cast(dict[str, object], json.loads(sidecar_path.read_text()))
        campaign = cast(str, sidecar["campaign"])
        archive = sidecar_path.with_suffix(".npz")
        by_campaign.setdefault(campaign, {})[cast(str, sidecar["run_identifier"])] = {
            "run_path": sidecar["run_path"],
            "fields": sidecar["fields"],
            "bytes": archive.stat().st_size if archive.exists() else 0,
        }
    for campaign, entries in by_campaign.items():
        manifest_path = pool_root / STORE_NAME / campaign / "manifest.json"
        manifest_path.write_text(json.dumps(entries, indent=1, sort_keys=True))


def Build_Store(
    pool_root: Path,
    campaign: str | None = None,
    limit: int | None = None,
    processes: int = 1,
    rebuild: bool = False,
) -> dict[str, object]:
    """Builds every missing or stale run archive and returns the build report."""
    report = Stale_Report(pool_root)
    wanted = set(report["missing"]) | set(report["stale"]) if not rebuild else None
    selected: list[CensusRow] = []
    for census_row in Read_Census(pool_root):
        if campaign is not None and Campaign_Of(census_row.path) != campaign:
            continue
        if wanted is not None and Run_Identifier(census_row.path) not in wanted:
            continue
        selected.append(census_row)
        if limit is not None and len(selected) >= limit:
            break
    failures: list[str] = []
    if processes > 1:
        with ProcessPoolExecutor(max_workers=processes) as pool:
            for _, error in pool.map(Build_One, selected, [pool_root] * len(selected), chunksize=4):
                if error is not None:
                    failures.append(error)
    else:
        for census_row in selected:
            _, error = Build_One(census_row, pool_root)
            if error is not None:
                failures.append(error)
    Write_Manifests(pool_root)
    built_report: dict[str, object] = {
        "extractor_version": EXTRACTOR_VERSION,
        "selected": len(selected),
        "failed": len(failures),
        "failures": failures,
    }
    report_path = pool_root / STORE_NAME / "build_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(built_report, indent=1))
    return built_report


def Main(argv: list[str] | None = None) -> int:
    """Runs the store builder from the command line."""
    parser = argparse.ArgumentParser(description="Build the derived tensor store on the corpus partition.")
    parser.add_argument("--campaign", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--processes", type=int, default=1)
    parser.add_argument("--rebuild", action="store_true")
    arguments = parser.parse_args(argv)
    report = Build_Store(
        POOL_ROOT,
        campaign=cast(str | None, arguments.campaign),
        limit=cast(int | None, arguments.limit),
        processes=cast(int, arguments.processes),
        rebuild=cast(bool, arguments.rebuild),
    )
    print(json.dumps({key: report[key] for key in ("selected", "failed")}))
    for failure in cast(list[str], report["failures"])[:20]:
        print(failure)
    return 1 if cast(int, report["failed"]) else 0


if __name__ == "__main__":
    raise SystemExit(Main())

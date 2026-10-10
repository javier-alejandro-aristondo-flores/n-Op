"""A3 parts two and three: raw VASP files read by a separately written reader against the store, sampled over every campaign and file kind, and the core maxima of the all-electron core density against the atom positions on cells that are not cubic"""

import json
import random
from pathlib import Path

import numpy as np

POOL = Path("/Pool/VASP_DATA")
STORE = POOL / "_derived"
FIELD_FILES = {"CHGCAR": "charge_density", "AECCAR0": "all_electron_core_density",
               "AECCAR1": "superposed_atomic_density", "AECCAR2": "all_electron_valence_density",
               "ELFCAR": "electron_localization", "LOCPOT": "local_potential"}
DIVIDED_BY_VOLUME = {"CHGCAR", "AECCAR0", "AECCAR1", "AECCAR2"}


def Header_And_Grid_Start(lines: list[str]) -> tuple[np.ndarray, list[str], list[int], np.ndarray, int]:
    """lattice rows in angstrom, species, counts, fractional positions, and the index of the first grid line (the deep dive's reader)"""
    scale = float(lines[1].split()[0])
    lattice = np.array([[float(token) for token in lines[row].split()[:3]] for row in (2, 3, 4)])
    lattice = lattice * ((-scale / abs(np.linalg.det(lattice))) ** (1 / 3) if scale < 0 else scale)
    species = lines[5].split()
    counts = [int(token) for token in lines[6].split()]
    cursor = 7
    if lines[cursor].strip()[:1].lower() == "s":
        cursor += 1
    mode = lines[cursor].strip()[:1].lower()
    cursor += 1
    atom_count = sum(counts)
    positions = np.array([[float(token) for token in lines[cursor + atom].split()[:3]] for atom in range(atom_count)])
    if mode in ("c", "k"):
        positions = positions @ np.linalg.inv(lattice)
    cursor += atom_count
    while not lines[cursor].strip():
        cursor += 1
    return lattice, species, counts, positions, cursor


def Read_Blocks(path: Path, wanted: int) -> tuple[np.ndarray, list[str], np.ndarray, tuple[int, int, int], list[np.ndarray]]:
    """up to the wanted number of grid blocks, each as a (nx, ny, nz) array read x fastest, as the file stores it"""
    lines = path.read_text().splitlines()
    lattice, species, _, positions, cursor = Header_And_Grid_Start(lines)
    dimension_tokens = lines[cursor].split()
    dimensions = (int(dimension_tokens[0]), int(dimension_tokens[1]), int(dimension_tokens[2]))
    total = dimensions[0] * dimensions[1] * dimensions[2]
    blocks: list[np.ndarray] = []
    while len(blocks) < wanted:
        collected: list[str] = []
        count = 0
        row = cursor + 1
        while count < total:
            tokens = lines[row].split()
            collected.extend(tokens)
            count += len(tokens)
            row += 1
        values = np.array(collected[:total], dtype=np.float64)
        blocks.append(values.reshape(dimensions, order="F"))
        cursor = row
        while cursor < len(lines) and lines[cursor].split() != dimension_tokens:
            cursor += 1
        if cursor >= len(lines):
            break
    return lattice, species, positions, dimensions, blocks


def Relative_Gap(mine: np.ndarray, stored: np.ndarray) -> float:
    """the largest absolute difference relative to the largest stored magnitude"""
    stored = np.asarray(stored, dtype=np.float64)
    return float(np.max(np.abs(mine - stored)) / max(np.max(np.abs(stored)), 1e-30))


def Compare_Run(run_path: str, archive_path: Path) -> dict[str, object]:
    """every field file present in one run against its stored arrays, plus geometry and the electron count"""
    result: dict[str, object] = {"run": run_path}
    run_directory = POOL / run_path
    with np.load(archive_path) as archive:
        stored = {name: archive[name] for name in archive.files}
    volume = float(stored["cell_volume"])
    for file_name, field_name in FIELD_FILES.items():
        path = run_directory / file_name
        if not path.is_file() or path.stat().st_size == 0:
            continue
        spin_names = [f"{field_name}_up", f"{field_name}_down"]
        wanted = 2 if (file_name in ("CHGCAR",) and "magnetization_density" in stored) or spin_names[0] in stored else 1
        lattice, species, positions, dimensions, blocks = Read_Blocks(path, wanted)
        divisor = volume if file_name in DIVIDED_BY_VOLUME else 1.0
        if file_name == "CHGCAR":
            result["CHGCAR block 1 / volume vs charge_density"] = Relative_Gap(blocks[0] / divisor, stored["charge_density"])
            # control: the same comparison read z fastest must fail
            result["CONTROL CHGCAR read z fastest"] = Relative_Gap(blocks[0].reshape(-1, order="F").reshape(dimensions, order="C") / divisor, stored["charge_density"]) if len(set(dimensions)) == 1 else None
            if len(blocks) > 1:
                result["CHGCAR block 2 / volume vs magnetization_density"] = Relative_Gap(blocks[1] / divisor, stored["magnetization_density"])
            result["lattice max gap"] = float(np.max(np.abs(lattice - stored["lattice"])))
            wrapped = (positions - stored["positions"] + 0.5) % 1.0 - 0.5
            result["positions max fractional gap"] = float(np.max(np.abs(wrapped)))
        elif spin_names[0] in stored:
            result[f"{file_name} block 1 vs {spin_names[0]}"] = Relative_Gap(blocks[0] / divisor, stored[spin_names[0]])
            result[f"{file_name} block 2 vs {spin_names[1]}"] = Relative_Gap(blocks[1] / divisor, stored[spin_names[1]]) if len(blocks) > 1 else "second block missing"
        elif field_name in stored:
            result[f"{file_name} block 1 vs {field_name}"] = Relative_Gap(blocks[0] / divisor, stored[field_name])
        else:
            result[f"{file_name} present on disk but no stored {field_name}"] = True
    outcar = run_directory / "OUTCAR"
    if outcar.is_file() and "electron_count" in stored:
        with outcar.open(errors="replace") as stream:
            for line in stream:
                if "NELECT" in line:
                    result["OUTCAR NELECT minus stored electron_count"] = float(line.split()[2]) - float(stored["electron_count"])
                    break
    eigenval = run_directory / "EIGENVAL"
    if eigenval.is_file() and eigenval.stat().st_size > 0 and "eigenvalue_energies" in stored:
        lines = eigenval.read_text().splitlines()
        electrons, kpoint_count, band_count = (int(token) for token in lines[5].split()[:3])
        result["EIGENVAL electrons, kpoints, bands"] = [electrons, kpoint_count, band_count]
        result["stored energies shape"] = list(stored["eigenvalue_energies"].shape)
        first_band = lines[8].split()
        result["EIGENVAL first energy minus stored"] = float(first_band[1]) - float(np.asarray(stored["eigenvalue_energies"]).reshape(-1)[0])
    return result


def Core_Maxima_Check(archive_path: Path) -> dict[str, object]:
    """whether each atom sits on a local maximum of the core density, in the stored axis order and in a permuted one"""
    with np.load(archive_path) as archive:
        core = np.asarray(archive["all_electron_core_density"], dtype=np.float64)
        positions = np.asarray(archive["positions"], dtype=np.float64)
    shape = np.array(core.shape)

    def Nearest_Maximum_Distances(field: np.ndarray, field_shape: np.ndarray) -> np.ndarray:
        """for each atom, the periodic voxel distance to the highest voxel within two voxels of it, relative to its own voxel"""
        distances = []
        for position in positions:
            center = np.rint(position * field_shape).astype(int)
            best_value, best_offset = -np.inf, np.zeros(3)
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    for dz in range(-2, 3):
                        index = tuple((center + (dx, dy, dz)) % field_shape)
                        if field[index] > best_value:
                            best_value, best_offset = field[index], np.array((dx, dy, dz))
            distances.append(np.linalg.norm(best_offset))
        return np.array(distances)

    own = Nearest_Maximum_Distances(core, shape)
    # the atoms' own voxels hold the core peaks; the share of atoms whose peak value is high tells the orientation
    peak_share = float(np.mean([core[tuple(np.rint(p * shape).astype(int) % shape)] > np.percentile(core, 99) for p in positions]))
    permuted = np.transpose(core, (2, 1, 0))
    permuted_shape = np.array(permuted.shape)
    peak_share_permuted = float(np.mean([permuted[tuple(np.rint(p * permuted_shape).astype(int) % permuted_shape)] > np.percentile(core, 99) for p in positions]))
    return {"grid": core.shape, "atoms": len(positions), "atoms on a top-1% voxel, stored order": peak_share,
            "CONTROL atoms on a top-1% voxel, axes reversed": peak_share_permuted,
            "median distance to the local maximum (voxels)": float(np.median(own))}


def Main() -> None:
    """samples two runs per campaign that has field files, compares them, then runs the orientation check on non-cubic cells"""
    rng = random.Random(20260925)
    report: dict[str, object] = {"raw_vs_store": {}, "orientation": {}}
    for campaign in ("strain_atlas", "supercell_strains", "defect_set", "perovskite_grid", "alloy_ensemble", "relaxation_pool"):
        sidecars = sorted(path for path in (STORE / campaign).glob("*.json") if path.name != "manifest.json")
        for sidecar_path in rng.sample(sidecars, 2):
            run_path = json.loads(sidecar_path.read_text())["run_path"]
            report["raw_vs_store"][f"{campaign}: {run_path}"] = Compare_Run(run_path, sidecar_path.with_suffix(".npz"))
    alloy = sorted(path for path in (STORE / "alloy_ensemble").glob("*.npz"))
    with_core = [path for path in alloy if "all_electron_core_density" in np.load(path).files]
    for archive_path in rng.sample(with_core, min(3, len(with_core))):
        run_path = json.loads(archive_path.with_suffix(".json").read_text())["run_path"]
        report["orientation"][run_path] = Core_Maxima_Check(archive_path)
    print(json.dumps(report, indent=1, default=str))


if __name__ == "__main__":
    Main()

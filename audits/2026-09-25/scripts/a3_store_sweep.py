"""A3 part one: every archive's charge and magnetization integrals, field ranges and species labels, against its own electron count, moment and OUTCAR elements"""

import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

STORE = Path("/Pool/VASP_DATA/_derived")
CAMPAIGNS = ("alloy_ensemble", "defect_set", "perovskite_grid", "relaxation_pool", "strain_atlas", "supercell_strains",
             "uncatalogued")


def Element_Of_Title(title: str) -> str:
    """the element symbol a pseudopotential title names, from its second word, never the title itself"""
    words = title.split()
    match = re.match(r"[A-Z][a-z]?", words[1]) if len(words) > 1 else None
    return match.group(0) if match else "?"


def Species_Order(per_atom: np.ndarray) -> list[str]:
    """the species blocks in file order, collapsing each run of equal symbols"""
    order: list[str] = []
    for symbol in per_atom.tolist():
        if not order or order[-1] != symbol:
            order.append(str(symbol))
    return order


def Measure(archive_path: Path) -> dict[str, object]:
    """one archive's integrals, ranges and label comparison"""
    sidecar = json.loads(archive_path.with_suffix(".json").read_text())
    record: dict[str, object] = {"run": sidecar["run_path"], "campaign": archive_path.parent.name}
    with np.load(archive_path) as archive:
        names = set(archive.files)
        volume = float(archive["cell_volume"]) if "cell_volume" in names else float("nan")
        electrons = float(archive["electron_count"]) if "electron_count" in names else float("nan")
        record["electron_count"] = electrons
        if "charge_density" in names:
            density = np.asarray(archive["charge_density"], dtype=np.float64)
            record["charge_integral"] = float(density.mean() * volume)
            record["charge_minimum"] = float(density.min())
        if "magnetization_density" in names:
            magnetization = np.asarray(archive["magnetization_density"], dtype=np.float64)
            record["magnetization_integral"] = float(magnetization.mean() * volume)
            record["magnetization_above_density_voxels"] = int(np.sum(np.abs(magnetization) > density)) if "charge_density" in names else -1
        if "final_magnetization" in names:
            record["final_magnetization"] = float(archive["final_magnetization"])
        for spin in ("", "_up", "_down"):
            key = f"electron_localization{spin}"
            if key in names:
                field = archive[key]
                record[f"elf{spin}_range"] = [float(field.min()), float(field.max())]
        if "local_potential_up" in names and "local_potential_down" in names:
            up = np.asarray(archive["local_potential_up"], dtype=np.float64)
            down = np.asarray(archive["local_potential_down"], dtype=np.float64)
            record["potential_up_mean_abs"] = float(np.mean(np.abs(up)))
            record["potential_down_mean_abs"] = float(np.mean(np.abs(down)))
            record["potential_up_minus_down_max_abs"] = float(np.max(np.abs(up - down)))
        for aeccar in ("all_electron_valence_density", "superposed_atomic_density"):
            if aeccar in names:
                record[f"{aeccar}_integral"] = float(np.asarray(archive[aeccar], dtype=np.float64).mean() * volume)
        if "species" in names:
            record["header_species"] = Species_Order(archive["species"])
    titles = sidecar.get("pseudopotential_titles") or []
    record["outcar_elements"] = [Element_Of_Title(str(title)) for title in titles]
    return record


def Main() -> None:
    """writes one JSON line per archive to the named file, then prints the checks' summaries"""
    archives = sorted(path for campaign in CAMPAIGNS for path in (STORE / campaign).glob("*.npz"))
    with ProcessPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(Measure, archives, chunksize=8))
    with Path(sys.argv[1]).open("w") as stream:
        for record in records:
            stream.write(json.dumps(record) + "\n")
    print(f"{len(records)} archives measured")


if __name__ == "__main__":
    Main()

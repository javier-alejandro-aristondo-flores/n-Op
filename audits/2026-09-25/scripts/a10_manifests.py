"""A10: every training manifest on the volume as one table, beside the dates of the checkpoint and curve files next to it"""

import json
import sys
from datetime import datetime
from pathlib import Path

TRAINING = Path("/Pool/VASP_DATA/_derived/_training")
FIELDS = ("step_count", "completed_steps", "resumed_from_step", "stopped_early", "best_step", "best_validation_score",
          "seed", "learning_rate", "patience", "validation_interval", "validation_unit_count", "wall_clock_seconds",
          "device", "working_precision", "engine", "hook_present")


def Stamp(path: Path) -> str:
    """a file's modification time as local ISO text, or a dash when absent"""
    return datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds") if path.exists() else "-"


def Main() -> None:
    """writes a tab-separated table to the named file and prints a count"""
    rows: list[str] = []
    header = ["member", "run", *FIELDS, "manifest_time", "checkpoint_time", "curves_time", "stray_keys"]
    rows.append("\t".join(header))
    for manifest_path in sorted(TRAINING.glob("*/*_manifest.json")):
        member = manifest_path.parent.name
        run = manifest_path.name.removesuffix("_manifest.json")
        manifest = json.loads(manifest_path.read_text())
        checkpoint_time = Stamp(manifest_path.parent / f"{run}_checkpoint.npz")
        stray = sorted(set(manifest) - set(FIELDS) - {"run_name", "parameter_names", "final_loss"})
        values = [str(manifest.get(field, "")) for field in FIELDS]
        rows.append("\t".join([member, run, *values, Stamp(manifest_path), checkpoint_time,
                               Stamp(manifest_path.parent / f"{run}_curves.npz"), ",".join(stray)]))
    Path(sys.argv[1]).write_text("\n".join(rows) + "\n")
    print(f"{len(rows) - 1} manifests tabulated")


if __name__ == "__main__":
    Main()

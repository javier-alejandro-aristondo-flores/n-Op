"""lists every entry added, removed or changed between two fingerprint files, by content, time and permission separately"""

import sys
from pathlib import Path


def Read_Fingerprints(path: Path) -> dict[str, tuple[str, str, str, str, str]]:
    """path to (kind, size, mtime, mode, sha256)"""
    table: dict[str, tuple[str, str, str, str, str]] = {}
    for line in path.read_text().splitlines():
        name, kind, size, mtime, mode, digest = line.split("\t")
        table[name] = (kind, size, mtime, mode, digest)
    return table


def Main() -> None:
    """prints one line per difference and a closing count; exits nonzero when anything differs"""
    before = Read_Fingerprints(Path(sys.argv[1]))
    after = Read_Fingerprints(Path(sys.argv[2]))
    ignore_modes = "--ignore-modes" in sys.argv[3:]
    differences: list[str] = []
    for name in sorted(before.keys() - after.keys()):
        differences.append(f"removed\t{name}")
    for name in sorted(after.keys() - before.keys()):
        differences.append(f"added\t{name}")
    for name in sorted(before.keys() & after.keys()):
        old, new = before[name], after[name]
        changed = []
        if old[4] != new[4] or old[1] != new[1]:
            changed.append("content")
        if old[2] != new[2] and old[0] == "file":
            changed.append("mtime")
        if old[3] != new[3] and not ignore_modes:
            changed.append(f"mode {old[3]}->{new[3]}")
        if changed:
            differences.append(f"changed[{','.join(changed)}]\t{name}")
    for line in differences:
        print(line)
    print(f"{len(differences)} differences over {len(before)} before and {len(after)} after")
    sys.exit(1 if differences else 0)


if __name__ == "__main__":
    Main()

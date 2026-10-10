"""records permission bits, then makes the derived store read-only and every pseudopotential file unreadable, or restores the recorded bits"""

import os
import stat
import sys
from pathlib import Path


READ_ONLY_ROOTS = (Path("/Pool/VASP_DATA/_derived"), Path("/Pool/VASP_DATA/_census"))
PSEUDOPOTENTIAL_SEARCH_ROOT = Path("/Pool")
WRITE_BITS = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
READ_BITS = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH


def Read_Only_Targets() -> list[Path]:
    """every directory and file under the roots that must not change during the audit"""
    targets: list[Path] = []
    for root in READ_ONLY_ROOTS:
        for directory, _, files in os.walk(root, followlinks=False):
            targets.append(Path(directory))
            targets.extend(Path(directory) / name for name in files)
    return targets


def Pseudopotential_Targets() -> list[Path]:
    """every regular file on the volume whose name starts with the pseudopotential file name, case folded"""
    targets: list[Path] = []
    for directory, subdirectories, files in os.walk(PSEUDOPOTENTIAL_SEARCH_ROOT, followlinks=False):
        subdirectories[:] = [name for name in subdirectories if not name.startswith("lost+found")]
        for name in files:
            if name.upper().startswith("POTCAR"):
                path = Path(directory) / name
                if stat.S_ISREG(os.lstat(path).st_mode):
                    targets.append(path)
    return targets


def Record(record_path: Path) -> None:
    """writes kind, octal mode and path for every target, before anything is changed"""
    with record_path.open("x") as stream:
        for kind, targets in (("read_only", Read_Only_Targets()), ("unreadable", Pseudopotential_Targets())):
            for path in targets:
                stream.write(f"{kind}\t{stat.S_IMODE(os.lstat(path).st_mode):o}\t{path}\n")
    print(f"recorded {sum(1 for _ in record_path.open())} targets in {record_path}")


def Recorded(record_path: Path) -> list[tuple[str, int, Path]]:
    """the kind, original mode and path of every recorded target"""
    rows: list[tuple[str, int, Path]] = []
    for line in record_path.read_text().splitlines():
        kind, mode, name = line.split("\t", 2)
        rows.append((kind, int(mode, 8), Path(name)))
    return rows


def Apply(record_path: Path) -> None:
    """clears write bits on the read-only targets and read bits on the pseudopotential files"""
    failures = 0
    for kind, mode, path in Recorded(record_path):
        cleared = mode & ~WRITE_BITS if kind == "read_only" else mode & ~READ_BITS
        try:
            os.chmod(path, cleared, follow_symlinks=False)
        except OSError as error:
            failures += 1
            print(f"failed\t{path}\t{error}")
    print(f"applied to {len(Recorded(record_path))} targets, {failures} failures")


def Restore(record_path: Path) -> None:
    """sets every recorded target back to its recorded mode, files before the directories that hold them"""
    rows = Recorded(record_path)
    failures = 0
    for _, mode, path in sorted(rows, key=lambda row: -len(row[2].parts)):
        try:
            os.chmod(path, mode, follow_symlinks=False)
        except OSError as error:
            failures += 1
            print(f"failed\t{path}\t{error}")
    mismatches = sum(1 for _, mode, path in rows if stat.S_IMODE(os.lstat(path).st_mode) != mode)
    print(f"restored {len(rows)} targets, {failures} failures, {mismatches} modes differ from the record")


def Main() -> None:
    """record, apply or restore, against one record file"""
    action, record_path = sys.argv[1], Path(sys.argv[2])
    {"record": Record, "apply": Apply, "restore": Restore}[action](record_path)


if __name__ == "__main__":
    Main()

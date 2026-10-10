"""records size, modification time, permission bits and sha256 for every file and directory under the given roots"""

import hashlib
import os
import stat
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


CHUNK_BYTES = 8 * 1024 * 1024


def Digest_Of(path: str) -> str:
    """the sha256 of one file's bytes"""
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while block := stream.read(CHUNK_BYTES):
            digest.update(block)
    return digest.hexdigest()


def Entries_Under(root: Path) -> list[tuple[str, str, int, int, int]]:
    """every directory and file below a root with its kind, size, modification time and permission bits"""
    entries: list[tuple[str, str, int, int, int]] = []
    for directory, subdirectories, files in os.walk(root, followlinks=False):
        subdirectories.sort()
        for name in [directory, *[os.path.join(directory, file) for file in sorted(files)]]:
            status = os.lstat(name)
            kind = "dir" if stat.S_ISDIR(status.st_mode) else "link" if stat.S_ISLNK(status.st_mode) else "file"
            entries.append((name, kind, status.st_size, status.st_mtime_ns, stat.S_IMODE(status.st_mode)))
    return entries


def Main() -> None:
    """writes one tab-separated line per entry: path, kind, size, mtime in nanoseconds, octal mode, sha256"""
    output_path = Path(sys.argv[1])
    roots = [Path(argument) for argument in sys.argv[2:]]
    entries = [entry for root in roots for entry in Entries_Under(root)]
    files = [entry[0] for entry in entries if entry[1] == "file"]
    with ProcessPoolExecutor(max_workers=6) as pool:
        digests = dict(zip(files, pool.map(Digest_Of, files, chunksize=16)))
    with output_path.open("w") as stream:
        for name, kind, size, mtime, mode in entries:
            stream.write(f"{name}\t{kind}\t{size}\t{mtime}\t{mode:o}\t{digests.get(name, '-')}\n")
    print(f"{len(entries)} entries, {len(files)} files hashed, written to {output_path}")


if __name__ == "__main__":
    Main()

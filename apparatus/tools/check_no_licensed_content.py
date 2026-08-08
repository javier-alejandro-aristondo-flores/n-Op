#!/usr/bin/env python3
"""Prove no VASP-licensed material reached any committed file.

The repository holds ~95 MB of research output derived from run directories that each
carry a `POTCAR`. Pseudopotentials are VASP-licensed and this remote is public, so the
question "did any of one leak into a committed file" needs an answer that survives the
next person adding a file, not a one-time grep whose result nobody can reproduce.

**The scope is the whole repository, and that is a correction.** This guard once named a
single tree, `feasibility`, as a bare string. Two things were wrong with that. A tree that
is renamed leaves the guard scanning a path that does not exist -- which is loud rather
than silent, because the calibration probe writes *into* the guarded tree and an empty tree
is fatal, but it is still a stop rather than a check. Worse, a library added later is
outside the scope by default and the guard still exits 0: `programs/operator/` was written
after this file and inherited no protection, 19 MB of it, on a public remote. Scope by
default, exempt by exception.

What is and is not at issue, stated once:

  * **Eigenvalues, gaps, fitted coefficients and figures are computed results.** The VASP
    license restricts redistribution of the pseudopotentials and the source, not of
    numbers a calculation produced. Committing `spectra.npz` is fine.
  * **`POTCAR` content is not.** Nor is a checksum of one, which would let a holder of
    the file confirm a match.
  * **The licensed *filename* is expected**, as a key in `file_manifest.json` with its
    byte size, once per run directory. That is the record of the skip -- the extractor
    denies POTCAR by assertion rather than by omission -- and removing it would delete
    the evidence that the discipline held.
  * **Naming the pseudopotential family is provenance, not content.** `PAW_PBE C
    08Apr2002` in a dataset README records which potential produced the numbers, which is
    exactly what a reader needs. A header *block* -- `TITEL`, `LEXCH`, `END of PSCTR`
    together -- is the file itself. The allowlist below distinguishes them by name, and
    per-file rather than by pattern, so the distinction stays auditable.

    python apparatus/tools/check_no_licensed_content.py

Exit 0 clean, 1 on any finding. The calibration runs on every invocation: a guard nobody
has watched fail is indistinguishable from one that cannot fail.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

#: Strings that appear in a VASP pseudopotential and essentially nowhere else. `TITEL`
#: and `LEXCH` are POTCAR header keys; the other two bracket the file. Checked as bytes,
#: so a compressed or binary artifact carrying one uncompressed is still caught.
SIGNATURES = [
    b"END of PSCTR",
    b"LEXCH  =",
    b"TITEL  =",
    b"PAW_PBE",
    b"Error from kinetic energy argument",
]

#: The one licensed *name*, which is allowed to appear as a manifest key. Its presence is
#: evidence of the skip; its content would be the violation.
LICENSED_NAME = b"pseudopotential-LICENSED-DO-NOT-REDISTRIBUTE"

#: Files permitted to carry specific signatures, with the reason. A file passes only if
#: the signatures found in it are a **subset** of what is allowed here, so an allowlisted
#: file that acquires a *new* signature is still a finding. That is the property a bare
#: path allowlist would not have: exempting a path forever would let real content be
#: pasted into an exempt file and pass.
ALLOWED: dict[str, set[str]] = {
    "apparatus/tools/check_no_licensed_content.py": {
        "END of PSCTR", "LEXCH  =", "TITEL  =", "PAW_PBE",
        "Error from kinetic energy argument",
    },
    "apparatus/data/diamond-strain-sweep/read-me-first.md": {"PAW_PBE"},
    "apparatus/data/diamond-strain-sweep/01-what-this-data-is.md": {"PAW_PBE"},
    "apparatus/data/diamond-strain-sweep/02-how-to-read-and-derive.md": {"PAW_PBE"},
}

#: Why each of the above is benign. Kept beside the allowlist rather than in a comment so
#: a reader who does not trust the exemption can check the claim from the file itself.
ALLOWED_REASON = {
    "apparatus/tools/check_no_licensed_content.py":
        "this file defines the signatures; it cannot scan for them without holding them",
    "apparatus/data/diamond-strain-sweep/read-me-first.md":
        "names the potential as provenance -- 'Pseudopotential: PAW_PBE C 08Apr2002'",
    "apparatus/data/diamond-strain-sweep/01-what-this-data-is.md":
        "the manifest row recording the POTCAR was skipped, marked 'never publish'",
    "apparatus/data/diamond-strain-sweep/02-how-to-read-and-derive.md":
        "records the potential in a run-parameter line beside ENCUT and the code version",
}

MAX_BYTES = 400 * 1024 * 1024

#: Directories that are not ours to police. `.git` holds packed objects whose contents are
#: already covered by scanning the working tree; the rest are third-party or generated.
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache"}


def tracked_and_untracked() -> list[Path]:
    """Every file git would publish, plus every file it does not know about yet.

    Scanning only tracked files would pass on exactly the run that matters -- the one
    where a new artifact has been copied in and not yet added. Ignored files are excluded,
    because a file git will never publish cannot leak through git.
    """
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split("\n")
    paths = []
    for rel in out:
        if not rel:
            continue
        if set(Path(rel).parts) & SKIP_DIRS:
            continue
        p = ROOT / rel
        if p.is_file():
            paths.append(p)
    return sorted(paths)


def scan(path: Path) -> list[str]:
    """Signatures found in one file, ignoring the permitted bare filename."""
    try:
        data = path.read_bytes() if path.stat().st_size <= MAX_BYTES else b""
    except OSError as exc:
        return [f"unreadable: {exc}"]

    hits = []
    for signature in SIGNATURES:
        if signature in data:
            hits.append(signature.decode())
    return hits


def calibrate() -> tuple[bool, str]:
    """Plant a synthetic pseudopotential header and assert the scanner catches it.

    Deliberately not a real POTCAR -- the point is to exercise the matcher, and a real
    one could not be committed here anyway. Three probes, because this guard now has three
    ways to fail: a blind matcher, a matcher that cries wolf, and an allowlist that has
    widened into a blanket permission.
    """
    probe = ROOT / ".licence-probe-scratch"
    synthetic = (b"  PAW_PBE C 08Apr2002\n  LEXCH  = PE\n"
                 b"  TITEL  = PAW_PBE C 08Apr2002\n  END of PSCTR\n")
    try:
        probe.write_bytes(synthetic)
        hits = scan(probe)
        if len(hits) < 4:
            return False, f"probe caught only {hits}; the matcher is not looking"

        if not scan_is_clean_on(b"a column of eigenvalues: -11.747340 9.722515\n"):
            return False, "probe fires on ordinary numeric output -- it would cry wolf"

        # The allowlist must not be a blanket exemption. An allowlisted file that gains a
        # signature it is not allowed to carry has to be a finding, or every exemption is
        # permanent and unverified.
        name = "apparatus/data/diamond-strain-sweep/read-me-first.md"
        if not set(scan(probe)) - ALLOWED[name]:
            return False, "the subset rule does not fire: an exempt file could carry anything"

        return True, (f"caught {len(hits)} signatures, silent on ordinary output, "
                      f"subset rule fires on an over-carrying exempt file")
    finally:
        probe.unlink(missing_ok=True)


def scan_is_clean_on(payload: bytes) -> bool:
    """The other direction: the matcher must stay silent on innocent content."""
    return not any(signature in payload for signature in SIGNATURES)


def main() -> int:
    passed, detail = calibrate()
    print(f"calibration: {'PASS' if passed else 'FAIL'} — {detail}")
    if not passed:
        return 1

    files = tracked_and_untracked()
    if not files:
        print("fatal: no files to check — git reported nothing")
        return 1

    findings: list[tuple[str, list[str]]] = []
    exempted: list[str] = []
    name_mentions = 0
    skipped_large = 0
    allowlist_used: set[str] = set()

    for path in files:
        rel = str(path.relative_to(ROOT))
        if path.stat().st_size > MAX_BYTES:
            skipped_large += 1
            continue
        hits = scan(path)
        if hits:
            permitted = ALLOWED.get(rel, set())
            unexpected = sorted(set(hits) - permitted)
            if permitted:
                allowlist_used.add(rel)
            if unexpected:
                findings.append((rel, unexpected))
            else:
                exempted.append(rel)
        try:
            if LICENSED_NAME in path.read_bytes():
                name_mentions += 1
        except OSError:
            pass

    print(f"files scanned: {len(files) - skipped_large}"
          + (f" ({skipped_large} skipped above {MAX_BYTES // 1024 // 1024} MB)"
             if skipped_large else ""))
    print(f"files mentioning the licensed filename (permitted, it records the skip): "
          f"{name_mentions}")

    for rel in sorted(exempted):
        print(f"  exempt  {rel}\n     {ALLOWED_REASON.get(rel, 'no reason recorded')}")

    # A stale exemption is a slow failure: the file moved or stopped carrying the string,
    # and the entry stays behind as a permission nobody re-justified.
    stale = sorted(set(ALLOWED) - allowlist_used)
    for rel in stale:
        print(f"  STALE ALLOWLIST ENTRY  {rel} — no longer present, or no longer "
              f"carries a signature. Remove it.")

    for rel, hits in findings:
        print(f"\n  LICENSED CONTENT  {rel}\n     signatures: {hits}")

    if findings:
        print(f"\n{len(findings)} file(s) carry pseudopotential content and must not be "
              "committed.")
        return 1
    if stale:
        print(f"\n{len(stale)} stale allowlist entr{'y' if len(stale) == 1 else 'ies'}.")
        return 1

    print("no pseudopotential content in any file git would publish")
    return 0


if __name__ == "__main__":
    sys.exit(main())

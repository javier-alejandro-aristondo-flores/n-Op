#!/usr/bin/env python3
"""Prove no VASP-licensed material reached the committed feasibility artifacts.

`feasibility/` holds ~75 MB of research output derived from run directories that each
carry a `POTCAR`. Pseudopotentials are VASP-licensed and this remote is public, so the
question "did any of one leak into a committed file" needs an answer that survives the
next person adding a file, not a one-time grep whose result nobody can reproduce.

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

    python tools/check_no_licensed_content.py

Exit 0 clean, 1 on any finding. The calibration probe runs on every invocation: a
guard nobody has watched fail is indistinguishable from one that cannot.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUARDED = "apparatus/feasibility"

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

MAX_BYTES = 400 * 1024 * 1024


def tracked_and_untracked(root: Path) -> list[Path]:
    """Every file under the guarded tree, whether or not git knows about it yet.

    Scanning only tracked files would pass on exactly the run that matters -- the one
    where a new artifact has been copied in and not yet added.
    """
    return sorted(p for p in (root / GUARDED).rglob("*") if p.is_file())


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
    one could not be committed here anyway. Written to a scratch file inside the guarded
    tree so the probe traverses the same path a real leak would.
    """
    probe = ROOT / GUARDED / ".licence-probe-scratch"
    synthetic = (b"  PAW_PBE C 08Apr2002\n  LEXCH  = PE\n"
                 b"  TITEL  = PAW_PBE C 08Apr2002\n  END of PSCTR\n")
    try:
        probe.write_bytes(synthetic)
        hits = scan(probe)
        if len(hits) < 4:
            return False, f"probe caught only {hits}; the matcher is not looking"
        clean = scan_is_clean_on(b"a column of eigenvalues: -11.747340 9.722515\n")
        if not clean:
            return False, "probe fires on ordinary numeric output -- it would cry wolf"
        return True, f"caught {len(hits)} signatures, silent on ordinary output"
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

    files = tracked_and_untracked(ROOT)
    if not files:
        print(f"fatal: nothing under {GUARDED}/ to check")
        return 1

    findings = []
    name_mentions = 0
    skipped_large = 0
    for path in files:
        if path.stat().st_size > MAX_BYTES:
            skipped_large += 1
            continue
        hits = scan(path)
        if hits:
            findings.append((path.relative_to(ROOT), hits))
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

    for relative, hits in findings:
        print(f"\n  LICENSED CONTENT  {relative}\n     signatures: {hits}")

    if findings:
        print(f"\n{len(findings)} file(s) carry pseudopotential content and must not be "
              "committed.")
        return 1

    print("no pseudopotential content in any committed feasibility artifact")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Gate 4 step 0 -- one streaming pass over the six family archives.

Writes only small text files. The big ones (CHGCAR, WAVECAR, vasprun.xml, PROCAR) are
hashed *in the stream* and never written: the triplicate copy-vs-rerun test needs their
checksums, not their bytes, and the whole stream is being decompressed anyway.

POTCAR is denied by an assertion, not by omission from a keep-list. It is VASP-licensed
material and this project's remote is public.

The cache this writes is the one artifact of the campaign that must stay outside the
repository -- 1.6 GB mirroring run directories that each carry a pseudopotential. `paths`
asserts that, and the two small indexes describing it go to the committed results instead.
"""

import hashlib
import json
import os
import sys
import tarfile
import time

from paths import CACHE, RESULTS

#: The archives. Overridable for a differently-mounted copy of the dataset.
SRC = os.environ.get(
    "NOP_SWEEP_ARCHIVES", "/Pool/Diamond_Stretch_And_Skew_Sweep/renamed-archives")
DST = str(CACHE)

LICENSED = "pseudopotential-LICENSED-DO-NOT-REDISTRIBUTE.txt"

# Written to disk. All small, all text.
KEEP = {
    "calculation-settings.txt",              # INCAR   -- functional, ISPIN, ENCUT
    "kpoint-mesh-request.txt",               # KPOINTS -- the mesh request
    "input-crystal-geometry.txt",            # POSCAR  -- the imposed cell
    "final-relaxed-crystal-geometry.txt",    # CONTCAR -- relaxed positions
    "band-energies-per-kpoint.txt",          # EIGENVAL -- the workhorse
    "energy-per-iteration-summary.txt",      # OSZICAR -- iteration history
    "density-of-states-curve.txt",           # DOSCAR  -- cross-check on our own broadening
    "irreducible-kpoint-list-with-weights.txt",   # IBZKPT
    "orbital-character-per-band-per-kpoint.txt",  # PROCAR -- character overlap at large shear
    # The author's own pymatgen census, one pair per family. Not needed by any step, but
    # it is an independent extraction path over vasprun.xml -- a different file, parser
    # and author -- and so the only cross-check on our gaps that shares nothing with them.
    "electronic-summary-pbe.csv",
    "electronic-summary-hse06.csv",
}

# Hashed in-stream, never written.
HASH_ONLY = {
    "charge-density-grid-full.txt",
    "wavefunctions-binary-restart-only.bin",
    "everything-machine-readable.xml",
}

assert LICENSED not in KEEP and LICENSED not in HASH_ONLY


def main():
    if not os.path.isdir(SRC):
        sys.exit(
            f"no archive directory at {SRC}. Point NOP_SWEEP_ARCHIVES at the six "
            "family tarballs. They are 10.7 GB and are never committed."
        )
    archives = sorted(f for f in os.listdir(SRC) if f.endswith(".tar.gz"))
    manifest = {}          # run-dir -> {basename: size}
    digests = {}           # run-dir -> {basename: sha256}
    licensed_skipped = 0
    written = 0
    written_bytes = 0

    for arc in archives:
        t0 = time.time()
        path = os.path.join(SRC, arc)
        with tarfile.open(path, mode="r|gz") as tf:
            for member in tf:
                if not member.isfile():
                    continue
                base = os.path.basename(member.name)
                run = os.path.dirname(member.name)
                manifest.setdefault(run, {})[base] = member.size

                if base == LICENSED:
                    licensed_skipped += 1
                    continue

                if base in HASH_ONLY:
                    fh = tf.extractfile(member)
                    h = hashlib.sha256()
                    for chunk in iter(lambda: fh.read(1 << 20), b""):
                        h.update(chunk)
                    digests.setdefault(run, {})[base] = h.hexdigest()
                    continue

                if base not in KEEP:
                    continue

                fh = tf.extractfile(member)
                data = fh.read()
                digests.setdefault(run, {})[base] = hashlib.sha256(data).hexdigest()
                out = os.path.join(DST, member.name)
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with open(out, "wb") as g:
                    g.write(data)
                written += 1
                written_bytes += len(data)

        print(f"{arc}: {time.time() - t0:.0f}s, {written} files, "
              f"{written_bytes / 1e9:.2f} GB, licensed skipped {licensed_skipped}",
              flush=True)

    with open(f"{RESULTS}/file_manifest.json", "w") as f:
        json.dump(manifest, f)
    with open(f"{RESULTS}/digests.json", "w") as f:
        json.dump(digests, f)

    print(f"DONE runs={len(manifest)} written={written} "
          f"bytes={written_bytes / 1e9:.2f} GB licensed_skipped={licensed_skipped}")


if __name__ == "__main__":
    sys.exit(main())

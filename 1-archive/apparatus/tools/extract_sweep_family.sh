#!/usr/bin/env bash
# Extract one strain-sweep family's machine-readable output into the local cache.
#
# The dataset lives on /Pool and is never committed: every run directory carries a
# VASP-licensed POTCAR and this remote is public. This script pulls only the XML --
# about 60 MB per family, against 20 GB of archive -- so nothing licensed is unpacked.
#
#   ./tools/extract_sweep_family.sh                       # family 1, PBE (the EOS family)
#   ./tools/extract_sweep_family.sh 2                     # family 2, PBE
#   ./tools/extract_sweep_family.sh 1 2-accurate-hse06-atoms-fixed
#
# Then: ./.venv/bin/python -m pytest tests/ -q
#
# The tests skip cleanly when the cache is absent, so this is optional for the hermetic
# suite and required only for the real-data tests.

set -euo pipefail

FAMILY="${1:-1}"
SUB_RUN="${2:-1-cheap-pbe-atoms-relaxed}"
ARCHIVE_DIR="${NOP_POOL:-/Pool/Diamond_Stretch_And_Skew_Sweep}/renamed-archives"
CACHE="${NOP_CACHE:-$HOME/.cache/n-op-vasp}"

# -type f matters: a stray extracted directory beside the archives also matches the glob.
archive=$(find "$ARCHIVE_DIR" -maxdepth 1 -type f -name "${FAMILY}-*.tar.gz" -print -quit 2>/dev/null || true)
if [[ -z "$archive" ]]; then
    echo "no archive for family '${FAMILY}' under ${ARCHIVE_DIR}" >&2
    echo "available:" >&2
    ls -1 "$ARCHIVE_DIR" 2>/dev/null | sed 's/^/  /' >&2 || echo "  (directory unreadable)" >&2
    exit 1
fi

echo "archive : $(basename "$archive")"
echo "sub-run : ${SUB_RUN}"
echo "into    : ${CACHE}"
echo "scanning ~1 GB of archive for XML only; a minute or so..."

mkdir -p "$CACHE"
# -C must precede the pattern. GNU tar applies -C positionally among operands, so
# `tar -xzf A --wildcards 'PAT' -C DIR` extracts into the *current* directory and silently
# ignores DIR. That mistake once wrote two files into the read-only-by-intent dataset tree.
tar -xzf "$archive" -C "$CACHE" --wildcards "*/${SUB_RUN}/everything-machine-readable.xml"

name=$(basename "$archive" .tar.gz)
echo "extracted $(find "${CACHE}/${name}" -name '*.xml' | wc -l) points into ${CACHE}/${name}"

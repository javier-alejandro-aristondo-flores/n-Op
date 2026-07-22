#!/usr/bin/env python3
"""Calibrate the checkers: plant one defect per check, confirm each one fires.

`[traps]` §58: a checker that finds nothing may simply not be looking. Both
checkers in this repo have shipped holes that silently skipped whole classes of
citation while reporting green — `apparatus.py` validated only ids matching
`arch|impl|mvp|deriv`, its dated-anchor pattern required a dot and so skipped
every `[timeline] §<date>`, and `seams.py` captured `formula =` arguments with an
ASCII-only character class. Each of those was green the entire time it was broken.

This makes the rule executable. Every probe below plants exactly one defect of one
class into a scratch copy, runs the checker, and asserts that the expected message
appears. A probe that does NOT fire is a hole in the checker, not a pass.

    python journal/tools/calibrate.py          run every probe
    python journal/tools/calibrate.py -v       show each checker's output

Exit code 0 iff every probe fires. Read-only with respect to the repo: all work
happens in a temporary copy, which is removed on exit.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VERBOSE = "-v" in sys.argv

# (name, checker, relative path to mutate, find, replace, expected substring)
# `find` is matched verbatim; a probe whose `find` no longer appears is reported
# as STALE rather than silently skipped, because a stale probe is a hole too.
PROBES: list[tuple[str, str, str, str, str, str]] = [
    # --- apparatus -----------------------------------------------------------
    ("id resolving nowhere", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee [arch-99-nope].",
     "resolves to no page"),
    ("cited id without its edge", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee [arch-13-applicability].",
     "does not depends-on"),
    # Mutates an existing list rather than an empty one: a probe keyed on
    # `referenced-by: []` goes STALE the moment that page gains a consumer,
    # which is exactly what happened to its first version.
    ("asymmetric edge (reverse)", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "referenced-by:", "referenced-by:\n  - product",
     "is referenced-by"),
    ("dated anchor that does not resolve", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee [timeline] §1999-01-01.",
     "does not resolve"),
    ("ambiguous dated anchor", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee [timeline] §2026-06-10.",
     "ambiguous"),
    ("wrong dated parenthetical", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee [timeline] §2026-06-10 (No Such Thing).",
     "matches no heading"),
    ("numeric anchor that does not resolve", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee arch-07-pipeline §99.9.",
     "does not resolve"),
    ("line-number citation", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee 9.1-accuracy-ledger.md:42.",
     "line-number citation"),
    ("duplicate topic differing only in case", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "  - architectural principles", "  - architectural principles\n  - PURPOSE",
     "different casing"),
    ("out-of-vocabulary status", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "status: draft", "status: drfat", "is not draft"),
    ("out-of-vocabulary authority", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "authority: canon", "authority: cannon", "is not canon"),
    ("stale content-hash", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nAn unstamped edit.",
     "stale content-hash"),
    ("registry count claim", "apparatus",
     "physics/library/formulas/registry-manifest.csv",
     "1,bandgap-direct", "0,fake-row,`() → S`,B1,T0,D1,cheap,S1,none\n1,bandgap-direct",
     "substantive"),
    ("per-tag diff tally", "apparatus",
     "journal/pages/04-pipeline-and-compilation/4.4-computational-overview.md",
     "`D2` adjoint-required-and-gated (23)", "`D2` adjoint-required-and-gated (99)",
     "rows tagged"),
    ("vocabulary count phrasing", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nThere are 3 templates.",
     "templates; canon is"),
    ("ledger headline count", "apparatus",
     "journal/pages/09-reference-data-and-accuracy/9.1-accuracy-ledger.md",
     "## The 59 ledger-tracked observables", "## The 42 ledger-tracked observables",
     "ledger-tracked"),
    # Keyed on trap 1, not the tail: a probe pointing at the last trap number goes
    # stale every time the register grows, which is the failure this file exists to
    # report rather than commit.
    ("trap numbering gap", "apparatus",
     "journal/pages/10-process-and-governance/10.4-traps.md",
     "\n1. **", "\n0. **", "missing trap numbers"),
    ("citation of a trap that does not exist", "apparatus",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee `[traps]` §99.",
     "does not exist"),
    # --- seams ---------------------------------------------------------------
    ("retired formula name", "seams",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nA stray `kane-zener-rate`.",
     "retired-name"),
    ("retired name, wrong case", "seams",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nA stray `Padovani-Stratton-TFE`.",
     "retired-name"),
    ("case-variant near-miss", "seams",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee `acoustic-mismatch-tbr`.",
     "near-miss"),
    ("inline math in a formula slot", "seams",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nAlgebraicOf({x}, formula = a/(b·c))",
     "inline-math"),
    ("undeclared formula name", "seams",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nAlgebraicOf({x}, formula = not-a-row)",
     "formula-arg"),
    ("row-band endpoint not in the CSV", "seams",
     "journal/pages/01-purpose-and-product/1.4-principles.md",
     "# Architectural principles", "# Architectural principles\n\nCovered by rows 200-250.",
     "row-band"),
    ("D4 with no named relaxation", "seams",
     "physics/library/formulas/registry-manifest.csv",
     "S1 (soft-hull log-sum-exp)", "S1", "d4-no-relaxation"),
    ("registry row pointer naming the wrong row", "seams",
     "physics/library/formulas/registry-manifest.csv",
     "phonon-dispersion (row 9)", "phonon-dispersion (row 99)", "row-pointer"),
    ("stale unregistered-formulas declaration", "seams",
     "journal/pages/06-vocabularies-and-registry/6.8-compositions.md",
     "  - arrhenius\n", "  - arrhenius\n  - nothing-invokes-this\n", "stale-declaration"),
    ("glossary pointer naming no page", "seams",
     "journal/glossary.md", "| `impl-04-formulas` |", "| `arch-99-nope` |", "glossary-pointer"),
    ("reference-data row with no sigma", "seams",
     "physics/library/cert/reference-data/elastic-tensors.csv",
     "242.8 GPa,2.9 GPa,", "242.8 GPa,,", "refdata-sigma"),
]


def run(root: Path, checker: str) -> str:
    tool = root / "journal" / "tools" / f"{checker}.py"
    args = [sys.executable, str(tool)] + (["--check"] if checker == "apparatus" else [])
    p = subprocess.run(args, capture_output=True, text=True, cwd=root)
    return p.stdout + p.stderr


def main() -> int:
    fired = stale = missed = 0
    with tempfile.TemporaryDirectory() as td:
        base = Path(td) / "corpus"
        for d in ("journal", "physics", "informed-operator"):
            if (REPO / d).exists():
                shutil.copytree(REPO / d, base / d)
        for f in ("README.md",):
            if (REPO / f).exists():
                shutil.copy(REPO / f, base / f)

        # the baseline must be clean, or every probe is meaningless
        for checker in ("apparatus", "seams"):
            out = run(base, checker)
            if "OK" not in out and "clean" not in out:
                print(f"BASELINE NOT CLEAN ({checker}) — probes would be meaningless:\n{out}")
                return 2

        for name, checker, rel, find, repl, expect in PROBES:
            target = base / rel
            original = target.read_text(encoding="utf-8")
            if find not in original:
                print(f"  STALE   [{checker}] {name}"
                      f"\n          probe text no longer present in {rel}")
                stale += 1
                continue
            target.write_text(original.replace(find, repl, 1), encoding="utf-8")
            out = run(base, checker)
            target.write_text(original, encoding="utf-8")
            if expect in out:
                print(f"  FIRED   [{checker}] {name}")
                fired += 1
            else:
                print(f"  MISSED  [{checker}] {name}"
                      f"\n          expected {expect!r} in the checker's output")
                missed += 1
            if VERBOSE:
                print("          " + out.strip().replace("\n", "\n          "))

    total = len(PROBES)
    print(f"\ncalibration: {fired}/{total} fired, {missed} missed, {stale} stale")
    if missed or stale:
        print("A missed probe is a hole in the checker. A stale probe is a hole in "
              "this file — the corpus moved and the probe stopped testing anything.")
    return 0 if (missed == 0 and stale == 0) else 1


if __name__ == "__main__":
    sys.exit(main())

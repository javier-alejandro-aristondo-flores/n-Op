#!/usr/bin/env python3
"""Calibrate the checkers: plant one defect per check, confirm each one fires.

`[traps]` §58: a checker that finds nothing may simply not be looking. Both
checkers in this repo have shipped holes that silently skipped whole classes of
citation while reporting green — `check_book_structure.py` validated only ids matching
`arch|impl|mvp|deriv`, its dated-anchor pattern required a dot and so skipped
every `[timeline] §<date>`, and `check_data_agreement.py` captured `formula =` arguments with an
ASCII-only character class. Each of those was green the entire time it was broken.

This makes the rule executable. Every probe below plants exactly one defect of one
class into a scratch copy, runs the checker, and asserts that the expected message
appears. A probe that does NOT fire is a hole in the checker, not a pass.

    python journal/tools/check_the_checkers.py          run every probe
    python journal/tools/check_the_checkers.py -v       show each checker's output

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

# Calibrated checks that are not PROBES rows, because the fault they plant is
# not a corpus defect: the two scratch-copy guards plant a *location*.
# `check_book_structure.py` reads this constant when it checks the probe count quoted in
# prose, so the published number stays the number actually calibrated.
GUARD_PROBES = 2

# (name, checker, relative path to mutate, find, replace, expected substring)
# `find` is matched verbatim; a probe whose `find` no longer appears is reported
# as STALE rather than silently skipped, because a stale probe is a hole too.
PROBES: list[tuple[str, str, str, str, str, str]] = [
    # --- apparatus -----------------------------------------------------------
    ("id resolving nowhere", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee [arch-99-nope].",
     "resolves to no page"),
    ("cited id without its edge", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee [applicability-classifiers].",
     "does not depends-on"),
    # The three `referenced-by` probes below plant the three ways a generated
    # field can disagree with its derivation: an entry too many, an entry naming
    # nothing, and an entry missing because a forward edge was added. All three
    # now surface as staleness -- the field is derived from `depends-on`, so
    # asymmetry and dangling ids are not representable, only out-of-date.
    #
    # Mutates an existing list rather than an empty one: a probe keyed on
    # `referenced-by: []` goes STALE the moment that page gains a consumer,
    # which is exactly what happened to its first version.
    ("referenced-by with an entry too many", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "referenced-by:", "referenced-by:\n  - product",
     "stale referenced-by"),
    ("dated anchor that does not resolve", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee [timeline] §1999-01-01.",
     "does not resolve"),
    ("ambiguous dated anchor", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee [timeline] §2026-06-10.",
     "ambiguous"),
    ("wrong dated parenthetical", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee [timeline] §2026-06-10 (No Such Thing).",
     "matches no heading"),
    ("numeric anchor that does not resolve", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee compose-time-pipeline §99.9.",
     "does not resolve"),
    ("line-number citation", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee 9.1-accuracy-ledger.md:42.",
     "line-number citation"),
    ("duplicate topic differing only in case", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "  - architectural principles", "  - architectural principles\n  - PURPOSE",
     "different casing"),
    ("out-of-vocabulary authority", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "authority: canon", "authority: cannon", "is not canon"),
    ("stale content-hash", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nAn unstamped edit.",
     "stale content-hash"),
    ("registry count claim", "structure",
     "physics/library/formulas/registry-manifest.csv",
     "1,bandgap-direct", "0,fake-row,`() → S`,B1,T0,D1,cheap,S1,none\n1,bandgap-direct",
     "substantive"),
    ("per-tag diff tally", "structure",
     "journal/pages/04-pipeline-and-compilation/4.4-computational-overview.md",
     "`D2` adjoint-required-and-gated (23)", "`D2` adjoint-required-and-gated (99)",
     "rows tagged"),
    ("vocabulary constant unanchored from its owner page", "structure",
     "journal/pages/06-vocabularies-and-registry/6.4-computational-methods.md",
     "title: The 12 computational methods", "title: The 13 computational methods",
     "canon constant is 12"),
    ("cost-tier distribution", "structure",
     "journal/pages/04-pipeline-and-compilation/4.4-computational-overview.md",
     "T2 BZ/mesh integral ≤ 10 s (11)", "T2 BZ/mesh integral ≤ 10 s (13)",
     "cost tier T2"),
    ("vocabulary count phrasing", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nThere are 3 templates.",
     "templates; canon is"),
    ("ledger headline count", "structure",
     "journal/pages/09-reference-data-and-accuracy/9.1-accuracy-ledger.md",
     "## The 59 ledger-tracked observables", "## The 42 ledger-tracked observables",
     "ledger-tracked"),
    # Keyed on trap 1, not the tail: a probe pointing at the last trap number goes
    # stale every time the register grows, which is the failure this file exists to
    # report rather than commit.
    ("trap numbering gap", "structure",
     "journal/pages/10-process-and-governance/10.4-traps.md",
     "\n1. **", "\n0. **", "missing trap numbers"),
    ("citation of a trap that does not exist", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee `[traps]` §99.",
     "does not exist"),
    ("open-decision list misnumbered", "structure",
     "journal/pages/10-process-and-governance/10.2-open-decisions.md",
     "\n2. PDE-mesh", "\n5. PDE-mesh", "open-decision list is numbered"),
    ("traps out of order", "structure",
     "journal/pages/10-process-and-governance/10.4-traps.md",
     "\n2. **", "\n62. **", "out of order"),
    ("duplicate trap number", "structure",
     "journal/pages/10-process-and-governance/10.4-traps.md",
     "\n2. **", "\n1. **", "duplicate trap numbers"),
    ("missing required frontmatter field", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "title: Architectural principles\n", "", "missing frontmatter field"),
    ("duplicate id", "structure",
     "journal/pages/01-purpose-and-product/1.1-purpose-and-scope.md",
     "id: purpose-and-scope", "id: architectural-principles", "duplicate id"),
    ("depends-on naming no page", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "depends-on:\n", "depends-on:\n  - arch-99-nope\n", "depends-on unknown id"),
    ("referenced-by naming no page", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "referenced-by:\n", "referenced-by:\n  - arch-99-nope\n",
     "stale referenced-by"),
    # A new forward edge must show up on the other end. This is the direction
    # that matters in practice: `referenced-by` is what a reader follows to find
    # a page's consumers, and for most of this corpus's life adding a
    # `depends-on` by hand left the far end silently incomplete.
    ("referenced-by missing after a new forward edge", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "depends-on:\n", "depends-on:\n  - topology-atlas\n",
     "stale referenced-by"),
    ("gap in the ledger's row numbering", "structure",
     "journal/pages/09-reference-data-and-accuracy/9.1-accuracy-ledger.md",
     "\n| 30 |", "\n| 31 |", "ledger rows missing"),
    ("marker-count drift", "structure",
     "journal/pages/06-vocabularies-and-registry/6.1-canonical-vocabularies.md",
     "(+2 architectural markers", "(+3 architectural markers", "markers"),
    ("canon formula-count row gone unparseable", "structure",
     "journal/pages/06-vocabularies-and-registry/6.1-canonical-vocabularies.md",
     "132 substantive (+2 architectural markers, non-residualized)",
     "a good few formulas", "not parseable"),
    ("page with no frontmatter at all", "structure",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "---\nid: architectural-principles", "id: architectural-principles", "no frontmatter"),
    # --- data agreement ---------------------------------------------------------------
    ("retired formula name", "data",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nA stray `kane-zener-rate`.",
     "retired-name"),
    ("retired name, wrong case", "data",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nA stray `Padovani-Stratton-TFE`.",
     "retired-name"),
    # The human spelling, which the identifier sweep cannot see: prose writes
    # "Born stability", never `Born-stability-cubic`, and for months only the
    # second was checked.
    ("retired eponym in its prose spelling", "data",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles",
     "# Architectural principles\n\nThe Born stability criteria apply.",
     "retired-eponym"),
    ("retired eponym with an en-dash", "data",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles",
     "# Architectural principles\n\nSee the Schottky–Mott rule.",
     "retired-eponym"),
    ("case-variant near-miss", "data",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nSee `acoustic-mismatch-tbr`.",
     "near-miss"),
    ("inline math in a formula slot", "data",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nAlgebraicOf({x}, formula = a/(b·c))",
     "inline-math"),
    ("undeclared formula name", "data",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nAlgebraicOf({x}, formula = not-a-row)",
     "formula-arg"),
    # A BO level in the Bundle column is how the real defect arrived: the canon
    # table reads `| B1 | electronic-structure | L1 |` and rows 91-94 took the
    # third column. Plant the same slip.
    ("BO level in the Bundle column", "data",
     "physics/library/formulas/registry-manifest.csv",
     "1,bandgap-direct,`(BandStruct) → Scalar`,B1,",
     "1,bandgap-direct,`(BandStruct) → Scalar`,L1,",
     "vocabulary"),
    ("out-of-vocabulary cost tier", "data",
     "physics/library/formulas/registry-manifest.csv",
     "1,bandgap-direct,`(BandStruct) → Scalar`,B1,T0,",
     "1,bandgap-direct,`(BandStruct) → Scalar`,B1,T9,",
     "vocabulary"),
    ("out-of-vocabulary path", "data",
     "physics/library/formulas/registry-manifest.csv",
     "B1,T0,D1,cheap,S1,bands",
     "B1,T0,D1,quick,S1,bands",
     "vocabulary"),
    ("row-band endpoint not in the CSV", "data",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles", "# Architectural principles\n\nCovered by rows 200-250.",
     "row-band"),
    ("D4 with no named relaxation", "data",
     "physics/library/formulas/registry-manifest.csv",
     "S1 (soft-hull log-sum-exp)", "S1", "ungateable-d4-row"),
    ("registry row pointer naming the wrong row", "data",
     "physics/library/formulas/registry-manifest.csv",
     "phonon-dispersion (row 9)", "phonon-dispersion (row 99)", "row-pointer"),
    ("stale unregistered-formulas declaration", "data",
     "journal/pages/06-vocabularies-and-registry/6.8-typed-compositions.md",
     "  - arrhenius\n", "  - arrhenius\n  - nothing-invokes-this\n", "stale-declaration"),
    ("glossary pointer naming no page", "data",
     "journal/glossary.md", "| `named-formulas` |", "| `arch-99-nope` |", "glossary-pointer"),
    ("reference-data row with no sigma", "data",
     "physics/library/cert/reference-data/elastic-tensors.csv",
     "242.8 GPa,2.9 GPa,", "242.8 GPa,,", "missing-uncertainty"),
    ("reference-data row with no source", "data",
     "physics/library/cert/reference-data/elastic-tensors.csv",
     "Polian Grimsditch Grzegory JAP 79 3343 (1996) 10.1063/1.361236,experimental",
     ",experimental", "missing-source"),
    # An unquoted comma in a prose cell, which is how the real defect arrived:
    # every column right of it shifts, and the by-name checks keep passing
    # because the cells they read are still non-empty.
    ("reference-data row whose columns have shifted", "data",
     "physics/library/cert/reference-data/elastic-tensors.csv",
     "242.8 GPa,2.9 GPa,", "242.8 GPa,2.9 GPa,extra,", "wrong-field-count"),
    ("reference-data date in the future", "data",
     "physics/library/cert/reference-data/elastic-tensors.csv",
     ",experimental,1,2026-06-10,2026-06-10", ",experimental,1,2026-06-10,2099-01-01",
     "bad-date"),
    ("backticked name that is not a registry row", "data",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles",
     "# Architectural principles\n\nSee `not-a-known-thing` in the registry.",
     "formula-name"),
    # Expect the class banner `== tolerance (`, not the message text: `tolerance`
    # and `glossary` are substrings of other classes' output, so a looser expect
    # would pass on the wrong finding.
    ("divergent values for one tolerance symbol", "data",
     "journal/pages/01-purpose-and-product/1.4-architectural-principles.md",
     "# Architectural principles",
     "# Architectural principles\n\nHere τ_adj = 1e-9, but there τ_adj = 1e-3.",
     "== tolerance ("),
    ("duplicate glossary entry", "data",
     "journal/glossary.md", "| **PhysicsGraph** |",
     "| **PhysicsGraph** | duplicate. | `physics-graph` |\n| **PhysicsGraph** |",
     "== glossary ("),
]


# Probe labels -> the tool each one exercises. Two names for one thing is what
# this indirection buys: the label reads in a probe list, the filename says what
# the tool does.
CHECKERS = {"structure": "check_book_structure.py",
            "data": "check_data_agreement.py"}


def run(root: Path, checker: str) -> str:
    tool = root / "journal" / "tools" / CHECKERS[checker]
    args = [sys.executable, str(tool)] + (["--check"] if checker == "structure" else [])
    p = subprocess.run(args, capture_output=True, text=True, cwd=root)
    return p.stdout + p.stderr


def data_check_classes() -> set[str]:
    """Every finding class `check_data_agreement.py` can emit, read out of its source.

    Derived, not listed. A hand-maintained list of what the probes cover is one
    more thing that can drift out of date, and drift in *this* file is the
    failure it exists to report."""
    src = (REPO / "journal/tools/check_data_agreement.py").read_text(encoding="utf-8")
    return set(re.findall(r"findings\['([A-Za-z0-9_-]+)'\]", src))


def scratch_copy_refusal() -> list[str]:
    """Both checkers must refuse to run inside a scratch worktree copy.

    This one is not a corpus defect, so it cannot be a PROBES row: the planted
    fault is the checker's *location*, not its input. It is calibrated all the
    same, because the guard exists to stop precisely the failure that has
    already happened once — two identical copies of the book on disk, both
    reporting green, one of them stale."""
    fired, errs = 0, []
    with tempfile.TemporaryDirectory() as td:
        fake = Path(td) / ".claude" / "worktrees" / "copy" / "journal" / "tools"
        fake.mkdir(parents=True)
        for f in (*CHECKERS.values(), "corpus_root.py"):
            shutil.copy(REPO / "journal" / "tools" / f, fake / f)
        for checker in CHECKERS:
            p = subprocess.run([sys.executable, str(fake / CHECKERS[checker])],
                               capture_output=True, text=True)
            if p.returncode != 2 or "REFUSED" not in (p.stdout + p.stderr):
                errs.append(f"  MISSED  [{checker}] runs in a scratch worktree copy "
                            f"without refusing (exit {p.returncode})")
            else:
                print(f"  FIRED   [{checker}] refuses to run in a scratch copy")
                fired += 1
    return fired, errs


def main() -> int:
    fired = stale = missed = 0
    data_seen: set[str] = set()
    guard_fired, guard_errs = scratch_copy_refusal()
    for e in guard_errs:
        print(e)
    fired += guard_fired
    missed += len(guard_errs)
    with tempfile.TemporaryDirectory() as td:
        base = Path(td) / "corpus"
        for d in ("journal", "physics", "informed-operator"):
            if (REPO / d).exists():
                shutil.copytree(REPO / d, base / d)
        for f in ("README.md",):
            if (REPO / f).exists():
                shutil.copy(REPO / f, base / f)

        # the baseline must be clean, or every probe is meaningless
        for checker in CHECKERS:
            out = run(base, checker)
            if "OK" not in out and "clean" not in out:
                print(f"BASELINE NOT CLEAN ({checker}) — probes would be meaningless:\n{out}")
                return 2

        for name, checker, rel, find, repl, expect in PROBES:
            target = base / rel
            # A probe whose target file is gone is STALE, not a crash. Renaming
            # 28 pages made every path here wrong at once and this raised
            # FileNotFoundError mid-run, which reports nothing about the other
            # probes -- the opposite of what a calibration is for.
            if not target.exists():
                print(f"  STALE   [{checker}] {name}"
                      f"\n          probe target no longer exists: {rel}")
                stale += 1
                continue
            original = target.read_text(encoding="utf-8")
            if find not in original:
                print(f"  STALE   [{checker}] {name}"
                      f"\n          probe text no longer present in {rel}")
                stale += 1
                continue
            target.write_text(original.replace(find, repl, 1), encoding="utf-8")
            out = run(base, checker)
            target.write_text(original, encoding="utf-8")
            if checker == "data":
                data_seen |= set(re.findall(r"^== (\S+) \(", out, re.M))
            if expect in out:
                print(f"  FIRED   [{checker}] {name}")
                fired += 1
            else:
                print(f"  MISSED  [{checker}] {name}"
                      f"\n          expected {expect!r} in the checker's output")
                missed += 1
            if VERBOSE:
                print("          " + out.strip().replace("\n", "\n          "))

    # The guards are calibrated but are not PROBES rows. Counting the numerator
    # without the denominator is how a tally reads as verified while being
    # wrong (`[traps]` §67).
    total = len(PROBES) + GUARD_PROBES
    print(f"\ncalibration: {fired}/{total} fired, {missed} missed, {stale} stale")

    # Coverage, not just pass rate. `10.1-conventions` and `instructions.md` both
    # say this file plants "one defect per check" — for a long time that was false
    # of four data-agreement classes (`formula-name`, `tolerance`, `glossary`,
    # `missing-source`), so a clean 29/29 was cited as evidence for something it
    # did not establish. Asserting the coverage is the only way the sentence stays
    # true as checks are added.
    uncovered = sorted(data_check_classes() - data_seen)
    if uncovered:
        print(f"UNCOVERED  data-agreement checks with no probe: {', '.join(uncovered)}\n"
              "           These can be silently broken and calibration still "
              "reports green.")
    else:
        print(f"coverage: every data-agreement check ({len(data_seen)}) fired under some probe")

    if missed or stale or uncovered or guard_errs:
        print("A missed probe is a hole in the checker. A stale probe is a hole in "
              "this file — the corpus moved and the probe stopped testing anything. "
              "An uncovered check is a hole in this file that green cannot show you.")
    return 0 if (missed == 0 and stale == 0 and not uncovered
                 and not guard_errs) else 1


if __name__ == "__main__":
    sys.exit(main())

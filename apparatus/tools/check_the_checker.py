#!/usr/bin/env python3
"""Prove the structure checker is looking.

Plants one defect per class into a scratch copy and asserts the checker fails on
it. Reports three failure modes, and all three are holes:

  missed     — a planted defect the checker did not catch. A hole in the checker.
  stale      — a probe whose anchor text no longer exists. A hole in the probe list.
  uncovered  — an error site in the checker that no probe reaches. Derived from the
               checker's own source, not from a list that could drift from it.

The third mode exists because a calibration with holes is the same failure one
level up, and this project has shipped exactly that: a "one defect per check"
claim that was false of thirteen classes while a clean run was cited as evidence.

    python tools/check_the_checker.py
"""
from __future__ import annotations

import ast
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "apparatus" / "tools" / "check_structure.py"
CONTRACT_REL = "journals/practice/agent-contract.md"
VICTIM_REL = "journals/practice/probe-target.md"

# A minimal well-formed page. Probes mutate this, not the contract, so a probe
# cannot accidentally pass by tripping the contract's own exemption.
VICTIM = """---
id: probe-target
title: "Probe target"
owns:
  - probe target topic
anchors:
  here: "A heading"
depends-on: [agent-contract]
open-questions: []
---
# Probe target

A page that exists to be broken. It cites [agent-contract#shape].

## A heading

| one | two |
|---|---|
| a | b |
"""

# (name, find, replace, expected fragment of the finding)
PROBES: list[tuple[str, str, str, str]] = [
    ("frontmatter not valid YAML",
     'title: "Probe target"', 'title: `unquoted backtick`', "not valid YAML"),
    ("missing required key",
     "open-questions: []\n", "", "missing"),
    ("forbidden key (content-hash)",
     "open-questions: []", "open-questions: []\ncontent-hash: 73b6142e008f", "forbidden frontmatter key"),
    ("unknown key",
     "open-questions: []", "open-questions: []\nvibes: high", "unknown frontmatter key"),
    ("id does not match filename",
     "id: probe-target", "id: probe-targert", "does not match filename stem"),
    ("owns is empty",
     "owns:\n  - probe target topic", "owns: []", "owns is empty"),
    ("owns lists its own id",
     "  - probe target topic", "  - probe-target", "owns lists its own id"),
    ("duplicate topic across pages",
     "  - probe target topic", "  - frontmatter schema", "duplicate topic"),
    ("anchor declares a heading that is absent",
     'here: "A heading"', 'here: "No such heading"', "which is not a heading"),
    ("depends-on names no page",
     "depends-on: [agent-contract]", "depends-on: [agent-contract, no-such-page]",
     "which is not a page"),
    ("citation resolves to no page",
     "[agent-contract#shape]", "[no-such-page]", "resolves to no page"),
    ("citation without a depends-on edge",
     "depends-on: [agent-contract]", "depends-on: []", "without a depends-on edge"),
    ("citation to an undeclared anchor",
     "[agent-contract#shape]", "[agent-contract#no-such-anchor]", "declares no\n"),
    ("section ordinal",
     "A page that exists", "See agent-contract §4.1. A page that exists", "section ordinal"),
    ("line-number citation",
     "A page that exists", "See journals/practice/agent-contract.md:42. A page exists",
     "line-number citation"),
    ("path citation — a page",
     "A page that exists", "See journals/practice/agent-contract.md. A page exists",
     "names the path"),
    # The rule was enforced for pages and not for data artifacts: one citation form
    # checked, an equivalent form left to accumulate. Four references had already
    # slipped through before the pattern was widened.
    ("path citation — a data artifact",
     "A page that exists", "The registry is at apparatus/data/registry-manifest.csv. A page exists",
     "names the path"),
    ("table arity mismatch",
     "| a | b |", "| a | b | c |", "cells, header"),
    ("history marker",
     "A page that exists", "This was formerly a different page. It exists",
     "history marker"),
    # Backticked, because that is the form a tag takes. An unbacked D2 is a
    # deformation potential and must NOT be caught — planting the unbacked form
    # would test the opposite of the rule.
    ("retired vocabulary tag (backticked)",
     "A page that exists", "The row is tagged `D2`. A page that exists", "retired tag"),
    ("unbacked tag-shaped token is NOT a tag",
     "A page that exists", "D1 through D5 are deformation potentials. A page exists",
     None),
    # Frontmatter is prose too, and was unchecked until a builder noticed. Both of
    # these passed silently before: a citation inside an open question's summary,
    # and an open question pointing at an anchor its own page never declares.
    ("open question points at an undeclared anchor",
     "open-questions: []",
     "open-questions:\n  - id: q\n    anchor: nowhere\n    summary: \"A gap.\"",
     "does not declare"),
    ("citation inside frontmatter",
     "open-questions: []",
     "open-questions:\n  - id: q\n    anchor: here\n    summary: \"See [no-such-page].\"",
     "resolves to no page"),
    ("open-questions entry is not a mapping",
     "open-questions: []", "open-questions:\n  - just a string", "not a mapping"),
    ("open question missing a required field",
     "open-questions: []",
     "open-questions:\n  - id: q\n    anchor: here",
     "missing 'summary'"),
    ("anchor on a data artifact",
     "[agent-contract#shape]", "[registry#some-anchor]", "has no anchors"),
    ("name index points at a page that never uses the name",
     "## A heading", "## A heading\n\n| `FooRecord` | see [agent-contract] |\n|---|---|",
     "never uses it"),
    ("depends-on edge that the body never cites",
     "depends-on: [agent-contract]", "depends-on: [agent-contract, glossary]",
     "never cites it"),
    # Frontmatter carries prose, so it can carry a tag. And a retired marker that is
    # also a proper noun stays correct when written in full — the corpus retired the
    # missing-data marker and kept the software names.
    ("retired tag in frontmatter",
     "open-questions: []",
     "open-questions:\n  - id: q\n    anchor: here\n    summary: \"A bare `GAP` row.\"",
     "retired tag"),
    ("qualified proper noun is NOT a retired tag",
     "open-questions: []",
     "open-questions:\n  - id: q\n    anchor: here\n    summary: \"The `GAP` computer-algebra system.\"",
     None),
    ("stale emitted corpus.json",
     None, None, "stale"),
    # Structural probes: these plant a whole file rather than mutating the victim,
    # so `find` carries a ("+file", relative-path) spec and `repl` its content.
    ("page at the wrong depth",
     ("+file", "journals/stray.md"), VICTIM.replace("probe-target", "stray"),
     "pages live at"),
    ("page with no frontmatter",
     ("+file", "journals/practice/no-frontmatter.md"), "# Just a heading\n",
     "no frontmatter block"),
    ("frontmatter that is not a mapping",
     ("+file", "journals/practice/scalar-frontmatter.md"),
     "---\njust a string\n---\n# Body\n", "not a mapping"),
]


def error_sites() -> dict[str, str]:
    """Every errs.append in the checker, keyed by its longest literal fragment.

    Derived from the checker's own AST rather than from a maintained list, so the
    coverage claim cannot drift away from the code it describes.
    """
    tree = ast.parse(CHECKER.read_text(encoding="utf-8"))
    sites: dict[str, str] = {}
    # Any finding sink, not just `errs`. A refactor that routed two sites through a
    # local alias once dropped them silently out of this count — the coverage claim
    # drifting away from the code it describes, which is the exact failure this
    # script exists to catch, one level up.
    sinks = {"errs", "pending", "unresolved", "findings"}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "append"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in sinks):
            continue
        arg = node.args[0] if node.args else None
        parts = ([v.value for v in arg.values if isinstance(v, ast.Constant)]
                 if isinstance(arg, ast.JoinedStr)
                 else [arg.value] if isinstance(arg, ast.Constant) else [])
        literal = max((p.strip() for p in parts), key=len, default="")
        if literal:
            sites[literal] = f"line {node.lineno}"
    return sites


def run(work: Path) -> str:
    r = subprocess.run([sys.executable, str(work / "apparatus" / "tools" / "check_structure.py"), "--check"],
                       capture_output=True, text=True, cwd=work)
    return r.stdout + r.stderr


def main() -> int:
    missed, stale, seen = [], [], []

    for name, find, repl, expect in PROBES:
        with tempfile.TemporaryDirectory() as td:
            # A minimal fixture — the contract plus one victim page — not a copy of
            # the live corpus. The calibration measures the checker; if it copied
            # the corpus it would break every time a page was mid-write, and the
            # pressure would then be to weaken the calibration rather than fix the
            # page.
            work = Path(td) / "corpus"
            (work / "journals" / "practice").mkdir(parents=True)
            shutil.copytree(ROOT / "apparatus" / "tools", work / "apparatus" / "tools")
            shutil.copy2(ROOT / CONTRACT_REL, work / CONTRACT_REL)
            (work / VICTIM_REL).write_text(VICTIM, encoding="utf-8")

            # Establish a clean, non-stale baseline for this scratch copy.
            subprocess.run([sys.executable, str(work / "apparatus" / "tools" / "check_structure.py")],
                           capture_output=True, cwd=work)
            base = run(work)
            if "OK" not in base:
                print(f"  !! baseline not clean before probe {name!r}:\n{base}")
                return 2

            if find is None:                      # the staleness probe
                (work / "apparatus" / "generated" / "corpus.json").write_text("{}\n", encoding="utf-8")
            elif isinstance(find, tuple):         # a structural probe: plant a file
                target = work / find[1]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(repl, encoding="utf-8")
            else:
                victim = work / VICTIM_REL
                text = victim.read_text(encoding="utf-8")
                if find not in text:
                    stale.append(name)
                    continue
                victim.write_text(text.replace(find, repl, 1), encoding="utf-8")

            # A negative probe asserts the CONTENT is clean. Since the digest now
            # hashes page bodies, the harness's own mutation registers as staleness —
            # which is the digest working, not a finding about the content. So
            # regenerate first and then judge.
            if expect is None:
                subprocess.run([sys.executable, str(work / "apparatus" / "tools" / "check_structure.py")],
                               capture_output=True, cwd=work)
            out = run(work)
            if expect is None:                     # negative probe: must stay clean
                if "OK" in out:
                    seen.append("")
                else:
                    missed.append((name, "no finding", out.strip()[:200]))
            elif expect.strip() in out:
                seen.append(out)
            else:
                missed.append((name, expect, out.strip()[:200]))

    sites = error_sites()
    joined = "\n".join(seen)
    uncovered = {lit: loc for lit, loc in sites.items() if lit.strip() not in joined}

    print(f"probes: {len(PROBES)} · caught {len(seen)} · missed {len(missed)} · "
          f"stale {len(stale)}")
    print(f"checker error sites: {len(sites)} · unreached by any probe: {len(uncovered)}")

    for name, expect, out in missed:
        print(f"\n  MISSED  {name}\n     expected {expect!r}\n     got: {out}")
    for name in stale:
        print(f"\n  STALE   {name} — its anchor text no longer exists in the probe page")
    for lit, loc in sorted(uncovered.items(), key=lambda kv: kv[1]):
        print(f"\n  UNCOVERED  {loc}: {lit[:88]!r}")

    return 1 if (missed or stale or uncovered) else 0


if __name__ == "__main__":
    sys.exit(main())

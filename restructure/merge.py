#!/usr/bin/env python3
"""Merge the Phase 1 disposition fragments into one table plus three registers.

Read-only over the corpus. Writes only under restructure/.
Run: python restructure/merge.py
"""
from __future__ import annotations
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRAGMENTS = ROOT / "disposition"
OUT = ROOT / "merged"

EXPECTED = [
    "oracle-state", "oracle-laws-seams", "oracle-compilation",
    "oracle-cert-accuracy", "oracle-registry", "program", "practice",
    "appendix-a", "appendix-b", "appendix-c", "strata",
]

SECTIONS = {
    "rows":           r"^##\s+Disposition rows\s*$",
    "open":           r"^##\s+Open questions\s*$",
    "log":            r"^##\s+Log-worthy advancements\s*$",
    "contradictions": r"^##\s+Contradictions",
    "notes":          r"^##\s+Notes for Phase 2\s*$",
}
ORDER = ["rows", "open", "log", "contradictions", "notes"]


def split_sections(text: str) -> dict[str, str]:
    """Return {section_key: body} by locating each ## heading and slicing to the next."""
    marks = []
    for key, pat in SECTIONS.items():
        m = re.search(pat, text, re.M)
        if m:
            marks.append((m.start(), m.end(), key))
    marks.sort()
    out = {}
    for i, (_s, e, key) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        out[key] = text[e:end].strip()
    return out


# Split on pipes that are NOT backslash-escaped. An escaped `\|` inside a cell
# otherwise splits the row into extra fields and shifts every column right of it —
# the same arity defect `journal/instructions.md` documents for the reference CSVs,
# reproduced here on markdown tables.
UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")


def table_rows(body: str) -> list[list[str]]:
    """Pipe-table data rows, minus header and separator. Cells stripped."""
    rows = []
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        if re.fullmatch(r"\|[\s:|-]+\|", s):      # separator
            continue
        inner = s[1:-1] if s.endswith("|") else s[1:]
        cells = [c.strip().replace(r"\|", "|") for c in UNESCAPED_PIPE.split(inner)]
        if not any(cells):
            continue
        if cells[0].strip("*` ") in {"#", "id", "date", "claim"}:
            continue                               # header
        rows.append(cells)
    return rows


DISPOSITION = re.compile(r"^\**\s*(keep|move|mine|delete)\b", re.I)


def repair_row(cells: list[str]) -> tuple[list[str], bool]:
    """Rejoin a 6-column disposition row that literal `|` split into more.

    Physics notation contains bare pipes — bra-kets `⟨a|H|b⟩`, `|e_κ|²`,
    determinants — which split a markdown row exactly as an unquoted comma
    splits a CSV row. Anchor on the disposition cell (a short keyword that
    cannot contain a pipe); the location cell sits immediately before it and is
    a `path:line` string that also cannot. Everything else rejoins.
    """
    if len(cells) <= 6:
        return cells, False
    idx = next((i for i, c in enumerate(cells)
                if 1 <= i < len(cells) - 1 and DISPOSITION.match(c) and len(c) < 40), None)
    if idx is None or idx < 2:
        return cells, False
    return ([cells[0],
             "|".join(cells[1:idx - 1]),
             cells[idx - 1],
             cells[idx],
             cells[idx + 1] if idx + 1 < len(cells) else "",
             "|".join(cells[idx + 2:])], True)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    present, missing = [], []
    for name in EXPECTED:
        (present if (FRAGMENTS / f"{name}.md").exists() else missing).append(name)

    if missing:
        print(f"!! {len(missing)} fragment(s) absent: {', '.join(missing)}")
        print("   Merging what is present. Re-run when the rest land.\n")

    parsed: dict[str, dict[str, str]] = {}
    for name in present:
        parsed[name] = split_sections((FRAGMENTS / f"{name}.md").read_text(encoding="utf-8"))

    # ---- per-section merge -------------------------------------------------
    counts: dict[str, Counter] = {k: Counter() for k in ORDER}
    for key in ORDER:
        chunks = []
        for name in present:
            body = parsed[name].get(key, "").strip()
            if not body:
                continue
            counts[key][name] = len(table_rows(body)) if key != "notes" else body.count("\n") + 1
            chunks.append(f"### from `{name}`\n\n{body}\n")
        (OUT / f"{key}.md").write_text(
            f"# Merged — {key}\n\n"
            f"Fragments: {len(present)}/{len(EXPECTED)}"
            + (f" (missing: {', '.join(missing)})" if missing else "")
            + "\n\n" + "\n---\n\n".join(chunks) + "\n",
            encoding="utf-8",
        )

    # ---- conflict detection ------------------------------------------------
    problems: list[str] = []

    # (a) same target anchor claimed by rows in more than one fragment
    target_owners: dict[str, set[str]] = defaultdict(set)
    disp_tally: Counter = Counter()
    repaired: Counter = Counter()
    unparsed: list[str] = []
    for name in present:
        for raw in table_rows(parsed[name].get("rows", "")):
            cells, was_repaired = repair_row(raw)
            if was_repaired:
                repaired[name] += 1
            if len(cells) < 5 or not any(cells):
                continue
            disp = cells[3].lower()
            for d in ("keep", "move", "mine", "delete"):
                if d in disp:
                    disp_tally[d] += 1
                    break
            else:
                disp_tally["other/unparsed"] += 1
                unparsed.append(f"{name}: disposition={cells[3][:40]!r} fact={cells[1][:50]!r}")
            tgt = cells[4].strip("`* ")
            if tgt and tgt not in {"—", "-", ""}:
                target_owners[tgt].add(name)
    shared = {t: o for t, o in target_owners.items() if len(o) > 1}
    for t, o in sorted(shared.items()):
        problems.append(f"target claimed by {len(o)} fragments: `{t}`  <- {', '.join(sorted(o))}")

    # (b) open-question ids. Two very different situations share one symptom.
    oq: dict[str, set[str]] = defaultdict(set)
    for name in present:
        for cells in table_rows(parsed[name].get("open", "")):
            if cells:
                oq[cells[0].strip("`* ")].add(name)
    convergent, serial = [], defaultdict(set)
    for qid, o in sorted(oq.items()):
        if re.fullmatch(r"(OQ|Q)[-_]?\d+", qid, re.I):
            # A serial id carries no meaning and collides across fragments by
            # construction. This is the naming scheme the corpus already retired
            # once (retired-ids.csv, 2026-07-22) reappearing in a work product.
            for src in o:
                serial[src].add(qid)
        elif len(o) > 1:
            # Same descriptive slug from independent surveyors = the same gap
            # found more than once. That is corroboration, not a collision.
            convergent.append((qid, o))
    for src, ids in sorted(serial.items()):
        problems.append(
            f"RENAME: `{src}` used {len(ids)} serial open-question ids "
            f"({', '.join(sorted(ids)[:4])}…) — ids must be descriptive and globally unique")

    # (c) delete rows with no stated reason. Frontmatter-field deletes are governed
    # by plan D6/§4, so the reason lives in the plan rather than the row.
    FRONTMATTER = re.compile(r"authority|content-hash|referenced-by|^`?tag`?$", re.I)
    for name in present:
        for raw in table_rows(parsed[name].get("rows", "")):
            cells, _ = repair_row(raw)
            if len(cells) >= 6 and "delete" in cells[3].lower() and len(cells[5]) < 12:
                if FRONTMATTER.search(cells[1]):
                    continue
                problems.append(f"{name}: delete row with thin/absent reason -> {cells[1][:60]!r}")

    (OUT / "conflicts.md").write_text(
        "# Merge conflicts and gate checks\n\n"
        "## Needs resolution before Phase 2\n\n"
        + ("\n".join(f"- {p}" for p in problems) if problems else "None detected.")
        + "\n\n## Convergent findings — the same gap found independently\n\n"
        "Not conflicts. Two or more surveyors reached the same descriptive id from\n"
        "different scopes, which corroborates the finding. Merge into one entry and\n"
        "record every source.\n\n"
        + ("\n".join(f"- `{q}` — found by {', '.join(sorted(o))}" for q, o in convergent)
           if convergent else "None.")
        + "\n\n## Shared targets — verify, do not assume\n\n"
        "Two fragments routing content to one anchor is correct when they carry\n"
        "*different* facts, and a duplication when they carry the same one. Each needs\n"
        "an eyeball before the page is written.\n\n"
        + ("\n".join(f"- `{t}` <- {', '.join(sorted(o))}" for t, o in sorted(shared.items()))
           if shared else "None.")
        + "\n", encoding="utf-8")

    # ---- report ------------------------------------------------------------
    print(f"fragments merged : {len(present)}/{len(EXPECTED)}")
    print(f"\n{'fragment':<22}{'rows':>7}{'open':>7}{'log':>6}{'contra':>8}")
    for name in present:
        print(f"{name:<22}{counts['rows'][name]:>7}{counts['open'][name]:>7}"
              f"{counts['log'][name]:>6}{counts['contradictions'][name]:>8}")
    print(f"{'TOTAL':<22}{sum(counts['rows'].values()):>7}{sum(counts['open'].values()):>7}"
          f"{sum(counts['log'].values()):>6}{sum(counts['contradictions'].values()):>8}")
    print("\ndispositions:", ", ".join(f"{k}={v}" for k, v in sorted(disp_tally.items())))
    if repaired:
        print("\nrows repaired (literal `|` in physics notation split the row):")
        for k, v in sorted(repaired.items()):
            print(f"  {k:<22}{v:>4}")
    if unparsed:
        print(f"\nstill unparsed: {len(unparsed)}")
        for u in unparsed[:6]:
            print(f"  {u}")
    print(f"\nconflicts/gate failures: {len(problems)}  -> restructure/merged/conflicts.md")
    print(f"shared targets (legitimate merges OR collisions): {len(shared)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""A5 strict pass: each results-page number looked for only in its own member's report and results.json (and the stage-zero report), sections mapped by their entry heading"""

import importlib.util
import json
import re
import sys
from pathlib import Path

BASELINE = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
MEMBER_OF_ENTRY = {"I.1": "factorized_fourier", "I.2": "alias_free_convolutional", "I.3": "factorized_fourier",
                   "I.4": "galerkin_transformer", "II.1": "deep_operator_network", "II.2": "multiple_input_operator_network",
                   "II.3": "nonlinear_manifold_decoder", "II.4": "factorized_fourier", "III.1": "deep_dft",
                   "III.3": "gaussian_plane_wave", "IV.1": "residual_correction", "IV.2": None,
                   "IV.3": "residual_correction", "V.1": "codomain_attention", "VI.1": "deep_operator_network"}
spec = importlib.util.spec_from_file_location("trace", Path(__file__).parent / "a5_trace_numbers.py")
trace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)


def Forms_Of_Text(text: str) -> set[str]:
    """every printed number in a text and every rounding of it"""
    forms: set[str] = set()
    for token in trace.Numbers_In(text):
        bare = token.replace(",", "")
        forms.add(bare)
        try:
            forms |= trace.Printed_Forms(float(bare.rstrip("%")) / (100.0 if bare.endswith("%") else 1.0))
        except ValueError:
            pass
    return forms


def Forms_Of_Member(member: str | None) -> set[str]:
    """the printed forms of every number in a member's report and results.json"""
    if member is None:
        return set()
    forms: set[str] = set()
    report = BASELINE / "operators" / member / "report.md"
    if report.exists():
        forms |= Forms_Of_Text(report.read_text())
    results = BASELINE / "operators" / member / "results.json"
    if results.exists():
        for value in trace.Values_In(json.loads(results.read_text())):
            forms |= trace.Printed_Forms(value)
    return forms


def Main() -> None:
    """prints every number not found in its own member's sources, with the member it was checked against"""
    stage0 = Forms_Of_Text((BASELINE / "operators/stage0-report.md").read_text())
    cache: dict[str | None, set[str]] = {}
    section_member: str | None = None
    rows = []
    for number, line in enumerate((BASELINE / "operator-results.md").read_text().splitlines(), start=1):
        heading = re.match(r"## ([IVX]+\.\d)", line)
        if heading:
            section_member = MEMBER_OF_ENTRY.get(heading.group(1))
        elif line.startswith("## "):
            section_member = None
        row = re.match(r"\| ([IVX]+\.\d) \|", line)
        member = MEMBER_OF_ENTRY.get(row.group(1)) if row else section_member
        if member not in cache:
            cache[member] = Forms_Of_Member(member)
        for token in trace.Numbers_In(line):
            bare = token.replace(",", "")
            forms = cache[member] | stage0
            rows.append({"line": number, "member": member, "number": token,
                         "traced": bare in forms or bare.rstrip("%") in forms, "context": line.strip()[:120]})
    Path(sys.argv[1]).write_text("".join(json.dumps(row) + "\n" for row in rows))
    untraced = [row for row in rows if not row["traced"]]
    unmapped = sum(1 for row in rows if row["member"] is None)
    print(f"{len(rows)} numbers, {unmapped} outside any member section, {len(untraced)} not in their own member's sources")


if __name__ == "__main__":
    Main()

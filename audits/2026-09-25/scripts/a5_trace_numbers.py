"""A5 first pass: every number printed on the results page and in cross_member.md, looked for at its printed precision in the member reports and results.json files"""

import json
import re
import sys
from pathlib import Path

BASELINE = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
NUMBER = re.compile(r"(?<![\w.])[-−]?\d[\d,]*\.?\d*(?:[eE][-−+]?\d+)?%?")


def Numbers_In(text: str) -> list[str]:
    """every decimal, percentage or scientific number in a text, as printed"""
    found = []
    for match in NUMBER.finditer(text):
        token = match.group(0).replace("−", "-")
        if "." in token or "e" in token.lower() or token.endswith("%"):
            found.append(token)
    return found


def Printed_Forms(value: float) -> set[str]:
    """the ways a stored value can be printed: fixed decimals, as a percentage, in scientific notation"""
    forms: set[str] = set()
    for decimals in range(0, 8):
        forms.add(f"{value:.{decimals}f}")
        forms.add(f"{100 * value:.{decimals}f}%")
    for digits in range(0, 5):
        forms.add(f"{value:.{digits}e}".replace("e-0", "e-").replace("e+0", "e+"))
    return forms


def Values_In(node: object) -> list[float]:
    """every number anywhere in a parsed JSON tree"""
    if isinstance(node, bool):
        return []
    if isinstance(node, (int, float)):
        return [float(node)]
    if isinstance(node, dict):
        return [value for child in node.values() for value in Values_In(child)]
    if isinstance(node, list):
        return [value for child in node for value in Values_In(child)]
    return []


def Main() -> None:
    """prints each page number with where it was found, and a count of the untraced ones"""
    sources: dict[str, set[str]] = {}
    for results in sorted(BASELINE.glob("operators/*/results.json")):
        forms: set[str] = set()
        for value in Values_In(json.loads(results.read_text())):
            forms |= Printed_Forms(value)
        sources[str(results.relative_to(BASELINE))] = forms
    for report in sorted(BASELINE.glob("operators/*/report.md")) + [BASELINE / "operators/stage0-report.md"]:
        forms = set()
        for token in Numbers_In(report.read_text()):
            bare = token.replace(",", "")
            forms.add(bare)
            # a report's number also counts as the source of any rounding of it the page prints
            try:
                value = float(bare.rstrip("%")) / (100.0 if bare.endswith("%") else 1.0)
            except ValueError:
                continue
            forms |= Printed_Forms(value)
        sources[str(report.relative_to(BASELINE))] = forms
    target = BASELINE / sys.argv[1]
    untraced = 0
    rows = []
    for line_number, line in enumerate(target.read_text().splitlines(), start=1):
        for token in Numbers_In(line):
            bare = token.replace(",", "")
            homes = [name for name, forms in sources.items() if bare in forms or bare.rstrip("%") in forms]
            if not homes:
                untraced += 1
            rows.append({"line": line_number, "number": token, "found_in": homes, "context": line.strip()[:160]})
    Path(sys.argv[2]).write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    print(f"{len(rows)} numbers on {sys.argv[1]}, {untraced} found in no report and no results.json")


if __name__ == "__main__":
    Main()

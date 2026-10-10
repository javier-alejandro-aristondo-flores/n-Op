"""the mechanical gate: every finding's quote located in its file at the audited commit, exactly or after whitespace and markup folding, never by line number"""

import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

BASELINE = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
AUDITED_COMMIT = "485a7d9"


def Text_Of(file: str) -> str | None:
    """the text a finding's file names: a repository path at the audited commit, a commit message, or a readable file on the volume"""
    if file.startswith("commit:"):
        result = subprocess.run(["git", "-C", str(BASELINE), "show", "-s", "--format=%B", file.removeprefix("commit:")],
                                capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else None
    if file.startswith("/"):
        path = Path(file)
        if path.suffix.lower() in (".png", ".npz") or not path.is_file():
            return None
        try:
            return path.read_text(errors="replace")
        except OSError:
            return None
    relative = file.removeprefix("./").removeprefix(str(BASELINE) + "/")
    if relative.lower().endswith((".png", ".npz")):
        return None
    result = subprocess.run(["git", "-C", str(BASELINE), "show", f"{AUDITED_COMMIT}:{relative}"], capture_output=True, text=True,
                            errors="replace")
    return result.stdout if result.returncode == 0 else None


def Folded(text: str) -> str:
    """whitespace collapsed and markdown emphasis and code marks dropped"""
    text = re.sub(r"[*`]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def Ground(file: str, quote: str) -> str:
    """exact, folded, unicode-folded, missing, or unreadable"""
    text = Text_Of(file)
    if text is None:
        return "unreadable"
    if quote in text:
        return "exact"
    if Folded(quote) in Folded(text):
        return "folded"
    if Folded(unicodedata.normalize("NFKC", quote)) in Folded(unicodedata.normalize("NFKC", text)):
        return "unicode-folded"
    return "missing"


def Controls() -> list[tuple[str, bool]]:
    """the four checks the gate must pass before its verdicts count"""
    plain = Ground("operators/data/store.py", "the file holds charge times cell volume, so the volume comes back out here")
    special = Ground("operator-results.md", "MAE 0.00217 vs kill ≤ 0.0488")
    mutated = Ground("operators/data/store.py", "the file holds charge times cell volume, so the volume comes back out herE")
    wrong_path = Ground("operators/data/splits.py", "the file holds charge times cell volume, so the volume comes back out here")
    return [("a plain quote matches", plain == "exact"), ("a quote with a special character matches", special in ("exact", "folded")),
            ("a one-character mutation misses", mutated == "missing"), ("a wrong path misses", wrong_path == "missing")]


def Main() -> None:
    """grounds every finding in the named JSON-lines file and writes the verdicts beside each"""
    controls = Controls()
    for name, passed in controls:
        print(f"control: {name}: {'ok' if passed else 'FAILED'}")
    if not all(passed for _, passed in controls):
        sys.exit("the gate's controls failed, so none of its verdicts count")
    rows = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines() if line.strip()]
    counts: dict[str, int] = {}
    with Path(sys.argv[2]).open("w") as stream:
        for row in rows:
            row["grounding"] = Ground(row["file"], row["quote"])
            if row.get("counter_kind") == "quote" and row.get("counter_file"):
                counter_quote = row["counter"].split("\n")[0][:400]
                row["counter_grounding"] = Ground(row["counter_file"], counter_quote)
            counts[row["grounding"]] = counts.get(row["grounding"], 0) + 1
            stream.write(json.dumps(row) + "\n")
    print(f"{len(rows)} findings grounded: {counts}")


if __name__ == "__main__":
    Main()

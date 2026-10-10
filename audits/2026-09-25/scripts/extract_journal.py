"""reads a workflow journal and writes every completed auditor's findings as JSON lines, and every ledger agent's rows, labeled by slice"""

import json
import sys
from pathlib import Path


def Completed(journal: Path) -> dict[str, dict[str, object]]:
    """the latest completed record per agent label, with its result"""
    started: dict[str, str] = {}
    done: dict[str, dict[str, object]] = {}
    for line in journal.read_text().splitlines():
        record = json.loads(line)
        label = str(record.get("label", ""))
        if record.get("type") == "started":
            started[str(record.get("agentId"))] = label
        if "result" in record and record.get("result") is not None:
            label = label or started.get(str(record.get("agentId")), "")
            done[label] = record
    return done


def Main() -> None:
    """findings to argv[2], ledger rows to argv[3], resolutions to argv[4], and a count per label"""
    done = Completed(Path(sys.argv[1]))
    findings, rows, resolutions = [], [], []
    for label, record in sorted(done.items()):
        result = record["result"]
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                print(f"{label}: result is not JSON")
                continue
        if not isinstance(result, dict):
            continue
        if label.startswith("audit:"):
            slice_name = label.removeprefix("audit:")
            for number, finding in enumerate(result.get("findings", []), start=1):
                findings.append({"id": f"{slice_name}-{number:03d}", "slice": slice_name, **finding})
            print(f"{label}: {len(result.get('findings', []))} findings, {len(result.get('design_notes', []))} notes,"
                  f" {len(result.get('could_not_check', []))} unchecked")
        elif label.startswith("extract:"):
            chunk = label.removeprefix("extract:")
            for number, row in enumerate(result.get("rows", []), start=1):
                rows.append({"row_id": f"{chunk}-{number:03d}", "chunk": chunk, **row})
            print(f"{label}: {len(result.get('rows', []))} rows, {len(result.get('no_commitment', []))} without commitment")
        elif label.startswith("resolve:"):
            resolutions.extend(result.get("resolutions", []))
    Path(sys.argv[2]).write_text("".join(json.dumps(f) + "\n" for f in findings))
    Path(sys.argv[3]).write_text("".join(json.dumps(r) + "\n" for r in rows))
    Path(sys.argv[4]).write_text("".join(json.dumps(r) + "\n" for r in resolutions))
    print(f"{len(findings)} findings, {len(rows)} ledger rows, {len(resolutions)} resolutions extracted")


if __name__ == "__main__":
    Main()

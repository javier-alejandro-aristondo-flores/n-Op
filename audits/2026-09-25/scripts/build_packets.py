"""turns grounded findings into stripped verification packets: path, quote, claim and a pointer, batched by slice, eight at most"""

import json
import sys
from collections import defaultdict
from pathlib import Path

NEGATION = "The quoted text is correct as written and consistent with the code, data and artifacts it describes."
BATCH_SIZE = 8


def Packet(row: dict[str, object]) -> dict[str, object]:
    """only what a blind verifier may see: no evidence, no severity, no author"""
    return {"id": row["id"], "file": row["file"], "quote": row["quote"], "claim": row["claim"], "negation": NEGATION,
            "pointer": row.get("counter_file") or ""}


def Main() -> None:
    """argv[1] grounded findings; argv[2] output batches; findings that did not ground are listed, not verified"""
    rows = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines() if line.strip()]
    by_slice: dict[str, list[dict[str, object]]] = defaultdict(list)
    dropped = []
    serious: dict[str, bool] = {}
    for row in rows:
        if row.get("grounding") == "missing":
            dropped.append(row["id"])
            continue
        by_slice[str(row.get("slice", "phase-a"))].append(row)
        serious[str(row["id"])] = row.get("severity") in ("S1", "S2", "S3")
    batches = []
    for slice_name, slice_rows in sorted(by_slice.items()):
        for start in range(0, len(slice_rows), BATCH_SIZE):
            chunk = slice_rows[start:start + BATCH_SIZE]
            batches.append({"batch_id": f"{slice_name}-{start // BATCH_SIZE + 1}",
                            "items": [Packet(row) for row in chunk],
                            "serious": [str(row["id"]) for row in chunk if serious[str(row["id"])]]})
    Path(sys.argv[2]).write_text(json.dumps(batches, indent=1))
    print(f"{sum(len(b['items']) for b in batches)} packets in {len(batches)} batches; {len(dropped)} did not ground and are listed, not verified")
    if dropped:
        print("not grounded:", ", ".join(map(str, dropped[:30])))


if __name__ == "__main__":
    Main()

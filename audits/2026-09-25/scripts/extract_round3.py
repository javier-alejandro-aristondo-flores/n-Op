"""pull the round-3 verification returns (verdicts, reproductions, defenses) out of the workflow journal, falling back to the agents' saved scratch files, into three jsonl files"""
import json
import sys
from pathlib import Path

AUDIT = Path(__file__).resolve().parent.parent
SCRATCH = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-scratch")
KINDS = {"verify": ("verdicts", "verdicts.json"), "reproduce": ("reproductions", "reproductions.json"), "defend": ("defenses", "defenses.json")}


def Journal_Returns(journal):
    """label -> returned object for every completed agent in the journal"""
    rows = [json.loads(line) for line in journal.read_text().splitlines() if line.strip()]
    label_of = {row["agentId"]: row["label"] for row in rows if row.get("type") == "started"}
    return {label_of[row["agentId"]]: row["result"] for row in rows if row.get("type") == "result" and row.get("agentId") in label_of and row.get("result")}


def Main():
    """argv[1] the journal; writes findings/round3-{verdicts,reproductions,defenses}.jsonl and prints the counts"""
    returns = Journal_Returns(Path(sys.argv[1]))
    batches = json.loads((AUDIT / "findings/round3-batches.json").read_text())
    for kind, (field, saved_name) in KINDS.items():
        collected = []
        sources = {"journal": 0, "saved": 0, "missing": []}
        for batch in batches:
            if kind == "reproduce" and batch["tier"] != "full":
                continue
            if kind == "defend" and batch["tier"] not in ("full", "defended"):
                continue
            label = f"{kind}:{batch['id']}"
            folder = SCRATCH / f"{kind}-{batch['id']}"
            items = None
            if label in returns and returns[label].get(field):
                items = returns[label][field]
                sources["journal"] += 1
            elif (folder / saved_name).exists():
                try:
                    items = json.loads((folder / saved_name).read_text()).get(field)
                    sources["saved"] += 1
                except json.JSONDecodeError:
                    items = None
            if not items:
                sources["missing"].append(batch["id"])
                continue
            for item in items:
                item = dict(item)
                item["batch"] = batch["id"]
                item["tier"] = batch["tier"]
                collected.append(item)
        out = AUDIT / f"findings/round3-{field}.jsonl"
        out.write_text("".join(json.dumps(item, sort_keys=True) + "\n" for item in collected))
        print(f"{field}: {len(collected)} rows from {sources['journal']} journal returns and {sources['saved']} saved files; missing batches: {sources['missing']}")


if __name__ == "__main__":
    Main()

"""measures from the transcripts, not from any agent's own report, which owned files each auditor actually opened, whole or in part"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

BASELINE = "/home/javier/Projects/Physics/Programs/n-Op-audit-baseline/"


def Label_Of(meta_path: Path) -> str:
    """an agent's workflow label from its meta file"""
    meta = json.loads(meta_path.read_text())
    return str(meta.get("label") or meta.get("description") or "")


def Touches(transcript: Path) -> dict[str, set[str]]:
    """repository paths each tool call reached: read whole, read in part, or named in a shell command"""
    touched: dict[str, set[str]] = defaultdict(set)
    for line in transcript.read_text().splitlines():
        record = json.loads(line)
        message = record.get("message") or {}
        if message.get("role") != "assistant":
            continue
        for block in message.get("content") or []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            tool, arguments = block.get("name"), block.get("input") or {}
            if tool == "Read":
                path = str(arguments.get("file_path", ""))
                if path.startswith(BASELINE):
                    kind = "part" if arguments.get("offset") or arguments.get("limit") else "whole"
                    touched[path.removeprefix(BASELINE)].add(kind)
            elif tool in ("Bash", "Grep"):
                command = str(arguments.get("command", "")) if tool == "Bash" else ""
                text = json.dumps(arguments)
                for match in re.findall(r"(?:operators/[\w/.-]+|operator-results\.md|test-suite\.md)", text):
                    name = match.rstrip(".,;:'\")")
                    # a cat or a show of the whole file reads it; a sed or head range reads part; anything else searches it
                    if re.search(rf"\b(cat|git\s+(?:-C\s+\S+\s+)?show\s+\S*:)\s*\S*{re.escape(name)}(?!\S*\s*\|\s*(grep|head|sed|wc))", command):
                        touched[name].add("whole")
                    elif re.search(rf"\b(sed\s+-n|head|tail|awk)\b[^|;]*{re.escape(name)}", command):
                        touched[name].add("part")
                    else:
                        touched[name].add("shell")
    return touched


def Main() -> None:
    """per slice: owned text files opened whole, in part, only by shell, or never"""
    directory = Path(sys.argv[1])
    ownership = json.loads(Path(sys.argv[2]).read_text())["files"]
    report: dict[str, dict[str, list[str]]] = {}
    merged: dict[str, dict[str, set[str]]] = {}
    for meta_path in sorted(directory.glob("agent-*.meta.json")):
        label = Label_Of(meta_path)
        if not label.startswith("audit:"):
            continue
        slice_name = label.removeprefix("audit:")
        owned = [name for name in ownership.get(slice_name, []) if not name.endswith((".png", ".json"))]
        transcript = meta_path.with_name(meta_path.name.replace(".meta.json", ".jsonl"))
        touched = Touches(transcript)
        # an auditor relaunched after an interruption has several transcripts, and what any of them opened counts
        for name, kinds in merged.get(slice_name, {}).items():
            touched.setdefault(name, set()).update(kinds)
        merged[slice_name] = touched
        status = {"whole": [], "part": [], "shell": [], "never": []}
        for name in owned:
            kinds = touched.get(name, set())
            status["whole" if "whole" in kinds else "part" if "part" in kinds else "shell" if kinds else "never"].append(name)
        report[slice_name] = status
        print(f"{slice_name:44s} whole {len(status['whole']):3d}  part {len(status['part']):3d}  shell only {len(status['shell']):3d}  never {len(status['never']):3d}")
    Path(sys.argv[3]).write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    Main()

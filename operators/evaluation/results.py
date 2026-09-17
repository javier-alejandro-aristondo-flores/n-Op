"""one member's whole results artifact, written and read back as deterministic, sorted-key JSON"""

import hashlib
import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

from operators.evaluation.scoring import FloorComparison, MetricSummary


@dataclass(frozen=True, slots=True)
class ResultKey:
    """which member, configuration, task, split, evaluation block and group one row or verdict answers for"""

    member: str
    configuration: str
    task: str
    split: str
    block: str
    group: str


@dataclass(frozen=True, slots=True)
class ResultRow:
    """one metric summary, keyed to the member and block it was measured on, beside that block's own signature"""

    key: ResultKey
    summary: MetricSummary
    block_signature: str


@dataclass(frozen=True, slots=True)
class VerdictRow:
    """one floor comparison, keyed to the member and block it was measured on"""

    key: ResultKey
    comparison: FloorComparison


@dataclass(frozen=True, slots=True)
class MemberResults:
    """one member's whole results artifact: every row and verdict its report committed, and how to rebuild them"""

    member: str
    regenerate: str
    rows: tuple[ResultRow, ...]
    verdicts: tuple[VerdictRow, ...]


def Block_Signature(unit_keys: Iterable[str]) -> str:
    """the first twelve hex characters of the sha256 over the sorted, newline-joined distinct unit keys"""
    # a block is its set of units, so a caller handing one key per run or per spin channel hashes the same block
    joined = "\n".join(sorted(set(unit_keys)))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:12]


def Rounded_Floats(value: Any) -> Any:
    """value with every float rounded to six places, recursively, so a regeneration reproduces its own bytes"""
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, dict):
        # an isinstance check on a bare Any narrows to dict[Unknown, Unknown], so the keys are cast explicitly
        as_dict = cast(dict[str, Any], value)
        return {name: Rounded_Floats(entry) for name, entry in as_dict.items()}
    if isinstance(value, (list, tuple)):
        as_sequence = cast("list[Any] | tuple[Any, ...]", value)
        return [Rounded_Floats(entry) for entry in as_sequence]
    return value


def Write_Member_Results(path: Path, results: MemberResults) -> None:
    """the whole artifact as sorted-key, six-place JSON, with no timestamp or hash bookkeeping of its own"""
    payload = Rounded_Floats(asdict(results))
    path.write_text(json.dumps(payload, sort_keys=True, indent=1) + "\n")


def Result_Key_From(payload: dict[str, Any]) -> ResultKey:
    """one result key rebuilt from its own JSON dict"""
    return ResultKey(
        member=payload["member"],
        configuration=payload["configuration"],
        task=payload["task"],
        split=payload["split"],
        block=payload["block"],
        group=payload["group"],
    )


def Read_Member_Results(path: Path) -> MemberResults:
    """a member's results artifact rebuilt from the archive it was written to"""
    payload = json.loads(path.read_text())
    rows = tuple(
        ResultRow(
            key=Result_Key_From(row["key"]),
            summary=MetricSummary(**row["summary"]),
            block_signature=row["block_signature"],
        )
        for row in payload["rows"]
    )
    verdicts = tuple(
        VerdictRow(key=Result_Key_From(verdict["key"]), comparison=FloorComparison(**verdict["comparison"]))
        for verdict in payload["verdicts"]
    )
    return MemberResults(member=payload["member"], regenerate=payload["regenerate"], rows=rows, verdicts=verdicts)

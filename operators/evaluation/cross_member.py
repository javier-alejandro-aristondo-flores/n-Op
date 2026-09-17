"""the comparison table over every landed member's own results artifact, refusing what cannot be compared"""

from pathlib import Path

from operators.evaluation.results import MemberResults, Read_Member_Results, ResultKey, ResultRow, VerdictRow
from operators.inspection import Render_Table, Table
from operators.tasks import Card_Named

CROSS_MEMBER_PATH = Path(__file__).parent / "cross_member.md"
OPERATORS_ROOT = Path(__file__).resolve().parent.parent
MEMBERS = (
    "factorized_fourier",
    "alias_free_convolutional",
    "deep_operator_network",
    "multiple_input_operator_network",
    "nonlinear_manifold_decoder",
    "deep_dft",
    "residual_correction",
    "codomain_attention",
    "galerkin_transformer",
    "gaussian_plane_wave",
)


def Member_Results_Path(member: str, operators_root: Path = OPERATORS_ROOT) -> Path:
    """where one member's committed results artifact lives"""
    return operators_root / member / "results.json"


def Every_Member_Results(
    members: tuple[str, ...] = MEMBERS, operators_root: Path = OPERATORS_ROOT
) -> tuple[MemberResults, ...]:
    """every member's results artifact found on disk, read in canon order"""
    found: list[MemberResults] = []
    for member in members:
        path = Member_Results_Path(member, operators_root)
        if path.is_file():
            found.append(Read_Member_Results(path))
    return tuple(found)


def Pooled_Rows(results: tuple[MemberResults, ...]) -> tuple[ResultRow, ...]:
    """every row every member reported, pooled into one sequence"""
    return tuple(row for member_results in results for row in member_results.rows)


def Pooled_Verdicts(results: tuple[MemberResults, ...]) -> tuple[VerdictRow, ...]:
    """every verdict every member reported, pooled into one sequence"""
    return tuple(verdict for member_results in results for verdict in member_results.verdicts)


def Card_Split_Of(row: ResultRow) -> str:
    """the row's own task card's committed split, or a refusal naming the member and the unknown task"""
    try:
        return Card_Named(row.key.task).split
    except KeyError:
        raise ValueError(f"{row.key.member}: no task card named {row.key.task!r} (key {row.key})") from None


def Card_Split_Partition(rows: tuple[ResultRow, ...]) -> tuple[tuple[ResultRow, ...], tuple[ResultRow, ...]]:
    """every row measured on its own task card's committed split, and every other row, never pooled together"""
    on_card: list[ResultRow] = []
    outside: list[ResultRow] = []
    for row in rows:
        (on_card if row.key.split == Card_Split_Of(row) else outside).append(row)
    return tuple(on_card), tuple(outside)


def Signature_Refusals(rows: tuple[ResultRow, ...]) -> list[str]:
    """one message per task, split, block and group whose rows disagree on which units they were scored over"""
    members_by_signature: dict[tuple[str, str, str, str], dict[str, set[str]]] = {}
    for row in rows:
        measurement = (row.key.task, row.key.split, row.key.block, row.key.group)
        members_by_signature.setdefault(measurement, {}).setdefault(row.block_signature, set()).add(row.key.member)
    refusals: list[str] = []
    for measurement, signatures in sorted(members_by_signature.items()):
        if len(signatures) <= 1:
            continue
        task, split, block, group = measurement
        named = {signature: sorted(members) for signature, members in sorted(signatures.items())}
        refusals.append(f"{task} {split} {block} {group}: block signatures disagree across members {named}")
    return refusals


def Verdicts_For(verdicts: tuple[VerdictRow, ...], key: ResultKey) -> tuple[str, ...]:
    """every floor verdict a row's own key carries, named by the floor beside its own outcome"""
    return tuple(
        f"{verdict.comparison.floor_name}:{verdict.comparison.verdict}" for verdict in verdicts if verdict.key == key
    )


def Task_Table(task: str, rows: tuple[ResultRow, ...], verdicts: tuple[VerdictRow, ...]) -> Table:
    """one task's own rows, sorted by member then configuration, each carrying the verdicts its key earned"""
    task_rows = sorted(
        (row for row in rows if row.key.task == task),
        key=lambda row: (row.key.member, row.key.configuration, row.key.group, row.summary.metric_name),
    )
    return tuple(
        {
            "member": row.key.member,
            "configuration": row.key.configuration,
            "group": row.key.group,
            "metric": row.summary.metric_name,
            "units": row.summary.unit_count,
            "median": f"{row.summary.median:.6f}",
            "verdicts": ", ".join(Verdicts_For(verdicts, row.key)) or "-",
        }
        for row in task_rows
    )


def Outside_Card_Split_Table(split: str, rows: tuple[ResultRow, ...], verdicts: tuple[VerdictRow, ...]) -> Table:
    """one non-card split's own rows, sorted by task then member, each carrying the verdicts its key earned"""
    split_rows = sorted(
        (row for row in rows if row.key.split == split),
        key=lambda row: (row.key.task, row.key.member, row.key.configuration, row.key.group, row.summary.metric_name),
    )
    return tuple(
        {
            "task": row.key.task,
            "member": row.key.member,
            "configuration": row.key.configuration,
            "group": row.key.group,
            "metric": row.summary.metric_name,
            "units": row.summary.unit_count,
            "median": f"{row.summary.median:.6f}",
            "verdicts": ", ".join(Verdicts_For(verdicts, row.key)) or "-",
        }
        for row in split_rows
    )


def Outside_Card_Split_Section(rows: tuple[ResultRow, ...], verdicts: tuple[VerdictRow, ...]) -> str:
    """every row whose split differs from its own task card's, one table per split, apart from the tables above"""
    splits = sorted({row.key.split for row in rows})
    tables = "\n\n".join(
        f"#### {split}\n\n{Render_Table(Outside_Card_Split_Table(split, rows, verdicts))}" for split in splits
    )
    return f"### Rows outside the card's split\n\n{tables}"


def Cross_Member_Table(results: tuple[MemberResults, ...]) -> str:
    """every task's own rows on its card split, one table each, a further section for every other split, or nothing"""
    rows = Pooled_Rows(results)
    if not rows:
        return "no artifacts"
    on_card_rows, outside_rows = Card_Split_Partition(rows)
    refusals = Signature_Refusals(rows)
    if refusals:
        raise ValueError("; ".join(refusals))
    verdicts = Pooled_Verdicts(results)
    sections = [
        f"### {task}\n\n{Render_Table(Task_Table(task, on_card_rows, verdicts))}"
        for task in sorted({row.key.task for row in on_card_rows})
    ]
    if outside_rows:
        sections.append(Outside_Card_Split_Section(outside_rows, verdicts))
    return "\n\n".join(sections)


def Write_Cross_Member_Table(path: Path = CROSS_MEMBER_PATH, members: tuple[str, ...] = MEMBERS) -> None:
    """the cross-member table regenerated from every landed member's own artifact and committed"""
    body = Cross_Member_Table(Every_Member_Results(members))
    path.write_text(f"# Cross-member table\n\n{body}\n")


if __name__ == "__main__":
    Write_Cross_Member_Table()

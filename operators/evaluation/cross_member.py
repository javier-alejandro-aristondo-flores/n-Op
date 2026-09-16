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


def Split_Refusals(rows: tuple[ResultRow, ...]) -> list[str]:
    """one message per row whose split does not match its own task card's split"""
    refusals: list[str] = []
    for row in rows:
        card_split = Card_Named(row.key.task).split
        if row.key.split != card_split:
            refusals.append(
                f"{row.key.member} {row.key.task} {row.key.configuration}:"
                f" split {row.key.split!r} differs from the card's {card_split!r}"
            )
    return refusals


def Signature_Refusals(rows: tuple[ResultRow, ...]) -> list[str]:
    """one message per task whose rows disagree on which units they were scored over"""
    signatures_by_task: dict[str, set[str]] = {}
    for row in rows:
        signatures_by_task.setdefault(row.key.task, set()).add(row.block_signature)
    return [
        f"{task}: block signatures disagree across members {sorted(signatures)}"
        for task, signatures in sorted(signatures_by_task.items())
        if len(signatures) > 1
    ]


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


def Cross_Member_Table(results: tuple[MemberResults, ...]) -> str:
    """every landed member's rows, one table per task, or a plain statement when no artifact exists"""
    rows = Pooled_Rows(results)
    if not rows:
        return "no artifacts"
    refusals = Split_Refusals(rows) + Signature_Refusals(rows)
    if refusals:
        raise ValueError("; ".join(refusals))
    verdicts = Pooled_Verdicts(results)
    sections = [
        f"### {task}\n\n{Render_Table(Task_Table(task, rows, verdicts))}"
        for task in sorted({row.key.task for row in rows})
    ]
    return "\n\n".join(sections)


def Write_Cross_Member_Table(path: Path = CROSS_MEMBER_PATH, members: tuple[str, ...] = MEMBERS) -> None:
    """the cross-member table regenerated from every landed member's own artifact and committed"""
    body = Cross_Member_Table(Every_Member_Results(members))
    path.write_text(f"# Cross-member table\n\n{body}\n")


if __name__ == "__main__":
    Write_Cross_Member_Table()

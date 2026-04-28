"""Rich-based progress and error formatting for the CLI."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


_CONSOLE: Console = Console()
_ERROR_CONSOLE: Console = Console(stderr=True)


def report_phase(message: str) -> None:
    """Print a single-line phase marker to stdout."""
    _CONSOLE.print(f"[bold cyan]>[/] {message}")


def report_completion(
    *,
    problem_name: str,
    content_hash: str,
    problem_directory: Path,
    library_filename: str,
    chunk_count: int,
) -> None:
    """Print a summary panel describing the completed registration."""
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("Problem name", problem_name)
    table.add_row("Content hash", content_hash)
    table.add_row("Directory", str(problem_directory))
    table.add_row("Library", library_filename)
    table.add_row("Chunk sources", str(chunk_count))
    _CONSOLE.print(Panel(table, title="[green]registration complete[/]",
                         border_style="green"))


def report_error(message: str, *, detail: str | None = None) -> None:
    """Print a red error block to stderr."""
    body = message if detail is None else f"{message}\n\n{detail}"
    _ERROR_CONSOLE.print(Panel(body, title="[red]compose-physics error[/]",
                               border_style="red"))


def report_subprocess_failure(*, command: list[str], exit_code: int,
                              stdout: str, stderr: str) -> None:
    """Format a subprocess failure with full command, exit code, and output."""
    rendered_command = " ".join(command)
    detail_lines = [f"command: {rendered_command}",
                    f"exit code: {exit_code}"]
    if stdout.strip():
        detail_lines.append("--- stdout ---")
        detail_lines.append(stdout.rstrip())
    if stderr.strip():
        detail_lines.append("--- stderr ---")
        detail_lines.append(stderr.rstrip())
    report_error("subprocess failed", detail="\n".join(detail_lines))

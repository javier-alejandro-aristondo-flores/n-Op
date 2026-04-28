"""High-level CLI entry point: parse, register, build, report.

This module wires the four CLI submodules into a single ``main``
function. It contains no parsing, no SBCL details, no make logic;
it only sequences the phases and renders user-facing output.
"""

from __future__ import annotations

import sys
from typing import Sequence

from compose_physics.cli.arguments import parse_arguments
from compose_physics.cli.build import run_make_build
from compose_physics.cli.formatting import (
    report_completion,
    report_error,
    report_phase,
)
from compose_physics.cli.sbcl_invocation import run_registration


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    try:
        arguments = parse_arguments(argv)
    except SystemExit as system_exit:
        return int(system_exit.code or 0)

    try:
        report_phase(
            f"registering {arguments.source_pathname.name} into "
            f"{arguments.registry_root}"
        )
        result = run_registration(arguments)

        report_phase(
            f"building shared library with {arguments.parallel_jobs} job(s)"
        )
        run_make_build(
            problem_directory=result.problem_directory,
            parallel_jobs=arguments.parallel_jobs,
            library_filename=result.library_filename,
        )

        report_completion(
            problem_name=result.problem_name,
            content_hash=result.content_hash,
            problem_directory=result.problem_directory,
            library_filename=result.library_filename,
            chunk_count=result.chunk_count,
        )
        return 0
    except RuntimeError as failure:
        report_error(str(failure))
        return 1
    except KeyboardInterrupt:
        report_error("interrupted by user")
        return 130


if __name__ == "__main__":
    sys.exit(main())

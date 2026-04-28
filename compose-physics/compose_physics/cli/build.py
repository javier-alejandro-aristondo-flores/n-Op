"""Run ``make -j`` against a populated problem directory.

The Lisp side emits sources and a Makefile but does not invoke
the C compiler. This module is the build half of the pipeline:
it shells out to ``make``, captures output, and surfaces failures
through the formatting module.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from compose_physics.cli.formatting import report_subprocess_failure


def run_make_build(*, problem_directory: Path, parallel_jobs: int,
                   library_filename: str) -> Path:
    """Invoke make in the problem directory and return the .so path.

    The Makefile's default target is the shared library, so a bare
    ``make -j N`` produces it. We confirm the library exists on
    success; if it does not, we treat the build as failed even if
    make returned zero (defensive, since users may edit the Makefile).
    """
    make_executable = shutil.which("make")
    if make_executable is None:
        raise RuntimeError(
            "no 'make' executable found on PATH; install GNU make "
            "or set PATH to include it"
        )

    command = [
        make_executable,
        "-C", str(problem_directory),
        f"-j{parallel_jobs}",
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if completed.returncode != 0:
        report_subprocess_failure(
            command=command,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        raise RuntimeError(
            f"make exited with status {completed.returncode}"
        )

    library_pathname = problem_directory / library_filename
    if not library_pathname.is_file():
        raise RuntimeError(
            f"make returned 0 but expected library was not produced: "
            f"{library_pathname}"
        )
    return library_pathname

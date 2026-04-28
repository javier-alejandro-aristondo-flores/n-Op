"""Argument parsing for the compose-physics CLI.

The CLI exposes a single verb, ``register``, that takes a Lisp
source file and produces a populated problem directory under a
registry root. Every knob is flag-driven; environment variables
provide secondary overrides where conventional, and no setting is
read from the user's source code.

The resolution order is: explicit flag > environment variable >
hard-coded default. Resolution is performed once, here, so that
downstream modules see a fully-resolved configuration object and
never have to re-check os.environ.
"""

from __future__ import annotations

import argparse
import dataclasses
import os
from pathlib import Path
from typing import Sequence


SOURCE_DESTINATION_CHOICES: tuple[str, ...] = ("move", "copy", "leave")


@dataclasses.dataclass(frozen=True, slots=True)
class RegisterArguments:
    """Fully-resolved register-verb configuration."""

    source_pathname: Path
    registry_root: Path
    source_destination: str
    c_compiler: str
    c_flags: str
    parallel_jobs: int
    chunk_row_count: int
    library_extension: str
    sbcl_pathname: str


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="compose-physics",
        description=(
            "Construct compiled C kernels for a closed-form physics "
            "problem and place them in a content-addressed registry "
            "directory. The CLI does construction only; consumers "
            "load the resulting shared library directly."
        ),
    )
    subparsers = parser.add_subparsers(dest="verb", required=True)

    register_parser = subparsers.add_parser(
        "register",
        help="Register a Lisp source file as a problem in the registry.",
    )
    register_parser.add_argument(
        "source_pathname",
        type=Path,
        help="Path to the Lisp source file defining the problem.",
    )
    register_parser.add_argument(
        "--registry-root",
        type=Path,
        default=None,
        help=(
            "Root directory under which problem directories are created. "
            "Falls back to the COMPOSE_PHYSICS_REGISTRY environment variable, "
            "then to ./compose-physics-registry."
        ),
    )
    register_parser.add_argument(
        "--source-dest",
        choices=SOURCE_DESTINATION_CHOICES,
        default="move",
        help=(
            "What to do with the input source file once registration "
            "completes. Default: move (the working directory ends up clean)."
        ),
    )
    register_parser.add_argument(
        "--c-compiler",
        default=None,
        help=(
            "C compiler to use. Falls back to the CC environment variable, "
            "then to 'cc'."
        ),
    )
    register_parser.add_argument(
        "--c-flags",
        default=None,
        help=(
            "C compiler flags. Falls back to the CFLAGS environment variable, "
            "then to '-O3 -fPIC -ffast-math -Wall -Wextra'."
        ),
    )
    register_parser.add_argument(
        "--parallel-jobs",
        type=int,
        default=None,
        help=(
            "make -j concurrency. Falls back to the JOBS environment "
            "variable, then to the host's CPU count."
        ),
    )
    register_parser.add_argument(
        "--chunk-row-count",
        type=int,
        default=32,
        help=(
            "Maximum rows per chunked C source file. Larger values produce "
            "fewer translation units but compile more slowly per file."
        ),
    )
    register_parser.add_argument(
        "--library-extension",
        default=None,
        help=(
            "Filename extension for the linked shared library. "
            "Default: 'so' (Linux). Use 'dylib' on macOS."
        ),
    )
    register_parser.add_argument(
        "--sbcl",
        dest="sbcl_pathname",
        default=None,
        help=(
            "Path to the SBCL executable. Falls back to the SBCL "
            "environment variable, then to 'sbcl' (resolved via PATH)."
        ),
    )
    return parser


def _resolve_registry_root(value: Path | None) -> Path:
    if value is not None:
        return value.expanduser().resolve()
    env_value = os.environ.get("COMPOSE_PHYSICS_REGISTRY")
    if env_value:
        return Path(env_value).expanduser().resolve()
    return (Path.cwd() / "compose-physics-registry").resolve()


def _resolve_compiler(value: str | None) -> str:
    if value is not None:
        return value
    return os.environ.get("CC", "cc")


def _resolve_compiler_flags(value: str | None) -> str:
    if value is not None:
        return value
    return os.environ.get("CFLAGS", "-O3 -fPIC -ffast-math -Wall -Wextra")


def _resolve_parallel_jobs(value: int | None) -> int:
    if value is not None:
        return max(1, value)
    env_value = os.environ.get("JOBS")
    if env_value and env_value.isdigit():
        return max(1, int(env_value))
    return max(1, os.cpu_count() or 1)


def _resolve_library_extension(value: str | None) -> str:
    if value is not None:
        return value
    return os.environ.get("COMPOSE_PHYSICS_LIBRARY_EXTENSION", "so")


def _resolve_sbcl(value: str | None) -> str:
    if value is not None:
        return value
    return os.environ.get("SBCL", "sbcl")


def parse_arguments(argv: Sequence[str] | None = None) -> RegisterArguments:
    """Parse argv and return a fully-resolved RegisterArguments object.

    Resolution applies the flag > env-var > default precedence chain
    once, so downstream modules see a stable view of configuration.
    """
    parser = _build_parser()
    namespace = parser.parse_args(argv)
    if namespace.verb != "register":
        parser.error(f"unknown verb: {namespace.verb!r}")

    source_pathname: Path = namespace.source_pathname
    if not source_pathname.is_file():
        parser.error(f"source file does not exist: {source_pathname}")

    return RegisterArguments(
        source_pathname=source_pathname.resolve(),
        registry_root=_resolve_registry_root(namespace.registry_root),
        source_destination=namespace.source_dest,
        c_compiler=_resolve_compiler(namespace.c_compiler),
        c_flags=_resolve_compiler_flags(namespace.c_flags),
        parallel_jobs=_resolve_parallel_jobs(namespace.parallel_jobs),
        chunk_row_count=int(namespace.chunk_row_count),
        library_extension=_resolve_library_extension(namespace.library_extension),
        sbcl_pathname=_resolve_sbcl(namespace.sbcl_pathname),
    )

"""compose_physics — Python CLI for constructing problem registries.

The CLI's only job is construction: parse arguments, invoke SBCL on
a generated Lisp script that calls register-problem, then run make
against the populated problem directory. It does not load or run
the resulting shared library; that is the consumer's responsibility.
"""

__all__ = ["main"]

from compose_physics.cli.arguments import parse_arguments
from compose_physics.cli.entrypoint import main

#!/usr/bin/env python3
"""Which corpus is this, and is it the real one?

A result with no address is a result you cannot cash. This repo carried two
complete copies of the book for weeks — one at the repo root, one under
`.claude/worktrees/corpus-reconciliation/` — with identical page counts,
identical trap counts, and no way to tell them apart from a checker's output.
Both printed `apparatus OK`. An agent read the stale one, believed it, and
reported a conclusion about the corpus that was confidently wrong.

`.claude/` is gitignored, so `git status` and `git grep` never mention such a
copy. `find`, `glob` and `grep` do. So the checkers say where they ran and
refuse to run anywhere that is not the corpus itself.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

# Scratch copies live here. A checker passing inside one of these says nothing
# about the corpus, which is the whole reason this module exists.
SCRATCH_MARKERS = (".claude/worktrees", ".claude\\worktrees")


def current_commit(root: pathlib.Path) -> str | None:
    """Short HEAD hash, or None outside a git repo.

    `check_the_checkers.py` runs the checkers against a temporary copy that has no git
    metadata; that is legitimate, so a missing commit is not an error."""
    try:
        done = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.strip() or None if done.returncode == 0 else None


def describe(root: pathlib.Path) -> str:
    """The address a success line carries: `d3d6958 · /path/to/n-Op`."""
    commit = current_commit(root)
    return f"{commit} · {root}" if commit else f"no-git · {root}"


def refuse_if_scratch_copy(root: pathlib.Path, allowed: bool = False) -> None:
    """Exit 2 if this is a scratch worktree rather than the corpus.

    Passing `--worktree` is the deliberate override; the point is that running
    in a copy must be a decision, not an accident."""
    if allowed:
        return
    posix = root.as_posix()
    if any(marker.replace("\\", "/") in posix for marker in SCRATCH_MARKERS):
        print(f"REFUSED  this is a scratch worktree copy, not the corpus:\n"
              f"         {root}\n"
              f"         A green result here says nothing about the book. Run "
              f"from the repo root,\n"
              f"         or pass --worktree if you meant to check the copy.",
              file=sys.stderr)
        raise SystemExit(2)

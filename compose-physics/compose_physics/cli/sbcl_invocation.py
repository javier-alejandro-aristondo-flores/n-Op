"""Generate a Lisp registration script and invoke SBCL on it.

The Python side never imports any Lisp; it shells out to SBCL with
a freshly-generated script for each registration. The script:

  1. Loads ASDF and pushes the compose-physics system path onto
     the central registry.
  2. Loads the system.
  3. Loads the user's source file (which must define a problem
     and bind it via (defparameter *problem* ...) at the toplevel).
  4. Calls register-problem with all the resolved configuration.
  5. Writes a result sexp containing the problem name, content
     hash, directory, library filename, and chunk count to a
     known result-pathname so the CLI can read it back.

The Lisp script lives in a temporary file so concurrent CLI runs
do not collide. Stdout / stderr are captured for diagnostics.
"""

from __future__ import annotations

import dataclasses
import re
import subprocess
import tempfile
from pathlib import Path

from compose_physics.cli.arguments import RegisterArguments
from compose_physics.cli.formatting import report_subprocess_failure


# Resolve the system root once: the directory holding compose-physics.asd.
# This file lives at <root>/compose_physics/cli/sbcl_invocation.py, so the
# system root is two levels up.
_SYSTEM_ROOT: Path = Path(__file__).resolve().parent.parent.parent


@dataclasses.dataclass(frozen=True, slots=True)
class RegistrationResult:
    """Mirror of the Lisp-side registration-result struct."""

    problem_name: str
    content_hash: str
    problem_directory: Path
    library_filename: str
    chunk_count: int


_KEY_VALUE_PATTERN = re.compile(r'(:[\w-]+)\s+("[^"]*"|[^\s):][^\s)]*)')


def _parse_result_sexp(text: str) -> RegistrationResult:
    """Parse the small result sexp written by the generated Lisp script.

    The sexp shape is fixed:
      (:registration-result
        :problem-name "..."
        :content-hash "..."
        :problem-directory "..."
        :library-filename "..."
        :chunk-count N)
    """
    pairs: dict[str, str] = {}
    for key, raw_value in _KEY_VALUE_PATTERN.findall(text):
        unquoted = raw_value[1:-1] if raw_value.startswith('"') else raw_value
        pairs[key] = unquoted
    try:
        return RegistrationResult(
            problem_name=pairs[":problem-name"],
            content_hash=pairs[":content-hash"],
            problem_directory=Path(pairs[":problem-directory"]),
            library_filename=pairs[":library-filename"],
            chunk_count=int(pairs[":chunk-count"]),
        )
    except KeyError as missing_key:
        raise RuntimeError(
            f"registration result sexp missing key {missing_key!r};"
            f" full text was:\n{text}"
        ) from missing_key


def _render_lisp_script(*, arguments: RegisterArguments,
                        result_pathname: Path) -> str:
    """Render the Lisp script that drives one registration."""
    return f"""
(require :asdf)
(push #p"{_SYSTEM_ROOT}/" asdf:*central-registry*)
(asdf:load-system :compose-physics)

(load #p"{arguments.source_pathname}")

(unless (and (find-symbol "*PROBLEM*" :common-lisp-user)
             (boundp (find-symbol "*PROBLEM*" :common-lisp-user)))
  (error "source file did not define cl-user::*problem*"))

(let* ((problem (symbol-value (find-symbol "*PROBLEM*" :common-lisp-user)))
       (result
        (compose-physics:register-problem
         problem
         :registry-root #p"{arguments.registry_root}/"
         :source-pathname #p"{arguments.source_pathname}"
         :source-disposition {':' + arguments.source_destination}
         :chunk-row-count {arguments.chunk_row_count}
         :c-compiler "{arguments.c_compiler}"
         :c-flags "{arguments.c_flags}"
         :library-extension "{arguments.library_extension}")))
  (with-open-file (stream #p"{result_pathname}"
                          :direction :output
                          :if-exists :supersede
                          :if-does-not-exist :create)
    (format stream
            "(:registration-result :problem-name ~S :content-hash ~S~%~
              :problem-directory ~S :library-filename ~S :chunk-count ~D)~%"
            (compose-physics:problem-name problem)
            (compose-physics:registration-result-content-hash result)
            (compose-physics:registration-result-problem-directory result)
            (compose-physics:registration-result-library-filename result)
            (length (compose-physics:registration-result-chunk-filenames
                     result)))))
"""


def run_registration(arguments: RegisterArguments) -> RegistrationResult:
    """Generate and execute the Lisp registration script."""
    with tempfile.TemporaryDirectory(prefix="compose-physics-") as tmp_dir:
        tmp_dir_path = Path(tmp_dir)
        script_pathname = tmp_dir_path / "register.lisp"
        result_pathname = tmp_dir_path / "result.sexp"

        script_text = _render_lisp_script(
            arguments=arguments,
            result_pathname=result_pathname,
        )
        script_pathname.write_text(script_text, encoding="utf-8")

        command = [
            arguments.sbcl_pathname,
            "--non-interactive",
            "--load", str(script_pathname),
        ]
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if completed.returncode != 0 or not result_pathname.is_file():
            report_subprocess_failure(
                command=command,
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
            )
            raise RuntimeError(
                f"SBCL registration script failed with exit code "
                f"{completed.returncode}"
            )

        return _parse_result_sexp(result_pathname.read_text(encoding="utf-8"))

"""A14: flags test functions that cannot fail, assert only conditionally, swallow exceptions, skip, or promise every case over a hard-coded few"""

import ast
import json
import sys
from pathlib import Path

TESTS = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline/operators/tests")
SWEEPING_WORDS = ("Every", "All", "Each", "Always", "Never", "Any")


def Assertions_In(node: ast.AST) -> list[ast.AST]:
    """assert statements plus calls that assert by name (pytest.raises, numpy testing, assert helpers)"""
    found: list[ast.AST] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Assert):
            found.append(child)
        elif isinstance(child, ast.Call):
            called = ast.unparse(child.func)
            if "raises" in called or "assert" in called.lower() or "testing." in called or called.startswith("Check"):
                found.append(child)
        elif isinstance(child, ast.With) and any("raises" in ast.unparse(item.context_expr) for item in child.items):
            found.append(child)
    return found


def Conditional_Only(function: ast.FunctionDef) -> bool:
    """whether every assertion sits under an if, for, while or try inside the function"""
    unconditional = 0
    for statement in function.body:
        if isinstance(statement, (ast.If, ast.For, ast.While, ast.Try)):
            continue
        unconditional += len(Assertions_In(statement))
    return unconditional == 0 and len(Assertions_In(function)) > 0


def Broad_Handlers(function: ast.FunctionDef) -> int:
    """except clauses that catch everything or a bare Exception"""
    count = 0
    for child in ast.walk(function):
        if isinstance(child, ast.ExceptHandler):
            caught = "" if child.type is None else ast.unparse(child.type)
            if caught in ("", "Exception", "BaseException"):
                count += 1
    return count


def Skip_Sites(tree: ast.Module) -> list[str]:
    """every skip, skipif and expected-failure site, as source text"""
    sites: list[str] = []
    for child in ast.walk(tree):
        if isinstance(child, (ast.Call, ast.Attribute)):
            text = ast.unparse(child)
            if any(word in text for word in ("skip(", "skipif(", "xfail(", "importorskip(")) and len(text) < 200:
                sites.append(text)
    return sorted(set(sites))


def Main() -> None:
    """one record per flagged test and a summary line"""
    flags: list[dict[str, object]] = []
    defined = 0
    skip_sites: dict[str, list[str]] = {}
    for path in sorted(TESTS.glob("test_*.py")):
        tree = ast.parse(path.read_text())
        skip_sites[path.name] = Skip_Sites(tree)
        for function in [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]:
            if not function.name.startswith("Test_"):
                continue
            defined += 1
            reasons: list[str] = []
            assertions = Assertions_In(function)
            if not assertions:
                reasons.append("no assertion at all")
            elif Conditional_Only(function):
                reasons.append("assertions only under a branch, loop or try")
            if Broad_Handlers(function):
                reasons.append("a broad exception handler")
            if any(word in function.name.split("_") for word in SWEEPING_WORDS):
                literal_collections = [child for child in ast.walk(function)
                                       if isinstance(child, (ast.List, ast.Tuple)) and 0 < len(child.elts) <= 6
                                       and all(isinstance(element, ast.Constant) for element in child.elts)]
                if literal_collections:
                    reasons.append("a sweeping name beside a short literal collection")
            if reasons:
                flags.append({"file": path.name, "test": function.name, "line": function.lineno, "reasons": reasons})
    total_sites = sum(len(sites) for sites in skip_sites.values())
    print(json.dumps({"defined_tests": defined, "flagged": flags, "skip_sites": skip_sites}, indent=1))
    print(f"{defined} Test_ functions defined, {len(flags)} flagged, {total_sites} distinct skip or expected-failure sites",
          file=sys.stderr)


if __name__ == "__main__":
    Main()

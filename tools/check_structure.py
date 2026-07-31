#!/usr/bin/env python3
"""Structure checker for the n-Op journals.

The rules are not written here. They are parsed from the last fenced ``yaml``
block of ``journals/practice/agent-contract.md`` — so the document an agent reads
and the enforcement it faces are the same artifact and cannot disagree.

    python tools/check_structure.py            regenerate generated/corpus.json, then check
    python tools/check_structure.py --check    check only; fail if the emission is stale

Exit 0 clean, 1 on any finding.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
JOURNALS = ROOT / "journals"
CONTRACT = JOURNALS / "practice" / "agent-contract.md"
EMITTED = ROOT / "generated" / "corpus.json"

# A page that must name what it forbids cannot also be searched for those names.
# Exactly one page is exempt, and every run says so out loud — an exemption nobody
# is told about is how the previous corpus grew holes it reported as green.
MARKER_EXEMPT = {"agent-contract"}

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FENCE_RE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
CITE_RE = re.compile(r"\[([a-z0-9][a-z0-9-]{2,})(?:#([a-z0-9][a-z0-9-]*))?\]")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*$", re.MULTILINE)
ORDINAL_RE = re.compile(r"§\s*\d")
LINENUM_RE = re.compile(r"\b[\w./-]+\.(?:md|csv|py)\s*:\s*\d+\b")
PATHCITE_RE = re.compile(r"\bjournals/[\w./-]+\.md\b")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")


def load_contract() -> dict:
    """The last fenced yaml block of the contract IS the rule set."""
    if not CONTRACT.exists():
        sys.exit(f"fatal: no contract at {CONTRACT.relative_to(ROOT)}")
    blocks = re.findall(r"^```yaml\n(.*?)^```", CONTRACT.read_text(encoding="utf-8"),
                        re.DOTALL | re.MULTILINE)
    if not blocks:
        sys.exit("fatal: contract carries no ```yaml schema block")
    return yaml.safe_load(blocks[-1])


def prose(body: str) -> str:
    """Body with fenced blocks and inline code removed — what a reader is asserting."""
    return INLINE_CODE_RE.sub(" ", FENCE_RE.sub("", body))


def load_pages(errs: list[str]) -> list[dict]:
    pages = []
    for path in sorted(JOURNALS.rglob("*.md")):
        rel = path.relative_to(ROOT)
        parts = path.relative_to(JOURNALS).parts
        if not 2 <= len(parts) <= 3:
            errs.append(f"{rel}: pages live at journal/page or journal/section/page")
            continue
        text = path.read_text(encoding="utf-8")
        m = FM_RE.match(text)
        if not m:
            errs.append(f"{rel}: no frontmatter block")
            continue
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            errs.append(f"{rel}: frontmatter is not valid YAML — {str(e).splitlines()[0]}")
            continue
        if not isinstance(fm, dict):
            errs.append(f"{rel}: frontmatter is not a mapping")
            continue
        pages.append({
            "rel": str(rel), "path": path, "fm": fm,
            "body": text[m.end():], "stem": path.stem,
            "journal": parts[0], "section": parts[1] if len(parts) == 3 else None,
        })
    return pages


def check_frontmatter(pages: list[dict], schema: dict, errs: list[str]) -> None:
    required = set(schema["frontmatter"]["required"])
    forbidden = set(schema["frontmatter"]["forbidden"])
    for p in pages:
        fm, rel = p["fm"], p["rel"]
        missing = required - set(fm)
        if missing:
            errs.append(f"{rel}: frontmatter missing {sorted(missing)}")
        present_forbidden = forbidden & set(fm)
        if present_forbidden:
            errs.append(f"{rel}: forbidden frontmatter key(s) {sorted(present_forbidden)}")
        extra = set(fm) - required - forbidden
        if extra:
            errs.append(f"{rel}: unknown frontmatter key(s) {sorted(extra)}")
        if fm.get("id") != p["stem"]:
            errs.append(f"{rel}: id {fm.get('id')!r} does not match filename stem {p['stem']!r}")

        owns = fm.get("owns") or []
        if not owns:
            errs.append(f"{rel}: owns is empty — a page that owns nothing is a page "
                        f"the duplicate-topic invariant cannot see")
        if fm.get("id") in owns:
            errs.append(f"{rel}: owns lists its own id — that claims no topic")

        anchors = fm.get("anchors") or {}
        headings = set(HEADING_RE.findall(p["body"]))
        for slug, heading in anchors.items():
            if heading not in headings:
                errs.append(f"{rel}: anchor '{slug}' declares heading {heading!r}, "
                            f"which is not a heading on this page")


def check_topics(pages: list[dict], errs: list[str]) -> dict[str, tuple[str, str]]:
    owner: dict[str, tuple[str, str]] = {}
    for p in pages:
        for topic in p["fm"].get("owns") or []:
            if topic in owner:
                errs.append(f"duplicate topic {topic!r}: owned by "
                            f"{owner[topic][0]} and {p['fm']['id']}")
            else:
                owner[topic] = (p["fm"]["id"], p["rel"])
    return owner


def check_citations(pages: list[dict], errs: list[str]) -> None:
    by_id = {p["fm"].get("id"): p for p in pages}
    for p in pages:
        rel, text = p["rel"], prose(p["body"])
        declared = set(p["fm"].get("depends-on") or [])
        for target in declared:
            if target not in by_id:
                errs.append(f"{rel}: depends-on names {target!r}, which is not a page")
        for cid, anchor in CITE_RE.findall(text):
            if cid not in by_id:
                errs.append(f"{rel}: citation [{cid}] resolves to no page")
                continue
            if cid not in declared:
                errs.append(f"{rel}: cites [{cid}] without a depends-on edge")
            if anchor and anchor not in (by_id[cid]["fm"].get("anchors") or {}):
                errs.append(f"{rel}: cites [{cid}#{anchor}] but {cid} declares no "
                            f"such anchor")
        if ORDINAL_RE.search(text):
            errs.append(f"{rel}: section ordinal (§N) — cite a declared anchor instead")
        if LINENUM_RE.search(text):
            errs.append(f"{rel}: line-number citation — line refs rot on every edit")
        if PATHCITE_RE.search(text):
            errs.append(f"{rel}: cites a page by path — cite the id")


def check_tables(pages: list[dict], errs: list[str]) -> None:
    """Header cell-count against every row.

    An unescaped `|` inside physics notation splits a row and shifts every cell
    right of it, and by-name checks keep passing because the cells they read are
    non-empty and merely hold the wrong values. That shipped for a month here.
    """
    for p in pages:
        width, hdr_line = None, 0
        for n, line in enumerate(FENCE_RE.sub("", p["body"]).splitlines(), 1):
            if not TABLE_ROW_RE.match(line):
                width = None
                continue
            if TABLE_SEP_RE.match(line):
                continue
            cells = len(UNESCAPED_PIPE.split(line.strip().strip("|")))
            if width is None:
                width, hdr_line = cells, n
            elif cells != width:
                errs.append(f"{p['rel']}:{n}: table row has {cells} cells, header "
                            f"(line {hdr_line}) has {width} — escape literal pipes as \\|")
                width = None


def check_vocabulary(pages: list[dict], schema: dict, errs: list[str]) -> None:
    markers = [m for group in schema["forbidden-markers"].values() for m in group]
    retired = {tok: (fam, new)
               for fam, mapping in schema["retired-vocabularies"].items()
               for tok, new in mapping.items()}
    tok_re = re.compile(r"(?<![\w-])(" + "|".join(re.escape(t) for t in retired) + r")(?![\w-])")
    for p in pages:
        rel, pid, text = p["rel"], p["fm"].get("id"), prose(p["body"])
        if pid not in MARKER_EXEMPT:
            low = text.lower()
            for marker in markers:
                if marker.lower() in low:
                    errs.append(f"{rel}: history marker {marker!r} — pages state what "
                                f"is true, not how it got that way; the log holds history")
            for tok in set(tok_re.findall(text)):
                fam, new = retired[tok]
                errs.append(f"{rel}: retired {fam} token {tok!r} — use {new!r}")


def emit(pages: list[dict], owner: dict, schema: dict) -> dict:
    libs = schema.get("libraries", {})
    referenced_by: dict[str, set] = {p["fm"]["id"]: set() for p in pages}
    for p in pages:
        for t in p["fm"].get("depends-on") or []:
            if t in referenced_by:
                referenced_by[t].add(p["fm"]["id"])
    return {
        "pages": {
            p["fm"]["id"]: {
                "path": p["rel"], "title": p["fm"].get("title"),
                "journal": p["journal"], "section": p["section"],
                "library": libs.get(p["journal"]),
                "owns": p["fm"].get("owns") or [],
                "anchors": p["fm"].get("anchors") or {},
                "depends_on": sorted(p["fm"].get("depends-on") or []),
                "referenced_by": sorted(referenced_by[p["fm"]["id"]]),
            } for p in sorted(pages, key=lambda x: x["fm"]["id"])
        },
        "topics": {t: {"page": pid} for t, (pid, _) in sorted(owner.items())},
        "open_questions": [
            {**q, "page": p["fm"]["id"]}
            for p in pages for q in (p["fm"].get("open-questions") or [])
        ],
    }


def main() -> int:
    check_only = "--check" in sys.argv
    schema = load_contract()
    errs: list[str] = []

    pages = load_pages(errs)
    if not pages:
        sys.exit("fatal: no pages found under journals/")

    check_frontmatter(pages, schema, errs)
    owner = check_topics(pages, errs)
    check_citations(pages, errs)
    check_tables(pages, errs)
    check_vocabulary(pages, schema, errs)

    corpus = emit(pages, owner, schema)
    rendered = json.dumps(corpus, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if check_only:
        current = EMITTED.read_text(encoding="utf-8") if EMITTED.exists() else None
        if current != rendered:
            errs.append("generated/corpus.json is stale — run without --check")
    else:
        EMITTED.parent.mkdir(parents=True, exist_ok=True)
        EMITTED.write_text(rendered, encoding="utf-8")

    if errs:
        print(f"{len(errs)} finding(s):\n")
        for e in errs:
            print(f"  {e}")
        return 1

    print(f"structure OK · {len(pages)} pages, {len(owner)} owned topics, "
          f"{len(corpus['open_questions'])} open questions")
    # A clean run must state its own holes, or it is measuring the checker.
    print(f"  exempt from the history-marker sweep: {sorted(MARKER_EXEMPT)} "
          f"(a page that forbids a word must be allowed to name it)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

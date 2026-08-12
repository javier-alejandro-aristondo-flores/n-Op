#!/usr/bin/env python3
"""Structure checker for the n-Op journals.

The rules are not written here. They are parsed from the last fenced ``yaml``
block of ``journals/practice/agent-contract.md`` — so the document an agent reads
and the enforcement it faces are the same artifact and cannot disagree.

    python tools/check_structure.py            regenerate generated/corpus.json, then check
    python tools/check_structure.py --check    check only; fail if the emission is stale
    python tools/check_structure.py --partial  while the corpus is being built

Exit 0 clean, 1 on any finding.

``--partial`` exists because the page graph is **cyclic by design** — two pages each
explain the other — so no order exists in which every citation resolves as it is
written. It downgrades "cites a page that does not exist yet" to a counted note and
keeps every other check hard, so an agent writing one page can still catch its own
frontmatter, table and vocabulary errors. It always prints what it downgraded: a
partial run that read like a clean one would be worse than no run at all.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
JOURNALS = ROOT / "journals"
CONTRACT = JOURNALS / "practice" / "agent-contract.md"
EMITTED = ROOT / "apparatus" / "generated" / "corpus.json"

# Some pages exist to warn about vocabulary, and cannot do that without naming it.
# Each exemption is narrow, carries its reason, and is printed on every run — an
# exemption nobody is told about is how the previous corpus grew holes it reported
# as green. Note these are the three pages a reader consults *about* words, which is
# why they are the three that need to quote them.
# The contract shows paths because showing the layout is its job, and one page names
# the checkers as programs to run rather than as data to cite.
PATH_EXEMPT = {"agent-contract", "conventions", "traps"}

# Tokens whose bare form is retired but which remain correct as part of a proper
# noun. The corpus retired the missing-data marker and kept the software names.
QUALIFIED = {"GAP": ("computer-algebra", "Gaussian Approximation")}

EXEMPT = {
    "agent-contract": "specifies the vocabulary, so it must name what it forbids",
    "traps":          "warns that short tokens collide with physics, by example",
    "glossary":       "disambiguates retired tokens from the external names they shadow",
}

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FENCE_RE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
CITE_RE = re.compile(r"\[([a-z0-9][a-z0-9-]{2,})(?:#([a-z0-9][a-z0-9-]*))?\]")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*$", re.MULTILINE)
# A bare § is an EXTERNAL citation — "Öttinger 2005 §5.3", "Jackson 1998 §17.2" —
# and is legitimate. Internal citations cannot use § at all, since the syntax is
# [page-id#anchor]. So the check is not "is there a §" but "is a corpus page id
# standing in front of one". The old corpus built the blunt version, measured it
# against real prose, and deleted it for crying wolf; this is the precise version.
ORDINAL_RE = re.compile(r"(?<![\w-])([a-z0-9][a-z0-9-]{2,})[\s`]*§\s*\d")
LINENUM_RE = re.compile(r"\b[\w./-]+\.(?:md|csv|py)\s*:\s*\d+\b")
# Every repo path, not only a page. The rule "cite the id, never the path" was
# enforced for pages and unenforced for data artifacts — one citation form checked
# and an equivalent form left to accumulate, which is exactly the asymmetry that let
# 289 backticked page ids go unverified in the previous corpus. Four references had
# already slipped through before this was widened.
PATHCITE_RE = re.compile(r"\b(?:journals|programs|tests|apparatus|data|log|generated|tools)/[\w./-]+")
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
            "rel": str(rel), "path": path, "fm": fm, "fm_text": m.group(1),
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

        # Every open question points at an anchor on its own page, and that pointer
        # was unvalidated — a register whose entries resolve to nothing is worse than
        # no register, because it is what an agent reads to find the gaps.
        for q in fm.get("open-questions") or []:
            if not isinstance(q, dict):
                errs.append(f"{rel}: open-questions entry is not a mapping")
                continue
            for field in ("id", "anchor", "summary"):
                if not q.get(field):
                    errs.append(f"{rel}: open question missing {field!r}")
            a = q.get("anchor")
            if a and a not in (fm.get("anchors") or {}):
                errs.append(f"{rel}: open question {q.get('id')!r} points at anchor "
                            f"{a!r}, which this page does not declare")

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


def check_citations(pages: list[dict], errs: list[str], pending: list[str],
                    schema: dict, partial: bool = False) -> None:
    by_id = {p["fm"].get("id"): p for p in pages}
    # Data artifacts share the page namespace: ids are unique corpus-wide, so a
    # reader never has to know which kind a citation is. They carry no anchors and
    # no graph edge — there is nothing on the other end to depend on.
    data_ids = set(schema.get("data-artifacts") or {})
    unresolved = pending if partial else errs
    for p in pages:
        # Frontmatter carries prose too — an open question's summary can cite a
        # page — and scanning only the body left those citations unchecked.
        rel = p["rel"]
        text = prose(p["body"]) + "\n" + p["fm_text"]
        declared = set(p["fm"].get("depends-on") or [])
        for target in declared:
            if target not in by_id:
                unresolved.append(f"{rel}: depends-on names {target!r}, which is not a page")
        for cid, anchor in CITE_RE.findall(text):
            if cid in data_ids:
                if anchor:
                    errs.append(f"{rel}: [{cid}#{anchor}] — a data artifact has no anchors")
                continue
            if cid not in by_id:
                unresolved.append(f"{rel}: citation [{cid}] resolves to no page")
                continue
            if cid not in declared:
                errs.append(f"{rel}: cites [{cid}] without a depends-on edge")
            if anchor and anchor not in (by_id[cid]["fm"].get("anchors") or {}):
                errs.append(f"{rel}: cites [{cid}#{anchor}] but {cid} declares no "
                            f"such anchor")
        for hit in ORDINAL_RE.findall(text):
            if hit in by_id:
                errs.append(f"{rel}: internal section ordinal '{hit} §N' — cite a "
                            f"declared anchor instead")
        if LINENUM_RE.search(text):
            errs.append(f"{rel}: line-number citation — line refs rot on every edit")
        if p["fm"].get("id") not in PATH_EXEMPT and PATHCITE_RE.search(text):
            hit = PATHCITE_RE.search(text).group(0)
            errs.append(f"{rel}: names the path {hit!r} — cite the id, so a move is "
                        f"one edit to the map and not one per page")
        cited = {c for c, _ in CITE_RE.findall(text)}
        for edge in sorted(declared - cited):
            errs.append(f"{rel}: depends-on names {edge!r} but the body never cites it "
                        f"— the reverse index would overstate coupling")


NAME_ROW = re.compile(r"^\s*\|\s*`([A-Za-z][A-Za-z0-9_]*)`\s*\|[^|]*\[([a-z0-9][a-z0-9-]*)\]")


def check_name_index(pages: list[dict], errs: list[str]) -> None:
    """A row that says 'this name is specified there' must be true of there.

    Every such row already carries a *valid* citation — it resolves, it is in
    depends-on, it passes every other rule. What is unchecked is the proposition
    the row asserts about the target's contents. That is the structural blind
    spot: the rules validate pointers, and a name index is a set of claims.
    """
    by_id = {p["fm"].get("id"): p for p in pages}
    for p in pages:
        for line in p["body"].splitlines():
            m = NAME_ROW.match(line)
            if not m:
                continue
            token, target = m.groups()
            if target in by_id and token not in by_id[target]["body"]:
                errs.append(f"{p['rel']}: name index says `{token}` is specified on "
                            f"[{target}], and that page never uses it")


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
    # A token may belong to more than one retired family — T0..T3 was cost in the
    # oracle and cadence in the operator, which is exactly the collision that made
    # an iterative residual read T3 by cost and T2 by cadence. Keep every reading so
    # the finding names them all rather than silently picking whichever was parsed
    # last.
    retired: dict[str, list[tuple[str, str]]] = {}
    for fam, mapping in schema["retired-vocabularies"].items():
        for tok, new in mapping.items():
            retired.setdefault(tok, []).append((fam, new))
    for p in pages:
        rel, pid = p["rel"], p["fm"].get("id")
        if pid in EXEMPT:
            continue

        # History markers are prose claims, so they are checked against prose.
        low = prose(p["body"]).lower()
        for marker in markers:
            if marker.lower() in low:
                errs.append(f"{rel}: history marker {marker!r} — pages state what "
                            f"is true, not how it got that way; the log holds history")

        # Retired tags are the opposite: they live INSIDE inline code, because the
        # old convention wrote every short symbol in backticks precisely to hold
        # `D1` the tag apart from D1 the wurtzite deformation potential. Checking
        # prose (which strips code spans) therefore missed every tag in the form
        # tags are actually written — verified by probe: `D2`, `T3` and `B7` all
        # passed silently before this.
        #
        # The span must equal the token exactly. `C2/m` is a space group and
        # contains C2; an unbacked D1 is a deformation potential. Neither is a
        # retired tag, and a looser rule would flag both — which is how the old
        # corpus's version of this check came to be deleted for crying wolf.
        # Frontmatter too: an open question's summary is prose and can carry a tag.
        region = FENCE_RE.sub("", p["body"]) + "\n" + p["fm_text"]
        for m in INLINE_CODE_RE.finditer(region):
            tok = m.group(0).strip("` ").strip()
            # A retired marker that is also an external proper noun is legitimate
            # when written in full — the corpus keeps the software names and retires
            # only the bare marker. Judge by what follows it.
            trailer = region[m.end():m.end() + 48].lstrip()
            if tok in QUALIFIED and trailer.startswith(QUALIFIED[tok]):
                continue
            if tok in retired:
                opts = " or ".join(f"{new!r} ({fam})" for fam, new in retired[tok])
                errs.append(f"{rel}: retired tag `{tok}` — use {opts}")


def emit(pages: list[dict], owner: dict, schema: dict) -> dict:
    # A digest of the pages this index was built from, so a READER can tell it is
    # current. The checker already detects staleness; a reader consulting the index
    # directly could not — and a stale index does not fail quietly here, it
    # manufactures false findings, because a missing topic is documented as meaning
    # "no page claims this" rather than "the index is behind". Content-hashed, not
    # timestamped, so regeneration stays a no-op.
    digest = hashlib.sha256()
    for p in sorted(pages, key=lambda x: x["rel"]):
        digest.update(p["rel"].encode())
        digest.update(p["path"].read_bytes())
    libs = schema.get("libraries", {})
    referenced_by: dict[str, set] = {p["fm"]["id"]: set() for p in pages}
    for p in pages:
        for t in p["fm"].get("depends-on") or []:
            if t in referenced_by:
                referenced_by[t].add(p["fm"]["id"])
    return {
        "source_digest": digest.hexdigest()[:16],
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
        "data": dict(sorted((schema.get("data-artifacts") or {}).items())),
        # Malformed entries are already reported as findings; emitting must not
        # crash on them. A checker that dies on bad input reports nothing at all,
        # and its traceback can even satisfy a probe by accident — which is how
        # this line was found.
        "open_questions": [
            {**q, "page": p["fm"]["id"]}
            for p in pages for q in (p["fm"].get("open-questions") or [])
            if isinstance(q, dict)
        ],
    }


def main() -> int:
    check_only = "--check" in sys.argv
    partial = "--partial" in sys.argv
    schema = load_contract()
    errs: list[str] = []
    pending: list[str] = []

    pages = load_pages(errs)
    if not pages:
        sys.exit("fatal: no pages found under journals/")

    check_frontmatter(pages, schema, errs)
    owner = check_topics(pages, errs)
    check_citations(pages, errs, pending, schema, partial)
    check_name_index(pages, errs)
    check_tables(pages, errs)
    check_vocabulary(pages, schema, errs)

    corpus = emit(pages, owner, schema)
    rendered = json.dumps(corpus, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if check_only or partial:
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

    if pending:
        print(f"PARTIAL · {len(pending)} citation(s) awaiting a page that is not "
              f"written yet:\n")
        for m in pending:
            print(f"  {m}")
        print()
    print(f"structure {'OK (partial)' if partial else 'OK'} · {len(pages)} pages, "
          f"{len(owner)} owned topics, {len(corpus['open_questions'])} open questions")
    # A clean run must state its own holes, or it is measuring the checker.
    print(f"  exempt from the path sweep: {sorted(PATH_EXEMPT)} "
          f"(they show the layout or name a program to run)")
    print("  exempt from the vocabulary sweep, and why:")
    for pid, why in sorted(EXEMPT.items()):
        print(f"    {pid:<16} {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

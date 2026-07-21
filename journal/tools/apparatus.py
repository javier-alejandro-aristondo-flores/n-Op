#!/usr/bin/env python3
"""Generate the book apparatus and check its invariants.

Emits at the repo root:
    contents.md   chapters -> pages, in reading order (the table of contents)
    index.md      canonical topic -> owning page (the "one fact, one home" index)

Checks (exit 1 on any failure):
    1. every page has parseable frontmatter and the required fields
    2. `id` globally unique
    3. `canonical-for` topics globally unique   <- the anti-drift invariant
    4. `depends-on` / `referenced-by` symmetric
    5. every [id] reference in prose resolves to a real page
    6. `content-hash` matches the body (stale hash = someone edited by hand
       without regenerating, which breaks working-copy staleness detection)

This replaces the old assemble.py, whose job (emitting monoliths that
restated the tree) was deleted with the monoliths themselves.

    python tools/apparatus.py            regenerate + check
    python tools/apparatus.py --check    check only, write nothing
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "pages"

REQUIRED = ("id", "title", "chapter", "tag", "authority", "content-hash")
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
REF_RE = re.compile(r"\[([a-z0-9][a-z0-9-]{2,})\]")


def parse(path: pathlib.Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if not m:
        return None
    fm, body = m.group(1), text[m.end():]
    rec: dict = {"path": path, "body": body, "_fm": fm}
    for line in fm.splitlines():
        sm = re.match(r"^([a-z-]+):\s*(.*)$", line)
        if sm and sm.group(2).strip() not in ("", "[]"):
            rec[sm.group(1)] = sm.group(2).strip()
        elif sm:
            rec[sm.group(1)] = [] if sm.group(2).strip() == "[]" else None
    for name in ("canonical-for", "depends-on", "referenced-by"):
        rec[name] = list_field(fm, name)
    return rec


def list_field(fm: str, name: str) -> list[str]:
    if not re.search(rf"^{re.escape(name)}:", fm, re.MULTILINE):
        return []
    out, started = [], False
    for line in fm.splitlines():
        if re.match(rf"^{re.escape(name)}:", line):
            if line.split(":", 1)[1].strip() == "[]":
                return []
            started = True
            continue
        if started:
            if line.startswith("  - "):
                out.append(line[4:].strip())
            elif line and not line[0].isspace():
                break
    return out


def load() -> list[dict]:
    pages = []
    for p in sorted(PAGES.rglob("*.md")):
        rec = parse(p)
        if rec is None:
            print(f"FAIL  no frontmatter: {p.relative_to(ROOT)}")
            continue
        rec["rel"] = p.relative_to(ROOT).as_posix()
        pages.append(rec)
    return pages


def sort_key(r: dict) -> tuple:
    ch, _, n = r.get("tag", "0.0").partition(".")
    return (int(ch or 0), int(n or 0))


def check(pages: list[dict]) -> list[str]:
    errs: list[str] = []

    for r in pages:
        for f in REQUIRED:
            if not r.get(f):
                errs.append(f"{r['rel']}: missing frontmatter field `{f}`")

    for r in pages:
        want = f"{int(r['chapter']):02d}-{r.get('chapter-name','')}"
        got = r["path"].parent.name
        if got != want:
            errs.append(f"{r['rel']}: filed under {got}/ but frontmatter says "
                        f"chapter {r['chapter']} ({want}/)")

    seen: dict[str, str] = {}
    for r in pages:
        pid = r.get("id")
        if pid in seen:
            errs.append(f"duplicate id `{pid}`: {seen[pid]} and {r['rel']}")
        seen[pid] = r["rel"]

    owner: dict[str, str] = {}
    for r in pages:
        for topic in r["canonical-for"]:
            if topic in owner:
                errs.append(
                    f"canonical-for `{topic}` claimed twice: {owner[topic]} and {r['rel']}")
            owner[topic] = r["rel"]

    by_id = {r["id"]: r for r in pages}
    for r in pages:
        for dep in r["depends-on"]:
            t = by_id.get(dep)
            if t is None:
                errs.append(f"{r['rel']}: depends-on unknown id `{dep}`")
            elif r["id"] not in t["referenced-by"]:
                errs.append(
                    f"asymmetry: {r['id']} depends-on {dep}, but {dep} does not list it")

    for r in pages:
        for ref in set(REF_RE.findall(r["body"])):
            if ref in by_id or "-" not in ref:
                continue
            if re.match(r"^(arch|impl|mvp|deriv)-", ref):
                errs.append(f"{r['rel']}: reference [{ref}] resolves to no page")

    for r in pages:
        actual = hashlib.sha256(r["body"].encode()).hexdigest()[:12]
        if r.get("content-hash") and r["content-hash"] != actual:
            errs.append(
                f"{r['rel']}: stale content-hash "
                f"({r['content-hash']} -> {actual}); regenerate")

    return errs


def registry_tallies() -> tuple[int, int, dict[str, int]] | None:
    """(substantive, markers, diff tally) from the canonical registry CSV.
    A row whose Tier is an em dash is an architectural marker, not a formula."""
    csv_path = ROOT.parent / "physics/library/formulas/registry-manifest.csv"
    if not csv_path.exists():
        return None
    import csv as _csv
    with csv_path.open(encoding="utf-8", newline="") as fh:
        rows = list(_csv.reader(fh))[1:]
    markers, diff = 0, {}
    for row in rows:
        tier = row[4].strip() if len(row) > 4 else ""
        if tier == "—":
            markers += 1
            continue
        if len(row) > 5:
            d = row[5].strip()
            diff[d] = diff.get(d, 0) + 1
    return len(rows) - markers, markers, diff


def check_counts(pages: list[dict]) -> list[str]:
    """The registry CSV is canonical for formula rows; the vocabularies page is
    canonical for the counts. They must agree, and so must every prose claim."""
    errs: list[str] = []
    tallies = registry_tallies()
    if tallies is None:
        return ["registry-manifest.csv not found — cannot check counts"]
    substantive, markers, _diff = tallies

    canon = next((r for r in pages if "vocabulary counts" in r["canonical-for"]), None)
    if canon is None:
        canon = next((r for r in pages if r["id"] == "arch-09-vocabularies"), None)
    if canon is None:
        return ["no page claims `vocabulary counts` — cannot check counts"]

    m = re.search(r"(\d+)\s+substantive\s*\(\+(\d+)\s+architectural markers",
                  canon["body"])
    if not m:
        errs.append(f"{canon['rel']}: canon formula-count row not parseable")
    else:
        c_sub, c_mark = int(m.group(1)), int(m.group(2))
        if c_sub != substantive:
            errs.append(f"count drift: {canon['rel']} claims {c_sub} substantive "
                        f"formulas; registry CSV has {substantive}")
        if c_mark != markers:
            errs.append(f"count drift: {canon['rel']} claims {c_mark} markers; "
                        f"registry CSV has {markers}")

    # "N substantive formulas" is the canonical whole-vocabulary phrasing
    # (conventions §count phrasing) and is never used for a subset, so it can
    # be checked strictly wherever it appears.
    for r in pages:
        for n in re.findall(r"(\d+)\s+substantive formulas", r["body"]):
            if int(n) != substantive:
                errs.append(f"{r['rel']}: says {n} substantive formulas; "
                            f"registry CSV has {substantive}")
    return errs


def check_citations(pages: list[dict]) -> list[str]:
    """Section coordinates must resolve, and nothing may cite a line number."""
    errs: list[str] = []
    coords: dict[str, set[str]] = {}
    for r in pages:
        found = set()
        for line in r["body"].splitlines():
            if line.startswith("#"):
                # numeric section coordinates (4.2, 12.0.3)
                for tok in re.findall(r"\b\d+(?:\.\d+)+\b", line):
                    found.add(tok)
                    found.add(tok.split(".")[0])
                # dated headings: pages like [timeline] are cited by date, and a
                # dot-requiring pattern silently skipped every one of them
                for tok in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", line):
                    found.add(tok)
        coords[r["id"]] = found

    # the corpus cites both full ids (`arch-12-cert §12.0.3`) and the historical
    # short form (`arch-12 §12.0.3`); resolve the short form by unique prefix
    prefix: dict[str, str] = {}
    for pid in coords:
        m = re.match(r"^((?:arch|impl|mvp)-\d+)-", pid)
        if m:
            prefix.setdefault(m.group(1), pid)

    cite = re.compile(r"\[?([a-z][a-z0-9-]{3,})\]?[`\s]*§(\d{4}-\d{2}-\d{2}|\d+(?:\.\d+)*)")
    for r in pages:
        for pid, coord in cite.findall(r["body"]):
            pid = pid if pid in coords else prefix.get(pid, pid)
            if pid not in coords or not coords[pid]:
                continue          # unknown target or a page with no numbered headings
            if coord not in coords[pid] and coord.split(".")[0] not in coords[pid]:
                errs.append(f"{r['rel']}: §{coord} does not resolve in `{pid}`")

    lineref = re.compile(r"\b[\w./-]+\.md:\d+\b")
    for r in pages:
        for hit in set(lineref.findall(r["body"])):
            errs.append(f"{r['rel']}: line-number citation `{hit}` "
                        f"(line refs rot on every edit — cite a heading)")
    return errs


def render_contents(pages: list[dict]) -> str:
    out = ["# Contents", "",
           "Generated by `tools/apparatus.py` — do not edit.", "",
           "The `tag` (e.g. `4.2`) is a **display label**: regenerated freely, "
           "never cited. Cite the `id`.", ""]
    cur = None
    for r in sorted(pages, key=sort_key):
        ch = r.get("chapter")
        if ch != cur:
            cur = ch
            name = (r.get("chapter-name") or "").replace("-", " ")
            out += ["", f"## {ch} — {name}", ""]
        topics = ", ".join(r["canonical-for"][:3])
        supp = " *(supporting)*" if r.get("authority") == "supporting" else ""
        out.append(f"- **{r['tag']}** [{r['title']}]({r['rel']}) "
                   f"· `{r['id']}`{supp}")
        if topics:
            out.append(f"  <br/>canonical for: {topics}")
    out.append("")
    return "\n".join(out)


def render_index(pages: list[dict]) -> str:
    rows = []
    for r in pages:
        for topic in r["canonical-for"]:
            rows.append((topic, r))
    rows.sort(key=lambda t: t[0].lower())

    out = ["# Index", "",
           "Generated by `tools/apparatus.py` — do not edit.", "",
           "Every canonical topic and the single page that owns it. If a topic "
           "is not here, no page claims it; if it appears once, the "
           "one-fact-one-home invariant holds.", "",
           "| Topic | Page | id |", "|---|---|---|"]
    for topic, r in rows:
        out.append(f"| {topic} | {r['tag']} [{r['title']}]({r['rel']}) | `{r['id']}` |")
    out += ["", f"*{len(rows)} canonical topics across {len(pages)} pages.*", ""]
    return "\n".join(out)


def restamp(pages: list[dict]) -> int:
    """Rewrite stale content-hash values in place. The hash is tool-maintained:
    regenerating restamps it, --check verifies it."""
    n = 0
    for r in pages:
        actual = hashlib.sha256(r["body"].encode()).hexdigest()[:12]
        if r.get("content-hash") == actual:
            continue
        text = r["path"].read_text(encoding="utf-8")
        text = re.sub(r"^content-hash:.*$", f"content-hash: {actual}",
                      text, count=1, flags=re.MULTILINE)
        r["path"].write_text(text, encoding="utf-8")
        r["content-hash"] = actual
        n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    pages = load()
    if not pages:
        print("FAIL  no pages found under pages/")
        return 1

    if not args.check:
        n = restamp(pages)
        if n:
            print(f"restamped {n} content-hash value(s)")
        (ROOT / "contents.md").write_text(render_contents(pages), encoding="utf-8")
        (ROOT / "index.md").write_text(render_index(pages), encoding="utf-8")
        print(f"wrote contents.md, index.md ({len(pages)} pages)")

    errs = check(pages)
    errs += check_counts(pages)
    errs += check_citations(pages)

    if errs:
        print(f"\napparatus FAILED — {len(errs)} problem(s):")
        for e in errs:
            print(f"  {e}")
        return 1

    topics = sum(len(r["canonical-for"]) for r in pages)
    print(f"apparatus OK — {len(pages)} pages, {topics} canonical topics, "
          f"graph symmetric, hashes fresh")
    return 0


if __name__ == "__main__":
    sys.exit(main())

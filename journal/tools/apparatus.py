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

# Bracketed tokens that are physics notation, not page ids: species and defect
# concentrations. Miller indices are excluded by the leading-alpha test.
NOT_IDS = frozenset({"platelet", "defect", "carrier", "host", "propagator"})

# Every page may cite these without taking a structural dependency: they are
# indexes over the corpus, not upstream sources. An edge to them from all 58
# pages would say nothing and would make the graph a hairball.
INDEX_PAGES = frozenset({"timeline", "traps"})

FENCE_RE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
CHANGELOG_RE = re.compile(r"^#+ Changelog\b.*", re.DOTALL | re.MULTILINE)


def citable(body: str) -> str:
    """Body text that can create a graph edge.

    A changelog entry, a supersession banner, or an example inside a code fence
    mentions a page without depending on it; promoting those to edges is what
    turns a dependency graph into a mention graph."""
    body = FENCE_RE.sub("", body)
    body = CHANGELOG_RE.sub("", body)
    return "\n".join(ln for ln in body.splitlines() if not ln.lstrip().startswith(">"))


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

    # `status` and `authority` are closed vocabularies; a typo would otherwise
    # invent a state nothing handles.
    for r in pages:
        if r.get("status") and r["status"] not in ("draft", "review", "stable"):
            errs.append(f"{r['rel']}: status `{r['status']}` is not "
                        f"draft | review | stable")
        if r.get("authority") not in ("canon", "supporting"):
            errs.append(f"{r['rel']}: authority `{r.get('authority')}` is not "
                        f"canon | supporting")

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
        # ...and the reverse. Only one direction was checked, so a stale
        # `referenced-by` entry left by a deleted citation survived silently --
        # and `referenced-by` is what a reader follows to find consumers.
        for back in r["referenced-by"]:
            t = by_id.get(back)
            if t is None:
                errs.append(f"{r['rel']}: referenced-by unknown id `{back}`")
            elif r["id"] not in t["depends-on"]:
                errs.append(
                    f"asymmetry: {r['id']} is referenced-by {back}, "
                    f"but {back} does not depends-on it")

    # Every bracketed lowercase token is checked, not just the arch/impl/mvp/deriv
    # families: the old prefix filter skipped `[instructions]`, `[product]`,
    # `[traps]` and every other unprefixed id, which is most of the corpus.
    # Non-id brackets in this domain are concentrations and Miller indices; they
    # are listed rather than pattern-guessed, so a new one forces a decision.
    for r in pages:
        for ref in set(REF_RE.findall(r["body"])):
            if ref in by_id or ref in NOT_IDS or not ref[0].isalpha():
                continue
            errs.append(f"{r['rel']}: reference [{ref}] resolves to no page "
                        f"(add it to NOT_IDS if it is a concentration or index)")

    # An `[id]` in the body is what creates a depends-on edge (conventions,
    # "depends-on edge criterion"). Derived mechanically so the graph is
    # auditable rather than asserted. Excluded: fenced code, changelog entries,
    # blockquote banners, and the two index pages every page may cite freely.
    for r in pages:
        for ref in sorted(set(REF_RE.findall(citable(r["body"])))):
            if ref not in by_id or ref == r["id"] or ref in INDEX_PAGES:
                continue
            if ref not in r["depends-on"]:
                errs.append(f"{r['rel']}: body cites [{ref}] but does not "
                            f"depends-on it (conventions, edge criterion)")

    # No acyclicity check, deliberately. `depends-on` is a reference relation
    # between explanations, not a build order: arch-04-state and arch-05-generic
    # each explain the other, and the corpus is one large strongly-connected
    # component by design. A cycle check here would fire forty times and mean
    # nothing. Nothing may compute a transitive closure over this graph and read
    # it as layering — see [conventions].

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

    # The other five canonical whole-vocabulary phrasings (conventions, "count
    # phrasing is canonical"). Only "N substantive formulas" was ever checked, so
    # the rest drifted freely -- and the template count had three values in force.
    # Subset claims must use a different phrasing by construction, which is what
    # makes a strict check safe here. Changelogs are excluded: they quote
    # superseded counts on purpose.
    VOCAB = {"residual categories": 19, "methods": 12, "templates": 20,
             "observable bundles": 11, "cert obligations": 10}
    for r in pages:
        body = CHANGELOG_RE.sub("", r["body"])
        for phrase, want in VOCAB.items():
            for n in re.findall(rf"(?<!Stage )(?<!stage )(\d+)\s+{re.escape(phrase)}\b", body):
                if int(n) != want:
                    errs.append(f"{r['rel']}: says {n} {phrase}; canon is {want}")

    # Per-tag diff tallies quoted in prose, e.g. "`D2` adjoint-required (23)".
    # This tally was computed here and compared against nothing for as long as it
    # has existed, so it drifted every time a row was retagged -- and a retag is
    # exactly when it matters. Only backticked tags count, per the conventions'
    # backtick rule: `D1` is a diff tag, D1 unbacked is a deformation potential.
    TAG_COUNT = re.compile(r"`(D[0-9N])`[^`(]{0,90}?\((\d+)\)")
    for r in pages:
        for tag, n in TAG_COUNT.findall(r["body"]):
            want = _diff.get(tag, 0)
            if int(n) != want:
                errs.append(f"{r['rel']}: says {n} rows tagged `{tag}`; "
                            f"registry CSV has {want}")
    return errs


def check_citations(pages: list[dict]) -> list[str]:
    """Section coordinates must resolve, and nothing may cite a line number."""
    errs: list[str] = []
    coords: dict[str, set[str]] = {}
    # date -> [heading text], per page: three timeline entries share 2026-06-10,
    # so a bare date is ambiguous and the parenthetical is load-bearing.
    dated: dict[str, dict[str, list[str]]] = {}
    for r in pages:
        found = set()
        by_date: dict[str, list[str]] = {}
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
                    by_date.setdefault(tok, []).append(line.lower())
        coords[r["id"]] = found
        dated[r["id"]] = by_date

    # the corpus cites both full ids (`arch-12-cert §12.0.3`) and the historical
    # short form (`arch-12 §12.0.3`); resolve the short form by unique prefix
    prefix: dict[str, str] = {}
    for pid in coords:
        m = re.match(r"^((?:arch|impl|mvp)-\d+)-", pid)
        if m:
            prefix.setdefault(m.group(1), pid)

    cite = re.compile(
        r"\[?([a-z][a-z0-9-]{3,})\]?[`\s]*§(\d{4}-\d{2}-\d{2}|\d+(?:\.\d+)*)"
        r"(?:\s*\(([^)]{1,60})\))?")
    for r in pages:
        for pid, coord, paren in cite.findall(r["body"]):
            pid = pid if pid in coords else prefix.get(pid, pid)
            if pid not in coords or not coords[pid]:
                continue          # unknown target or a page with no numbered headings
            if coord not in coords[pid] and coord.split(".")[0] not in coords[pid]:
                errs.append(f"{r['rel']}: §{coord} does not resolve in `{pid}`")
                continue
            # A dated anchor may be ambiguous. `[timeline]` has three entries on
            # 2026-06-10 and two on 2026-07-16, so the parenthetical is part of
            # the address -- and it was never validated: any parenthetical passed.
            heads = dated.get(pid, {}).get(coord)
            if not heads:
                continue
            if paren:
                key = paren.strip().lower()
                if not any(key in h for h in heads):
                    errs.append(f"{r['rel']}: §{coord} ({paren}) matches no heading "
                                f"in `{pid}` (dated entries there: "
                                f"{len(heads)} on that date)")
            elif len(heads) > 1:
                errs.append(f"{r['rel']}: §{coord} is ambiguous in `{pid}` "
                            f"({len(heads)} entries share that date) -- "
                            f"add the disambiguating parenthetical")

    # `[traps] §N` is the corpus's most-cited coordinate and the traps page is a
    # bare numbered list, so a duplicated or skipped number silently repoints
    # every citation to it. Neither the numeric-heading harvester above nor the
    # dated-anchor one sees a list item.
    traps = next((r for r in pages if r["id"] == "traps"), None)
    if traps is not None:
        nums = [int(n) for n in re.findall(r"^(\d+)\. \*\*", traps["body"], re.M)]
        dupes = sorted({n for n in nums if nums.count(n) > 1})
        gaps = sorted(set(range(1, max(nums) + 1)) - set(nums)) if nums else []
        if dupes:
            errs.append(f"{traps['rel']}: duplicate trap numbers {dupes}")
        if gaps:
            errs.append(f"{traps['rel']}: missing trap numbers {gaps}")
        have = set(nums)
        for r in pages:
            for n in re.findall(r"traps\]?`?\s*§\s*(\d+)", r["body"]):
                if int(n) not in have:
                    errs.append(f"{r['rel']}: cites `traps` §{n}, which does not exist")

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

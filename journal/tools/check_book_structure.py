#!/usr/bin/env python3
"""Generate the book apparatus and check its invariants.

Emits at the repo root:
    contents.md   chapters -> pages, in reading order (the table of contents)
    index.md      canonical topic -> owning page (the "one fact, one home" index)

Restamps three tool-maintained things: `content-hash`, the derived
`referenced-by`, and the probe count quoted in prose.

Checks (exit 1 on any failure):
     1. every page has parseable frontmatter and the required fields
     2. `id` globally unique
     3. `canonical-for` topics globally unique   <- the anti-drift invariant
     4. `depends-on` names a real page; `referenced-by` is not stale
     5. every [id] reference in prose resolves to a real page
     6. a body citing an [id] has the corresponding depends-on edge
     7. section coordinates (`§1.3`, `§2026-06-10 (parenthetical)`) resolve,
        and an ambiguous dated anchor is rejected
     8. no line-number citations (`file.md:42` rots on every edit)
     9. registry counts: substantive/marker totals, the five other canonical
        vocabulary phrasings, the ledger headline, the per-tag diff tally, the
        per-tier cost distribution, and the probe count
    10. trap numbering contiguous, and `[traps] §N` resolves
    11. `authority` in vocabulary
    12. `content-hash` matches the body (stale hash = someone edited by hand
        without regenerating, which breaks working-copy staleness detection)

This list is duplicated in prose at `journal/instructions.md` §8 and
`10.1-conventions`; `check_the_checkers.py` is what keeps all three honest.

This replaces the old assemble.py, whose job (emitting monoliths that
restated the tree) was deleted with the monoliths themselves.

    python tools/check_book_structure.py            regenerate + check
    python tools/check_book_structure.py --check    check only, write nothing
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys

import corpus_root

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "pages"
REPO = ROOT.parent

REQUIRED = ("id", "title", "authority", "content-hash")
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
    rec.update(shelf_position(path))
    return rec


def shelf_position(path: pathlib.Path) -> dict:
    """Where the page sits, read off the path rather than restated in it.

    `chapter`, `chapter-name` and `tag` used to be hand-written frontmatter
    that duplicated the folder and the filename exactly -- 174 lines across 58
    pages holding nothing the path did not already say, plus a checker whose
    only job was confirming the two agreed. Deriving them makes the agreement
    unbreakable and deletes the check with the redundancy that needed it."""
    folder = path.parent.name                       # 04-pipeline-and-compilation
    number, _, slug = folder.partition("-")
    return {"chapter": number.lstrip("0") or "0",
            "chapter-name": slug,
            "tag": path.name.split("-", 1)[0]}      # 4.4-computational-overview.md


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


def consumers(pages: list[dict]) -> dict[str, list[str]]:
    """id -> the pages that depends-on it, sorted. The generated
    `referenced-by`. Only ids that resolve are listed: a dangling `depends-on`
    is reported by its own check rather than propagated into a second field."""
    known = {r["id"] for r in pages}
    out: dict[str, list[str]] = {r["id"]: [] for r in pages}
    for r in pages:
        for dep in r["depends-on"]:
            if dep in known:
                out[dep].append(r["id"])
    return {k: sorted(set(v)) for k, v in out.items()}


def check(pages: list[dict]) -> list[str]:
    errs: list[str] = []

    for r in pages:
        for f in REQUIRED:
            if not r.get(f):
                errs.append(f"{r['rel']}: missing frontmatter field `{f}`")

    # `authority` is a closed vocabulary; a typo would otherwise invent a rank
    # the authority order does not handle. (`status` was a closed vocabulary
    # too, and was deleted: all 58 pages read `draft`, so the field carried no
    # information while looking exactly like a signal.)
    for r in pages:
        if r.get("authority") not in ("canon", "supporting"):
            errs.append(f"{r['rel']}: authority `{r.get('authority')}` is not "
                        f"canon | supporting")

    # No chapter-versus-folder check: `chapter`, `chapter-name` and `tag` are
    # now read off the path (`shelf_position`), so they cannot disagree with it.
    # An invariant held by construction beats one held by a checker.

    seen: dict[str, str] = {}
    for r in pages:
        pid = r.get("id")
        if pid in seen:
            errs.append(f"duplicate id `{pid}`: {seen[pid]} and {r['rel']}")
        seen[pid] = r["rel"]

    # Case- and whitespace-insensitive: `mvp scope` and `MVP scope` were two
    # pages claiming the same topic, and the anti-drift invariant -- the one
    # check the corpus calls load-bearing -- did not see it.
    owner: dict[str, tuple[str, str]] = {}
    for r in pages:
        for topic in r["canonical-for"]:
            key = " ".join(topic.lower().split())
            if key in owner:
                prev_topic, prev_rel = owner[key]
                same = " identically" if prev_topic == topic else \
                    f" ({prev_topic!r} vs {topic!r} -- same topic, different casing)"
                errs.append(
                    f"canonical-for `{topic}` claimed twice: {prev_rel} and "
                    f"{r['rel']}{same}")
            owner[key] = (topic, r["rel"])

    by_id = {r["id"]: r for r in pages}
    for r in pages:
        for dep in r["depends-on"]:
            if dep not in by_id:
                errs.append(f"{r['rel']}: depends-on unknown id `{dep}`")

    # `referenced-by` is generated, not authored. It was 381 hand-kept entries
    # mirroring 381 `depends-on` entries exactly, guarded by a two-direction
    # symmetry check that existed solely to police the duplication. Now it is
    # derived and restamped like `content-hash`, so asymmetry and unknown-id
    # entries are both unrepresentable. This check is the freshness gate.
    want = consumers(pages)
    for r in pages:
        if r["referenced-by"] != want[r["id"]]:
            errs.append(f"{r['rel']}: stale referenced-by; regenerate "
                        f"(have {r['referenced-by']}, derived {want[r['id']]})")

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
    # between explanations, not a build order: unified-state and generic-dynamics
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


def registry_tallies() -> tuple[int, int, dict[str, int], dict[str, int]] | None:
    """(substantive, markers, diff tally, cost-tier tally) from the registry CSV.
    A row whose Tier is an em dash is an architectural marker, not a formula."""
    csv_path = ROOT.parent / "physics/library/formulas/registry-manifest.csv"
    if not csv_path.exists():
        return None
    import csv as _csv
    with csv_path.open(encoding="utf-8", newline="") as fh:
        rows = list(_csv.reader(fh))[1:]
    markers, diff, tier_tally = 0, {}, {}
    for row in rows:
        tier = row[4].strip() if len(row) > 4 else ""
        if tier == "—":
            markers += 1
            continue
        tier_tally[tier] = tier_tally.get(tier, 0) + 1
        if len(row) > 5:
            d = row[5].strip()
            diff[d] = diff.get(d, 0) + 1
    return len(rows) - markers, markers, diff, tier_tally


def check_counts(pages: list[dict]) -> list[str]:
    """The registry CSV is canonical for formula rows; the vocabularies page is
    canonical for the counts. They must agree, and so must every prose claim."""
    errs: list[str] = []
    tallies = registry_tallies()
    if tallies is None:
        return ["registry-manifest.csv not found — cannot check counts"]
    substantive, markers, _diff, _tier = tallies

    canon = next((r for r in pages if "vocabulary counts" in r["canonical-for"]), None)
    if canon is None:
        canon = next((r for r in pages if r["id"] == "canonical-vocabularies"), None)
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

    # ...and the constants above are themselves anchored, so they cannot quietly
    # disagree with the pages that own the vocabularies. The owning page states
    # its size in its own title; if someone adds a method and retitles 6.4, this
    # fires until the constant is updated deliberately. Verified 2026-07-22
    # against the actual lists: 12 methods, 20 templates, 11 bundles, 10
    # obligations, 4 typeclasses, and 9+3+5+2 = 19 categories.
    TITLE_ANCHOR = {"computational-methods": ("methods", r"(\d+) computational methods"),
                    "property-templates": ("templates", r"(\d+) abstract-property templates"),
                    "observable-bundles": ("observable bundles", r"(\d+) observable bundles")}
    for r in pages:
        anchor = TITLE_ANCHOR.get(r["id"])
        if not anchor:
            continue
        key, pat = anchor
        m2 = re.search(pat, r.get("title", ""))
        if not m2:
            errs.append(f"{r['rel']}: title no longer states its vocabulary size "
                        f"(expected /{pat}/) — the {key} count anchor is broken")
        elif int(m2.group(1)) != VOCAB[key]:
            errs.append(f"{r['rel']}: title says {m2.group(1)} {key}; "
                        f"check_book_structure.py's canon constant is {VOCAB[key]}")
    for r in pages:
        body = CHANGELOG_RE.sub("", r["body"])
        for phrase, want in VOCAB.items():
            for n in re.findall(rf"(?<!Stage )(?<!stage )(\d+)\s+{re.escape(phrase)}\b", body):
                if int(n) != want:
                    errs.append(f"{r['rel']}: says {n} {phrase}; canon is {want}")

    # The ledger's headline count against its own table's max row id. The
    # glossary has asserted "lint checks it equals the table's max row id" since
    # before any such check existed -- a claim of enforcement with nothing behind
    # it, which is the exact failure the corpus has a rule about.
    ledger = next((r for r in pages if r["id"] == "accuracy-ledger"), None)
    if ledger is not None:
        ids = [int(n) for n in re.findall(r"^\| (\d+) \|", ledger["body"], re.M)]
        if ids:
            top = max(ids)
            for n in re.findall(r"(\d+)\s+ledger-tracked observables", ledger["body"]):
                if int(n) != top:
                    errs.append(f"{ledger['rel']}: says {n} ledger-tracked "
                                f"observables; the table's max row id is {top}")
            missing = sorted(set(range(1, top + 1)) - set(ids))
            if missing:
                errs.append(f"{ledger['rel']}: ledger rows missing: {missing}")

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

    # "N probes" — the calibration's own size, quoted in four places. It drifted
    # the moment two probes were added, which is the same failure the calibration
    # exists to catch, one level up again. Counted from check_the_checkers.py's source.
    # The probe count is derived and restamped by `rewrite_probe_count`; this is
    # the freshness gate for `--check`, which writes nothing. Allowing up to two
    # intervening words matters: the first version required the number to abut
    # "probes", and `[traps]` §58 -- the trap about checkers that are not looking
    # -- says "29 SUCH probes" and was skipped for exactly that reason.
    want = probe_count()
    if want:
        for label, _path, body in quoting_probe_count(pages):
            for n, _mid, _tail in PROBE_COUNT_RE.findall(
                    CHANGELOG_RE.sub("", body)):
                if int(n) != want:
                    errs.append(f"{label}: says {n} probes; check_the_checkers.py "
                                f"defines {want} — run check_book_structure.py to restamp")

    # Cost-tier distributions, the diff tally's twin. Only the diff tally was
    # checked, so the tier line beside it drifted to 75/40/13/4 against an actual
    # 76/40/11/5 -- and because the wrong numbers still summed to 132, the error
    # survived every eyeball that checked the total. A distribution line is one
    # naming three or more tiers with counts; a lone `T3 (computing C)` is prose.
    TIER_COUNT = re.compile(r"\bT([0-3])\b[^()\n]{0,90}?\((\d+)")
    for r in pages:
        for line in r["body"].splitlines():
            hits = TIER_COUNT.findall(line)
            if len(hits) < 3:
                continue
            for tier, n in hits:
                want = _tier.get(f"T{tier}", 0)
                if int(n) != want:
                    errs.append(f"{r['rel']}: says {n} rows in cost tier T{tier}; "
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
                # The section number is the leading token of the heading, and
                # only that. Matching every number in the line would harvest
                # "the 12 computational methods" as a coordinate; requiring a
                # dot -- which this did, for the old `20.1` scheme -- misses the
                # bare ordinals the corpus uses now (`## 3 Per-cluster table`).
                lead = re.match(r"^#+\s+(\d+(?:\.\d+)*)(?!\S)", line)
                if lead:
                    tok = lead.group(1)
                    found.add(tok)
                    found.add(tok.split(".")[0])
                # dated headings: pages like [timeline] are cited by date, and a
                # dot-requiring pattern silently skipped every one of them
                for tok in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", line):
                    found.add(tok)
                    by_date.setdefault(tok, []).append(line.lower())
        coords[r["id"]] = found
        dated[r["id"]] = by_date

    # No short-form resolution any more. The corpus used to cite `arch-12
    # §12.0.3` alongside the full `arch-12-cert §12.0.3`, and this resolved the
    # bare prefix to a page. Both forms are gone: ids no longer carry a serial
    # number, and section coordinates are bare ordinals under the id
    # (`cert-obligations §1.3`). One address, one spelling.

    cite = re.compile(
        r"\[?([a-z][a-z0-9-]{3,})\]?[`\s]*§(\d{4}-\d{2}-\d{2}|\d+(?:\.\d+)*)"
        r"(?:\s*\(([^)]{1,60})\))?")
    for r in pages:
        for pid, coord, paren in cite.findall(r["body"]):
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
        # ...and in order. The set being complete is not enough: inserting 68
        # above 67 leaves no gap and no duplicate, so this check passed a
        # register that read 66, 68, 67 top-to-bottom. Readers consume it in
        # order and cite it by number.
        if nums and nums != sorted(nums):
            bad = next((i for i in range(1, len(nums)) if nums[i] < nums[i - 1]), None)
            errs.append(f"{traps['rel']}: trap numbers out of order — "
                        f"§{nums[bad]} appears after §{nums[bad - 1]}")
        have = set(nums)
        for r in pages:
            for n in re.findall(r"traps\]?`?\s*§\s*(\d+)", r["body"]):
                if int(n) not in have:
                    errs.append(f"{r['rel']}: cites `traps` §{n}, which does not exist")

    # The open register is a numbered list like the trap register, and readers
    # cite items by number ("arch-18 item 3"). Inserting an item without
    # renumbering silently repoints every such citation. Found the hard way: an
    # insertion on 2026-07-22 produced two items numbered 5, and nothing saw it.
    opens = next((r for r in pages if r["id"] == "open-decisions"), None)
    if opens is not None:
        head, _, _ = opens["body"].partition("**Verifier-soundness gaps")
        nums = [int(n) for n in re.findall(r"^(\d+)\. ", head, re.M)]
        if nums and nums != list(range(1, len(nums) + 1)):
            errs.append(f"{opens['rel']}: open-decision list is numbered {nums}; "
                        f"expected 1..{len(nums)} (items are cited by number)")

    lineref = re.compile(r"\b[\w./-]+\.md:\d+\b")
    for r in pages:
        for hit in set(lineref.findall(r["body"])):
            errs.append(f"{r['rel']}: line-number citation `{hit}` "
                        f"(line refs rot on every edit — cite a heading)")
    return errs


def render_contents(pages: list[dict]) -> str:
    out = ["# Contents", "",
           "Generated by `tools/check_book_structure.py` — do not edit.", "",
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
           "Generated by `tools/check_book_structure.py` — do not edit.", "",
           "Every canonical topic and the single page that owns it. If a topic "
           "is not here, no page claims it; if it appears once, the "
           "one-fact-one-home invariant holds.", "",
           "| Topic | Page | id |", "|---|---|---|"]
    for topic, r in rows:
        # A topic may legitimately contain `|` -- "coupling target shapes (Scalar
        # | AntisymmForm | PSDSymmForm)" does -- and an unescaped one silently
        # splits its row into five cells. The glossary already escapes them; this
        # generator did not, so the index shipped one broken row.
        cell = topic.replace("|", r"\|")
        out.append(f"| {cell} | {r['tag']} [{r['title']}]({r['rel']}) | `{r['id']}` |")
    out += ["", f"*{len(rows)} canonical topics across {len(pages)} pages.*", ""]
    return "\n".join(out)


PROBE_COUNT_RE = re.compile(r"(\d+)((?:\s+\w+){0,2})(\s+probes\b)")


def probe_count() -> int | None:
    """How many things `check_the_checkers.py` actually calibrates: PROBES rows plus the
    guards that cannot be PROBES rows."""
    cal = ROOT / "tools" / "check_the_checkers.py"
    if not cal.exists():
        return None
    src = cal.read_text(encoding="utf-8")
    guards = re.search(r"^GUARD_PROBES\s*=\s*(\d+)", src, re.M)
    n = (len(re.findall(r'^\s{4}\("', src, re.M))
         + (int(guards.group(1)) if guards else 0))
    return n or None


def quoting_probe_count(pages: list[dict]) -> list[tuple[str, pathlib.Path, str]]:
    """(label, path, text) for every file that quotes the probe count.

    `README.md` and `instructions.md` quote it and live outside `pages/`; the
    check that compares it against prose only ever walked `pages`, so two of the
    five sites drifted unwatched -- one of them the file an agent reads first.
    `[timeline]` is excluded: its entries state what was true on a day."""
    out = [(r["rel"], r["path"], r["body"]) for r in pages if r["id"] != "timeline"]
    for extra in (ROOT / "instructions.md", ROOT.parent / "README.md"):
        if extra.exists():
            out.append((extra.name, extra, extra.read_text(encoding="utf-8")))
    return out


def rewrite_probe_count(pages: list[dict]) -> int:
    """Restamp the probe count in prose, the way `content-hash` is restamped.

    This number is a fact about a Python list, transcribed into English in five
    places. It drifted 45 -> 47 -> 48 -> 49 -> 50 over one working pass, and
    50 -> 52 -> 50 over the pass that wrote this function -- every move touching
    four or five files. Checking it only converts the drift into a failing run
    somebody then fixes by hand. Deriving it means nobody types it again."""
    want = probe_count()
    if want is None:
        return 0
    n = 0
    for _label, path, _text in quoting_probe_count(pages):
        text = path.read_text(encoding="utf-8")
        head, sep, changelog = text.partition("\n## Changelog")
        fixed = PROBE_COUNT_RE.sub(
            lambda m: f"{want}{m.group(2)}{m.group(3)}"
            if m.group(1) != str(want) else m.group(0), head)
        if fixed != head:
            path.write_text(fixed + sep + changelog, encoding="utf-8")
            n += 1
    return n


def rewrite_consumers(pages: list[dict]) -> int:
    """Write the derived `referenced-by` block into each page.

    Runs before the hashes are restamped: `referenced-by` is frontmatter, so it
    does not enter the body hash, but the file must settle before anything else
    reads it."""
    want = consumers(pages)
    n = 0
    for r in pages:
        derived = want[r["id"]]
        if r["referenced-by"] == derived:
            continue
        block = ("referenced-by: []" if not derived else
                 "referenced-by:\n" + "\n".join(f"  - {c}" for c in derived))
        text = r["path"].read_text(encoding="utf-8")
        # Replace the whole field: the key line plus any `  - ` items under it.
        text = re.sub(r"^referenced-by:(?:[^\n]*)(?:\n  - [^\n]*)*",
                      lambda _m: block, text, count=1, flags=re.MULTILINE)
        r["path"].write_text(text, encoding="utf-8")
        r["referenced-by"] = derived
        n += 1
    return n


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
    ap.add_argument("--worktree", action="store_true",
                    help="permit running against a scratch worktree copy")
    args = ap.parse_args()

    corpus_root.refuse_if_scratch_copy(REPO, allowed=args.worktree)

    pages = load()
    if not pages:
        print("FAIL  no pages found under pages/")
        return 1

    if not args.check:
        c = rewrite_consumers(pages)
        if c:
            print(f"rewrote referenced-by on {c} page(s)")
        # Before restamping: this rewrites bodies, which changes their hashes.
        p = rewrite_probe_count(pages)
        if p:
            print(f"restamped the probe count in {p} file(s)")
            pages = load()
        n = restamp(pages)
        if n:
            print(f"restamped {n} content-hash value(s)")
        (ROOT / "contents.md").write_text(render_contents(pages), encoding="utf-8")
        (ROOT / "index.md").write_text(render_index(pages), encoding="utf-8")
        print(f"wrote contents.md, index.md ({len(pages)} pages)")

    errs = check(pages)
    errs += check_counts(pages)
    errs += check_citations(pages)

    where = corpus_root.describe(REPO)

    if errs:
        print(f"\nbook structure FAILED @ {where} — {len(errs)} problem(s):")
        for e in errs:
            print(f"  {e}")
        return 1

    topics = sum(len(r["canonical-for"]) for r in pages)
    print(f"book structure OK @ {where}")
    print(f"  {len(pages)} pages, {topics} canonical topics, "
          f"graph symmetric, hashes fresh")
    return 0


if __name__ == "__main__":
    sys.exit(main())

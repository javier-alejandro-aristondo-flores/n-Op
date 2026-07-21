#!/usr/bin/env python3
"""Migrate the n-Op corpus into the book layout.

Target (repo root):
    glossary.md  contents.md  index.md  instructions.md
    pages/<chapter>.<n>-<slug>.md
    pages/appendix/...

Identity model:
  - stable address  = the page `id` (unchanged from the existing frontmatter
                      where one exists; minted from the slug otherwise).
                      Citations resolve against this and nothing else.
  - display tag     = `<chapter>.<n>` — disposable, regenerated freely,
                      never cited.
  - content hash    = sha256 of the body, stamped into frontmatter. Staleness
                      detection for working copies only.

Run with --dry-run to print the mapping without touching the tree.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Chapter scheme — by concern, oracle-dominant.
# Chapters 2-6 are the contiguous oracle block.
# ---------------------------------------------------------------------------

CHAPTERS = {
    1:  "purpose-and-product",
    2:  "inputs-and-state",
    3:  "laws-and-residuals",
    4:  "pipeline-and-compilation",
    5:  "certification-and-applicability",
    6:  "vocabularies-and-registry",
    7:  "consumers-and-seams",
    8:  "mvp-and-build",
    9:  "reference-data-and-accuracy",
    10: "process-and-governance",
    11: "appendix-derivations",
}

# Ordered page manifest: (chapter, source path relative to ROOT).
# Order within a chapter fixes the display tag; it is presentational only.
MANIFEST: list[tuple[int, str]] = [
    # 1 — purpose & product
    (1,  "docs/architecture/01-purpose.md"),
    (1,  "docs/product.md"),
    (1,  "docs/architecture/02-libraries.md"),
    (1,  "docs/implementation/01-principles.md"),
    (1,  "docs/presentation/2026-07-16-justification-report.md"),

    # 2 — inputs & state
    (2,  "docs/architecture/03-inputs.md"),
    (2,  "docs/architecture/04-state.md"),
    (2,  "docs/architecture/15-gamma-hat.md"),
    (2,  "docs/architecture/21-multiscale-state.md"),
    (2,  "docs/architecture/08-bo-levels.md"),
    (2,  "docs/mvp/02-gamma-budget.md"),

    # 3 — laws & residuals
    (3,  "docs/architecture/05-generic.md"),
    (3,  "docs/architecture/11-residuals.md"),
    (3,  "docs/architecture/19-coupling-structure.md"),

    # 4 — pipeline & compilation
    (4,  "docs/architecture/06-physics-graph.md"),
    (4,  "docs/architecture/07-pipeline.md"),
    (4,  "docs/architecture/20-representations.md"),
    (4,  "docs/computational-overview.md"),

    # 5 — certification & applicability
    (5,  "docs/architecture/12-cert.md"),
    (5,  "docs/architecture/13-applicability.md"),
    (5,  "docs/architecture/17-out-of-scope.md"),
    (5,  "docs/implementation/08-cert-detail.md"),

    # 6 — vocabularies & registry
    (6,  "docs/architecture/09-vocabularies.md"),
    (6,  "docs/architecture/10-typeclasses.md"),
    (6,  "docs/architecture/14-topology.md"),
    (6,  "docs/implementation/02-methods.md"),
    (6,  "docs/implementation/03-templates.md"),
    (6,  "docs/implementation/04-formulas.md"),
    (6,  "docs/implementation/05-bundles.md"),
    (6,  "docs/implementation/06-compositions.md"),
    (6,  "docs/formula-registry.md"),
    (6,  "docs/properties.md"),

    # 7 — consumers & seams
    (7,  "docs/architecture/16-pino-bridge.md"),
    (7,  "docs/implementation/07-residual-factory.md"),
    (7,  "docs/implementation/09-cross-cutting.md"),

    # 8 — MVP & build
    (8,  "docs/mvp/01-system.md"),
    (8,  "docs/mvp/03-capabilities.md"),
    (8,  "docs/mvp/04-in-mvp-vs-deferred.md"),
    (8,  "docs/mvp/05-decisions-forced.md"),
    (8,  "docs/mvp/06-build-order.md"),
    (8,  "docs/implementation/10-build-sequence.md"),
    (8,  "docs/implementation/11-verification.md"),

    # 9 — reference data & accuracy
    (9,  "docs/accuracy-ledger.md"),
    (9,  "physics/library/cert/reference-data/README.md"),

    # 10 — process & governance
    (10, "docs/meta/conventions.md"),
    (10, "docs/architecture/18-open-decisions.md"),
    (10, "docs/meta/AUDIT_PROMPT.md"),

    # 11 — appendix: derivations (research stratum, supporting material)
    (11, "physics/research/group-A-ion-dynamics.md"),
    (11, "physics/research/group-B-electronic-magnetic-optical.md"),
    (11, "physics/research/group-C-transport-thermo-chemical.md"),
    (11, "physics/research/defects-surfaces-interfaces.md"),
    (11, "physics/research/non-equilibrium-high-field.md"),
    (11, "physics/research/csp-heterostructure.md"),
    (11, "physics/research/uwbg-observable-catalog.md"),
    (11, "physics/research/residual-generator-catalog.md"),
    (11, "physics/research/implementation-language.md"),
]

# Files deliberately NOT migrated as pages.
#   generated  — deleted outright; the apparatus replaces them
#   collapse   — folded into the timeline page (chapter 10), then deleted
#   keep-live  — stays where it is for now (active work product)
#   husk       — deleted, content already migrated elsewhere
DISPOSITIONS = {
    "generated": [
        "docs/architecture.md",
        "docs/implementation-plan.md",
        "docs/mvp-slice.md",
        "docs/_bundles/full-spec.md",
        "docs/_bundles/llm-context-arch-only.md",
        "docs/_bundles/llm-context-mvp-build.md",
    ],
    "collapse": [
        "docs/audits/2026-06-09-physics-audit.md",
        "docs/audits/2026-06-10-reaudit-addendum.md",
        "docs/audits/2026-06-10-wave1-iii-n-audit.md",
        "docs/audits/2026-07-07-gap-audit.md",
        "docs/audits/2026-07-16-reconciliation-pass.md",
        "docs/specs/2026-06-10-pass-c-accuracy-design.md",
        "docs/specs/2026-06-10-wave1-iii-n-seeding.md",
        "docs/specs/2026-07-16-evolver-duality-research-brief.md",
        "docs/presentation/slides.md",
        "docs/presentation/pullback-diagram.md",
        "docs/presentation/2026-06-25-physics-as-a-cs-oracle.md",
    ],
    "keep-live": [
        "docs/audits/2026-07-16-wave2-beta-ga2o3-audit.md",
        "docs/specs/2026-07-08-wave2-beta-ga2o3-seeding.md",
        "docs/specs/2026-07-16-evolver-duality-research.md",
        "docs/specs/2026-07-21-oracle-code-spec-research-brief.md",
        "informed-operator/design/learnable-structure-requirements.md",
        "informed-operator/design/residual-loss-methodology.md",
    ],
    "husk": [
        "physics/research/applicability-classifiers.md",
    ],
}

# Stays at the repo root; not pages.
#   README.md         — repo entry point, rewritten to point into the book
#   docs/meta/glossary.md — folded into the generated root apparatus
ROOT_KEEP = ["README.md", "docs/meta/glossary.md"]

# Explicit ids where the filename would mint a poor slug.
ID_OVERRIDES = {
    "docs/presentation/2026-07-16-justification-report.md": "rationale",
    "physics/library/cert/reference-data/README.md":        "reference-battery",
    "docs/meta/AUDIT_PROMPT.md":                            "audit-prompt",
    "physics/research/group-A-ion-dynamics.md":             "deriv-ion-dynamics",
    "physics/research/group-B-electronic-magnetic-optical.md": "deriv-electronic",
    "physics/research/group-C-transport-thermo-chemical.md":   "deriv-transport",
    "physics/research/defects-surfaces-interfaces.md":      "deriv-defects",
    "physics/research/non-equilibrium-high-field.md":       "deriv-high-field",
    "physics/research/csp-heterostructure.md":              "deriv-csp",
    "physics/research/uwbg-observable-catalog.md":          "deriv-observable-catalog",
    "physics/research/residual-generator-catalog.md":       "deriv-generator-catalog",
    "physics/research/implementation-language.md":          "deriv-language-study",
}

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def split_frontmatter(text: str) -> tuple[str | None, str]:
    m = FM_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def get_field(fm: str | None, name: str) -> str | None:
    if not fm:
        return None
    m = re.search(rf"^{re.escape(name)}:\s*(.+)$", fm, re.MULTILINE)
    return m.group(1).strip() if m else None


def get_list_field(fm: str | None, name: str) -> list[str]:
    if not fm:
        return []
    m = re.search(rf"^{re.escape(name)}:\s*(.*)$", fm, re.MULTILINE)
    if not m:
        return []
    if m.group(1).strip() == "[]":
        return []
    out, started = [], False
    for line in fm.splitlines():
        if re.match(rf"^{re.escape(name)}:", line):
            started = True
            continue
        if started:
            if line.startswith("  - "):
                out.append(line[4:].strip())
            elif line and not line[0].isspace():
                break
    return out


def mint_id(src: str, fm: str | None) -> str:
    if src in ID_OVERRIDES:
        return ID_OVERRIDES[src]
    existing = get_field(fm, "id")
    if existing:
        return existing
    stem = pathlib.Path(src).stem
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)   # dated artifacts
    stem = re.sub(r"^\d+[-.]", "", stem)              # ordinal prefixes
    slug = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
    if src.startswith("physics/research/"):
        return f"deriv-{slug}"
    return slug


def slug_of(page_id: str) -> str:
    return re.sub(r"^(arch|impl|mvp)-\d+-", "", page_id)


def plan() -> list[dict]:
    rows, counters = [], {}
    for chapter, src in MANIFEST:
        p = ROOT / src
        if not p.exists():
            rows.append({"src": src, "missing": True})
            continue
        text = p.read_text(encoding="utf-8")
        fm, body = split_frontmatter(text)
        page_id = mint_id(src, fm)
        counters[chapter] = counters.get(chapter, 0) + 1
        n = counters[chapter]
        tag = f"{chapter}.{n}"
        sub = "appendix/" if chapter == 11 else ""
        dest = f"pages/{sub}{tag}-{slug_of(page_id)}.md"
        rows.append({
            "src": src, "dest": dest, "chapter": chapter, "tag": tag,
            "id": page_id, "had_fm": fm is not None,
            "canonical_for": get_list_field(fm, "canonical-for"),
            "depends_on": get_list_field(fm, "depends-on"),
            "referenced_by": get_list_field(fm, "referenced-by"),
            "research_sources": get_list_field(fm, "research-sources"),
            "title": get_field(fm, "title"),
            "status": get_field(fm, "status") or "draft",
            # chapter 11 is the derivation appendix: supporting material, and it
            # ranks below canon in the authority order (see 10.1-conventions).
            "authority": "supporting" if chapter == 11 else "canon",
            "sha": hashlib.sha256(body.encode()).hexdigest()[:12],
            "lines": text.count("\n") + 1, "missing": False,
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = plan()
    missing = [r for r in rows if r.get("missing")]

    print(f"{'TAG':>6}  {'ID':<28} {'LINES':>6}  DEST")
    print("-" * 100)
    cur = None
    for r in rows:
        if r.get("missing"):
            continue
        if r["chapter"] != cur:
            cur = r["chapter"]
            print(f"\n  == chapter {cur}: {CHAPTERS[cur]} ==")
        flag = "" if r["had_fm"] else "  [no frontmatter -> minted]"
        print(f"{r['tag']:>6}  {r['id']:<28} {r['lines']:>6}  {r['dest']}{flag}")

    print("\n" + "=" * 100)
    print(f"pages planned      : {len([r for r in rows if not r.get('missing')])}")
    print(f"missing sources    : {len(missing)}")
    for r in missing:
        print(f"    MISSING {r['src']}")

    for kind, files in DISPOSITIONS.items():
        present = [f for f in files if (ROOT / f).exists()]
        print(f"{kind:<18} : {len(present)}/{len(files)} present")

    # coverage check: every tracked .md accounted for
    accounted = {r["src"] for r in rows if not r.get("missing")}
    for files in DISPOSITIONS.values():
        accounted.update(files)
    accounted.update(ROOT_KEEP)
    stray = []
    for p in ROOT.rglob("*.md"):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith((".claude/", "tools/", "pages/")):
            continue
        if rel in accounted:
            continue
        stray.append(rel)
    print(f"\nunaccounted .md    : {len(stray)}")
    for s in sorted(stray):
        print(f"    ? {s}")

    if args.dry_run:
        print("\n(dry run — nothing written)")
        return 0

    execute(rows)
    return 0


def build_frontmatter(r: dict, fm: str | None, body: str) -> str:
    """Emit page frontmatter. `id` is preserved verbatim — it is the address."""
    title = r["title"]
    if not title:
        m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        title = m.group(1).strip() if m else r["id"]

    def block(name: str, items: list[str]) -> str:
        if not items:
            return f"{name}: []\n"
        return f"{name}:\n" + "".join(f"  - {i}\n" for i in items)

    canonical = r["canonical_for"]
    if not canonical:
        canonical = [r["id"]]          # minted pages own their own topic

    out = "---\n"
    out += f"id: {r['id']}\n"
    out += f"title: {title}\n"
    out += f"chapter: {r['chapter']}\n"
    out += f"chapter-name: {CHAPTERS[r['chapter']]}\n"
    out += f"tag: {r['tag']}\n"
    out += f"status: {r['status']}\n"
    out += f"authority: {r['authority']}\n"
    out += f"content-hash: {r['sha']}\n"
    out += block("canonical-for", canonical)
    out += block("depends-on", r["depends_on"])
    out += block("referenced-by", r["referenced_by"])
    out += block("research-sources", r["research_sources"])
    out += "---\n"
    return out


def execute(rows: list[dict]) -> None:
    moved = 0
    for r in rows:
        if r.get("missing"):
            continue
        src, dest = ROOT / r["src"], ROOT / r["dest"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        fm, body = split_frontmatter(src.read_text(encoding="utf-8"))
        dest.write_text(build_frontmatter(r, fm, body) + body.lstrip("\n"),
                        encoding="utf-8")
        src.unlink()
        moved += 1
    print(f"migrated {moved} pages")

    removed = 0
    for f in DISPOSITIONS["generated"]:
        p = ROOT / f
        if p.exists():
            p.unlink()
            removed += 1
    print(f"deleted {removed} generated artifacts")

    for f in DISPOSITIONS["husk"]:
        p = ROOT / f
        if p.exists():
            p.unlink()
            print(f"deleted husk {f}")

    # prune directories emptied by the migration
    for d in ("docs/architecture", "docs/implementation", "docs/mvp",
              "docs/_bundles", "docs/presentation"):
        p = ROOT / d
        if p.is_dir() and not any(p.rglob("*.md")):
            shutil.rmtree(p)
            print(f"pruned empty {d}/")


if __name__ == "__main__":
    sys.exit(main())

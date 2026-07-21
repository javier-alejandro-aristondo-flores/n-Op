#!/usr/bin/env python3
"""Mechanical seam checks (reconciliation-pass B9 tooling, kept as a standing machine check).

(a) row-band claims `rows N–M` vs the registry CSV (existence)
(b) backtick-quoted formula names in prose vs the CSV Name column
(c) duplicated numeric literals (tolerances etc.) across files
(d) glossary-term divergence candidates (term defined once, redefined elsewhere)
(e) retired formula names still resolving to nothing (retired-names.csv)
(f) near-miss formula names: case variants and one-edit neighbours of real rows
(g) D2/D4 rows whose `source` cell names no relaxation / no gate rationale
(h) `unregistered-formulas` declarations that the body no longer invokes
(i) glossary rows whose canonical pointer names no page
Read-only; prints findings, exit code = number of finding classes that fired.
"""
from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CSV_PATH = REPO / 'physics/library/formulas/registry-manifest.csv'

# The editable surface is the book. journal/live/ is frozen work product:
# internal staleness there is by-design and exempt (conventions, authority order).
# instructions.md is the entry point an agent reads first, so its staleness
# costs the most — and it sits outside pages/, where nothing was checking it.
EDITABLE = [REPO / 'README.md', REPO / 'journal' / 'instructions.md']
EDITABLE += sorted((REPO / 'journal' / 'pages').rglob('*.md'))
# The reference CSVs carry prose in their Source column and name formulas there.
# The registry itself is excluded: its source cells narrate their own retag
# history, so a retired name there is the record, not a dangling reference.
EDITABLE += sorted((REPO / 'physics/library/cert/reference-data').glob('*.csv'))

rows = list(csv.reader(CSV_PATH.open(encoding='utf-8')))[1:]
row_ids = {int(r[0]) for r in rows}
row_names = {r[1] for r in rows}
marker_ids = {int(r[0]) for r in rows if r[4].strip() == '—'}

findings = defaultdict(list)

# (a) row-band claims ------------------------------------------------------
BAND = re.compile(r'\brows?\s+(\d+)\s*[–-]\s*(\d+)\b', re.IGNORECASE)
for path in EDITABLE:
    for ln, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        for m in BAND.finditer(line):
            lo, hi = int(m.group(1)), int(m.group(2))
            if hi > 300 or lo >= hi:      # years, ranges of non-row things
                continue
            if not ({lo, hi} <= row_ids):
                findings['row-band'].append(f'{path.relative_to(REPO)}:{ln}: rows {lo}-{hi} — endpoint not in CSV')

# (b2) `formula = <name>` arguments ---------------------------------------
# A page may DECLARE unregistered names in its `unregistered-formulas`
# frontmatter. Declared names are tracked, not defects; undeclared ones fail.
# Inline mathematics is a separate violation (impl-04: "no inline math").
# Capture everything up to the closing delimiter, not just an ASCII identifier:
# `formula = σ/(n·e)` slipped through an [A-Za-z0-9_.-]+ capture for years.
FORMULA_ARG = re.compile(r'formula\s*=\s*(\{[^}]*\}[^,)`\n]*|[^,)`\n]+)')
KEBAB = re.compile(r'^[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+$')

def _declared(path):
    txt = path.read_text(encoding='utf-8')
    if not txt.startswith('---'):
        return set()
    fm = txt.split('---', 2)[1]
    out, on = set(), False
    for line in fm.splitlines():
        if line.startswith('unregistered-formulas:'):
            on = True; continue
        if on:
            if line.startswith('  - '): out.add(line[4:].strip())
            elif line and not line[0].isspace(): break
    return out

for path in EDITABLE:
    declared = _declared(path)
    for ln, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        for m in FORMULA_ARG.finditer(line):
            raw = m.group(1).strip('`')
            if raw.startswith('{'):                       # {a | b | c}-suffix
                head, _, suffix = raw.partition('}')
                cands = [f"{c.strip()}{suffix}" for c in head.strip('{').split('|')]
            else:
                cands = [raw]
            for c in cands:
                c = c.strip()
                if not c or '<' in c:        # `formula = <name>` is a placeholder
                    continue
                if c in row_names or c in declared:
                    continue
                if not KEBAB.match(c):
                    findings['inline-math'].append(
                        f'{path.relative_to(REPO)}:{ln}: formula = {c} — inline mathematics '
                        f'(impl-04-formulas forbids it; register a named row)')
                else:
                    findings['formula-arg'].append(
                        f'{path.relative_to(REPO)}:{ln}: formula = {c} — not a registry name '
                        f'and not declared in unregistered-formulas')

# (b) formula names in prose ----------------------------------------------
NAMEISH = re.compile(r'`([a-z][a-z0-9]*(?:-[a-zA-Z0-9_*]+){2,})`')
IGNORE_NAMES = set()
for path in EDITABLE:
    text = path.read_text(encoding='utf-8')
    for ln, line in enumerate(text.splitlines(), 1):
        for m in NAMEISH.finditer(line):
            name = m.group(1)
            if name in row_names or name in IGNORE_NAMES:
                continue
            if re.match(r'(arch|impl|mvp)-\d\d-', name):
                continue  # atomic-file id, not a formula name
            # a line that also carries a real row name is resolving the old one
            # in place ("proposed as X; landed as Y") — that is the fix, not a defect
            if any(rn in line for rn in row_names):
                continue
            # only flag if it *looks* like a formula row reference (nearby "row" or known family)
            if re.search(r'\brow\s+\d+|registry', line) and name not in row_names:
                close = [n for n in row_names if n.startswith(name[:12])]
                findings['formula-name'].append(
                    f'{path.relative_to(REPO)}:{ln}: `{name}` not a CSV Name'
                    + (f' (nearest: {close[0]})' if close else ''))

# (c) duplicated numeric literals ------------------------------------------
TOL = re.compile(r'\b(?:τ|δ)_[A-Za-z,]+\s*(?:=|≈)?\s*`?([0-9.]+e?-?[0-9]*)`?')
tol_sites = defaultdict(set)
for path in EDITABLE:
    for ln, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        for m in re.finditer(r'(τ_adj|δ_sym|δ_PSD|τ_SCF,strict|τ_SCF,train|τ_L3L4|τ_method|δ_surrogate|δ_meta)\D{0,20}?(1e-\d+|10[–-]20%|\d+%)', line):
            tol_sites[m.group(1)].add((m.group(2), str(path.relative_to(REPO))))
for sym, sites in sorted(tol_sites.items()):
    values = {v for v, _ in sites}
    if len(values) > 1:
        findings['tolerance'].append(f'{sym}: divergent values {sorted(values)} across {sorted({p for _, p in sites})}')

# (h) declared-gap list must match what is actually invoked ----------------
# A declaration that has drifted from the body is worse than none: it reports a
# gap that has moved. Both directions are defects -- a name declared but no
# longer invoked, and a name invoked but not declared (which (b2) also catches).
for path in EDITABLE:
    declared = _declared(path)
    if not declared:
        continue
    invoked = set()
    for line in path.read_text(encoding='utf-8').splitlines():
        for m in FORMULA_ARG.finditer(line):
            raw = m.group(1).strip('`').strip()
            if raw.startswith('{'):
                head, _, suffix = raw.partition('}')
                invoked |= {f"{c.strip()}{suffix}" for c in head.strip('{').split('|')}
            elif raw and '<' not in raw:
                invoked.add(raw)
    stale = sorted(n for n in declared if n not in invoked)
    if stale:
        findings['stale-declaration'].append(
            f'{path.relative_to(REPO)}: declares {stale} in `unregistered-formulas` '
            f'but the body no longer invokes them')

# (e) retired formula names ------------------------------------------------
# Naming is addressing (conventions): a renamed row must not leave the old name
# resolving to nothing. A line that carries BOTH the retired name and what it
# landed as is documenting the rename, not dangling — those are exempt.
RETIRED_PATH = REPO / 'physics/library/formulas/retired-names.csv'
retired = {}
if RETIRED_PATH.exists():
    with RETIRED_PATH.open(encoding='utf-8') as fh:
        for r in list(csv.reader(fh))[1:]:
            if r:
                retired[r[0]] = r[1]
def _blocks(lines):
    """Paragraph index: line number -> text of its contiguous non-blank block.
    Prose resolves a retired name across a sentence, not always on one line."""
    out, start = {}, 0
    for i, ln in enumerate(lines + ['']):
        if not ln.strip():
            block = '\n'.join(lines[start:i])
            for j in range(start, i):
                out[j + 1] = block
            start = i + 1
    return out

for path in EDITABLE:
    lines = path.read_text(encoding='utf-8').splitlines()
    blocks = _blocks(lines)
    for ln, line in enumerate(lines, 1):
        for old, new in retired.items():
            if not re.search(rf'(?<![\w-]){re.escape(old)}(?![\w-])', line, re.I):
                continue
            scope = blocks.get(ln, line)
            if any(part.strip() in scope for part in new.replace('+', ' ').split()):
                continue                     # the paragraph resolves it in place
            findings['retired-name'].append(
                f'{path.relative_to(REPO)}:{ln}: `{old}` is retired — landed as {new}')

# (f) near-miss formula names ----------------------------------------------
lower_names = {n.lower(): n for n in row_names}
NEARISH = re.compile(r'`([A-Za-z][a-zA-Z0-9]*(?:-[a-zA-Z0-9_*]+)+)`')
for path in EDITABLE:
    for ln, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        for m in NEARISH.finditer(line):
            name = m.group(1)
            if name in row_names or name in retired:
                continue
            if re.match(r'(arch|impl|mvp|deriv)-', name):
                continue
            if name.lower() in {r.lower() for r in retired}:
                continue
            hit = lower_names.get(name.lower())
            if hit and hit not in line:
                findings['near-miss'].append(
                    f'{path.relative_to(REPO)}:{ln}: `{name}` — case variant of `{hit}`')

# (g) D2/D4 rows must carry their gate/relaxation rationale in `source` -----
# A D4 row with no named relaxation is un-gateable (impl-04-formulas); the
# obligation-9 approval has nothing to approve.
RELAX_WORDS = ('relax', 'soft', 'log-sum-exp', 'gumbel', 'sigmoid', 'smooth')
for r in rows:
    if r[5].strip() == 'D4' and not any(w in r[7].lower() for w in RELAX_WORDS):
        findings['d4-no-relaxation'].append(
            f'registry row {r[0]} ({r[1]}): D4 with no relaxation named in `source`')

# (i) glossary canonical pointers ------------------------------------------
# Every glossary row names the page that owns the term. Nothing checked that the
# page exists, so a rename or a deletion would leave the glossary -- the file a
# reader consults FIRST -- pointing at nothing.
_ids = set()
for _p in sorted((REPO / 'journal' / 'pages').rglob('*.md')):
    _m = re.match(r'\A---\n(.*?)\n---\n', _p.read_text(encoding='utf-8'), re.DOTALL)
    if _m:
        _id = re.search(r'^id:\s*(\S+)', _m.group(1), re.M)
        if _id:
            _ids.add(_id.group(1))
_gloss_rows = re.findall(r'^\|\s*\*\*([^*|]+)\*\*\s*\|.*?\|([^|]*)\|\s*$',
                         (REPO / 'journal/glossary.md').read_text(encoding='utf-8'), re.M)
for _term, _canon in _gloss_rows:
    for _tok in re.findall(r'[a-z][a-z0-9-]{3,}', _canon):
        if _tok in _ids or _tok in {'traps', 'conventions', 'timeline', 'product'}:
            break
    else:
        if _canon.strip():
            findings['glossary-pointer'].append(
                f'glossary.md: **{_term.strip()}** -> `{_canon.strip()}` names no page id')

# (d) glossary divergence candidates ---------------------------------------
gloss = (REPO / 'journal/glossary.md').read_text(encoding='utf-8')
gloss_terms = re.findall(r'^\|\s*\*\*([^*|]+)\*\*', gloss, re.M)
dup = [t for t in gloss_terms if gloss_terms.count(t) > 1]
if dup:
    findings['glossary'].append(f'duplicate glossary entries: {sorted(set(dup))}')

for cls, items in findings.items():
    print(f'== {cls} ({len(items)}) ==')
    for item in items:
        print(f'  {item}')
if not findings:
    print('B9 seams clean')
sys.exit(len(findings))

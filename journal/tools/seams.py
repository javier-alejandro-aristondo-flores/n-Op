#!/usr/bin/env python3
"""Mechanical seam checks (reconciliation-pass B9 tooling, kept as a standing machine check).

(a) row-band claims `rows N–M` vs the registry CSV (existence)
(b) backtick-quoted formula names in prose vs the CSV Name column
(c) duplicated numeric literals (tolerances etc.) across files
(d) glossary-term divergence candidates (term defined once, redefined elsewhere)
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
EDITABLE = [REPO / 'README.md']
EDITABLE += sorted((REPO / 'journal' / 'pages').rglob('*.md'))

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
FORMULA_ARG = re.compile(r'formula\s*=\s*([A-Za-z0-9_.{|}-]+)')
for path in EDITABLE:
    for ln, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        for m in FORMULA_ARG.finditer(line):
            arg = m.group(1).strip('`')
            if arg.startswith('{'):          # {a | b | c} alternation
                cands = [c.strip() for c in arg.strip('{}').split('|')]
            else:
                cands = [arg]
            for c in cands:
                if c and c not in row_names:
                    findings['formula-arg'].append(
                        f'{path.relative_to(REPO)}:{ln}: formula = {c} — not a registry name')

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

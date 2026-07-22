#!/usr/bin/env python3
"""Does the book agree with the data files it describes?

`check_book_structure.py` checks the book's own structure. This checks the seams between
the book and everything it points at: the registry CSV, the reference-data
CSVs, the glossary, and the design docs that consume the same vocabulary.

(Formerly announced itself as "reconciliation-pass B9 tooling" and printed
"B9 seams clean". That B9 was a step label from a pass that finished months
ago; the corpus's real `B9` is the non-equilibrium-operating observable
bundle, which this tool has nothing to do with. Retired 2026-07-22.)

(a) row-band claims `rows N–M` vs the registry CSV (existence)
(b) backtick-quoted formula names in prose vs the CSV Name column
(c) duplicated numeric literals (tolerances etc.) across files
(d) glossary-term divergence candidates (term defined once, redefined elsewhere)
(e) retired formula names still resolving to nothing (retired-names.csv)
(f) near-miss formula names: case variants and one-edit neighbours of real rows
(g) D4 rows whose `source` cell names no relaxation
(h) `unregistered-formulas` declarations that the body no longer invokes
(i) glossary rows whose canonical pointer names no page
(j) registry `name (row N)` pointers that name the wrong row
(k) reference-data rows with no uncertainty or no source
(l) reference-data rows whose field count disagrees with the header
(m) reference-data dates that are non-ISO, in the future, or modified-before-added
Read-only; prints findings, exit code = number of finding classes that fired.
"""
from __future__ import annotations

import csv
import csv as _csv
import datetime as _dt
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_root  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
CSV_PATH = REPO / 'physics/library/formulas/registry-manifest.csv'

corpus_root.refuse_if_scratch_copy(REPO, allowed='--worktree' in sys.argv)

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
# The /informed-operator design docs consume this vocabulary and cite page ids.
# Nothing was sweeping them, and the note in residual-loss-methodology.md warning
# about a stale D-tag legend had itself gone stale.
EDITABLE += sorted((REPO / 'informed-operator/design').glob('*.md'))

rows = list(csv.reader(CSV_PATH.open(encoding='utf-8')))[1:]
row_ids = {int(r[0]) for r in rows}
row_names = {r[1] for r in rows}

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
# Inline mathematics is a separate violation (named-formulas: "no inline math").
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
                        f'(named-formulas forbids it; register a named row)')
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
# The symbol list is HARVESTED from the page that owns it, not restated here.
# It used to be nine symbols hard-coded in this file against seventeen in
# `cert-obligations §1.2` -- a check reporting clean on 53% coverage, with the
# shortfall recorded honestly in a comment and acted on by nothing. Reading the
# owner's table is the same technique `check_the_checkers.py` already uses to
# derive its coverage, applied one level over.
_CERT = REPO / 'journal/pages/05-certification-and-applicability/5.1-cert-obligations.md'
_ledger = re.search(r'^## [\d.]+ Tolerance ledger$(.*?)^## ',
                    _CERT.read_text(encoding='utf-8'), re.S | re.M)
TOL_SYMBOLS = sorted(re.findall(r'^\|\s*`([τδ]_[^`]+)`\s*\|', _ledger.group(1), re.M),
                     key=len, reverse=True) if _ledger else []
if not TOL_SYMBOLS:
    findings['tolerance'].append(
        'cert-obligations: the tolerance ledger table could not be read — '
        'every tolerance symbol is going unchecked')

_TOL_VALUE = r'(1e-\d+|10[–-]20%|\d+%|\d+ meV/atom|\d+σ)'
tol_sites = defaultdict(set)
if TOL_SYMBOLS:
    _tol_re = re.compile('(' + '|'.join(re.escape(s) for s in TOL_SYMBOLS)
                         + r')\D{0,20}?' + _TOL_VALUE)
    for path in EDITABLE:
        for ln, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            for m in _tol_re.finditer(line):
                tol_sites[m.group(1)].add((m.group(2), str(path.relative_to(REPO))))
for sym, sites in sorted(tol_sites.items()):
    values = {v for v, _ in sites}
    if len(values) > 1:
        findings['tolerance'].append(f'{sym}: divergent values {sorted(values)} across {sorted({p for _, p in sites})}')

# The ledger's exhaustiveness rule -- "a tolerance stated anywhere but absent
# from this table is a defect in this table" -- is NOT machine-checkable, and an
# attempt to make it one is recorded here so the next person does not repeat it.
#
# The obvious check is: flag every `τ_*` / `δ_*` not in the table. It fires 48
# times on correct prose. `τ` is not a reserved tolerance prefix in this corpus:
# `τ_n` and `τ_p` are SRH carrier lifetimes, `τ_PO` a polar-optical scattering
# time, `τ_E` an energy relaxation time, `τ_hop`, `τ_iv`, `τ_alloy` likewise.
# The ledger page's claim that "`δ`/`τ` denotes a *tolerance* throughout" is
# false of the appendices, and that overclaim is what made the check look sound.
#
# Narrowing it by requiring a tolerance-shaped value does not rescue it either:
# a relaxation time of `1e-12` s is shaped exactly like a tolerance of `1e-12`.
# Separating the two needs a namespace the corpus does not have (`tol_adj` vs
# `τ_adj`, say). Until then this stays a review rule, stated honestly as one.
# A check that cries wolf 48 times is worse than an absent check: it teaches
# the reader to skim past output, which is the failure the whole corpus is
# fighting.

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

# The identifier form is only half the surface. `Born-stability-cubic` is caught;
# "Born stability" -- which is how prose actually writes it -- was not, and
# neither were "Coffin–Manson fatigue" (en-dash, space) or "Pauling radius
# ratio". The rename discipline covered the machine spelling and missed the
# human one, and the human one is what sits in the bundle descriptions.
#
# Derived, not hand-authored: a `prose-form` column on 62 rows is 62 more things
# to keep in sync. Each retired name yields a separator-insensitive pattern
# (hyphen / en-dash / space), plus the same pattern minus its trailing
# qualifier, since prose says "Born stability" for `Born-stability-cubic`.
# Single-token stems are never generated -- "Born" alone would fire on
# Born–Oppenheimer, a different physicist and a live concept here.
SEP = r'[-–— ]'


def _prose_patterns(name: str) -> list[str]:
    parts = name.split('-')
    out = []
    for stem in (parts, parts[:-1]):
        if len(stem) >= 2 and stem[0][:1].isupper():
            out.append(SEP.join(re.escape(p) for p in stem))
    return out


prose_retired = {}
for _old in retired:
    for _pat in _prose_patterns(_old):
        prose_retired.setdefault(_pat, _old)

# One pass per line, with the word-boundary lookarounds hoisted OUT of the
# alternation. This is the whole performance story of this tool: 62 retired
# names each wrapped in its own `(?<![\w-])...(?![\w-])` costs 2.5 s per run,
# and calibration runs the tool once per probe, which turned a two-second check
# into a two-minute one and tripped a timeout. The same 62 names under a single
# shared lookbehind cost 0.14 s -- 18x, for identical hits. Longest-first so
# `Born-stability-cubic` wins over any prefix of itself.
def _one_pass(names):
    if not names:
        return None
    alts = '|'.join(re.escape(n) for n in sorted(names, key=len, reverse=True))
    return re.compile(rf'(?<![\w-])({alts})(?![\w-])', re.I)


_RETIRED_RE = _one_pass(retired)
_RETIRED_BY_LOWER = {o.lower(): o for o in retired}

# The prose forms are patterns, not literals (they carry a separator class), so
# they are joined directly rather than escaped.
_PROSE_RE = re.compile(
    r'(?<![\w-])(' + '|'.join(sorted(prose_retired, key=len, reverse=True))
    + r')(?![\w-])') if prose_retired else None
_PROSE_LOOKUP = {}
for _pat, _old in prose_retired.items():
    _PROSE_LOOKUP[re.compile(rf'\A{_pat}\Z')] = _old

for path in EDITABLE:
    lines = path.read_text(encoding='utf-8').splitlines()
    blocks = _blocks(lines)
    for ln, line in enumerate(lines, 1):
        hit_ident = set()
        for m in (_RETIRED_RE.finditer(line) if _RETIRED_RE else ()):
            old = _RETIRED_BY_LOWER[m.group(1).lower()]
            hit_ident.add(old)
            new = retired[old]
            scope = blocks.get(ln, line)
            if any(part.strip() in scope for part in new.replace('+', ' ').split()):
                continue                     # the paragraph resolves it in place
            findings['retired-name'].append(
                f'{path.relative_to(REPO)}:{ln}: `{old}` is retired — landed as {new}')
        for m in (_PROSE_RE.finditer(line) if _PROSE_RE else ()):
            old = next((o for rx, o in _PROSE_LOOKUP.items()
                        if rx.match(m.group(1))), None)
            if old is None or old in hit_ident:
                continue                     # the identifier check owns that one
            new = retired[old]
            scope = blocks.get(ln, line)
            if any(part.strip() in scope for part in new.replace('+', ' ').split()):
                continue                     # the paragraph resolves it in place
            findings['retired-eponym'].append(
                f'{path.relative_to(REPO)}:{ln}: "{m.group(0)}" is the prose form '
                f'of retired `{old}` — landed as {new}')

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

# (j) registry `name (row N)` pointers ------------------------------------
# The Depends-on column is the machine-readable edge list a code generator would
# build the DAG from. A pointer naming the wrong row builds the wrong DAG, and a
# rename leaves it naming nothing.
row_by_num = {r[0]: r[1] for r in rows}
for r in rows:
    for nm, num in re.findall(r'([A-Za-z0-9][\w\-*]*)\s*\(row (\d+)', r[8] or ''):
        if row_by_num.get(num) != nm:
            findings['row-pointer'].append(
                f'registry row {r[0]} ({r[1]}): depends-on says `{nm} (row {num})` '
                f'but row {num} is `{row_by_num.get(num, "MISSING")}`')

# (k) reference-data rows must carry a sigma and a source ------------------
# coupling-structure §8: an unprovenanced coefficient refuses the composition, and a
# sigma-column hole makes that refusal un-checkable. The rule was asserted in
# canon and verified once by hand during a 2026-07 audit; nothing kept it true.
for _p in sorted((REPO / 'physics/library/cert/reference-data').glob('*.csv')):
    for _r in _csv.DictReader(_p.open(encoding='utf-8')):
        _v = (_r.get('Value') or '').strip()
        _label = f"{_r.get('Property')}/{_r.get('Material')}"
        if 'GAP' not in _v.upper() and not (_r.get('Uncertainty') or '').strip():
            findings['missing-uncertainty'].append(
                f'{_p.name}: {_label} has no uncertainty (coupling-structure §8)')
        if not (_r.get('Source') or '').strip():
            findings['missing-source'].append(
                f'{_p.name}: {_label} has no source (unprovenanced coefficient)')

# (l) reference-data row arity, and (m) date sanity ------------------------
# A Source cell carrying an unquoted comma splits into extra fields and shifts
# every column right of it. `transport-coefficients.csv` shipped one such row for
# a month: its `Source class` held a prose fragment, `Added` held "experimental"
# and `Modified` held "1". Check (k) passed it, because the cells it reads by
# NAME were still non-empty -- they just held the wrong values. Arity is what
# catches a shift; presence is not.
_TODAY = _dt.date.today()
for _p in sorted((REPO / 'physics/library/cert/reference-data').glob('*.csv')):
    _raw = list(_csv.reader(_p.open(encoding='utf-8')))
    _width = len(_raw[0])
    for _n, _row in enumerate(_raw[1:], 2):
        if _row and len(_row) != _width:
            findings['wrong-field-count'].append(
                f'{_p.name}:{_n}: {len(_row)} fields, header has {_width} — a cell '
                f'with an unquoted comma shifts every column after it')
    for _r in _csv.DictReader(_p.open(encoding='utf-8')):
        _label = f"{_r.get('Property')}/{_r.get('Material')}"
        _seen = {}
        for _f in ('Added', 'Modified'):
            _v = (_r.get(_f) or '').strip()
            if not _v:
                continue
            try:
                _seen[_f] = _dt.date.fromisoformat(_v)
            except ValueError:
                findings['bad-date'].append(
                    f'{_p.name}: {_label} has {_f}={_v!r}, not an ISO date')
                continue
            if _seen[_f] > _TODAY:
                findings['bad-date'].append(
                    f'{_p.name}: {_label} has {_f}={_v}, which is in the future')
        if len(_seen) == 2 and _seen['Modified'] < _seen['Added']:
            findings['bad-date'].append(
                f"{_p.name}: {_label} was Modified {_seen['Modified']} before it "
                f"was Added {_seen['Added']}")

# (n) every coded registry column must stay inside its vocabulary -----------
# `Diff` got a checker after a Diff incident and `Tier` after a Tier incident.
# `Bundle` and `Path` appeared in neither tool.
#
# The vocabularies are HARVESTED, never restated here -- a second copy is the
# thing this tool exists to catch. For `Bundle` that means TWO sources, and
# reading only one produced a false positive with teeth: the eleven `B*` codes
# come from the table in `canonical-vocabularies`, but `named-formulas` owns
# the *schema* and admits one more value --
#
#     bundle : {BundleId}   -- one or more of B1..B11, or the L1 primitive tag
#
# `L1` on rows 91-94 is deliberate: Z*, ε∞, χ∞ and α_M are level-1 primitives
# feeding several bundles at once, and both canon pages say so. A first version
# of this check harvested only the table, reported those four rows as a defect,
# and the "fix" retagged four correct rows to `B1` before either page was read
# (`[traps]` §70). Harvest from the field's schema, not from an enumeration
# that happens to sit nearby.
_VOCAB_PAGE = REPO / 'journal/pages/06-vocabularies-and-registry/6.1-canonical-vocabularies.md'
_SCHEMA_PAGE = REPO / 'journal/pages/06-vocabularies-and-registry/6.6-named-formulas.md'
_BUNDLES = set(re.findall(r'^\|\s*(B\d+)\s*\|', _VOCAB_PAGE.read_text(encoding='utf-8'), re.M))
# ...plus any extra tag the schema documents for this field.
# The phrase wraps inside a code fence, so it is matched wherever it lands
# rather than anchored to the words that precede it on one line.
_BUNDLES |= set(re.findall(r'`?(\w+)`?\s+primitive tag',
                           _SCHEMA_PAGE.read_text(encoding='utf-8')))
COLUMN_VOCAB = {
    3: ('Bundle', _BUNDLES),
    4: ('Tier', {'T0', 'T1', 'T2', 'T3'}),
    5: ('Diff', {'D0', 'D1', 'D2', 'D3', 'D4', 'DN'}),
    6: ('Path', {'cheap', 'faithful'}),
}
if not _BUNDLES:
    findings['vocabulary'].append(
        'canonical-vocabularies: no `| Bn |` bundle table found — the Bundle '
        'vocabulary could not be harvested, so Bundle went unchecked')
for r in rows:
    for _i, (_name, _allowed) in COLUMN_VOCAB.items():
        _cell = r[_i].strip()
        if _cell in ('—', ''):
            continue                       # architectural markers carry no tags
        # a cell may name several, `B6/B7`; every part must be in vocabulary
        _bad = [p for p in _cell.split('/') if p.strip() not in _allowed]
        if _bad:
            findings['vocabulary'].append(
                f'registry row {r[0]} ({r[1]}): {_name}={_cell!r} — '
                f'{", ".join(repr(b) for b in _bad)} not in '
                f'{{{", ".join(sorted(_allowed))}}}')

# (g) D2/D4 rows must carry their gate/relaxation rationale in `source` -----
# A D4 row with no named relaxation is un-gateable (named-formulas); the
# obligation-9 approval has nothing to approve.
RELAX_WORDS = ('relax', 'soft', 'log-sum-exp', 'gumbel', 'sigmoid', 'smooth')
for r in rows:
    if r[5].strip() == 'D4' and not any(w in r[7].lower() for w in RELAX_WORDS):
        findings['ungateable-d4-row'].append(
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

_where = corpus_root.describe(REPO)
for cls, items in findings.items():
    print(f'== {cls} ({len(items)}) ==')
    for item in items:
        print(f'  {item}')
if findings:
    print(f'data agreement FAILED @ {_where} — '
          f'{len(findings)} finding class(es)')
else:
    print(f'data agreement clean @ {_where}')
sys.exit(len(findings))

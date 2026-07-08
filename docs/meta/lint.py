'''Lint the atomic doc tree against the conventions in conventions.md.

Checks performed (each failure prints to stderr and contributes to the
non-zero exit code):

  1. Frontmatter present, parseable, and contains the mandatory fields.
  2. `id` matches `<tree>-<filename-stem>` for the file's directory.
  3. `canonical-for` topics are globally unique across the tree.
  4. `depends-on` / `referenced-by` are symmetric.
  5. Every `[<tree>-NN-slug]` reference in prose resolves to a file id.
  6. Every `research-sources` path exists relative to the repo root.
  7. Every atomic file appears in exactly one monolith in manifest.yaml.
  8. Vocabulary counts quoted anywhere in README / AUDIT_PROMPT / docs match
     the arch-09 canon and the registry CSV (formulas, categories, methods,
     templates, bundles, obligations, and the overview's tier/diff tallies).
     A line may opt out with the literal marker `lint:ignore-counts`.

The lint is read-only and pure; it never modifies the tree.
'''

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import yaml


DOCS_ROOT: Path = Path(__file__).resolve().parents[1]
REPO_ROOT: Path = DOCS_ROOT.parent
MANIFEST_PATH: Path = DOCS_ROOT / 'meta' / 'manifest.yaml'

TREE_DIRS: tuple[tuple[str, str], ...] = (
    ('arch', 'architecture'),
    ('impl', 'implementation'),
    ('mvp', 'mvp'),
)

REQUIRED_FIELDS: tuple[str, ...] = (
    'id',
    'title',
    'status',
    'revision',
    'canonical-for',
    'depends-on',
    'referenced-by',
    'research-sources',
)

VALID_STATUSES: frozenset[str] = frozenset({'draft', 'review', 'stable'})

ID_REFERENCE_PATTERN: re.Pattern[str] = re.compile(r'\b(arch|impl|mvp)-\d{2}-[a-z0-9-]+\b')


@dataclass(frozen=True, slots=True)
class FileRecord:
    path: Path
    tree_prefix: str
    frontmatter: dict[str, object]
    body: str


def Discover_Files() -> tuple[FileRecord, ...]:
    discovered_records: list[FileRecord] = []
    for tree_prefix, tree_dir in TREE_DIRS:
        directory_path: Path = DOCS_ROOT / tree_dir
        for source_path in sorted(directory_path.glob('*.md')):
            with source_path.open(encoding='utf-8') as source_handle:
                file_text: str = source_handle.read()
            frontmatter, body_text = _Strip_Frontmatter(file_text)
            discovered_records.append(
                FileRecord(
                    path=source_path,
                    tree_prefix=tree_prefix,
                    frontmatter=frontmatter,
                    body=body_text,
                )
            )
    return tuple(discovered_records)


def _Strip_Frontmatter(file_text: str) -> tuple[dict[str, object], str]:
    if not file_text.startswith('---\n'):
        return {}, file_text
    closing_index: int = file_text.find('\n---\n', 4)
    if closing_index == -1:
        return {}, file_text
    frontmatter_text: str = file_text[4:closing_index]
    body_text: str = file_text[closing_index + len('\n---\n'):]
    parsed_frontmatter: object = yaml.safe_load(frontmatter_text)
    if not isinstance(parsed_frontmatter, dict):
        return {}, body_text
    return parsed_frontmatter, body_text


def Check_Frontmatter_Shape(records: tuple[FileRecord, ...]) -> list[str]:
    failures: list[str] = []
    for record in records:
        if not record.frontmatter:
            failures.append(f'{record.path}: missing frontmatter')
            continue
        for required_field in REQUIRED_FIELDS:
            if required_field not in record.frontmatter:
                failures.append(f'{record.path}: missing field `{required_field}`')
        status_value: object = record.frontmatter.get('status')
        if isinstance(status_value, str) and status_value not in VALID_STATUSES:
            failures.append(f'{record.path}: invalid status {status_value!r}')
        revision_value: object = record.frontmatter.get('revision')
        if not isinstance(revision_value, int):
            failures.append(f'{record.path}: revision must be an integer')
    return failures


def Check_Id_Matches_Filename(records: tuple[FileRecord, ...]) -> list[str]:
    failures: list[str] = []
    for record in records:
        expected_id: str = f'{record.tree_prefix}-{record.path.stem}'
        actual_id: object = record.frontmatter.get('id')
        if actual_id != expected_id:
            failures.append(
                f'{record.path}: id {actual_id!r} does not match expected {expected_id!r}'
            )
    return failures


def Check_Canonical_For_Unique(records: tuple[FileRecord, ...]) -> list[str]:
    topic_owners: dict[str, list[str]] = defaultdict(list)
    for record in records:
        canonical_topics: object = record.frontmatter.get('canonical-for', [])
        if not isinstance(canonical_topics, list):
            continue
        owner_id: str = str(record.frontmatter.get('id', record.path.stem))
        for topic_value in canonical_topics:
            topic_owners[str(topic_value)].append(owner_id)
    failures: list[str] = []
    for topic_value, owner_list in topic_owners.items():
        if len(owner_list) > 1:
            owners_joined: str = ', '.join(owner_list)
            failures.append(f'topic {topic_value!r} claimed canonical by multiple files: {owners_joined}')
    return failures


def Check_Depends_Referenced_By_Symmetric(records: tuple[FileRecord, ...]) -> list[str]:
    by_id: dict[str, FileRecord] = {
        str(record.frontmatter.get('id', record.path.stem)): record for record in records
    }
    failures: list[str] = []
    for record in records:
        owner_id: str = str(record.frontmatter.get('id', record.path.stem))
        depends_on: object = record.frontmatter.get('depends-on', [])
        if not isinstance(depends_on, list):
            continue
        for upstream_id in depends_on:
            upstream_record: FileRecord | None = by_id.get(str(upstream_id))
            if upstream_record is None:
                failures.append(f'{owner_id}: depends-on points at unknown id {upstream_id!r}')
                continue
            upstream_referenced_by: object = upstream_record.frontmatter.get('referenced-by', [])
            if not isinstance(upstream_referenced_by, list) or owner_id not in [
                str(value) for value in upstream_referenced_by
            ]:
                failures.append(
                    f'{owner_id}: depends-on {upstream_id!r}, '
                    f'but {upstream_id!r}.referenced-by is missing {owner_id!r}'
                )
    return failures


def Check_Inline_References_Resolve(records: tuple[FileRecord, ...]) -> list[str]:
    known_ids: set[str] = {
        str(record.frontmatter.get('id', record.path.stem)) for record in records
    }
    failures: list[str] = []
    for record in records:
        owner_id: str = str(record.frontmatter.get('id', record.path.stem))
        for matched_id in ID_REFERENCE_PATTERN.findall(record.body):
            if isinstance(matched_id, tuple):
                continue
        for full_match in ID_REFERENCE_PATTERN.finditer(record.body):
            referenced_id: str = full_match.group(0)
            if referenced_id == owner_id:
                continue
            if referenced_id not in known_ids:
                failures.append(f'{owner_id}: inline reference {referenced_id!r} does not resolve')
    return failures


def Check_Research_Sources_Exist(records: tuple[FileRecord, ...]) -> list[str]:
    failures: list[str] = []
    for record in records:
        research_paths: object = record.frontmatter.get('research-sources', [])
        if not isinstance(research_paths, list):
            continue
        owner_id: str = str(record.frontmatter.get('id', record.path.stem))
        for source_path_value in research_paths:
            absolute_source_path: Path = REPO_ROOT / str(source_path_value)
            if not absolute_source_path.exists():
                failures.append(
                    f'{owner_id}: research-sources path does not exist: {source_path_value!r}'
                )
    return failures


def Check_Manifest_Coverage(records: tuple[FileRecord, ...]) -> list[str]:
    with MANIFEST_PATH.open(encoding='utf-8') as manifest_handle:
        manifest_data: object = yaml.safe_load(manifest_handle)
    if not isinstance(manifest_data, dict):
        return ['manifest.yaml root must be a mapping']
    monoliths_section: object = manifest_data.get('monoliths', {})
    if not isinstance(monoliths_section, dict):
        return ['manifest.yaml `monoliths` must be a mapping']
    membership_count: dict[str, int] = defaultdict(int)
    for monolith_spec in monoliths_section.values():
        if not isinstance(monolith_spec, dict):
            continue
        sources_listed: object = monolith_spec.get('sources', [])
        if not isinstance(sources_listed, list):
            continue
        for source_relative in sources_listed:
            membership_count[str(source_relative)] += 1
    failures: list[str] = []
    record_relative_paths: set[str] = {
        str(record.path.relative_to(DOCS_ROOT)) for record in records
    }
    for record_relative in record_relative_paths:
        if membership_count.get(record_relative, 0) == 0:
            failures.append(f'manifest: file not covered by any monolith: {record_relative}')
        elif membership_count.get(record_relative, 0) > 1:
            failures.append(f'manifest: file covered by multiple monoliths: {record_relative}')
    for listed_relative in membership_count:
        if listed_relative not in record_relative_paths:
            failures.append(f'manifest: monolith references missing file: {listed_relative}')
    return failures


REGISTRY_CSV_PATH: Path = REPO_ROOT / 'physics' / 'library' / 'formulas' / 'registry-manifest.csv'
VOCAB_CANON_PATH: Path = DOCS_ROOT / 'architecture' / '09-vocabularies.md'
OVERVIEW_PATH: Path = DOCS_ROOT / 'computational-overview.md'
COUNT_SCAN_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {'audits', '_archive', 'superpowers', 'presentation', '_bundles'}
)
COUNT_IGNORE_MARKER: str = 'lint:ignore-counts'

# (pattern, canon key) — a number matched by the pattern must equal the arch-09
# canon value for that key. Lookbehinds exclude subset phrasings ("~35 named
# formulas", "5-7 bundles") so only whole-vocabulary claims are validated.
COUNT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r'(?<![~\d.])(\d+)\s+substantive\b'), 'formulas'),
    (re.compile(r'\((\d+)\s+entries\s+\+'), 'formulas'),
    (re.compile(r'(?<![~\d.–-])(\d+)\s+named\s+formulas\b'), 'formulas'),
    (re.compile(r'(?<![~\d.–(-])(\d+)\s+formulas\b'), 'formulas'),
    (re.compile(r'(?<![~\d.])(\d+)\s+residual\s+categor'), 'categories'),
    (re.compile(r'(?<![~\d.])(\d+)\s+named\s+tags\b'), 'categories'),
    (re.compile(r'(?<![~\d.])(\d+)\s+CategoryTags\b'), 'categories'),
    (re.compile(r'(?<!Stage )(?<![~\d.–-])(\d+)\s+methods\b'), 'methods'),
    (re.compile(r'(?<![~\d.–-])(\d+)\s+templates\b'), 'templates'),
    (re.compile(r'(?<![~\d.–-])(\d+)\s+(?:observable\s+)?bundles\b'), 'bundles'),
    (re.compile(r'(?<![~\d.])(\d+)\s+cert\s+obligations\b'), 'obligations'),
)

ARCH09_CANON_PATTERNS: dict[str, str] = {
    'methods': r'\|\s*Computational methods\s*\|\s*(\d+)',
    'templates': r'\|\s*Abstract-property templates\s*\|\s*(\d+)',
    'formulas': r'\|\s*Named formulas\s*\|\s*(\d+)\s+substantive',
    'markers': r'\|\s*Named formulas\s*\|\s*\d+\s+substantive\s*\(\+(\d+)',
    'bundles': r'\|\s*Observable bundles\s*\|\s*(\d+)',
    'categories': r'\|\s*Residual categories\s*\|\s*(\d+)',
    'obligations': r'\|\s*Cert obligations\s*\|\s*(\d+)',
}


def _Registry_Tallies() -> tuple[int, int, dict[str, int], dict[str, int]]:
    '''(substantive, markers, tier tally, diff tally) from the canonical CSV.'''
    with REGISTRY_CSV_PATH.open(encoding='utf-8', newline='') as csv_handle:
        data_rows: list[list[str]] = list(csv.reader(csv_handle))[1:]
    marker_count: int = 0
    tier_tally: dict[str, int] = defaultdict(int)
    diff_tally: dict[str, int] = defaultdict(int)
    for row in data_rows:
        tier_value: str = row[4].strip() if len(row) > 4 else ''
        if tier_value == '—':
            marker_count += 1
            continue
        tier_tally[tier_value] += 1
        if len(row) > 5:
            diff_tally[row[5].strip()] += 1
    return len(data_rows) - marker_count, marker_count, dict(tier_tally), dict(diff_tally)


def _Arch09_Canon() -> tuple[dict[str, int], list[str]]:
    canon_text: str = VOCAB_CANON_PATH.read_text(encoding='utf-8')
    canon_values: dict[str, int] = {}
    parse_failures: list[str] = []
    for canon_key, canon_pattern in ARCH09_CANON_PATTERNS.items():
        pattern_match = re.search(canon_pattern, canon_text)
        if pattern_match is None:
            parse_failures.append(f'counts: arch-09 canon row not found for {canon_key!r}')
            continue
        canon_values[canon_key] = int(pattern_match.group(1))
    return canon_values, parse_failures


def _Count_Scan_Files() -> list[Path]:
    scan_files: list[Path] = [REPO_ROOT / 'README.md', REPO_ROOT / 'AUDIT_PROMPT.md']
    for markdown_path in sorted(DOCS_ROOT.rglob('*.md')):
        relative_parts: tuple[str, ...] = markdown_path.relative_to(DOCS_ROOT).parts
        if relative_parts[0] in COUNT_SCAN_EXCLUDED_DIRS:
            continue
        scan_files.append(markdown_path)
    return scan_files


def Check_Vocabulary_Counts(records: tuple[FileRecord, ...]) -> list[str]:
    del records  # reads the canon + CSV + scan set directly
    failures: list[str] = []
    canon_values, parse_failures = _Arch09_Canon()
    failures.extend(parse_failures)
    substantive_count, marker_count, tier_tally, diff_tally = _Registry_Tallies()
    if canon_values.get('formulas') not in (None, substantive_count):
        failures.append(
            f'counts: arch-09 claims {canon_values["formulas"]} substantive formulas; '
            f'registry CSV has {substantive_count}'
        )
    if canon_values.get('markers') not in (None, marker_count):
        failures.append(
            f'counts: arch-09 claims {canon_values["markers"]} markers; '
            f'registry CSV has {marker_count}'
        )
    canon_values['formulas'] = substantive_count  # CSV is ground truth for the scan
    for scan_path in _Count_Scan_Files():
        if not scan_path.exists():
            continue
        for line_number, line_text in enumerate(
            scan_path.read_text(encoding='utf-8').splitlines(), start=1
        ):
            if COUNT_IGNORE_MARKER in line_text:
                continue
            for count_pattern, canon_key in COUNT_PATTERNS:
                for pattern_match in count_pattern.finditer(line_text):
                    quoted_value: int = int(pattern_match.group(1))
                    expected_value: int | None = canon_values.get(canon_key)
                    if expected_value is not None and quoted_value != expected_value:
                        failures.append(
                            f'counts: {scan_path.relative_to(REPO_ROOT)}:{line_number}: '
                            f'says {quoted_value} {canon_key}, canon is {expected_value}'
                        )
    if OVERVIEW_PATH.exists():
        # The §6.3 tally lines write "T0 … (69 formulas) · T1 … (40) · …" — parse
        # each "T<n>/D<n> … (<count>)" segment on the cost-tier / diff-tag lines.
        for overview_line in OVERVIEW_PATH.read_text(encoding='utf-8').splitlines():
            if '**cost-tier:**' in overview_line:
                tally_kind, csv_tally = 'T', tier_tally
            elif '**diff-tag:**' in overview_line:
                tally_kind, csv_tally = 'D', diff_tally
            else:
                continue
            for tally_match in re.finditer(
                rf'\b{tally_kind}(\d)\b[^·(]*\((\d+)(?:\s+formulas)?\)', overview_line
            ):
                tag_name: str = f'{tally_kind}{tally_match.group(1)}'
                quoted_tally: int = int(tally_match.group(2))
                if csv_tally.get(tag_name, 0) != quoted_tally:
                    failures.append(
                        f'counts: computational-overview.md says {tag_name}=({quoted_tally}); '
                        f'registry CSV tallies {csv_tally.get(tag_name, 0)}'
                    )
    return failures


def Run_Checks(records: tuple[FileRecord, ...]) -> tuple[Iterable[str], ...]:
    checks: tuple[object, ...] = (
        Check_Frontmatter_Shape,
        Check_Id_Matches_Filename,
        Check_Canonical_For_Unique,
        Check_Depends_Referenced_By_Symmetric,
        Check_Inline_References_Resolve,
        Check_Research_Sources_Exist,
        Check_Manifest_Coverage,
        Check_Vocabulary_Counts,
    )
    with ThreadPoolExecutor(max_workers=len(checks)) as worker_pool:
        results: list[Iterable[str]] = list(
            worker_pool.map(lambda check_function: check_function(records), checks)  # type: ignore[arg-type, operator]
        )
    return tuple(results)


def Main() -> int:
    records: tuple[FileRecord, ...] = Discover_Files()
    all_results: tuple[Iterable[str], ...] = Run_Checks(records)
    failure_total: int = 0
    for result_failures in all_results:
        for failure_message in result_failures:
            print(failure_message, file=sys.stderr)
            failure_total += 1
    if failure_total == 0:
        print(f'lint OK — {len(records)} files clean')
        return 0
    print(f'lint FAILED — {failure_total} issues across {len(records)} files', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(Main())

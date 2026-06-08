'''Carve monolithic docs into atomic per-section files with frontmatter.

This script reads the current monolithic spec documents
(architecture.md, implementation-plan.md, mvp-slice.md), splits each
along its top-level section boundaries, and emits one atomic file per
section under the appropriate per-doc directory, prepending YAML
frontmatter conformant to docs/meta/conventions.md.

It is run once to bootstrap the atomic-file tree. After this point,
edits happen on the atomic files and assembly is mechanical via
assemble.py.
'''

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import NamedTuple


DOCS_ROOT: Path = Path(__file__).resolve().parents[1]


class Section(NamedTuple):
    number: int
    title: str
    body: str


def Read_Source(path: Path) -> str:
    with path.open(encoding='utf-8') as source_handle:
        return source_handle.read()


def Split_Top_Sections(markdown_text: str) -> list[Section]:
    '''Split a markdown document along its `## ` section headers.

    Lines before the first `## ` (the document title and any preface)
    are returned as Section number 0 with title 'preface'.
    '''
    section_header_pattern: re.Pattern[str] = re.compile(
        r'^##\s+(?P<heading>.+?)\s*$',
        re.MULTILINE,
    )
    matches: list[re.Match[str]] = list(section_header_pattern.finditer(markdown_text))
    sections: list[Section] = []
    if not matches:
        return [Section(number=0, title='preface', body=markdown_text.strip() + '\n')]
    preface: str = markdown_text[: matches[0].start()].strip()
    if preface:
        sections.append(Section(number=0, title='preface', body=preface + '\n'))
    for index, match in enumerate(matches):
        end: int = matches[index + 1].start() if index + 1 < len(matches) else len(markdown_text)
        heading: str = match.group('heading')
        body: str = markdown_text[match.start():end].rstrip() + '\n'
        section_number: int = _Extract_Section_Number(heading, fallback=index + 1)
        sections.append(Section(number=section_number, title=heading, body=body))
    return sections


def _Extract_Section_Number(heading: str, fallback: int) -> int:
    leading_number_pattern: re.Pattern[str] = re.compile(r'^(\d+)[\.\s]')
    leading_number_match: re.Match[str] | None = leading_number_pattern.match(heading)
    if leading_number_match is not None:
        return int(leading_number_match.group(1))
    return fallback


def Slugify(title: str) -> str:
    lowered: str = title.lower()
    cleaned: str = re.sub(r'[^a-z0-9]+', '-', lowered).strip('-')
    return cleaned or 'section'


def Build_Frontmatter(
    file_id: str,
    title: str,
    canonical_for: list[str],
    depends_on: list[str],
) -> str:
    yaml_lines: list[str] = ['---', f'id: {file_id}', f'title: {title}', 'status: draft', 'revision: 1']
    if canonical_for:
        yaml_lines.append('canonical-for:')
        for entry in canonical_for:
            yaml_lines.append(f'  - {entry}')
    else:
        yaml_lines.append('canonical-for: []')
    if depends_on:
        yaml_lines.append('depends-on:')
        for entry in depends_on:
            yaml_lines.append(f'  - {entry}')
    else:
        yaml_lines.append('depends-on: []')
    yaml_lines.append('referenced-by: []')
    yaml_lines.append('research-sources: []')
    yaml_lines.append('---')
    yaml_lines.append('')
    return '\n'.join(yaml_lines)


def Strip_Section_Number_Prefix(heading: str) -> str:
    '''Remove a leading `N.` or `N` from a section heading for the title field.'''
    return re.sub(r'^\d+\.\s*', '', heading).strip()


def Write_Atomic(
    output_path: Path,
    file_id: str,
    title: str,
    body: str,
    canonical_for: list[str] | None = None,
    depends_on: list[str] | None = None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter_text: str = Build_Frontmatter(
        file_id=file_id,
        title=title,
        canonical_for=canonical_for or [],
        depends_on=depends_on or [],
    )
    body_with_h1: str = body
    if not body_with_h1.lstrip().startswith('# '):
        body_with_h1 = f'# {title}\n\n' + re.sub(r'^##\s+.+?\n', '', body, count=1).lstrip()
    output_path.write_text(frontmatter_text + body_with_h1, encoding='utf-8')


ARCHITECTURE_LAYOUT: list[tuple[int, str, str, list[str]]] = [
    (1, '01-purpose', 'Purpose and scope', ['purpose', 'mvp scope']),
    (2, '02-libraries', 'Library landscape', ['library partitioning']),
    (3, '03-inputs', 'Inputs', ['top-level inputs']),
    (4, '04-state', 'The unified state', ['state 7-tuple']),
    (5, '05-generic', 'Dynamics — GENERIC', ['GENERIC equation', 'nine regimes as extractions']),
    (6, '08-bo-levels', 'The 4-level Born-Oppenheimer hierarchy', ['BO hierarchy', 'dressing tiers']),
    (7, '_dead-three-layer', '(retired) Three-layer architecture', []),
    (8, '09-vocabularies', 'Canonical vocabularies and counts', ['vocabulary counts']),
    (9, '15-gamma-hat', 'γ̂ representation', []),
    (10, '10-typeclasses', 'Layer-0 typeclass alphabet', ['Layer-0 typeclasses']),
    (11, '11-residuals', 'Residuals', []),
    (12, '12-cert', 'Cert obligations', ['ten cert obligations']),
    (13, '13-applicability', 'Applicability classifiers', ['applicability discipline']),
    (14, '14-topology', 'Topology atlas', ['topology atlas']),
    (15, '_dead-two-tier', '(retired) Two-tier accuracy', []),
    (16, '17-out-of-scope', 'Out of scope', ['scope exclusions']),
    (17, '18-open-decisions', 'Open decisions', ['open decisions']),
]


IMPLEMENTATION_LAYOUT: list[tuple[int, str, str, list[str]]] = [
    (1, '01-principles', 'Architectural principles', ['architectural principles']),
    (2, '02-methods', 'The 12 computational methods', ['method signatures']),
    (3, '03-templates', 'The 20 abstract-property templates', ['template signatures']),
    (4, '04-formulas', 'The named-formula registry', ['formula registry signatures']),
    (5, '05-bundles', 'The 11 observable bundles', ['bundle signatures']),
    (6, '06-compositions', 'Target observables as typed compositions', ['per-regime compositions']),
    (7, '07-residual-factory', 'Residual contract', []),
    (8, '07-residual-factory-record', 'ResidualGenerator factory', []),
    (9, '_dead-dressing-cert-records', '(retired) Dressing-layer cert records', []),
    (10, '08-cert-detail', 'Cert obligations — detail and axis mapping', ['cert obligation detail']),
    (11, '09-cross-cutting', 'Cross-cutting design rules', ['cross-cutting rules']),
    (12, '_pino-bridge-source', 'pino-bridge exports (source for arch/16)', []),
    (13, '_dead-per-regime-extraction', '(retired) Per-regime GENERIC extraction', []),
    (14, '10-build-sequence', 'Build sequence', ['build sequence']),
    (15, '11-verification', 'Verification', ['verification gates']),
]


MVP_LAYOUT: list[tuple[int, str, str, list[str]]] = [
    (1, '01-system', 'The system', ['diamond MVP system']),
    (2, '02-gamma-budget', 'γ̂ budget at MVP scale', ['γ̂ MVP budget']),
    (3, '03-capabilities', 'The three capability slices', ['MVP capabilities']),
    (4, '04-in-mvp-vs-deferred', 'In-MVP vs deferred', ['MVP scope']),
    (5, '_dead-closed-form-vs-kinetic', '(retired) Closed-form vs kinetic', []),
    (6, '05-decisions-forced', 'Decisions this slice forces', ['MVP-forced decisions']),
    (7, '06-build-order', 'MVP build order', ['MVP build order']),
]


def Carve_Document(
    source_path: Path,
    output_dir: Path,
    layout: list[tuple[int, str, str, list[str]]],
    id_prefix: str,
) -> None:
    sections: list[Section] = Split_Top_Sections(Read_Source(source_path))
    section_lookup: dict[int, Section] = {section.number: section for section in sections}
    for section_number, target_id, override_title, canonical_for in layout:
        if target_id.startswith('_dead-') or target_id.startswith('_'):
            continue
        if section_number not in section_lookup:
            print(f'  [skip] {source_path.name} §{section_number} not found', file=sys.stderr)
            continue
        section: Section = section_lookup[section_number]
        cleaned_title: str = override_title or Strip_Section_Number_Prefix(section.title)
        Write_Atomic(
            output_path=output_dir / f'{target_id}.md',
            file_id=f'{id_prefix}-{target_id}',
            title=cleaned_title,
            body=section.body,
            canonical_for=canonical_for,
            depends_on=[],
        )
        print(f'  wrote {output_dir.name}/{target_id}.md  ←  {source_path.name} §{section_number}')


def main() -> None:
    repo_root: Path = DOCS_ROOT.parent
    arch_source: Path = repo_root / 'docs' / 'architecture.md'
    impl_source: Path = repo_root / 'docs' / 'implementation-plan.md'
    mvp_source: Path = repo_root / 'docs' / 'mvp-slice.md'
    print('Carving architecture.md ...')
    Carve_Document(
        source_path=arch_source,
        output_dir=DOCS_ROOT / 'architecture',
        layout=ARCHITECTURE_LAYOUT,
        id_prefix='arch',
    )
    print('Carving implementation-plan.md ...')
    Carve_Document(
        source_path=impl_source,
        output_dir=DOCS_ROOT / 'implementation',
        layout=IMPLEMENTATION_LAYOUT,
        id_prefix='impl',
    )
    print('Carving mvp-slice.md ...')
    Carve_Document(
        source_path=mvp_source,
        output_dir=DOCS_ROOT / 'mvp',
        layout=MVP_LAYOUT,
        id_prefix='mvp',
    )
    print('Done.')


if __name__ == '__main__':
    main()

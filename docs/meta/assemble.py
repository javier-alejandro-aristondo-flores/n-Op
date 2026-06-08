'''Assemble atomic doc files into monoliths and named bundles.

Reads docs/meta/manifest.yaml, concatenates the atomic files listed
under each monolith / bundle in order, strips per-file YAML
frontmatter, prepends a TOC, and writes the regenerated output to
disk. Designed to be idempotent: re-running over a clean tree
produces byte-identical output.
'''

from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import yaml


DOCS_ROOT: Path = Path(__file__).resolve().parents[1]
MANIFEST_PATH: Path = DOCS_ROOT / 'meta' / 'manifest.yaml'

GENERATED_BANNER: str = (
    '<!-- GENERATED FILE — do not edit. Source files under '
    'docs/{architecture,implementation,mvp}/. '
    'Regenerate with `python docs/meta/assemble.py`. -->\n'
)


@dataclass(frozen=True, slots=True)
class AssemblyTarget:
    name: str
    title: str
    output_path: Path
    sources: tuple[Path, ...]


def Read_Manifest(manifest_path: Path) -> tuple[tuple[AssemblyTarget, ...], tuple[AssemblyTarget, ...]]:
    with manifest_path.open(encoding='utf-8') as manifest_handle:
        raw_manifest: object = yaml.safe_load(manifest_handle)
    if not isinstance(raw_manifest, dict):
        raise ValueError('manifest.yaml root must be a mapping')

    monoliths: tuple[AssemblyTarget, ...] = _Build_Targets(raw_manifest.get('monoliths', {}))
    bundles: tuple[AssemblyTarget, ...] = _Build_Targets(raw_manifest.get('bundles', {}))
    return monoliths, bundles


def _Build_Targets(targets_section: object) -> tuple[AssemblyTarget, ...]:
    if not isinstance(targets_section, dict):
        return ()
    targets_built: list[AssemblyTarget] = []
    for target_name, target_spec in targets_section.items():
        if not isinstance(target_spec, dict):
            raise ValueError(f'manifest target {target_name!r} must be a mapping')
        output_relative: object = target_spec.get('output')
        title: object = target_spec.get('title', target_name)
        source_paths: object = target_spec.get('sources', [])
        if not isinstance(output_relative, str):
            raise ValueError(f'manifest target {target_name!r} missing string `output`')
        if not isinstance(title, str):
            raise ValueError(f'manifest target {target_name!r} `title` must be a string')
        if not isinstance(source_paths, list):
            raise ValueError(f'manifest target {target_name!r} `sources` must be a list')
        sources_built: tuple[Path, ...] = tuple(
            DOCS_ROOT / str(source_relative) for source_relative in source_paths
        )
        targets_built.append(
            AssemblyTarget(
                name=str(target_name),
                title=title,
                output_path=DOCS_ROOT / output_relative,
                sources=sources_built,
            )
        )
    return tuple(targets_built)


def Strip_Frontmatter(file_text: str) -> tuple[dict[str, object], str]:
    '''Return (frontmatter_dict, body_text). Frontmatter is empty if absent.'''
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


def Render_Toc(source_files: tuple[Path, ...]) -> str:
    toc_lines: list[str] = ['## Contents', '']
    for source_path in source_files:
        with source_path.open(encoding='utf-8') as source_handle:
            file_text: str = source_handle.read()
        frontmatter, body_text = Strip_Frontmatter(file_text)
        section_title: str = str(frontmatter.get('title', source_path.stem))
        anchor_id: str = str(frontmatter.get('id', source_path.stem))
        _ = body_text
        toc_lines.append(f'- [{section_title}](#{anchor_id})')
    toc_lines.append('')
    return '\n'.join(toc_lines)


def Assemble_Target(target: AssemblyTarget) -> str:
    chunks: list[str] = [
        GENERATED_BANNER,
        f'# {target.title}\n',
        Render_Toc(target.sources),
    ]
    for source_path in target.sources:
        with source_path.open(encoding='utf-8') as source_handle:
            file_text: str = source_handle.read()
        frontmatter, body_text = Strip_Frontmatter(file_text)
        anchor_id: str = str(frontmatter.get('id', source_path.stem))
        chunks.append(f'\n<a id="{anchor_id}"></a>\n')
        chunks.append(body_text.rstrip() + '\n')
    return '\n'.join(chunks)


def Write_Target(target: AssemblyTarget) -> Path:
    rendered_text: str = Assemble_Target(target)
    target.output_path.parent.mkdir(parents=True, exist_ok=True)
    with target.output_path.open('w', encoding='utf-8') as output_handle:
        output_handle.write(rendered_text)
    return target.output_path


def Main() -> int:
    monoliths, bundles = Read_Manifest(MANIFEST_PATH)
    all_targets: tuple[AssemblyTarget, ...] = monoliths + bundles
    with ThreadPoolExecutor(max_workers=max(1, len(all_targets))) as worker_pool:
        written_paths: list[Path] = list(worker_pool.map(Write_Target, all_targets))
    for written_path in written_paths:
        print(f'wrote {written_path.relative_to(DOCS_ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(Main())

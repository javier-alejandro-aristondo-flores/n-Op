# Scaffolding baseline — measured at 2af93d2

Verification target (plan §11.3): every count below must be **0** after cutover.
Scope: the corpus as it stands, excluding .git and restructure/.

| Pattern | Current count | Target |
|---|---|---|
| history-marker lines | 116 | 0 |
| strikethrough `~~` | 7 | 0 |
| `Changelog` headings | 10 | 0 |
| backticked-id citations (unchecked syntax) | 467 | 0 |
| bracketed-id citations (surviving syntax, will gain anchors) | 344 | n/a |
| ordinal section coordinates `§N` | 814 | 0 |
| retired `arch-NN`/`impl-NN` ids | 37 | 0 |
| `content-hash:` stamps | 57 | 0 |
| `authority:` fields | 59 | 0 |
| pages with vacuous `canonical-for` | 18 | 0 |
| pages with invalid-YAML frontmatter | 3 | 0 |

## Notes

- `§N` ordinals include legitimate external citations (e.g. `Öttinger 2005 §5.3`).
  The corpus deliberately does not check these because they are shaped identically
  to internal coordinates. After the restructure, internal citations carry anchors
  (`[page#anchor]`), so any surviving `§` is unambiguously external — which is what
  makes the target 0 for *internal* ones checkable at all.
- The backticked-id list is a sample of 25 known page ids, not exhaustive; the true
  count is higher. It is a floor, not a measurement.
- **`content-hash` 57 and `authority` 59 against 58 pages is not a defect.**
  `10.1-conventions` documents the frontmatter schema in its body, so it carries a
  second, illustrative `authority: canon | supporting` and `content-hash: <12 hex>`.
  Checked and dismissed — recorded here so it is not re-investigated.
  *Carry to Phase 2:* the new checker must parse only the leading frontmatter block,
  never a schema example in a body. The same hazard moves to
  `practice/agent-contract`, which will document the schema by definition.
- These counts use a wider scope than the plan's §2 figures (they include
  `journal/live/`, `physics/`, and `informed-operator/`, which §2 counted separately).
  Both are correct for their scope; this file is the one to verify against.

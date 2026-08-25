"""Corpus access — the discipline of test-suite.md §9, as code.

Intended contents (implementation phase):
  - parsers — CHGCAR-family readers: spin-block aware (under spin polarization every field
    file doubles: density + magnetization, localization up/down, potential up/down),
    augmentation-block skipping, values divided by cell volume on ingest (grid mean equals
    the electron count — the parser calibration check)
  - store — the derived-tensor store design of §9.1: one file per run on /Pool, float32
    fields, float64 labels, provenance sidecars; nothing volumetric leaves /Pool
  - splits — the split engine: consumes the duplicate registry, the orbit map (exact
    symmetry degeneracy makes random splits test-on-train), the twin and satellite co-split
    rules, and the exclusion registry E1–E10
  - floors — identity, global affine + per-shell linear filter, basis + nearest-neighbor,
    superposed atomic densities (already on disk as AECCAR1 for the paired-fields block),
    spectral Poisson (doubles as the pipeline units test), pointwise semilocal
    electron-localization, and the spectral scissor
"""

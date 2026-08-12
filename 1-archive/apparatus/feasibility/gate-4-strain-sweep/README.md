# Gate 4 — the strain sweep

**Question:** does strain → electronic structure carry response beyond textbook
deformation-potential theory?

**Answer:** `VERDICT.md`. Read that first; everything here is the evidence it cites.

**Corpus:** the diamond stretch-and-skew sweep — 1,179 distortion points (1,131 physically
distinct), each computed twice, PBE then gap-tuned HSE06(α = 0.27). Documented in
`data/diamond-strain-sweep/`; the archives are 10.7 GB on `/Pool` and are never committed.

## Two roots

| | where | committed |
|---|---|---|
| **results, figures** | this directory | **yes** — every number in the verdict is checkable without the dataset |
| **extracted cache** | `/Pool`, overridable with `NOP_SWEEP_CACHE` | **never** — 1.6 GB mirroring run directories that each carry a licensed pseudopotential |

`code/paths.py` resolves both and asserts the distinction in opposing directions. While the
campaign ran, both were one directory on `/Pool` and each script asserted
`OUT.startswith("/Pool/")`; that single assertion became two when the results moved into the
repository.

**Only the first two programs need the cache.** Everything downstream reads the committed
tables, so the pipeline detaches from `/Pool` after `build_table.py` — which is what makes
this verdict checkable on a machine that has never seen the dataset.

## The programs

In dependency order. Run from the repository root, e.g.
`./.venv/bin/python feasibility/gate-4-strain-sweep/code/step3_ladder.py`.

| program | needs cache | reads | writes | why it exists |
|---|:---:|---|---|---|
| `paths.py` | — | — | — | resolves the two roots; puts the repository on the import path so `physics.formulas.elastic` resolves from anywhere |
| `extract_sweep.py` | builds it | the six family archives | the cache; `file_manifest.json`, `digests.json` | one streaming pass over 10.7 GB. Writes only small text; hashes CHGCAR, WAVECAR and vasprun **in the stream** so the copy-vs-rerun test has checksums without the bytes. Denies `POTCAR` by assertion |
| `sweep_read.py` | ✔ | EIGENVAL, POSCAR, INCAR, OSZICAR | — | the readers, plus observables O1–O4. Reuses the repository's own `green_lagrange_voigt` rather than reimplementing strain |
| `build_table.py` | ✔ | cache; `step0_runs.csv` | `observables.csv`, `spectra.npz`, `wide_bands.npz`, `table_meta.json` | the master table. Canonicalizes two things without which no run is comparable to any other: k-points folded onto shared ±k classes, and bands truncated to the common 8 |
| `step0_inventory.py` | ✔ | cache; `file_manifest.json` | `step0_runs.csv`, `step0_summary.json` | coverage, pairing, mesh, files present, and each functional's own a₀. **Blocking** — it decides whether the corpus reaches the nonlinear regime at all |
| `step1_noise.py` | ✔ | cache; `observables.csv`, `digests.json`, the committed run manifest | `step1_noise.csv`, `step1_noise.json`, `step1_copies.csv` | the noise floor, by two independent routes. **Blocking** — no residual anywhere means anything until it is compared against this |
| `step2_report.py` | — | `observables.csv`, `step1_copies.csv`, `table_meta.json` | stdout | what the observables look like, including the argmin-hopping artifact, reported rather than smoothed |
| `step3_ladder.py` | — | `observables.csv`, `step1_copies.csv`, `step1_noise.csv` | `step3_ladder.csv`, `step3_ladder.json`, `step3_residual_vs_strain.csv` | the scalar ladder M0–M4, where M2 is deformation-potential theory with valley `min` and Bir–Pikus splitting — the model to beat |
| `step4_dos.py` | — | `spectra.npz`, `observables.csv`, `step1_copies.csv`, `wide_bands.npz` | `step4_dos.json`, `step4_residual_vs_strain_{pbe,hse}.csv`, `step4_profile_{pbe,hse}.npz` | the function-valued ladder L0–L3, and what the 8-band truncation costs |
| `step4b_extrapolate.py` | — | `spectra.npz`, `observables.csv`, `step1_copies.csv` | `step4b_splits_{pbe,hse}.csv` | the same ladder off-grid. Exists because interpolation flattered one rung so badly it nearly changed the verdict |
| `step5_drift.py` | ✔ (PROCAR only) | `spectra.npz`, `observables.csv`, `step1_copies.csv` | `step5_coefficients.csv`, `step5_drift_vs_strain.csv`, `step5_noise.json` | does the hybrid correction drift with strain? The one measurement designed so that no outcome returns empty |
| `plots.py` | — | the result tables | `figures/plot_gate4_summary.png` | the four headline panels |

`step5_drift.py` needs the cache only for its band-matching verification, which reads
PROCAR on the ten most-strained cells. The drift measurement itself runs from
`spectra.npz`.

## Reproducing

Without the dataset, everything from `step2_report.py` onward runs as-is and reproduces the
verdict's tables. Two numbers worth checking, because they are the ones the decision rests
on:

```
step3_ladder.py   PBE indirect gap, M2, grouped CV, top strain quartile   148.9 meV
step5_drift.py    slope_occ, mean over 1,131 shapes                       0.1102
```

With the dataset, point `NOP_SWEEP_CACHE` at an extracted cache — or build one with
`extract_sweep.py`, given `NOP_SWEEP_ARCHIVES`. A script that needs the cache and cannot
find it exits with a message saying so, rather than failing fifty lines later.

## What is not here

`results/logs/` holds the console output of the runs that produced the committed tables —
provenance, not input. The `probe/` directory used to work out the file formats, and the
1.6 GB cache, stay on `/Pool`.

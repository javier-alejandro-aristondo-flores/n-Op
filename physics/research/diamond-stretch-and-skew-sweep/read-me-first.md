# Diamond stretch-and-skew sweep — reference suite

> **Copy — the dataset itself lives at `/Pool/Diamond_Stretch_And_Skew_Sweep/`.** This is a
> research-stratum companion describing an external DFT dataset (diamond lattice-distortion
> sweeps, VASP 6.2.0, PBE + HSE06(α=0.27)); it is **not** part of the lint-enforced atomic tree
> (`docs/architecture/`, `docs/implementation/`, `docs/mvp/`), which stays canonical. `/Pool` is
> the source of truth for both these documents and the data; if they ever disagree, `/Pool`
> wins. The data is **not** in this repository and must not be — every run directory holds a
> VASP-licensed POTCAR and this remote is public. Cite this suite from a spec via
> `research-sources:`.


**Read this first.** This folder holds a complete VASP dataset (diamond, lattice-distortion
sweeps at PBE + tuned-HSE06 level) plus a document suite that teaches you — human or agent —
how to read it, what every file means, and everything that can be derived from it.

## The suite

| File | What it answers |
|---|---|
| `read-me-first.md` | This map, provenance, and archive-health summary. |
| `01-what-this-data-is.md` | What the dataset is; directory anatomy; a dictionary of every file type; what values/units/conventions mean. |
| `02-how-to-read-and-derive.md` | **How to derive what the program needs**: the needs-map (bundle/bridge → recipe), the reading mechanics (files, fields, transformations, corrections), and verified worked examples with real numbers. |
| `03-what-is-derivable.md` | **Grab-everything list**: the exhaustive inventory of everything extractable or scientifically extrapolatable, useful to the project or not, tiered T0–T6 by model-dependence, plus the explicit NOT-derivable list and extrapolation discipline. |
| `04-data-health-gaps-and-caveats.md` | Design gaps, systematic caveats, licensing warnings, and traps. |
| `index-of-all-runs.tsv` | Machine-readable manifest: one row per distortion point (1,179 rows) with parsed deformation parameters, duplicate flags, and completeness status. |
| `CHANGELOG.md` | Every old→new name mapping. Also the inverse map: it is what you apply to restore VASP-canonical filenames. |

## What the data is, in three sentences

Six "distortion families" sample the six lattice degrees of freedom (3 axial strains,
3 shear angles) of the 2-atom diamond primitive cell (C, a₀ = 3.567 Å), **1,179 distortion
points** in total (**1,131 physically distinct** — see the duplicate warning below). Every
point was computed twice with VASP 6.2.0: a PBE ionic relaxation at fixed cell, then an
HSE06 hybrid single-point with **AEXX = 0.27** (a gap-tuned 27% exact-exchange fraction —
not the standard 25%) restarted from the PBE wavefunction. Each run keeps the full VASP
output cast, **2,358 calculations**, ≈ 10.7 GB compressed.

## Contents of `renamed-archives/`

| Archive | Deformation | Grid | Points |
|---|---|---|---|
| `1-scale-all-axes-uniformly.tar.gz` | volume sweep | V = 10.05…12.35 Å³, step 0.05 | 47 |
| `2-stretch-one-axis-or-two-axes.tar.gz` | uniax-x, biax-xy | ε = ±0.005…±0.100, step 0.005 | 40+40 |
| `3-skew-one-plane.tar.gz` | single shears xy/xz/yz | γ = ±0.005…±0.100, step 0.005 | 120 |
| `4-skew-two-planes.tar.gz` | shear plane-pairs xy·xz, xy·yz, xz·yz | γ ∈ {0, ±0.025, ±0.05, ±0.075, ±0.1}, 9×9 per pair | 228 |
| `5-skew-three-planes.tar.gz` | simultaneous 3 shears | γᵢ ∈ {±0.03, ±0.06, ±0.09} | 192 |
| `6-stretch-all-three-axes.tar.gz` | (εx,εy,εz) grid | {±0.02,±0.04,±0.06,±0.08}³ | 512 |

`original-archives-untouched/2atoms.tar.gz` is the pristine 10.7 GB source. It verifies
end-to-end with `gzip -t`, and every archive above was rebuilt from it. It is the provenance
anchor: the whole tree is reproducible from that one file.

## Provenance and recovery history

- Generated 2026-04-10 by cluster user `enk43` on a SLURM machine ("leap3" job scripts);
  INCAR comments are in Portuguese; the submit scripts mail `nathanrabelo@ufv.br`
  (Universidade Federal de Viçosa). Pseudopotential: `PAW_PBE C 08Apr2002`. VASP 6.2.0
  (18Jan21, "complex" build).
- **The data arrived broken twice, and is now whole.** It was first delivered as
  `test_files_for_diamond.zip` (8.10 GB), truncated in transfer; byte-slicing recovered 877
  points and concluded that a family 4 had existed and was lost. A OneDrive folder-zip
  re-download (`OneDrive_2026-07-16.zip`, 8.36 GB) was also truncated, but reached 30 points
  further. On **2026-07-16** the payload was downloaded **directly as a single file** rather
  than as a generated folder-zip. That file — `2atoms.tar.gz`, 10,698,913,488 bytes — passes
  `gzip -t` end-to-end.
- **Family 4 was never lost; it was simply last.** The archive order is 1, 3, 2, 6, 5, **4**,
  so every truncated copy stopped before reaching it. It is `4_angular-distortion-2angles`,
  228 points, mtime 11:44 — exactly inside the 10:50→12:04 gap the earlier salvage predicted
  from the numbering. That inference was correct; only the conclusion ("lost") was wrong.
- The lesson worth keeping: **OneDrive's "download folder as zip" truncates on payloads this
  size.** Download the file itself.

## Non-negotiable warnings

1. **POTCAR files are VASP-licensed material.** They are inside every run directory, now
   renamed `pseudopotential-LICENSED-DO-NOT-REDISTRIBUTE.txt`. Do not publish, redistribute,
   or commit them to any public repository. This is why the data lives here on `/Pool` and
   not inside the n-Op git repository, whose remote is public.
2. **AEXX = 0.27 is not standard HSE06.** Never compare these hybrid energies/gaps to
   literature HSE06(0.25) numbers without saying so; always carry α in provenance.
3. **The strain reference is the experimental lattice constant**, not either functional's
   own equilibrium — every strained run carries a constant reference stress offset (measured:
   **+19.7 kB at PBE, −86.3 kB at HSE06**). Difference it out, or carry a linear term in your
   energy fit. Omitting it biases C44 by 15% (details in `02_…` §B3 and `04_…` §2).
4. **1,179 rows are only 1,131 distinct shapes.** 24 single-skew shapes are each computed
   three times — once in `3-skew-one-plane`, twice in `4-skew-two-planes` — and all copies
   are bit-identical. **De-duplicate before any fit or training set**, or those 24 shapes
   carry 3× weight. The manifest's `duplicate_group` column marks them.
5. **Never rename these files back by hand.** `CHANGELOG.md` is the exact inverse map. VASP
   requires its canonical filenames, so restoring them is a prerequisite for any restart
   (see `03_…` T5).

# 01 — What this data is

> **Copy — the dataset itself lives at `/Pool/Diamond_Stretch_And_Skew_Sweep/`.** This is a
> research-stratum companion describing an external DFT dataset (diamond lattice-distortion
> sweeps, VASP 6.2.0, PBE + HSE06(α=0.27)); it is **not** part of the lint-enforced atomic tree
> (`docs/architecture/`, `docs/implementation/`, `docs/mvp/`), which stays canonical. `/Pool` is
> the source of truth for both these documents and the data; if they ever disagree, `/Pool`
> wins. The data is **not** in this repository and must not be — every run directory holds a
> VASP-licensed POTCAR and this remote is public. Cite this suite from a spec via
> `research-sources:`.


Audience: anyone (human or agent) who has never seen VASP output. After reading this you
should know what every file is, how to open it, and what the numbers mean.

Filenames in this tree have been renamed to plain language. `CHANGELOG.md` holds the exact
mapping to the VASP-canonical names, which is what you must restore before feeding anything
back to VASP.

## 1. The physical object being computed

Diamond: carbon in the diamond structure, described by its **2-atom fcc primitive cell**.
Unstrained reference: conventional lattice constant **a₀ = 3.567 Å** (the experimental
value), primitive vectors in the (a/2)(0,1,1), (a/2)(1,0,1), (a/2)(1,1,0) convention —
i.e. component value 1.7835 Å — with carbon atoms at fractional (0,0,0) and (¼,¼,¼).
Primitive-cell volume V₀(nominal) = a₀³/4 = 11.345 Å³.

Every run in this dataset is that cell **deformed** in a controlled way (see §3), with
total energy, forces, stress, band energies, densities of states, and charge density
computed by density-functional theory (DFT) using VASP.

## 2. The calculation: a two-step ladder at every point

Each distortion point is a directory containing exactly two sub-runs:

```
<family>/<point-name>/
├── 1-cheap-pbe-atoms-relaxed/       step 1: PBE functional, ionic relaxation at FIXED cell
└── 2-accurate-hse06-atoms-fixed/    step 2: HSE06 hybrid (alpha=0.27) static run, restarted from step 1
```

**Step 1 (`1-cheap-pbe-atoms-relaxed/`)** — INCAR essentials and what they mean:

| Tag | Value | Meaning |
|---|---|---|
| `ENCUT = 550` | 550 eV | Plane-wave basis cutoff (energy resolution of the basis). |
| `ISMEAR = 0`, `SIGMA = 0.01` | Gaussian, 10 meV | Occupation smearing — appropriate for an insulator. |
| `IBRION = 2`, `NSW = 500`, `POTIM = 0.5` | CG relaxation | Atoms are moved to their minimum-force positions. |
| `ISIF = 2` | | **Cell is frozen**; only atomic positions relax. The imposed strain is preserved. |
| `EDIFF = 1E-6`, `EDIFFG = -0.001` | | SCF converged to 10⁻⁶ eV; ions until forces < 1 meV/Å. |
| `ISYM = 0` | | Symmetry detection off (required for arbitrary distortions). |
| `LORBIT = 11` | | Orbital-projected eigenvalues (PROCAR + projected DOS) are written. |
| `LWAVE/LCHARGE = .TRUE.` | | WAVECAR and CHGCAR kept (that's why the dataset is large). |
| `NELM = 60`, `ALGO = Normal`, `NCORE = 12` | | SCF iteration cap, algorithm, parallel core grouping. |
| `PREC` | `Accurate` **or** `Accuratei` | **Varies by family** — see the note below. |

**The `PREC` typo, and proof it is harmless.** Families 1, 3, 5 spell `PREC = Accuratei`;
families 2, 4, 6 spell it correctly as `Accurate`. VASP prefix-matches the typo silently.
This is not a guess: family 3's `skew-x-toward-y-by-minus-0.100` and family 4's
`skew-xy-minus-0.100-xz-plus-0.000` are the **same geometry**, differ in **only** the `PREC`
spelling and a POSCAR comment line, and produce **bit-identical energies**. The typo is
provably inert. Trust the vasprun.xml parameter echo, not the INCAR text, as a general rule.

**Step 2 (`2-accurate-hse06-atoms-fixed/`)** — differences from step 1:
`ISTART = 1, ICHARG = 1` (restart from step-1 WAVECAR/CHGCAR), `NSW = 0` (no ionic motion:
a single-point calculation **at the PBE-relaxed geometry**), and the hybrid block

```
LHFCALC = .TRUE.   HFSCREEN = 0.2   AEXX = 0.27
```

which is HSE06 with the exact-exchange fraction raised from 0.25 to **0.27**. This tuning
reproduces diamond's experimental indirect band gap: extracting the gap from this data
gives 5.44 eV vs. 5.47 eV experimental (verified, see `02_…` §C4). Consequence: these are
"HSE06(α=0.27)" numbers — a deliberately calibrated functional, not textbook HSE06.

**K-points**: Γ-centered 7×7×7 Monkhorst–Pack mesh for both steps. Because `ISYM = 0`,
only time-reversal symmetry reduces the set: **172 irreducible k-points** (of 343) with
weights, listed in `irreducible-kpoint-list-with-weights.txt` and in the vasprun.xml
`kpointlist`. **Bands**: `NBANDS = 8` (8 valence electrons → 4 filled bands + 4 empty).
**Spin**: ISPIN = 1 (non-spin-polarized — correct for diamond).

## 3. The deformation families and their exact conventions

All deformations act on the unstrained cell of §1. Lattice rows transform as
row-vector × matrix; below, F is written so that new-row = old-row · F.
**Every convention below was verified on all 1,179 points** by recomputing
F = A_ref⁻¹ · A_def from the actual POSCAR lattices (recipe in `02_…` §B2).

| Family | Directory pattern | Deformation F | Sampled grid | Points |
|---|---|---|---|---|
| 1 scale all axes | `cell-volume-<V>-cubic-angstroms` | isotropic rescale to cell volume **V Å³** (encoded as a *negative POSCAR scale factor* −V; VASP reads negative scale = target volume) | V = 10.05 … 12.35, step 0.05 | 47 |
| 2 stretch 1 axis | `stretch-x-axis-by-<±e>` | diag(1+e, 1, 1) | e = ±0.005 … ±0.100, step 0.005 | 40 |
| 2 stretch 2 axes | `stretch-x-and-y-axes-by-<±e>` | diag(1+e, 1+e, 1) | same | 40 |
| 3 skew 1 plane | `skew-<p>-toward-<q>-by-<±g>` | simple shear: component p gains g × component q | pq ∈ {xy, xz, yz}, g = ±0.005 … ±0.100 | 120 |
| 4 skew 2 planes | `skew-<p1p2>-<±a>-<p3p4>-<±b>` | two simple shears composed; first plane gets a, second gets b | 3 plane-pairs × 9×9 grid, γ ∈ {0, ±0.025, ±0.05, ±0.075, ±0.1} | 228 |
| 5 skew 3 planes | `skew-xy-<±a>-xz-<±b>-yz-<±c>` | lower-triangular composition: x += a·y + b·z, then y += c·z | γᵢ ∈ {±0.03, ±0.06, ±0.09}; 192 of 216 | 192 |
| 6 stretch 3 axes | `stretch-x-<±x>-y-<±y>-z-<±z>` | diag(1+εx, 1+εy, 1+εz) | each ∈ {±0.02, ±0.04, ±0.06, ±0.08} → 8³ | 512 |

### The shear sector is a nested design

This is the structure worth internalizing. In Voigt coordinates the three shear degrees of
freedom are ε₄ (yz), ε₅ (xz), ε₆ (xy). The three shear families sample that 3-D space at
three different dimensionalities:

- **Family 3 samples the three axes** — one shear at a time, finely (step 0.005, to ±0.1).
- **Family 4 samples the three coordinate planes** — its `xy_xz` pair is the (ε₅,ε₆) plane,
  `xy_yz` is (ε₄,ε₆), `xz_yz` is (ε₄,ε₅) — at step 0.025, and because it *includes zero*,
  each plane contains the axes.
- **Family 5 samples the interior** — all three nonzero, coarsely (step 0.03, to ±0.09).

Axes ⊂ planes ⊂ interior. Nothing else in the dataset has this structure; the normal-strain
sector (families 1/2/6) has no equivalent 2-D layer.

### Notes and traps

- **Family 1 POSCARs use a different lattice frame** (a₁-along-x form + negative volume
  scale); families 2/3/4/5/6 use unit scale with strain baked into the (0,1,1)-form
  components. **Consequence: family 1's F carries a rotation that is a frame artifact, not
  physics.** Its antisymmetric part reaches 0.087, which is impossible for an isotropic
  rescale. `FᵀF` is isotropic to 1×10⁻¹¹, which proves it is cosmetic. **Never compare F
  across families** — compare Green–Lagrange strain or `FᵀF`.
- **Never infer the deformation from the directory name** — recompute it from the actual
  3×3 lattice (recipe in `02_…` §B2).
- Shears (families 3/4/5) are **simple shears**: F has a rotational part. They are also
  **exactly volume-preserving** — `det F = 1.000000` at every one of their 540 points, with
  no rounding slop. Families 2/6 have symmetric F, no rotation, and det F ranging 0.78–1.26.
- At |γ| = 0.1 the difference between engineering shear and Green–Lagrange strain matters;
  see `02_…` §B2.
- **The shear families are not purely shear in finite-strain terms.** A simple shear at γ
  produces a Green–Lagrange normal component of γ²/2 (0.005 at γ = 0.1). This is small but
  real, and it is why the "no mixed normal+shear sampling" claim needs the careful phrasing
  in `04_…` §2.
- Family 6 never has a zero component (pure-axis cases live in families 1/2). Family 4 does.

## 4. Dictionary of files in every run directory

Sizes are typical per run. The VASP-canonical name is given so you can map to any VASP
documentation you find; `CHANGELOG.md` is the machine-readable version of this column.

| File (as named here) | VASP name | Size | Format | What it is / how to read |
|---|---|---|---|---|
| `calculation-settings.txt` | `INCAR` | ~1 kB | text, `TAG = value` | The *requested* calculation parameters. The authoritative echo of what VASP actually used is inside vasprun.xml. |
| `kpoint-mesh-request.txt` | `KPOINTS` | 5 lines | text | "Auto / 0 / Gamma / 7 7 7 / 0 0 0" = Γ-centered 7×7×7. |
| `input-crystal-geometry.txt` | `POSCAR` | ~10 lines | text | Input crystal: comment; scale factor (positive = multiplier, **negative = target volume in Å³**); 3 lattice-vector rows (Å); element symbols; counts; `Direct` = fractional coordinates follow. |
| `final-relaxed-crystal-geometry.txt` | `CONTCAR` | ~10 lines | text | Same format, **final (relaxed) positions**. Difference from the input geometry = internal relaxation (nonzero only in shear families). |
| `pseudopotential-LICENSED-DO-NOT-REDISTRIBUTE.txt` | `POTCAR` | 207 kB | text (licensed) | `PAW_PBE C 08Apr2002`, ENMAX = 400 eV. **Licensed — never publish.** |
| `everything-machine-readable.xml` | `vasprun.xml` | ~0.5–0.6 MB | XML | **The primary machine-readable output.** Parameter echo, k-points + weights, per-ionic-step structures/energies/forces/**stress tensors**, final eigenvalues + occupations, (projected) DOS, atom info. Parse this; ignore most other files. |
| `full-run-log-human-readable.txt` | `OUTCAR` | ~170 kB | text log | Use only for things not in vasprun (VASP version line 1, timing, PAW details). Regex-fragile. |
| `energy-per-iteration-summary.txt` | `OSZICAR` | ~2 kB | text | One line per SCF iteration (`DAV: …`) and one summary per ionic step: `N F= <free energy> E0= <sigma->0 energy> dE= …`. Quick energy reads: last `E0=`. **First `E0=` is the clamped-ion energy** (§C3 of `02_…`). |
| `band-energies-per-kpoint.txt` | `EIGENVAL` | ~56 kB | text | Redundant with vasprun.xml (prefer the XML). |
| `density-of-states-curve.txt` | `DOSCAR` | ~83 kB | text | Header (6 lines; line 6 = Emax Emin NEDOS E_Fermi 1.0), then NEDOS rows of (E, DOS, integrated DOS). |
| `orbital-character-per-band-per-kpoint.txt` | `PROCAR` | ~0.5 MB | text | Orbital/site-projected band weights for every k, band. Also inside vasprun (`<projected>`). |
| `irreducible-kpoint-list-with-weights.txt` | `IBZKPT` | ~13 kB | text | The 172 irreducible k-points with integer weights. |
| `charge-density-grid-full.txt` | `CHGCAR` | 1.2 MB | text | ρ(r) on an FFT grid + PAW augmentation occupancies. POSCAR-style header, blank line, `NGXF NGYF NGZF`, then ρ·V values in Fortran order (x fastest), 5 per line, then `augmentation occupancies` blocks. Units: electrons (values are ρ×cell-volume; divide by V for e/Å³; sum × V/N_grid = N_electrons = 8). |
| `charge-density-grid-low-precision.txt` | `CHG` | 0.8 MB | text | Lower-precision, no augmentation data. Skip. |
| `wavefunctions-binary-restart-only.bin` | `WAVECAR` | 4–5 MB | **binary** | Plane-wave coefficients. Build-specific ("complex, 64-bit-record" build). Only useful to restart VASP or for specialist post-processing. |
| `atom-positions-per-relaxation-step.txt` | `XDATCAR` | ~0.5 kB | text | Ionic positions per relaxation step (trajectory). |
| `pair-correlation-function.txt` | `PCDAT` | small | text | Uninteresting for 2 atoms. |
| `relaxation-bookkeeping.txt` | `REPORT` | small | text | Skip. |
| `cluster-job-log-<jobid>.txt` | `slurm-<jobid>.out` | ~2 kB | text | Cluster job logs. Two logs in one directory = the job was re-run; vasprun.xml reflects the final state. |
| `cluster-submission-script.sh` | `run-vasp-leap3` | ~1 kB | shell | The SLURM submission script (cluster provenance). |

### Per-family top-level files

These sit at the root of each family archive, not inside run directories. **The earlier
version of this document omitted them entirely.**

| File (as named here) | Original | What it is |
|---|---|---|
| `extract-summary-csv.py` | `build_Vol_opt` | A **pymatgen extractor**, despite the name — it walks every point directory, parses vasprun/OUTCAR/POTCAR/POSCAR, and writes the summary CSVs below. Interactive: it prompts for which sub-run to scan. It **silently skips** any directory missing one of those four files, which is why absence from a CSV cannot distinguish "never run" from "crashed". |
| `build-hse06-runs.sh` | `build_HSE06` | Sets up each HSE06 sub-run from its PBE parent: makes the directory, copies CONTCAR→POSCAR, and **writes the HSE06 INCAR**. Recycled from a gallium-oxide project — it still says `# Enter the folder (e.g., MgGa2O4_distorted)`. |
| `electronic-summary-pbe.csv` | `comprehensive_electronic_summary.csv` | The author's own census at PBE level: one row per point with volume, lattice params, total energy, band gap, VBM/CBM, Fermi, convergence flag. |
| `electronic-summary-hse06.csv` | `comprehensive_electronic_summary_2-HSE06.csv` | Same at HSE06 level. |
| `make-band-gap-table.py` | `gap_table.py` | Gap tabulation helper (family 1 only). |
| `fast-analysis-script.py` | `nathan_fast_analyze.py` | Analysis helper. Renamed to drop the collaborator's personal name. |
| `build-volume-sweep-runs.sh` | `build_Vol_opt` (shell variant) | Run setup. |
| `collect-volume-sweep-results.sh` | `build_results_Vol_opt` | Result collection. Present in families 2–6 even though only family 1 has volume points. |
| `build-gibbs2-input.sh` | `build_gibbs2_ing` | GIBBS2 (quasi-harmonic EOS tool) input builder. Family 1 only. |
| `gulp-input-diamond.gin` | `Diamont.gin` | GULP input. Family 1 only. The original misspelled "Diamond". |

A stray vim swap file (`.build_Vol_opt.swp`) was present in family 3 and has been deleted.

## 5. Units and sign conventions (memorize these)

- **Energy**: eV. `E0` (σ→0 extrapolated) is the number to use, not `F`, though for
  SIGMA = 0.01 they agree to < 0.1 meV here. Absolute energies contain arbitrary
  pseudopotential offsets: **only differences within the same functional mean anything.**
  PBE and HSE06(0.27) totals differ by ~3 eV/cell in zero level — never mix them in one fit.
- **Length**: Å. **Volume**: Å³ (per 2-atom primitive cell; per-atom = /2).
- **Forces**: eV/Å, Cartesian, in vasprun `<varray name="forces">`.
- **Stress**: **kB (kilobar)** in vasprun/OUTCAR; 10 kB = 1 GPa. VASP's sign convention:
  **positive diagonal = compressive**; an expanded/stretched crystal shows *negative*
  diagonal stress (tension). External pressure that would balance the cell:
  P = −(σxx+σyy+σzz)/3.
- **Eigenvalues**: eV, absolute (not gap-referenced). Fermi level `efermi` is in
  vasprun/DOSCAR; for an insulator it sits mid-gap-ish and is only a bookkeeping number.
  Band gap must be computed from eigenvalues + occupations (recipe in `02_…` §C4).
- **k-points**: fractional coordinates of the *primitive reciprocal lattice* (not the
  cubic conventional one). Γ = (0,0,0).
- **Charge density**: stored as ρ(r)·V_cell in electrons (see table above).

## 6. What "derivable" means here — the mental model

Think of the dataset as a sampled scalar field and several sampled tensor/function fields
over a 6-dimensional deformation space:

```
deformation g  ∈  (isotropic V) ∪ (εx,εy,εz) ∪ (γxy,γxz,γyz)   [sampled on 6 sub-manifolds]
        ↓ for each sampled g, at two theory levels (PBE relaxed / HSE06(0.27) static):
E(g)            total energy                     [scalar]
σ(g)            stress tensor                    [3×3, every run — including HSE06]
u(g)            internal sublattice displacement [vector; nonzero only under shear]
{εnk(g)}        band energies at 172 k-points    [172 × 8]
DOS(E; g)       density of states                [function]
ρ(r; g)         charge density                   [3D field]
+ per-step relaxation trajectories (positions, E, F, σ) in the PBE runs
```

Everything in `03-what-is-derivable.md` is some functional of these primitives —
derivatives on the sampled grids, fits, symmetrized combinations, or model-mediated
extrapolations. `02-how-to-read-and-derive.md` gives the reading recipes.

# 04 — Data health, gaps, and caveats

> **Copy — the dataset itself lives at `/Pool/Diamond_Stretch_And_Skew_Sweep/`.** This is a
> research-stratum companion describing an external DFT dataset (diamond lattice-distortion
> sweeps, VASP 6.2.0, PBE + HSE06(α=0.27)); it is **not** part of the lint-enforced atomic tree
> (`docs/architecture/`, `docs/implementation/`, `docs/mvp/`), which stays canonical. `/Pool` is
> the source of truth for both these documents and the data; if they ever disagree, `/Pool`
> wins. The data is **not** in this repository and must not be — every run directory holds a
> VASP-licensed POTCAR and this remote is public. Cite this suite from a spec via
> `research-sources:`.


The honest ledger: what is missing, what was never sampled, what is systematically biased,
and what to double-check before trusting a number. Read together with `03_…`'s NOT-derivable
list.

## 1. Completeness ledger

**Nothing is truncated.** The source `original-archives-untouched/2atoms.tar.gz` passes
`gzip -t` end-to-end, and all six families extract cleanly.

| Family | Points | State |
|---|---|---|
| 1 scale all axes uniformly | 47 | complete (V = 10.05…12.35, step 0.05, no gaps) |
| 2 stretch one or two axes | 80 | complete (40 uniax-x + 40 biax-xy) |
| 3 skew one plane | 120 | complete (3 planes × 40) |
| 4 skew two planes | 228 | **12 genuine points absent** — see below |
| 5 skew three planes | 192 | **24 grid combinations absent** — see below |
| 6 stretch all three axes | 512 | complete (full 8³ grid) |

**Historical note, kept because it explains the shape of everything else.** This data arrived
broken twice. `test_files_for_diamond.zip` (8.10 GB) was truncated; byte-slicing salvaged 877
points and concluded family 4 had existed and was lost entirely. A OneDrive folder-zip
re-download (8.36 GB) was also truncated, reaching 30 points further into family 5. On
2026-07-16 the payload was downloaded **directly as a single file** instead of as a
server-generated folder-zip, and that copy is whole. Family 4 was always there — the archive
order is 1, 3, 2, 6, 5, **4**, so it sits past every truncation point. **If you ever re-fetch
this: download the file, not the folder.**

### Family 4 — 12 absent points

Each of the three plane pairs is missing the **same five** of its 9×9 grid:

| absent (γ₁, γ₂) | reading |
|---|---|
| (0, 0) | the origin — deliberate; the undeformed cell lives in families 1/2 |
| (−0.05, −0.05), (−0.05, +0.05), (+0.05, −0.05), (+0.05, +0.05) | **genuine 2-angle points, absent** |

Identical holes in all three pairs ⇒ systematic exclusion or an identically-failed batch, not
scattered crashes. 12 real points. Each is one PBE + one HSE06 job away (`03_…` #62). It is
worth noting that `|γ₁| = |γ₂| = 0.05` is exactly the diagonal of the sampled square at half
range — an oddly deliberate-looking hole.

### Family 5 — 24 absent combinations

The grid is a clean 6³ = 216 over γᵢ ∈ {±0.03, ±0.06, ±0.09}, but only **192** exist. The 24
absentees are structured, not random: the set is closed under g2↔g3 exchange, symmetric under
sign flip, and **none of them has |g2| = 0.09**.

**Whether they were never launched or launched and crashed is not determinable from here**,
and this is a property of the tooling, not a failure of investigation: the census extractor
(`extract-summary-csv.py`) silently skips any directory missing one of its four required
files, so "never run" and "ran and died" produce identical evidence. Both census CSVs list
exactly the 192 that exist.

### Duplicates: 1,179 rows are 1,131 shapes

24 single-skew shapes are each computed **three times** — once in `3-skew-one-plane`, twice in
`4-skew-two-planes` (each shear plane belongs to two of the three plane-pairs, so family 4's
zero-rows repeat it twice). All copies are **bit-identical**.

This is a live hazard, not a curiosity: **any naive fit or training set built from the
manifest gives those 24 shapes 3× weight.** The manifest's `duplicate_group` column marks all
72 affected rows. De-duplicate on it. See `02_…` §B6.

## 2. Design gaps (never sampled — not recoverable by re-transfer)

1. **No mixed normal+shear deformations.** This remains the highest-value gap, but the old
   phrasing was wrong and the correction matters. It is *not* true that "every sampled point
   is either pure-normal or pure-shear": in Green–Lagrange terms a simple shear at γ carries
   a normal component of γ²/2 (up to 0.005 in family 3, 0.010 in family 4, 0.008 in family 5).
   So the shear families **do** carry mixed content, and the full cubic fit is formally
   rank-complete including C144 and C155.
   **The conclusion survives the correction anyway.** That leakage lies on a constrained path
   (e1 = γ²/2 tied to e6 = γ) that is nearly degenerate with pure quartic shear terms, and the
   resulting C144/C155 are unusable — swinging −2709 → +6982 → −10890 GPa across fit windows
   against a literature ≈ −674. So: **C144/C155 are weakly and unusably determined**, and a
   dedicated mixed stretch+skew campaign is still the fix. If new runs are ever commissioned,
   this is where they go. See `03_…` #39.
   The subtle danger is that the leakage gives a fit *formal rank* in that sector — so a
   surrogate will look confident exactly where it is least trustworthy (`03_…` E5).
2. **Family 6 has no zero components** (εᵢ ∈ {±0.02…±0.08} only) — the axis planes of the
   (εx,εy,εz) cube are covered only by families 1/2; interior-to-face interpolation has a step
   in sampling density. **Family 4 does not share this flaw** — it includes γ = 0 rows, which
   is precisely why the shear sector has a proper axes ⊂ planes ⊂ interior nesting and the
   normal sector does not.
3. **Family 2 samples only uniax-x and biax-xy.** Correct exploitation of cubic symmetry — but
   unlike family 3 (which redundantly sampled all three shear planes and thereby provides a
   genuine noise estimate), family 2 has no redundancy check of its own.
4. **Grid steps differ by family** — 0.005 (families 2/3), 0.025 (family 4), 0.03 (family 5),
   0.02 (family 6). Family 4's finest step (0.025) sits **outside** the |γ| ≤ 0.02
   linear-response window, so **family 4 is not a linear-constants family**; its value is the
   anharmonic regime and the cross-plane structure. Use family 3 for C44.
5. **Single k-mesh, single ENCUT** across all 2,358 runs: internal data cannot bound k-point
   or basis-set convergence error (external convergence knowledge required). The Pulay
   measurement of §3.4 quantifies one consequence but is not a bound on the error.
6. **NBANDS = 8**: only 4 conduction bands; no high-energy spectrum.
7. Not-computed outputs: no LVTOT/LAECHG (no electrostatic-potential alignment → no absolute
   band-edge tracking), no LELF, no DFPT/phonon runs, no LOPTICS.

## 3. Systematic caveats (biases to correct or declare)

1. **Reference-state offset** (the big one, `02_…` §B3): strains are defined about the
   *experimental* a₀ = 3.567 Å. Measured equilibria differ: PBE V₀ = 11.4133 Å³ (reference is
   −0.6% in volume from PBE equilibrium); HSE06(0.27) V₀ = 11.1517 Å³ (reference +1.7%).
   **Measured directly at the reference volume**: **+19.7 kB at PBE** (compressive),
   **−86.3 kB at HSE06** (tensile, 8.6 GPa). All slope/curvature recipes must difference it
   out or carry an explicit linear term; all "at-equilibrium" claims must say *whose*
   equilibrium.
   **Quantified cost of ignoring it**: fitting elastic constants without a linear term biases
   **C44 by 15%** and C11 by 6% at |e| ≤ 0.006, and inflates the fit residual 60× (`02_…`
   §C2). This is the single most common way to get wrong numbers out of this dataset.
2. **Tuned functional**: AEXX = 0.27 (with HFSCREEN = 0.2). Gap-calibrated to diamond
   experiment (✔ reproduces 5.4383 vs 5.47 eV). It is *not* literature HSE06(0.25):
   comparisons must carry the α. Expect slightly stiffer elasticity (B₀ = 474 GPa vs 443
   experimental) — hybrid overbinding, aggravated by α-tuning.
3. **HSE at PBE geometry**: step 2 does not re-relax ions. For shear runs the internal
   coordinate is PBE-optimal, not HSE-optimal → HSE energies sit slightly above the true HSE
   surface (second-order-small, but a real bias for HSE-level C44/ζ); HSE forces in shear runs
   are *not* zero and are not an error.
4. **Pulay/stress bias, now measured.** ENCUT = 550 eV = 1.375 × ENMAX(400). Good, but not
   stress-converged luxury. The energy-route V₀ and the stress-route V₀ disagree by
   **+0.109% (PBE) / +0.122% (HSE06)** — i.e. **absolute stresses carry ≈ +5 kB of Pulay
   bias**. Both levels agree on the magnitude despite very different functionals, which is the
   evidence it is a basis-set effect of the shared cutoff rather than something
   level-specific. **Prefer energy-route fits for absolute quantities, stress-route for
   slopes** (offsets and bias cancel in differences). See `02_…` §C6.
5. **Mesh-limited gap**: CBM falls between mesh points; absolute indirect gap biased high by
   up to ~0.05–0.1 eV. Gap *derivatives* across strain are much safer.
6. **Finite-strain semantics**: families 3/4/5 are *simple* shears (rotation included); beyond
   |γ| ≈ 0.02 use Green–Lagrange strain or fit along the sampled ray (`02_…` §B2). Family 4
   compounds this: two composed simple shears make the three plane pairs **inequivalent at
   finite γ** (`02_…` §B7). Their spread is physics, not noise.
7. **Smearing**: ISMEAR = 0, SIGMA = 0.01 eV — negligible for an insulator; E0 vs F
   differences are < 0.1 meV (ignorable).

## 4. File-level quirks and provenance smells

- **The `PREC = Accuratei` typo is not universal, and it is provably harmless.** Families 1,
  3, 5 carry the typo; families 2, 4, 6 spell `Accurate` correctly. Proof of inertness: a
  family-3 point and a family-4 point at the same geometry differ in *only* the PREC spelling
  and a POSCAR comment, and produce **bit-identical energies**. VASP prefix-matches it.
  Always read parameters from the vasprun echo anyway.
- **The analysis scripts were recycled from a gallium-oxide project.** `build-hse06-runs.sh`
  still reads `# Enter the folder (e.g., MgGa2O4_distorted)`, and that script *generates* each
  HSE06 INCAR. This is a provenance smell rather than a known defect — the settings that
  matter were re-derived from the vasprun echo and check out — but it is why `01_…` §2 tells
  you to trust the echo over the INCAR text.
- **`extract-summary-csv.py` is misnamed in the original** (`build_Vol_opt` — it builds
  nothing; it is a pymatgen extractor). It is also interactive (prompts for which sub-run to
  scan) and **silently skips** directories missing any of vasprun/OUTCAR/POTCAR/POSCAR, which
  is why census absence is ambiguous (§1).
- **`collect-volume-sweep-results.sh` and `build-volume-sweep-runs.sh` appear in families
  2–6** where no volume points exist — leftovers from the family-1 template. Harmless, but do
  not read them as evidence of volume sampling in those families.
- Family 1's POSCAR comment says `Diamond Supercell 2x2x2` in places and family 3's says
  `Diamond 2x2x2 FCC` — **both are misleading**. Every cell in this dataset is the 2-atom
  primitive cell. VASP ignores comment lines; so should you.
- A stray vim swap file (`.build_Vol_opt.swp`) was present in family 3 and has been deleted.
- **POTCAR (licensed VASP material) is present in every run directory**, renamed
  `pseudopotential-LICENSED-DO-NOT-REDISTRIBUTE.txt` — internal use only, never
  publish/redistribute/commit to public repos. This is why this dataset lives on `/Pool` and
  not inside the n-Op git repository, whose remote is public.
- Wavefunction files are binary and build-specific ("complex" VASP 6.2.0 build) — useful only
  as restart seeds on a compatible build; not parseable data.
- INCAR comments are Portuguese; the submit scripts mail `nathanrabelo@ufv.br` (Universidade
  Federal de Viçosa). Provenance flavour, no effect.
- **Two strays that are NOT part of this dataset and must not be ingested:**
  1. The original zip's loose `CHGCAR` (58.7 MB) — an "H2 dimer in a box" spin-polarized
     tutorial artifact. Not diamond.
  2. `converged_without_stress.zip` (395 MB) — a **64-atom 2×2×2 diamond supercell** with
     incompatible settings (`ENCUT = 460` not 550, `SIGMA = 0.1` not 0.01, `ISPIN = 2`
     spin-polarized, which is wrong for diamond). Different cell, different basis, different
     physics. Its own truncation is a OneDrive `WebMeTAException`, not a VASP error. It is
     *not* the home of family 4's 12 missing points.

## 5. Fit-for-purpose vs the program

What this dataset **feeds well**: the `h`-slot (lattice) dependence of energy/stress at fixed
composition — B7 mechanics (full cubic elastic tensor + anharmonic extensions), B8 EOS/
cold-curve thermodynamics, B1 gap-vs-strain at a gap-calibrated hybrid level, B10 stability
margins, the bare→dressed (PBE→HSE) pairs over 1,131 distinct shapes, and a per-run
consistency battery for cert-style import validation — now including a genuine **symmetry
null** (`02_…` §C5), which is a stronger class of check than anything the dataset previously
offered.

What it **cannot feed** (do not stretch it): phonon dispersions/thermal transport (B2),
carrier transport (B3), defects (B4), surfaces (B5), interfaces (B6), non-equilibrium/
high-field (B9), degradation kinetics (B11), any finite-temperature observable at data-grade,
and polar/piezo channels (vacuously zero in diamond — usable only as symmetry null-checks).
It exercises the deformation seam of the architecture deeply and nothing else.

## 6. Trust-level summary

| Class | Trust | Basis |
|---|---|---|
| E(V), EOS parameters, per level | high | ✔ sub-meV BM3 residuals; literature match; stress-route V₀ agrees to 0.11% |
| Linear elastic constants **with the linear term** | high | ✔ RMS 0.027–0.129 meV; C11−C12 = 933 vs 955 expt; B reconciles with EOS B₀ via B₀′·ΔP |
| Linear elastic constants **without** it | **do not use** | ✔ 15% error on C44, 60× worse residual |
| Kleinman ζ, clamped/relaxed C44 split, ω_TO(Γ) | high (PBE), medium (HSE, §3.3) | ✔ ζ = 0.0976, flat in γ; ω ≈ 1307 cm⁻¹ vs 1290–1300 PBE lit. |
| Gap *changes* under strain, deformation potentials | high | mesh bias cancels in differences |
| Absolute gaps | medium | mesh-limited CBM (+0.05–0.1 eV); α-tuned on purpose |
| Absolute stresses | medium | ✔ Pulay bias measured at ≈ +5 kB; reference offset correctable |
| C456 | medium | ✔ stable ≈ −1135 GPa across all fit windows; family 5 only |
| C111, C112, C123 | medium-low | fitting-protocol sensitive; C111 diverges as the window tightens |
| 4th-order shear cross terms | low-medium | ✔ ≈ −360 GPa; needs family 4 to separate from C456 |
| **C144, C155** | **none — do not quote** | ✔ formally rank-complete, numerically unusable (swings −2709 → +6982 → −10890) |
| T4 thermal-model outputs | trend-grade | Debye assumption, declared model |
| Anything in `03_…` D-list | none | not in the data |

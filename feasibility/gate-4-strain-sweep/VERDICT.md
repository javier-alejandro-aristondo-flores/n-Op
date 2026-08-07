# Gate 4 — the strain sweep: is there electronic response beyond textbook theory?

**Result: PROCEED, REFRAMED — the second row, and the prize is not where the row assumed.**

No row of the pre-registered table fires cleanly. That is stated first because the gate
asked for a row and the honest answer is that the measurement landed between two of them,
passing every scalar clause of row 3 and failing its density-of-states clause on both
halves. The reading below says which row governs and why.

## Verdict

The sweep reaches **14.85% Green–Lagrange strain**, so the first question — whether this
corpus even samples the nonlinear regime — is answered decisively yes, and the fourth
decision row is dead. The response is enormous: the PBE indirect gap runs from **4.81 eV
down to 0.441 eV**, a factor of eleven, and in 44 of 1,131 shapes the conduction minimum
moves to Γ and diamond becomes **direct-gap**. A linear model of that is worthless — M1
scores 632 meV against the 638 meV no-information anchor, an improvement of 0.9%.

**But the sixty-year-old theory is not worthless, and it is the finding.** Deformation-potential
theory with valley `min` and Bir–Pikus degeneracy splitting — five parameters, all of them
published physics — cuts the residual to **115.8 meV**, capturing 82% of the variation. It
is also, by a wide margin, the **best extrapolator in the ladder**: trained on the axis and
skew families and tested on the 512-cell general-stretch family it scores **69.7 meV**,
against 884.8 meV for gradient-boosted trees and 33,894 meV for a generic quadratic. A
model that reproduces the whole sweep and then fails to leave it is not a model of the
physics; M2 leaves it.

**Nothing cheap reaches the noise floor, and nothing cheap beats the physics.** The decision
variable — M2's grouped-CV residual on the indirect gap over the top strain quartile — is
**R2 = 148.9 meV**, 7.4× the gate's 20 meV threshold and 14,000× the measured noise. The
6-variable regressor ceiling M4 ties M2 on interpolation (107.3 vs 115.8 meV) and loses on
every honest split. So there *is* residual structure beyond textbook theory, it is real,
and it is worth about 116 meV — which is **2.7% of the observable's 4.36 eV span**.

**Row 3's density-of-states clause fails, and the reason matters more than the failure.**
Under cross-validation a quadratic-invariant map reaches **12.7%**, below the 15% the row
requires, and a nearest-neighbor lookup reaches **5.3%**. That last number nearly ended
this gate as a kill — until the structured splits showed it measures the grid, not the
curve. Off the sampled region every rung collapses together: kNN 6.4% → **26.3%**, the
quadratic map 13.0% → **24.6%**, and the linear map to **120%**, worse than predicting
zero, against a 29.5% no-information anchor. Interpolating a dense grid is easy and tells
an operator nothing.

The row also asks *where* the residual sits, naming gap-edge reshaping as signal an
operator could own and uniform smear as noise. It is **not at the gap edges**: 24.7% of the
residual lies in the deep valence below −10 eV and 40.9% in the conduction region above
+7 eV, against 2.5% in the gap and 8.5% at the conduction edge.

**Step 5 returned the unambiguous result, exactly as designed.** The PBE→HSE06 correction
**drifts with strain, by five orders of magnitude more than noise**.

## The citable number

Applying diamond's equilibrium-geometry hybrid gap correction to strained diamond
mis-corrects by **47.5 meV on average and 201 meV at worst**. The correction falls at
**−9.1 meV per 1% of strain magnitude**, from 1.292 eV extrapolated to zero strain to
1.201 eV at ‖E‖ = 0.10, with a **325 meV total spread** across the 1,131 shapes — against a
noise floor of **0.002 meV**, a ratio of 1.6 × 10⁵.

This is standard practice being quantified for the first time: equilibrium scissor and
stretch corrections are routinely applied to strained structures. Second-order strain
invariants explain only **R² = 0.37** of the drift, so it is structured but not simply, and
it is not a volume effect — trace alone gives R² = 0.15, deviator alone 0.14.

Gate 2's coefficients, measured on 64-atom defect supercells at one geometry, are
reproduced in shape on a 2-atom primitive cell across 1,131 geometries:

| coefficient | Gate 2, one geometry | here, mean ± sd | range |
|---|---|---|---|
| occupied slope | ~0.10 | **0.1102 ± 0.0027** | 0.018 |
| unoccupied slope | ~0.07 | **0.0941 ± 0.0059** | 0.032 |
| unoccupied intercept | ~0.84 | **0.9045 ± 0.0595** | 0.293 |
| indirect-gap correction | — | **1.2231 ± 0.0597 eV** | 0.325 |

## Numbers

| Quantity | Value |
|---|---|
| Distortion points / physically distinct | **1,179 / 1,131** |
| Points with a readable run at **both** functionals | **1,179 of 1,179 (100%)**, 0 read failures |
| k-mesh | Γ-centered **7×7×7**, **172** points = (343+1)/2, time reversal only (ISYM = 0) |
| Mesh identical across runs, modulo ±k | **verified**, 172 classes, 0 mismatches in 300 sampled |
| Spin | **ISPIN = 1** — `# ISPIN = 2` is commented out in every INCAR |
| Bands | NBANDS = 8 (4 occupied); **8 family-1 PBE runs carry 96** |
| Max strain ‖E‖ / above 5% / above 10% | **0.1485** / 78.4% / 21.3% |
| PBE equilibrium | V₀ **11.4133 Å³**, a₀ **3.5740 Å**, B₀ **434.2 GPa**, B₀′ 3.66, residual 0.15 meV |
| HSE06(0.27) equilibrium | V₀ **11.1517 Å³**, a₀ **3.5465 Å**, B₀ **473.8 GPa**, B₀′ 3.59, residual 0.17 meV |
| Triplicates | **bit-identical physics** — largest eigenvalue difference within any group **0.000 eV** |
| Symmetry-twin orbits / points | **213 orbits**, 996 points, sizes 3/4/6/8 |
| **σ_noise, indirect gap** | **0.0105 meV** rms, 0.035 meV worst |
| Operative threshold σ = max(3σ_noise, 20 meV) | **20 meV** — the gate's floor, 600× the measured noise |
| Free check: Γ triplet under isotropic strain | **0.002 meV** (vs 3064 meV anisotropic) |
| Free check: valley splitting under isotropic strain | **0.0000 meV** |
| PBE indirect gap range | **0.441 – 4.806 eV** |
| Shapes with conduction minimum at Γ (direct gap) | **44 of 1,131** |
| Δ-valley splitting | median **1.14 eV**, max **3.98 eV** |
| Metallic / partially occupied points | **0** |

### Scalar ladder — PBE indirect gap, grouped CV, MAE in meV

| model | params | all | top quartile | worst |
|---|---|---:|---:|---:|
| M0 constant | 1 | 638.4 | 947.6 | 2552.0 |
| M1 hydrostatic linear | 2 | 632.2 | 900.2 | 2295.9 |
| **M2 deformation-potential** | **5** | **115.8** | **148.9** | 1075.2 |
| M3b quadratic invariants | 8 | 285.0 | 362.8 | 1573.6 |
| M3 generic quadratic | 28 | 294.5 | 344.1 | 1852.4 |
| **M4 gradient-boosted trees** | — | **107.3** | 172.7 | 1283.2 |

HSE06 behaves identically (M2 116.6, M4 111.0). The valence splitting at Γ is the one
observable where M4 clearly beats the physics (57.6 vs 107.2 meV).

### Structured splits — PBE indirect gap, MAE in meV

| split | M0 | M1 | M2 | M3b | M3 | M4 |
|---|---:|---:|---:|---:|---:|---:|
| small strain → large strain | 945 | 993 | **158** | 764 | 758 | 515 |
| axis+skew families → general stretch | 906 | 945 | **70** | 507 | 33894 | 885 |

### Density-of-states ladder — PBE, σ = 0.3 eV, residual as % of curve integral

| model | grouped CV | complete window | small→large | families→general |
|---|---:|---:|---:|---:|
| L0 equilibrium curve | 33.8% | 29.3% | 41.3% | 43.0% |
| L0mean training mean | 20.8% | 19.7% | 26.0% | 29.5% |
| L1 linear | 18.9% | 17.7% | 26.7% | **120.0%** |
| L2 quadratic invariants | **12.7%** | 11.7% | 32.4% | 24.6% |
| L3 nearest neighbor | **5.3%** | 4.8% | 16.3% | 26.3% |

HSE06 tracks PBE throughout (L2 13.1%, L3 5.5%).

## The leakage check, and a difference from Gate 3

Cross-validation groups by symmetry orbit, so a shape and its octahedral images share a
fold. Gate 3 found grouping mattered. **Here it does not**: grouped and plain k-fold agree
to 0.1 meV for M2 (115.83 vs 115.94) and 2.6 meV for M4 (107.25 vs 104.70). The grouping is
still correct and still reported, but no model was exploiting symmetry-image leakage —
which is itself mild evidence that the ladder is measuring physics rather than memorizing.

## Corrections made during the analysis

Four, all found by controls rather than by inspection.

- **A checksum is not a rerun.** The triplicate test on raw file hashes said the copies
  *differ* — 72 of 144 EIGENVAL comparisons. Comparing the parsed numbers instead gives a
  largest difference of exactly **0 eV**. The HSE INCAR sets `System = <directory name>`, so
  the copies carry different name strings in line 5 and identical physics in every other
  line. The dataset's read-me was right; the instrument was wrong.
- **Character matching is ill-posed in a two-atom all-carbon cell.** Assigning PBE to HSE
  bands by lm-character overlap alone drove the fitted unoccupied intercept to **−14.7 eV**,
  because an occupied and an unoccupied state can carry near-identical s/p characters and
  the assignment cheerfully swapped them across the gap. Gate 2's combined cost (energy
  difference plus λ = 2.0 eV × character mismatch) resolves it, and under that cost index
  matching changes the coefficients by at most **2.2 × 10⁻⁴** — validated, not assumed.
- **The degeneracy check was specified wrongly and passed anyway.** Testing the Γ triplet on
  all *shear-free* cells reported a 3064 meV "splitting". Shear-free is not cubic: a cell
  stretched unequally along x, y, z splits the triplet through the tetragonal deformation
  potential b. Restricted to **isotropic** strain, where symmetry actually protects the
  degeneracy, the splitting is **0.002 meV**.
- **A 1e-12 isotropy tolerance rejected 39 of 47 isotropic cells**, because family 1's
  POSCARs use an a₁-along-x frame whose residual shear survives at 1e-11 — the trap the
  dataset documents.

## The sampling artifact, reported not smoothed

The conduction minimum can hop between mesh points as strain deforms the bands. Measured on
genuine one-parameter sequences rather than a strain-magnitude sort:

| sequence | n | hops | median \|2nd difference\| | at the hop |
|---|---:|---:|---:|---:|
| volume sweep | 47 | **0** | 0.049 meV | — |
| skew x→y, x→z, y→z | 40 each | **0** | 2.47 meV | — |
| uniaxial x | 40 | 1 | 0.87 meV | **76.4 meV** |
| biaxial xy | 40 | 1 | 2.27 meV | **151.4 meV** |

So hopping is rare — two hops across 240 sequenced points — but where it happens it leaves a
kink of 76–151 meV, four to eight times the 20 meV threshold. Any fit reporting a residual
near 100 meV on those two families is partly fitting the mesh.

**Related caveat on the direct-gap finding.** The 44 shapes whose minimum sits at Γ are real
on this mesh, and their indirect gap equals their Γ direct gap to 0.00 eV. But the true Δ
minimum lies near 0.76 Γ→X while the mesh's nearest point is at 0.857, so the sampled Δ
energy is an overestimate and the indirect→direct crossover strain would move on a finer
mesh. The crossover is real; its location is mesh-limited.

## Recommendation

**Proceed, on row 2's terms, and do not claim row 3's.** Specifically:

1. **The operator's scalar case is thin and should not be the headline.** Textbook theory
   from the 1950s reaches 116 meV; nothing tested beats it, and the leftover is 2.7% of the
   observable's range. Any paper leading with strain→gap accuracy will meet Bardeen–Shockley
   and Bir–Pikus in review, and correctly.

2. **The defensible operator claim is off-grid, function-valued prediction.** That is the one
   place where every cheap model fails together (16–32%) and an operator has room. This gate
   cannot show it will succeed there — only that the competition does not.

3. **What should be published from this gate, immediately, is Step 5.** It is complete, it is
   five orders of magnitude above noise, it needs no operator, and it corrects standard
   practice: **equilibrium hybrid corrections mis-correct strained diamond by 9.1 meV per
   percent strain, 47.5 meV on average and 201 meV at worst.** Alongside it, the deformation
   potentials fitted here at **both** PBE and HSE06 are, to our knowledge, not in the
   literature at the hybrid level.

4. **Do not build on the density-of-states residual as evidence of learnable structure.** It
   concentrates in the deep valence and high conduction, not at the gap edges, which is the
   shape the gate named as noise rather than signal.

The honest summary across four gates: the density target died; the eigenvalue target
survived as an energy stretch four free parameters capture; the configuration-specific
remainder proved unpredictable; and now the strain target shows large, genuine nonlinearity
that sixty-year-old theory already explains four-fifths of. The case for an operator has
not strengthened. What has strengthened, twice now, is the case for publishing the cheap
correction as the deliverable.

## Files

- `VERDICT.md` — this document
- `plot_gate4_summary.png` — the four headline panels
- `observables.csv` — 1,179 points, O1–O4 at both functionals, strains, volumes
- `spectra.npz` — canonicalized eigenvalues (1179 × 172 × 8, both functionals), weights, k-grid
- `step0_runs.csv`, `step0_summary.json` — inventory and coverage
- `step1_noise.csv`, `step1_noise.json`, `step1_copies.csv` — noise floor, orbit structure
- `step3_ladder.csv/.json`, `step3_residual_vs_strain.csv` — the scalar ladder
- `step4_dos.json`, `step4_residual_vs_strain_*.csv`, `step4_profile_*.npz` — the DOS ladder
- `step4b_splits_*.csv` — the DOS structured splits
- `step5_coefficients.csv`, `step5_drift_vs_strain.csv`, `step5_noise.json` — the drift
- `file_manifest.json`, `digests.json` — every member of every archive, with checksums

Scripts: `extract_sweep.py`, `sweep_read.py`, `build_table.py`, `step0_inventory.py`,
`step1_noise.py`, `step2_report.py`, `step3_ladder.py`, `step4_dos.py`,
`step4b_extrapolate.py`, `step5_drift.py`, `plots.py`.

## Method notes

- Strain is Green–Lagrange, referred to the experimental a₀ = 3.567 Å, computed by the
  n-Op repository's own `physics.formulas.elastic.green_lagrange_voigt` — the routine whose
  transpose convention was pinned down by reproducing the dataset's published C44 (570.0
  against 570.5 GPa). Reusing it rather than reimplementing it is why the family-3 second-order
  normal components come out at γ²/2 = 0.005 exactly as the dataset predicts.
- The equation-of-state fit reuses `physics.formulas.eos.fit_energy_volume` and reproduces
  the dataset's published PBE fit to all four digits — an end-to-end check that the read
  path, the scale rule and the units are right before any new number is trusted.
- **Symmetry orbits are computed, not assumed**: two shapes are twins exactly when their
  strain tensors are related by one of the 48 octahedral operations, which is a statement
  about the crystal rather than about how the sweep named its families.
- POSCAR's negative scale is a target for |det A|, not a multiplier. Family 1 uses it
  exclusively.
- The density of states is built from eigenvalues with k-point weights, two electrons per
  band, Gaussian σ = 0.3 eV on a −25…+15 eV grid referred to each run's own valence maximum.
  The 8-band truncation costs **0.00%** inside that window: on the eight 96-band runs, band 9
  begins at +18.4 eV above the maximum, outside the window entirely. The metric is reported
  additionally on the sub-window (≤ +8.36 eV) where the 8-band set is provably complete at
  every sampled shape.
- All statistics are k-point-weighted. Ridge regularization is chosen by an inner grouped
  CV inside each training fold.
- All outputs under `/Pool/`, asserted at the top of every script. **No POTCAR was copied
  anywhere** — the extractor denies it by assertion, not by omission, and skipped 2,364 of
  them. No raw run content left `/Pool`.

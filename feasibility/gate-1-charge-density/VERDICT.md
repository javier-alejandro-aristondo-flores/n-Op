# PBE → HSE06 charge density difference — go/no-go verdict

**Result: STOP. Do not build the operator.**

## Verdict

Across 81 defect configurations that share an identical geometry between their PBE and
HSE06 runs, the normalized mean absolute error between the two charge densities is
**0.784% ± 0.030%** (range 0.751–0.952%; clean subset 0.784% ± 0.030%, n=54). That places
the identity baseline inside the marginal 0.5–2% band, where the decision rule permits
proceeding *only if the spread across configurations is a substantial fraction of the
mean*. It is not: the standard deviation is **3.8% of the mean**, and pure diamond with no
dopant at all sits at 0.775%, statistically indistinguishable from the doped population.
The correction is therefore a near-constant property of the carbon host rather than
something that varies with the defect being modeled. Three independent checks agree.
Spatially, only **1.8% of the integrated |Δρ| lies within 2 Å of the dopant against 3.4% of
the cell volume** (enrichment 0.55) — the defect region carries *less* than its share of the
difference, so there is no localized residual for an operator to specialize on. A
one-dimensional lookup table on the local PBE density, fitted once on pure diamond and
transferred untouched, already removes about a quarter of |Δρ| and drops the error to
**0.52–0.65%**, which is at ChargE3Net's published accuracy (0.523%) — meaning a neural
operator would have to beat a trivial scalar map to justify itself, with under 0.55% of
total signal left to win. The descriptor regression does *not* trigger the independent
override (R² = 0.161 against six dopant descriptors, best pair 0.100), but that is 16% of a
quantity that is itself negligible, not evidence of learnable structure. The measurement is
real and not numerical noise — two independent PBE runs of pure diamond differ by 0.108%,
so the functional signal is ~7× the noise floor — but real and small is still small. This
is the expected physics: a screened hybrid changes eigenvalues in a wide-gap covalent
insulator far more than it changes the ground-state density, and in this same dataset the
band gap moves 4.11 → 5.28 eV (+28%) while the density moves 0.78%.

## Numbers

| Quantity | Value |
|---|---|
| Candidate configurations with both PBE and HSE06 | **97** (not ~58 as the prior index suggested) |
| Passed the geometry gate (`same-geometry`) | **82** |
| Failed the gate (`different-geometry`) | **15** — all HSE06 `NSW=40` |
| Excluded as a data defect | **1** (Zr) |
| **Used for the measurement** | **81** |
| Mean NMAE, full set (n=81) | **0.7841%** |
| Standard deviation | **0.0302%** (sd/mean = 0.038) |
| Min / max | 0.7512% / 0.9516% |
| Mean NMAE, clean subset (n=54) | **0.7838%** ± 0.0302% |
| Mean NMAE, spin-suspect subset (n=27) | 0.7848% ± 0.0306% |
| Pure diamond, no dopant | **0.7749%** |
| Grid dimensions | 80×80×80 for **every** run — no interpolation required |
| Electron-count check | **PASS**, max relative error 1.65 × 10⁻⁷ |
| Cell volume difference within a pair | **0.000 Å³** for all 97 pairs |
| Signal within 2 Å of dopant | 1.8% of |Δρ| vs 3.4% of volume (enrichment 0.55) |
| Descriptor regression R² (6 descriptors) | **0.161** — override not triggered |
| Pointwise lookup residual | 0.52–0.65% NMAE (removes ~25% of |Δρ|) |
| Same-functional noise floor (PBE vs PBE) | 0.108% |

## Geometry gate detail

Displacement between the PBE and HSE06 final structures separates cleanly into two
populations, so the 0.01 Å threshold is not splitting a continuum:

- **62 pairs** at *exactly* zero displacement (HSE06 `NSW=0`, single-point on the PBE geometry)
- **20 pairs** in 1×10⁻³ – 9×10⁻³ Å (HSE06 `NSW=40` that relaxed back to the PBE geometry)
- **— gap —** next value is 1.33×10⁻² Å
- **15 pairs** at 0.013 – 0.759 Å → `different-geometry`, excluded

The excluded 15 are the large, strongly relaxing dopants: Fr (0.759 Å), Ra (0.525), Ca
(0.259), Sr (0.188), Y, Sc, Rh, Rb, At, Ni, Pd, Zn and three others. All are HSE06 `NSW=40`.
Reported separately as required; 15/97 is a modest fraction and does not change the framing.

## Data defect found

`single_defects_new-only-HSE06/Transition-Metals/Zr/hse06` is a **byte-for-byte duplicate of
the PBE run**: identical CHGCAR md5 (`9f5c3ec6…`) and an identical OSZICAR final energy
(−567.66828 eV, 17 ionic steps), despite carrying `LHFCALC = .TRUE.` in its INCAR. No
self-consistent HSE06 density was ever written for Zr. Excluded from all statistics.

## Recommendation

Do not proceed to architecture work on a PBE → HSE06 density operator. The trivial identity
baseline is already at 0.784%, a one-dimensional lookup takes it to ~0.55%, and the total
available signal is smaller than the intrinsic error of published charge-density models.

The transferable PBE → HSE06 signal in this corpus is in the **eigenvalues, not the
density**: the same 82 configurations show a band-gap shift of order 1.2 eV (+28%) against a
sub-1% density shift. A PBE → HSE06 defect-level / gap corrector trained on `EIGENVAL` and
`PROCAR` would have a target roughly thirty times larger relative to its baseline, and the
data to support it is already in this corpus.

## Files

- `pairs_geometry.csv` — all 97 pairs, geometry classification, INCAR settings, quality flags
- `unpaired_runs.csv` — the 5 runs with no counterpart
- `nmae_per_config.csv` — the per-configuration table (Step 3)
- `summary.json` — machine-readable summary of every statistic quoted here
- `plot_a_nmae_histogram.png` — distribution of per-configuration NMAE
- `plot_b_radial_profile.png` — radial profile of |Δρ| around the dopant
- `plot_c_descriptor_regression.png` — the negative control
- `plot_d_pointwise_control.png` — stronger control: pure-diamond pointwise map transferred
- `radial_profiles.json` — per-configuration radial profiles
- `chgcar_locations.json` — which archive holds each CHGCAR

## Method notes

- Densities parsed with `pymatgen.io.vasp.outputs.Chgcar` (2026.7.31) as specified;
  cross-validated against an independent parser — both recover 257.0000 electrons for
  N-doped diamond (63 C × 4 + N × 5), agreeing to 7 significant figures.
- Raw CHGCAR values are ρ·V, so their grid mean *is* the cell electron count; this is what
  the sanity check tests. Volumes were verified identical within every pair, so the
  normalization cancels — verified, not assumed.
- Spin-polarized files: `data["total"]` (total density) used for the metric;
  `data["diff"]` (spin density) parsed but not used, per spec.
- Streamed one configuration at a time from the zip archives; never more than two densities
  resident. Temporary extractions were written to `/Pool` and deleted.
- Functional was determined from each INCAR's `LHFCALC`, never from directory names —
  several run directories are named `sigma00001`, `config2` or `sigma-0.0001`.
- All outputs written under `/Pool/`, asserted at the top of each script rather than left to
  `.gitignore`. No raw run-directory content, and in particular no POTCAR, was copied
  anywhere else.

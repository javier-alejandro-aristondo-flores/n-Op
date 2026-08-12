# PBE → HSE06 eigenvalue correction — go/no-go verdict

**Result: PROCEED — but not for the reason the hypothesis proposed.**

## Verdict

The correction is emphatically **not** a rigid scissor shift. Across 81 clean pairs and
255,568 matched states, a two-parameter model (one constant for occupied states, one for
unoccupied, fitted once globally) leaves a residual mean absolute error of **0.759 eV on the
2,883 states lying inside the gap** — three times the 0.25 eV proceed threshold, and
actually *worse* than applying no correction at all (0.690 eV), because the globally fitted
occupied constant is dominated by deep valence states and is badly wrong for defect levels.
Refitting those same two constants using only in-gap states — a reading more favorable to
the rigid model — still leaves **0.374 eV**. The kill condition is not met under either
reading, and the clean subset (0.674 eV, n=2007) agrees with the full set. The reason is
visible directly: the shift is a near-linear function of energy, roughly 0.10·E on the
occupied side and 0.07·E + 0.84 on the unoccupied side, so the valence band is *stretched*
by about 10% rather than held fixed while the conduction band is lifted. Consistent with
this, the density of states genuinely deforms rather than translating: after the best rigid
two-constant shift, **32.7% of the HSE06 curve's integral remains unmatched** at 0.3 eV
broadening (23.0% at 0.5 eV), so a curve-to-curve operator would be learning a real
function-to-function map, not a translation. **However, the proposed mechanism is not
supported.** Once the occupied/unoccupied confound is removed, the Model-2 residual shows no
usable correlation with either the inverse participation ratio or the weight on the dopant
atoms — R² ≤ 0.015 in every channel. Localization does not predict which states deviate, so
the "free predictive feature already sitting in files you have" does not materialize. What
*is* learnable is the per-configuration offset: fitting two constants separately per
configuration drops the in-gap residual from 0.374 eV to **0.158 eV**, so roughly 0.22 eV of
the correction is configuration-specific structure a model could capture, above an
irreducible within-configuration scatter of 0.158 eV. Proceed, but scope the architecture
around predicting a per-configuration correction, and note that a four-parameter
linear-in-energy formula already reaches 0.340 eV on in-gap states with no model at all.

## Numbers

| Quantity | Value |
|---|---|
| Pairs with both EIGENVAL and PROCAR | **81 of 81** (82 same-geometry, minus the corrupt Zr duplicate) |
| k-point sampling identical within pair | **81 / 81** |
| EIGENVAL vs PROCAR energy agreement | 5 × 10⁻⁷ eV |
| States matched | **255,568** |
| Reordered (band n ↔ band m, m≠n) | 22.8% — median character overlap 0.978, so genuine |
| Ambiguous (overlap < 0.70) | **543 of 256,000 = 0.21%** |
| Host gap, resolved configs (n=62) | PBE **4.60 eV**, HSE06 **5.74 eV**, opening **1.21 eV** |
| Host gap unresolved → excluded from in-gap | **19 of 81 configs** |
| **In-gap residual after Model 2, global fit** | **0.759 eV** |
| In-gap residual after Model 2, refit on in-gap | **0.374 eV** |
| In-gap, clean subset / spin-suspect | 0.674 eV (n=2007) / 0.954 eV (n=876) |
| Localization correlation (confound-free) | **R² ≤ 0.015** |
| DOS residual after best rigid shift (σ=0.3 eV) | **32.7%** of the curve integral |
| Per-configuration headroom (in-gap) | 0.374 → **0.158 eV** |

### Model ladder — residual MAE (eV), Model 2 = two parameters fitted once on all states

| group | n | M0 none | M1 scissor | M2 two const | M2L linear | M3 per-config |
|---|---:|---:|---:|---:|---:|---:|
| all states | 255,568 | 1.116 | 0.701 | 0.412 | **0.184** | 0.341 |
| deep occupied | 119,878 | 1.176 | 1.176 | 0.505 | 0.181 | 0.476 |
| band edges | 93,809 | 0.904 | 0.277 | 0.339 | 0.162 | 0.242 |
| **in gap** | **2,883** | **0.690** | **0.455** | **0.759** | **0.347** | 0.651 |
| high unoccupied | 38,998 | 1.474 | 0.280 | 0.280 | 0.236 | 0.143 |

**Model-1 sanity check passes:** on the states it can actually move (unoccupied), Model 1
cuts the error from 1.415 to 0.221 eV — an 84% reduction. Model 1 leaves deep occupied
states untouched by construction, which is why the all-states improvement looks smaller.

## Step 1 — the alignment control fails, and it is not an alignment error

Deep occupied states (more than 15 eV below the host VBM) move by **1.84 eV** on average,
above the 1 eV threshold the brief sets for declaring the alignment broken. It was
investigated rather than accepted:

- **A constant-offset error cannot survive VBM alignment** — it is absorbed exactly. Any
  residual motion is therefore energy-dependent, which no choice of zero can fix.
- The magnitude matches a known physical effect. For pure diamond the occupied bandwidth
  goes from **21.34 eV (PBE) to 23.40 eV (HSE06)**, a widening of 2.06 eV, in line with the
  literature figure of roughly 2 eV for hybrid functionals in diamond.
- The premise of the control — that deep states are "core-like" — does not hold here. In a
  PAW calculation the deepest bands in this window are C 2s-derived *valence* bands, which
  genuinely rebuild under exact exchange. True core states are frozen in the PAW dataset and
  never appear in EIGENVAL.

The alignment is therefore sound and the control's assumption is what fails. Recorded as a
caveat rather than patched over.

## A correction made during the analysis

The first pass anchored the zero on the *highest occupied state* and identified host band
edges by inverse participation ratio. Both were wrong for defect cells:

- For nitrogen the highest occupied state **is** the defect level (13% of its weight on N),
  so the zero was pinned to a state that itself shifts.
- An IPR cut let a defect state with 8% dopant weight pass as a band edge, collapsing
  nitrogen's apparent host gap to **0.274 eV** instead of ~4 eV, and yielding *zero* in-gap
  states for the textbook deep donor in diamond.

Both are fixed by classifying states with **dopant weight** (host-like if below 2× the bulk
share, n_dopants/64) and anchoring on the highest occupied host-like state. The threshold
was calibrated against the known pure-diamond gaps: it returns 4.60 / 5.74 eV against 4.11 /
5.28 eV for the undoped cell, with the gap *opening* — the physically meaningful quantity —
reproduced to 0.04 eV (1.21 vs 1.17 eV). Configurations whose host gap still fails to
resolve (19 of 81) are excluded from the in-gap group and reported, not silently included.

## Step 4 — mechanism test: negative

The hypothesis predicted that self-interaction error makes localized states shift more, so
the residual should track localization. It does not.

| measure | channel | r | R² |
|---|---|---:|---:|
| inverse participation ratio | in-gap occupied | +0.124 | 0.015 |
| inverse participation ratio | in-gap unoccupied | +0.082 | 0.007 |
| dopant weight | in-gap occupied | +0.057 | 0.003 |
| dopant weight | in-gap unoccupied | −0.029 | 0.001 |

A raw correlation of r = −0.30 appears if the globally fitted Model 2 is used without
splitting by occupancy, but that is an artifact: in-gap occupied states are both more
localized *and* handed a badly wrong constant, so occupancy masquerades as a localization
trend. Split by occupancy and refit fairly, the effect vanishes. The signs are not even
consistent between measures. **There is no usable localization feature in this corpus.**

## Step 5 — the DOS deforms

Residual difference from the HSE06 curve, as a percentage of its integral:

| broadening | no shift | rigid scissor | two constants | per-config |
|---|---:|---:|---:|---:|
| σ = 0.1 eV | 74.8% | 61.6% | 56.0% | 53.1% |
| σ = 0.3 eV | 54.1% | 40.4% | **32.7%** | 31.0% |
| σ = 0.5 eV | 43.4% | 30.8% | **23.0%** | 21.7% |

The metric depends on broadening — with 8 k-points the spectrum is a comb of spikes at small
σ — so σ = 0.3 eV is quoted as the realistic figure. Under any choice, roughly a quarter to a
third of the curve is not recovered by translating it. **The curve deforms; peaks move
relative to one another.** A curve-to-curve operator is a genuine function-to-function
problem here.

## Recommendation

Proceed to architecture work, with three constraints from this measurement:

1. **Do not build around localization.** The mechanism is not there (R² ≤ 0.015). Any
   architecture justified by "localized states shift more" is justified by something this
   corpus does not show.
2. **Beat the right baseline.** A four-parameter linear-in-energy formula reaches 0.340 eV on
   in-gap states, and per-configuration constants reach 0.158 eV. A model must beat 0.34 eV
   to be worth anything and 0.16 eV to beat knowing the answer per configuration.
3. **The learnable quantity is a per-configuration offset**, worth about 0.22 eV of the
   0.374 eV in-gap residual. The remaining 0.158 eV is within-configuration scatter that two
   constants per configuration cannot express — that, not localization, is where an operator
   would have to earn its keep.

The 19 configurations with an unresolved host gap and the 876 in-gap states from
spin-suspect runs should be re-examined before any training set is frozen.

## Files

- `per_state_table.csv.gz` — all 255,568 matched states with energies, shift, occupancy, IPR, dopant weight, match overlap, group
- `final_results.json` — every statistic quoted here
- `plot_1_shift_vs_energy.png` — shift versus energy, and the in-gap residual distribution
- `plot_2_model_ladder.png` — residual after each model, by state group
- `plot_3_localisation.png` — mechanism test, split by occupancy
- `plot_4_dos_shape.png` — DOS deformation and broadening sensitivity
- `cache/` — per-run eigenvalues and per-atom projections (162 runs)

## Method notes

- EIGENVAL read from the text corpus on `/Pool`; PROCAR streamed from the zip archives (it
  was not in the light extraction's keep-list). All 162 runs present, zero failures.
- States matched per (spin, k-point) by Hungarian assignment on a cost combining energy
  difference and character overlap (λ = 2.0 eV). Restricting the in-gap analysis to matches
  with overlap > 0.9 changes the residual by under 0.01 eV.
- Constants are fitted as weighted medians (L1-optimal for the reported MAE), which is the
  most favorable treatment of the rigid models and therefore conservative for a kill test.
- All statistics are k-point-weighted.
- All outputs under `/Pool/`, asserted at the top of each script. No POTCAR or raw run
  content copied elsewhere.

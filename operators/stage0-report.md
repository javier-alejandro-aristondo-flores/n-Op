# Stage-0 floor report

Measured from the derived tensor store; regenerate with `python3 -m operators.data.stage0`.
Cubic-block folds: 261 train runs, 76 evaluation runs (fold 0).

## Cross-fidelity floors (strain atlas, all same-grid pairs)

- pairs with matching grids: 1340 of 1340
- identity floor: median 1.117% relative L2, interquartile 0.046%
- global affine floor: median 1.050%, interquartile 0.036%, median slope 0.9935
- scissor over 1340 eigenvalue pairs: shift 1.2231 ± 0.0572 eV; linear residual 38.6 meV; r-squared 0.9980
- recorded for comparison (667 CSV-joined pairs): shift 1.2612 ± 0.0317 eV; residual 31.7 meV; r-squared 0.9967

## Superposed-atomic-density floor (normalized mean absolute error)

- defect_set: median 14.96%, interquartile 1.29%, runs 196
- supercell_strains: median 14.94%, interquartile 0.01%, runs 169
- alloy_ensemble: median 27.02%, interquartile 3.64%, runs 182

## Basis decay and the projection gate (train folds of the cubic block)

- charge_density_80 (261 snapshots): rank 8: 4.63%, rank 16: 2.61%, rank 32: 0.84%, rank 64: 0.13%; gate GO at rank 15
- electron_localization_up_40 (261 snapshots): rank 8: 4.94%, rank 16: 3.36%, rank 32: 1.54%, rank 64: 0.30%; gate GO at rank 19
- local_potential_mean_removed_80 (261 snapshots): rank 8: 7.28%, rank 16: 4.48%, rank 32: 1.74%, rank 64: 0.27%; gate GO at rank 23
- charge_density_80, defect campaign alone (147 snapshots): rank 16: 2.42%; gate GO at rank 14 — the suite expected this block to fail the gate; it does not

## Per-shell isotropic linear filter (train folds 1-4, evaluated on fold 0)

- charge to localization (coarse grid): mean absolute error median 0.0816, interquartile 0.0074, evaluated on 76 runs
- charge to potential (mean-removed): relative L2 median 23.35%, interquartile 11.82%

## Spectral-Poisson floor (defect campaign; the units test)

- Hartree only: median 159.22% mean-removed relative L2
- climatology only: median 61.92%
- Hartree + climatology: median 57.26% over 42 held-out runs
- the units test passes when the combined floor beats both of its parts
- the raw Hartree term anti-correlates with the total potential (electrons pile up where
  ionic attraction is deepest), which is why Hartree alone exceeds one hundred percent;
  the analytic single-mode test validates the conventions independently
- the semilocal exchange-correlation ridge extension of this floor is pending; it lands
  with the cross-fidelity implementation specifications

## Semilocal pointwise localization floor (per-spin ridge on density features)

- mean absolute error: median 0.0964, interquartile 0.0026, over 152 held-out run-channels
- the pattern rule: a field-to-localization member must beat this by at least twenty percent


# DOS deformation after each shift model

Residual difference from the HSE06 curve, as a percentage of its integral.
Mean over 81 configurations (standard deviation in brackets).

| model | free params | σ = 0.1 eV | σ = 0.3 eV | σ = 0.5 eV |
|---|---:|---:|---:|---:|
| no shift (M0) | 0 | 74.8% (11.2) | 54.1% (6.1) | 43.4% (3.6) |
| rigid scissor (M1) | 1 | 61.6% (9.9) | 40.4% (5.8) | 30.8% (4.7) |
| two constants (M2) | 2 | 56.0% (10.8) | 32.7% (6.2) | 23.0% (5.1) |
| linear in energy (M2L) | 4 | 35.8% (13.3) | 14.8% (10.9) | 9.5% (8.7) |
| per-configuration (M3) | 2 × 81 | 53.1% (10.4) | 31.0% (4.8) | 21.7% (2.5) |

σ = 0.3 eV is the realistic figure: with 8 k-points the spectrum is a comb of
spikes at small σ, which inflates the metric independently of any model.
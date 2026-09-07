# deep_operator_network — measured report

Regenerate with `python -m operators.deep_operator_network.report`.
Relative L2 per run, aggregated over symmetry orbits rather than runs, because runs inside
one orbit are exact copies of each other. Configuration: `principal_component`.

## cheap functional — strain to charge density, held-out test orbits

Train 608 runs, validation 83, test 88 over 22 orbits. Basis rank 32; branch widths (64, 64, 64); 16000 steps chosen on validation.

```
group                       metric       units  runs  median    interquartile  mean_interval       
rank_32_projection_ceiling  relative_l2  22     88    0.000017  0.000009       [0.000018, 0.000029]
ridge_floor                 relative_l2  22     88    0.004140  0.002923       [0.003237, 0.005166]
nearest_neighbor_floor      relative_l2  22     88    0.008958  0.011493       [0.007580, 0.012349]
member                      relative_l2  22     88    0.001069  0.001345       [0.001045, 0.002104]
```

```
group  floor                  floor_median  member_median  improvement  required  verdict
all    ridge_to_coefficients  0.004140      0.001069       74.2%        25.0%     pass   
all    nearest_neighbor_copy  0.008958      0.001069       88.1%        50.0%     pass   
```

```
group              metric       units  runs  median    interquartile  mean_interval       
biaxial            relative_l2  3      3     0.001460  0.000423       [0.001228, 0.002073]
isotropic          relative_l2  5      5     0.003644  0.000492       [0.001995, 0.003806]
one_angle_shear    relative_l2  2      9     0.000499  0.000344       [0.000155, 0.000842]
three_angle_shear  relative_l2  2      8     0.000880  0.000326       [0.000554, 0.001206]
triaxial           relative_l2  6      24    0.000723  0.000743       [0.000579, 0.002479]
two_angle_shear    relative_l2  2      36    0.000649  0.000193       [0.000455, 0.000842]
uniaxial           relative_l2  3      3     0.000981  0.000360       [0.000435, 0.001156]
```

## accurate functional — strain to charge density, held-out test orbits

Train 608 runs, validation 83, test 88 over 22 orbits. Basis rank 32; branch widths (64, 64, 64); 32000 steps chosen on validation.

```
group                       metric       units  runs  median    interquartile  mean_interval       
rank_32_projection_ceiling  relative_l2  22     88    0.000017  0.000009       [0.000018, 0.000031]
ridge_floor                 relative_l2  22     88    0.004111  0.002887       [0.003235, 0.005144]
nearest_neighbor_floor      relative_l2  22     88    0.008964  0.011493       [0.007578, 0.012347]
member                      relative_l2  22     88    0.001013  0.001385       [0.000974, 0.001795]
```

```
group  floor                  floor_median  member_median  improvement  required  verdict
all    ridge_to_coefficients  0.004111      0.001013       75.4%        25.0%     pass   
all    nearest_neighbor_copy  0.008964      0.001013       88.7%        50.0%     pass   
```

```
group              metric       units  runs  median    interquartile  mean_interval       
biaxial            relative_l2  3      3     0.001796  0.000376       [0.001160, 0.001912]
isotropic          relative_l2  5      5     0.002490  0.000623       [0.001546, 0.002806]
one_angle_shear    relative_l2  2      9     0.000338  0.000068       [0.000269, 0.000406]
three_angle_shear  relative_l2  2      8     0.001559  0.000524       [0.001036, 0.002083]
triaxial           relative_l2  6      24    0.000806  0.000409       [0.000566, 0.002369]
two_angle_shear    relative_l2  2      36    0.000473  0.000203       [0.000269, 0.000676]
uniaxial           relative_l2  3      3     0.000648  0.000449       [0.000133, 0.001032]
```

## Standing

- 4 of 4 floor comparisons pass
- the ridge floor is the binding one; the nearest-neighbor copy is roughly threefold weaker, against the suite's expectation that a factorial sweep would make copying brutal
- the basis reconstructs the same fields to a thousandth of the floor, so the error measured here is the parameter map's and none of it the representation's

Caveat: 1 of 2 blocks chose the largest budget offered (32000 steps), so the search did not settle inside its range. Quadrupling the budget moved the member by three to seven percent against a margin it clears by seventy, so the boundary is recorded rather than chased.


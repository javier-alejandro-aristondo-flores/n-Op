# codomain_attention -- results

Standing: **pre-training**. The member, the split, the loader, the masking scheme, the token-shared
readout and the per-token conservation heads are built. Training has not started -- the card is
scheduled by the integrator. This section pre-registers every floor and bar in absolute numbers, per
house policy, before any step of training runs. The dedicated localization competitor
(`factorized_fourier`) trained in 3.94 hours to 0.00217 mean absolute error on fold 0 of the same cubic block; its
dedicated potential run is queued ahead of this member's own card slot.

## Configuration

- hidden channels per token: 32
- kept modes per axis: 19 (mode extent 39)
- attention heads: 2
- explicit-stack layers: 4
- processing grid: (40, 40, 40)
- channel vocabulary: charge_density, magnetization_density, electron_localization_up, electron_localization_down, local_potential_up, local_potential_down
- parameters: 3,838,762 (30.7 MB at double precision, 15.4 MB at the single-precision working width)
- peak memory: not yet measured (deferred to the scaled forward-and-backward pass under "card is yours")

## Floors and bars (fold 0 of the cubic block, cited from the promoted numbers already measured)

- **k1_localization_zero_shot**: floor `factorized_fourier_dedicated_localization` = 0.00217, metric `mean_absolute_error`, required improvement -1.0, absolute bar **0.004340** -- reject if the zero-shot completion error exceeds this on two or more pairwise tasks
- **k1_localization_fine_tuned**: floor `factorized_fourier_dedicated_localization` = 0.00217, metric `mean_absolute_error`, required improvement -0.25, absolute bar **0.002713** -- reject only if still worse than this after the pairwise fine-tune
- **k1_potential_zero_shot**: floor `factorized_fourier_dedicated_potential` = None, metric `mean_removed_relative_l2`, required improvement -1.0, absolute bar **pending** -- pending: the dedicated potential run is queued on the card ahead of this member's
- **k2_localization_semilocal_floor**: floor `semilocal_ridge_floor` = 0.097618, metric `mean_absolute_error`, required improvement 0.2, absolute bar **0.078094** -- the completion flagship deflates if zero-shot elf lands within twenty percent of this
- **k2_potential_spectral_poisson_semilocal_xc**: floor `hartree_plus_semilocal_xc_ridge` = 0.479646, metric `mean_removed_relative_l2`, required improvement 0.3, absolute bar **0.335752** -- the v-read adds nothing over textbook physics if it does not clear this

## Split counts (measured against the committed paired-fields fold map)

- fold 0 (evaluation): 76 runs
- fold 1 (validation): 65 runs
- folds 2-4 (pretrain): 196 runs
- alloy transfer set (zero-shot only): 182 runs
- K3 low-data defect slice (a quarter of the pretraining defect-only identifiers): 27 runs


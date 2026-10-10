# Blind key — every defect known before the auditors launch (2026-09-25)

Fixed before any auditor starts; its sha256 is recorded in the audit folder's provenance.

## Rule for "found"

An item is found when at least one round-1 or later auditor finding, before any verification:
- names at least one of the item's files (the results page, a report, a code file, a test), and
- describes the same defect: an overlapping quote, or the same number, or the same identifier
  with the same failure mode.

Scoring is binary per item, made by me before looking at verifier outcomes. Items marked
`memory-file` are scored separately (the detail sits in a memory file auditors could read);
items marked `hinted` are scored separately (the auto-loaded memory index still alludes to them).

## Items

| id | files | defect | source | status |
|---|---|---|---|---|
| K01 | store `species` for the silicon single-impurity runs; raw file headers | both silicon single-impurity runs name the dopant "H" in every file header; OUTCAR and the electron count say silicon; the store inherits the wrong label | deep dive | memory-file (index line neutralized before launch) |
| K02 | `residual_correction/report.py`, its floors figure | the floors figure collapses five floors under one name, drawing one bar | deep dive | memory-file |
| K03 | `inspection/plots/results.py` `Render_Error_Spread` | the title counts run-by-spin rows as "units" | deep dive | memory-file |
| K04 | `evaluation/scoring.py`, reports with a `mean_interval` column | the interval bootstraps the mean but sits beside medians (deep_dft's reduced ridge median falls outside its own interval) | deep dive | memory-file |
| K05 | `factorized_fourier/figures/.../floors.png`, `report.py` | the floors figure plots relative L2 while the verdicts are on mean absolute error | deep dive | memory-file |
| K06 | `operator-results.md` (VI.1), `deep_operator_network/report.md` | the energy trunk is called "pass" though the test plan sets it no bar | planning | blind |
| K07 | `factorized_fourier` `Spin_Channels` comment | "about a quarter" of defect runs carry magnetization above density; the true count is off by about half | planning | blind |
| K08 | `test-suite.md` I.1, `factorized_fourier` | the flagship is split and judged differently from the split the test plan names for I.1, without a recorded reason | planning | blind |
| K09 | `tasks/__init__.py` localization card, flagship | the card's metrics and conservation law are not what the member computes or applies | planning | blind |
| K10 | a budget or selection step | a per-run median where the unit median is the rule | planning | blind |
| K11 | `evaluation/perovskite_block.py` or its callers | member predictions and floors are renormalized differently on the perovskite block | planning | blind |
| K12 | `data/exclusions.py` | exclusion rules E5–E9 are declared but `Excluded_Paths_For_Scope` has no callers | planning | blind |
| K13 | `data/store.py` | a docstring calls the archive name a content identifier; it is a hash of the path | planning | blind |
| K14 | an occupancy comment (spectra or loader) | "one to two" is wrong for the occupancy it describes | planning | blind |
| K15 | `operator-results.md` | stale status words: I.2, III.1, V.1 "member not started"; I.3 "pending"; III.3 "no package exists"; cross-member "not yet" | planning, outputs map | hinted |
| K16 | `evaluation/cross_member.md` | the conformal coverage median reads 1.000000 where the correction report says 0.977 | planning | blind |
| K17 | `factorized_fourier/report.md` | the floors are said to reproduce stage zero's "exactly"; 0.0964 is a run-channel median, 0.097618 a unit median | planning | blind |
| K18 | `deep_operator_network/report.md`, results page | "14 of 14" and "25 of 35" count comparisons over different scopes | planning | blind |
| K19 | `residual_correction` spec and build | the specified quantile (pinball-loss) head was not built; the band is plain split conformal | planning | blind |
| K20 | the affine floor (`Identity_And_Affine_Floors` or the correction report) | the affine floor is fitted per pair, not as the specified global map | planning | blind |
| K21 | member `manifest.toml` files | stale manifests: "declared, not built" for built configurations, a listed FiLM conditioning, stale ranks | planning | blind |
| K22 | `test-suite.md` | cost and size estimates contradicted by measurement and never edited | planning | blind |
| K23 | an orbit count per strain family | orbits counted twice across families | planning | blind |
| K24 | `deep_operator_network/report.md` perovskite | the "every shape" verdict rests on floors from the angle stratum only | planning | blind |
| K25 | results page or flagship documents | the explicit rung's best validation loss quoted as 8.0e-5 in one place and 8.1e-5 in another | planning | blind |
| K26 | `evaluation/cross_member.py`, `cross_member.md` | the flagship and the branch–trunk network are absent, silently, for want of a `results.json` | outputs map, confirmed | blind |
| K27 | `operator-results.md` I.4 | "52,283 steps in its two hours"; the manifests show 33,170 steps in about 78 minutes | outputs map, confirmed | blind |
| K28 | `tests/test_evaluation.py` results-page test | inverted closing guard, any-row matching, the two members without `results.json` skipped | tests map, confirmed | blind |
| K29 | commit `a5cd89f` message | "worse on every one of the three card metrics"; on relative L2 the member is better (0.069531 vs 0.070017) | planning, confirmed | blind |
| K30 | `training/loop.py` `Train` | a zero-step resume rewrites the manifest, curves and plots; resuming an early-stopped run trains on and overwrites the checkpoint | outputs map, confirmed | blind |
| K31 | `deep_dft/IMPLEMENTATION.md`, `tests/test_deep_dft.py`, `tests/test_parts.py` | real pseudopotential titles from the corpus on the public remote | my check, confirmed | blind |
| K32 | `galerkin_transformer/results.json` | the regeneration line omits the run argument, so a rerun drops both verdicts | outputs map | blind |
| K33 | `alias_free_convolutional/results.json` | zero rows although the report states measured floors | outputs map | blind |
| K34 | `deep_operator_network/report.md` | assembled across four commits; no single run produced it | outputs map | blind |
| K35 | `factorized_fourier/report.py` ladder table, other reports | numbers with nothing on disk: hard-coded wall clock and peak memory, early cap-hit fractions, the seed-sweep spread, manifold and correction timings | outputs map | blind |
| K36 | `nonlinear_manifold_decoder/report.py` | a docstring promises a "fresh training run"; it is a zero-step resume | outputs map | blind |
| K37 | residual and manifold manifests on `/Pool` | rewritten with 0 s and cpu; the original timings survive only as checkpoint dates | outputs map | blind |
| K38 | `factorized_fourier/report.md` vs `report.py` | the report predates seven generator commits; the hard-coded ladder table lacks the injected row and shows the fixed point as "--" | outputs map | blind |
| K39 | `galerkin_transformer/figures/` | 74 committed figures with no generating function in the repo | outputs map | blind |
| K40 | results page, codomain documents | the partial codomain pretrain (2,800 of about 2,828 steps, no manifest) is recorded nowhere | outputs map | hinted |
| K41 | `deep_operator_network/configs/energy_trunk.toml` | a comment calls its own, already corrected, value wrong | critique | blind |
| K42 | `test-suite.md` via `475a282` | I.1's configuration line rewritten to "as built" with no note in the document | critique | blind |
| K43 | `nonlinear_manifold_decoder/report.md` | first committed after the earliest surviving training checkpoint | critique | blind |
| K44 | `multiple_input_operator_network` loader | the void run loads without error under the same parameter names; nothing guards against it | outputs map | blind |
| K45 | training manifests | no commit, configuration or data hash recorded | critique | blind |
| K46 | `data/splits.py` `Regenerated_Artifacts_Match` and its test | proves determinism only, while read as proving the splits correct | critique | blind |
| K47 | `evaluation/scoring.py` `Compare_To_Floor` | never checks that the member rows and floor rows cover the same units | planning | blind |
| K48 | the license scanner | no scanner covers `operators/`; the archived one resolves to `1-archive/` | tests map | blind |
| K49 | `evaluation/cross_member.md` | verdicts dropped for the two-input network and the manifold decoder | planning | blind |
| K50 | tests across the package | about twenty tests whose names promise more than they check | tests map | blind |
| K51 | `factorized_fourier/report.md` | 1.35% where the median 0.013450 rounds to 1.34% or 1.35% depending on the pass (a rounding flip) | outputs map | blind |
| K52 | flagship committed figures vs `/Pool` cache | the committed figures can no longer be reproduced from the cache, which the ladder run rewrote after trunk | outputs map | blind |

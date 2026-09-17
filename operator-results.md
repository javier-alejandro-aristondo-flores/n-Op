# Operator results — one page to judge every entry of the suite

One section per entry of `test-suite.md`, in the canon's order. Every number here is copied from
the committed report of the member that produced it (`operators/<member>/report.md`), which stays
the source of truth; this page is the index, kept current by the integrator at each landing.
Verdicts use the canon's own bars; levels added before a member trained are labeled as added.

| as of | trunk | tests | figures |
|---|---|---|---|
| 2026-09-17, 14:30 | `99f5b1b` | 617 + 9 card-only | 784 committed |

Words used throughout, defined once: the *electron localization function* is a field on [0, 1]
saying how strongly electrons are pinned at a point; the *density of states* is the curve of how
many electronic states sit at each energy; a *floor* is a baseline computed before a member trains,
on the member's own evaluation block; a *kill* is the canon's bar that removes a member or task
if missed; the *cheap* and *accurate* functionals are the two levels of theory in the corpus; a
*unit* is the exchangeable group (a symmetry orbit, or a same-geometry pair) every number is
aggregated to before its median is taken. "One seed" means a single training run: the branch–trunk
member measured a seed spread of 14–35% of the median on its own task, so no few-percent
difference between two single runs is resolvable anywhere on this page.

Status words: **not started** (a stub), **parts built** (its shared parts exist, no member),
**built** (the member exists and tests pass), **floors measured**, **trained** (one seeded run),
**judged** (trained and scored against its floors), **finished** (every configuration and task the
canon names, judged), **killed** (a canon bar was missed and the entry or task is removed),
**not built: cost** (a canon-named build is skipped and recorded as a cost decision, not a miss).

## Summary, one row per canon entry

Copied from the sections below; no number here is computed fresh. Entries without a member number
yet read **pending**.

| entry | member | configuration | status | task / split / block | headline vs bar | verdict |
|---|---|---|---|---|---|---|
| I.1 | `factorized_fourier` | explicit | judged (localization); potential and parametric floors measured, training queued | charge_to_localization / fold 0, cubic block | MAE 0.00217 vs kill ≤ 0.0488 | pass, 97.8% better |
| I.2 | `alias_free_convolutional` | — | parts built, member not started | charge_to_localization (planned) | pending | pending |
| I.3 | `factorized_fourier` | weight_tied_injected | four of five rungs trained and judged; the three stability rungs for the fixed point are built, probes queued | charge_to_localization / fold 0 | MAE 0.00271 (injected), 0.00297 (plain), copy margins 56% and 52% | pass; weight-tying yes at matched parameters, no at matched width; fixed_point pending |
| I.4 | `galerkin_transformer` | width 128, 4 heads, 4 layers | killed at its stage-1 gate, one seed | lattice_to_charge / perovskite angle stratum, fold 0 (25 runs) and 27 interior arm levels | 0.1780 vs bar ≤ 0.0426 (copy 0.0853); 0.1191 vs bar ≤ 0.0132 (interpolation 0.0264) | killed by its own pre-registration after three defects were fixed; tied with the training-mean field (0.1755); stage 2 not run |
| II.1 | `deep_operator_network` | principal_component | finished | strain_to_charge / 40³ block, cheap functional | 0.000821 vs ridge kill ≤ 0.003105 (25% better) | pass, 14 of 14 |
| II.2 | `multiple_input_operator_network` | — | not started | charge_and_potential_to_localization (planned) | pending | pending |
| II.3 | `nonlinear_manifold_decoder` | canonical | killed, one seed | strain_to_charge / 423 interior arm levels (and the committed split, 22 units) | 0.002452 vs bar ≤ 0.000607 (bracketing interpolation 0.000911) | killed on the interpolation bar, as pre-registered and as the canon predicted; grid transfer a narrow miss (1.32× vs 1.3×) |
| II.4 | `factorized_fourier` | parametric | built with floors measured, training queued | strain_to_charge, parametric / interior levels | floor 0.091% vs kill ≤ 0.064% | pending, not yet trained |
| III.1 | `deep_dft` | — | parts built, member not started | structure_to_charge_defects (planned) | pending | pending |
| III.3 | `gaussian_plane_wave` | — | not started; no package exists yet | structure → charge (planned) | pending | pending |
| IV.1 | `residual_correction` | projection_backbone | judged, one seed | cheap_to_accurate_charge / strain_atlas_holdout / test, 22 orbits | 0.002079 vs kill ≤ 0.005565 (identity 0.011131) | pass the canon kill; 406× worse than the closed-form ridge, so nothing gained over linear regression |
| IV.2 | — | — | not started | cheap_to_accurate_states (planned) | pending | pending |
| IV.3 | `wrappers` (`ConformalCalibrator`) | level 0.90, orbit unit | applied to IV.1 | cheap_to_accurate_charge / test orbits | coverage 0.977 vs guaranteed 0.900–0.942 | valid, over-covering (conservative) |
| V.1 | `codomain_attention` | — | parts built, member not started | field_completion (planned) | pending | pending |
| VI.1 | `deep_operator_network` | energy_trunk | finished | strain_to_states / 248 test runs, 30 orbits | curve L1 0.206 vs ridge 0.368 | pass, 44% better |

---

## I.1 — Factorized Fourier neural operator · charge density → electron localization (and → local potential)

**Status: localization task judged (explicit stack); the deep-equilibrium ladder in progress
(I.3); potential task built with floors measured, training queued; parametric variant built with
floors measured, training queued (II.4).** Package `operators/factorized_fourier/`.

Assembly as built: per-spin log-compressed densities plus six lattice Gram-matrix channels on the
fine 80³ grid → truncation to 40³ (exact, before the lift, since a pointwise linear lift commutes
with spectral truncation) → twelve factorized spectral layers at the full coarse Nyquist (19 modes
per axis; the canon's "20³" is one more than a 40-point axis can hold) at width 64, 11.55M
parameters → bounded head 1/(1 + softplus²). Trained on folds 2–4 (196 runs), early-stopped on fold
1 (65 runs, 24 units), judged on fold 0 (76 runs, 29 units) of the cubic block, which no training or
model selection touched. Batch 1, single precision on the card, one seed.

**Floors on that block, mean absolute error, both spins, unit-aggregated medians:**

| floor | pooled | defect set | strains |
|---|---|---|---|
| semilocal pointwise ridge (density, gradient, Laplacian) — the canon's kill anchor | 0.0976 | — | — |
| per-shell linear filter (a one-layer linear Fourier operator) | 0.0830 | — | — |
| training-mean template (added) | 0.0160 | — | — |
| nearest-training-run copy, by input distance (added, the memorization null) | 0.0062 | 0.0082 | 0.0014 |

The canon's floor turned out weaker than a positional template on this block: the geometries are
near-identical, so a coordinate-blind fit loses to an average. Three levels were therefore added
before training and pre-registered.

**Result, explicit stack (24,404 steps, 3.94 h):**

| | mean absolute error | relative L2 | structural similarity |
|---|---|---|---|
| pooled, 29 units | **0.00217** | 1.05% | 0.9998 |
| defect set | 0.00233 | 1.35% | 0.9995 |
| strains | 0.00070 | 0.26% | 0.99999 |

| level | bar (mean absolute error) | verdict |
|---|---|---|
| canon kill: half the semilocal ridge | ≤ 0.0488 | pass, 97.8% better than the ridge |
| canon pattern rule: 20% better than the ridge | ≤ 0.0781 | pass |
| added: beat the template | < 0.0160 | pass, 86% better |
| added: beat the nearest-run copy | < 0.0062 | pass, 65% better |
| added stretch: half the template | ≤ 0.0080 | pass |

Self-consistency: the same weights answering an 80³ grid they never trained on, truncated back,
sit within 0.62% relative L2 of the direct coarse answer. The alloy campaign carries no localization
target, so the every-shape transfer row does not apply here. Caveats: one seed; the strain rows
read 3.3× better than the defect rows because strain barely moves this field, so the defect rows
are the real test — and they still beat verbatim copying three to one. The nearest published
number (a 2026 hydrogen-only localization network at 0.019) is an easier problem, not a competitor.

**Potential task (charge density → local potential), floors measured, not yet trained.** The
target lives on the fine grid; the coarse trunk's own truncation ceiling is 2.13% mean-removed
relative L2, an order of magnitude below the bar, so the design keeps the coarse trunk and resamples
back to 80³. Floors per spin on the full cubic block (mean-removed relative L2, medians): Hartree
term alone 154%; positional climatology 60.3%; Hartree + climatology 40.3%; Hartree + semilocal
exchange-correlation ridge 47.96% — the canon's anchor, so the **bar is 23.98%** (twice as good),
and the canon says a miss is "the physics floor suffices", a finding. Metric-aware spectral kernels
(a learned per-mode gain over the physical wavevector) are wired in for this task.

**What remains here:** the ladder (I.3), the potential run, the parametric run (II.4), a seed
sweep behind every row, the five-fold protocol once for the final table.

---

## I.2 — Convolutional neural operator · charge density → electron localization (and → local potential)

**Status: parts built, member not started.** The multi-scale composition with exact spectral
resampling exists (`operators/compositions/multi_scale.py`); the fused activation-resampling kernel
with its own gradient rule — the entry's identity, mandatory because naive autodiff materializes
the doubled grid and exhausts the card — does not. Floors: shares I.1's, already measured on the
same block; its own identity check (match a width-matched plain U-Net and degrade at most half as
much under grid shift) is not built.

---

## I.3 — Deep-equilibrium Fourier operator, with the weight-tied ladder · charge density → electron localization, computed as a fixed point

**Status: four of five rungs trained and judged; the fixed-point rung's three canon stability rungs
are built and tested (spectral clipping, a Jacobian penalty, a normalized parametrization), their
probes queued on the card.** Lives in `operators/factorized_fourier/` as configurations of one factory, the
canon's own design. The experiment is the decomposition curve explicit → weight-tied → fixed point,
isolating what weight sharing buys from what implicit depth buys; "weight-tying yes, deep
equilibrium no" is a legitimate verdict.

| rung | parameters | steps | wall-clock | peak card memory | validation loss | mean absolute error | verdict on the five levels |
|---|---|---|---|---|---|---|---|
| explicit, twelve layers | 11.55M | 24,404 | 3.94 h | 3.6 GB | 8.0e-5 | 0.00217 | all pass |
| weight-tied, one layer applied twelve times (no input injection) | 0.96M | 23,804 | 2.69 h | 3.2 GB | 1.2e-4 | 0.00297 | all pass; copy margin 52% |
| explicit, one layer — the exact matched-parameter comparator | 0.96M | 35,505 (full budget, still improving) | 0.52 h | 0.7 GB | 3.9e-4 | 0.01004 | canon levels pass; fails the copy and the stretch |
| weight-tied with input injection — the fixed point's exact unrolled counterpart | 0.96M | 28,504 | resumed across two power losses | 3.5 GB | 1.0e-4 | 0.00271 | all pass; copy margin 56% |
| fixed point (phantom gradient, depth 3) | 0.96M | — | — | — | — | — | pending |

Reading so far: re-applying one layer twelve times beats applying it once by more than three to one
at identical parameter count; injecting the input at every application buys another 9% (0.00271
against 0.00297; defects 0.00316, strains 0.00107); the twelve-layer stack is still a quarter better
than the best tied rung for twelve times the parameters. So far: weight-tying yes at matched
parameters, no at matched width. One seed per rung.

Canon bars for the fixed-point rung: beat the explicit comparator at both matchings (same width and
matched parameters) over three seeds, or be at least 3× faster to train; health floor ≥ 90% of
validation inputs converging to a relative residual of 1e-3 within 32 iterations (kill under 80%).

Four latent defects in the shared fixed-point primitive surfaced on its first card runs and are
fixed on the trunk: numpy asked to read a card tensor; a host-bound Anderson step; no input
injection, so the equilibrium was identical for every input and the model could only emit a
constant; an absolute residual tolerance that on a four-million-entry iterate meant parts per
million. A fifth item is measured and open: the shared layer does not contract at its default
initialization, and the canon's first stability rung, a contractive initialization, holds only at
the start — with the shared layer's weights scaled by 0.1 or 0.03 the solves converge at step 100
(cap-hit 0.34, mean 22 iterations) and training drives the map back out of contractivity by step
200–300 (cap-hit 0.98 → 1.00) at both scales. The next rungs the canon names are builds: per-mode
spectral clipping, a Jacobian penalty, a monotone parametrization; one of them is built before the
rung trains. Even at the cap the injected model learns (validation loss 3.4e-3 at step 200, better
than the explicit stack there); what it lacks is a converged equilibrium, which the health floor
exists to say. The honest counterpart of the fixed point is a weight-tied rung *with* input
injection, queued after it; the injection-free weight-tied row above stays as an extra rung.

---

## I.4 — Galerkin transformer with query-point decoding · charge density → electron localization / local potential

**Status: killed at its stage-1 gate by its own pre-registration, one seed (20260916).** A new
package, `operators/galerkin_transformer/`: softmax-free attention (queries times the key–value
product over the token count, keys and values normalized over the token axis, verified against a
token-by-token double loop with no token-by-token tensor ever formed), a cross-attention decoder at
query points, width 128, four heads, four layers, 374,145 parameters. The canon stages this entry:
first the perovskite lattice factors → charge density gate on the angle stratum (32³ tokens, 64³
queries, the six factors as constant channels), two hours of wall-clock; only on a pass, the
localization task on the cubic block.

| population | row | median relative L2 |
|---|---|---|
| fold 0 of the angle stratum, 25 runs | nearest-angle copy, the floor | 0.0853 (bar ≤ 0.0426) |
| | the training-mean field (context) | 0.1755 |
| | **the member** | **0.1780 — killed** |
| 27 interior levels of the angle arm | linear-in-angle interpolation, the floor | 0.0264 (bar ≤ 0.0132) |
| | **the member** | **0.1191 — killed** |

Run `perovskite_gate_v2_52283`: 52,283 steps in its two hours at 0.138 s per step, 1.5 GB on the
card; validation flat at the mean field through every stage. For scale, the built branch–trunk
member reaches 0.0183 on the same fold.

**The kill is of a repaired member, not of a bug.** Its first gate run never trained, and three
defects were found and fixed before this verdict: the decoder's queries carried coordinates only, so
training drove the output blind to the lattice factors (outputs for two different structures 27%
apart at initialization, 4e-8 apart after training; fixed by conditioning the queries on the
factors, with a regression test); the electron-count renormalization sat inside the training loss
(moved to inference only, the house pattern); and the raw density's core cusps owned the squared
error (the top 5% of voxels carry 77% of it; fixed by per-voxel target standardization, the
corpus's own recorded prescription). After the fixes the member reaches the mean field in a
hundred steps, keeps its input dependence (14% between its two most separated evaluation runs),
and learns nothing beyond the mean.

*An untested hypothesis, recorded before the verdict:* on this task the network is handed no
field, only six constants and order-four periodic coordinate features, so everything spatial must
be synthesized from four modes per axis, while the lattice response is concentrated near the atomic
cores of a 64³ grid; the branch–trunk member wins the same task because a proper-orthogonal basis
hands it that structure. The canon names no rung after this gate, so it is not pursued. The
localization stage and the potential cross-entry bar were not run.

---

## II.1 — DeepONet family (branch–trunk) · strain or lattice parameters → charge density; (and → density of states, VI.1)

**Status: finished — four configurations, two field campaigns, the state-density task, two
extrapolation holdouts.** Package `operators/deep_operator_network/`. A branch reads the run's
parameters into a latent vector; a trunk turns a query point into features; their product is the
field at that point. Configurations: `principal_component` (fixed modes, the linear version of the
map *is* the ridge floor), `proper_orthogonal` (fixed modes on a per-voxel standardized field),
`canonical` (a learned coordinate trunk, queryable at any point and grid), `energy_trunk` (the
trunk over energy, VI.1).

**Strain atlas → charge density**, 40³ same-shape block, 88 held-out test runs over 22 orbits per
functional, relative L2, orbit-aggregated medians, single precision on the card, 32,000 steps, one
seed:

| row | cheap functional | accurate functional |
|---|---|---|
| ridge floor (parameters → mode coefficients); kill: beat by 25% | 0.00414 | 0.00411 |
| nearest-neighbor field copy; kill: beat by 2× | 0.00896 | 0.00896 |
| rank-32 projection ceiling | 0.000017 | 0.000017 |
| `principal_component` | **0.000821** | **0.001092** |
| `proper_orthogonal` | **0.000819** | **0.001122** |
| `canonical`, scored on the same 40³ block | 0.001896 | 0.002413 |
| `canonical`, all 124 test runs across nine grid shapes (copy floor 0.0094) | 0.002339 | 0.002766 |

Every comparison passes (fourteen of fourteen). The two fixed-basis configurations are
indistinguishable: a twelve-run seed sweep put their paired difference at 0.5% and 1.8% against
within-configuration spreads of 14–35%, and the published explicit bias term is a structural zero
(+1.6e-18 on the training block). The learned trunk is the only configuration that reads every grid
shape; it costs about 2.3× the fixed basis on the shared grid, the division of labor predicted.

**Strain atlas → density of states** (the energy trunk, VI.1), 248 test runs over 30 orbits, both
functionals pooled, window −28 to +8 eV from the valence-band maximum:

| row | curve L1, whole window | curve L1, band edges −2…+6 eV |
|---|---|---|
| training-mean floor | 0.392 | 0.757 |
| ridge floor | 0.368 | 0.518 |
| **member, the card's own loss** | **0.206** (44% better than the ridge) | **0.265** (49%) |
| ablation, band edges weighted 5× | 0.208 | 0.193 |

Per functional, whole window: cheap 0.195, accurate 0.215. The canon sets no numeric kill for this
task. Two facts recorded before building: the whole-window metric dilutes the strain signal about
fivefold because 467 of 601 bins are nearly strain-invariant valence states, and the support-edge
gap read-out is an artifact of the smearing on this window (every truth crosses its threshold at
+0.020 eV with zero spread), so the floors' zero there is inherited, not earned.

**Perovskite lattice factors → charge density** (II.1b), one seed, relative L2, unit-aggregated
medians; fold 0 is the interpolation block the canon judges; the two factor holdouts are
extrapolation rows labeled and reported, not kills:

| split | ridge floor | copy floor | `principal_component` | `proper_orthogonal` | `canonical`, shared grid | `canonical`, every shape |
|---|---|---|---|---|---|---|
| fold 0 (interpolation) | 0.0423 | 0.0853 | **0.0183** pass/pass | **0.0189** pass/pass | **0.0235** pass/pass | 0.0248 (50 runs, 26 shapes) |
| factor-0.8 holdout (extrapolation) | 0.0755 | 0.0877 | 0.0937 | 0.1264 | **0.0434** | 0.0443 (122 runs, 62 shapes) |
| factor-1.2 holdout (extrapolation) | 0.0766 | 0.0877 | 0.0584 | 0.0606 | **0.0499** | 0.0461 |

Under extrapolation the fixed bases degrade to about the linear floor while the learned trunk stays
best; it is the only configuration clearing a holdout (both bars on 0.8, and 43% against a 50% copy
bar on 1.2, where its run was still improving at its budget). The learned trunk reads the length
stratum's 124 distinct grid shapes at about the shared-grid error. Every fixed-basis budget search
chose its largest candidate; the ceiling is recorded rather than chased.

**What remains here:** a seed sweep behind any few-percent claim; the five-fold protocol once for
the final table; the projection variants of the field-to-field tasks (II.1c) are unbuilt.

---

## II.2 — Multiple-input operator network · (charge density, local potential) → electron localization

**Status: not started.** Its low-rank kernel has a lifted forward (a Nyström integral, not the
multiplicative latent combination this member needs, which is member work), its composition is
the layerless one the branch–trunk member uses, and the encoders and readouts it needs exist.

---

## II.3 — Nonlinear manifold decoder · strain or lattice parameters → charge density, decoded point by point

**Status: killed on its pre-registered interpolation bar, one seed (20260916).**
`operators/nonlinear_manifold_decoder/`: the six strain components plus the functional → a sensor
encoder → `NonlinearDecoder` (the value at a point is a nonlinear function of latent and position,
proven not expressible as a linear map of its latent), point-sampled on every grid shape; 272,001
parameters; about 10,200 steps in seven minutes on the card (≈0.7 GB sampled), the rest of its
46 minutes host evaluation. Relative L2, medians:

| population | row | median | reading |
|---|---|---|---|
| 423 interior levels of the strain arms (leave one level out) | bracketing linear interpolation, the floor | 0.000911 | bar: a third better, ≤ 0.000607 |
| | Gaussian radial basis on the six strain components, the second floor | 0.000991 | bar ≤ 0.000661 |
| | ridge to the strain tensor (context) | 0.004225 | — |
| | nearest-run copy (context) | 0.019876 | — |
| | **the member** | **0.002452** | **killed: 2.7× worse than interpolation** |
| committed holdout split, 22 units | the member's headline | 0.002424 | context: the built branch–trunk canonical reads 0.0019–0.0024 on the same split |
| every grid shape, 30 units | the member | 0.002795 | — |
| grid transfer | error off the dominant 40³ shape against on it | 0.003188 against 0.002424 | inflation 1.32× against a bar of 1.3×: a narrow miss |

The canon predicted this: on an interpolation split a linear interpolation between bracketing
training levels is nearly exact, and a learned decoder cannot beat it by a third. The member is a
working operator that answers on nine grid shapes at the branch–trunk member's accuracy; it is
killed by its bar, not by a defect.

---

## II.4 — Parametric factorized Fourier operator · strain or lattice parameters → charge density

**Status: built with floors measured; training queued at a reduced budget.** A configuration of
I.1: the parameter vector broadcast as constant channels plus periodic coordinate features of the
query grid (proven necessary — constant channels alone can only produce a constant field), the
density out with the electron count renormalized exactly.

The decisive floor the canon names, linear interpolation of the density between bracketing
parameter values along a sweep arm, measured on every interior level of the strain atlas (423
levels, seven families), relative L2 medians per family: one-angle shear 5e-6, isotropic 2e-5,
uniaxial 2.5e-5, biaxial 6.6e-5, two-angle shear 1.9e-4, three-angle shear 6.5e-4, triaxial 1.4e-3;
pooled **0.091%**. Beside it on the same leave-one-level-out block: the ridge to rank-32 modes, the
nearest-run copy in parameter space, the training mean. **Canon kill: under 0.7× the best floor,
i.e. 0.064% relative L2**, on interpolation splits; the canon itself predicts the interpolation floor
wins there and calls that informative. The arm map (strain families with their levels; perovskite's
two three-dimensional sweeps) is report-local data until the variant survives.

---

## III.1 — DeepDFT · atomic structure → charge density (and magnetization), queryable anywhere

**Status: parts built, member not started.** `AtomEmbedding` (keyed by element and
pseudopotential title, never element alone), the continuous displacement kernel, periodic radius
graphs by cell height, and the superposed-atomic-density floor (Stage-0) exist. Kills: 10× the
superposed-density floor; 3× the reduced isotropic kernel-ridge floor; moments within 5% with the
right sign on 90% of magnetic runs. Named schedule risk: scatter-add throughput.

---

## III.3 — Gaussian plane-wave neural operator · atomic structure → charge density

**Status: not started; no package exists yet.** Its kill benchmark *is* III.1 at matched budget,
so it cannot be judged before III.1 is measured; the canon records in advance that it expects this
entry to land redundant, and building it is what makes that prediction worth something.

---

## IV.1 — Residual correction · cheap-functional charge density → accurate-functional charge density

**Status: judged, one seed (20260916).** `operators/residual_correction/`, configuration
`projection_backbone`: the cheap density's rank-32 basis coefficients → a small network starting at
the identity → the correction's rank-32 basis, zero-mean conserved; 24,865 parameters; 20,000 steps
in about 34 minutes. Test block: 88 runs in 22 symmetry orbits of the strain atlas holdout, relative
L2, orbit-aggregated medians.

| row | median | against the identity floor |
|---|---|---|
| identity (return the cheap density) | 0.011131 | the floor |
| global affine | 0.010466 | 6.0% better |
| ridge from the strain components | 0.000049 | 99.6% better |
| ridge from the cheap density's coefficients | 0.000005 | 100.0% better |
| rank-32 representation ceiling | 0.000002 | — |
| **the member** | **0.002079** | **81.3% better; canon kill ≤ 0.005565 passed; ΔR² 0.9645** |

The pass is against the canon's pre-registered bar only. The closed-form ridge from the cheap
density's own coefficients is 406 times better than the trained member: on this holdout, which
removes symmetry orbits but leaves every held-out point a small interpolation step from a training
point, the correction is almost exactly linear in those coefficients and the network adds nothing
over linear regression. The canon's conditioning on campaign and exchange fraction is a no-op on
this one-campaign block and was not built; the spectral backbone is the escalation for a miss and
was not needed.

---

## IV.2 — Spectral correction · cheap-functional density of states → accurate-functional density of states

**Status: not started.**

---

## IV.3 — Conformal interval wrapper · any prediction → the same prediction with a guaranteed-coverage interval

**Status: applied to IV.1.** `ConformalCalibrator` in `operators/wrappers/`, a wrapper, never a
member. Level 0.90, exchangeable unit the symmetry orbit, calibrated on 23 validation orbits and
applied to the 22 test orbits of the correction member: coverage 0.977 against a guaranteed
interval of 0.900 to 0.942. Valid and conservative: it over-covers by 0.036.

---

## V.1 — Codomain attention · any subset of the fields → the missing fields

**Status: parts built, member not started.** The whole kernel package exists
(`operators/kernels/codomain_attention/`): attention over at most eight field tokens with
token-shared spectral query, key, value and output blocks, function-space layer norm, a
token-shared local term, a max-shifted softmax; parameter count independent of the token count.
`VariableEncoding` exists in `operators/encoders/`. Kills: the dedicated per-pair Fourier operator at
equal compute on the same 365-run block with the alloy campaign held out on both sides; the
potential read must beat the spectral-Poisson + semilocal floor by 30%.

---

## VI.1 — Energy-trunk operator · strain parameters → density of states over energy

**Status: finished** — a configuration of II.1's member; results in the II.1 section above.

---

## Out of scope by the canon's own deferral

III.2 (rotation-equivariant structure model, twelve to twenty person-weeks, after the bigger
machine), III.4 (a candidate pending a drill), VI.2 (band structure, one design decision open), and
every "super-later" ablation: the full-width fine-grid trunk, the large codomain-attention
configuration with alloy fine-tunes, the tensor-factorized configuration.

## The cross-member table

Not yet: it means something only once several members have numbers on the canonical fold maps,
and it is valid only there. Scheduled as the sweep's close-out.

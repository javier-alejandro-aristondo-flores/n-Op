# deep_dft — atomic structure → charge density field (and magnetization)

Queryable at any point.

**Operator.** DeepDFT — Jørgensen & Bhowmik, *npj Computational Materials* 8, 183 (2022), with
the PaiNN-style vector-feature upgrade as the recorded stretch. Suite entry: `test-suite.md` §4,
III.1 — the structure-to-field anchor.

## What it assembles

Atom embedding → member-local `MessagePassingStack` (three atom-atom compact-support-kernel
layers, then three atom-probe layers over one point set carrying atoms and probes together) →
member-local `ProbeHead`, a two-layer perceptron reading each point's own features onto a
two-channel (density, magnetization) head. The framework's `ExplicitStack` is grid-typed and
cannot host point-set message passing, and the shared `PointwiseProjection` assumes a
channel-first grid layout rather than `PointSet`'s point-first one, so both are member-local
builds against the framework's `Layer`/`Kernel` shapes rather than direct reuse. The shared
`Conserving` wrapper is likewise not reused directly: it flattens every output channel together
before renormalizing, which is correct for a single-channel target but scales magnetization by a
density-derived factor once a second channel rides beside it, so renormalization to the electron
count is a member-local function acting on the density channel alone.

## Why it is shaped this way

**The probe mechanism is the operator argument.** The input is the atomic configuration as an
empirical measure — a sum of delta functions carrying species — and the first layer is an
integral operator with a learned continuous kernel evaluated against it. Probe points placed
anywhere in the cell join the message graph but only receive, so the density is a function
queryable at any point and differentiable in position. Grids supply supervision only; the corpus
exercises the claim directly, since one model consumes 40³, 64³, 80³, and 48×96×216 supervision.

**One point set, with roles.** Probes receive messages at every layer, so the layer state is
atoms and probes together. This is what collapsed the framework's two point representations into
one carrying a `roles` field.

**Periodic images by cell height.** With a cutoff comparable to the shortest cell height, the
minimum-image shortcut silently drops neighbors; images are enumerated per direction from the
cell heights with an exact distance filter.

**The spin channel is this suite's own extension.** The literature predicts total density only;
here a second channel carries magnetization, its loss normalized by the integrated absolute
moment and masked where the calculation was spin-restricted.

**Probe sampling is importance-weighted.** Error mass concentrates in atom-centered volumes, so
the sampler mixes uniform and atom-centered draws and de-biases with inverse-proposal weights,
keeping the loss an unbiased estimate.

## Floors and kill thresholds

Three gates. Against the superposed-atomic-densities floor (already on disk for the paired-field
runs): a factor of ten. Against the reduced isotropic kernel-ridge floor: a factor of three, or
probe message passing is not earning its complexity. On the magnetic runs: moment error within
five percent and the correct total-moment sign on ninety percent. Any gate failed after the full
budget kills that task; two tasks killed removes the member.

## Implementation specification

**Encoder.** `encoders.AtomEmbedding` over a training-fold vocabulary of every `(element,
pseudopotential title)` pair the defect campaign's folds one through four carry, plus one trained
`("unknown", "unknown")` row. A member-local `SpeciesKeys.Resolved` maps any pair the vocabulary
does not hold onto that row rather than letting `AtomEmbedding.Vocabulary_Indices` raise; during
training `Relabeled_Species_Keys` additionally relabels a random ~10% of every batch's own keys to
the unknown row, so its embedding is trained rather than left at its random initialization. The
title-to-element match is by the title's second whitespace-separated token with any `_xx`-style
PAW suffix stripped (`"PAW_PBE Fr_sv 29May2007"` → element `Fr`); a run's own OUTCAR titles are
matched against its own species column this way, not by position. One real corpus case exercises
the unknown row directly: `diamond/single_defects_new-only-GGA-PBE/IVA-element-single-impurity/Si`
carries hydrogen atoms in its geometry but only `Si` and `C` titles in its OUTCAR (a stale
POTCAR/geometry pairing), so its `H` atoms have no resolvable title and route to the unknown row
even before the training-vocabulary check runs.

**Composition — `MessagePassingStack`.** Three `ContinuousDisplacementKernel(cutoff_radius=4.0,
basis_count=20, output_channels=64, input_channels=64)` layers, each summed with a linear (no
hidden layer, no activation) local term and passed through `Gaussian_Error_Linear_Unit`, applied
over the atoms alone (`roles` absent, every atom both sends and receives, self-edges at distance
zero included since the kernel is not filtered to exclude them — the local linear term is a
second, explicit self-channel, so this is a mild redundancy rather than a bug). The resulting atom
features are then concatenated with zero-initialized probe features into one joint point set with
`roles` (atom = 1, probe = 0), and three more identically shaped layers run over the joint set,
`Sending_Points` filtering every kernel sum to atom-sourced edges only — an atom keeps refining
from other atoms, a probe only ever receives. The two phases share one radius graph and one
`Radial_Profile_Features` evaluation per phase (not per layer), since positions are fixed for the
whole forward pass and only the carried values change layer to layer. Each phase's graph is
`Periodic_Radius_Graph`, cell-height image enumeration, never the minimum-image shortcut. The
profile is pure geometry, computed once per phase on the host in plain numpy; the kernel's own
`Forward` combines it with the carried point values through a bare multiplication, which assumes
both operands already share one engine, so `MessagePassingStack.Forward` casts the profile onto
whichever engine the carried values already belong to (`Matched_To_Values`, a member-local seam
using a lifted tensor's own `new_tensor` construction rather than a second dispatch primitive)
before either phase's layers run.

**Readout — `ProbeHead`.** `MultilayerPerceptron((64, 64, 2), "probe_head")`, applied to every
point's final features (called only on the probe rows in the assembled operator, since only probes
are queried, but the head itself is agnostic to which rows it is handed).

**Renormalization.** `Renormalized_To_Electron_Count` scales the density channel alone so its
full-grid integral equals the sidecar's own `electron_count`; the magnetization channel is left
untouched. Applied only at grid-discretization inference, never during probe-sampled training,
matching the canon's own "exact, free" framing of full-grid renormalization.

**Probe sampler — `ProbeBatchSource`.** Per step, two structures drawn with replacement, 1,000
probes each: half uniform in the fractional cell, half atom-centered. The atom-centered half picks
a uniformly random atom and adds a three-dimensional isotropic Gaussian offset of width 0.7
angstrom (drawn directly as a Cartesian 3-vector, not as a separately drawn radius and direction —
the two constructions are not the same distribution: a radius drawn as a bare one-dimensional
`|N(0, sigma)|` combined with a uniform direction has density `f_R(r) / (4 pi r^2)`, which diverges
at the origin, not the smooth three-dimensional Gaussian density `Mixture_Proposal_Density`
assumes; drawing the offset directly as `N(0, sigma^2 I_3)` is the standard, numerically well
behaved construction and is what is built and tested here). The proposal's own Cartesian density
(half constant `1/V_cell`, half the atom-centered Gaussian mixture, periodic images summed by cell
height out to a `4 sigma` margin) gives each probe a self-normalized importance weight
`1 / q(x)`; the per-structure loss is `sum(weight * pointwise_loss) / sum(weight)`, an unbiased
estimator of the uniform-cell average regardless of the arbitrary normalization constant dropped
from `q`. Probe targets are read by `Trilinear_Interpolate`, periodic (wraps at the grid boundary,
never assumes a padded edge); measured root-mean-square error on a smooth three-mode synthetic
field at the campaign's own 80-cubed resolution, 20,000 random query points, is in `report.md`
(regenerate with `python3 -m operators.deep_dft.report`) — order `1e-3`, consistent with a
second-order-accurate interpolant at this resolution against a field whose curvature scale is many
grid spacings wide.

**Floors — `deep_dft/floors.py`.** The superposed-atomic-density floor re-derives
`normalized_mean_absolute_error(superposed_atomic_density, charge_density)` per run rather than
reusing `operators.data.Superposed_Atomic_Density_Errors` directly, because that function returns
a bare array silently skipping runs whose fields are missing — this member needs the result keyed
by identifier to build `ScoredRun` rows without a silent identifier/value misalignment. Measured
over all 196 defect runs it reproduces stage zero's committed 14.96% almost exactly (14.959%,
n=189); measured on fold zero alone it is 15.09% (the two numbers differ because they are
different populations, not because of two implementations — this member's own gate rows use the
fold-zero number). The reduced-SALTED floor is a `Fit_Standardized_Ridge` from
per-`(species, width)` isotropic Gaussian shell densities (eight widths 0.3 to 3.0 angstrom,
log-ish spaced, periodic images by cell height out to a `4 x width` margin) onto
`charge_density - superposed_atomic_density`, fit on 1,000 mixture-sampled probes per training run
and scored on a fixed 5,000-point random subsample of each fold-zero run's own grid — a deliberate
cost tradeoff for the floor alone (the member itself is scored on the true full grid, per policy).
The nearest-structure-copy floor matches by per-element atom-count composition (not by lattice,
since every defect run shares one 64-atom cubic cell) and copies the neighbor's full density grid
verbatim; it is reported for context and carries no gate.

**Gate C.** `Moment_Gate_Row` and `Total_Moment` in `floors.py`: the "25 magnetic fold-zero runs"
are exactly those with `abs(final_magnetization) > 1e-3` in the stored OSZICAR echo — verified
against the corpus directly (this threshold selects precisely 25 of the 42 fold-zero runs, not an
estimate). Runs with a `magnetization_density` field whose grid-integrated absolute moment is
below `1e-6` electron-bohr-magnetons (a real ISPIN=2-but-non-magnetic case, distinct from the
`final_magnetization` selection above) are treated as carrying no usable magnetization for the
loss's own normalization, since the metric's normalizer divides by that integral and would raise
on an exact zero.

**Training readiness.** Not started under this policy (floors before training, and the card is
scheduled by the team lead). `ContinuousDisplacementKernel.Forward` and `Profile_Matrices` now
carry messages through `Scatter_Add` and `Einstein_Summation` on the dispatched substrate rather
than `np.add.at`/`np.einsum`, so the kernel differentiates on the foreign engine; this landed on
trunk after this member's own layers were written and reached this stream through the standard
rebase, alongside `Write_Member_Results`. One seam did need rework once the lift arrived: the
kernel's own `Forward` combines the caller's profile features with the caller's point values
through a bare multiplication, which silently assumes the two already share an engine, and this
composition was computing that profile on the host in plain numpy regardless of which engine
carried the point values — correct under `NumpyEngine`, a `TypeError` under `TorchEngine`. The fix
is `Matched_To_Values` in `message_passing.py`, applied once per phase; see the composition
section above. Everywhere else the package was already engine-dispatch-clean
(`Gaussian_Error_Linear_Unit`, `Concatenate_Channels`, `Zeros_Beside` from `operators.substrate`,
never a bare reference to the foreign engine or an engine-specific branch). Gradient correctness is
verified on the reference `NumpyEngine` (central differences,
`Test_Two_Path_Agreement_And_A_Gradient_On_Every_Parameter`) and, now that the lift is present, on
the foreign engine directly against that same central-difference reference
(`Test_Foreign_Engine_Forward_And_Gradient_Agree_On_A_Tiny_Structure`, skipped when the foreign
engine is unavailable) — every one of the tiny configuration's 23 named parameters carries a
finite, nonzero gradient there, matching the reference to `1e-4` relative.

## Inspection

`DeepDft.Inspect()` aggregates the encoder, composition and readout under `encoder.`,
`composition.` and `readout.` prefixes (the `NeuralOperator` default), plus the member's own
`last_predicted_grid` and `last_renormalized_grid`. Notable keys:

- `encoder.atom_embedding_table` (vocabulary x 64) and `encoder.last_vocabulary_indices` — the
  learned per-species rows and which one every atom in the last call resolved to, unknown row
  included.
- `composition.atom_atom_layer_{0,1,2}.kernel.*` and `composition.atom_probe_layer_{0,1,2}.kernel.*`
  — each layer's own `radial_weights`, sampled `profile_over_radius` curve, and last edge
  distances and output values, from `ContinuousDisplacementKernel.Inspect`.
- `composition.atom_atom_layer_{0,1,2}.local_linear.*` and the atom-probe equivalents — the local
  linear weights and biases.
- `composition.last_atom_count`, `.last_probe_count`, `.last_atom_atom_edge_count`,
  `.last_atom_probe_edge_count` — the last forward pass's own graph sizes.
- `composition.last_atom_to_probe_adjacency` (atoms x probes, zero-one) — this member's own
  figure: every probe inside the cutoff of every atom, periodic images included. Rendered by the
  shared generic suite (a two-dimensional array routes to `Render_Matrix` by rank alone), so no
  drawing code lives outside `operators/inspection/plots/`.
- `readout.last_predicted_values` — the probe head's raw two-channel output before any
  renormalization.
- `last_predicted_grid` / `last_renormalized_grid` — the full-grid call's density and
  magnetization channels, before and after the electron-count renormalization.

Every key above is rendered by `Render_Inspection_Suite` with none skipped
(`Test_Every_Inspect_Key_Renders`), and `report.py` caches the raw arrays under
`/Pool/VASP_DATA/_derived/_figures/deep_dft/` before drawing the committed PNGs under
`operators/deep_dft/figures/`.

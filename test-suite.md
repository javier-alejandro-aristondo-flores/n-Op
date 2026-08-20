# The Operator Test Suite

**Successor to `operator-list.md`.** Built data-first on 2026-08-19 from the corpus census
(`/Pool/VASP_DATA/_census/ANSWERS.md`, 2026-08-12) and ten independent feasibility drills, each of
which re-verified its own data counts on `/Pool` and its own citations against the literature.
Every member below is a **named, literature-published operator architecture**; every count is
traceable to a command in the verification appendix (§12).

---

## 0. Charter

**What a member is (the operator gate).** A suite member maps between function spaces. It must
have at least one of:

1. **Field/function input and output** with a genuine discretization-robustness story — spectral
   parametrization on a fixed mode set (Fourier lineage), query-anywhere decoding (trunk networks,
   probe points), or alias-free bandlimited design (CNO lineage);
2. an **operator-theoretic mechanism** — an implicit fixed point living in a function space
   (deep-equilibrium lineage).

**No pure neural nets.** Fixed-vector→fixed-vector predictors are excluded regardless of pedigree
(CGCNN, ALIGNN, Mat2Spec, DOSTransformer, message-passing interatomic potentials). Scalar
quantities (band gaps, energies) enter the suite only as *functionals of predicted functions* —
auxiliary read-outs, never members and never training targets in their own right.

**In-house gate.** Everything will be built against the project's own automatic differentiation
(implementation language still open; polyglot acceptable; not Rust; no external deep-learning
frameworks). Specs are therefore written against **required primitives** (§10), not a language.
Public reference code is cited only as a correctness oracle.
*Open decision, deferred to implementation (Javier, 2026-08-19, not final): whether vendor math
libraries (FFT, BLAS) may be wrapped as opaque kernels. Direction of travel is fully in-house
(own FFT, own AD) with low-level GEMM substrate tolerated. Both cost figures are carried for every
Fourier-lineage entry; no verdict hinges on the choice.*

**Compute tiers.** Every member is fully specified now; each entry carries one of:
- **LOCAL-NOW** — trains on the resident machine (RTX 2060, 6 GB VRAM; 31 GiB RAM; 16 threads).
- **SUPER-LATER** — spec complete; runs when supercomputer access arrives.
Only LOCAL-NOW entries are implemented and run in the first build.

**Out of scope, permanently, for this suite:**
- **Learned SCF acceleration** (the sibling project's territory). Fence, enforced on sight: no
  supervising on SCF iterates; no model inside any DFT loop as initializer/mixer/preconditioner;
  no scoring by SCF-steps-saved; no feeding model output back into VASP.
- **Interatomic-potential training** on the relaxation pool (excluded class; its proper uses are
  recorded in §8 for a different project).
- **Corpus-invented benchmarks**: every task here has literature precedent as an operator task.

**The never-pool rule.** The corpus carries three exact-exchange fractions — AEXX **0.27**
(diamond strain atlas), **0.25** (defect set + one pristine reference), **0.325** (alloy ensemble,
on a PBEsol base) — plus PBE, PBEsol, and +U flavors. "HSE" quantities are different targets per
campaign. Δ-operators are per-campaign; metrics are reported per campaign *and* per functional,
always; a pooled "universal hybrid-functional corrector" is not a legitimate claim on this corpus.
Cross-campaign weight sharing exists only as explicitly labeled transfer or conditioning
experiments.

---

## 1. The data, named

English block names (project convention: corpus-invented names are spelled out; symbols live in
equations only). Counts as verified 2026-08-19.

| Block | Campaign | Contents | Key numbers |
|---|---|---|---|
| **Strain Atlas** | `diamond/2_atoms_4-10-2026` | 2-atom diamond under 1–6-axis strain; PBE + HSE(0.27) at every point, HSE restarted from the PBE wavefunction (geometry byte-identical) | 2,680 runs = **1,340 points × 2**; charge density only, ~40³ grids (36–48 on strained axes); 172 irreducible k everywhere; gaps PBE 0.441–4.806 / HSE 1.497–6.137 eV; 24 byte-alias triples → 1,131 distinct frozen points + 160 new + 1 reference; **~299 exchangeable orbit units for label tasks** (§9.2) |
| **Supercell Strains** | `diamond/Pure` | 64-atom pristine diamond strains, PBE, spin-polarized (moments ≈ 0) | 200 runs; 120 shears on the *identical* g-grid as the Strain Atlas shear family (119 usable for ρ/V); full-field on 169; shears uniform 80³; one PBE+HSE(0.25) pristine reference pair |
| **Defect Set** | `diamond/{single,pair,triads,new-only}` | 64-atom diamond defects, PBE 100 / HSE(0.25) 96, spin-polarized | 196 runs → **189 distinct fields** (byte-copy exclusions); all full-field 80³; 113 magnetic; 57 dopant elements; 8 irreducible k; **56 byte-verified same-geometry PBE↔HSE pairs** (chained campaigns) + 37 independently-relaxed pairs (drift-stratified); 12 relaxations hit the step cap |
| **Perovskite Grid** | `ggapbe` | AgNbO₃ 5-atom cell on two 5³ factorial lattice sweeps (lengths; angles). **PBE, not hybrid** | 250 runs → 249 distinct (shared center); charge density only; angle sweep uniform 64³; gaps 0.000–1.680 eV (median 0.057), 4 exact metals; fractional-occupancy flags on 106/125 angle-sweep runs; 260 irreducible k |
| **Alloy Ensemble** | `alloy` | β-(Al<sub>x</sub>Ga<sub>1−x</sub>)₂O₃, 20-atom monoclinic, PBEsol; disorder ensemble + volume series + 9-composition pipeline | 182 runs, all full-field; grids 48×96×216-class (7 variants); 76 disorder configs; **9 PBEsol↔HSE(0.325) pairs, byte-identical geometry; 7 of 9 same-k** (§11.1); HSE gaps 4.62→6.96 eV |
| **Relaxation Pool** | `j-dataset` | 1,500 Materials-Project oxide semiconductors + 76 element references, PBEsol (+U on 289), cell+ion relaxations | **No volumetric data.** 30,487 force+stress-labeled ionic steps over 1,482 runs (median 14); gaps on 1,437 (0.004–7.14 eV); irreducible k 4–397 (median 27); 73 dead runs |
| **Paired Fields** | Alloy + Supercell + Defects | Same-run field sets: charge density (+magnetization), ELF, total local potential, all-electron core/valence densities | **547 = 182 + 169 + 196**; the flagship block for field→field operators |

**Two laws of the Paired Fields block.**
1. **The half-grid law.** ELFCAR is written on the half-resolution wavefunction grid, exactly half
   per axis, corpus-wide (80³→40³; 48×96×216→24×48×108, all alloy variants verified). ELF is a
   *coarse-grid pointwise evaluation*, not a filtered decimation — heads live at the coarse scale;
   never train fine-then-downsample. There is **no fine-grid ELF ground truth anywhere**, so
   super-resolved ELF output is a self-consistency check only, never a headline.
2. **The spin-block law.** Under spin polarization (all Supercell Strains and Defect Set runs, 18
   alloy pipeline runs) *every* field file doubles: CHGCAR = (ρ, m), **ELFCAR = (ELF↑, ELF↓),
   LOCPOT = (V↑, V↓)** — verified independently by three drills; absent from the census. AECCAR
   files stay spin-summed. Channel counts are therefore heterogeneous across and within blocks
   (token count 5→8); real magnetic signal exists only in 113 Defect Set runs.

**File conventions every parser must honor:** CHGCAR grids store ρ·V<sub>cell</sub> (verified:
grid-mean = NELECT to 6 digits) followed by augmentation-occupancy text blocks (parsed past, never
regressed) and, when spin-polarized, the magnetization block with its own augmentation. LOCPOT is
the *total* local potential (LVTOT everywhere; no LVHAR anywhere), eV, with no absolute zero in a
periodic cell. ELF is dimensionless in [0,1]. POTCAR files are license-restricted: contents are
never quoted, and POTCAR-derived artifacts never leave `/Pool`.

---

## 2. Pattern I — grid field → grid field (Paired Fields, 547)

Tasks: **ρ→ELF** (the flagship: ELF needs orbital information the density alone lacks — genuine
physics; prior-art note below) and **ρ→V** (retained as a *calibration probe*: the
Hartree part is an exact Fourier multiplier, so the honest question is only whether anything beats
the physics floor, §9.6). Channel convention: 2-in (ρ, m) / 2-out per the spin-block law, with
m ≡ 0 injected for spin-restricted runs; functional identity (PBE / PBEsol / HSE-0.25) enters as a
conditioning input or a split axis — orbital-dependent targets across mixed functionals are
label-heterogeneous otherwise. Splits: grouped, stratified, byte-copies deduplicated first (§9.2–3).
**Pattern rule:** every member must beat the semilocal pointwise ELF floor (§9.6) by ≥ 20% to
stay on the ρ→ELF task; the flagship entry carries its own stricter bar.

**Prior art on the flagship (post-delivery audit, 2026-08-19).** A geometry→ELF neural network
now exists: ELF topology of dense hydrogen from atomic positions (arXiv:2604.26445 / Chem. Eur.
J. 2026 — R² 0.992, MAE 0.019; single element, pure NN, no operator structure). The flagship
claim is therefore stated precisely: **ρ→ELF as operator learning, on multi-species solids, with
discretization-transfer protocols** — and the hydrogen model's MAE 0.019 becomes an external
calibration point from an easier system. Adjacent: V2Rho-FNO (arXiv:2603.15669) learns
potential→density with an FNO — the reverse direction of this pattern's ρ→V probe.

#### I.1 — Factorized Fourier Neural Operator (F-FNO) · **IN-LOCAL · flagship**
**Operator.** F-FNO: Tran, Mathews, Xie, Ong, ICLR 2023 (arXiv:2111.13802); parent FNO: Li et al.,
ICLR 2021 (arXiv:2010.08895). Gate: weights live on a fixed set of Fourier modes of the torus —
the same parameters evaluate on any grid; the 80³→40³ half-grid map is *natively* spectral
truncation inside the operator. Separable per-axis spectral weights make full-Nyquist modes
affordable in 3-D — the reason F-FNO leads the lineage here.
**Design.** Truncate-early: lift on the fine grid → one real FFT → truncate to the coarse Nyquist →
all Fourier layers at 40³ → ELF head on the coarse grid. Input log(1+ρ/ρ₀) (the density spans 2+
decades; dynamic range is the Gibbs driver); ELF head 1/(1+softplus²) matching ELF's defining
form; 6 Gram-matrix channels + per-mode |k_phys|² spectral features (non-orthogonal cells; for
ρ→V the metric is mandatory: V_H(k) = 4πρ(k)/|k|²). Config: width 64, 12 layers, modes 20³ (full
Nyquist at 40³) ≈ 8M params. Vanilla-FNO comparator (w32, 4 layers, 12³ modes, 56.6M) kept as the
capacity ablation. Two free exact constraints at inference: predicted densities renormalized to
the run's electron count; the potential head's uniform (G=0) mode pinned to zero, matching the
gauge convention (§9.4).
**Compute.** ~1.7 GB fp32 at batch 1–2 (alloy grids ~2.5 GB) — fits; epochs 30–60 s; full training
6–12 h local. The full-width fine-grid trunk (9+ GB) is the one SUPER-LATER ablation.
**Floors & kills.** ρ→ELF: kill unless < 0.5× the semilocal pointwise floor (ridge/MLP on ρ, |∇ρ|,
∇²ρ — the Savin/Tsirelson-style approximate ELF) on held-out Defect Set chemistry with sweep-arm
splits. ρ→V: if not > 2× better than the canonical spectral-Poisson + semilocal-XC floor (§9.6), record "physics floor
suffices" and keep the task as a pipeline unit test — a finding, not a failure.
**Risks.** FFT-substrate decision (§0); Gibbs at bond/core discontinuities (log-compression + full
Nyquist is the mitigation, CNO is the architectural hedge); correlated-sweep leakage.

#### I.2 — Convolutional Neural Operator (CNO) · **IN-LOCAL**
**Operator.** Raonić et al., NeurIPS 2023; alias-free formalism in Bartolucci et al. (ReNO),
NeurIPS 2023. Gate: operator between bandlimited function spaces — convolutions of fixed physical
support, sinc up/downsampling, activations applied at 2× sampling rate. On our periodic tori the
story *strengthens* (DFT sinc resampling is exact). Honesty: paper and official code are 1-D/2-D;
**no 3-D CNO exists in the literature — the 3-D validation is ours to produce**, and that is part
of this entry's value.
**Design.** ELF head on CNO's own second scale (exact half-grid match — zero extra machinery);
2-channel spin convention; 6 metric channels for varying cells (ablate; fallback per-campaign).
Config: 4 scales 80→40→20→10, widths 32/64/128/256 ≈ 9M params.
**Build (the entry's identity).** The **fused activation-resampling kernel (act2x) with a custom
VJP** — upsample ×2 → nonlinearity → downsample ×2, tile-streamed so the 8× intermediate never
materializes. Naive AD OOMs the 6 GB card; fusion is *mandatory, not an optimization*. ~1.6–2.0
kLoC; alias-free surcharge ≈ +40% kernel effort over a plain U-Net.
**Compute.** 1.3–1.8 GB fp32 checkpointed (alloy 3.4 GB) — fits; 5–7 min/epoch over the 547; 500
epochs ≈ 1–2.5 days local.
**Floors & kills.** Shares I.1's floors, plus its own identity check: CNO must match-or-beat a
width-matched plain U-Net at native grids **and** degrade at most half as much under grid-shift
probes (the 21 axis-stretched 72–84 cells; sinc-resampled inputs). If CNO ≈ U-Net on both, the
alias-free surcharge is unearned → entry REJECT. Kill ρ→ELF if < 20% better than the pointwise
semilocal floor (the pattern rule, §2 — map effectively local).
**Risks.** act2x is novel engineering; 547 samples vs 9M params (symmetry augmentation mandatory);
low-frequency ρ→V tail favors the Fourier lineage.

#### I.3 — Deep Equilibrium Fourier Operator (FNO-DEQ), with the weight-tied ladder · **IN-LOCAL · sequenced after I.1**
**Operator.** DEQ: Bai, Kolter, Koltun, NeurIPS 2019. FNO-DEQ: Marwah et al., NeurIPS 2023
(arXiv:2312.00234). Gate: the fixed point is a multi-channel field over the cell; the tied block
is an FNO kernel-integral operator; the model is the implicitly defined operator input →
equilibrium field. All published evidence is 2-D ≤ 128²; **80³ is unmapped**.
**The experiment (why this entry exists).** A three-rung ladder on identical splits — explicit
FNO → weight-tied unrolled FNO → FNO-DEQ — isolating what weight-tying buys from what implicit
depth buys. Measured up front: ~¾ of the memory advantage is weight-tying alone; the honest
deliverable is the decomposition curve, not an "O(1) memory" headline. "Weight-tying yes, DEQ no"
is a legitimate suite verdict and will be reported as such if the middle rung matches.
**Build.** +600–900 lines on the I.1 stack (~85% shared). Forward: damped Picard baseline, then
Anderson acceleration m=3–5 (m×m Tikhonov least squares on CPU; restart on ill-conditioning;
tolerance 1e-3; cap 32). Broyden rejected at this scale (≈4.2 GB of update history). Backward,
ranked by AD demand: Jacobian-free (debug floor) → **phantom gradients S ≤ 3 (default — requires
the tape to accumulate shared-parameter gradients across chained applications of one weight set)**
→ exact implicit-function-theorem adjoint (needs a tape replayable as a linear operator; the audit
tool). Stability escalation: damping → per-mode spectral clipping → Hutchinson Jacobian penalty →
monotone parametrization. **Mandatory 8³ gradient audit** (phantom vs IFT vs finite differences vs
full unroll) before any 80³ run; every later anomaly re-runs it before hyperparameters move. fp32
only on this card.
**Compute.** Peak 1.3 GB at paper scale (explicit comparator 1.8 GB); at width 64 the explicit
model busts 6 GB on optimizer state (8.6 GB) while FNO-DEQ fits (4.1 GB). Step overhead ≈ 3.5–4×;
~80 s/epoch on the 547; hours per run. Inference is tape-free: 160³ discretization-transfer demos
fit locally.
**Floors & kills.** Kill benchmark: explicit FNO at matched *total* parameters (both matchings —
same-width and matched-params), 3 seeds; kill if not better while ≥ 3× wall-clock. Health floor:
≥ 90% of validation samples converge to 1e-3 within 32 iterations after tuning (kill < 80%).
Residual-vs-error correlation logged (flags non-contractive learned maps).
**Risks.** Fixed-point nonconvergence at 3-D scale; phantom-gradient bias at small n; solver and
model failures entangle (the audit rule exists for this).

#### I.4 — Galerkin Transformer with query-point decoding (merged GT + OFormer) · **IN-LOCAL**
**Operator.** Galerkin Transformer: Cao, NeurIPS 2021 (softmax-free attention as a learnable
Petrov–Galerkin projection; tokens are grid samples with continuous coordinate features). OFormer:
Li, Meidani, Farimani, TMLR 2023 — merged in, contributing exactly one thing: the cross-attention
decoder over *output-coordinate queries*, which is what serves the half-grid ELF head. One build,
not two: as standalone entries they are redundant.
**Why it's tractable.** Linear attention is O(N·d): 64³ native ≈ 3.8 GB; 80³ ≈ 2.9 GB *with
layer-granular gradient checkpointing*; alloy grids only at reduced width (else SUPER-LATER).
Dense softmax attention is dead at every resolution in scope (65 GB/layer at 40³) — recorded in
§8. **No surviving configuration uses patching**: patches would tie the embedding to a fixed
resolution and forfeit precisely what this corpus can test; a patched ViT exists only as a labeled
ablation.
**Build.** Attention core = two GEMMs per head (no custom kernel); the hard parts are
checkpointing inside our own AD (the critical path for ≥ 80³ — slippage collapses scope to 64³),
stable layer-norm backward at N ≈ 10⁶, and an fp16 loss scaler on this card. ≈ 1M params;
~2–2.5 kLoC.
**Floors & kills (staged, cheap-first).** Perovskite Grid 64³ is the proving ground: beat
nearest-angle field copy AND linear-in-angle interpolation by ≥ 2× within ~2 h of wall-clock, or
the field→field attention entry dies before any 80³ spend. Beat the pointwise semilocal floor by
≥ 20%. **Cross-entry kill: on ρ→V, land within 1.5× of I.1's error on the same split or the
attention V-task retires.** 80³ envelope: ≤ 5.5 GB and ≤ 2 s/step checkpointed, else SUPER-LATER.
**Risks.** Per-head low-rank global mixing can blur sharp defect/ELF detail (the staged gates
front-load this); channel heterogeneity across the 547.

---

## 3. Pattern II — parameters → field

The corpus's parametric families: **Strain Atlas** strain → density (2,582 deduplicated fields =
1,291 distinct points × two functionals — the largest homogeneous parametric set), **Perovskite
Grid** lattice → density (249), **Supercell Strains** shear → density (119; transfer/eval only —
underpowered standalone). Varying grids (15 shapes in the Strain Atlas, per-cell grids in the
Perovskite length sweep) are this pattern's native advantage: voxel centers are exact fractional
coordinates, so no resampling exists anywhere in the pipeline. Leakage discipline is the orbit map
(§9.2): exact symmetry degeneracy makes naive random splits test-on-train.

#### II.1 — DeepONet, POD-DeepONet, PCA-Net · **IN-LOCAL · cheapest builds in the suite**
**Operators.** DeepONet: Lu, Jin, Pang, Zhang, Karniadakis, Nat. Mach. Intell. 3:218 (2021) —
branch on parameters, trunk on fractional coordinates with integer-frequency Fourier features
(exact periodicity); the trunk makes the output a genuine function queryable anywhere. POD-DeepONet:
Lu et al., CMAME 393:114778 (2022). PCA-Net: Bhattacharya, Hosseini, Kovachki, Stuart, SMAI-JCM
7:121 (2021). Gate honesty, stated in the doc as in the drill: the coordinate-trunk variants are
the canonical members; POD/PCA variants sit at the gate's edge (their query-anywhere property is
interpolated through stored modes) and are labeled accordingly.
**Tasks.** (a) strain→ρ on the Strain Atlas — the pattern flagship; (b) lattice→ρ on the
Perovskite Grid (extrapolation split: hold out all factor-0.8 runs, separately 1.2); (c)
projection-based ρ→ELF and ρ→V on the Paired Fields — **conditional, gated by a measured Stage-0
POD spectrum per campaign** (GO iff ≤ 3% reconstruction error at rank ≤ N/2; the Defect Set is the
expected failure — moving localized features are the classic POD killer; a failing block stays
with the grid-native pattern-I members).
**Build.** No FFT, no convolution, no attention: ~8 kernels, ~5 kLoC (GEMM+MLP+Adam, periodic
trilinear gather, fp64 Gram POD — 365×512k snapshots ≈ 0.25 TFLOP, seconds of BLAS, < 4 GiB; the
one-time ~20 GB text parse dominates). All configs ≤ 1M params. This family plus floors is Wave 1:
it validates the tensor store, splits, and metrics end-to-end before any spectral kernel exists.
**Compute.** Point-sampled training: memory O(batch), never O(grid) — ~70 ms/step at 131k
point-evaluations; a full model in 40–60 min on the 2060; PCA-Net in minutes on CPU.
**Floors & kills.** Ridge from parameters to POD coefficients (closed-form; the natural floor):
kill any DeepONet variant not ≥ 25% better on held-out strain families. 1-NN field copy in
parameter space (factorial sweeps make it strong): require ≥ 2×. Linear PCA-Net vs MLP: if the MLP
is ≤ 10–15% better, keep the linear model and kill the neural claim.
**Twin-axis note.** For the Supercell evaluation the branch–trunk family has **no torus mismatch**
(fractional trunk + continuous lattice parameters; tile the primitive-cell prediction 2×2×2) — but
the Strain Atlas has no combined shear+volume family, so the twin query composes two axes never
seen jointly, on top of the basis-set systematic: scored as a *transfer probe*, never an accuracy
headline.

#### II.2 — MIONet (ρ, V) → ELF · **IN-LOCAL · add-on**
Jin, Meng, Lu, SIAM J. Sci. Comput. 44(6):A3490 (2022). Two branches (ρ-projection, V-projection)
+ shared trunk; ≈ 0.6M params; rides II.1's entire stack and the same POD gate. Kill: if adding V
improves ρ→ELF by ≤ 5%, V adds nothing — drop the task.

#### II.3 — NOMAD (nonlinear manifold decoder) · **IN-LOCAL**
Seidman, Kissas, Perdikaris, Pappas, NeurIPS 2022 (arXiv:2206.03551). Pointwise nonlinear decoder
over output coordinates breaks the linear-reconstruction ceiling that limits POD-based members;
< 0.5 GB at any grid; natively consumes the Strain Atlas's varying grids. Restricted to parametric
tasks (its global-latent bottleneck disqualifies field→field 512k-point inputs; ρ→V allowed only
as a kill-gated baseline). **The operator badge is earned on grid transfer:** error inflation
≤ 1.3× when evaluated on off-dominant grids (36/48-axis Strain Atlas cells); beat RBF/linear
parameter-interpolation by ≥ 1.5×.

#### II.4 — Parametric F-FNO (+ FNO-DEQ steady-state variant) · **IN-LOCAL**
Parameters broadcast as constant channels into the I.1 backbone; the operator character is the
resolution-invariant query, stated plainly (params→field is parametric regression at heart — the
gate case is the weakest in the suite and the doc says so). Blocks: Strain Atlas (~1.2 GB, batch
4–8, 40–80 s epochs), Perovskite 64³, Supercell 119. FNO-DEQ variant on the Perovskite angle sweep
(steady-state framing = honest motivation, hypothesis-grade prediction). **Decisive floor for both:
linear interpolation of ρ between bracketing parameter values** — on smooth factorial sweeps it is
brutal, and the likely outcome is that it wins on interpolation splits; that result is informative
and will be reported, not buried. Kill unless < 0.7× best floor on leave-one-arm-out.

---

## 4. Pattern III — structure → queryable field

**Gate preamble (this pattern's argument).** Input: the atomic configuration as an empirical
measure Σᵢ δ(r−Rᵢ) ⊗ e_{zᵢ}. First layer: an integral operator with a learned continuous kernel
evaluated against that measure. Output: a field evaluated at *probe points* that join the message
graph but only receive messages — queryable at any r, differentiable in r. The map is measures →
C(T³): an operator with mesh-free queries. Grids supply supervision points, never model shape —
and this corpus exercises that claim directly (one member consumes 40³, 64³, 80³, and 48×96×216
supervision). Voxel-to-voxel networks are excluded exactly here.

#### III.1 — DeepDFT (invariant), with the PaiNN-equivariant upgrade as the stretch · **IN-LOCAL · anchor**
**Operator.** Jørgensen & Bhowmik, npj Comput. Mater. 8:183 (2022) — both variants are in the
paper; probe-point mechanism per the preamble.
**Tasks.** (a) Defect Set structure→ρ(+m) — the highest-value slice (189 distinct fields, 57
dopant chemistries, all full-field; ELF as a secondary head; V exploratory only — long-range
electrostatics likely violates the 4 Å locality, predict V−⟨V⟩ and expect little); (b) Alloy
Ensemble configuration→ρ (76-config disorder — the literature's own NMC benchmark is exactly this
shape); (c) Strain Atlas / Supercell strain→ρ (structure encodes strain natively; the big-n
block). Cross-campaign zero-shot (train diamond, infer Perovskite/Alloy) is a *diagnostic axis*:
species embeddings are warm (all of Ag, Nb, O, Al, Ga occur as Defect Set dopants), failure is the
expected calibration result, and the Nb PAW-variant clash plus the PBE→PBEsol shift are printed on
the plot.
**Spin (a modest, honest novelty).** The literature predicts total density only; this suite adds a
(ρ, m) two-channel head — m-loss normalized by ∫|m|, masked for spin-restricted campaigns, scored
only on the 113 magnetic runs.
**Build.** Periodic radius graphs — **skew-safe image enumeration by cell heights (nᵢ =
⌈r_c/dᵢ⌉, dᵢ = V/|aⱼ×aₖ|, exact distance filter); minimum-image shortcuts are wrong in the
monoclinic alloy cell.** Sinc radial basis (20 fns) + cosine cutoff; filter-generating MLPs;
gather/scatter message passing (atoms→atoms, atoms→probes); 2.1M params; ~3–5 kLoC, 4–6
person-weeks. Hardest kernel: batched scatter-add and its AD rule on GPU — **own-AD scatter
performance is this entry's schedule risk** (a 5× slowdown vs framework baselines turns Strain
Atlas training into weeks). PaiNN upgrade: +ℓ=1 vector channels via scalar–vector products, no
Clebsch–Gordan tables, 1.5M params, +2 pw — buys the paper's largest error reductions.
**Probe sampling.** Mixture sampler (uniform + atom-centered radial), de-biased by
inverse-proposal weights — the paper's own error analysis concentrates mass in atom-centered
volumes. Predicted densities are renormalized to the electron count at full-grid inference
(exact, free).
**Compute.** Probe minibatches (2 structures × 1000 probes) ≤ ~3 GB — fits with ≥ 2× headroom;
Defect-Set-scale training 1–2 days, Strain-Atlas-scale 2–5 days on the 2060; full-grid inference
~1 min/structure; whole campaigns RAM-resident.
**Floors & kills.** Gate A: ≥ 10× better than the SAD floor (superposed atomic densities —
**already on disk as AECCAR1 for all 547 runs**; built from POTCAR radial densities for the other
blocks, artifacts staying on `/Pool`) on held-out-chemistry Defect Set splits, target ≤ 0.5%
normalized MAE. Gate B: ≥ 3× better than the reduced-SALTED floor (see below). Gate C (spin):
m-error ≤ 5% with correct total-moment sign on ≥ 90% of magnetic runs. Any gate failed after the
full budget (both samplers tried) kills the task; two tasks killed removes the member.
**Pattern floor.** Reduced SALTED (ℓ=0): per-species Gaussian shells, closed-form ridge on probe
samples — "SAD + learned isotropic corrections" (~1–2 kLoC). Full SALTED (λ-SOAP, CG products,
periodic density fitting) is 6–10 kLoC — *not* a cheap floor; cited (Grisafi et al., ACS Cent.
Sci. 2019; Lewis et al., JCTC 2021) and shelved.

#### III.2 — ChargE3Net · **SUPER-LATER (capability-qualified)**
Koker et al., npj Comput. Mater. 10:161 (2024). Passes every scientific gate (same probe
mechanism, E(3)-equivariant features to ℓ=4). Deferred on two grounds, both honest: (i) the
in-house build is the suite's largest single item (spherical harmonics to ℓ=4, Wigner/CG tables,
tensor-product path bookkeeping, equivariance test harness: ~8–15 kLoC, 12–20 person-weeks —
the machinery e3nn spends its life optimizing); (ii) the papers' own numbers show **parity with
equivariant DeepDFT on exactly our data regime** (single-host site-occupation: 0.060% vs 0.061%),
with higher-ℓ gains appearing on chemical diversity this corpus doesn't have. Revisit when III.1
measurably plateaus *and* the supercomputer arrives.

#### III.3 — GPWNO · **candidate pending drill (found in post-delivery audit; NOT an entry)**
Gaussian Plane-Wave Neural Operator (arXiv:2402.04278): structure→density with a plane-wave
global branch + Gaussian local basis — a named operator the original sweep missed, and one that
shares the suite's batched-FFT primitive with the Fourier lineage. Recorded as a candidate only:
the suite admits no undrilled members. Admission path = a feasibility drill on the same schema as
the other ten (verified counts, in-house primitive spec, 6 GB math, floors, kills).

---

## 5. Pattern IV — cross-fidelity Δ operators

**Pair inventory (all byte-verified).** Strain Atlas: **1,339 same-geometry PBE↔HSE(0.27) pairs**
(HSE restarted from the PBE wavefunction; relaxed-geometry handoff byte-identical; + 1 reference
spare) — the largest clean cross-fidelity field-pair set anywhere in the corpus, on ~40³ grids.
Defect Set: **56 distinct same-geometry pairs** (the chained campaigns: single 19 + pair 16 +
triads 24, minus byte-copies) + **37 independently-relaxed pairs** (new-only campaign; geometry
drift bimodal — median 0.007 Å but 7 pairs > 0.05 Å up to 0.759 Å — stratify, and keep drifted
pairs out of headline numbers). Alloy Ensemble: 9 pairs, byte-identical geometry; **7 of 9
on identical 36-point k-lists** (explicit KPOINTS both stages); the endpoints (x=0, x=100) have
no stage-3 KPOINTS file, so KSPACING=0.35 governs there — 30 vs 36 irreducible points, a
registered k-mesh confound on exactly those two pairs (§11.1). Eval-only at n=9 (7 clean). Supercell Strains: one
pristine PBE+HSE(0.25) pair — a single-point sanity probe for Defect-Set-trained operators.

**Gate boundary.** Members: ρ_PBE→ρ_HSE (field→field) and DOS_PBE(E)→DOS_HSE(E)
(function→function). Scalar gap Δ-regression is a pure-vector task — excluded as a member; it
enters only as an auxiliary head or as a functional read-out of a predicted field/spectrum. The
conformal wrapper is a wrapper, never a member.

#### IV.1 — Residual Δ operator, ρ_PBE→ρ_HSE on the Strain Atlas · **IN-LOCAL · best local-first science in the suite**
**Named lineage.** Δ-learning: Ramakrishnan, Dral, Rupp, von Lilienfeld, JCTC 11:2087 (2015).
Multifidelity operator form: Howard, Perego, Karniadakis, Stinis, J. Comput. Phys. 493:112462
(2023) — whose composite architecture *degenerates to the residual form here* because the
low-fidelity field is given, stated rather than cargo-culted. Cross-fidelity transfer:
Subramanian et al., NeurIPS 2023 (arXiv:2306.00258).
**This is a precision task.** Measured: the identity floor (submit ρ_PBE unchanged) sits at
**1.11–1.19% relative L2**; a global affine map explains almost nothing beyond it (1.05–1.10%,
a ≈ 0.993). All metrics are therefore Δ-normalized — headline = ΔR² = 1 − ‖ρ̂−ρ_H‖²/‖ρ_H−ρ_P‖².
**Design.** Backbone from I.1 (or POD-DeepONet from II.1 — both ride existing stacks; this entry
owns only the Δ-specific pieces): residual head with **zero-initialized last layer, so training
starts exactly at the identity floor**, and mean-projected — **∫Δρ dV = 0 exactly** (both
fidelities share the electron count): a free, exact conservation constraint; FiLM conditioning on campaign/AEXX (per-campaign default,
the conditioned single model is the labeled ablation); Subramanian-style transfer protocol to the
Defect Set's 56 pairs (freeze spectral weights, tune lift/project + FiLM, spin-channel adapter).
**Compute.** The whole pair set is 0.66 GB fp32 — resident in VRAM outright; batch 8–16 at 40³;
epochs in tens of seconds; full runs in hours. Uniquely local-friendly.
**Floors & kills.** Identity; global affine; ridge on POD(Δρ) coefficients. **Kill: the member
must reach ≤ 0.5× identity (≈ 0.56% rel-L2), i.e. explain ≥ 75% of ‖Δρ‖².**
**Auxiliary gap read-out (not a member).** The measured scissor floor is brutal: Δgap = 1.2612 ±
0.0317 eV over 667 CSV-joined pairs; a linear scissor leaves 31.7 meV std (R² = 0.9967). Any gap
head must beat ≤ 24 meV on orbit-held-out data including the triaxial family — and the floor is
recomputed from EIGENVAL over all 1,339 pairs before any number is locked (the CSV join misses the
low-gap tail). If the head only matches the scissor, that is the reported result.

#### IV.2 — Spectral Δ: DOS_PBE(E) → DOS_HSE(E) on the Strain Atlas · **IN-LOCAL · secondary**
Energy-trunk function→function map (the DeepONet form from II.1/VI.1). Honesty clause: at 172
irreducible k × 8 bands per side this is a *coarse spectral function*, not a converged DOS — the
map is well-posed because both sides are identically sampled (rebuild recipe and smearing per
§7's suite-wide rule); the energy window stops below the
top band's minimum (only 4 conduction bands exist); gap-edge error is the primary metric. Floors:
identity DOS; **scissor-warped DOS** (shift conduction manifold by the campaign scissor); beat by
≥ 25% windowed error or record the floor as sufficient.

#### IV.3 — Conformalized Quantile Regression wrapper · **IN-LOCAL · wrapper/floor, ~50 lines**
Romano, Patterson, Candès, NeurIPS 2019. Two-quantile pinball head (τ = 0.05/0.95) +
split-conformal offset, calibrated at the **orbit level** — the honest unit count is ~299
exchangeable orbits, not 1,291 points. Calibration math, stated in the doc: n_cal ≈ 60 → 90%
marginal coverage guaranteed in [0.900, 0.916] with realized-coverage std ≈ ±4%; n_cal ≈ 90
tightens to ±3.2%. Claims are marginal and orbit-level only — never conditional. Extension on the same machinery
(~50 more lines): sup-norm conformal *bands for field predictions* (functional conformal
prediction, Diquigiovanni et al. lineage), calibrated at the same orbit level — distribution-free
uncertainty for the Pattern-IV field outputs, not just their scalar read-outs.

---

## 6. Pattern V — multi-channel completion (Paired Fields as one object)

#### V.1 — Codomain Attention Neural Operator (CoDA-NO) · **IN-LOCAL**
**Operator.** Rahman et al., NeurIPS 2024 (arXiv:2403.12553; official code in `neuraloperator`).
Tokens are *channel functions* (ρ, m, ELF↑, ELF↓, V↑, V↓, core density, valence density);
K/Q/V are produced by spectral blocks whose weights are shared across tokens — which is what makes
the channel count variable; attention scores are L² inner products; masked-reconstruction
pretraining is *literally* the any-to-any completion task. Gate: every component is a
function-space map.
**Why it is uniquely tractable here.** Sequence length = channel count (5–8), so the attention
map is ≤ 64 entries and costs < 0.5% of a step — while any spatial-token transformer at 80³ would
need a 2.6×10¹¹-entry map. The corpus's channel heterogeneity (spin-block law: token count varies
5→8 across runs) is not a nuisance but the selling point being tested.
**Design.** Train on Supercell + Defect Set (365 runs, 80³-dominant); **the Alloy Ensemble is
held out entirely** as the discretization/geometry/functional transfer set, with 5/25/100-shot
fine-tunes — the exact analog of the paper's transfer protocol, making corpus heterogeneity the
headline generalization test. The deliverable includes the full any-to-any completion matrix —
including inverse reads ((ELF, V)→ρ; V→ρ) that no dedicated entry trains — with untrained
directions labeled exploratory. ELF half-grid: zero-invention default — Fourier zero-pad the ELF
channel to the fine grid at input; evaluate its loss on the native coarse points (the even-index
subsample). Spin-difference channels reparametrized as sum/difference (differences are near-zero
outside the magnetic Defect subset — demoted to auxiliary alongside m). Declared adaptations,
flagged as engineering not invention: the functional covariate (4 levels) as an embedding in the
variable-encoding slot the architecture already concatenates.
**Build.** Primitives 1:1 with the suite's shared list — per-channel spectral convolution
(token-shared weights), tiny T×T attention, learned-Fourier variable encodings, function-space
layer norm. **Hardest kernel is identical to I.1's (batched 3-D real FFT + complex contraction):
built once, shared.** ≈ 19M params fp32.
**Compute.** ≈ 2.6 GB fp32 at 6 tokens / ≈ 3.2 GB at 8 — fits; ~0.3–0.5 s/step, 3–5 min/epoch
over the block; a 200-epoch masked pretrain in 10–24 h local. (On this card "half precision"
means fp16 + loss scaler; there is no hardware bf16.) Alloy-grid full-resolution fine-tunes and
the ~50M Tucker-factorized config go SUPER-LATER.
**Data-volume honesty and mitigations.** 547 multi-channel samples vs the paper's 8k/40k
snapshots: exact grid-symmetry augmentation (all 48 diamond-group operations act exactly on even
80³ grids — the non-symmorphic quarter-shifts are exact 20-point rolls; ISYM=0 so no
symmetrization bias), mask multiplicity, and **density-only inpainting samples imported from the
Strain Atlas (2,680 @ 40³) and Perovskite Grid (250 @ 64³) — consumable only by a variable-channel
model**, which no dedicated pairwise competitor can use. Augmented views are correlated, not new
information — the low-data gate below stays the honest arbiter.
**Floors & kills (competitor = dedicated per-pair F-FNO at equal *total* GPU-hours, trained on
the same 365-run Supercell+Defect block — the Alloy Ensemble stays held out on both sides, else
the comparison is invalid).** Absolute bar for the V-read: the canonical spectral-Poisson +
semilocal-XC floor (§9.6), ≥ 30% or the read adds nothing over textbook physics.
K1: zero-shot masked completion > 2× the dedicated model on ≥ 2 pairwise tasks AND still > 1.25×
after fine-tuning → REJECT to the FNO bank. K2: the pointwise semilocal ELF floor lands within
20% (the pattern rule, §2) → the completion flagship deflates to the pairwise entries. K3: a 25%-of-Defect-Set low-data
test shows no pretraining advantage over a same-data dedicated model → the pretraining premise —
this entry's entire point — is dead here → REJECT. (At 547 samples the corpus sits permanently in
the paper's scarcity regime: the premise *applies*; K1/K3 test it rather than assume it.)

---

## 7. Pattern VI — spectrum as a function

#### VI.1 — DOS-DeepONet (energy-trunk) · **IN-LOCAL; Relaxation Pool tier is a stretch**
Branch on structure/strain parameters, trunk on energy: the output is DOS(E), a genuine function
queryable at any E; the band gap is a derived functional (support-edge read-out), reported as a
diagnostic only. Blocks, in order of label quality:
- **Strain Atlas** strain→DOS: 172 irreducible k, both functionals, 2,582 curves — excellent and
  homogeneous; the primary block (and IV.2's substrate).
- **Perovskite Grid** lattice→DOS near metallicity: 260 irreducible k; metallic points *keep*
  their fields and DOS (DOS at the Fermi level is signal); they are excluded only from gap-edge
  read-outs.
- **Relaxation Pool** structure→DOS: **stretch tier, behind the k-quality gate** — irreducible-k
  quartiles are 4/18/27/40/397, and below ~50 points the level spacing forces smearing so wide it
  destroys the features being scored. Tiers: ≥ 27 → 720 runs (permissive), ≥ 50 → 246
  (recommended), ≥ 64 → 156 (high-fidelity); the +U subset (55 of the 246) is a separate reporting
  stratum; the 82-dim composition descriptor is operator-legit but crude, and losing to the ridge
  floor is the budgeted outcome.
**Suite-wide DOS rule (from the drills, binding everywhere):** never read DOSCAR — the Defect
Set's tight-smearing population is unusable and consistency demands one recipe. Rebuild DOS from
EIGENVAL + IBZKPT weights: Gaussian smearing σ = 0.15–0.2 eV (Strain Atlas), 0.1–0.15
(Perovskite), 0.2 (Supercell/Defect, 8-k band-folding compensates); spin channels summed; curves
normalized per cell; window aligned to the valence-band maximum. Gaps always from the occupancy
walk, never from a DOS threshold.

#### VI.2 — Band-structure operator, strain → E_n(k) · **stretch, pending one design decision**
Branch on strain, trunk on (k, band index): 172 irreducible k × 8 bands × 2,582 spectra on the
Strain Atlas — strictly richer than DOS and the operator-legitimate refinement of every gap
read-out. Open question gating admission: band crossings (sorted-spectrum targets stay continuous
but lose band identity; band-tracked targets need connectivity resolution along strain paths).
Admitted as an entry only once that choice is made and its floor is spec'd (scissor-warped PBE
bands; per-band ridge on strain). Rides II.1's stack unchanged otherwise.

---

## 8. Rejected candidates — the rectification record

Every cut, with its load-bearing reason. Gate rejections cite the charter; feasibility rejections
were measured or verified, and are final on those grounds.

| Candidate | Class | Reason |
|---|---|---|
| LOCA (Kissas et al., JMLR 2022) | attention operator | Fixed-sensor input featurization never ingests a 512k-point field; built for the sparse-output regime — ours is the dense opposite; dominated within-group by NOMAD |
| Dense softmax attention (any ViT-style operator) | attention | 65 GB of attention matrices per layer at 40³ already; quadratic is dead at every resolution in scope |
| Transolver (Wu et al., ICML 2024) | attention | → SUPER-LATER shelf, not rejected: linear-complexity and a slim config fits, but its geometry-adaptivity is idle on all-uniform grids and its paper config needs ~19 GB at 64³ |
| EDMD / Koopman on the Relaxation Pool | evolution operator | Rank-starved (median 69-dim state vs 13 snapshot pairs; 39% of runs ≤ 10 steps); no shared phase space across 1,482 materials |
| Deep Koopman / VAMPnets on the Relaxation Pool | evolution operator | Cross-material observables require a permutation-invariant, size-extensive, 73-element chemistry encoder = exactly the excluded message-passing machinery — "an MLIP wearing an operator hat"; VAMP additionally needs a stochastic process with nontrivial slow spectrum, and a deterministic quench has neither |
| Neural ODE flow maps on relaxation paths | evolution operator | The recorded dynamics is a conjugate-gradient optimizer with line search — non-autonomous, history-dependent; not a flow. No published operator-learning precedent for emulating DFT relaxation paths (searched 2026-08-19) → corpus-invented task, banned |
| Pooled-Strain-Atlas EDMD | evolution operator | The one formulation that fixes the encoder problem (shared ~6-dof space, 2,669 pairs) still fails twice: near a quadratic minimum linear EDMD saturates (member can only tie its own floor), and the literature-recognized content is the static endpoint map — not an operator task. Optional non-member appendix: a one-day linear-algebra sanity build |
| MACE / NequIP / M3GNet fine-tuning on the 30,487 labeled steps | interatomic potential | Pure neural nets under the gate. For the record: this is a textbook MLIP pool, the 76 element references make formation energies computable corpus-wide, and 1,437 initial→relaxed pairs exist — all reserved for a different project |
| CGCNN / ALIGNN / Mat2Spec / DOSTransformer | property predictor | Fixed-vector outputs; gate |
| DeepRelax (Nat. Commun. 2024) | learned relaxation | Equivariant-GNN generative model — the excluded machinery; prior art only |
| Scalar gap / scalar Δ-gap as members | any | Vector regression; enters only as functionals of predicted functions. The measured scissor floor (31.7 meV residual on a 1.26 eV shift) is the standing warning |
| Plain 3-D U-Net as a member | convolutional | Grid-tied strides, aliasing activations — no function-space story; serves as CNO's floor |
| Naive Strain-Atlas↔Supercell zero-shot transfer | protocol | Different tori (primitive vs conventional cell) + 0.33% lattice-constant offset + basis change; survives only as the retiled protocol scored against the measured block-gap null (§9.5b) |
| Zero-shot super-resolved ELF as a headline | protocol | No fine-grid ELF ground truth exists anywhere in the corpus; self-consistency only |
| Full SALTED as a floor | kernel method | 6–10 kLoC of λ-SOAP/CG/density-fitting machinery is not a floor; replaced by the reduced isotropic form |
| Broyden fixed-point solver | DEQ internals | ~4.2 GB of update history at 80³; Anderson chosen |
| Pooled-AEXX "universal HSE corrector" | claim class | Three exact-exchange fractions are three different targets; the claim is invalid on this corpus |
| Any learned-SCF formulation | scope | The four-condition fence in §0; the sibling project's territory |

---

## 9. Cross-cutting protocol

### 9.1 Canonical tensor store (design — nothing is materialized until the build is approved)
`/Pool/VASP_DATA/_derived/<campaign>/<run_id>.npz`, one file per run (the run is the
split/exclusion unit; re-folding is a manifest edit, never a data rewrite), plus per-campaign
manifests. **fp32 for fields** (SCF convergence bounds physical content ~3 orders above fp32
rounding; halves I/O on the 6 GB card), **fp64 for scalars, geometry, DOS curves, and every metric
accumulation**. The sole baked transform: densities ÷ V_cell (e/Å³; volume kept). **No baked
standardization** — per-campaign statistics are computed on the train split only and applied at
load (baking them leaks test information into every twin/transfer axis). ELF stays raw [0,1];
potential stored raw with its spatial mean as a scalar.
**Size: ≈ 9.7 GB ≈ 8% of the 124 GB free** (core 7.9 GB + a deletable 1.5 GB floor cache). Not
materialized: CHG, WAVECAR, PROCAR, augmentation text, alias-copy payloads, any Relaxation-Pool
volumetrics (none exist), per-model prediction dumps (quota: metrics + ≤ 5 example fields,
transient).

### 9.2 Splits and leakage rules (enforced in code, not convention)
- **R1** Byte-alias groups are one datum (24 Strain Atlas triples; the Perovskite shared center —
  deduplicated, representative to train as the identity anchor).
- **R2** Functional pairs of one geometry co-split (Strain Atlas PBE+HSE; Defect pairs; Alloy
  stages).
- **R3** The Strain-Atlas↔Supercell twin shear grid (120 identical g-values) gets one canonical
  fold map reused by both campaigns whenever both are in play.
- **R4** The Alloy Ensemble splits by configuration, with each configuration's satellites (volume
  series + pipeline stages + the verbatim ensemble twin) as one unit (8×14 + 3 + 67 = 182 ✓).
- **R5** Sweeps are near-duplicates along the parameter: every number is labeled
  **interpolation** (grouped-random) or **extrapolation** (leave-level-out / hold-out-the-0.8s).
- **R6** Exclusions (§9.3) apply before splitting.
- **The orbit map (new artifact, required).** Measured on the Strain Atlas: gap labels are
  *exactly* degenerate across axis-permutation triples and shear sign/permutation orbits (≤ 0.1
  meV), and the triaxial family collapses 512 points → 120 permutation multisets (0.00 meV);
  two-shear families are near-degenerate (classes ≤ 71/173 meV — at or above the 32 meV learnable
  signal). Consequences: the 160-point auxiliary sweep contributes **zero** new labels (exact
  rotational copies — reserved as a built-in equivariance probe); label-task splits operate on
  **~299 orbit units, not 1,291 points**; the split generator consumes `duplicates.csv` + the
  orbit map + the twin/satellite maps, and any random split is invalid by construction.
- Schemes: Paired Fields — grouped stratified 5-fold over ≈ 341 units (Alloy by composition,
  Supercell by deformation family, Defects by chemistry class). Strain Atlas — fixed 80/10/10 by
  sweep family. Perovskite — 5-fold + the extrapolation variant. Full-CV cost is stated honestly:
  ≈ 150 trainings ≈ 1–2 GPU-weeks local — develop on fold 1; run the full 5-fold once per member
  for the final table. Cross-pattern comparisons (any two members on one task) are valid only on
  these canonical fold maps.

### 9.3 Exclusion registry (exact, enumerable)
| id | items | scope |
|---|---|---|
| E1 | Defect triads B-N-S `C8-C55-C1` branch (6 runs) — byte-copy of `C8-C53-C1` | all tasks |
| E2 | Defect Zr "HSE" ≡ PBE bytes (drift exactly 0.0000 Å — the byte-copy signature) | all tasks; keep the PBE side as PBE-only |
| E3 | Perovskite duplicated center (length-sweep copy) | alias-mapped, one survivor |
| E4 | Supercell `shear_xy_g0.010`: no charge density, no potential | ρ/V tasks only — ELF, all-electron densities, eigenvalues usable; a 305 MB wavefunction survives, so ρ/V are regenerable later if wanted |
| E5 | Supercell `shear_xy_g0.015`: eigenvalue file absent (wavefunction too) | eigenvalue/DOS labels only; fields fine |
| E6 | Relaxation Pool dead runs (73) | all label tasks |
| E7 | Perovskite exact metals (4) | gap-derived labels only; fields and DOS fully usable |
| E8 | Perovskite fractional-occupancy flags — **majority on the angle sweep (106/125)** + 22/125 length | gap labels reported with/without; fields usable |
| E9 | Defect step-cap relaxations (12) | keep for field tasks, flagged (the SCF is converged for the as-is geometry); exclude from any label presuming a relaxed ground state |
| E10 | The stray hydrogen-in-a-box test run at the diamond root | all tasks |

Trap, recorded: the manifest's ionic-convergence flag alone wrongly condemns 72 Defect Set
statics (zero-step runs count as unconverged); the real list is E9's twelve, from the convergence
census.

### 9.4 Metrics
| quantity | primary | secondary | conventions |
|---|---|---|---|
| densities (ρ, m, all-electron) | relative L2 per run | low/high-frequency split; Bader-basin per-atom charges (Henkelman grid method; all-electron variant via the core+valence reference fields) | per-campaign median + IQR; unit-level bootstrap CIs |
| ELF | MAE | 3-D structural-similarity (7³ window); rel-L2 in the appendix | **deliberate, flagged deviation from the literature's rel-L2 default**: the denominator varies with each cell's low-ELF interstitial volume, making identical local accuracy score differently across campaigns |
| potential | mean-removed relative L2 | MAE after mean removal; the mean discrepancy as its own scalar | no absolute zero exists in a periodic cell; absolute-alignment tasks are out of scope by construction |
| DOS | smeared L1 (normalized) | 1-Wasserstein on unit-mass curves | §7's rebuild recipe; σ stated on every number |
| gap read-outs | MAE | fraction within ±0.1 eV | occupancy walk, never a DOS threshold |
Everything is reported per campaign *and* per functional, with the test-unit count beside every
aggregate.

### 9.5 Transfer and invariance axes (shared protocols, each with its null)
- **(a) Resolution.** Train on Fourier-truncated 40³ inputs (spectral truncation, never strided
  subsampling — subsampling aliases), evaluate at 80³. Null: trigonometric upsampling of the
  coarse truth = the irreducible truncation floor; report skill = 1 − err/err_trunc. The ELF
  half-grid gives every Paired-Fields run a built-in cross-resolution pair.
- **(b) Supercell.** Strain-Atlas-trained → Supercell twins at matched shear (119 usable ρ/V
  pairs, 120 ELF). Null: the **block gap** — the distance between the two campaigns' own truths
  after exact Fourier retiling — which prices in the basis-set, spin-treatment, and 0.33%
  lattice-offset systematics. Models are judged against it; the axis is never reported as pure
  size-generalization, and if held-out error ≤ the null, the experiment cannot resolve model
  quality and says so.
- **(c) Alloy transfer.** Zero-shot (query-anywhere members) or few-shot onto the held-out Alloy
  Ensemble; raw cross-chemistry errors are incomparable, so the score is skill vs the SAD floor.
- **(d) Symmetry sanity.** All 48 diamond-group operations act exactly on the even 80³ grids
  (quarter-shifts = exact 20-voxel rolls): report the median equivariance error
  ‖f(g·x) − g·f(x)‖/‖f‖ over operations × ~20 runs. Near-zero for built-in-equivariant members; a
  real diagnostic for the Fourier lineage. A symmetrized-inference ablation (group-averaged
  predictions) rides the same harness, reported as its own line — never silently enabled.
- **(e) The k-quality gate** for any Relaxation-Pool spectral task: tiers ≥ 27 / ≥ 50 / ≥ 64
  irreducible points → 720 / 246 / 156 survivors; below the gate, metric differences measure
  k-sampling, not the operator.
- **(f) Response operators.** Differentiate trained parametric members with respect to their
  branch inputs — ∂ρ̂/∂ε along sweep arms — and validate against finite differences of
  neighboring fields. Tests whether the learned map is smooth *as an operator*, beyond pointwise
  fit; costs no new data and no training — the AD stack computes it natively.
- **(g) Composition.** Chain structure→field into field→field members (III.1's predicted density
  feeding I.1's ELF head): measure error compounding against the direct map. A pipeline-level
  operator test; zero new training.

### 9.6 Floors (run wherever they type-match; §12 for constructions)
Identity (Δ-tasks; trig-upsampling for resolution) · global affine + **per-shell isotropic linear
filter** (≈ a one-layer linear Fourier operator — beating it certifies nonlinearity/anisotropy is
earning its keep) · POD + k-nearest-neighbor interpolation (the memorization null; brutal on
factorial sweeps) · **SAD** (superposed atomic densities — *already on disk as AECCAR1 for all 547
runs*; built from POTCAR radials for the other blocks, artifacts never leaving `/Pool`) ·
**spectral Poisson** (exact Hartree via 4πρ(G)/|G|², e² = 14.39964 eV·Å, G=0 → 0, + per-campaign
climatology for the exchange-correlation/local-ion remainder — doubles as pipeline calibration:
if this floor misbehaves, the extraction conventions are broken; with the semilocal-XC ridge
extension this is *the* canonical ρ→V floor every entry cites) · semilocal pointwise ELF
(ρ, |∇ρ|, ∇²ρ ridge/MLP) · linear scissor (spectra).

### 9.7 Provenance and egress
Every derived tensor carries a sidecar: run path, census-row hash, extractor version, units,
flags. Split manifests are versioned ID lists committed to the repository (paths are metadata —
fine off-Pool). **Egress rule: nothing volumetric and nothing POTCAR-derived leaves `/Pool`;**
off-Pool artifacts are metric tables and plots. A stale-tensor check runs before any metric is
reported.

---

## 10. Shared infrastructure and build order

### The primitive union (ranked by how many members depend on it)
1. **AD core, GEMM/MLP/Adam, parsers, tensor store, split engine** — everyone. The parsers are
   spin-block-aware and augmentation-skipping; the split engine consumes the duplicate registry,
   **the orbit map**, and the twin/satellite co-split rules.
2. **Batched 3-D real FFT with AD through complex tensors** — the entire Fourier lineage (I.1,
   I.3, II.4, IV.1, V.1) plus the spectral-Poisson floor and the resolution axis. *The* shared
   kernel. Substrate decision open (§0): both cost figures carried — vendor-wrapped (an adjoint
   wrapper, days) vs own Stockham FFT (the suite's largest single kernel, multi-week).
3. **Layer-granular gradient checkpointing inside the AD tape** — mandatory for attention at 80³
   (I.4), used opportunistically by I.1/I.2.
4. **Complex per-mode mixing (full + separable) and spectral truncate/pad** — Fourier lineage.
5. **Linear (softmax-free) attention + tiny channel attention + function-space layer norm** —
   I.4, V.1.
6. **Fused activation-resampling kernel with custom VJP** — I.2's identity.
7. **Fixed-point machinery** — Anderson solver (CPU least squares), weight-tied tape
   accumulation, phantom/Jacobian-free/implicit-function backward passes, spectral clipping — I.3.
8. **Periodic radius graphs (skew-safe image enumeration) + batched scatter-add with AD** — III.1;
   scatter throughput is that entry's schedule risk.
9. **fp64 Gram POD / randomized SVD** — II.1's family and half the floors; seconds of BLAS.
10. **Conformal calibration (~50 lines), FiLM conditioning, floor constructions** (§9.6).

### Build waves (all LOCAL-NOW; dependencies honored)
- **Wave 0 — the ground.** Tensor store + parsers + split/orbit/exclusion engine + the full floor
  suite. The floors alone produce this document's Stage-0 numbers and calibrate every pipeline
  (spectral-Poisson doubles as the units test). No GPU FFT decision needed.
- **Wave 1 — the projection family + the best science.** II.1–II.3 (no FFT, no convolution, no
  attention — cheapest builds, validates everything end-to-end), the Stage-0 POD gate, **IV.1 via
  the POD backbone** (the Δ flagship runs on 40³ fields resident in VRAM), IV.2, IV.3, VI.1.
- **Wave 2 — the Fourier lineage.** FFT substrate decided here. I.1 → II.4 → I.3 (the ladder) →
  IV.1's spectral backbone variant. Perovskite-64³ and Strain-Atlas-40³ first, then 80³.
- **Wave 3 — the heavy grid members.** I.2 (the fused kernel) ∥ I.4 (checkpointing) ∥ V.1
  (reuses Wave-2 spectral kernels + Wave-3 attention).
- **Wave 4 — structure→field.** III.1 invariant → PaiNN stretch. Independent of the FFT decision;
  can run parallel to Wave 2 if hands allow.
- **Supercomputer wave.** III.2, Transolver(++), the full-width FNO ablation, CoDA-NO large +
  alloy full-resolution fine-tunes, A-grid attention at full width — specs above, unchanged.

---

## 11. Honesty appendix — corrections this drill produced

1. **The alloy k-mesh story, corrected twice.** The earlier operator-list audit claimed all 9
   pipeline pairs mismatch k-meshes (explicit stage-2 KPOINTS vs stage-3 KSPACING). A feasibility
   drill then "refuted" this from a single pair — an overgeneralization. Ground truth, all nine
   checked (2026-08-19): **7 of 9 stage-3 runs carry an explicit KPOINTS (Γ 8×4×2) with 36-point
   k-lists identical to stage-2; the endpoints x=0 and x=100 have no stage-3 KPOINTS, so
   KSPACING=0.35 governs — 30 vs 36 irreducible points** (OUTCAR echoes confirm). Seven clean
   pairs; a registered confound on the two endpoints. Both prior claims were each half-wrong.
2. **Strain Atlas point count: 1,340** (1,339 strained + the reference pair), triple-confirmed;
   the census's own reconciliation already implied it.
3. **Census omission:** `shear_xy_g0.015` is missing its eigenvalue file too, not only its
   wavefunction (ANSWERS.md D2-6 says "complete... WAVECAR deleted"); and `shear_xy_g0.010`'s
   density/potential are absent outright, while its 305 MB wavefunction survives (E4).
4. **Perovskite fractional-occupancy flags are majority behavior** on the angle sweep (106/125),
   not an edge case.
5. **The ρ↔ELF pair count is 547, not 548:** one drill assumed the gap run's charge density
   existed because its ELF did; three independent verifications (sibling-file tests ×2, coverage
   matrix) show it lacks both charge density and potential.
6. **The spin-block law (§1) is nowhere in the census:** ELF and potential files also double
   under spin polarization — channel design suite-wide had to change.
7. **AECCAR1 is the SAD floor**, already on disk for all 547 full-field runs — the
   superposition-of-atomic-densities baseline requires no construction there.
8. **Post-delivery adversarial audit (2026-08-19).** Every measured claim in this document was
   re-derived independently of the drills that produced it: ~40 replicated exactly (scissor
   statistics, identity floor, magnetization sum, tensor-store arithmetic to the voxel, the
   spin-block law with a spin-restricted control, all pairing byte-checks) — and the orbit
   degeneracy measured *stronger* than claimed (exactly 0.00 meV on axis triples and shear
   orbits). One claim was found false and corrected (item 1: the k-mesh "refutation" had
   generalized a single-pair check to all nine). The audit also added the flagship prior-art
   note (§2), the GPWNO candidate (§4/III.3), the conservation constraints (I.1, III.1, IV.1),
   the Bader secondary metric (§9.4), transfer axes (f)–(g) (§9.5), the functional conformal
   extension (IV.3), and the VI.2 stretch candidate.

## 12. Verification appendix — commands behind the counts

All read-only; run 2026-08-19 by the drills (each verified its own block in its own context;
conflicts adjudicated by majority-of-independent-checks + census cross-reference).

```
# The 547 (three independent forms, all agree; +547 LOCPOT / 548 ELFCAR totals)
find /Pool/VASP_DATA -name ELFCAR -size +0 | wc -l                                    # 548
find /Pool/VASP_DATA -name ELFCAR -size +0 -execdir test -s CHGCAR \; -print | wc -l  # 547
#   per-tree: alloy 182 · diamond/Pure 169 · defect trees 196
#   the odd one out: diamond/Pure/New_files/angular-distortion/shear_xy_g0.010

# The half-grid law (headers; verified on ≥7 files across all shapes incl. 48x96x{192,200,216})
awk 'blank&&NF==3{print;exit}{blank=(NF==0)}' <run>/CHGCAR   # e.g. 80 80 80
awk 'blank&&NF==3{print;exit}{blank=(NF==0)}' <run>/ELFCAR   # e.g. 40 40 40

# The spin-block law (count of dimension lines = grid blocks per file)
grep -cE '^ *80 +80 +80 *$' <D3 run>/CHGCAR   # 2 (density, magnetization)
grep -cE '^ *40 +40 +40 *$' <D3 run>/ELFCAR   # 2 (ELF up, ELF down)
grep -cE '^ *80 +80 +80 *$' <D3 run>/LOCPOT   # 2 (V up, V down)
#   magnetization calibration: sum(block)/N = 2.000000 muB vs OUTCAR 1.9999995

# CHGCAR normalization: mean(grid)/1 = NELECT (rho stored x V_cell)
#   verified 8.0000 on 2-atom diamond runs (two independent parsers)

# Strain Atlas pairing and orbit structure
ls <point_dir>                                  # {1-GGA-PBE, 2-HSE06} at every point
cmp <pt>/1-GGA-PBE/CONTCAR <pt>/2-HSE06/POSCAR  # byte-identical (3 sweeps spot-checked)
# aliases: duplicates.csv -> 24 groups x3 copies; 1179 -> 1131; one pair cmp-verified
# orbits: sweep CSVs -> axis triples exact to 4 digits; shear 6-orbits <=0.1 meV;
#         512 triaxial -> 120 multisets at 0.00 meV => ~299 label units

# Defect Set pairs
#   chained: cmp <PBE>/CONTCAR <HSE>/POSCAR byte-identical (3 campaigns spot-checked) -> 59-3=56
#   new-only: 38<->38 by element; Zr drift exactly 0.0000 A (byte-copy) -> 37; drift from CONTCARs
#   functional census from d3_defect_table.csv (WARNING: quoted commas break naive -F, parsing)

# Alloy pipeline k-mesh (ALL NINE pairs; twice-corrected claim, see §11.1)
for x in 1-x-0 .. 9-x-100: sed -n 2p {stage2,stage3}/$x/IBZKPT; test -f stage3/$x/KPOINTS
#   7/9: explicit KPOINTS (G 8x4x2) both sides, 36 = 36, lists identical
#   x=0 & x=100: NO stage-3 KPOINTS -> KSPACING=0.35 governs -> 30 vs 36 irreducible (OUTCAR echo)

# Perovskite Grid
find ggapbe/angle_distortions -name CHGCAR | wc -l   # 125, headers uniform 64 64 64
# manifest.csv folder->lattice mapping verified against POSCAR to all printed digits

# Relaxation Pool shape
# j_chemistry.csv: 30,487 steps; <=5:236 | 6-10:345 | 11-20:413 | 21-50:392 | 51-100:99 | >100:15
# runs.jsonl ibz_nk quartiles: 4 / 18 / 27 / 40 / 397 (n=1,482)
# one vasprun.xml: 25 <calculation> = 25 forces varrays = 25 stress varrays = CSV nsteps

# Tensor-store size arithmetic: voxel sums from runs.jsonl grid fields
#   core ~1.94e9 voxels x 4 B + curves/labels ~= 7.9 GB; + SAD cache 1.5 GB ~= 9.7 GB vs 124 GB free
```

**Standing references:** census `/Pool/VASP_DATA/_census/ANSWERS.md` + sidecars (`runs.jsonl`,
`duplicates.csv`, `d3_defect_table.csv`, `convergence_census.csv`, `spin_census.csv`,
`file_coverage_matrix.csv`, `eps_twin_grids.csv`, `j_chemistry.csv`, `j_gaps.csv`, per-sweep
`manifest.csv`). Feasibility drill synthesis: `/home/javier/.claude/plans/take-a-look-at-snoopy-candle.md`.

# Stream S5: PINO Methodology — Residual Loss Design for Multi-Source Training

This is a literature-grounded methodology survey for the `n-Op` PINO. The focus is residual loss machinery suited to the four-source supervisory regime (cheap-compute, VASP, experiment, physics residuals) targeting UWBG-semiconductor screening.

---

## Part A — Literature Survey of Physics-Informed Methods

### A.1 PINNs (Raissi, Perdikaris, Karniadakis 2019)

The canonical PINN loss is a sum of three residual classes:

```
L_PINN = L_data + L_PDE + L_BC/IC
       = (1/N_d) Σ ||u_θ(x_i) − u_i||²
       + (1/N_r) Σ ||N[u_θ](x_j)||²    where N is the PDE operator
       + (1/N_b) Σ ||B[u_θ](x_k) − g(x_k)||²
```

`L_PDE` is a *physics residual* evaluated at "collocation points" sampled in the domain interior; it requires autodiff through the network for spatial/temporal derivatives. Works for low-dim, smooth PDEs. Documented failure modes (Wang et al. 2021, 2022; Krishnapriyan et al. 2021): gradient pathology where `L_PDE ≫ L_data`, spectral bias toward low frequencies, and "convergence to trivial solutions" in stiff/multi-scale regimes.

**Takeaway for us**: PINN structure is the template, but a single-PDE collocation loss is not what we have. We have *many* observable-level residuals at different cost tiers.

### A.2 Fourier Neural Operators (Li et al. 2020, 2021)

FNOs learn a mapping `G_θ: a(x) → u(x)` between function spaces by stacking integral-kernel layers parametrized in Fourier space. The base loss is purely data:

```
L_FNO = Σ_k ||G_θ(a_k) − u_k||_{L²}
```

**PI-FNO** variants (Li et al. 2021 "Physics-Informed Neural Operator") add a residual term `||N[G_θ(a)]||²` at sampled grid points and have been shown to improve out-of-distribution generalization, *particularly when training data is scarce*. The residual is computed in real space via differentiable spectral derivatives.

### A.3 DeepONet (Lu, Jin, Pang, Zhang, Karniadakis 2021)

Branch-trunk architecture: branch network encodes input function `u`, trunk network encodes evaluation location `y`, output is inner product. **PI-DeepONet** (Wang, Wang, Perdikaris 2021) adds a PDE-residual term computed via autodiff through the trunk. Demonstrated for parametric PDEs; struggles when input function is high-dimensional in a non-low-rank way.

### A.4 Materials-Specific Neural Operators / MLIPs

These are *machine-learned interatomic potentials* (MLIPs) rather than operator learners in the Li/Lu sense, but they are the closest neighbors of what `n-Op` is doing for materials:

| Model | Loss structure | Physics residuals? | Source |
|---|---|---|---|
| **SchNet** (Schütt 2017) | E + F (energy + forces) | Forces are `−∂E/∂R` enforced by autodiff — *exact gradient consistency*, not a soft residual | Schütt et al. 2017 |
| **NequIP** (Batzner 2022) | E + F + (sometimes) stress | Same E/F autodiff link; equivariance is *architectural* not loss-imposed | Batzner et al. Nat. Commun. 2022 |
| **MACE** (Batatia 2022) | E + F + stress | Same | Batatia et al. NeurIPS 2022 |
| **CHGNet** (Deng 2023) | E + F + stress + magnetic moments | Multi-target supervised, no explicit physics residual | Deng et al. Nat. Mach. Intell. 2023 |
| **M3GNet** (Chen 2022) | E + F + stress | Multi-target supervised | Chen & Ong Nat. Comput. Sci. 2022 |
| **Allegro** (Musaelian 2023) | E + F + stress | Same | Musaelian et al. Nat. Commun. 2023 |
| **GNoME** (Merchant 2023) | E + F (active learning loop) | DFT-in-the-loop replaces explicit residuals | Merchant et al. Nature 2023 |

**Critical observation**: the MLIP family enforces physics *architecturally* (equivariance, energy-conserving force = `−∇E`) rather than via soft loss residuals. The soft residual `||F + ∇E||²` is not used because the autodiff link makes it identically zero.

This is a *strong design lesson*: **if you can bake a physical constraint into the architecture, do not put it in the loss.** Soft residuals should be reserved for relations that cannot be made architectural (constitutive PDEs, transport equations, sum rules on derived observables).

### A.5 Generative Models for Crystals

| Model | How physics is enforced |
|---|---|
| **CDVAE** (Xie 2022) | VAE on crystal graph; physics is *encoded* (lattice + fractional coords) not residualized; periodicity is architectural |
| **DiffCSP** (Jiao 2023) | Diffusion in joint lattice + fractional-coord space; SE(3) equivariance architectural |
| **FlowMM** (Miller 2024) | Riemannian flow matching on (L, F, A) manifold; constraints architectural |
| **MatterGen** (Zeni 2025) | Diffusion + property guidance; property targeting via classifier-free guidance, not residual loss |

These projects **avoid residual loss entirely** and constrain via geometry/architecture. They cannot be the template for `n-Op` because we want to *use* /physics's residuals, not avoid them.

### A.6 Multi-Fidelity Neural Operators

| Method | Idea | Source |
|---|---|---|
| **Multi-fidelity DeepONet** | Branch network sees low-fi solution, learns high-fi correction | Lu et al. JCP 2022 |
| **MF-PINN** | Cascade of PINNs: low-fi PINN's output is input to high-fi PINN | Meng & Karniadakis JCP 2020 |
| **CoPhy-PGNN** | Composite loss with low-fi sim + high-fi sim + physics constraint | Elhamod et al. 2022 |
| **PI-MF-DeepONet** | Each fidelity has its own data loss; shared physics residual | Howard et al. 2022 |

The pattern: **share physics residual across fidelities; specialize data loss per fidelity**. This directly informs our four-source setup.

---

## Part B — Loss Balancing Methods

The expanded loss `L = Σ_k λ_k L_k` requires choosing weights. Survey:

| Method | Mechanism | When it works | Cost | Source |
|---|---|---|---|---|
| **Fixed weights** | Hand-tuned λ_k | Few terms, similar scales | 0 | — |
| **Uncertainty weighting** | `λ_k = 1/(2σ_k²)`, σ_k learned | Multi-task supervised, when scales differ in magnitude | Negligible | Kendall, Gal, Cipolla CVPR 2018 |
| **GradNorm** | Adjust λ_k so per-task gradient norms `||∇_W L_k||` equalize | Multi-task; reduces task interference | O(K) gradient norms/step | Chen et al. ICML 2018 |
| **NTK-balancing** | λ_k from spectrum of `K_k = J_k J_k^T` (NTK block per loss) | PINN; addresses spectral bias | O(N²) per epoch (subsample) | Wang, Yu, Perdikaris JCP 2022 |
| **Self-Adaptive PINN** | Per-collocation-point trainable weights, ascended | PINN regions of high residual | O(N) extra params | McClenny & Braga-Neto JCP 2023 |
| **Learning Rate Annealing** | Heuristic from gradient magnitudes per loss | PINN startup | Low | Wang et al. SIAM JSC 2021 |
| **Lagrangian / dual-ascent** | Treat residual as constraint, multipliers ascended | Hard constraints required | Medium; can be unstable | Lu et al. 2021; Basir & Senocak 2022 |
| **ReLoBRaLo** | Relative-loss-balanced with random lookback | Robust PINN training | Low | Bischof & Kraus 2021 |

**Empirical consensus** (from PINN benchmarks Wang 2022, Hao et al. 2023 survey):
- Fixed weights fail when loss-term scales differ by >2 orders of magnitude.
- GradNorm and NTK-balancing are roughly equivalent; NTK is more principled for PINNs, GradNorm more practical for multi-task supervised.
- Self-Adaptive PINN (point-wise weights) is the *single most reliable* technique for residual-dominant losses but requires per-point weight parameters.
- Lagrangian methods give *strict* constraint satisfaction but training instability is real.

**Recommendation for `n-Op`**: Hybrid — **GradNorm across the four source families** (cheap, VASP, exp, residuals) for outer balancing, **fixed (with NTK initialization)** within the residual family for individual λ_i. This avoids exploding the parameter count and keeps the four-source balance principled.

---

## Part C — Differentiability Discipline

For a residual to participate in gradient training, `∂L_res/∂θ` must exist *and be computable affordably*.

### Tag system (proposed)

| Tag | Meaning | Example | Gradient cost |
|---|---|---|---|
| **D0 — Closed-form** | Analytical formula; autodiff trivial | Effective-mass equation; Varshni gap-vs-T | O(forward) |
| **D1 — Autodiff-native** | Pure tensor pipeline of diff. primitives | k·p band slope; Drude conductivity | O(forward) |
| **D2 — Adjoint-required** | Iterative solver inside; needs adjoint equation | SCF, BTE, Poisson-drift-diffusion | O(forward) per adjoint, but adjoint solve ≈ forward solve |
| **D3 — Finite-difference fallback** | Black-box residual, no adjoint available | Legacy VASP-wrapper observable | O(P × forward) where P = #params perturbed |
| **D4 — Non-differentiable** | Discrete decisions, classifications | "is direct-gap?", phase label | Requires relaxation |

**Handling D4**:
- *Gumbel-Softmax / concrete distribution* (Jang, Maddison 2017) for categorical outputs
- *Straight-through estimator* (Bengio 2013) when gradient through the discrete op is needed
- *Surrogate continuous residual*: replace "is direct-gap" with `gap_indirect − gap_direct` (signed continuous quantity); the discrete fact becomes the sign of a differentiable scalar

**Handling D2 (adjoint)**: The *discrete adjoint method* (Giles & Pierce 2000; Plessix 2006) gives `∂L/∂θ` at the cost of one adjoint solve per loss-gradient regardless of #parameters. For SCF: Pulay-style adjoint (DFPT framework, Baroni et al. 2001) is the gold standard. For BTE: variational principles or RTA approximation make adjoint tractable.

**Architectural recommendation**: Every formula entry in `/physics`'s registry carries a `differentiability_tag :: D0 | D1 | D2 | D3 | D4` field, plus, for D2, a `:adjoint-implementation` slot. The PINO training loop respects the tag when choosing whether to evaluate the residual analytically, via autodiff, via stored adjoint, or by relaxation.

---

## Part D — Cost-Tiered Residual Sampling

Many residuals at many costs; can't evaluate all every step.

### Cost-tier classification

| Tier | Cost per eval | Cadence | Examples |
|---|---|---|---|
| **T0 — per-step** | O(1)–O(N_batch) | Every gradient step | Algebraic identities; sum rules; Varshni; Drude in EMA |
| **T1 — per-batch** | O(grid) | Every minibatch | k·p slopes; DOS integrals at fixed grid |
| **T2 — per-epoch** | O(SCF) | Sampled each epoch (importance-weighted) | SCF convergence residual; phonon DOS |
| **T3 — on-demand** | O(BTE/full DFT) | Triggered (loss plateau / validation drift) | Full BTE transport; full DFT bandstructure |

### Sampling strategies (validated in PINN/operator literature)

| Strategy | Source | Use |
|---|---|---|
| **Uniform random** | baseline | T0 residuals where landscape is uniform |
| **Residual-Adaptive Refinement (RAR)** | Lu et al. SIAM Rev 2021 | Add collocation points where residual is large |
| **RAD (Residual-based Adaptive Distribution)** | Wu, Lu, Xu, Karniadakis CMAME 2023 | Importance sample from `p(x) ∝ |res(x)|^k / Σ + c` |
| **Causal sampling** | Wang, Sankaran, Perdikaris 2022 | Time-causal weighting for IVPs |
| **Curriculum** | Krishnapriyan 2021 | Easy-to-hard residuals; start with smooth/cheap residuals |

**Recommendation for `n-Op`**: 
- T0 always-on.
- T1 always-on but only on subsampled k-points/grid points via **RAD** (importance sampling on residual magnitude).
- T2 **curriculum-scheduled**: first 30% of training without T2; introduce gradually.
- T3 only as **validation triggers**, never in the training gradient (used for early stopping / curriculum advancement).

---

## Part E — Multi-Source Training Regime (CRITICAL)

The four sources and their characteristic properties:

| Source | Trust | Coverage | Cost | Noise | What it constrains |
|---|---|---|---|---|---|
| (a) Cheap-compute | Low | Broad (all observables) | ~ms | Systematic bias | Smooth functional form |
| (b) VASP DFT | High (for what it computes) | Selective (energies, bands, forces; *not* transport) | ~CPU-hours | Functional/k-mesh systematic | Ground-truth electronic structure |
| (c) Experiment | Highest (where measured) | Sparse, observable-restricted | $$ | Measurement noise + sample variation | Real-world calibration |
| (d) Physics residuals | Trust ≡ trust in `/physics` itself | Tunable | T0–T3 spectrum | None (or known) | Physical consistency |

### Proposed loss structure

```
L_total = w_cheap(t) · Σ_o∈O_cheap  M_o · L²(ŷ_o, y_o^cheap)
        + w_vasp(t)  · Σ_o∈O_vasp   M_o · L²(ŷ_o, y_o^vasp)
        + w_exp(t)   · Σ_o∈O_exp    M_o · ρ_huber(ŷ_o, y_o^exp; σ_o^exp)
        + Σ_i λ_i(t) · L_res_i(ŷ; state)

where  M_o = coverage mask (1 if observable o is present for this sample, else 0)
       σ_o^exp = experimental uncertainty (Huber loss respects it)
       w_*(t) = curriculum schedules
       λ_i(t) = adaptive per-residual weights
```

### Coverage matrix discipline

Every training sample carries a **coverage vector** `m ∈ {0,1}^|O|` indicating which observables are present from which source. Loss is masked per term. This is standard in multi-task ML with missing labels (Caruana 1997; modern: PCGrad, Yu 2020).

### Curriculum (validated in MF-PINN literature)

| Phase | Active weights | Rationale |
|---|---|---|
| **Warm-up (0–10%)** | w_cheap high, λ_residual moderate, w_vasp/exp low | Network learns smooth approximate functional form from cheap data |
| **Refine (10–60%)** | w_cheap decay, w_vasp ramp, λ_residual high | High-fidelity correction; physics enforced |
| **Calibrate (60–90%)** | w_exp ramp, w_vasp held, λ_residual held | Experimental anchoring |
| **Polish (90–100%)** | All sources balanced via GradNorm | Final equilibrium |

This mirrors **MF-PINN cascading** (Meng & Karniadakis 2020) and **CoPhy-PGNN composite-loss curriculum** (Elhamod 2022). Both report that early physics-residual weight prevents overfitting to low-fidelity data; late experimental weight prevents drift from real-world calibration.

### Residual-vs-label tension

Documented (Daw et al. 2022 "Physics-Guided Neural Networks"): when labels conflict with physics residuals (e.g., experimental noise violates a sum rule), naively summing forces the network into a Pareto trade-off. Fixes:

1. **Noise-aware label loss**: Huber loss with σ from instrument uncertainty makes residuals "win" inside the experimental noise band.
2. **Constrained optimization framing**: residuals as constraints, labels as objective; KKT framework. Expensive but principled.
3. **Hierarchy via weights**: experimental noise band absorbed by `1/σ²` weighting in uncertainty-based balancing.

**Recommendation**: option (1) — Huber with per-observable σ from experimental metadata — is empirically the most reliable and cheapest.

---

## Part F — Convergence Properties

### Documented failure modes

| Mode | Symptom | Fix | Source |
|---|---|---|---|
| **Gradient pathology** | One loss term's gradient dominates | NTK / GradNorm / annealing | Wang et al. 2021 |
| **Spectral bias** | Low-freq learned, high-freq missed | Fourier features; SIREN; multi-scale loss | Tancik 2020; Sitzmann 2020 |
| **Residual stuckness** | Plateau far from solution | Curriculum; warm-start from cheap data | Krishnapriyan 2021 |
| **Stiff PDEs** | Training diverges | Causal weighting; domain decomposition (XPINN, cPINN) | Jagtap 2020; Wang 2022 |
| **Mode collapse on labels** | Network ignores residuals | Increase λ_residual via GradNorm | Wang 2022 |
| **Conflicting gradients** | Tasks pull network in opposite directions | PCGrad (project conflicting gradients) | Yu et al. NeurIPS 2020 |

### Theoretical results (limited but real)

- **Convergence of PINN training** to PDE solution proven only under restrictive conditions (Shin, Darbon, Karniadakis 2020): linear elliptic PDEs, sufficient collocation density, NTK regime.
- **No general guarantee** for nonlinear / non-elliptic / multi-fidelity regimes.
- **Neural operator universal approximation** (Kovachki et al. JMLR 2023) gives expressivity but not trainability.

The honest summary: PINO convergence is **empirical**. Discipline (gradient balancing, curriculum, coverage masking) is what makes it work in practice.

---

## Part G — Residual Generation as a First-Class Concept

The architectural gap: `/physics` has residual *categories* but no generator producing a residual from an arbitrary composition.

### Proposed typed interface (CS vocabulary)

```
;; Every observable in /physics is a composition:
(deftype observable
  (record (name symbol)
          (composition compose-expression)
          (output-type tensor-spec)
          (differentiability-tag (member :d0 :d1 :d2 :d3 :d4))
          (cost-tier (member :t0 :t1 :t2 :t3))
          (cheap-path compose-expression)
          (faithful-path compose-expression)))

;; A residual generator takes an observable + tolerance and returns
;; a callable that consumes (state, prediction) and returns scalar:
(deftype residual-generator
  (record (target observable)
          (path (member :cheap :faithful))
          (distance (member :l2 :l1 :huber :rel-l2))
          (weight-policy (member :fixed :gradnorm :ntk :self-adaptive))
          (eval-fn (-> state prediction scalar))))

;; The generator factory:
(defun make-residual-generator (observable
                                &key (path :faithful)
                                     (distance :l2)
                                     (weight-policy :gradnorm))
  ;; ... produces a residual-generator whose eval-fn is:
  ;; (lambda (state prediction)
  ;;   (let* ((target-value (evaluate-composition
  ;;                          (slot observable path) state))
  ;;          (delta (distance prediction target-value)))
  ;;     delta)))
  )
```

### Three properties this gives us

1. **Uniform consumption**: PINO sees a homogeneous collection of `residual-generator` records regardless of underlying physics.
2. **Cost-tier honoring**: PINO scheduler dispatches by `cost-tier`.
3. **Path selection**: cheap-vs-faithful choice is per-residual, per-training-phase.

### Sampling interface

```
(deftype residual-sample-policy
  (record (cadence (member :every-step :every-batch :every-epoch :on-demand))
          (sampler (-> domain (list collocation-point)))
          (importance-fn (or null (-> collocation-point scalar)))))
```

The PINO training step:

```
(defun pino-training-step (model batch generators sample-policies)
  (let* ((data-loss   (compute-data-loss model batch))
         (residual-losses
           (map (lambda (g p)
                  (when (active-this-step? p step)
                    (let ((points (sample p (domain-of g))))
                      (evaluate-residual g model points))))
                generators sample-policies))
         (lambdas (compute-adaptive-weights ...))
         (total (combine data-loss residual-losses lambdas)))
    (backprop total)))
```

This is the *missing machinery*. It is the architectural piece that turns `/physics` from a compendium of residual categories into a **residual factory** for the PINO.

---

## Part H — Recommendations for `/physics` Architecture

### H.1 Registry-level changes

Every formula entry adds:
- `:differentiability-tag` ∈ `{D0, D1, D2, D3, D4}`
- `:cost-tier` ∈ `{T0, T1, T2, T3}`
- `:adjoint-implementation` (optional; populated for D2)
- `:cheap-path` and `:faithful-path` compositions (already a project commitment)
- `:relaxation` (optional; populated for D4, e.g., Gumbel temperature, surrogate continuous form)

### H.2 Three exports of /physics (the user's framing)

| Export | Consumer | What /physics returns |
|---|---|---|
| **Generate** | Cheap-compute data pipeline | Forward evaluation along `:cheap-path` |
| **Validate** | Test harness | Forward evaluation along `:faithful-path` for comparison |
| **Import** | PINO training | `residual-generator` records ready to be summed into the loss |

The Import interface is the **new** thing this stream recommends; Generate and Validate already exist conceptually.

### H.3 Loss balancing policy (default)

- **Outer (cross-source) balancing**: GradNorm across {cheap, vasp, exp, residual-family-aggregate}. K=4 tasks, cheap to compute.
- **Inner (per-residual)**: NTK-initialized fixed weights, multiplied by curriculum schedule. Optional Self-Adaptive point-wise weights for T0 residuals where landscape is non-uniform.
- **Experimental term**: Huber loss with σ-from-metadata; this absorbs noise into the loss naturally.

### H.4 Sampling policy (default)

- T0 always-on, full evaluation.
- T1 always-on, **RAD-importance-sampled** k-points / grid points.
- T2 curriculum-gated (off for first 30% of training); when active, evaluated on a fraction of the batch chosen by largest-residual-first.
- T3 never in training gradient; runs as a periodic validation hook that can trigger curriculum advancement or early stopping.

### H.5 Curriculum (default)

Phase schedule from Part E, with knobs for `(warmup-end, refine-end, calibrate-end)` as percentages of total training steps. Defaults `(0.10, 0.60, 0.90)` per MF-PINN literature.

### H.6 Coverage matrix

Each training sample is a record:
```
(deftype training-sample
  (record (state state-record)
          (sources (alist source-tag observation-vector))
          (coverage-mask (alist source-tag bitmask))
          (uncertainty (alist source-tag sigma-vector))))
```
Loss terms read `coverage-mask` to mask absent labels. This is mandatory for the four-source regime; without it the four losses cannot share a network.

### H.7 What we explicitly recommend AGAINST

- **Hard constraints via Lagrangian dual-ascent** for the four-source regime — too unstable when sources disagree.
- **Soft residuals for relations enforceable architecturally** — if a residual is `||F − (−∇E)||²`, bake it into the architecture instead (see Part A.4: this is the MLIP lesson).
- **Single-λ uniform weighting** — empirically the most common cause of PINN training failure.
- **Treating residuals as "labels with zero noise"** — they are constraints, not measurements; coverage-mask logic differs.

---

## Key References

- Raissi, Perdikaris, Karniadakis (2019) — PINN, JCP 378
- Li et al. (2020) — FNO, ICLR 2021
- Li et al. (2021) — Physics-Informed Neural Operator (PINO), arXiv:2111.03794
- Lu, Jin, Pang, Zhang, Karniadakis (2021) — DeepONet, Nat. Mach. Intell. 3
- Wang, Wang, Perdikaris (2021) — Physics-Informed DeepONets, Sci. Adv. 7
- Wang, Teng, Perdikaris (2021) — Gradient pathologies in PINNs, SIAM JSC 43
- Wang, Yu, Perdikaris (2022) — NTK for PINN, JCP 449
- Krishnapriyan et al. (2021) — Characterizing PINN failure modes, NeurIPS
- Chen et al. (2018) — GradNorm, ICML
- Kendall, Gal, Cipolla (2018) — Uncertainty weighting, CVPR
- McClenny & Braga-Neto (2023) — Self-Adaptive PINNs, JCP 474
- Meng & Karniadakis (2020) — Composite multi-fidelity PINN, JCP 401
- Lu et al. (2022) — Multi-fidelity DeepONet, JCP 463
- Howard et al. (2022) — Multi-fidelity PI-DeepONet
- Elhamod et al. (2022) — CoPhy-PGNN composite-loss curriculum
- Wu, Lu, Xu, Karniadakis (2023) — RAD sampling, CMAME 403
- Yu et al. (2020) — PCGrad, NeurIPS
- Daw et al. (2022) — Physics-Guided Neural Networks survey
- Batzner et al. (2022) — NequIP, Nat. Commun. 13
- Batatia et al. (2022) — MACE, NeurIPS
- Deng et al. (2023) — CHGNet, Nat. Mach. Intell. 5
- Merchant et al. (2023) — GNoME, Nature 624
- Xie et al. (2022) — CDVAE, ICLR
- Jiao et al. (2023) — DiffCSP, NeurIPS
- Miller et al. (2024) — FlowMM, ICML
- Kovachki et al. (2023) — Neural operator theory, JMLR
- Hao et al. (2023) — PINN benchmarks survey
- Giles & Pierce (2000) — Adjoint methods
- Baroni et al. (2001) — DFPT (SCF adjoint), Rev. Mod. Phys. 73
- Jang & Gu (2017) — Gumbel-Softmax, ICLR
- Bischof & Kraus (2021) — ReLoBRaLo

---

## Summary for the Conductor

The methodology recommendation set for `n-Op`:

1. **Per-formula tags** (`differentiability ∈ D0–D4`, `cost-tier ∈ T0–T3`) — required to make residual selection mechanical.
2. **Residual generator factory** producing typed `residual-generator` records — the missing architectural piece.
3. **Three exports** of /physics: Generate, Validate, Import (Import is new).
4. **Outer GradNorm + inner NTK-initialized fixed weights** for loss balancing.
5. **Coverage-mask-aware multi-source loss** with Huber + per-observable σ for experimental terms.
6. **Four-phase curriculum**: warmup (cheap-heavy) → refine (VASP + residual) → calibrate (experiment) → polish (GradNorm equilibrium).
7. **RAD sampling for T1 residuals**; T3 only as validation triggers; T0 always-on.
8. **Architectural-over-soft** principle: if a constraint can be made architectural (equivariance, energy-conserving forces), do not residualize it.

The cleanest single takeaway: **`/physics` should expose a residual generator factory, and the PINO should consume residuals as typed records carrying differentiability tags, cost tiers, and sampling policies.** This is the architectural piece prior analysis flagged as missing, and it is exactly what the multi-source training regime demands.

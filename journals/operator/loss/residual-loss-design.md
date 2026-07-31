---
id: residual-loss-design
title: "Residual loss design"
owns:
  - physics-informed loss survey
  - architectural-before-soft principle
  - loss balancing policy
  - residual evaluation cadence
  - residual sampling policy
  - four supervisory sources
  - compared-against enum
  - label-presence mask
  - sample-applicability mask
  - source-weight curriculum
  - label-versus-residual tension
  - loss convergence honesty
anchors:
  scope: "What this page is"
  survey: "The literature"
  architectural-over-soft: "Architectural before soft"
  balancing: "Balancing the terms"
  adjoints: "Residuals that need an adjoint"
  relaxations: "Residuals with no useful derivative"
  cadence: "Cadence is a loop policy"
  sampling: "Sampling"
  four-sources: "The four supervisory sources"
  loss-structure: "The assembled loss"
  label-presence: "The label-presence mask"
  curriculum: "The source-weight curriculum"
  tension: "When a label and a residual disagree"
  convergence: "What convergence does and does not guarantee"
  defaults: "Defaults"
  anti-recommendations: "What not to do"
  references: "References"
depends-on:
  - named-formulas
  - residual-machinery
  - residual-definitions
  - pino-bridge
  - applicability-classifiers
  - accuracy-ledger
  - training-stages
  - learnable-structure-contract
open-questions:
  - id: sampling-policy-record-home
    anchor: sampling
    summary: "A sampling policy is a cadence, a sampler and an optional importance function, and nothing carries all three: the oracle's generator record has one flat four-valued field fusing a sampler, two importance schemes and an evaluation-scope value, with no cadence field at all, so the importance function has no typed home on either side of the seam."
  - id: compared-against-versus-supervisory-sources
    anchor: four-sources
    summary: "The per-generator compared-against enum has four values and this page has four supervisory sources, and they are not the same four: two enum values are compute-side and none names a physics residual. Whether the two enumerations are meant to align is unstated."
  - id: residual-weight-before-the-informed-epoch
    anchor: curriculum
    summary: "The source-weight curriculum gives physics residuals weight from the first training phase, and the stage ordering gives the oracle a single stage at the end; one is the multi-fidelity literature's schedule and the other is this project's decision, and which governs is unstated."
  - id: experimental-sigma-source
    anchor: tension
    summary: "The seam supplies two standard deviations without conflating them — one per datum on the external-ground-truth call, one the observable's declared accuracy scale, which feeds the error budget and not a loss weight — and this page has not chosen which one scales the experimental Huber term. Only the per-datum one varies per measurement."
---
# Residual loss design

## What this page is

A literature-grounded design survey for the operator's loss under the four-source
supervisory regime — cheap compute, density-functional theory, experiment, and physics
residuals — aimed at ultra-wide-bandgap semiconductor screening.

It records what the literature supports, what it warns against, and what this library
defaults to. It is design rationale for a loss, not a specification of shipped
machinery: where a recommendation has landed elsewhere, the owning page states it and
this page cites it.

## The literature

**Physics-informed networks.** The canonical loss is a sum of three residual classes: a
data term, an equation residual evaluated at collocation points sampled in the domain
interior, and a boundary-or-initial-condition term. The interior term needs autodiff
through the network for spatial and temporal derivatives. It works for low-dimensional,
smooth equations. Documented failure modes are gradient pathology when the equation
term dominates the data term, spectral bias toward low frequencies, and convergence to
trivial solutions in stiff or multiscale regimes (Wang et al. 2021, 2022;
Krishnapriyan et al. 2021).

That structure is the template. A single-equation collocation loss is not what this
project has: it has many observable-level residuals at widely different evaluation
costs.

**Neural operators.** Fourier neural operators learn a map between function spaces by
stacking integral-kernel layers parametrised in Fourier space; the base loss is purely
data. Physics-informed variants add a residual term at sampled grid points and improve
out-of-distribution generalisation, most visibly when training data is scarce. The
residual is computed in real space by differentiable spectral derivatives.

Branch-trunk operators encode the input function in a branch network and the evaluation
location in a trunk network, and take their inner product. Physics-informed variants
add an equation residual by autodiff through the trunk. They struggle when the input
function is high-dimensional in a way that is not low-rank.

**Machine-learned interatomic potentials.** These are the closest neighbours of what
this project does for materials, even though they are potentials rather than operator
learners.

| Model | Loss structure | Physics residuals |
|---|---|---|
| SchNet | energy and forces | forces are the negative energy gradient, enforced by autodiff — exact gradient consistency, not a soft residual |
| NequIP | energy, forces, sometimes stress | same autodiff link; equivariance is architectural, not loss-imposed |
| MACE | energy, forces, stress | same |
| CHGNet | energy, forces, stress, magnetic moments | multi-target supervised, no explicit physics residual |
| M3GNet | energy, forces, stress | multi-target supervised |
| Allegro | energy, forces, stress | same |
| GNoME | energy and forces, inside an active-learning loop | density-functional theory in the loop replaces explicit residuals |

**Generative crystal models.** Variational, diffusion and flow-matching models for
crystals encode physics geometrically — periodicity, fractional coordinates, rotational
equivariance are architectural — and avoid residual loss entirely. They cannot be the
template here, because the point of this project is to *use* the oracle's residuals
rather than to design around them.

**Multi-fidelity operators.** Multi-fidelity branch-trunk operators, cascaded
physics-informed networks, and composite-loss models converge on one pattern: **share
the physics residual across fidelities, specialise the data loss per fidelity.** That
pattern is what the four-source regime below is built on.

## Architectural before soft

The interatomic-potential family enforces physics **architecturally** — equivariance by
construction, and the force-as-negative-energy-gradient relation by autodiff — rather
than through soft loss residuals. The soft residual on that force relation is never
used, because the autodiff link makes it identically zero.

**If a physical constraint can be baked into the architecture, it does not belong in
the loss.** Soft residuals are for relations that cannot be made architectural:
constitutive equations, transport equations, sum rules over derived observables.

The seam offers a mechanism for exactly this: a compile-time symmetry descriptor the
operator can consume, after which equivariance residuals go to zero by construction
([learnable-structure-contract#optional-offers]).

## Balancing the terms

The expanded loss is a weighted sum of terms, and the weights have to come from
somewhere.

| Method | Mechanism | When it works | Cost |
|---|---|---|---|
| Fixed weights | hand-tuned | few terms, similar scales | none |
| Uncertainty weighting | weight is the reciprocal of twice a learned variance | multi-task supervised, when scales differ in magnitude | negligible |
| GradNorm | adjust weights so per-task gradient norms equalise | multi-task; reduces task interference | one gradient norm per task per step |
| Neural-tangent-kernel balancing | weights from the spectrum of the per-loss kernel block | physics-informed networks; addresses spectral bias | quadratic in sample count, so subsampled |
| Self-adaptive weighting | trainable per-collocation-point weights, ascended | regions of high residual | one extra parameter per point |
| Learning-rate annealing | heuristic from per-loss gradient magnitudes | startup | low |
| Lagrangian dual ascent | residual as constraint, multipliers ascended | when hard constraints are required | medium, and can be unstable |
| Relative-loss balancing with random lookback | normalised relative losses | robust training | low |

Empirical consensus across the benchmark literature:

- Fixed weights fail once term scales differ by more than two orders of magnitude.
- GradNorm and kernel balancing are roughly equivalent. Kernel balancing is more
  principled for physics-informed losses; GradNorm is more practical for multi-task
  supervised losses.
- Per-point self-adaptive weighting is the single most reliable technique for
  residual-dominant losses, at the price of a weight parameter per point.
- Lagrangian methods give strict constraint satisfaction, and their training
  instability is real.

**The policy here is hybrid**: GradNorm across the four source families for outer
balancing, and fixed weights inside the residual family, initialised from the
neural-tangent-kernel spectrum. That keeps the four-source balance principled without
exploding the parameter count.

## Residuals that need an adjoint

The discrete adjoint method gives the loss gradient at the cost of one adjoint solve
per loss gradient, independent of the number of parameters (Giles and Pierce 2000;
Plessix 2006). That is the cost claim behind the `adjoint` tier, whose name means what
[named-formulas#diff-tags] says it means.

`fixpoint-adjoint` is a **refinement of** `adjoint`, not an alternative to it. It
applies where the residual's output is a converged fixed point: the implicit-function
form then costs one linear solve independent of iteration count, and the formula runs
`adjoint`'s registration gate plus a conditioning check on the fixed-point Jacobian
([residual-machinery#registration-gate]). Named instances: Pulay-style adjoints in the
density-functional perturbation framework for a self-consistent field (Baroni et al.
2001); variational principles, or the relaxation-time approximation, for the Boltzmann
transport equation.

Neither is an escape hatch. A residual that cannot supply a derivative at all belongs
to `relaxed` or `none`, below.

What belongs on this page is the consequence for the loop: an adjoint-tier residual
costs roughly one extra forward-equivalent per gradient, which is what keeps it off the
per-step path.

## Residuals with no useful derivative

A residual whose output is integer, categorical, boolean or set-valued has no useful
derivative — the `none` tier — and cannot enter a gradient in that form. Three
techniques move such a quantity into the `relaxed` tier, which is the tier that ships a
*named* relaxation:

- **Concrete, or Gumbel-Softmax, relaxation** for categorical outputs (Jang et al.
  2017).
- **Straight-through estimator**, when a gradient has to pass through the discrete
  operation (Bengio et al. 2013).
- **Surrogate continuous residual** — replace the discrete predicate with a signed
  continuous quantity whose sign carries the discrete fact. "Is the band gap direct?"
  becomes the indirect-minus-direct gap difference.

The third is the strongest where it applies, because it removes the discreteness rather
than smoothing it: the discrete fact becomes the sign of a differentiable scalar, and
the residual stays exact.

Which tier a formula sits in is the oracle's classification
([named-formulas#diff-tags]), not the loop's. What the loop owns is whether it
evaluates such a residual at all.

## Cadence is a loop policy

Cadence is **how often** a residual is evaluated during training. It is a property of
the training loop, not of the formula. The oracle owns no loop, so it owns no cadence:
it classifies each formula by **evaluation cost**, and the binding from cost to cadence
is a policy this library sets.

**These are two vocabularies and they must stay two.** One token cannot say both: an
iterative residual is minutes by cost and per-epoch by cadence, and a shared token
binds it to whichever sense the reader happens to hold.

| Evaluation cost — the oracle's classification | Default cadence — this library's policy |
|---|---|
| microseconds, closed form | `per-step`, on every gradient step |
| milliseconds, small linear algebra or one-dimensional quadrature | `per-batch` |
| seconds, Brillouin-zone or mesh integral | `per-epoch`, served from a cache |
| minutes, iterative or partial-differential-equation solve | `on-demand` |

The cost names belong to the registry ([named-formulas#cost-tiers]); the four cadence
names belong here. The mapping is a **default**: the loop may depart from it — gating
a cheap residual off during warm-up, or pulling an expensive one forward when a validation
signal asks for it. What the loop may not do is put a minutes-cost residual on the
per-step path.

## Sampling

Cadence says how often. Sampling says **which points**.

| Strategy | Where it fits |
|---|---|
| Uniform random | the baseline; per-step residuals whose landscape is uniform |
| Residual-adaptive refinement | add collocation points where the residual is large |
| Residual-based adaptive distribution | importance-sample points with probability rising in residual magnitude |
| Causal weighting | time-causal weighting for initial-value problems |
| Curriculum | easy-to-hard; start with the smooth, cheap residuals |

A **sampling policy** is three things: a cadence, a sampler, and an optional importance
function over candidate points. **Nothing carries all three.** The oracle's generator
record ([residual-machinery#generator-record]) carries one flat four-valued field that
fuses a sampler, two importance schemes and one evaluation-scope value, and it has no
cadence field at all. The cadence is this library's, above. The importance function has
no typed home on either side.

## The four supervisory sources

| Source | Trust | Coverage | Cost | Noise | What it constrains |
|---|---|---|---|---|---|
| Cheap compute | low | broad, all observables | milliseconds | systematic bias | smooth functional form |
| Density-functional theory | high, for what it computes | selective — energies, bands, forces; *not* transport | processor-hours | functional and mesh systematics | ground-truth electronic structure |
| Experiment | highest, where measured | sparse and observable-restricted | high | measurement noise plus sample variation | real-world calibration |
| Physics residuals | equal to trust in the oracle | tunable | microseconds to minutes | none, or known | physical consistency |

The stage ordering that decides *when* each source is live is
[training-stages#stage-ordering]. This page decides how they are weighted once they
are.

**What a ground-truth-bridge residual compares against** is a per-generator choice, and
the name for it is `compared-against` — never `source`, which already denotes a
provenance citation on a formula record. Its four values are a model, a
density-functional-theory battery, an experiment battery, and a machine-learned
interatomic potential.

Those four values are not the four rows above. Two of them are compute-side, and none
of them names a physics residual, because a physics residual is compared against a law
rather than against a datum.

## The assembled loss

```
L_total = w_cheap(t) · Σ_o∈O_cheap  m_o · squared-error(ŷ_o, y_o^cheap)
        + w_dft(t)   · Σ_o∈O_dft    m_o · squared-error(ŷ_o, y_o^dft)
        + w_exp(t)   · Σ_o∈O_exp    m_o · huber(ŷ_o, y_o^exp ; σ_o^exp)
        + Σ_i λ_i(t) · residual_i(ŷ ; state)

  m_o       label-presence for observable o on this sample, 1 or 0
  σ_o^exp   the standard deviation scaling the experimental term; whether it is
            per datum or per observable is open
  w_*(t)    source-weight curriculum schedules
  λ_i(t)    per-residual weights, set by the balancing policy
```

The residual terms are keyed and never pre-summed by the oracle
([residual-definitions#granularity]); the summation above is the loop's own reduction,
and it is the loop's because keys are what make per-law weighting and scheduling
possible at all.

## The label-presence mask

`label-presence` is the mask this library owns. For one training sample it records
**which observables actually have ground truth, and from which source**. It indexes
observable against source, and it is per sample.

It is **not** the oracle's axis-coverage mask, which indexes the axis tuples of one
named target and says which of them an imported datum constrains
([pino-bridge#axis-coverage]). It is **not** the `sample-applicability-mask` either —
the per-sample bit, over a batch, saying whether a given generator applies to that
sample at all. That mask derives from the applicability predicate
([applicability-classifiers#the-predicate-contract]): the predicate is the oracle's,
the per-sample mask is the loop's.

**All three multiply into the same loss term**, which is exactly why they need three
names. A term survives only if the generator applies to the sample, the sample carries
a label for that observable, and the axis tuple is covered by the datum. Conflate any
two and the loss is wrong and green.

Every training sample therefore carries a label-presence vector over observables, per
source, and every data term is masked by it. This is standard practice in multi-task
learning with missing labels, and it is mandatory here: without it the four source
terms cannot share a network.

## The source-weight curriculum

| Phase, by elapsed fraction | Active weights | Rationale |
|---|---|---|
| Warm-up, 0 to 0.10 | cheap high, residual weights moderate, theory and experiment low | the network learns a smooth approximate functional form from cheap data |
| Refine, 0.10 to 0.60 | cheap decaying, density-functional theory ramping, residual weights high | high-fidelity correction, with physics enforced |
| Calibrate, 0.60 to 0.90 | experiment ramping, theory held, residual weights held | experimental anchoring |
| Polish, 0.90 to 1.00 | all four balanced by GradNorm | final equilibrium |

This mirrors cascaded multi-fidelity training and composite-loss curricula, both of
which report the same two findings: early residual weight prevents overfitting to
low-fidelity data, and late experimental weight prevents drift away from real-world
calibration.

**This schedule gates source weights.** The residual-category gate
([training-stages#curriculum-pointer]) gates which laws participate. They share their
endpoints and they gate different things.

**Which run these fractions denominate is unsettled**, and the residual-category gate
faces the same question — [residual-definitions#curriculum-gate] carries it. Both
schedules inherit whatever it resolves to.

**The residual column above does not agree with the stage ordering.** It gives residual
weight from the first phase; [training-stages#stage-ordering] gives the oracle one
stage at the end. The column is what the multi-fidelity literature reports; the stage
ordering is this project's own decision. Nothing reconciles them.

## When a label and a residual disagree

When a label conflicts with a physics residual — an experimental value whose noise
violates a sum rule, say — naively summing the two forces the network onto a
Pareto trade-off between them. Three fixes are documented:

1. **Noise-aware label loss.** A Huber term scaled by the instrument standard
   deviation lets the residual win inside the experimental noise band.
2. **Constrained-optimisation framing.** Residuals as constraints, labels as
   objective, under the Karush-Kuhn-Tucker conditions. Principled and expensive.
3. **Hierarchy through weights.** The noise band is absorbed by inverse-variance
   weighting in an uncertainty-based balancing scheme.

**The first is the policy here** — a scaled Huber term — because it is the cheapest and
empirically the most reliable.

**Which standard deviation scales it is not fixed, and this page does not pre-empt it.**
The seam supplies two, and does not conflate them: the external-ground-truth call
carries a standard deviation **per datum** ([residual-machinery#subtypes]), while the
generator's characteristic scale is the observable's **declared accuracy scale**, seeded
from the ledger ([accuracy-ledger#observable-regimes]) and composed into the error
budget rather than into a loss weight. Both are reachable across the seam; only the
per-datum one varies per measurement. The formula above writes the scale per observable,
which is the survey's form and not a decision.

## What convergence does and does not guarantee

| Failure mode | Symptom | Fix |
|---|---|---|
| Gradient pathology | one term's gradient dominates | kernel balancing, GradNorm, or annealing |
| Spectral bias | low frequencies learned, high frequencies missed | Fourier features, sinusoidal representations, multi-scale loss |
| Residual stuckness | plateau far from the solution | curriculum; warm-start from cheap data |
| Stiff equations | training diverges | causal weighting; domain decomposition |
| Mode collapse onto labels | the network ignores residuals | raise residual weight through GradNorm |
| Conflicting gradients | tasks pull in opposite directions | project conflicting gradients apart |

The theory is thin and worth stating honestly:

- Convergence of physics-informed training to the true solution is proven only under
  restrictive conditions — linear elliptic equations, sufficient collocation density,
  and the neural-tangent-kernel regime (Shin, Darbon, Karniadakis 2020).
- There is **no general guarantee** for nonlinear, non-elliptic or multi-fidelity
  regimes.
- Universal-approximation results for neural operators (Kovachki et al. 2023) give
  expressivity, not trainability.

**Convergence here is empirical.** Discipline — gradient balancing, curriculum, and
masking — is what makes it work in practice, and no accuracy claim on this project may
rest on more than that.

## Defaults

Settable defaults, gathered. Each is the recommendation of a section above.

- **Outer balancing.** GradNorm across the four source families, treating the residual
  family as one task.
- **Inner balancing.** Kernel-initialised fixed weights per residual, multiplied by
  the curriculum schedule. Optional per-point self-adaptive weights for `per-step`
  residuals whose landscape is non-uniform.
- **Experimental term.** Huber, scaled by a stated standard deviation — which of the
  two the seam supplies is open, above.
- **Sampling.** `per-step` always on, full evaluation. `per-batch` always on,
  importance-sampled by residual magnitude. `per-epoch` curriculum-gated off early;
  when active, evaluated on the largest-residual fraction of the batch. `on-demand`
  never in the training gradient — it runs as a periodic validation hook that can
  trigger curriculum advancement or early stopping.
- **Curriculum knobs.** Three fractions, marking the end of warm-up, refine and
  calibrate.
- **Per-sample record.** State, per-source observation vectors, per-source
  label-presence, per-source standard deviations.

## What not to do

- **Do not use Lagrangian dual ascent for hard constraints** in the four-source
  regime. It is too unstable when the sources disagree.
- **Do not residualise a relation that can be made architectural.** If the constraint
  is expressible in the architecture, put it there.
- **Do not use a single uniform weight** across terms. It is the most common cause of
  physics-informed training failure in the benchmark literature.
- **Do not treat residuals as labels with zero noise.** They are constraints, not
  measurements, and the masking logic differs.

## References

- Raissi, Perdikaris, Karniadakis 2019 — physics-informed neural networks, J. Comput. Phys. 378
- Li et al. 2020 — Fourier neural operator, ICLR 2021
- Li et al. 2021 — physics-informed neural operator, arXiv:2111.03794
- Lu, Jin, Pang, Zhang, Karniadakis 2021 — DeepONet, Nat. Mach. Intell. 3
- Wang, Wang, Perdikaris 2021 — physics-informed DeepONets, Sci. Adv. 7
- Wang, Teng, Perdikaris 2021 — gradient pathologies, SIAM J. Sci. Comput. 43
- Wang, Yu, Perdikaris 2022 — neural tangent kernel for physics-informed networks, J. Comput. Phys. 449
- Krishnapriyan et al. 2021 — characterizing failure modes, NeurIPS
- Chen et al. 2018 — GradNorm, ICML
- Kendall, Gal, Cipolla 2018 — uncertainty weighting, CVPR
- McClenny, Braga-Neto 2023 — self-adaptive physics-informed networks, J. Comput. Phys. 474
- Meng, Karniadakis 2020 — composite multi-fidelity network, J. Comput. Phys. 401
- Lu et al. 2022 — multi-fidelity DeepONet, J. Comput. Phys. 463
- Howard et al. 2022 — multi-fidelity physics-informed DeepONet
- Elhamod et al. 2022 — composite-loss curriculum
- Wu, Lu, Xu, Karniadakis 2023 — residual-based adaptive distribution sampling, Comput. Methods Appl. Mech. Eng. 403
- Yu et al. 2020 — gradient surgery for multi-task learning, NeurIPS
- Daw et al. 2022 — physics-guided neural networks survey
- Bischof, Kraus 2021 — relative-loss balancing with random lookback
- Hao et al. 2023 — physics-informed machine learning benchmark survey
- Jagtap et al. 2020 — extended and conservative domain decomposition
- Tancik et al. 2020 — Fourier features
- Sitzmann et al. 2020 — sinusoidal representation networks
- Caruana 1997 — multitask learning
- Schütt et al. 2017 — SchNet
- Batzner et al. 2022 — NequIP, Nat. Commun. 13
- Batatia et al. 2022 — MACE, NeurIPS
- Deng et al. 2023 — CHGNet, Nat. Mach. Intell. 5
- Chen, Ong 2022 — M3GNet, Nat. Comput. Sci. 2
- Musaelian et al. 2023 — Allegro, Nat. Commun. 14
- Merchant et al. 2023 — GNoME, Nature 624
- Xie et al. 2022 — crystal diffusion variational autoencoder, ICLR
- Jiao et al. 2023 — diffusion for crystal structure prediction, NeurIPS
- Miller et al. 2024 — Riemannian flow matching for materials, ICML
- Zeni et al. 2025 — diffusion with property guidance for materials
- Kovachki et al. 2023 — neural operator theory, JMLR
- Shin, Darbon, Karniadakis 2020 — convergence of physics-informed training
- Giles, Pierce 2000 — adjoint methods
- Plessix 2006 — adjoint-state method
- Baroni et al. 2001 — density-functional perturbation theory, Rev. Mod. Phys. 73
- Jang, Gu, Poole 2017 — Gumbel-Softmax, ICLR
- Bengio, Léonard, Courville 2013 — straight-through estimator
- Lu et al. 2021 — DeepXDE, SIAM Rev. 63
- Basir, Senocak 2022 — constrained physics-informed training

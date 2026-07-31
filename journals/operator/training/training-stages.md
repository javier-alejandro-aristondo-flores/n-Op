---
id: training-stages
title: "Training stages"
owns:
  - training stage ordering
  - where the oracle attaches
  - valuation oracle distinction
  - the synthesis analogue
  - quantum search refusal
  - trained-operator failure modes
anchors:
  stage-ordering: "The stage ordering"
  oracle-kind: "What kind of oracle this is"
  why-this-order: "Why this order"
  consequences: "What follows from it"
  curriculum-pointer: "Curriculum gating of residual categories"
  limits: "Where the trained operator falls short"
depends-on:
  - residual-definitions
  - purpose-and-scope
  - pino-bridge
  - residual-loss-design
  - learnable-structure-contract
  - boundary
open-questions:
  - id: two-curriculum-schedules
    anchor: curriculum-pointer
    summary: "Residual-category gating and the source-weight curriculum share the endpoints 0.10 / 0.60 / 0.90 but gate different things; whether that is one schedule described twice or two schedules that coincide is undetermined, and it decides whether the operator gets one knob or two."
---
# Training stages

How the operator is trained, in what order, and where the oracle attaches.

## The stage ordering

**1 · Supervised epochs.** Train on density-functional-theory data. This is the coarse
work: it cuts the search space for the learnable structure down to a region worth
refining.

**2 · Informed epoch.** The oracle scores emitted states and returns keyed residuals
with their gradients. Those terms guide the final epoch.

**3 · Inference.** The operator runs alone. It calls no oracle.

What the informed epoch consumes is **keyed** residuals, one per law per axis point,
never a sum. [residual-definitions#granularity] owns that granularity; what the
ordering adds is why the loop wants it. Keys are what let the epoch weight and
schedule each law separately, and they are what makes a perturbation test meaningful:
perturb a structure and the key that fires names the law it violated.

## What kind of oracle this is

Why the system is built around a check at all is [purpose-and-scope#why-a-grader].
What follows is what kind of check it is.

A textbook oracle returns one bit: yes or no. This one returns a keyed vector of
real-valued residuals together with their cotangents — a **valuation** oracle, not a
decision oracle. That distinction is the whole reason the seam carries what it carries
([learnable-structure-contract#vector-jacobian-product]): one bit gives a learner no
direction, and a residual with a gradient does.

The honest computational analogue of the informed epoch is
**counterexample-guided inductive synthesis** — a learner proposes, an independent
checker answers, and the answer drives the next proposal — **with a gradient in place
of the counterexample**. That names what the oracle contributes better than
"physics-informed loss" does: not a penalty term bolted onto an objective, but a
directed correction from a checker that was never trained.

**Grover's algorithm does not apply**, and the question deserves an answer because it
is the first one the word *oracle* provokes. Grover needs superposition over the search
space, a *marking* oracle, and amplitude amplification, and it pays only for
unstructured search. Training has gradients and does local descent: none of the three
preconditions holds, and there is no unstructured search to accelerate.

## Why this order

**The oracle refines. It does not search.**

A residual is a **local** signal. It says how far a supplied candidate sits from
satisfying each law, and which direction reduces that. Over a large space there is
nothing for such a signal to point toward. It becomes useful once the space is already
small — which is exactly what the supervised stage buys.

So the density-functional-theory data does the searching and the oracle does the
refining. Running the informed epoch first would not work, and running it forever would
not help.

## What follows from it

- The oracle is **training-time machinery**. It is not part of the deployed model.
- Nothing on the inference path calls the oracle's validation entry
  ([pino-bridge#validate]). A trained operator is a standalone predictor.
- **Any description drawing the oracle as a permanent loop around the operator is
  wrong.** It attaches for one stage.
- The four supervisory sources ([residual-loss-design#four-sources]) are weighted
  across training. This page fixes where the physics residuals sit in that order;
  [residual-loss-design] fixes how the four are balanced once they are all live.

The seam through which the oracle attaches is unchanged by any of this: it is the same
seam a design loop would drive ([learnable-structure-contract#loop-agnostic]), and the
loop that walks these stages lives in the loops library ([boundary]).

## Curriculum gating of residual categories

The stage ordering says **when** the oracle attaches. **Which** residual categories
participate, and at what elapsed fraction, is a second schedule, and it is the
oracle's: [residual-definitions#curriculum-gate] states the gate and the fractions it
turns on. The operator library may override any fraction or any category — the
schedule is a normative default, not a contract.

**Which run those fractions denominate is unsettled**, and it is carried as an open
item on that anchor. The answer moves the gate's phases relative to the stage boundary
above, so this page does not assert one.

That schedule gates residual *categories*. The source-weight curriculum
([residual-loss-design#curriculum]) gates the four supervisory *sources*. They share
their endpoints, which is the reason to say plainly that they are addressed separately
here.

## Where the trained operator falls short

The honest half, and it does argumentative work: all three failures are **silent**,
which is the case for scoring against something that is not learned.

- **Extrapolation.** Off the training distribution the model keeps returning in-range
  values with unchanged confidence. There is no error bar, and nothing in the output
  marks which side of the support boundary a query fell on. Plain ensembles or a
  Gaussian-process head give calibrated uncertainty, but that is added machinery, not
  something the operator has by default.
- **Spectral bias.** Smooth, low-frequency components are learned first and sharp ones
  last. Band edges, defect levels inside the band gap, and sharp features in the
  density of states are exactly the sharp structures, and they come out rounded. This
  is a documented property of gradient-trained networks, not a defect of this design.
- **Data appetite.** Operator learning wants dense coverage of the input distribution.
  That is why the supervised epochs come first, and why coverage is tracked per data
  source.

None of the three announces itself. A plausible number comes back either way.

**The oracle does not fix extrapolation.** It constrains training, so the model is
pushed toward states that satisfy the laws. It is absent at inference and cannot flag
an out-of-distribution query at prediction time. Coverage metadata on the training
corpus is the honest handle on that.

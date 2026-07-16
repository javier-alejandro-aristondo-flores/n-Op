# 2026-07-16 — Research brief: the scorer ↔ stepper duality ("evolver duality")

> **Commissioning note.** Independent deep-research commissioned by Javier (2026-07-16).
> Findings land as a memo at `docs/specs/2026-07-16-evolver-duality-research.md` and commit
> to **nothing**: no atomic-tree edit, no `docs/product.md` edit, no vocabulary change may
> follow from the memo before joint review. The product spec deliberately leaves every
> time-evolution verb unclaimed until this question resolves.

## 1. The question (as posed)

> "The same abstract data structure that the oracle is built from can be re-arranged, via
> some form of abstract algebra on trees, or some other related structure, into a form that
> is numerically integrable, and thus 'steppable'. … Somehow encoding a shared state that
> can be reformed into either form."

Restated against the architecture: `/physics` compiles a typed, hash-consed dataflow DAG
(the `PhysicsGraph`, `arch-06-physics-graph`) into a **scoring kernel** — a pure function
emitting keyed law-violation residuals. Can the **same compiled structure** admit a second
lowering into a **time-stepping kernel** — one IR, two interpreters (scorer ↔ stepper)?
If yes, under what algebraic conditions, for which subgraphs, and with what refusal rule
for the rest?

## 2. Why this is plausible on our substrate (the concrete seed — verify, don't assume)

- The IR's equation-of-motion residuals are structurally `r = LHS(dx/dt) − RHS(x, env)`.
  A stepper is precisely the isolation of the RHS: re-arranging the residual graph to
  expose `dx/dt = f(x, env)`. That re-arrangement is what the acausal-modeling world calls
  **causalization** — it is an existing, mechanized compiler pass in that literature, not
  a speculative operation.
- The dynamical form is first-order with **structured generators** — a reversible +
  dissipative split carrying degeneracy side-conditions and sign/symmetry tags
  (`arch-05-generic`) — so the target class for structure-preserving integrators is
  already algebraically tagged inside the IR rather than needing rediscovery.
- The pipeline already performs exact algebraic rewrites (`arch-07-pipeline`, Stage 3) and
  already synthesizes a *second program* from the same graph — the adjoint, at Stage 4. A
  stepper would be a **third emission from the same compile**. Under the product's
  artifact model (`docs/product.md`), it would ship as a sibling oracle-file with the same
  content-addressed identity discipline (`arch-20-representations §20.4`).
- The state is tiered with per-tier generators and heterogeneous timescales
  (`arch-21-multiscale-state`), so "steppable" plausibly means **multi-rate** steppable —
  the research must address tiered integration, not only single-clock ODE stepping.

## 3. Coverage demanded (research each; primary sources)

1. **Acausal equation-based model compilation** (the industrial embodiment of exactly this
   re-arrangement): Modelica-class structural simplification — sorting into
   block-lower-triangular form, tearing, alias elimination, causalization; OpenModelica /
   Dymola compiler literature; **ModelingToolkit.jl** as the closest living system
   (symbolic system → `structural_simplify` → integrable problem object). What are the
   preconditions, the failure modes, and the complexity of these passes?
2. **Structural index analysis and DAE index reduction as graph algebra**: the Pantelides
   algorithm, the dummy-derivative method, the Σ-method. When does high-index structure
   block direct stepping, and how is it mechanically repaired? What does "index" look like
   for *our* graph class?
3. **Rewriting substrates for the re-arrangement itself**: e-graphs / equality saturation
   as the working "abstract algebra on DAGs"; soundness conditions for rewrites under
   AD-safety; interaction with hash-consing and content addressing (does saturation
   preserve our identity discipline or fork it?).
4. **One-IR-many-interpreters formalisms**: initial algebras / recursion schemes /
   tagless-final. What does it *formally* mean for "scorer" and "stepper" to be two
   algebras over one term functor; what properties must the op-signature satisfy so both
   interpretations exist; where does the formalism predict the duality must break?
5. **Structure-preserving integration for the tagged system class**: splitting and
   projection methods for reversible + dissipative decompositions (the
   metriplectic/GENERIC-integrator literature), what an integrator must *consume from* the
   structure tags (degeneracy conditions, sign/PSD structure) and *preserve*; multi-rate /
   heterogeneous-cadence schemes fitting the tiered state (`arch-21-multiscale-state`).
   Behavioral framing — no derivations beyond what the argument needs.
6. **Fit against the existing spec** — read before writing: `docs/computational-overview.md`;
   `docs/architecture/05-generic.md`, `06-physics-graph.md`, `07-pipeline.md`,
   `18-open-decisions.md`, `21-multiscale-state.md`, `16-pino-bridge.md`;
   `docs/product.md`. Where do the closed vocabularies (`arch-09-vocabularies` — methods
   including `kinetic-evolution`, the cost tiers with T3 fixed-point solves, the
   differentiability tags) help or obstruct re-formability? Which registry-entry *classes*
   would refuse a stepper lowering (cert-only generators, `Import`-pinned reference nodes,
   pure reads, implicit fixed-point methods, …) and what is the principled refusal rule?

## 4. Demanded deliverable (the memo)

`docs/specs/2026-07-16-evolver-duality-research.md`, containing:

1. **Survivability verdict** on the shared-structure idea: *survives / survives with
   restrictions / dies* — argued from the researched material, not asserted. A
   well-argued "dies" is a fully successful outcome of this commission.
2. **The algebra**: the properties the IR / op-signature must satisfy for re-formability,
   stated precisely; which existing vocabulary entries or graph constructions violate
   them, named.
3. **The shape of a "steppable lowering"** as a *possible* spec addition — a Stage-4
   sibling emission? a separate pipeline? — behavioral only: artifacts, contracts, and
   invariants; no code, no language choice.
4. **Refusal cases**: the principled rule for subgraphs that cannot be causalized, and
   what the product should do there (refuse-by-absence, per the product's existing
   refusal semantics).
5. **A proposed resolution of the open integrator-interface decision**
   (`arch-18-open-decisions`), conditional on the verdict.
6. **Sources**: primary and citable (papers, canonical tool documentation). No blog-tier
   citations for load-bearing claims.

## 5. Constraints

- Computational vocabulary throughout; domain content only where the mathematics demands
  it.
- Honesty over enthusiasm; restrictions and refusals are results, not failures.
- The memo is the only file the researcher writes. Machines
  (`python docs/meta/lint.py`, `python docs/meta/assemble.py --check`,
  `python docs/meta/seams.py`) must remain green afterward.

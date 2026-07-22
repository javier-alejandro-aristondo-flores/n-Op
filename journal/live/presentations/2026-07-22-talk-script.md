# Talk script

*~25–30 min · 14 slides, 12 figures · figures in `figures/`, slide N uses fig N−1.*

Audience: materials scientists, EEs, physicists. They have the physics; the CS is the new part.
Spine: operator predicts material behaviour → its loss needs physics → oracle compiles the laws
into keyed differentiable residual terms that enter that loss. No proposer. Inverse design is a
direction, not a claim.

Pacing: slides 2–7 are the argument — ~2½ min each. 8–12 are machinery — ~90 s. Run long, cut
machinery, never the first half.

---

## 1 · Title

**Screen:** title, name, affiliation.

- CS undergrad, working on crystals.
- Claim: there's a CS-shaped problem in here, and treating it as one buys things.
- One line: compile the laws into a fast, checkable program; use it to keep an ML model honest.
- Half of this is complexity theory and compilers. Physics only where it pays.

## 2 · Two incumbents · `fig-01`

- Target: material behaviour at device conditions — >500 °C, high field, radiation.
- Direct DFT: trustworthy, unaffordable there.
- ML surrogate: cheap, unreliable under extrapolation — and fails *silently*. Returns a confident
  number at 900 K after training at 300 K.
- Empty quadrant. Instinct is to compromise along the diagonal. Don't — change the object.

## 3 · Hardness · `fig-02`

- Classical lattice ground states: NP-hard (Barahona '82).
- General quantum case — local Hamiltonian — QMA-complete (Kitaev).
- No efficient general algorithm under standard assumptions. Hardware doesn't move the wall.
- Other direction: checking a supplied candidate is cheap. That asymmetry *is* NP.
- So: not a faster solver. A cheap checker.

## 4 · Oracles · `fig-03`

- Oracle = black box, one query, unit cost. Used to stratify difficulty: `P^A`, `NP^A`; PH is
  iterated oracle access.
- Known limit: BGS '75 — oracles exist both ways, so relativizing arguments can't settle P vs NP.
- Ours is not a decision oracle. Returns a residual vector + gradients, not a bit.
- Reason: a bit gives a learner no direction. Valuation oracle, not decision oracle.

## 5 · Witness completeness · `fig-04`

- Cheap verification requires the *complete* witness.
- Partial witness — structure only — and the checker must solve for the electronic state. Back in
  the hard class.
- Complete witness → one pass.
- So score-not-solve is a complexity constraint, not a style preference.
- Consequence: the operator carries γ̂. The expensive part is exactly what we want learned.

## 6 · The system · `fig-05`

- Four objects, four maps. θ → x → (r, ∇r) → L → θ.
- Operator emits a complete state. Oracle scores it against the laws. Residuals are terms in the
  loss. Gradient returns to weights.
- Oracle is one arrow: no solving, no proposing, no loop, no verdict.
- Residuals stay keyed — per law, per axis point. Not one scalar. That's what lets you weight,
  schedule, and audit them individually.
- Status: spec'd and adversarially audited, **zero code**. Every number today is a design
  commitment, not a benchmark.

## 7 · The artifact · `fig-06`

- Compile once per material identity → a file. Not a service, not a framework.
- Four parts: the callable; the slot schema; a content-hash ID; a pinned cert.
- Slot schema means it's self-describing — enumerate every check it contains. Not in the list ⇒
  not there.
- ID: file hash = kernel hash. Provenance is a lookup, not archaeology.
- Cert travels with it.
- Immutable — new pin, new registry version, new identity ⇒ new file.
- Two outputs overall: per material, this file. Across the programme, a model whose predictions
  carry evidence.

## 8 · Grammar · `fig-07`

- CIF + conditions is a *compile request*, not a scoreable object. Parse, then elaborate.
- Closed grammar: 132 formulas, 12 methods, 20 templates, 11 bundles. No free-form expressions.
- Walk the tree: κ_lattice derives to a template and a method; terminals are registry rows — 9, 10,
  25. An observable is a sentence, not new code.
- Dotted branch is pruned: `is-polar` is false for diamond, so the polar scattering term never
  enters the kernel. Applicability is first-order decidable, and non-decidable classifiers are
  rejected at registration.
- So a request compiles or is refused with a reason — before it costs cluster time.
- Rest of the compiler, briefly: cross-formula CSE, hash-consing, tearing, then lowering + codegen.
- Two time scales: compile s–min once per material; call µs–ms, millions of times. Partial
  evaluation (Futamura), not a trick.

## 9 · Symmetry · `fig-08`

- Operator commutes with the group ⇒ Schur ⇒ block-diagonal by irrep. Blank blocks are work
  avoided.
- Sampling collapses onto orbits — one representative each.
- Cost scales with orbits, not points. Paid once, at compile.

## 10 · Cost · `fig-09`

- Commitment: no per-sample hot path worse than `O(log n)`, and none calls a solver.
- Left: the shaded band is the admissible region. Set membership, map lookup, BDD evaluate, verdict
  meet — all of them sit inside it. `O(n)` is excluded by construction.
- Deliberately falsifiable — each op is checkable against the bound.
- Gradients: naive reverse mode tapes all N iterations. IFT adjoint at a converged fixed point is
  one linear solve — flat in N.
- That's the difference between gradients being affordable and being the blocker.

## 11 · Refusal · `fig-10`

- Applicability as a BDD over material predicates.
- Terminal `absent`: the check isn't in the compiled kernel. No zero, no NaN, no silent fallback to
  an inapplicable formula.
- Absence carries a machine-readable reason. So a file's coverage is enumerable — including its
  gaps.

## 12 · Trust · `fig-11`

- Cert per kernel: obligations, verdicts, numeric witnesses. No prose anywhere.
- Aggregation is a semilattice meet. One `Failed` ⇒ `Failed`.
- Content-addressed throughout: file hash = kernel hash. Reproducibility is structural, not
  procedural.

## 13 · Sign trap · `fig-12`

- Two conventions for one quantity. Both correct in-frame.
- Lift `b` across ⇒ bowing inverts ⇒ interface charge takes the wrong sign. Review doesn't catch
  it — the wrong version is as plausible as the right one.
- 51 in the register. Most found *after* something had been stated wrongly.
- Fix: state the invariant once, canonically; machine-check it. Care isn't a mechanism.
- Own example: the seams checker scanned formula names in one syntactic position, missed another.
  Reported clean. Widening it surfaced 17 real findings. A narrow parser fails quietly.

## 14 · Close

**Screen:** *Verifying is cheaper than solving.*

- General problem stays intractable. Checking is cheap. Put the checker inside the loss.
- Out: per material, a file that states what it knows and refuses the rest. Across the programme,
  a model whose predictions arrive with evidence.
- Frame's own limit: relativization — an oracle only tells you what's reachable *relative to what
  it's handed*. Which is why witness completeness was the load-bearing decision.
- Not faster physics. Addressable, checkable, reproducible physics.

---

## Backup slides

Specs in the outline; render if asked.

- CSE / hash-consing — "which optimisations?"
- CEGIS side-by-side — "has this shape been done?" Yes; gradient replaces the counterexample.
- Pullback square — for a categorical questioner.
- Evolver negative result — "what doesn't work?" One IR for scorer *and* stepper: strong form
  refuted (causality assignment is global matching, not per-node); shared-kernel form survives.

## Likely questions

- **Benchmarks?** None. Zero code. Design commitments; spec'd and audited, not built. Say it early.
- **Does it design materials?** No, and the oracle doesn't try — inverse design is out of scope for
  it. The contract stays compatible with that direction.
- **Time evolution / lifetime?** Unclaimed. Researched; verdict was "survives with restrictions";
  waits on its own wave.
- **Language?** Open, being re-evaluated. A polyglot proposal is documented; treating it as a
  candidate.
- **Isn't this a PINN?** Same family, different rigour. A PINN adds a penalty term. This compiles a
  closed, versioned, citation-traced vocabulary into a certified artifact, keeps every residual
  separately addressable, and refuses what it can't stand behind.
- **Why an undergrad on this?** The failure modes here are CS failure modes — conventions, naming,
  provenance, parsers. Fifty-one documented cases where care wasn't enough.

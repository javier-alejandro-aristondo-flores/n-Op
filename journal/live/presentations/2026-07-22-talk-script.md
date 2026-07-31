# Talk script

*~13 min · 10 slides. Every bullet is a line to say out loud, roughly as written.*

Audience: materials scientists, EEs, physicists. They have the physics. The CS is the new part.

3 argues the architecture and 7 gives its limits. 4 is the object against real data;
5 and 6 are why it's shaped that way and how data earns its way in. 8 and 9 are the checker.

---

## 1 · Title

**Screen:** title, name, affiliation.

- I'm a CS undergrad, and I work on crystals.
- Half of this is complexity theory and compilers. The claim is that the data structure and the
  physical law are the same object.

## 2 · What this operator does · `fig-02`

- The operator does channel completion. You hand it a topology plus whatever properties you know,
  and it returns the ones you didn't.
- Some channels are constants, some are curves. All of them are functions.
- The topology has to be there, or the problem is one-to-many. What I'm after is predicting crystal
  structures.

## 3 · Why an operator · `fig-03`

- A few things here push toward an operator rather than a fixed-size network.
- The channels are functions — the density matrix over two points in space, the field over space
  and time. A wide output layer has to pick a grid and commit to it, and the meshes change per
  material.
- The oracle also evaluates residuals at arbitrary points on an axis, nowhere near the training
  grid, and the model has to answer there.
- And the physics is nonlocal, so a kernel that sees the whole cell in one layer beats a local
  stencil.

## 4 · The state, against a real run · `fig-04`

- The record is seven slots, and this is it measured against a real calculation. Hydrogen in a box,
  four ionic steps.
- h is the cell. R and P are the ion positions and momenta, and Pi-h is the cell's own momentum.
- Z is species — the only discrete slot, and it never changes. No gradient runs through an integer,
  so you can't search over composition by descent.
- Gamma-hat is the one-body density matrix, a function of two points in space. A is the external
  field.
- Three slots come straight out of the run. Gamma-hat is partial — the charge density file gives me
  the diagonal, and the off-diagonal needs a wavefunction file this run didn't write.
- Three are missing, for three different reasons. Two are settings: I froze the cell, and this was a
  relaxation and not dynamics, so I've plotted the conjugate quantities instead.
- The vector potential is different. It doesn't exist in the theory that produced these files.
  That's the term n-Op adds.

## 5 · Why those seven · `fig-05`

- This is the law I care about. L is the reversible part, antisymmetric and energy-conserving;
  M is dissipative and makes entropy.
- Elastic response, phonons, transport and optics are all restrictions of that one law.
- L acts on conjugate pairs, so the momenta have to be in the state. The record is the domain of the
  law, not a schema I picked. Leave a slot out and you've deleted the physics that needed it.

## 6 · Getting data in · `fig-06`

- Before I read a run I hash its settings — functional, cutoff, pseudopotentials, k-mesh, smearing,
  symmetry. Energies only compare within one hash.
- Then it has to pass arithmetic it already claims. Forces sum to zero, stress is symmetric,
  occupations count the electrons, the determinant matches the volume. One frame, closed form, free.
- Past that gate every value carries an uncertainty or it doesn't go in. Either I compute the same
  shape twice and look at the spread, or I read the components symmetry says must vanish. Either way
  that's precision, not accuracy.

## 7 · Where it falls short · `fig-07`

- The honest other half. Two failure modes, and both are quiet.
- Off the training distribution it keeps answering, in range, with the same confidence. And spectral
  bias means smooth modes get learned first and sharp ones last, so band edges and defect levels
  come out rounded.
- Neither announces itself, which is the argument for scoring the output against something that
  isn't learned.

## 8 · The checker, and where it goes · `fig-08`

- Running DFT directly at device conditions is trustworthy and unaffordable. Finding a ground state
  is NP-hard — Barahona, 1982 — and the quantum version is QMA-complete, which is Kitaev. But
  checking a candidate you already have is one pass.
- So I build the checker. A textbook oracle hands back one bit; mine hands back one residual per
  law, with gradients, because a bit gives a learner no direction to move in.
- It attaches here. Supervised epochs on VASP data first, which is what narrows the search space,
  then the informed epoch, where the oracle scores the operator's output into the loss.
- The data does the searching and the oracle only refines. At inference the operator runs alone.
- Residuals stay keyed and never summed, so I can weight them and see which law fired. And none of
  this is implemented yet — every number is a design target.

## 9 · What gets checked · `fig-09`

- These are named laws, not one penalty term.
- Forces vanish at a relaxed structure. Phonon frequencies squared stay non-negative on anything
  claimed stable. The density matrix is Hermitian, eigenvalues between zero and one, trace is the
  electron count. Then conservation, algebraic identities, thermodynamics and symmetry — nineteen
  categories.
- The last few need gamma-hat, so you can't get them out of geometry. That's why the operator hands
  over the whole record.

## 10 · Close

**Screen:** *Verifying is cheaper than solving.*

- The general problem stays hard and checking stays cheap, so put the checker inside the loss.
- Pick the state so the law fits it, and make the data pass a gate before it gets in.
- Thanks — happy to take questions.

---

## Backup slides

On disk in `figures/unused/`. Render if asked.

- The seven slots as a plain table, without the run — `fig-04-state`.
- Find versus check, the search tree against one pass — `fig-09-hardness`.
- The closed grammar: a CIF compiles, guards prune, seconds to compile and microseconds to call —
  `fig-12-grammar`.
- Fingerprint and the invariant battery, drawn out — `fig-04-admission`.
- Green–Lagrange strain, both routes, and the transpose trap — `fig-06-strain`.
- Clamped versus relaxed off the trajectory, and Kleinman zeta — `fig-07-trajectory`.
- Cost tiers and preconditions — `fig-09-tiers`.
- Delta-transferability, is the correction constant — `fig-10-delta`.
- Accuracy targets per observable, with uncertainty and source.
- What it refuses, and the physical reason for each.
- CEGIS side by side, with a gradient in place of the counterexample.

## Answers to have ready

Short versions. The long ones are in the prep doc.

- **Oracle at inference?** No, training-time only. A trained operator is a standalone predictor.
- **Why not residuals alone?** Local signal, nothing to point at over a big space. VASP narrows first.
- **Benchmarks?** None. No code yet. Everything I quoted is a design target.
- **Does it design materials?** No. Inverse design is out of scope for the oracle.
- **Why is species immutable?** It's discrete. Composition search needs something off the gradient
  path, which is a different problem.
- **Time evolution?** Researched, survives with restrictions, not claimed yet.
- **What language?** Open. There's a polyglot proposal and everything in it is a candidate.
- **Isn't this a PINN?** A PINN adds a penalty term by hand. This compiles a closed, cited
  vocabulary into an artifact, keeps every residual addressable, and refuses what it can't back.
- **Topological materials?** That Kitaev result is the complexity one, not band topology. There's a
  topology atlas, but it classifies a structure you hand it. It generates nothing.
- **Why an undergrad?** The failure modes are CS failure modes — conventions, transposes,
  provenance, parsers. 51 documented cases where care wasn't enough.

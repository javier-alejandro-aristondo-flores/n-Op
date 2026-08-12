# The decision docket — auditor 3, pass C

Six questions the audit marked **physics-gated**: Javier's alone, because each needs a
judgment no amount of corpus-reading settles. This file does not leave them blank. Each
carries the corpus text it rests on, what is actually true, both branches costed, and **a
recommendation to ratify or reject**.

**Nothing here is applied.** The corpus is untouched by this pass. Ratification produces a
separate, gated edit batch.

Two of the six — §5 and §6 — **contradict Javier's own recorded design intent**. That is
said plainly at the head of each rather than buried, because a recommendation that quietly
overrules the person who has to ratify it is worth nothing.

Every corpus-invented name is written in English, with the corpus's own token given once as
a locator. Symbols appear only inside equations.

---

## 1 · The continuity equation, and whether the state needs a second current field

**Verdict: the corpus's drift-diffusion balance is wrong three ways, and only one of them is
a sign.**

### What the corpus says

The macro tier's state, from `multiscale-state.md`:

> n,p : Field[DeviceMesh → ℝ₊]   [m⁻³],
> j   : Field[DeviceMesh → ℝ³]   [A·m⁻²] )

**Two carrier densities, one current field.** The momentum closure on the same page derives
both currents correctly and knows they differ:

> Drift-diffusion gives `j_n = q·μ_n(E,T)·n·E + q·D_n·∇n` for electrons and `j_p = q·μ_p·p·E − q·D_p·∇p` for holes: **only the diffusion term changes sign between carriers, never the drift term.**

But the homogenization map writes a single balance:

> (DD) ∂_t n + ∇·j = G − R,   j_n = q·μ_n·n·E + q·D_n·∇n

### What is wrong with it

**a. Dimensions.** The state declares carrier density in `m⁻³` and current in `A·m⁻²`. So
`∂_t n` carries `m⁻³s⁻¹` and `∇·j` carries `A·m⁻³ = C·m⁻³s⁻¹`. **The two terms cannot be
added** — they differ by exactly one factor of charge. The missing `1/q` is not cosmetic; it
is what makes the equation an equation.

**b. Sign.** Charge continuity is `∂ρ/∂t + ∇·J = 0`. For electrons the charge density is
`−q·n`, so the correct balance is `∂_t n − (1/q)∇·j_n = G − R`. The corpus has `+∇·j`. The
sign is inverted for electrons — and it is inverted *because* the carrier's charge sign was
dropped along with the `1/q`. One omission, two symptoms.

**c. The same symbol means two different things four lines apart.** `(DD)` uses `j` where it
defines `j_n` — the electron current. `(H)` uses the same `j` for Joule heating:

> (H)  C_p·ρ_m·∂_t T_L − ∇·(κ(T)∇T_L) = j·E

Joule heating is driven by the **total** current, `j_n + j_p`. So `j` is the electron current
in one line and the total current in the next.

### Why one current field cannot survive

This is a **semiconductor** oracle. Bipolar transport is not an optional refinement:

- The Poisson equation on the same page reads `ρ = q(p − n + N_D⁺ − N_A⁻)` — both carriers.
- `p` is a state field with, under the single-current reading, **no equation of motion at
  all**. A state variable the dynamics cannot move is not a state variable.
- The residual set contains an avalanche-multiplication guard, `max(0, ∫α dx − 1)²`, registry
  row 75. **Avalanche breakdown is definitionally bipolar** — electrons and holes each
  multiplying, each feeding the other. One current field cannot express it.
- The downstream target is high-field, high-current-density power devices. That regime *is*
  the bipolar regime.

### Recommendation

**Carry two current fields. Write the balances per carrier with the charge factor explicit.**

```
state:  ( T_L, φ, n, p, j_n, j_p )

(DD_n)  ∂_t n − (1/q)∇·j_n = G − R
(DD_p)  ∂_t p + (1/q)∇·j_p = G − R
(H)     C_p·ρ_m·∂_t T_L − ∇·(κ(T)∇T_L) = (j_n + j_p)·E
```

**Cost:** the macro state tuple grows from five fields to six; the continuum
equation-of-motion residual gains one axis; current storage on the device mesh doubles. That
is cheap, and it is the only reading under which `p` is a real state variable.

**What ratifying changes:** the macro state tuple in `multiscale-state.md`; the three
balance equations; the Joule-heating source; and the residual's axis structure. It is a
**state-type change**, which is why it is not a mechanical correction.

---

## 2 · What the electromagnetic vector potential slot actually is

**Verdict: the corpus's architecture already answers this. One word contradicts it.**

### What the corpus says

`unified-state.md` types the slot as external:

> A )     external EM vector potential       ∈ ℝ³ field A(r,t)

But `generic-dynamics.md` gives that same slot every attribute of a genuine dynamical degree
of freedom — its own energy:

> + E_EM[A]          (1/8π) ∫ (|E_⊥|² + |B|²) dr   — transverse sector only;

its own block in the Poisson operator:

> · Maxwell on A                 Hamiltonian form of the EM field

and its own equation-of-motion residual, `EOM/A`, listed among the nine. And then the gauge
partition says so outright:

> This is the standard nonrelativistic-QED partition: transverse field dynamical, Coulomb interaction instantaneous in the matter sector.

**"Transverse field dynamical."** The architecture is unambiguous. Only the slot's type
annotation disagrees with it.

### The three readings, and what each costs

| Reading | What it means | Cost |
|---|---|---|
| **Purely external and prescribed** | The field is a given drive; the system does not own it | The field energy leaves the system energy, the Maxwell block leaves the Poisson operator, and the `EOM/A` residual is deleted or demoted to an input check. **The closed enum of 19 categories changes** — nine equation-of-motion categories become eight |
| **External but free-field evolving** — obeys source-free Maxwell, matter does not source it | "External" means "not matter-sourced," not "not evolved" | **Energy conservation fails by construction.** Matter absorbs from a field that is never depleted, so the conservation residual fires permanently on every driven system — a false positive the oracle can never clear |
| **Fully dynamical and matter-sourced** | A genuine state slot; the caller supplies a self-consistent light–matter state | The operator must learn to emit a self-consistent transverse field. Real work — but the operator's, not the oracle's |

### Recommendation

**The third. Delete the word "external" from the slot type.**

Everything else in the corpus already implements this reading. It is the only one under which
the field energy legitimately sits in the system energy, the Maxwell block legitimately sits
in the Poisson operator, the `EOM/A` residual is a genuine equation-of-motion check, and
energy conserves.

**It does not violate score-not-solve.** That principle says the *oracle* never solves — the
*caller* supplies a complete state. A self-consistent field is exactly the kind of hard
channel the operator exists to produce.

### Correction — this is not a one-word fix

An earlier draft of this section called it *"the cheapest possible fix: one word."* **That was
wrong**, and pass B's angle 3 is what caught it. Deleting *"external"* is necessary and not
sufficient, because **the vector potential has no conjugate momentum.**

Every other dynamical slot arrives as a canonical pair — positions with momenta, the cell with
its momentum, each carrying its own symplectic block and its own residual category. `A` arrives
alone. Yet the corpus asserts its Maxwell block is *canonical*, which is a claim about a
conjugate pair:

> Canonical blocks (symplectic `(R,P)`, `(h,Π_h)`; Lie–Poisson `γ̂`; Maxwell `A`)

In the Coulomb gauge the corpus fixes, the transverse field's canonical momentum is the
transverse electric field. **It is independent initial data** — `A` and `E_⊥` are the two
quadratures of each mode, and `E_⊥` is not recoverable from `A` at an instant. So it is not
emergent under the corpus's own axiom, it belongs to no other tier, and it is not one of the
seven.

The energy functional makes this self-evident: it is written as a functional of `A` alone and
its integrand contains `E_⊥`. `B = ∇×A` is recoverable; `E_⊥` is not. **So `E_EM[A]` is not a
functional of `A`, `δE/δx` has no computable value on that block, and the `EOM/A` residual has
no right-hand side.**

Verified by hand: `conjugate` occurs exactly twice in the corpus — once as `conjugate-gradient`,
an optimizer and a false friend, and once as the cell-metric conjugate. Control fires — `Π_h`
returns its slot, its symplectic block, its residual category and its kinetic-energy term, the
full complement of a carried conjugate momentum. `A` has none of them.

**Revised recommendation: delete "external" *and* add an eighth slot** carrying the transverse
electric field as `A`'s conjugate momentum. The one-word version leaves the equation of motion
undefined.

### This is the second of three independent holes in the state type

Three findings, three different routes, all landing on the same object:

| Hole | Route | What the state cannot represent |
|---|---|---|
| No second current field | pass C, §1 above | Bipolar transport — and `p` has no equation of motion at all |
| No conjugate momentum for the field | pass B, angle 3 | The transverse field's other quadrature, so `EOM/A` has no right-hand side |
| No isotope, only atomic number | pass B, angle 3 | ¹²C versus ¹³C — in a **diamond-first** build, where the mass difference is 8.3%, phonon frequencies scale as `M^(−1/2)`, and `traps.md` **enforces** an isotope declaration on every thermal-conductivity reference row that the state type cannot carry |

**The state type should be reopened once, for all three, rather than patched three times.**

---

## 3 · The metastability band's currency

**Verdict: the band is stated in one currency and consumed in another, and the residual fires
on the single example the corpus offers as reading zero.**

### What the corpus says

The tolerance ledger, `cert-obligations.md`:

> | `δ_meta` | temperature-and-pressure hull metastability band ([residual-definitions]; the hull formula in the registry) | `50 meV/atom`, per-material overridable — diamond at +25 reads inside the band |

And the residual, `residual-definitions.md`:

> `max(0, ΔG_form(T,P) − ΔG_hull(T,P) − δ_meta)²`, whose band lets diamond
> read `R = 0` at its Berman–Simon boundary point of +25 meV/atom at 300 K

### What is actually true

**+25 meV/atom is the experimental number.** The Berman–Simon line is a measured phase
boundary. But the residual does not consume a measured number — it consumes
`ΔG_form − ΔG_hull` **as the oracle's own machinery computes it**, which is density-functional
theory.

Diamond's computed distance above hull under the corpus's default functional is
**138.297 meV/atom** (Materials Project `mp-66`, `gga_gga+u`, retrieved 2026-07-31),
corroborated to about 1 meV/atom by an independent 1997 calculation reporting 131.

Against a 50 meV/atom band the residual evaluates to `(138.297 − 50)² ≈ 7.8×10³ (meV/atom)²`
— **on the one material the ledger names as reading inside the band.**

Admitting diamond under the corpus's own functional needs a band of about 139 or wider, at
which point the residual admits nearly anything and discriminates nothing. A different
functional does not rescue it: r2SCAN gives 115.

### The explanation that is wrong, recorded so it is not re-argued

The intuitive diagnosis — *"PBE lacks dispersion, so graphite's interlayer binding is
missing"* — **predicts the wrong sign.** PBE recovers almost none of graphite's interlayer
binding, which leaves graphite too high in energy and pushes diamond's distance above hull
*down*. Restoring dispersion makes the number **worse**, toward 180.

The tell is LDA, which gives about 20 meV/atom. LDA over-binds interlayer; if an interlayer
mechanism were responsible, LDA would move toward graphite, not away from it. The sign flip
lives in **GGA exchange on the intra-layer covalent energetics** — the sp³-versus-sp²
comparison — not in dispersion.

### Recommendation

**A tolerance must be stated in the currency of the quantity it bounds.** Therefore:

1. The ledger row carries the **functional** it is valued against. A hull-distance band
   without a functional tag is not a number.
2. Diamond's per-material override is seeded from a **computed** distance under that
   functional, not from the Berman–Simon experimental value.
3. **The clause "diamond at +25 reads inside the band" is deleted.** It is true in
   experimental currency and false in the currency the residual consumes, and it is the
   sentence that makes the defect invisible.

**Confidence note.** The 138.297 figure was retrieved in an earlier session and I have not
re-queried it here. The recommendation does not depend on its precision — any value
substantially above 50 breaks the claim identically, and three independent methods (PBE 138,
r2SCAN 115, LDA 20) all disagree with 25.

---

## 4 · The nudged-elastic-band tolerance's currency

**Verdict: sharper than a missing sign — the row carries no unit at all.**

### What the corpus says

> | `τ_NEB` | `PathStationaryOf` climbing-image nudged-elastic-band force convergence | `1e-3` |

Every neighboring row in that same table carries a unit: `1e-6 relative`, `1e-9 absolute`,
`1e-8 Ha`, `1e-4 Ha`, `50 meV/atom`. **This row is the only bare numeral in its own table.**

### What is actually true

`1e-3` is *exactly* VASP's default `EDIFFG`, and in VASP the **sign selects the currency**:
positive is an energy change in eV, negative is a force in eV/Å. The corpus carries no sign,
so the numeral inherits neither.

The two readings are two orders of magnitude apart and give opposite verdicts:

- **As a force**, `1e-3 eV/Å` is **50× tighter** than both the ASE and Quantum ESPRESSO
  defaults of `0.05 eV/Å`, and likely unreachable against ordinary force noise.
- **As an energy**, `1e-3 eV` is about **2× looser** than typical practice.

And an energy test **cannot certify what the obligation's own name asserts.** A climbing-image
band is stationary in energy at the saddle by construction, so the energy change can pass
while the perpendicular force is still large. The name says *force convergence*; only one
reading can deliver it.

### Recommendation

**Force, negative sign, and re-value.** Write it as `-5e-2 eV/Å` — the ASE and Quantum
ESPRESSO default — or state a tighter value deliberately with the reason. The row must carry
its unit like every other row in the table.

This is the one item on this docket where the evidence points to a single answer with no live
counter-argument. It is here rather than on the mechanical list only because changing a
convergence tolerance changes what the oracle certifies.

---

## 5 · Stage ordering — where the oracle attaches

> **This recommendation contradicts Javier's recorded design intent.** The intent is that
> supervised epochs narrow the space first, the oracle guides the final epoch only. It is
> recorded as a project decision, and it is what the corpus says. I am arguing against it.
> Reject freely.

### What the corpus says

`training-stages.md` argues the oracle attaches late:

> **The oracle refines. It does not search.**

> So the density-functional-theory data does the searching and the oracle does the
> refining. Running the informed epoch first would not work, and running it forever would
> not help.

### What is actually true

**Seven of seven papers checked prescribe physics residuals throughout training, not in a
final stage.** So does the corpus's own curriculum category gate, which schedules residual
categories across the full training fraction in four phases — Warmup, Refine, Polish,
Cooldown — starting at `0.00`. The corpus therefore contains both positions, and its own
`curriculum-denominator` open question is this same disagreement wearing a different hat.

**But the corpus's argument is not wrong — it is aimed at the wrong variable.** The documented
failure mode it describes is real: when a physics residual dominates early, the loss landscape
is stiff and the network collapses toward trivial solutions. That is precisely why the
loss-balancing literature exists — gradient-norm balancing, neural-tangent-kernel weighting,
self-adaptive weights.

**The reconciliation is weight, not presence.** The residual is present from the start at a
small weight that ramps. It is never *absent*. That is what all seven papers do, it is what
the four-phase gate describes, and it preserves the corpus's own insight — early on, the
supervised data dominates the loss anyway, so the oracle is not being asked to search.

### Recommendation

**Attach the oracle from the start with a ramped weight. Replace "one stage only" with "one
weight schedule over the whole run."**

**One decision closes two questions**: the curriculum gate's denominator resolves to the whole
training run, and the `curriculum-denominator` open question dies with it.

**Cost of ratifying:** the operator holds the oracle through training rather than for one
stage, so compiled kernels must be resident throughout. **Cost of rejecting:** the corpus keeps
two incompatible schedules and the denominator question stays open — that cost is real and
should not be paid silently.

---

## 6 · Whether the oracle stays absent at inference

> **This one also contradicts Javier's recorded design intent** — *"never imply an oracle call
> at inference."* Same standing: argued, not assumed.

### What the corpus says

> **3 · Inference.** The operator runs alone. It calls no oracle.

And it names the consequence as its most-emphasized limitation:

> **The oracle does not fix extrapolation.** It constrains training, so the model is
> pushed toward states that satisfy the laws. It is absent at inference and cannot flag
> an out-of-distribution query at prediction time. Coverage metadata on the training
> corpus is the honest handle on that.

### What is actually true

**That limitation is a consequence of the deployment choice, not a property of the oracle.**
The oracle costs microseconds to milliseconds per call — the same order as the operator's own
forward pass. Calling it on the operator's output roughly **doubles** inference cost.

What that buys is the exact thing the corpus names as missing. Coverage metadata says *"this
query is far from training data."* A residual says *"this answer violates this law by this
much"* — per law, per axis point, with a key naming the law. **The residual is the strictly
better out-of-distribution signal**, because it grades the answer rather than the question.

**The real constraint is not cost — it is compilation.** The oracle is compiled per crystal
identity. If the query names a crystal with no cached kernel, there is nothing to call, and
compiling takes seconds to minutes against an inference budget of milliseconds. So the oracle
can score at inference **exactly when the query's identity has a cached kernel** — which, for
the design loop's enumerate-and-compile searches, is most of them.

Note also that the oracle is *already* called outside training: the design loop evaluates
candidates and sinks gradients into the candidate itself. "Absent at inference" is a claim
about the operator's inference specifically, not about the system.

### Recommendation

**Restate the absence as a deployment mode rather than a property.** The oracle is absent at
inference **by default**, and available as an opt-in verification pass whenever the query's
crystal identity has a compiled kernel. The out-of-distribution limitation then holds where it
actually holds — **novel identities only** — and coverage metadata is the honest handle for
exactly that case, rather than for every case.

**One caveat must travel with this, or it becomes a false guarantee.** Small residuals mean
*consistent with the laws the oracle checks*, never *correct*. A state can satisfy every
checked law and still be the wrong answer. The verification pass is a **necessary-not-sufficient**
filter and must be documented as one.

**Cost of ratifying:** roughly 2× inference cost when enabled, and the oracle-file must ship
with the deployed operator. **Cost of rejecting:** none structurally — but the corpus should
then say *why* it declines a cheap check for its own worst weakness, because at present it
reads as an oversight rather than a decision.

---

## Still held from auditor 2 — not physics, still Javier's

These need a decision but not a physics judgment.

| Item | Scale | The condition on it |
|---|---|---|
| The tolerance rename to English names | 17 names, 57 sites | Must land cell by cell with the disambiguation paragraph deleted **in the same commit** |
| The registry retag of retired markers | 508 cells | Lands **with** the checker extension that sweeps `data/`, or not at all — the retag alone leaves the same hole open for the next drift |
| The source-class controlled vocabulary | 22 values, 19 undeclared | Needs the controlled set decided before anything is rewritten |
| The four undeclared uncertainty encodings | 4 | A schema decision, not a data edit |

**Do not do either rename with `sed`.** A blind substitution during the last batch turned
*"normalized K-1 is a GAP"* into *"is a UNSEEDED"* — ungrammatical, because the token was
being used as a noun and the replacement is a marker. It was caught in diff review. A blind
symbol-to-word map launders meaning, and 57 and 508 sites are too many to catch by eye twice.

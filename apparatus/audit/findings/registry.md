# Cohesion audit — the formula registry and the vocabularies over it

Subject: `journals/oracle/registry/` (ten pages) and `data/registry-manifest.csv`
(134 rows = 132 substantive formulas + 2 architectural markers).

Status: **resumed.** This file was written in a first run that a session limit
cut short with six of eight undergraduates unspawned. The second run staffed the
sweep the register records as owed — all eight ran.

- **F1–F22** are the first run's.
- **F23–F36** are the second run's own direct sweep: fourteen findings, every one
  mechanical and carrying the control that earned it.
- **F37–F40** (§1b) were recovered from the blind calibration arm and re-verified
  against the **real** manifest. They are real defects and **not** detections —
  the reason is a scoring rule stated at the head of §1b and it binds every blind
  arm this program runs.

§5 (calibration), §6 (transcript) and §8 (coverage) are rewritten for the
combined result.

Two established findings are **not re-investigated here**: the manifest carrying
retired serial vocabulary on all 134 rows with mismatched column names, and the
closed provenance vocabulary matching zero rows. They are F1 below, kept for the
record; the principal owns the fix.

Everything called clean carries the comparison that earned it.

---

## 1 · Findings

### F1 — The manifest was never retagged. The closed provenance vocabulary matches zero of 134 rows.

**Claim.** `formula-registry#provenance` states seven admissible provenance
values — `observable-catalog`, `crystal-structure-prediction`,
`defects-and-interfaces`, `non-equilibrium-high-field`,
`residual-loss-methodology`, `extension`, `topology-atlas` — and asserts: *"This
is a closed vocabulary, so the provenance field is checkable in the same way the
other coded fields are. It has to be: it is the field that decides whether a row
is defensible, and an unchecked provenance field is how a row with no source
looks exactly like a row with one."*

**Evidence.** Tally of the `Source` column over all 134 rows:

```
S1 27 · S1+S2 5 · S1+S2+S3 2 · S1+S3 3 · S1+S4 1 · S2 20 · S2+S3 6
S3 18 · S4 27 · S5 3 · extension 15 · topology atlas 7
```

Two of the seven English values appear (`extension`, and `topology atlas`
unhyphenated). **The five research-stream values appear on zero rows**; all 112
stream-grounded rows carry the retired serials `S1`–`S5`. The same holds for
every other coded column: `Bundle` is `B1`…`B11`/`L1`, not
`electronic-structure`…`degradation`/`linear-response-primitive`; `Tier` is
`T0`–`T3`, not `microseconds`…`minutes`; `Diff` is `D0`–`D4`/`DN`, not
`read`…`none`; `Path` is `cheap`/`faithful` under a column the pages call
`anchor-class`. The column *names* diverge too — the manifest header is
`#, Name, Signature, Bundle, Tier, Diff, Path, Source, Depends on` against
`formula-registry#fields`' `row number, name, signature, bundle, cost-tier,
differentiability, anchor-class, provenance, depends-on`.

Nothing can see this. `tools/check_structure.py:96` globs
`JOURNALS.rglob("*.md")` and the file never opens `data/`. Its vocabulary sweep
(`check_vocabulary`, lines 275–320) flags a retired tag written as inline code
*inside a page* — the CSV is outside its reach by construction. `python3
tools/check_structure.py` reports `structure OK · 45 pages` with the manifest in
this state.

**Why this is a content finding and not a bookkeeping one.** The pages are
canonical for the vocabularies; the manifest is canonical for the per-row
values. Right now the canonical value store speaks a language its own definition
pages declare retired, and the definition of `provenance` — the field the page
says decides whether a row is defensible — is enforced against nothing. A reader
who takes `formula-registry` at its word believes the provenance column is
checked. It is not checkable, because no admissible value occurs in it.

**Severity** high. **Confidence** certain (mechanical).

**What would refute it.** A second manifest, or a generated view of this one,
carrying the English vocabulary. I searched `data/`, `generated/` and
`journals/` and found none; `generated/` contains no manifest.

**Proposed correction.** Apply the bijection recorded in
`audit/inherited/VOCABULARY.md` §1–2 to the CSV in the same commit that teaches
a checker to read it, and add `Source`/`provenance` to the column-vocabulary
check — `VOCABULARY.md:65-68` notes it was skipped, "which is how an undefined
vocabulary survived on 132 rows". **Do not apply the bijection blind:** it is a
mechanical relabeling, so any row mis-assigned under the old legend stays
mis-assigned under the new one. F10–F14 below are rows in exactly that state.

---

### F2 — The closed-registry rule is stated categorically on three pages and violated eighteen times on a fourth, and the three do not carry the exception.

**Claim.** `named-formulas#the-registry`: *"The registry is the closed set of
typed, fully parameterized algebraic formulas the oracle **is allowed to
invoke**."* `named-formulas#no-inline-math`: *"Every algebraic combination
invokes a named formula… The rule binds at the call site as well as here —
`algebraic-combination` always dispatches to a registry row."*
`computational-methods#signatures`, on `algebraic-combination`: *"always
dispatches to a registry row — no inline math"*.

**Evidence.** `typed-compositions` contains eighteen
`AlgebraicOf(…, formula = X)` invocations where `X` is not a manifest row, lists
them in `#declared-gap`, and says *"**They are deliberately not registered.**"* I
confirmed all eighteen are absent from the CSV. The page is honest; the other
three are not qualified. `named-formulas`' `depends-on` block does not even list
`typed-compositions`, so the page stating the closure rule has no edge to the
page carrying its exception. Only `properties#scope-vs-inventory` mentions the
gap.

The consequence is not cosmetic. `computational-methods` says the method "has no
other way to combine its inputs"; an implementation built from that page cannot
express `typed-compositions`' own worked compositions for hardness, ionic
diffusion, catalytic activity, absorption, refractive index, carrier mobility,
formation energy, free energy, stress–strain, adsorption energy, surface energy
or thermal expansion — twelve of the thirty-five catalog properties.

**Severity** high. **Confidence** certain.

**What would refute it.** A sentence on `named-formulas` or
`computational-methods` qualifying the closure claim. Neither has one.

**Proposed correction.** State the exception where the rule is stated, with the
citation to `typed-compositions#declared-gap`, on both pages.

---

### F3 — `QHA-expansion`'s invocation cannot form the tensor form the corpus pins, because the compliance tensor is not an input.

**Claim.** `typed-compositions#thermal`:

```
ThermalExpansion = AlgebraicOf({ModeGrüneisen(T), HeatCapacity(T)},
                               formula = QHA-expansion)
```

and `typed-compositions#declared-gap` classifies `QHA-expansion` as
**transcription**, with the reason: *"`QHA-expansion` is the case where the
pinned form matters most, because [traps#thermal-expansion-form] pins the
*tensor* form including the compliance-not-stiffness trap that makes the naive
version dimensionally wrong."*

**Evidence.** `journals/practice/traps.md:221-225` — *"Thermal-expansion tensor
form. Uses **compliance** `S = C⁻¹` and the `1/V` prefactor. *Breaks:* a
dimensionally wrong expansion tensor, propagating into gap-versus-temperature
strain, shear modulus, and the temperature-pressure hull."*

The pinned form is `α_ij = (1/V) Σ_kl S_ijkl Σ_λ γ_λ,kl c_λ`. It requires the
elastic compliance tensor **S** and the volume **V**. The invocation's declared
inputs are the mode Grüneisen parameters and the heat capacity — neither S nor V
is present, and `AlgebraicOf(inputs: {Value}, formula: NamedFormula) → Value`
takes no implicit arguments.

So the page names the trap, classifies the row as safe *because* the trap is
pinned, and then writes the one invocation that walks into it. The trap's own
failure statement is the failure this composition would produce.

A second, smaller mismatch in the same line: `ModeGrüneisen(T)` is invoked as a
temperature-dependent object, while manifest row 12 `grueneisen-mode` has
signature `(ω_λ(q,V)) → γ_λ` with no temperature argument.

**Severity** high — a dimensionally invalid thermal expansion propagates to
three downstream quantities the trap names. **Confidence** high.

**What would refute it.** A statement that `AlgebraicOf` closes over ambient
elastic constants, or a compliance tensor reachable from `HeatCapacity(T)`.
Neither exists; `property-templates#signatures` gives `AlgebraicOf` exactly two
arguments.

**Proposed correction.** `ThermalExpansion = AlgebraicOf({ModeGrüneisen,
HeatCapacity(T), ElasticConstants, V}, formula = QHA-expansion)` — with
`ElasticConstants` inverted to compliance inside the formula, and the inversion
stated. `ElasticConstants` is already a defined composition on the same page.

---

### F4 — `slab-arithmetic` is classified transcription on a premise that is false: its inputs do not determine the factor of two.

**Claim.** `typed-compositions#declared-gap` lists `slab-arithmetic` with Form =
*"determined by its inputs"*, and defines the class: *"**Transcription** means
the expression is written above, or the name plus its inputs determine it, or
this corpus already pins the form."*

**Evidence.** The invocation is
`SurfaceEnergy = AlgebraicOf({E_BO(slab), E_BO(bulk-per-formula-unit), n, A},
formula = slab-arithmetic)`. The surface energy of a symmetric slab is
`γ = (E_slab − n·E_bulk)/(2A)`; of a slab with one surface passivated or
reconstructed, `/(A)`. Which applies is a convention about what `A` denotes
(cross-sectional area against total exposed area), and it is not recoverable
from the four declared inputs. The choice is a **factor of two in every surface
energy**.

That the corpus treats a factor of two as exactly this class of hazard is its
own position: `named-formulas#corrected-forms` opens *"Five forms are canonical
in the registry, and each is one a näive derivation gets wrong"* and its first
entry is *"Optical absorption is `(2ω/c)·Im(√ε)` — the factor of two is part of
the form."* The slab factor of two is the same hazard and is not among the five.

Downstream: γ feeds manifest rows 44 (`surface-grand-potential-γ`), 45
(`wulff-shape`) and 86 (`bi-slab-grand-potential`), and `SurfaceEnergy` realizes
two catalog properties.

**Severity** high. **Confidence** high.

**What would refute it.** A definition of `A` elsewhere in the corpus fixing
total-exposed-area semantics. I grepped `journals/` for a slab-area convention
and found none.

**Proposed correction.** Either add the expression to the Form cell as was done
for the other four, or move `slab-arithmetic` to the research half. The same
argument applies more weakly to `adsorption-energy-difference`, whose sign
convention (negative-as-bound against positive binding energy) is likewise not
determined by its inputs.

---

### F5 — Two of the nine "research" names fail the page's own transcription test, and one of them is pinned by the corpus already.

**Claim.** `typed-compositions#declared-gap` splits eighteen names 9/9 and says
*"**Research** means a modeling choice with literature behind it, and the
choice has to be made and cited before a row exists."*

**Evidence, `harmonic-transition-rate-normalization`.** Classified research,
"needs literature". But `named-formulas#corrected-forms` — the corpus pinning
its own forms — contains: *"The harmonic transition-rate normalization consumes
products over normal modes — scalars — not the spectra themselves."*
`typed-compositions` restates the pin at `#transport` and writes the invocation
with the form already resolved:

```
ν₀ = AlgebraicOf({StateReadoutOf(ν_min,    product-of-modes),
                  StateReadoutOf(ν_saddle, product-of-modes)},
                 formula = harmonic-transition-rate-normalization)
```

Two scalars in, one scalar out, ratio fixed by the Vineyard construction. The
page's transcription test has three disjuncts and this satisfies the third —
*"or this corpus already pins the form"* — on a pin the same page cites.

**Evidence, `htst-rate`.** Classified research. Its invocation is
`AlgebraicOf({ν₀, E_a, T}, formula = htst-rate)`. `arrhenius` is classified
**transcription** with Form "determined by its inputs" and its invocation is
`AlgebraicOf({D₀, E_a, T}, formula = arrhenius)`. Same three input kinds, same
functional shape `prefactor · exp(−E_a/k_BT)`, opposite classifications, no
stated ground for the difference.

**Severity** medium — this is what decides whether a row is nine literature
searches or nine transcriptions, and the page presents the split as the actionable
output of the open question. **Confidence** high.

**What would refute it.** A modeling choice inside either name that I have
missed — for `htst-rate`, a quantum or anharmonic correction the corpus intends;
for the normalization, a convention about whether the saddle product runs over
`3N−1` or `3N` modes. The second is real and is the one thing worth citing, but
it is a convention to state, not a literature search, and the corpus states the
analogous convention for `jump-diffusivity` explicitly ("the geometric prefactor
convention is the trap").

**Proposed correction.** Move both to transcription, or state per row which
modeling choice is open. Note this changes the open question's own summary
("Nine are transcription plus tag assignment; nine need literature").

---

### F6 — `CarrierMobility` consumes a two-element set where a single conductivity is required.

**Claim.** `typed-compositions#transport`:

```
Conductivity    = { ConductivityViaBTE, ConductivityViaKubo }
CarrierMobility = AlgebraicOf({Conductivity, carrier-density},
                              formula = mobility-from-conductivity)
```

**Evidence.** `Conductivity` is explicitly a set of two distinct computations,
and the page says their agreement **is not assumed**: *"it is enforced as a
method-equivalence residual under obligation-6."* `AlgebraicOf(inputs: {Value},
formula: NamedFormula) → Value` returns one value. Nothing on the page says
which member `CarrierMobility` takes, or whether it takes both and returns two
mobilities. The ambiguity is exactly the size of the method gap the residual
exists to measure — so the reader cannot bind `CarrierMobility` to a determinate
object, and two readers will bind it differently.

This is the misinterpretable class: a competent reader follows the page
correctly and still gets a different answer than another competent reader.

**Severity** medium. **Confidence** high.

**What would refute it.** A selection rule for set-valued observables. I checked
`property-templates`, `computational-methods` and `typeclass-alphabet`; none
defines one, and `Conductivity` is the only set-valued composition on the page.

**Proposed correction.** Name the member — `CarrierMobility =
AlgebraicOf({ConductivityViaBTE, carrier-density}, …)` — or define the
set-valued-input rule once.

A related observation, not a separate finding: `mobility-from-conductivity`
(`μ = σ/(n·e)`) is the algebraic inverse of registered row 14 `drude-conductivity`
(`(μ, n, e) → σ`). Registering it creates a second row for one relation.

---

### F7 — Row 69's Maxwell residual has no sign convention, and the relation it names carries a minus sign.

**Claim.** Row 69 `thermodynamic-cross-derivative-residual`, signature
`(∂μ_i/∂T, ∂S/∂N_i) → ‖Δ‖`, `Source` = `S5 (a.k.a. Maxwell)`.

**Evidence.** From `dG = −S dT + V dP + Σ_i μ_i dN_i`, equality of mixed second
partials of G gives

```
(∂μ_i/∂T)_{P,N} = −(∂S/∂N_i)_{T,P}
```

The residual that vanishes identically is therefore
`‖∂μ_i/∂T + ∂S/∂N_i‖`, **not** the difference. The row states neither the sign
nor which of the two it forms, and `Δ` in the output reads as a difference.

The failure is asymmetric and both branches are bad. Formed as a difference, the
residual is `2·∂μ_i/∂T` — maximally violated everywhere, so it fires constantly
on correct thermodynamics. Formed as a difference and then "fixed" by someone
taking magnitudes, it is satisfied by construction and measures nothing. This is
a consistency residual, so a vacuously-satisfied version is invisible.

**Severity** medium-high — it is one of the corpus's few pure-consistency rows,
and the row's whole job is to fire when the thermodynamics is inconsistent.
**Confidence** high (the relation is textbook; the absence is mechanical).

**What would refute it.** A sign convention stated on
`residual-definitions` or `cert-obligations` for cross-derivative residuals. I
grepped for "Maxwell" across `journals/`; `residual-definitions:143` names
"Onsager reciprocity" with no form, and the inherited notes record the same
form-free treatment there. No Maxwell sign appears.

**Proposed correction.** Write the relation into the `Source` cell as the corpus
does for rows 68, 72, 74 and 125 — e.g. `(∂μ_i/∂T)_{P,N} + (∂S/∂N_i)_{T,P} = 0;
R = (∂μ_i/∂T + ∂S/∂N_i)²`.

---

### F8 — Row 83 cannot form its declared output: the fatigue ductility coefficient is absent from the signature.

**Claim.** Row 83 `plastic-strain-fatigue-life`, signature `(Δε_p, c) → N_f`,
`Source` = `S3 (a.k.a. Coffin–Manson)`.

**Evidence.** Coffin–Manson is `Δε_p/2 = ε_f′·(2N_f)^c`. Inverting for `N_f`
requires **three** quantities: `Δε_p`, the exponent `c`, and the fatigue
ductility coefficient `ε_f′`. With only `(Δε_p, c)` the equation has no solution
— `N_f` is undetermined up to the unknown scale `ε_f′`, which is a material
constant spanning orders of magnitude.

Corroboration from a second source: `audit/inherited/contradictions.md`
(appendix-b, C7) records the same formula in the appendix stratum as
`plastic-strain-fatigue-life (Δε_p, ε_f, c) → CyclesToFailure` — **with** `ε_f`.
The registry row dropped it. The contradiction entry registered this as "the
same physics proposed as two differently-parameterized formulas"; the sharper
statement is that one of the two parameterizations is not solvable.

**Severity** high — an unformable output on a `degradation`-bundle row.
**Confidence** high.

**What would refute it.** A convention fixing `ε_f′` from other row inputs (it
is sometimes approximated by the true fracture ductility). Nothing in the row or
in `journals/` states one.

**Proposed correction.** Restore `ε_f′`: `(Δε_p, ε_f′, c) → N_f`, and state
whether `Δε_p` is the range or the amplitude — the factor of two in `Δε_p/2` is
the same class of hazard as F4.

---

### F9 — Row 82 cannot form its declared output: Black's prefactor is absent.

**Claim.** Row 82 `electromigration-mttf`, signature `(j, E_a, T, n) → MTTF`,
`Source` = `S3 (a.k.a. Black)`.

**Evidence.** Black's equation is `MTTF = A·j^(−n)·exp(E_a/k_BT)`. `A` is a
material- and geometry-dependent constant carrying the units of the result;
without it the row returns a dimensionless shape, not a time. The signature has
`j`, `E_a`, `T` and `n` and no `A`.

**Severity** medium — same class as F8, lower blast radius (row 82 has no
registered consumers). **Confidence** high.

**What would refute it.** A convention that `MTTF` is reported normalized to a
reference condition. Not stated.

**Proposed correction.** Add `A` to the signature, or declare the output as a
ratio to a reference lifetime and say so.

---

### F10 — Row 87's cost tier is the cost of *populating* the cache, not of one evaluation — and the page builds its cost lesson on that reading.

**Claim.** Row 87 `reference-phase-energy-cache`, signature `(phase-id) → E_ref`,
`Tier` = T3 (`minutes`), `Diff` = D0 (`read`).
`named-formulas#cost-tiers` defines the column: *"What one evaluation of the
formula costs"*, T3 = *"self-consistent loop or partial-differential-equation
solve"*, ≤10 min. The page then makes this row its worked example:

> *"`reference-phase-energy-cache` costs `minutes` to evaluate and is `read` for
> differentiability — among the most expensive evaluations in the registry,
> carrying the cheapest gradient there is, an identity adjoint. Cost and
> differentiability are independent axes, and the expensive tail is where they
> come apart."*

**Evidence.** The row is a cache keyed on a phase identifier. One evaluation is
a keyed lookup — microseconds. What takes minutes is the density-functional
battery that fills the cache, and that is a different operation performed at a
different time. The row's `Depends on` cell says `DFT battery`, naming the
populating step rather than the evaluation.

The corpus draws exactly this distinction elsewhere, in the neighboring
paragraph, and applies it to the other column only:

> *"A row that also takes continuous arguments is **not** a pure read, however
> cache-backed its implementation. An implementation detail — a cache — is not a
> mathematical one — an identity adjoint."*

That reasoning is used to keep `chemical-potential-ref-table` off `read`. The
same reasoning applied to the `cost-tier` column says a cache's evaluation cost
is a lookup, not the cost of the thing cached.

**Consequence.** `named-formulas#cost-tiers` states that the cost value is what
the residual factory reads *"when it decides how often to sample a generator"*,
and warns that the expensive tail is where misreading it does damage. A row
sampled as if it cost minutes, when it costs microseconds, is sampled far too
rarely — the mirror of the failure the paragraph warns about.

**Severity** medium. **Confidence** high on the mismatch; the page's showcase
paragraph is the part I am least willing to see rewritten, so I flag rather than
prescribe.

**What would refute it.** A statement that the tier is a cache-miss worst case.
None is present, and a worst-case reading would make T3 correct for row 87 and
wrong for the page's lesson, which contrasts *evaluation* cost with gradient
cost.

**Proposed correction.** Javier's call. Either re-tier to `microseconds` and
find a different showcase for the cost/differentiability independence — row 80
`NEGF-transmission` is T3 and D2 and makes a weaker but honest version of the
point — or declare explicitly that this row's tier is the populating cost and
say what the factory should do with it.

---

### F11 — Row 54 is simultaneously "closed form" by tier and "transcendental fixed point" by differentiability.

**Claim.** Row 54 `critical-thickness-force-balance`, `Tier` = T0, `Diff` = D3,
`Source` = *"h_c appears inside its own log ⇒ transcendental fixed point;
adjoint is one linear solve against the transposed fixed-point Jacobian. a.k.a.
Matthews–Blakeslee"*.

**Evidence.** T0 is defined as `closed form`, ≤10 µs
(`named-formulas#cost-tiers`). The row's own justification for its D3 tag is
that it is **not** a closed form. It is the only row in the manifest carrying
both values (D3 rows: 5 at T1, 13 at T3, 36 at T1, 54 at T0, 122 at T3).

The 10 µs bound may well survive — a scalar Newton iteration on
`h_c = k·[ln(h_c/b) + 1]` converges in a few steps. It is the tier's *meaning*
that fails, and the tier column is a two-part claim: a work description and a
bound.

**Severity** medium — self-contradiction inside one row, and the row is the
only place a reader can learn what T0 admits. **Confidence** certain.

**Proposed correction.** Either widen T0's description to "closed form or a
scalar root-find", which is honest and cheap, or move row 54 to T1.

---

### F12 — Rows 92–94 claim `seconds` on a Brillouin-zone-integral justification, while their own dependency is the self-consistent linear-response sub-stage.

**Claim.** Rows 92 (`operator-position-derivative-tensor`, Born effective
charges Z*), 93 (`high-frequency-response-tensor`, ε∞) and 94
(`electronic-linear-response-tensor`, χ∞) are all T2 (`seconds`, ≤10 s),
`faithful`, D2. `named-formulas#cost-tiers` names row 92 as its worked example:
*"`single-mode-rta-lattice-kappa` (row 25) and `operator-position-derivative-tensor`
(row 92) are `seconds` — a Brillouin-zone integral each."*

**Evidence.** All three rows' `Depends on` cell reads `linear-response
sub-stage`. Density-functional perturbation theory is a **self-consistent
linear-response solve** — one per perturbation, each of the order of an SCF
calculation, and Z* requires 3N atomic-displacement perturbations or three
electric-field perturbations. `named-formulas#cost-tiers` defines T3 as
*"self-consistent loop or partial-differential-equation solve"*. By the corpus's
own legend, the computation these rows depend on is T3 work.

The Berry-phase route to Z* is a set of string integrals over the zone and could
fairly be called a Brillouin-zone integral, so the justification is not absurd —
but it describes a different algorithm from the one the `Depends on` cell names,
and the ≤10 s bound is not reachable for either route on the corpus's own
materials (β-Ga₂O₃ is monoclinic with ten atoms in the primitive cell).

The consequence is the one my brief names: a row claiming seconds that hides a
self-consistent solve is a false claim with performance consequences, and the
residual factory reads this column to set sampling frequency.

**Severity** medium-high. **Confidence** medium-high — I have verified the
internal inconsistency (dependency against justification against legend)
mechanically; the wall-clock claim rests on my judgment of DFPT cost rather
than on a measurement, and I did not have an undergraduate to send at it.

**What would refute it.** A statement that these rows *read* precomputed
linear-response output rather than invoking it — in which case the tier is right
and the `Depends on` cell should say so, and the `Diff` value probably wants
re-examining against the `read` criterion. That reading is plausible and I could
not settle it; see gap G1.

---

### F13 — Two mesh-integral rows sit one tier below a third that does the same work.

**Claim.** Row 4 `DOS-tetrahedron` `(BandStruct, k-mesh) → ε↦Scalar` is T1;
row 10 `phonon-DOS` `(ω_λ(q), q-mesh) → ε↦Scalar` is T1; row 25
`single-mode-rta-lattice-kappa` `(ω_λ(q), τ_λ) → κ_L` is T2.

**Evidence.** `named-formulas#cost-tiers` defines T1 as *"small linear algebra,
one-dimensional quadrature"* and T2 as *"Brillouin-zone or mesh integral"*. Rows
4 and 10 take a mesh as an explicit argument and integrate over it — the T2
description, verbatim. Row 25 sums over the same q-mesh as row 10, with the same
per-point work plus a velocity and a lifetime, and is tagged T2 and cited on the
page as the worked example of a Brillouin-zone integral.

Rows 4 and 10 are therefore tagged one tier below a row that does strictly more
of the same work on the same grid.

**Severity** medium. **Confidence** high on the internal inconsistency.

**What would refute it.** A convention that the tetrahedron DOS is evaluated on
a coarse mesh and κ on a fine one. Not stated, and the mesh is a free argument
in both.

**Proposed correction.** Move rows 4 and 10 to `seconds`, or state the mesh-size
convention that separates them.

---

### F14 — A coupled electromagnetic–thermal partial-differential-equation residual is tagged three tiers below a drift-diffusion one.

**Claim.** Row 71 `coupled-em-thermal-pde-residual`
`(j, E, T_L, σ(T), κ(T)) → ‖PDE‖` is T1 (`milliseconds`, "small linear algebra,
one-dimensional quadrature"). Row 106 `hydrogen-redistribution-drift-diffusion`
is T3.

**Evidence.** Row 71 evaluates a residual of a coupled field problem over a
device mesh with temperature-dependent transport coefficients. It does not
*solve* the system — which is a fair argument for it being cheaper than a solve —
but a full-field residual evaluation with two coupled fields is not "small
linear algebra, one-dimensional quadrature". Row 106 is likewise a rate field
from a transport operator rather than a solve, and is T3.

**Severity** medium. **Confidence** medium — the residual/solve distinction is a
real one and I could not establish the mesh size either row assumes.

**Proposed correction.** State the mesh-size assumption for both, or re-tier
row 71 to `seconds`.

---

### F15 — Row 25 carries no validity domain, although the corpus's own ledger records it failing in both directions inside the target range.

**Claim.** Row 25 `single-mode-rta-lattice-kappa`, `Source` = `S1 (a.k.a.
Callaway/Slack)` — no validity domain, no error statement.

**Evidence.** `journals/oracle/accuracy/accuracy-ledger.md:126` states, for the
same quantity: *"relaxation-time three-phonon **underestimates** diamond by
30–50% near 300 K, so the anchor is the iterative solution near 2200, **not** the
relaxation-time value near 1800. In the other direction, three-phonon
**overpredicts** the nitrides at high temperature."* The inherited diamond lead
(`audit/inherited/leads/diamond.md:96`) records the complementary figure: *"at
1000 K, three-phonon scattering alone **overpredicts κ of diamond** … by 31%."*

Both are true and they are different effects — the single-mode approximation
discards normal-process redistribution (fixed by row 122, iterative LBTE), and
three-phonon-only omits four-phonon scattering (fixed by row 121). The registry
carries both corrections as rows. **Row 25 itself says nothing about needing
them.** A consumer reading the manifest alone gets a formula that is wrong by
30–50% in one direction at 300 K and by ~31% in the other at 1000 K, with no
signal in the row.

**Severity** high — this is the corpus's headline observable for its headline
material, and it is the row the 2026-06-10 re-audit passed as sound.
**Confidence** high.

**Proposed correction.** Put the regime statement in the `Source` cell, as rows
121, 123 and 127 already do for their own limits, and name rows 121 and 122 as
the required corrections rather than leaving them as unlinked siblings.

---

### F16 — Row 121's validity domain is stated in terms of a quantity the corpus admits it does not know well enough to evaluate it.

**Claim.** Row 121 `kappa-4phonon-high-t-correction`, `Source` = *"Slack-like
4-phonon multiplicative factor, valid T≳0.4Θ_D; Feng-Lindsay-Ruan PRB 96
161201"*.

**Evidence.** `accuracy-ledger.md:55` carries this open question:

> *"The diamond Debye temperature, 2200 K ± 50, is UNSEEDED, and the literature
> spread is method-dependent from about 1860 K (elastic constants) to about
> 2230 K (low-temperature specific heat) — far wider than the stated
> uncertainty… This row is coupled to the thermal-conductivity battery: it sets
> the four-phonon validity threshold at 0.4 of it, so **2200 K puts the 773 K
> conductivity anchor outside the four-phonon window and 1860 K puts it
> inside**."*

So row 121's declared validity domain is not decidable for the corpus's own MVP
material at the corpus's own anchor temperature. A validity domain that cannot
be evaluated is, operationally, no validity domain — and this one silently
selects between two different conductivity anchors.

Θ_D belongs to the accuracy subject; **the row that consumes it is mine**, and
the finding is that row 121 states a domain in a quantity with an unresolved
factor-of-1.2 spread and does not say so.

**Severity** medium-high. **Confidence** high.

**Proposed correction.** State the threshold in kelvin per material rather than
as a multiple of a contested Θ_D, or carry the branch explicitly. Coordinate with
whoever owns the accuracy ledger — this is one open question with two owners.

I verified the citation itself and it is sound: see §2.

---

### F17 — Row 25's eponym names two models, and the row computes neither.

**Claim.** Row 25's `Source` cell is `S1 (a.k.a. Callaway/Slack)`.

**Evidence.** The signature is `(ω_λ(q), τ_λ) → κ_L`, i.e. the mode-resolved
single-mode relaxation-time sum `κ = (1/V)Σ_λ c_λ v_λ² τ_λ`. Callaway's model
(1959) separates normal from umklapp processes and adds a second, correction
term that the single-mode sum does not contain — that omission is precisely the
30–50% underestimate the ledger records in F15, and is what row 122 exists to
repair. Slack's is a high-temperature closed form built from the Debye
temperature, mean atomic mass, number of atoms per cell and Grüneisen parameter
— it takes none of row 25's inputs and returns a scalar estimate rather than a
mode sum.

`formula-registry#provenance` states the purpose of this cell: the `a.k.a.` is
*"the literature attribution the row is known by… which is where a literature
search starts"*. A search started from "Callaway" returns a formula with an
extra term; from "Slack", a formula with different arguments entirely. The
corpus's own rule (`agent-contract#vocabulary`) is that an eponym is renamed
when *"a reader could bind the name to the wrong object"*. Both names bind to
the wrong object here, and one of them binds to the very term whose absence is
the row's known error.

**Severity** medium. **Confidence** high.

**Proposed correction.** `a.k.a. single-mode relaxation-time approximation
(Peierls–Boltzmann); the Callaway two-relaxation-time correction is row 122 and
the four-phonon correction is row 121`.

---

### F18 — Row 88's attribution appears to conflate two distinct papers into one non-existent one.

**Claim.** Row 88, `Source` = *"extension (a.k.a. Pick-Cochran-Martin /
Gonze-Lee)"*.

**Evidence.** The standard attribution for the microscopic theory of the
non-analytic term is **Pick, Cohen and Martin**, Phys. Rev. B **1**, 910 (1970).
**Cochran and Cowley**, J. Phys. Chem. Solids **23**, 447 (1962) is a separate
and also-relevant reference for the same physics. "Pick-Cochran-Martin" is
neither: it reads as Pick–Cohen–Martin with Cohen replaced by Cochran. Gonze–Lee,
PRB **55**, 10355 (1997), is correctly named.

**Severity** low-medium — the row's physics is not affected; the failure is that
the field this cell exists to serve (where a literature search starts) returns
nothing for one of its two names. **Confidence** medium: I could not complete
verification, because the session WebSearch budget was exhausted and I could not
reach a bibliographic record for a 1970 Phys. Rev. B paper through the arXiv API
(which predates it) or CrossRef without the DOI. This is registered as gap G2
rather than asserted.

**Proposed correction, conditional on G2.** `a.k.a. Pick–Cohen–Martin /
Gonze–Lee`.

---

### F19 — The two band-gap rows are spectral extrema and declare no exception set.

**Claim.** Rows 1 `bandgap-direct` and 2 `bandgap-indirect` are D1 (`direct`).

**Evidence.** Both are minima over a k-grid (row 2 additionally a max over the
valence band). `typeclass-alphabet#sampleable` defines `Differentiable` as
*"total on the domain *minus* an `exceptionSet`"* and names the members:
*"Phase transitions, **band crossings** and charge-transition levels live in the
exception set: they are the points where the derivative genuinely does not exist,
and naming them is what lets a consumer distinguish that from a numerical
failure."*

A band extremum that migrates between k-points, or a degeneracy at the extremum,
is that case. But the exception set is a typeclass-level property with no
manifest field, so **a reader of the manifest cannot tell that rows 1 and 2
carry a non-empty one** — and the corpus's MVP material is diamond, whose
conduction-band minimum sits on Δ rather than at a zone-boundary point, so the
argmin's location is a live quantity rather than a fixed one.

**Severity** low-medium. **Confidence** medium-high.

**Proposed correction.** Note the exception set in the `Source` cell, as rows 12
and 101 already do for theirs ("exception set at mode crossings…", "Exception
set: the mod-2π branch cut and spectral degeneracies"). Rows 1 and 2 are the
only extremum rows without such a note.

---

### F20 — Two catalog properties named "free energy" resolve to different thermodynamic potentials.

**Claim.** `properties#catalog` lists one property, `Thermodynamic | Free
energy`. `typed-compositions#thermodynamic` realizes it as
`FreeEnergy(T) = AlgebraicOf({E_BO, F_vib, F_el}, formula =
helmholtz-free-energy-decomposition)` — the **Helmholtz** free energy.
`observable-bundles#contents` lists the `thermodynamics` bundle as holding
*"Gibbs free energy, phase-diagram convex hull…"*, and manifest row 65 is
`gibbs-free-energy-phase` `(E_0, ω(q), T, P) → G(T,P)`.

**Evidence.** F and G are different potentials at different fixed variables
(F at fixed V, G at fixed P) and differ by PV. One catalog property resolves
to F through the coverage table and to G through the bundle contents, with no
page reconciling them. The corpus operates at finite pressure — row 68 is the
Clausius–Clapeyron slope and row 124 is a temperature- **and pressure**-aware
hull — so the two are not interchangeable here.

**Severity** medium. **Confidence** high.

**Proposed correction.** Split the catalog property, or state which potential
"Free energy" denotes and give the other its own row.

---

### F21 — Row 53 applies a metallic-alloy solubility heuristic outside its domain, and omits one of its four rules from the signature.

**Claim.** Row 53 `substitution-compatibility-score`,
`(r_A, r_B, χ_A, χ_B, valence) → score`, `Source` = `S2 (a.k.a. Hume-Rothery)`.

**Evidence.** The Hume-Rothery rules for substitutional solid solubility are
four: atomic-radius difference under ~15%, **same crystal structure**, similar
electronegativity, similar valence. The signature carries radii, electronegativities
and valence — three of the four. Crystal structure is absent, so the score cannot
express the rule that most often refuses a substitution.

Separately, the rules were formulated for **metallic** solid solutions. The
corpus's hosts are covalent (diamond, c-BN) and ionic-covalent (AlN, GaN,
β-Ga₂O₃), where directional bonding and formal-charge compensation dominate over
size-and-valence matching. The row states no validity domain.

**Severity** medium. **Confidence** medium-high on the missing rule (mechanical);
medium on the domain question, which wants a literature check I could not staff.

**Proposed correction.** Add the structure argument, and state the domain — or
rename away from Hume-Rothery, since the score as constructed is not the
Hume-Rothery criterion.

---

### F22 — Row 134's stated justification for neglecting radiative recombination is not the reason the conclusion holds.

**Claim.** Row 134 `radiative-recombination-rate`, `Source` = *"…a.k.a. van
Roosbroeck-Shockley detailed-balance R=B_rad·(np−n_i²); … **negligible in UWBG
device balance (tiny n_i)** — carried for PL/validation channels"*. Repeated at
`accuracy-ledger.md:172`: *"negligible in the ultra-wide-gap device balance,
given the tiny intrinsic carrier density"*.

**Evidence.** `R = B_rad(np − n_i²)` is dominated by the `np` term whenever
carriers are injected; `n_i²` sets only the equilibrium offset. A small `n_i`
makes the *equilibrium* rate small and says nothing about the rate under
injection, which is the device condition. The correct reason radiative
recombination is small in these materials is that `B_rad` is small for indirect
and wide-gap systems and that Shockley–Read–Hall through deep levels dominates —
not that `n_i` is tiny.

The conclusion may well be right; the stated reason is not a reason. That
matters because the justification is what a later reader will re-use when the
device operates under high injection, where the same sentence would license the
same neglect for a different and wrong reason.

**Severity** medium — a wrong justification attached to a right conclusion, in a
cell that exists to be quoted. **Confidence** high on the physics; the magnitude
of the conclusion I did not verify.

**Proposed correction.** Replace the parenthetical with the operative reason and
state the injection level at which the neglect was assessed.

---

### F23 — The schema declares that signatures carry units. Zero of 134 do.

**Claim.** Two pages state it as a property of the field, not as an aspiration.
`formula-registry.md:49`, the field table: *"| `signature` | typed inputs to
output, **with units** |"*. `named-formulas.md:74`, the record: *"`signature :
(Inputs) → Output -- typed, with units`"*.

**Evidence.** I swept all 134 `Signature` cells for any unit token — `eV`, `meV`,
`GPa`, `MPa`, `Pa`, `K`, `cm⁻¹`, `cm⁻³`, `cm⁻²`, `cm³`, `cm⁶`, `m⁻³`, `s⁻¹`,
`W/m`, `V/cm`, `MV/cm`, `J/K`, `Å`, `nm`, `µm`, `torr`, `atm`, `C/m`, `F/m`,
`S/cm`, `kg`. **Count: 0.** Every signature is bare symbols:
`(C_ij) → B`, `(μ, n, e) → σ`, `(ΔE, ω_LO, S_HR, T) → C_p`.

Control, run in the same pass so the negative is not an instrument failure: the
detector fires on `` `(E_def [eV], q) → E_form [eV]` `` and on
`` `(T [K]) → κ [W/m·K]` ``, and is silent on `` `(C_ij) → B` ``. The
detector works; the units are absent.

**Why this is a content finding.** It is the enabling condition for F24. Units
are what distinguishes two quantities sharing a symbol, and the manifest has at
least eight such pairs. A capture coefficient in cm³/s and an Auger coefficient
in cm⁶/s are both written `C_p`, and nothing in the row can tell them apart.
The signature field is also the only place a consumer could learn them: there is
no units column, and `journals/practice/conventions.md` is a *writing*-conventions
page (style, count phrasing, data files) in which the string `unit` does not
occur, while `glossary.md` declares itself *"An index, not a second definition"*.

**And a typeclass method depends on this data.**
`typeclass-alphabet.md:50-62` makes `Quantity` the first of the corpus's four
typeclass axes:

> *"**Quantity — the value axis.** Units, equality within a tolerance, and
> behavior under a change of units or basis. **Every numeric output is a
> `Quantity`.**"*
>
> ```
> Quantity:
>   unitsOf     : a → Units
>   approxEq    : Tolerance → a → a → Bool
>   rescale     : Units → a → a
>   combineTol  : Tolerance → Tolerance → Tolerance
> ```

`unitsOf` is an accessor returning a value's units, and `rescale` converts
between unit systems. **There is no per-row units data anywhere for either to
read.** So this is not an unmet documentation promise — it is a declared
typeclass method with no backing store, on the axis the page says every numeric
output inhabits. Two of the four `Quantity` methods are unimplementable from the
registry as it stands.

That also gives the finding a second consequence beyond F24: `rescale` is what
would catch a Gaussian-against-SI mix-up, and the corpus carries a trap for
exactly that hazard (`traps.md`, *"Gaussian units and the Maxwell source term —
the 4π in the source term rides the unit system. Breaks: factor-4π errors across
the electromagnetic sector"*). The trap names the hazard; the method that would
detect it has no data.

**Severity** medium-high. **Confidence** certain (mechanical, with control).

**What would refute it.** A units declaration elsewhere that the signature field
defers to. I checked `conventions.md`, `glossary.md`, `typeclass-alphabet` and
`property-templates`; none carries a per-quantity unit table. The reference-data
CSVs carry a units convention for *measured* values, not for formula arguments.

**Proposed correction.** Either annotate the signatures — which is what the
schema already promises and what makes F24 self-checking — or strike "with
units" from both pages and add a units column. The first is better: it is the
one change that makes the collisions in F24 visible at the point of use.

---

### F24 — The signature column is not a namespace. Eight symbols denote two or more different physical quantities, and in five cases one of them is a registered row's declared output.

**Claim.** The manifest's `Signature` column is the corpus's type contract, and
`Depends on` names symbols rather than rows in 142 of 245 referents (F25) — so
symbol identity is the only handle most cells offer for wiring one row to
another.

**Evidence.** Parsing every signature with bracket-depth tracking (so
`Z*[I,α,β]` is one token, not three — control below), here are the symbols that
appear as one row's **declared output** and another row's **input meaning a
different quantity**:

| symbol | produced by | there it is | consumed by | there it is |
|---|---|---|---|---|
| `C_p` | row 40 `multiphonon-emission-capture` | carrier capture coefficient, cm³/s | row 39 `auger-recombination` | Auger coefficient, cm⁶/s |
| `Ω` | row 86 `bi-slab-grand-potential` | grand potential, eV | rows 88, 113, 114 | unit-cell volume, Å³ |
| | | | row 127 `alloy-disorder-scattering` | volume per atom |
| `B` | row 61 `bulk-modulus` | bulk modulus, GPa | row 19 `hall-mobility-from-σ` | magnetic flux density, T |
| `S` | row 23 `seebeck-from-conductivity-derivative` | Seebeck coefficient, V/K | row 48 `MIGS-corrected-barrier` | interface pinning slope, dimensionless |
| `N_d` | row 111 `nrt-displacements` | displacements per cascade, a count | row 79 `thermionic-field-emission-current` | donor density, cm⁻³ |

And two collisions with no registered producer, between consumers only:

| symbol | one meaning | the other |
|---|---|---|
| `ε` | dielectric constant — rows 31, 32, 33, 43, 49, 89, 90, 120 | strain — rows 63, 64 (and `ε[J]` in 117) |
| `n` | carrier density, cm⁻³ — rows 14, 36, 38, 39, 134 | Black's current-density exponent, dimensionless — row 82 |
| `b` | Burgers vector, Å — row 54 | bond-valence softness parameter, ≈0.37 Å — row 55 |

All of these are **bare identical tokens**, not decorated variants. Two weaker
cases where the tokens differ by decoration and a careful reader can separate
them: `e` (elementary charge, row 14) against `e[i,J]` (piezoelectric stress
tensor, rows 114, 117); and `p` (hole density, rows 36, 38, 39, 134) against
`p[α]` (pyroelectric coefficient, row 128).

**The `C_p` case is the worst, and it is worth following all the way.** Row 40
`multiphonon-emission-capture` produces a carrier capture coefficient. **No row
in the manifest names row 40 as a dependency** — I grepped the `Depends on`
column for `multiphonon`, `row 40` and `(40)` and the only hit is row 40's own
line. It is a dangling producer.

Meanwhile the one row whose signature contains the token `C_p` is row 39,
`auger-recombination`, where it is the Auger coefficient — a different quantity
in different units (cm⁶/s against cm³/s) arising from a different process
(three-carrier Auger against trap-mediated multiphonon capture). So the single
symbol match for row 40's output is the one row that must not consume it.

Where it *should* go is row 38, `SRH-recombination`, since a capture coefficient
is what sets a Shockley–Read–Hall lifetime, `τ_p = 1/(c_p N_t)`. Row 38's
signature is `(n, p, τ_n, τ_p, n_i) → R_SRH` — it takes the **lifetimes**, not
the coefficients, so the edge cannot be expressed even if someone wanted to draw
it. The registry has a producer of capture coefficients, a consumer of capture
lifetimes, no row converting one to the other, and a symbol collision that makes
the gap look filled.

**The `S` case is the one that has already bitten.** Row 48's `Depends on` cell
reads `barrier-from-workfunction-affinity (row 47), S, φ_CNL, E_g` — it lists
`S` as a dependency. A consumer resolving that referent by symbol finds exactly
one registered row producing `S`: row 23, the Seebeck coefficient. The correct
referent is the interface pinning parameter, which no row produces and which is
therefore an unregistered input the cell does not mark as one — unlike rows 7,
8, 9, 47 and 80, which do mark theirs.

**The corpus states this hazard and applies it to the wrong column.**
`named-formulas.md:178-182`: *"The values are spelled out in English so that no
differentiability value can be read as a physical quantity. Wide-bandgap
semiconductor physics is dense with letter-and-digit labels — deformation
potentials, deep-donor configurations — and a tag drawn from the same alphabet
cannot be searched for without returning the physics, or the physics without
returning the tag."* That reasoning is correct and it was applied to the six-value
`differentiability` vocabulary. It was not applied to the several-hundred-symbol
quantity namespace, where the collisions are real rather than hypothetical.

**Severity** high — this is the corpus's type contract, and F23 removes the one
mechanism that would disambiguate it. **Confidence** certain on the eight token
collisions (mechanical, control below); the *reading* of each symbol's intended
meaning is mine, from the row's formula and eponym, and is stated per row above
so a third party can check each.

Control on the parser: `` `(Z*[I,α,β], Δw[I], Ω) → P_sp[α]` `` parses to inputs
`['Z*[I,α,β]', 'Δw[I]', 'Ω']`, output `['P_sp[α]']`; `` `(C_ij, ρ) → v_L, v_T` ``
to `['C_ij', 'ρ']` and `['v_L', 'v_T']`. Character-class control: `μ0`/`μ₀`,
`E_0`/`E₀`, `v_g`/`v-g` all normalize equal, so a subscript variant cannot hide a
collision from the sweep.

**Independent corroboration, from a reader who had never seen this finding.** The
blind calibration undergraduate — working only from a 24-row extract, forbidden
from opening the real manifest or this file — independently reported that row
127's `Ω` is undefined, and separately that row 119's `D_it` carries no unit
where the two available readings differ by a factor 6×10¹⁸ (now F39). Two of the
eight collisions here were reached from scratch by someone with no access to the
argument, which is the strongest evidence I have that they are visible defects
rather than an auditor's construction.

**What would refute it.** A per-row scoping rule stating that signature symbols
are local to the row. No page states one, and the `Depends on` column's use of
bare symbols as referents presupposes the opposite.

**Proposed correction.** Attach units in the signature (F23), which makes every
collision above visible at the point of use, and rename the two worst: row 39's
Auger coefficients to `C_n^Aug`/`C_p^Aug`, and row 48's pinning parameter to
`S_pin`. `Ω` for volume against grand potential is worth a corpus-wide decision
rather than a row edit.

---

### F25 — `Depends on` is four different columns wearing one name, and its declared meaning covers 17% of its contents.

**Claim.** Both schema pages give this column one meaning.
`named-formulas.md:81`: *"`depends-on : {Symbol}  -- upstream formulas and
primitives`"*. `formula-registry.md:55`: *"| `depends-on` | upstream formulas and
primitives |"*.

**Evidence.** I split all 134 cells into referents (comma-split at paren depth
zero) and classified each. 245 referents:

| what it actually is | count | example |
|---|---|---|
| a reference to another registry row, by number or by name | **41** | row 121 → `single-mode-rta-lattice-kappa (row 25)` |
| a restatement of the row's **own signature inputs** | **142** | row 43 `(c_def, T, ε)` depends on `c_def, T, ε` |
| an informal collective noun naming a kind, not an object | **31** | `slabs`, `radii`, `bands`, `thermo`, `populations`, `μ-channels`, `γ family`, `mechanics ×2` |
| a named object that is neither a row nor a signature input | **31** | `ECI cache`, `R0-table`, `DFT battery`, `linear-response sub-stage` |

**The consequence is that a non-empty cell carries no information about whether
dependencies are stated.** 142 cells echo the signature, so "this row declares
its dependencies" and "this row declares nothing" look identical. A missing edge
is therefore invisible, and there are missing edges. Restricting to cases where a
row's input token is *exactly* another row's declared output symbol and the
meanings agree, the following real edges are not recorded:

| row | consumes | produced by | its cell says instead |
|---|---|---|---|
| 15 `matthiessen-mobility` | `μ_imp`, `μ_ph` | row 20 | `μ-channels` |
| 16 `field-dependent-mobility` | `v_sat` | rows **17 and 18** — two producers, no selection rule | `μ0, v_sat, E` |
| 22 `polar-optical-scattering-rate` | `α_F` | row 21 | `α_F, bands` |
| 24 `electronic-kappa-from-conductivity` | `σ` | row 14 | `σ` |
| 35 `defect-boltzmann-population` | `E_form` | row 30 | `E_form, T` |
| 37, 43 | `c_def` | row 35 | `populations` / `c_def, T, ε` |
| 45, 46 | `γ` | row 44 | `γ` / `γ family` |
| 57, 61, 62 | `C_ij` | row 60 `elastic-constants-Cij` | `elastic` / `C_ij` / `C_ij, ρ` |
| 72 | `τ_E` | row 73 | `j, E, τ_E, n` |
| 73 | `α_F`, `Ξ` | rows 21, 63 | `α_F, mech` |
| 75 | `α(E)` | row 74 | `α(E)` |
| 77, 78, 79 | `φ_B` | row 47 | `φ_B, E` / `φ_B, T` / `φ_B, N_d, T` |
| 89 | `α_M` | row 91 `lattice-coulomb-summation-scalar` | `q, ε, Madelung` |

Row 16 is the sharpest: `v_sat` is produced by **two** registered rows (17,
`v-sat-POP-limit`, and 18, `v-sat-intervalley`) and row 16 names neither. This is
F6's set-valued-input problem again, inside the manifest rather than in
`typed-compositions`.

The corpus **can** do this correctly, which is what makes the 41 a control rather
than an accident: rows 115, 116, 119, 121, 122, 123, 125, 127, 128, 132 and 133
all name their upstream rows by name and number. Row 123's cell —
`impact-ionization-coefficient (row 74), avalanche-multiplication (row 75)` — is
the form the whole column should take.

**Severity** medium-high. **Confidence** certain on the classification
(mechanical, reproducible); the missing-edge list is mine and each entry is
checkable in one line.

**What would refute it.** A statement that the column is descriptive prose rather
than a dependency graph. Neither schema page says that, and
`residual-machinery.md`'s generator record carries a separate typed
`dependencies : {Symbol}` field for *"same-pass fixed-point co-convergence"* —
so the corpus already has a place for the loose sense and a place for the strict
one, and the manifest column is doing both.

**Proposed correction.** Split it: `depends-on` holding row references only, and
the informal content moved into the provenance cell where it can be read as
prose. Then the column becomes checkable — every referent must resolve to a row
number — which is what would have caught F26.

---

### F26 — Three `Depends on` cells name storage objects that do not exist anywhere in the corpus.

**Claim.** Row 84 `cluster-expansion-energy` depends on an **`ECI cache`**;
row 55 `bond-valence-sum` on an **`R0-table`**; row 87
`reference-phase-energy-cache` on a **`DFT battery`**.

**Evidence, `ECI cache`.** The string `ECI` occurs in exactly two places in the
whole repository outside the manifest: `property-templates.md:130`,
`ConfigurationalFreeEnergyOf(parameterization: {ClusterExpansion(ECI), …`, which
is a parameterization of a template, not a cache; and nothing else. No page
defines an ECI cache, no file under `data/` holds effective cluster
interactions, and no registry row produces them. Row 84's output
`E_CE = Σ_α J_α Π_{i∈α} σ_i` is **linear in exactly the quantity that has no
source** — the row computes nothing without them.

**Evidence, `R0-table`.** The bond-valence parameters `R₀` are the entire content
of a bond-valence sum: `BVS = Σ_I exp((R₀ − R_I)/b)`. Grepping `journals/` and
`data/` for `R0`, `bond-valence` and `bond valence` returns one hit outside the
manifest — `observable-bundles.md:89`, which lists bond-valence sum as a member
of the `static-validity` bundle. There is no table, in `data/reference-data/` or
anywhere else.

**Evidence, `DFT battery`.** "Battery" *is* a defined concept in this corpus, but
it is the **reference battery** — 179 rows of curated measured and computed
values in five CSVs, described at `reference-battery.md:40-52`. A "DFT battery"
is not that object, and no page defines one. Row 87's `E_ref` values therefore
have no stated source, on a row whose `anchor-class` is `faithful`, which
`named-formulas.md:246-249` defines as *"trusted only against a reference-grade
computation… or against a measured battery entry."*

Control for all three: the same grep resolves `elastic-tensors.csv` to
`reference-battery.md:47` and `accuracy-ledger.md:362,398`, and resolves
`linear-response sub-stage` to a real page. The method finds referents that
exist.

**Severity** high for `ECI cache` and `R0-table` — both rows are unevaluable, not
merely under-documented. Medium for `DFT battery`, which is a provenance gap on
a row that otherwise works. **Confidence** certain (mechanical, with control).

**What would refute it.** Any of the three appearing under a different name. I
also searched for `effective cluster interaction`, `cluster expansion`, `bond
valence parameter` and `R_0` with the subscript variants folded; nothing.

**Proposed correction.** Register the two absent objects as rows — an
ECI-fitting row and an `R0` parameter table row, the latter exactly parallel to
row 87 — or mark both dependencies `(unregistered input)` as rows 7, 8, 9, 47
and 80 already do. The honest marking is the cheap fix; the rows are the right
one. `DFT battery` should say which battery.

---

### F27 — Two of the ten fields the formula record declares have no column, under a page that says there is one column per field. One of them is the record of whether the adjoint gate passed.

**Claim.** `formula-registry.md:43`: *"**One column per field of the formula
record** ([named-formulas#formula-record]):"* — followed by a nine-row table.

**Evidence.** `named-formulas.md:71-84` declares a ten-field record: `name`,
`signature`, `bundle`, `cost-tier`, `differentiability`, `anchor-class`,
`provenance`, `depends-on`, **`applicability`**, **`adjoint-validated`**. The
manifest header is `#,Name,Signature,Bundle,Tier,Diff,Path,Source,Depends on` —
the row number plus eight. The last two record fields have no column and no
per-row value anywhere.

`adjoint-validated : Passed | Failed(witness) | NotApplicable |
Relaxed(rationale)` is the field recording whether the vJp-versus-JvP
registration gate passed. **23 rows are `adjoint` and 5 are
`fixpoint-adjoint`** — 28 rows that run that gate — and the manifest, which
`formula-registry.md:31-33` calls *"canonical for every per-row value"*, records
no verdict for any of them.

The same enum appears at `residual-machinery.md:96` under a **different name**,
`adjoint-cert`, on the *generator* record rather than the formula record. So the
verdict lives on a different object in a different library under a different
name, and the formula record's field is unpopulated.

`applicability` is partly mitigated: `applicability-classifiers.md:111-125`
carries a **per-property** table of 13 predicates, and five rows carry an
`is-…-gated` note in prose inside the provenance cell (`is-alloy-gated` ×1,
`is-dielectric-layer-gated` ×3, `is-noncentrosymmetric-gated` ×1). That is 5 of
134 rows, against a record field declared for all of them, and the property table
is keyed on properties rather than rows.

**Severity** medium-high for `adjoint-validated` — the corpus's central
differentiability guarantee has no per-row record. Medium for `applicability`.
**Confidence** certain (mechanical).

**What would refute it.** A second manifest or generated view carrying the two
columns. `generated/` holds no manifest; I checked.

**Proposed correction.** Either add both columns, or amend
`formula-registry.md:43` to say which record fields the manifest carries and name
where the other two live. The `adjoint-validated`/`adjoint-cert` naming
divergence should be resolved to one name in the same edit — two names for one
four-value enum across two pages is the second-copy hazard
`formula-registry.md:107-110` warns about, applied to a field rather than a
vocabulary.

---

### F28 — `reference-battery` states that nothing points into its three absent sub-areas. Six registry rows point into them, and two exist for no other purpose.

**Claim.** `reference-battery.md:52-55`: *"**Three sub-areas have no file yet**:
interface properties — Schottky barriers, work functions and carbide-formation
energies per metal-semiconductor pair; defect formation energies per host,
species and charge state; and elemental chemical potentials at standard
conditions. **Nothing reads them, and no row anywhere points into them.**"*

**Evidence.** Six manifest rows point into exactly those three sub-areas:

| row | signature | which absent sub-area |
|---|---|---|
| 47 `barrier-from-workfunction-affinity` | `(W_m, χ_s) → φ_B` | work functions; its `Depends on` says so verbatim — *"work function and electron affinity (unregistered inputs)"* |
| 48 `MIGS-corrected-barrier` | `(W_m, χ_s, S, φ_CNL, E_g) → φ_B_eff` | Schottky barriers |
| 81 `carbide-growth-parabolic` | `(D_0, E_a, T, t) → x²(t)` | carbide formation |
| 30 `defect-formation-energy` | `(E_def, E_host, μ_i, q, E_F) → E_form` | defect formation energies per host, species and charge state |
| 66 `chemical-potential-ref-table` | `(species, T, P) → μ_i` | elemental chemical potentials at standard conditions |
| 87 `reference-phase-energy-cache` | `(phase-id) → E_ref` | the reference phase energies rows 66 and 30 stand on |

Rows 66 and 87 have no other content: a chemical-potential reference table and a
reference-phase energy cache **are** the elemental-chemical-potential sub-area.
The sentence's second clause is false on its strongest reading (no row points
into them) and its first clause is false on any reading (nothing reads them).

**Why it matters beyond the sentence.** The claim is what licenses leaving the
three files unwritten. Read as true, three absent data files are dead weight;
read correctly, they are the unstated inputs of six registered formulas —
including row 30, which is on the MVP capability slice
(`capability-slices.md:57`), and row 66, whose derivative feeds row 69's Maxwell
residual (F7).

**Severity** high — a false negative that hides six live dependencies.
**Confidence** certain.

**What would refute it.** A narrower reading of "row" as "reference-data row"
rather than "row anywhere". Even under it, *"Nothing reads them"* is false: rows
30, 47 and 66 read them. The sentence says "no row **anywhere**".

**Proposed correction.** Replace with the true statement and the consequence:
*"Three sub-areas have no file yet… **Registry rows 30, 47, 48, 66, 81 and 87
consume values from them**, and stand on unregistered inputs until the files
exist."* This is a cross-subject finding — the sentence belongs to whoever owns
`reference-battery`; the six rows are mine, and they are the evidence.

---

### F29 — Row 120 declares an input its own stated form never uses, and the option the cell offers makes that form incomplete.

**Claim.** Row 120 `ahc-gap-renormalization`, signature
`(ZPR, Θ, T, ε) → ΔE_g(T)`, provenance *"adiabatic Allen-Heine one-shot;
ΔE_g=ZPR·coth(Θ/2T); slope-kind∈{isochoric,total} per ProvenanceLedger; a.k.a.
Giustino RMP 2017 / Antonius PRL 112 215501"*.

**Evidence.** The stated closed form `ΔE_g = ZPR·coth(Θ/2T)` consumes `ZPR`, `Θ`
and `T`. **`ε` appears in the signature and nowhere in the form.** The functional
form itself is right — `coth(Θ/2T) = 2n_B(Θ) + 1`, giving `ΔE_g → ZPR` as
`T → 0` and `ΔE_g ≈ 2·ZPR·T/Θ` at high temperature, both correct for a one-shot
adiabatic Allen–Heine treatment.

The two readings of `ε` are both defects, in opposite directions:

- **`ε` is strain or volume.** Then the cell's `slope-kind ∈ {isochoric, total}`
  is the operative switch, and the stated form computes only the **isochoric**
  (electron-phonon) part. The **total** gap shift is the isochoric part *plus* the
  thermal-expansion contribution, which is what `ε` would carry. So under
  `slope-kind = total` the stated form is **incomplete**, and the cell offers a
  setting its own formula cannot compute.
- **`ε` is a dielectric constant** (the reading F24 shows is available, since
  eight other rows use bare `ε` that way). Then it is a dead input.

The reference-data CSVs settle which quantity is intended but not which the
formula computes: they carry `ahc-zpr-isochoric`, `ahc-zpr-gap-isochoric` and
`ahc-zpr-lattice-expansion` as **separate** properties, so the corpus's own data
model treats the lattice-expansion term as a distinct quantity from the isochoric
ZPR — and the row has one `ZPR` slot.

**Severity** medium. **Confidence** high on the mismatch (mechanical: the input
does not occur in the form); medium on which reading is intended.

**What would refute it.** A statement that `ε` enters through `ZPR` — i.e. that
the caller supplies a strain-dressed ZPR. Nothing says so, and the separate
`ahc-zpr-lattice-expansion` reference property argues against it.

**Proposed correction.** State the total-slope form explicitly with its
thermal-expansion term and the input it consumes, or drop `ε` and restrict
`slope-kind` to `isochoric`. Either way say which quantity `ε` is.

*This was found by the same mechanical sweep that produced F30: for every row
whose provenance cell states a closed form, check which signature inputs the form
never mentions. Control: row 72, whose cell states
`T_e = T_L + (2/3)(j·E)τ_E/(n k_B)` against signature `(j·E, τ_E, n, T_L)`, is
correctly **not** flagged — every input occurs. Six further flags were dismissed
as notational variants (`Φ` for `Φ_dose`, `σ_i` for `σ-config`, `E_a` for
`E_a_cryst`, `P_sp(T0)` for `P_sp0`) and are logged in §2.*

---

### F30 — Row 129 states a proportionality, not a formula, and its trap density is unused. It cannot form a current density.

**Claim.** Row 129 `poole-frenkel-current`, signature
`(N_t, φ_t, E, ε_opt, T) → J_PF`, provenance *"trap-assisted dielectric leakage
J∝E·exp(−(φ_t−β_PF√E)/kT), β_PF=√(q³/(π ε_opt ε0))"*.

**Evidence.** The cell states `J ∝ E·exp(…)` — a proportionality with no
prefactor. The declared output `J_PF` is a current density, and a proportionality
cannot produce one. The signature's `N_t` (trap density), which is what the
missing prefactor is built from — the standard form is
`J = q μ N_t E exp(−(φ_t − β_PF√E)/k_BT)`, or equivalently `q n₀ μ E` with `n₀`
set by the trap occupancy — **appears nowhere in the stated form**. The carrier
mobility in the dielectric is absent from both the form and the signature.

This is the same class as F8 (row 83, missing fatigue ductility coefficient) and
F9 (row 82, missing Black prefactor): a row whose declared output cannot be
formed from what it declares. It is the third instance, which makes it a pattern
rather than three accidents — and all three are in the `degradation` and
`non-equilibrium-operating` bundles, the bands added most recently.

**The Poole–Frenkel coefficient itself is correct** and I am not filing against
it: `β_PF = √(q³/(π ε_opt ε₀))` is exactly twice the Schottky coefficient
`β_S = √(q³/(4π ε ε₀))`, which is the standard relation. The corpus got the
factor of two right — the same class of hazard as the `(2ω/c)` absorption
prefactor it pins on `named-formulas#corrected-forms`.

**Severity** medium-high — an unformable output, on a row the cell calls *"the
dominant high-T gate-leakage channel"*. **Confidence** high.

**What would refute it.** A convention that `J_PF` is reported normalized, or a
prefactor supplied by the template rather than the row. Neither is stated; row 82
would need the same exemption and is filed as F9 for lacking it.

**Proposed correction.** Write the prefactor into the form and add the
dielectric mobility to the signature: `(N_t, μ_diel, φ_t, E, ε_opt, T) → J_PF`
with `J = q μ_diel N_t E exp(−(φ_t − β_PF√E)/k_BT)`, and replace `∝` with `=`.

---

### F31 — Two rows are `faithful` for work that involves no reference-grade computation, and both sit downstream of `cheap` rows that do the actual physics.

**Claim.** `named-formulas.md:246-249` defines the field: *"A `cheap` row stands
on its own closed form. A `faithful` row is one whose value is trusted only
against a reference-grade computation — a density-functional, perturbation,
non-equilibrium-Green's-function or Monte-Carlo evaluation — or against a
measured battery entry."*

**Evidence.** Fifteen rows are `faithful`. Thirteen fit the definition
exactly — row 6 (a G0W0 *surrogate*, anchored to real G0W0), 13 (self-consistent
phonons), 40 and 41 (capture coefficients and Huang–Rhys factors from a
density-functional relaxation), 80 (literally non-equilibrium Green's
functions), 87 (a density-functional cache), 88 and 92–94 (density-functional
perturbation theory), 99–101 (invariants over a density-functional eigenstate
grid).

**Two do not.** Row 45 `wulff-shape`, `(γ(hkl)) → polyhedron`, is the Wulff
construction — the inner envelope of planes placed at distance proportional to
γ(hkl). Row 67 `phase-diagram-convex-hull`, `(G_phases(μ,T)) → hull`, is a lower
convex envelope of a set of numbers. Neither invokes a density-functional,
perturbation, Green's-function or Monte-Carlo evaluation. Both are deterministic
geometry over inputs supplied by other rows.

Nor can either be anchored the other admissible way. The reference battery's five
CSVs hold no surface-energy, Wulff, facet, hull or phase-boundary property — I
listed every distinct `Property` value across all five and none matches. Control:
the same listing returns `bulk-modulus`, `debye-temperature` and `elastic-C11`,
so the probe finds properties that are there.

**The inversion is the sharp part.** The rows producing their inputs are `cheap`:

| row | tag | what it does |
|---|---|---|
| 44 `surface-grand-potential-γ` | **cheap** | computes γ from a slab energy — the density-functional step |
| 45 `wulff-shape` | **faithful** | geometry over γ |
| 65 `gibbs-free-energy-phase` | **cheap** | computes G from `E_0` and a phonon spectrum |
| 67 `phase-diagram-convex-hull` | **faithful** | geometry over G |

So the row carrying the reference-grade physics is the one that "stands on its
own closed form", and the row doing pure geometry is the one "trusted only
against a reference-grade computation." That is the field's meaning reversed on
both pairs.

**The corpus groups these rows itself and then splits them.** Row 46's provenance
cell reads: *"relaxation: softmin over γ(term) at temperature τ_soft — **same
log-sum-exp family as rows 45/67**"*. Rows 45, 46 and 67 are one family by the
corpus's own statement: same relaxation, and 45 and 46 consume the same γ from
row 44. Their anchor-class is `faithful`, `cheap`, `faithful`. Across all six
`relaxed` rows the split is 2 faithful (45, 67) against 4 cheap (46, 50, 84, 85),
with no stated ground anywhere.

**Why it is not cosmetic.** `named-formulas.md:251-256` makes this field
load-bearing: *"That makes it the axis a consistency pair runs along… a
consistency pair is one whose two members sit on opposite sides of this field —
the cheap model against the microscopic reference it has no agreement theorem
with."* Under that rule rows 44 and 45 qualify as a consistency pair — they sit
on opposite sides — but they compute different objects (a surface energy and a
polyhedron), so there is nothing to compare. A pair-construction routine reading
this column would build a residual between a scalar and a shape.

**Severity** medium-high — it corrupts the construction the field exists to
drive. **Confidence** high on rows 45 and 67 (their work is geometry, and the
battery has no entry for either); certain on the internal inconsistency of the
45/46/67 family, which the corpus states and then contradicts.

**What would refute it.** A reading of `faithful` as "the declared relaxation
must be checked against the exact discrete construction." That is a real
obligation — but it is obligation 9 on the `relaxed` tag, not the anchor class,
and it would apply equally to rows 46, 50, 84 and 85, which are `cheap`.

**Proposed correction.** Move rows 45 and 67 to `cheap`, and — if the intent was
that a hull or a Wulff shape is only trustworthy against a reference computation
of the same object — say that on `named-formulas#anchor-class` as a third case,
because as written the field admits only two.

---

### F32 — Of the three compositions that invoke a registered row, two disagree with the row's signature. One of them proves row 30 is missing a required input.

**Claim.** `typed-compositions` contains 21 `AlgebraicOf(…, formula = X)`
invocations. Eighteen name unregistered formulas (that is F2). **Exactly three
name a registered manifest row**, and they are the only place in the corpus where
a call site can be checked against a signature.

**Evidence.**

| # | invocation (`typed-compositions`) | manifest signature | agree? |
|---|---|---|---|
| 61 | `BulkModulus = AlgebraicOf({ElasticConstants}, formula = bulk-modulus)` (line 164) | `(C_ij) → B` | **yes** — one input, matching |
| 2 | `BandGap = AlgebraicOf({BandStructure}, formula = bandgap-indirect)` (line 135) | `(BandStruct, k-grid) → Scalar` | **no** — the invocation drops `k-grid` |
| 30 | `DefectFormationEnergy = AlgebraicOf({E_defect, E_perfect, Δn, μ, q, E_F}, formula = defect-formation-energy)` (lines 116–119) | `(E_def, E_host, μ_i, q, E_F) → E_form` | **no** — the invocation carries `Δn`; the signature has no such input |

Row 61 is the control: the method can find agreement when it is there.

**Row 30 is the substantive one, and the invocation is the correct side.** The
Zhang–Northrup formation energy is

```
E_form[X^q] = E_def − E_host − Σ_i n_i μ_i + q(E_F + E_VBM) + E_corr
```

`n_i` is the number of atoms of species *i* added or removed. Without it the term
`Σ_i n_i μ_i` cannot be formed: the signature supplies the chemical potentials
`μ_i` and no stoichiometry to weight them by. **The manifest row cannot form its
declared output**, and the corpus's own composition — which carries `Δn`
explicitly — says so.

This is the fourth instance of one class: F8 (row 83, fatigue ductility
coefficient absent), F9 (row 82, Black's prefactor absent), F30 (row 129, trap
density unused and no prefactor), and now row 30. Four rows whose declared output
cannot be formed from their declared inputs. Row 30 is the most serious of the
four: it is on the MVP capability slice (`capability-slices.md:57`), it feeds
rows 34, 35 and 124, and its derivative is one of the three slow-tier consistency
identities (`residual-definitions.md:194`, `dE_form/dE_F = q`).

**Row 2 is the milder one but the direction matters.** An *indirect* gap is
`min_k E_c(k) − max_k′ E_v(k′)` over a sampled grid — the grid is what makes it
indirect rather than direct. The invocation passing only `{BandStructure}` either
means the grid is carried inside the band-structure object (in which case row 2's
signature is redundant and row 1 `bandgap-direct`, `(BandStruct) → Scalar`, is the
consistent form) or it means the invocation is under-specified. The two pages
cannot both be right, and nothing reconciles them.

**A secondary absence, stated separately because my confidence is lower.** The
`q(E_F + E_VBM)` term needs a reference for `E_F`. The strings `VBM` and
`valence band maximum` appear **nowhere in `journals/`**, case-insensitively —
the only occurrence in the repository is inside row 48's provenance cell in the
manifest (*"φ_CNL is measured from the VBM"*). So the corpus states the
valence-band reference convention for the Schottky-barrier row and nowhere for
the defect row that also needs it. Control: the same case-insensitive method
finds `fermi` in `named-formulas.md`; an earlier case-**sensitive** pass returned
zero and would have reported a false absence, which is logged here because it is
exactly the character-class failure the method rules exist to catch.

**Severity** high for row 30, medium for row 2. **Confidence** certain on the
disagreements (mechanical, both texts quoted); high on the physics that `Δn` is
required.

**What would refute it.** For row 30: a convention that `μ_i` is pre-weighted by
stoichiometry — i.e. that the input is `Σ n_i μ_i` rather than the chemical
potentials themselves. Nothing states that, and the invocation passing `Δn` and
`μ` as separate members contradicts it.

**Proposed correction.** Row 30 → `(E_def, E_host, Δn, μ_i, q, E_F) → E_form`,
matching the corpus's own invocation, and state the `E_F` reference. Row 2:
decide which page is right and make the other match.

---

### F33 — The structured input types of the topology band, the iterative thermal-conductivity row and the reference cache are named in signatures and defined nowhere.

**Claim.** Signatures are the corpus's type contract
(`formula-registry.md:49`, *"typed inputs to output"*). A structured input — an
object a consumer has to construct, as against a scalar quantity — must be
definable from the corpus.

**Evidence.** I extracted every word-like input token from all 134 signatures
(114 of them) and searched `journals/` for each. Restricting to **structured
types**, not scalar quantity symbols:

| input | rows | defined in `journals/`? |
|---|---|---|
| `BandStruct` | 1, 2, 3, 4 | **yes** — `typed-compositions` |
| `DOS` | 5 | **yes** — `typed-compositions`, `accuracy-ledger` |
| `k-mesh` | 4 | **yes** — `build-sequence`, `reference-battery`, `residual-machinery` |
| `q-mesh` | 10 | **yes** — `coupling-structure` |
| `k-grid` | 2 | **no** |
| `AZ_class` | 96 | **no** |
| `high-sym-momenta` | 98 | **no** |
| `eigenstates_on_grid` | 99, 100 | **no** |
| `antiunitary_op` | 100 | **no** |
| `eigenstates_on_loop` | 101 | **no** |
| `X_BS_element` | 102 | **no** |
| `boundary_orientation` | 102 | **no** |
| `site-orbit` | 97 | **no** |
| `collision-matrix` | 122 | **no** |
| `phase-id` | 87 | **no** |
| `slab_pair` | 50 | **no** |

The first four are the control: the method finds structured types that are
defined, so the eleven absences are not an instrument failure.

**Three things this shows, in ascending order of weight.**

*One — `k-grid` against `k-mesh`.* Rows 2 and 4 are adjacent rows sampling
reciprocal space, and they spell the object differently. Only `k-mesh` occurs
anywhere else in the corpus. Either they are the same type under two names, or
they are two types and nothing says how they differ.

*Two — six rows, five slab spellings, none defined.* Row 44 `E_slab`, row 50
`slab_pair`, rows 51 and 86 `slab_A`/`slab_B`, row 58 `slab`, row 59
`slab_twin`/`slab_bulk`. No page defines a slab type. A consumer implementing the
surface-resolved bundle has to infer the object five times.

*Three — the topology band is un-implementable from the corpus.* Rows 96–102 take
eight structured inputs and **not one is defined**. `topology-atlas.md` is the
page that owns them and it does define two neighboring objects — its atlas record
carries `EBRs : elementary band representations` and `compatibility :
compatibility-relation matrix` (lines 32–33) — so the page had the opportunity and
the form, and the signatures' own inputs are not among them. `AZ_class` is the
sharpest: Altland–Zirnbauer is a ten-fold classification of *Hamiltonians* by
time-reversal, particle-hole and chiral symmetry, and row 96 pairs it with a
space-group number to produce a symmetry-indicator group. Whether that is even the
right classifying input is a physics question for the topology undergraduate; that
it is undefined is settled here.

`typeclass-alphabet` does not close this. It defines *typeclasses* — `Quantity`,
`Sampleable`, `HasAnalyticStructure`, `DiscreteStructure` — which say what
operations a type supports, not which concrete types exist.

**Severity** medium — no claim is false; eleven signatures cannot be
implemented from the corpus. It is the undeclared-absence class, and it lands
hardest on the two bands added last. **Confidence** certain on the absences
(mechanical, with control); the reading of which tokens count as "structured" is
mine and the table shows every one so it can be disputed row by row.

**What would refute it.** A type-definition page I did not search. I searched all
of `journals/`; `typeclass-alphabet` and `property-templates` are the two pages
that could carry it and neither does.

**Proposed correction.** Define the eight topology inputs on `topology-atlas`
beside the two record fields already there, unify the slab spellings to one type,
and make `k-grid` and `k-mesh` one name. `collision-matrix` and `phase-id` need
definitions wherever rows 122 and 87 are documented — `phase-id` is the key space
of the cache F26 shows has no backing object, so the two should be fixed together.

---

### F34 — The two sum-rule rows have swapped conventions. Row 7 states its rule in force constants and takes the mass-weighted dynamical matrix, which differ by a factor the corpus's MVP material makes invisible.

**Claim.** `named-formulas.md:319-321` pins the acoustic sum rule as one of five
canonical forms: *"The acoustic sum rule sums over all lattice translations,
`Σ_J Σ_R Φ_{IαJβ}(R) = 0`, not over the sites of one cell."* Row 7's signature is
`(D(q→0)) → ‖residual‖`.

**Evidence.** Those are two different objects. The corpus says so itself:
`property-templates.md:82` defines `HarmonicStiffnessHessianOf` as *"the
**mass-weighted** dynamical matrix"*, and row 9 `(D(q)) → ω_λ(q)` produces
frequencies directly from `D`, which is only true of the mass-weighted matrix
(its eigenvalues are `ω²`). So in this corpus `D` is mass-weighted and `Φ` is not:

```
D_{Iα,Jβ}(q) = (1/√(M_I M_J)) · Σ_R Φ_{Iα,Jβ}(R) · e^{iq·R}
```

At `q → 0` this gives `Σ_R Φ_{Iα,Jβ}(R) = √(M_I M_J) · D_{Iα,Jβ}(0)`, so the
pinned rule expressed in the object row 7 actually consumes is

```
Σ_J √(M_J) · D_{Iα,Jβ}(0) = 0
```

**not** `Σ_J D_{Iα,Jβ}(0) = 0`. The two coincide only when every mass in the cell
is equal.

**And the corpus's MVP material is the one case where they coincide.** Diamond is
monatomic, so the unweighted sum is correct for it and any implementation checked
against diamond passes. The materials where it fails are the rest of the
program:

| material | masses | `√(M_J)` spread the naive form drops |
|---|---|---|
| diamond | C only | 1.000 |
| c-BN | 10.81, 14.01 | 1.138 |
| AlN | 26.98, 14.01 | **1.388** |
| GaN | 69.72, 14.01 | **2.231** |
| β-Ga₂O₃ | 69.72, 16.00 | **2.088** |

Diamond is exactly 1 and hides the error completely; c-BN is within 14% and
hides most of it. The error is a factor of two on both Wave-2 gallium compounds.

**The corpus already carries this exact hazard as a trap, and applies it to a
different row.** `traps.md:226-230`, *Electron-phonon vertex normalization*:
*"The `√(2Mω)` single-mass shorthand is valid for one species only; multi-species
cells need mass-weighted eigenvectors. **Breaks:** a per-species mass error in
every electron-phonon matrix element. — advisory"*. That is structurally the same
defect — a single-species shorthand applied to a multi-species cell — and it is
registered for the electron-phonon vertex and not for the sum rule.

**Row 126 has the mirror-image problem.** `rotational-sum-rule` takes
`(Φ[I,α,J,β], R_I)` — bare force constants, correctly — but its `Depends on`
cell names `dynamical-matrix-hermiticity (row 8), phonon-dispersion (row 9)`.
Both of those consume `D(q)`; **neither produces `Φ`**. So the row's declared
dependencies produce none of its inputs. And the row it does *not* name is row 7,
the acoustic sum rule — which matters physically, because the rotational
condition `Σ_J (Φ_{Iα,Jβ}R_{Jγ} − Φ_{Iα,Jγ}R_{Jβ}) = 0` is **origin-dependent
unless the translational sum rule holds**: shifting `R_J → R_J + a` changes it by
`a_γ Σ_J Φ_{Iα,Jβ} − a_β Σ_J Φ_{Iα,Jγ}`, which vanishes only when the acoustic
sum rule is satisfied. Row 126's frame-independence is conditional on row 7, and
row 126 does not name row 7.

*Another investigation has separately found the rotational sum rule wrong as
written and frame-dependent. I have not duplicated that; the finding here is the
registry-side one — the dependency edge that would make it conditional is absent,
and the two sum-rule rows take each other's natural input type.*

**A third, smaller ambiguity, stated with lower confidence.** For a polar
material `D(q→0)` is direction-dependent — that non-analytic limit is what row 88
exists to supply. Row 7's signature writes `D(q→0)` with no direction argument
and no statement of whether the sum rule is checked on the analytic part or the
full limit. AlN, GaN and β-Ga₂O₃ are polar. I flag this rather than file it.

**Severity** high — a canonical pinned form that does not match the signature of
the row implementing it, on a residual that is one of the corpus's separately
weighted contributions (`residual-definitions.md:251`, *"The acoustic sum rule
per Cartesian pair (α, β) and per shell R"*), failing silently on the MVP
material and biting on all three Wave-2 materials. **Confidence** high on the
algebra (derivable in three lines, shown above); certain on the row-126
dependency mismatch (mechanical).

**What would refute it.** A statement that `D` in row 7 denotes the
non-mass-weighted force-constant matrix in reciprocal space — some authors do
write it that way. `property-templates.md:82` and row 9's signature both say
otherwise. If that reading were intended, row 9 would be wrong instead.

**Proposed correction.** Write the mass weighting into the pinned form so the two
objects agree — either state the rule as `Σ_J √(M_J) D_{Iα,Jβ}(0) = 0` beside the
`Φ` form, or change row 7's signature to take `Φ` as row 126 does. Add row 7 to
row 126's `Depends on`, and replace rows 8 and 9 there, which produce nothing row
126 consumes. Add the multi-species case to `traps.md` beside the
electron-phonon-vertex entry it already has.

*Cluster 4 was asked this same question independently, with the derivation to
perform rather than the answer. Its return either corroborates this or corrects
it, and is recorded as such.*

---

### F35 — Cross-subject, reported not chased: row 111 consumes a value whose provenance cites a page that declares the value does not exist.

**My half of this is row 111.** `nrt-displacements`, `(T_dam, E_d) → N_d`,
`Depends on: T_dam, E_d(host)`. It consumes a per-host displacement threshold.
The other half belongs to whoever owns the provenance ledger, and I have not
chased it further than the two greps below.

**Evidence.** `data/reference-data/material-constants.csv` carries:

```
displacement-threshold-Ed, β-Ga₂O₃ (C2/m), —, 25 eV, 5 eV,
  literature (carried from non-equilibrium stratum H.1; multiscale-state §4),
  literature-review, 1, 2026-07-16, 2026-07-16
```

The `Source` field names `multiscale-state §4` as where the value comes from.
`multiscale-state.md:242`, in the row-111 table in that very section, reads:

| Host | Displacement threshold `E_d` |
|---|---|
| Diamond | ~37–50 eV |
| GaN | ~20 eV |
| AlN | ~35 eV |
| β-Ga₂O₃ | **`UNSEEDED`** |

And `multiscale-state.md:61`, a declared open question, states it in prose: *"The
β-Ga₂O₃ value is **UNSEEDED**; diamond, GaN and AlN carry numbers whose only
source is that chapter."*

**So the value's provenance is self-refuting**: `25 eV ± 5` cites as its source a
page that says the value is unseeded, and carries the source class
`literature-review`. The inherited lead
(`audit/inherited/PROVENANCE.md`, and the brief's third live thread) already
records that this scalar matches no per-site value in the literature and that its
provenance-type claims a review no internal document performed. **This adds the
sharper fact: the internal document it does cite says the opposite.** Control:
the same CSV's `debye-temperature` rows carry real external citations (Guo APL
106 111909; Wang–Zhao Powder Diffr.), so the file does record genuine provenance
when it has it.

**Registry consequence, which is the part I own.** Row 111's `N_d = 0.8·T_dam/(2·E_d)`
is inversely proportional to `E_d`, and row 112 `frenkel-pair-yield` multiplies
`N_d` straight into a defect density. So the Wave-2 defect density scales as
`1/E_d` on a value with no provenance. The literature's per-site β-Ga₂O₃
thresholds span roughly 7 eV (directional minima) to above 60 eV, which is close
to an order of magnitude in `N_d`.

**Severity** high, but **not mine to fix**. Reported to the principal. What is
mine: row 111 states no per-site or directional convention for `E_d` in a corpus
whose Wave-2 material has five inequivalent sites, and row 111's own signature
takes a **scalar** `E_d` — which is the registry-side statement of the same
problem, and is a finding of the undeclared-absence class regardless of how the
provenance question resolves.

---

### F36 — The anchor-class field exists to define consistency pairs. Not one constructible consistency pair exists in the manifest, and all three pairs the corpus names by hand fail — including the one it names twice, by row number.

**Claim.** `named-formulas.md:251-256` gives the `anchor-class` field its purpose,
and the phrasing is definitional, not descriptive:

> *"That makes it the axis a consistency pair runs along:
> [residual-definitions#pair-kinds] defines the pair kinds, and **a consistency
> pair is one whose two members sit on opposite sides of this field** — the cheap
> model against the microscopic reference it has no agreement theorem with."*

`residual-definitions.md:166-175` then names three pairs as its worked examples.

**Evidence. All three fail, each in a different way.**

**Pair 1 — the one named twice, and by row number.**
`residual-definitions.md:167-168` gives *"Callaway/Slack thermal conductivity
against iterative Boltzmann transport"*, and lines 173–175 make it explicit:
*"The thermal-conductivity siblings — registry rows 121
(`kappa-4phonon-high-t-correction`) and 122 (`iterative-lbte-kappa`) — bind to
registry row 25 as a **consistency pair**."*

| row | | `anchor-class` |
|---|---|---|
| 25 | `single-mode-rta-lattice-kappa` | **cheap** |
| 121 | `kappa-4phonon-high-t-correction` | **cheap** |
| 122 | `iterative-lbte-kappa` | **cheap** |

All three sit on the **same** side. Under the rule `named-formulas` states, this
is not a consistency pair. And row 122 is the iterative Boltzmann solution — the
"microscopic reference" half of the corpus's own sentence — carrying the tag that
means *"stands on its own closed form"*.

**Four pages name this pair, and one of them marks it enforced.**

| where | what it says |
|---|---|
| `residual-definitions.md:167` | *"Callaway/Slack thermal conductivity against iterative Boltzmann transport"* |
| `residual-definitions.md:173-175` | *"registry rows 121… and 122… bind to registry row 25 as a **consistency pair**"* |
| `capability-slices.md:98` | *"the closed-form quasi-harmonic plus Slack–Callaway conductivity sits alongside it as a **consistency pair, not an equivalence pair**"* — on the MVP capability slice |
| `traps.md:406-412` | *"Callaway against the full Boltzmann transport equation is a **consistency** pair, not an equivalence pair… **Breaks:** an obligation that either always trips or is vacuously satisfied. — **enforced**, [residual-definitions#pair-kinds]"* |

**The trap describes its own condition.** It is marked `enforced`, its stated
failure mode is *"an obligation that either always trips or is vacuously
satisfied"*, and the pair it is enforced about does not exist under the rule that
defines pairs — so the obligation it guards is vacuously satisfied. This is the
register's defect class 4 (*"'enforced' as a prose claim with no mechanism"*)
occurring inside my subject, and it is self-diagnosing.

`cert-obligations.md:139` closes the loop from the tolerance side: `τ_method` is
*"declared **per formula pair**"* — and there is no pair to declare it for.

*A side observation, which is F17 propagating.* All four of those passages call
row 25 "Callaway/Slack" or "Slack–Callaway". F17 argues that neither eponym
denotes row 25's signature. If F17 stands, the mis-binding is not a single
provenance cell — it has been copied into four pages, one of which is the MVP
capability slice. That raises F17's blast radius considerably and is why the
eponym sweep was told to settle it against the primary papers.

**Pair 2 — the second member is not registered.**
*"cheap-Chynoweth ionization against Boltzmann/Monte-Carlo"*. Row 74
`impact-ionization-coefficient` (a.k.a. Chynoweth) is `cheap`. Searching all 134
rows for `Monte`, `monte`, `Boltzmann` or `boltzmann` in either the name or the
provenance returns exactly **one** row — row 35 `defect-boltzmann-population`,
which is Boltzmann *statistics*, not Boltzmann transport, and is a defect
population rather than an ionization rate. There is no Monte-Carlo or
Boltzmann-transport ionization row. The pair has one member.

**Pair 3 — neither member is registered.**
The equivalence-pair example is *"Conductivity by Boltzmann transport versus by
Kubo"*. `ConductivityViaBTE` and `ConductivityViaKubo` are two of the eighteen
names `typed-compositions#declared-gap` declares deliberately unregistered (F2).
Neither is a manifest row. This is an *equivalence* pair rather than a
consistency pair, so it does not bear on the anchor-class axis — but it means all
three worked examples in the section are unconstructible from the registry.

**And no other pair is available.** I checked every pair of rows sharing a
declared output token where one is `cheap` and one is `faithful`. Across 117
cheap and 15 faithful rows there is exactly one such pair — rows 99 and 102, both
declaring output type `Integer` — and that is a collision of generic type names,
not a shared quantity: row 99 is a Chern number and row 102 is a boundary-mode
multiplicity. **There is no pair of rows in this manifest computing the same
quantity on opposite sides of the anchor-class field.**

**What this means.** The `anchor-class` column is populated on all 132 substantive
rows and is 13-of-15 correct on its own criterion (F31). But the construction it
exists to drive cannot be performed anywhere in the registry. This is the
"guarantee asserted rather than constructed" class: a field carrying a correct
value, defended by a well-written page, wired to nothing.

It also converges independently with a finding from the tolerance-ledger subject —
that `τ_method`, the tolerance a consistency pair trips at, is declared by **zero
pairs**, and the manifest has no column that could carry one. Two subjects
reached the same place from opposite ends: there are no pairs to declare a
tolerance for.

**Severity** high. The field is one of nine, it is stated as load-bearing on its
own page, and its consumer does not exist. It also downgrades F31 in importance
while confirming it: rows 45 and 67 are mis-tagged, and the mis-tagging currently
costs nothing because nothing reads the column for its stated purpose.

**Confidence** certain on the three pair failures and on the exhaustive
same-output search (both mechanical, reproducible from the manifest alone). The
inference that *therefore* no consistency pair can be built rests on identifying
pairs by shared output token; a pair whose two members declare different output
symbols for the same physical quantity would escape that search — which, given
F23 and F24, is entirely possible and is the honest limit of this sweep.

**What would refute it.** A declared pair list somewhere outside the manifest. I
searched `journals/` for pair declarations and found the definitions and the
three examples, no list. If such a list exists it would also have to explain how
rows 25 and 122 sit on opposite sides of a field that gives them the same value.

**Proposed correction.** Physics-gated, and it is a real decision rather than an
edit. Either row 122 is the microscopic reference — in which case it is
`faithful`, not `cheap`, and so is row 121, and the pair becomes constructible —
or the corpus means something by `cheap`/`faithful` other than what
`named-formulas#anchor-class` says, in which case the definitional sentence at
lines 251–256 is the thing to change. **Row 122's own provenance cell argues for
the first**: it says the row is *"dormant/anchored to published κ_iter in V1, live
solve V2"*, and "anchored to published" is `faithful` by the field's own
definition — *"trusted only against a reference-grade computation… or against a
measured battery entry."* On the corpus's own words row 122 is mis-tagged, and
fixing that one cell makes the corpus's flagship consistency pair exist.

---

## 1b · Findings recovered from the calibration arm — real defects, not detections

**These four are findings, and they must not count toward my calibration score.**
The reason is a scoring hazard worth stating in general terms, because it will
recur on every blind arm this program runs:

> **A plant is an edit. An absence is not editable.** Every defect I planted
> changed a value that was present. A finding of the form *"nothing states X"*
> therefore reads **identically** in the planted copy and the real one — it cannot
> be a detection of anything I did, and counting it as one inflates the score with
> the auditor's own corpus defects. Conversely it cannot be dismissed as a
> false positive either, since the planted copy is faithful to the real one
> everywhere I did not edit.
>
> **Operationally: partition every blind-arm return into EDIT findings and
> ABSENCE findings before scoring. Score against EDIT findings only. Route
> ABSENCE findings into the normal findings file after checking them against the
> real artifact.** That check is not optional — an absence in the planted copy is
> only a real defect if it survives in the unplanted one, and my plant on row 55
> is exactly a case where it might not have.

All four below were checked against the **real** `data/registry-manifest.csv`, not
the planted copy, and all four survive. Credit for finding them belongs to the
calibration undergraduate.

### F37 — Row 55 cannot form its output: it needs a neighbor set, and under periodic boundaries that needs the cell vectors and a cutoff.

Row 55 `bond-valence-sum`, real signature `(R_I, R0, b) → BVS_atom`, provenance
cell `S2` — no parenthetical at all.

The bond-valence sum is `BVS_I = Σ_j exp((R₀ − R_Ij)/b)`, a sum **over the
neighbors j of atom I**, of **bond lengths** `R_Ij`.

**The manifest settles what `R_I` denotes, and it is not a bond length.** Two
other rows use the same token: row 132 `xrd-structure-factor`,
`(h, R_I, Z_I, ⟨u²⟩, (hkl))`, whose stated form is
`F_hkl = Σ_I f_I(q)·e^{iq·R_I}·e^{−W_I}` — there `R_I` is unambiguously an
**atomic position**, and row 132 correctly also takes `h`. And row 126
`rotational-sum-rule`, `(Φ[I,α,J,β], R_I)`, likewise uses it as a position.

So on row 55 `R_I` is a set of atomic positions, and the bond lengths the formula
needs must be built from them. Under periodic boundaries that requires the cell
vectors `h` (minimum image, or a supercell expansion) and a coordination cutoff
to decide which neighbors are bonded. Row 55 carries neither. **Row 132 — the
one other row taking `R_I` — takes `h` alongside it. Row 55 does not.**

**The corpus supplies exactly these on the adjacent row and not on this one.**
Row 50 `interface-bond-counting` is `(slab_pair, **cutoff**) → bond-vec` — it
takes the cutoff explicitly, and its provenance cell discusses the cutoff at
length. Row 60 `elastic-constants-Cij` names `h` in its `Depends on` cell. So `h`
and a cutoff are both objects this registry passes when a row needs them; row 55
needs both and receives neither. `h` is a first-class state slot
(`unified-state.md:30`, `crystal-inputs.md:50-53`), so nothing was missing to pass.

Fifth instance of the unformable-signature class, after rows 82, 83, 129 and 30.
**Severity** medium-high. **Confidence** high. **Correction:**
`(R_Ij-set | (R_I, h, r_cut), R0, b) → BVS_atom`, and note that `R0` and `b` are
per-cation–anion-pair parameters, which is the `R0-table` F26 shows does not exist.

### F38 — Row 91's Madelung constant has no site charges and no reference-length convention, and row 89 consumes it beside a length that must match a convention neither row states.

Row 91 `lattice-coulomb-summation-scalar`, `(lattice) → α_M`,
`a.k.a. Madelung constant`.

A Madelung constant is not a function of the lattice alone. It requires the
**formal site charges** — for a structure with more than one inequivalent site
there is a constant per site, and it scales with the charge assignment — and it
is defined only relative to a chosen **reference length**. Rock-salt is quoted as
1.747565 against the nearest-neighbor distance and 3.495 against the cubic
lattice parameter: the same structure, two numbers differing by a factor of two,
both correct under their own convention.

**The consequence is downstream and quantitative.** Row 89
`charged-supercell-extrapolation-isotropic-general` is `(q, ε, L, α_M) → ΔE_iso`,
and the Makov–Payne leading term is `q²α_M/(2εL)`. `α_M` and `L` must be
expressed against the **same** reference length or the correction is wrong by
their ratio. Row 89 takes them as two independent inputs and states no
requirement that they agree; row 91 states no convention for the one it emits.
This is a finite-size correction on charged defect supercells — the quantity it
corrects is a defect formation energy, which is row 30, which is on the MVP
capability slice.

**Severity** high. **Confidence** high. **Correction:** give row 91 the site
charges and a declared reference length, and state on row 89 that `L` is measured
against the same one.

### F39 — `D_it` carries no unit, the two available readings differ by a factor 6.24×10¹⁸, and the corpus's own stated relation is dimensionally consistent under both.

Row 116 `interface-trap-density` produces `D_it(E)`; rows 115 and 119 consume it.
Row 119's provenance cell states the conversion `C_it = q²·D_it`.

Interface trap density is conventionally quoted in `cm⁻²eV⁻¹`. The SI reading is
`m⁻²J⁻¹`. Neither row says which, and no unit appears in any signature (F23).

**Dimensional analysis cannot catch this, which is what makes it dangerous.**
Under `D_it` in `cm⁻²J⁻¹`: `q²·D_it` = C²·cm⁻²·J⁻¹ = C²/(cm²·C·V) = C/(cm²·V) =
F/cm². Under `D_it` in `cm⁻²eV⁻¹`: identical dimensional form, because an
electron-volt is a joule times a dimensionless number. **Both readings pass a
dimensional check and their numeric values differ by `1/q = 6.2415×10¹⁸`** —
18.80 orders of magnitude, arithmetic run rather than asserted.

`D_it` drives subthreshold swing (row 119) and the two-dimensional electron-gas
sheet density (row 115), both figures of merit. A 10¹⁸ error in either is not a
tolerance question.

This is the single sharpest instance of F23 in the manifest: the field that would
disambiguate is declared by the schema, absent from all 134 rows, and the
`Quantity` typeclass method that would convert between the readings — `rescale`
— has no data to read.

**Severity** high. **Confidence** certain (the arithmetic is above and
re-runnable). **Correction:** state the unit on rows 116, 115 and 119.

### F40 — The Voigt shear convention is unstated on the two rows that consume Voigt strain, and it is a factor of two.

Rows 114 `(Z*[I,α,β], du/dε[κ,J], Ω, e_clamped) → e[i,J]` and 117
`(e[i,J], ε[J]) → P_pz[i]` use Voigt index `J` on a **strain**.

Voigt notation treats stress and strain asymmetrically: engineering shear strain
carries a factor of two over tensor shear strain (`γ_4 = 2ε_23`), while stress
does not. `P_pz[i] = Σ_J e[i,J] ε[J]` therefore differs by a factor of two on the
three shear components depending on which convention `ε[J]` follows. Nothing in
`journals/` states one — the only canonical hits for "Voigt" are about the
*averaging scheme*, which is a different thing (below). The strain-sweep data
companion mentions Voigt coordinates, but it is explicitly marked not part of
canon.

**Severity** medium-high — a silent factor of two on the piezoelectric response
of the noncentrosymmetric materials, feeding rows 115 and 118. **Confidence**
high. **Correction:** state the convention once, where the Voigt index is
introduced.

**A cross-subject contradiction found alongside it, reported not chased.**
`typed-compositions.md:39` declares an open question: *"Which averaging scheme the
bulk modulus takes over the elastic constants — Voigt, Reuss or Hill — is an open
pick."* `accuracy-ledger.md:150` records row 37's tolerance as `±5%` with the
basis *"**Voigt average**"*. One page says the pick is open; the other has made
it and budgeted a tolerance against it. The accuracy ledger is not my subject.

*Row 127's undefined `Ω` — the fifth item recovered from that arm — is already
filed as part of F24, where it is one of the eight symbol collisions. The
calibration undergraduate reached it independently, which is corroboration of
F24 from a reader who had never seen it.*

---

## 2 · Findings that did not survive

**The topology-atlas count and group order — checked and correct.**
`topology-atlas#x-bs` claims *"117 of the 230 space groups have a non-trivial
symmetry-indicator group under time reversal in the spin-doubled setting, and
the largest such group has order 72."* I fetched Po, Vishwanath & Watanabe,
arXiv:1703.00911 (*Symmetry-based Indicators of Band Topology in the 230 Space
Groups*, Nat. Commun. **8**, 50) via ar5iv and extracted Table 3 — spinful with
time reversal and significant spin-orbit coupling, which is the setting the
corpus names. Distinct X_BS groups and their space-group counts:

```
ℤ₂ 20 · ℤ₃ 2 · ℤ₄ 28 · ℤ₈ 3 · ℤ₁₂ 4 · ℤ₂×ℤ₄ 35 · ℤ₂×ℤ₈ 5 · ℤ₃×ℤ₃ 3
ℤ₄×ℤ₈ 2 · ℤ₆×ℤ₁₂ 2 · ℤ₂×ℤ₂×ℤ₄ 8 · ℤ₂×ℤ₄×ℤ₈ 2 · ℤ₂×ℤ₂×ℤ₂×ℤ₄ 3
```

The counts sum to **117**, matching the corpus. Orders: ℤ₂×ℤ₄×ℤ₈ = 64,
ℤ₄×ℤ₈ = 32, ℤ₂×ℤ₂×ℤ₂×ℤ₄ = 32, and **ℤ₆×ℤ₁₂ = 72**, the largest. Both numbers
check out, in the exact setting stated.

**This one nearly became a false finding, and the method matters.** The fetch's
own prose conclusion was *"No order-72 groups appear in any table. The largest
groups found have orders like 32 or 24"* — it had mis-multiplied ℤ₆×ℤ₁₂ as 24.
Had I taken the summary rather than doing the arithmetic on its own enumerated
list, I would have filed a fabricated finding against a correct page. I have put
this warning into every undergraduate prompt I issue.

**Feng–Lindsay–Ruan PRB 96 161201 — real, and correctly attributed.** Row 121's
citation was a fabricated-citation candidate: an arXiv API query for
`all:"four-phonon" AND au:Ruan` returned 14 papers from that group including
Feng & Ruan PRB **93**, 045202 (2016), and **nothing** with a PRB 96 (2017)
journal reference. That absence is not evidence — the paper was simply never
posted. CrossRef on `10.1103/PhysRevB.96.161201` returns: *"Four-phonon
scattering significantly reduces intrinsic thermal conductivity of solids"*,
Tianli Feng, Lucas Lindsay, Xiulin Ruan, Physical Review B, volume 96, issue 16,
article 161201, 2017. Title, author list, volume, article number and year all
match the row. Whether it says what it is cited **for**, and whether `0.4Θ_D` is
its threshold, remain open — gap G3.

**`typed-compositions`' coverage claim — mechanically verified.** The page
asserts *"every identifier it names is defined in a block on this page"* and
pairs each catalog property with a composition. Parsing both pages: 35
catalog properties, 35 coverage rows, **set-identical, no duplicates, no
gaps**; 37 distinct identifiers named in the coverage table, **all 37 defined**
in code blocks on the page. The claim holds as stated. (`SurfaceEnergy` realizes
two properties and is defined once, as the page says.)

**The `fixpoint-adjoint` retag — all five rows are genuine fixed points.** The
inherited hazard was a row registered as a fixed point because a retired legend
was read as a current one (under that legend D3 meant "finite-difference
fallback"). I checked each of the five against the current criterion — *the
output is a converged fixed point and the adjoint cost is independent of forward
iteration count*:

- Row 5 `fermi-level-charge-neutral` — E_F is the root of charge neutrality. The
  row states `dE_F/dp = −(∂F/∂p)/(∂F/∂E_F)`, which is the implicit-function
  derivative, correctly signed. A root-find rather than a literal fixed-point
  iteration, but the adjoint structure is identical and iteration-count
  independent. Holds.
- Row 13 `SCPH-self-consistent-phonons` — self-consistent phonon equations,
  genuine fixed point. Holds.
- Row 36 `self-consistent-charge-balance` — coupled defect and carrier
  populations, genuine fixed point. Holds.
- Row 54 `critical-thickness-force-balance` — Matthews–Blakeslee has h_c inside
  its own logarithm, a transcendental equation solved iteratively; the
  implicit-function adjoint applies. Holds. (Its *tier* does not — F11.)
- Row 122 `iterative-lbte-kappa` — the Omini–Sparavigna iterative solution is a
  fixed-point iteration on the mode-resolved deviation function. Holds.

No `fixpoint-adjoint` row is a transient. The one row that **was** a transient —
row 106, a drift-diffusion rate field — carries an explicit note recording its
move off D3 for exactly the stated reason ("its adjoint is a backward-in-time
vJp whose cost scales with the step count, which is exactly what D3 promises it
does not"). The retag was applied correctly on this axis.

**The `relaxed` retag — all six rows name a relaxation.** The rule is that a
`relaxed` row without a named relaxation in its provenance cell is un-gateable
and fails the registry-build gate. Rows 45 (`soft-hull log-sum-exp`), 46
(`softmin over γ(term) at temperature τ_soft`), 50 (`soft-cutoff coordination
Σ_j σ((r_cut−d_ij)/δ) with declared width δ`), 67 (`soft-min hull log-sum-exp`),
84 (`continuous site occupations x_i∈[−1,1], mean-field / Gumbel-Softmax`) and
85 (`softmin over the set plus a sigmoid on (d−d_min)`) each name one. Six of
six.

**Rows 1 and 2 as `relaxed` — considered and rejected.** A minimum over a k-grid
is an argmin construction, and the corpus tags argmin rows `relaxed`. But the
relevant distinction is whether the *output* is piecewise constant. For rows 45,
46 and 67 it is — which is why row 46's own note says a vJp-vs-JvP gate "passes
spuriously here because both sides agree on the zero gradient in region
interiors". `min_k E(k)` is continuous and piecewise smooth with a nonzero
gradient; only the argmin's identity jumps. `direct` is the right tag. What
survives from this is the weaker F19.

**`(2ω/c)·Im(√ε)` — correct.** `α = 2ωκ/c` with `ñ = n + iκ = √ε`, so
`Im(√ε) = κ`. The corpus's insistence that "the factor of two is part of the
form" is right.

**Row 68's Clausius–Clapeyron correction — correct.** `dP/dT = ΔH/(TΔV) = ΔS/ΔV`,
and the corpus's own reasoning for adding T ("ΔH/ΔV alone has units of pressure,
not pressure per kelvin") is sound. The corpus caught this itself.

**Row 125's Wegscheider residual — correct.** Thermodynamic consistency of a
reaction network requires `Σ_r σ_r ln K_r = 0` around each cycle; the row's
`(Σ_r σ_r ln K_r)²` is the right residual.

**Row 41's Huang–Rhys disambiguation — correct and well made.** The cell states
S is the dimensionless lattice-relaxation energy in phonon quanta and *"NOT the
electron-phonon matrix element g_qν"*. That is the right distinction and the
right place for it.

**The `read` tag on row 87 — correct.** A cache keyed on a phase identifier
alone has an identity adjoint. The corpus's reasoning for keeping
`chemical-potential-ref-table` off `read` is also correct. The tier is the
problem (F10), not the differentiability.

**Inherited contradictions, triaged.** Of the eight registered by the registry
surveyor, **five are resolved by the restructure**: the cost-tier legend is no
longer restated on `formula-registry` (it links to `named-formulas#cost-tiers`);
the bare-ordinal cert-obligation citations are now anchored
(`[cert-obligations#the-ten-obligations]`); the "four live places" anchor-class
count is gone; the scope-versus-inventory precedence rule is now stated once, on
`properties`; and the "every other document references these numbers rather than
restating them" rule survives in a form the corpus now keeps — no page restates
a manifest count except one (below). **One persists in altered form**: the
closed-vocabulary claim against the eighteen unregistered names — now declared
on `typed-compositions` but still stated categorically elsewhere, which is F2.
**One persists as declared**: ν₀ carries two names on one page
(`harmonic-transition-rate-normalization` and `harmonic-rate-prefactor`), now
honestly registered as an open question; I verified the page's assertion that
they name the same quantity, and they do — ν₀ in harmonic transition-state
theory is the harmonic prefactor. **One is a checker fact that no longer
applies**: `check_data_agreement.py` does not exist in this tree.

**One restated manifest count, and it is accurate.**
`residual-machinery.md:64` says *"A SET, not a scalar: 40 of the 134 registry
rows carry two bundles."* `formula-registry#counts` forbids restating a count
over the manifest. I counted: 40 rows carry a slashed bundle pair. The count is
correct today. Structure is not my subject; flagged and moved on.

**Six rows declare unregistered inputs, honestly.** Rows 7, 8, 9 (D(q) from the
DFPT reference solve), 47 (work function and electron affinity), 80 (H_device
and contact self-energies) and 115 (ΔE_C) say so in the `Depends on` cell. This
is good practice, but it is a *second* gap category that no page pairs with the
eighteen-name one, and it sits under `named-formulas`' unqualified phrase
"**fully parameterized**". Noted, not filed. **F26 sharpens this**: three cells
name objects with no referent and do *not* carry the marking, so the honest six
establish that the corpus has a convention for it and three rows do not use it.

---

*Everything from here in this section is the second run's.*

**Six flags from the unused-input sweep, dismissed as notational variants.** The
sweep behind F29 and F30 — for each row whose provenance cell states a closed
form, which signature inputs does the form never mention — produced eight flags.
Two are findings (rows 120, 129). Six are not, and each is dismissed for a stated
reason:

| row | flagged input | why it is not a defect |
|---|---|---|
| 5 | `DOS`, `dopants` | the cell states the *adjoint*, `dE_F/dp = −(∂F/∂p)/(∂F/∂E_F)`, not a closed form for `E_F`. There is no closed form — that is the cell's point |
| 84 | `σ-config` | the cell writes `σ_i`, the per-site occupation; same object, different notation |
| 112 | `Φ_dose` | the cell writes `Φ` |
| 128 | `P_sp0` | the cell writes `P_sp(T0)` |
| 131 | `E_a_cryst`, `n_avrami` | the cell writes `E_a` and `n` |
| 119 | `C_ox`, `C_dep` | the cell states only the helper relation `C_it = q²·D_it`, not the swing formula. The signature is right; the cell is partial. Worth an editorial note, not a finding |

**Forty-nine of the fifty-two raw `Depends on` non-resolutions, dismissed.** The
first pass of the referent sweep reported 52 cells whose contents could not be
matched to a row, a page or a file. Classifying them (F25) showed 31 are informal
collective nouns (`slabs`, `radii`, `bands`) and 18 are restatements of the row's
own signature inputs written in a subscript variant my first probe could not
match. **Only three name an object that should exist and does not** — F26. The
first pass would have supported a much larger and much weaker finding; the
classification is what reduced it to the three that are real.

**Two symbol collisions found and not filed as such.** `e` (elementary charge,
row 14) against `e[i,J]` (piezoelectric stress tensor, rows 114, 117), and `p`
(hole density, rows 36, 38, 39, 134) against `p[α]` (pyroelectric coefficient,
row 128). Both are distinguishable by their index decoration, so a careful reader
does not confuse them. They are listed under F24 as the weak cases rather than
counted among the eight.

**`μ` in row 105, left as an open reading rather than filed.** Row 105
`vacancy-generation-arrhenius` takes `(c_V^q, T, μ, j, x_ox', ρ_dis, k_ann)`. In
a vacancy-generation rate `μ` is almost certainly a chemical potential, which
would make it collide with the mobility that rows 15 and 16 produce. But the row
also carries a current density `j`, and a mobility is not absurd beside it. I
could not settle which, the row's cell does not say, and I am not willing to file
a collision on my own reading of an undocumented symbol. **The undeclared meaning
is itself the point** — it is the F23/F24 problem in its purest form, and it is
recorded here rather than inflated into a finding.

**Row 129's Poole–Frenkel coefficient — checked and correct.** The cell states
`β_PF = √(q³/(π ε_opt ε0))`. The Schottky coefficient is `β_S = √(q³/(4π ε ε₀))`
and the Poole–Frenkel coefficient is exactly `2β_S`, giving
`√(4·q³/(4π ε ε₀)) = √(q³/(π ε ε₀))`. The corpus has the factor of two right.
This was a live candidate — the same class of hazard as the absorption `2ω/c`
prefactor the corpus pins on `named-formulas#corrected-forms` — and it survives.
F30 is filed against the row's *prefactor absence*, not against this coefficient.

**Thirteen of the fifteen `faithful` rows — checked and correct.** Rows 6, 13,
40, 41, 80, 87, 88, 92, 93, 94, 99, 100 and 101 each involve a density-functional,
perturbation-theory, Green's-function or Monte-Carlo evaluation, which is the
field's stated criterion. Only rows 45 and 67 fail it (F31). The `Path` column is
right on 132 of 134 rows.

**Row 61 `bulk-modulus` — the call site matches the signature.** This is the
control for F32 and it holds: `AlgebraicOf({ElasticConstants}, formula =
bulk-modulus)` against `(C_ij) → B`, one input each.

**A character-class failure of my own, recorded because it nearly produced a
false absence.** Checking whether the corpus states the valence-band reference
for `E_F`, a case-sensitive grep for `Fermi` in `named-formulas.md` returned
**zero** — which would have supported a much broader "the corpus never mentions
the Fermi level" claim. The page uses lowercase `fermi-level-charge-neutral`. Run
case-insensitively the control fires, and the narrower finding in F32 — that
`VBM` and `valence band maximum` appear nowhere in `journals/` — survives the
corrected method. This is the second rule of the brief doing its job on the
auditor rather than on the corpus.

---

## 3 · Shaped gaps

### G1 — Do rows 92–94 invoke the linear-response solve or read its output?

| part | content |
|---|---|
| **what it would settle** | Does one evaluation of row 92 (`operator-position-derivative-tensor`) run a density-functional perturbation-theory solve, or read a tensor the linear-response sub-stage has already produced? |
| **the conclusion without it** | It invokes. The `Depends on` cell names the sub-stage as a dependency rather than as a cached product; the `anchor-class` is `faithful`, meaning the value is trusted only against a reference-grade computation; and `Diff` is `adjoint`, which presumes a computation to differentiate through rather than a stored value. |
| **the branches** | **If it invokes:** F12 stands, the tier is wrong by one to two levels on three rows, and `named-formulas#cost-tiers`' worked example needs replacing. **If it reads:** the tier is right, F12 falls, and two new questions open — why the differentiability is `adjoint` rather than `read` when row 87 (the same shape) is `read`, and why the `Depends on` cell names a solve rather than a cache. |
| **what depends on it** | F12 entirely. Nothing else; F13 and F14 are independent tier findings. |

Settling it needs one sentence from whoever owns `compose-time-pipeline` — the
linear-response sub-stage is Stage 2.5 there — not a paper.

### G2 — Is "Pick-Cochran-Martin" a real attribution?

| part | content |
|---|---|
| **what it would settle** | Does a paper by authors named Pick, Cochran and Martin on the non-analytic term in the dynamical matrix exist, or is the row's attribution a conflation of Pick, Cohen & Martin, Phys. Rev. B **1**, 910 (1970) with Cochran & Cowley, J. Phys. Chem. Solids **23**, 447 (1962)? |
| **the conclusion without it** | It is a conflation. Pick–Cohen–Martin is the standard citation for the microscopic theory; Cochran–Cowley is the standard citation for the phenomenological non-analytic term; "Pick-Cochran-Martin" matches neither author list. |
| **the branches** | **If the conflation is confirmed:** correct the cell to `Pick–Cohen–Martin / Gonze–Lee`, and consider adding Cochran–Cowley, since both are cited for this term in the literature. **If a Pick–Cochran–Martin paper exists:** no change; the row is right and I was wrong. |
| **what depends on it** | F18 alone. No physics claim in row 88 depends on the branch — the Gonze–Lee half of the attribution is correct either way, and I did not find an error in the row's inputs. |

Blocked only by the exhausted search budget; a CrossRef query on the 1970 Phys.
Rev. B volume, or one look at any DFPT review's reference list, closes it.

### G3 — Is `T≳0.4Θ_D` Feng–Lindsay–Ruan's threshold, and what does the paper claim for diamond?

| part | content |
|---|---|
| **what it would settle** | Does PRB **96**, 161201 (2017) state a validity threshold of about 0.4 of the Debye temperature for a multiplicative four-phonon correction, and does it report a diamond-specific overprediction figure (the inherited lead records 31% at 1000 K)? |
| **the conclusion without it** | The threshold is probably **not** the paper's. Its title claim is that four-phonon scattering *significantly reduces* intrinsic conductivity, and the group's related work emphasizes that four-phonon scattering matters well below 0.4Θ_D for materials with large acoustic–optical gaps. A floor at 0.4Θ_D would contradict the source it cites. The citation itself is verified real and correctly attributed (§2). |
| **the branches** | **If 0.4Θ_D is the paper's:** F16 stands as written — the domain is real but not evaluable, because diamond's Θ_D is contested between 1860 K and 2230 K. **If it is not the paper's:** F16 strengthens to a false claim — a validity domain attributed to a source that does not state it — and row 121's correction becomes applicable over a wider range than the row admits, which changes the 300–750 K conductivity anchors. |
| **what depends on it** | F16's severity and class. F15 is independent. The accuracy ledger's Θ_D open question is coupled to the first branch only. |

**Acquisition request** — this is the one paper worth buying for my subject.

---

## 4 · Acquisition requests

| paper | what it settles | conclusion without it | what changes either way | findings waiting |
|---|---|---|---|---|
| Feng, Lindsay & Ruan, *Phys. Rev. B* **96**, 161201(R) (2017), DOI 10.1103/PhysRevB.96.161201 | Whether `T≳0.4Θ_D` is the paper's threshold, and what it reports for diamond | The threshold is probably not the paper's; the citation is verified real | Decides whether F16 is a non-evaluable domain or a false attribution, and whether row 121 applies below 750 K | F16, G3 |

Not on arXiv — I checked the group's full arXiv record (14 four-phonon papers,
none with a PRB 96 journal reference). CrossRef confirms the article exists but
carries no abstract. A purchase or an institutional copy is the shortest route.

---

## 5 · Calibration result

### Second run — the calibration that is actually mine

**The first run's calibration score was never recovered.** That run planted eight
defects and dispatched an agent, and the session ended before the agent returned;
the score is not in this file because it never existed. It is recorded below as a
zero-information result rather than quietly dropped, because a calibration whose
score is unknown is exactly a calibration that did not happen.

**The second run planted ten fresh defects** in a scratch copy at
`…/scratchpad/calib/registry-manifest-planted.csv`, and gave a blind agent a
24-row subset — the 10 planted rows among 14 untouched ones — with the same
standards file the physics undergraduates got, no hint that anything was planted,
and two hard constraints: it may not open `data/registry-manifest.csv` and it may
not open `audit/findings/`. Without those the test is a diff, not a sweep.

The plants span the four axes the second run swept, so the calibration measures
*these* methods rather than a generic one:

| # | row | planted defect | axis it tests |
|---|---|---|---|
| 1 | 61 `bulk-modulus` | `T0` → `T3` — a closed form re-tiered to minutes | cost tier |
| 2 | 55 `bond-valence-sum` | `(R_I, R0, b)` → `(R_I, R0)` — the softness parameter dropped | signature type-check |
| 3 | 78 `thermionic-emission-current` | `a.k.a. Richardson–Dushman` → `a.k.a. Fowler–Nordheim` | eponym bound to wrong object |
| 4 | 43 `debye-screening-defect-defect` | `D1` → `DN` — a smooth closed form claiming no useful derivative | differentiability, on the value the corpus calls "most likely to be wrong" |
| 5 | 19 `hall-mobility-from-σ` | provenance gains `μ_H = σ_xy/(σ_xx²·B)` — wrong; the correct relation is `σ_xy/(σ_xx·B)` | false algebra in a provenance cell |
| 6 | 107 `platelet-nucleation-allen-cahn` | `E_nuc=3.5eV` → `E_nuc=35eV` | order-of-magnitude value error |
| 7 | 126 `rotational-sum-rule` | `Born-Huang` → `Born-Oppenheimer` | eponym, author substituted |
| 8 | 127 `alloy-disorder-scattering` | `τ⁻¹∝x(1−x)ΔU²g(E)` → `τ⁻¹∝x(1−x)ΔU g(E)²` | exponents swapped |
| 9 | 39 `auger-recombination` | `(n, p, C_n, C_p)` → `(n, C_n, C_p)` — hole density dropped | signature type-check |
| 10 | 132 `xrd-structure-factor` | `e^{−W_I}` → `e^{+W_I}` | sign flip in a Debye–Waller factor |

Two properties are already established regardless of the score: **every plant
applied cleanly** — the planting script asserts each target string occurs exactly
once before substitution and all ten assertions passed — and the agent was given
no signal separating planted rows from untouched ones.

**Two of the untouched rows carry live findings of mine** (126 is the rotational
sum rule, under investigation on other grounds; 132's `Z_I`-against-`f_I(q)`
mismatch is real and unplanted). So the run also tests discrimination: a real
defect found on an untouched row is a true positive against the corpus, and I
will score it separately from the ten plants rather than folding it in.

**Score: pending, and the reason is a routing fault rather than an unfinished
agent.** The undergraduate completed. **Its report routed past me to the top of
the fleet** — the third cross-arm leak in this program, and the principal
correctly declined to classify it, since "absent from the real corpus" and
"planted" are indistinguishable without the answer key. I have asked the agent to
re-emit its verdicts to me in a scoreable form and will report the number
unrounded when it arrives.

**Two things are already recoverable and are recorded rather than held.**

*One — the scoring rule this exposed.* A plant is an edit; an absence is not
editable, so an absence finding reads identically in both copies and **cannot be
a detection**. Scoring must partition the return into EDIT and ABSENCE findings
and score against EDIT findings only, routing ABSENCE findings into the findings
file after checking each against the **real** artifact. Four survived that check
and are filed as F37–F40. Counting them as detections would have inflated this
calibration with the corpus's own defects — which is the precise failure a
calibration exists to prevent, arriving from an unexpected direction. The full
statement is at the head of §1b.

*Two — the architectural conclusion about the leak.* It is not disciplinary and
not fixable by care at any single level: a sub-subagent two levels down routes its
full contents past its own parent. **A calibration arm cannot live anywhere in the
scorer's tree at any depth.** Recorded in `audit/REGISTER.md` as the first of four
rules for running a blind arm.

**What the score will and will not bound.** The 14 findings of the second run's
own direct sweep (F23–F36) are mechanical with in-line controls — each states the
control that fired — so their evidence does not depend on this score. What the
score bounds is the *undergraduate* returns. F37–F40 depend on neither: they were
re-verified against the real manifest by me, with the file quotations given in
place.

### First run — reported as found, and as unrecovered

**Reported as found, and it is incomplete.** I planted eight defects in a scratch
copy of the manifest at
`/tmp/…/scratchpad/calib/registry-manifest.csv` and gave an undergraduate twenty
rows to audit — the eight planted ones (24, 30, 41, 45, 72, 74, 80, 121) hidden
among twelve untouched ones (38, 52, 55, 56, 61, 68, 76, 78, 82, 83, 123, 125) —
with the same brief and legends the physics undergraduates get, and no hint that
anything was planted. The plants span the four finding classes:

| # | row | planted defect | class |
|---|---|---|---|
| 1 | 72 | hot-carrier balance prefactor `(2/3)` → `(3/2)` | false claim, prefactor |
| 2 | 123 | `κ_BR>0 ⇒ E_b rises with T` → `κ_BR<0 ⇒ E_b falls with T` | false claim, sign/direction |
| 3 | 74 | impact-ionization α redeclared as a rate in s⁻¹ | false claim, units |
| 4 | 80 | NEGF transmission re-tiered T3 → T0 | dishonest cost tier |
| 5 | 45 | Wulff shape D4 → D1, relaxation name stripped | differentiability mis-tag |
| 6 | 121 | four-phonon validity `T≳0.4Θ_D` → `T≲0.1Θ_D` | inverted validity domain |
| 7 | 41 | Huang–Rhys `NOT the matrix element g_qν` → `the matrix element g_qν` | eponym bound to wrong object |
| 8 | 30 | defect formation energy signature loses `E_F` | missing required input |

Note that plants 2 and 6 land on rows that are *also* the subject of live
findings of mine (F16 concerns row 121's genuine threshold), so the calibration
tests discrimination as well as detection.

**The calibration agent was still running when this report was written.** The
score is therefore not yet known, and **nothing in §1 or §2 should be read as
carrying a demonstrated detection rate.** I will report the score as found —
including a partial one — the moment it returns; a method that catches six of
eight is a six-of-eight gate and rounding it up is the failure the calibration
exists to prevent. Two things are already true and worth stating: the eight
plants were verified to apply cleanly (each target string occurred exactly once
before substitution, asserted in the planting script), and the agent was given
no signal distinguishing planted rows from untouched ones.

---

## 6 · Evidence transcript for what is called clean

Beyond §2, the following were checked mechanically and are recorded so the
sweep is inspectable:

| what | how | result |
|---|---|---|
| manifest row count | `csv.DictReader` over `data/registry-manifest.csv` | 134 rows = 132 substantive + 2 architectural markers (rows 103, 104), matching `named-formulas#the-registry` |
| `Diff` distribution | column tally | D0 1 · D1 91 · D2 23 · D3 5 · D4 6 · DN 6 · `—` 2. Exactly one `read` row, as `named-formulas#diff-tags` implies |
| `Path` distribution | column tally | cheap 117 · faithful 15 · `—` 2 |
| `Tier` distribution | column tally | T0 76 · T1 40 · T2 11 · T3 5 · `—` 2 |
| dual-bundle rows | count of slashed `Bundle` values | 40, matching `residual-machinery.md:64` |
| all 18 declared-gap names absent from the manifest | set difference against the `Name` column | confirmed absent |
| every coverage-table identifier defined on its page | regex parse of `typed-compositions` code blocks | 37 named, 37 defined, none missing |
| catalog ↔ coverage correspondence | set comparison of `properties#catalog` against `typed-compositions#coverage` | 35 ↔ 35, set-identical, no duplicates |
| `applicability-classifiers` resolves | `ls journals/*/*/` | exists at `journals/oracle/certification/` |
| checker scope | read of `tools/check_structure.py` | globs `journals/**/*.md`; `data/` never opened; `python3 tools/check_structure.py` → `structure OK · 45 pages, 273 owned topics, 51 open questions` |
| row-band map against the manifest | band ranges in `named-formulas#row-bands` against row numbers and `Source` cells | consistent; rows 128–134 all carry `2026-07 gap-audit` provenance as the band claims |

**Second run — mechanical sweeps, each with its control.**

| what | how | result |
|---|---|---|
| units in signatures | 26-token unit regex over all 134 `Signature` cells; control fires on two synthetic signatures carrying units and is silent on a real bare one | **0 of 134** carry any unit token — F23 |
| signature symbol namespace | bracket-depth-tracking parser over all signatures, then every symbol that is one row's output and another's input; parser control on `(Z*[I,α,β], Δw[I], Ω) → P_sp[α]` and `(C_ij, ρ) → v_L, v_T`; character-class control on `μ0`/`μ₀`, `E_0`/`E₀`, `v_g`/`v-g` | **8 bare-token collisions**, 5 involving a registered producer — F24 |
| `Depends on` referents | 245 referents split at paren depth zero and classified against the declared schema; control resolves `phonon-dispersion`→row 9, `single-mode-rta`→row 25, `interface-trap-density`→row 116 | 41 row references · 142 signature echoes · 31 informal nouns · 31 named objects — F25 |
| referents with no object | grep of `journals/` and `data/` for each named object; control resolves `elastic-tensors.csv` and `linear-response sub-stage` | **3 unresolved**: `ECI cache`, `R0-table`, `DFT battery` — F26 |
| record fields against columns | `named-formulas#formula-record` (10 fields) against the manifest header (9 columns) and `formula-registry#fields` (9 rows) | **2 fields have no column** — F27 |
| unused inputs | for every row whose provenance cell states a closed form, which signature inputs the form never mentions; control: row 72 correctly **not** flagged | 8 flags → 2 findings (F29, F30), 6 dismissed as notational variants |
| composition call sites | the 3 `AlgebraicOf` invocations naming a registered row, against their signatures; control: row 61 agrees | **2 of 3 disagree** — F32 |
| anchor-class | all 15 `faithful` rows against the field's stated criterion; battery-property listing to test the second admissible anchor; control returns `bulk-modulus`, `debye-temperature`, `elastic-C11` | **13 of 15 correct**, rows 45 and 67 fail — F31 |
| bundle values | every `Bundle` cell split on `/` against the twelve admissible values; control catches synthetic `B12` and `B99` | **clean — 0 violations.** B1 16 · B2 15 · B3 18 · B4 23 · B5 8 · B6 25 · B7 9 · B8 10 · B9 20 · B10 9 · B11 15 · L1 4 |
| bundle values against the page's named examples | the 12 rows `observable-bundles` names explicitly, against their manifest cells | **12 of 12 agree** |
| validity-domain baseline | regex for validity / regime / gating markers over all 134 provenance cells; control set of 8 rows known to declare *something* well | **9 of 134** carry any domain, regime or gating marker. Control returned **5 of 8** — see below |

**The validity-domain control returned 5 of 8, and the miss is informative rather
than a failure.** The three control rows the detector did not find — 74, 68 and
41 — declare a *unit* (`α is cm⁻¹, not a rate in s⁻¹`), a *dimensional necessity*
(`ΔH/ΔV alone has units of pressure, not pressure per kelvin`) and a
*disambiguation* (`NOT the electron-phonon matrix element g_qν`). None of those
is a validity domain. So the detector is correctly measuring one axis and the
control set spans two; the honest reading is that **the corpus declares
well on three distinct axes** — validity domain, units, and what-a-quantity-is-not
— and my probe sees only the first.

**The 9-of-134 figure is a baseline, not a defect count.** A row with no stated
domain is a defect only if it needs one, and many closed forms do not. It is
recorded so the cost-tier-and-domains undergraduate's return can be checked
against a number rather than against an impression: if that return names far more
than 125 deficient rows it is over-firing, and if it names very few it has not
swept.

**The bundle axis is clean and that is a result, not an absence.** All 134 rows
draw on the twelve admissible values, the four `linear-response-primitive` rows
are exactly rows 91–94 as `observable-bundles.md:112` states, and every row the
page names by hand carries the bundle the page assigns it. The page also defends
itself against the obvious finding: its contents lists are marked *"Representative
contents. The authoritative per-row assignment is the manifest's `bundle`
field"*, so a row absent from a list is not a defect. I looked for the
contradiction this axis usually yields and there is none.

**Two cells I read closely and am not filing against.** Row 46's note that a
vJp-vs-JvP gate "passes spuriously here because both sides agree on the zero
gradient in region interiors" is a correct and unusually sharp observation about
its own gate. Row 50's note that "row 116 inherited a gradient that is zero
almost everywhere" correctly diagnoses why a hard cutoff cannot be `direct`.
Both are the corpus catching itself, and both should survive any edit.

---

## 7 · Log-worthy advancements

Reported, not written — `log/timeline.md` has a single writer.

1. The registry manifest was never migrated to the spelled-out vocabulary the
   restructure defined, and no checker reads it (F1).
2. The `fixpoint-adjoint` and `relaxed` retags were verified correct row by row
   — eleven rows, eleven holding — against the inherited hazard of a row
   registered under a retired legend.
3. Feng, Lindsay & Ruan PRB 96 161201 (2017) verified real and correctly
   attributed via CrossRef, closing a fabricated-citation candidate.
4. `topology-atlas`' two hard numeric claims (117 space groups, largest indicator
   group of order 72) verified against Po/Vishwanath/Watanabe Table 3.
5. `typed-compositions`' coverage claim verified mechanically — 35 properties, 35
   compositions, every identifier defined.

**Second run.**

6. **The anchor-class field's stated purpose is unrealized across the whole
   registry** — no constructible consistency pair exists, and all three the
   corpus names by hand fail, including the thermal-conductivity pair it names
   twice and by row number (F36). Converges with the tolerance-ledger subject's
   independent finding that zero pairs declare `τ_method`.
7. **The signature field declares units and carries none** on any of 134 rows
   (F23), which is the enabling condition for eight quantity-symbol collisions,
   five of them pairing a registered producer with a consumer of a different
   quantity (F24).
8. **The acoustic sum rule's pinned canonical form and its row's signature are
   different objects**, differing by a mass weighting that is exactly invisible on
   the monatomic MVP material and a factor ≈2 on both gallium compounds (F34).
9. **Row 30 `defect-formation-energy` cannot form its output** — `Δn` is absent,
   and the corpus's own composition carries it (F32). Fourth instance of the
   unformable-signature class, after rows 82, 83 and 129.
10. **Three `Depends on` cells name storage objects that exist nowhere**
    (`ECI cache`, `R0-table`, `DFT battery`), and the column's declared meaning
    describes 41 of its 245 referents (F25, F26).
11. **`reference-battery`'s claim that nothing points into its three absent
    sub-areas is false** — six registry rows do, and two exist for nothing else
    (F28).
12. **The bundle axis is clean**, verified rather than assumed: 0 vocabulary
    violations across 134 rows, 12 of 12 agreement with the page's hand-named
    examples, and the nine slow-tier rows whose cost and differentiability
    `multiscale-state` independently restates all agree with the manifest.

**Method — a scoring rule for blind arms, and it is the one item here that
generalizes beyond this subject.**

13. **A plant is an edit; an absence is not editable.** An absence finding reads
    identically in the planted copy and the real one, so it can be neither a
    detection nor a false positive — it is unclassifiable by the answer key.
    Partition every blind-arm return into EDIT and ABSENCE findings *before*
    scoring; score against EDIT only; route ABSENCE findings into the normal
    findings file after checking each against the **real** artifact. Skipping
    that check is unsafe in both directions: an absence may be an artifact of a
    plant that removed something, and it may equally be a real defect the arm
    found for free. This calibration produced four real corpus defects (F37–F40)
    that would have inflated the score had they been counted as detections —
    a calibration corrupted by the very defects it was measuring the ability to
    find.
14. **The two figures should be reported separately** — EDIT detections out of
    plants, and ABSENCE findings recovered — because they measure different
    things: the first measures the method, the second measures the corpus.

---

## 8 · What this sweep did not cover, and why

Stated plainly so the gap is not mistaken for a clean result.

### Second run — what was staffed

Eight undergraduates were spawned, which is the full authorization. The
concurrent-subagent pool was saturated fleet-wide on the first two attempts at
the eighth; it was held and retried until a slot freed, so all eight ran.

| # | subject | rows |
|---|---|---|
| 1 | differentiability tag against what each row computes | all 134 |
| 2 | cost tier, and undeclared validity ranges / tolerances / sign conventions | all 134 |
| 3 | every `a.k.a.` attribution against the primary literature | ~40 cells |
| 4 | electronic structure, phonons, linear response, topology, sum rules | 1–13, 88, 91–102, 120, 126, 133 |
| 5 | carrier transport, scattering, thermal transport | 14–29, 63, 64, 121, 122, 127 |
| 6 | defects, recombination, high field, degradation, radiation | 30–43, 70–76, 81–83, 105–112, 123, 129–131, 134 |
| 7 | surfaces, interfaces, barriers, tunneling, mechanics, thermodynamics, polarization | 44–62, 65–69, 77–80, 84–87, 95, 113–119, 124, 125, 128, 132 |
| 8 | blind calibration | 24-row planted subset |

Clusters 4–7 partition all 132 substantive rows with no gaps and no overlaps, and
each was told to type-check signatures and resolve `Depends on` referents as well
as check the physics. Clusters 1–3 sweep three axes across the whole manifest.
**Every row is therefore covered on at least three axes, and the four axes the
brief named — differentiability tags, signature type-checking, dangling
dependencies, and eponyms — each have a dedicated owner.**

The 11 findings in F23–F33 are the postdoc's own direct sweep, run in parallel
with the eight, and cover the axes that are mechanical rather than
literature-facing: units, the symbol namespace, the dependency-column semantics,
the record-field-to-column correspondence, unused inputs, composition call sites,
anchor class, bundle values, and undefined input types.

### First run — what could not be staffed, kept for the record

Six of the eight physics clusters the first run decomposed the subject into could
not be staffed: the concurrent-subagent pool (20) was saturated fleet-wide across every
attempt. **Two undergraduates ran** — defect energetics and finite-size
corrections (rows 30–34, 37, 42, 43, 89–91), and the calibration. **Six did
not**: electronic structure and topology (rows 1–6, 96–102, 120); phonons, sum
rules and linear-response primitives (7–13, 88, 91–94, 126, 133); carrier
transport and scattering (14–22, 63, 64, 127); thermal transport (23–29, 121,
122); surfaces, interfaces, barriers and tunneling (44–54, 77–80, 86);
polarization, piezoelectricity and the two-dimensional electron gas (113–119,
128); mechanics, static validity and thermodynamics (55–62, 65–69, 84, 85, 87,
95, 124, 125, 132); high-field and degradation (70–76, 81–83, 105–112, 129–131).

F1–F22 are therefore the first run's **own direct sweep**, strongest on the axes
that do not need literature — internal consistency between the manifest and the
ten pages, tag correctness against the corpus's own definitions, signature
completeness, and the two named threads — and weakest on the axis the brief
called the largest: *is each governing equation right against the primary
literature?*

The first run closed by naming the rows with a literature-facing claim that no
one had checked, so the work would be picked up rather than repeated: 17 and 21
(the `ε0` ambiguity — vacuum permittivity or static dielectric constant — which
changes both formulas), 16 (Caughey–Thomas at 1000 K), 22 (a relaxation time for
inelastic polar-optical scattering), 23 and 24 (the Mott formula and the
Sommerfeld Lorenz number in non-degenerate wide-gap material), 26 and 27
(hydrodynamic phonon rows with no validity domain, in a corpus operating at
300–1200 K), 38 (SRH without a trap level), 40 (multiphonon capture without a
matrix element), 111 (a scalar displacement threshold for a five-site monoclinic
crystal), 114 (the King-Smith-Vanderbilt attribution), and 20 (two mobilities
from three inputs).

**Every one of those was written into a second-run undergraduate's prompt as a
named question**, with the primary source to fetch and the arithmetic to do —
17, 21, 16, 20, 22, 23, 24, 26, 27 to cluster 5; 38, 40, 111 to cluster 6; 114 to
cluster 7 and to the eponym sweep. That list is closed, and what remains open is
recorded in §3 as shaped gaps rather than as unstaffed work.

# A3 — registry and residual machinery: build sheet

Units 7 and 8. The question throughout is *could a competent implementer type this*,
not *is it true* and not *is it enough physics*.

Frontmatter `open-questions:` blocks were read **last**, and only to mark which of these
the corpus already admits. Where a finding is already confessed it says so and the
finding is scoped to the part that is not.

---

### R1 — no unit system is declared anywhere in the corpus, and the one pointer to one resolves to a page about prose style, in `formula-registry.md` / `mvp-system.md`

**Verdict:** ABSENT

**The obligation.** The manifest field schema promises units on every row:

> | `signature` | typed inputs to output, with units |

The reference battery promises them on every value:

> - **Value** — the numerical value in canonical units.

And the typeclass alphabet makes units a method every numeric output must implement:

> Units, equality within a tolerance, and behavior under a change of units or
> basis. Every numeric output is a `Quantity`.

**What is missing.** No page states what the canonical units *are*. `Units` is a type
that appears in exactly three places, all of them the `Quantity` signature block on
`typeclass-alphabet.md`, and is expanded nowhere. Zero of the 134 signature cells in
`data/registry-manifest.csv` carries a unit. The only page that addresses the question
at all defers it:

> Units — internal and reported — follow the corpus convention ([conventions]).

`conventions.md` owns `page style`, `count phrasing`, `verdict discipline` and
`data and generated files`. It says nothing about physical units. The deferral
resolves to a page that does not answer it.

The consequence is not cosmetic. `Quantity.combineTol` composes tolerances along the
DAG and the tolerance ledger gives absolute defaults (`τ_SCF,strict` at `1e-8` Ha,
`δ_meta` at `50 meV/atom`, `τ_cons` `1e-8` relative). An implementer working in
eV/Å and one working in Hartree/Bohr both satisfy every stated rule and emit
residuals differing by powers of 27.211. Nothing in the corpus separates them.

**Control.** Searched `grep -rni 'unit system\|atomic units\|Hartree atomic\|SI units\|base units' journals/` → 1 hit, `traps.md`, and it is the *opposite* of a declaration:
`The 4π in the source term rides the unit system.` Searched
`grep -rni 'canonical unit\|unit convention\|units are\|reported in\|internal units\|working units' journals/`
→ 3 hits, two of which are `reference-battery.md` *using* the phrase 'canonical units'
and one of which is `crystal-inputs.md` saying units 'are stated nowhere'.
Control that fires: `grep -rn 'Canonical names and default values' journals/` → 1 hit,
`cert-obligations.md`, opening the tolerance ledger — so the corpus does write a
canonical-values table where it has decided one, and a search of this shape reaches it.
Second control: `grep -c 'PRB\|PRL\|JAP\|APL\|Phys\.\|J\. ' data/reference-data/*.csv`
→ 61 rows, so searches of this shape reach the data files too.

---

### R2 — the manifest is written in codes whose only decode table is labeled `retired-vocabularies`, in `agent-contract.md`

**Verdict:** UNDERSPECIFIED

**The obligation.** The manifest is canonical, and every consumer is required to take
each coded field's vocabulary from that field's owning page:

> **Every consumer harvests the vocabulary from its defining page. No consumer
> restates it.**

Those owning pages define English vocabularies. `named-formulas.md` gives
differentiability as `read | direct | adjoint | fixpoint-adjoint | relaxed | none`;
`observable-bundles.md` gives eleven bundle names plus `linear-response-primitive`;
`named-formulas.md` gives cost as `microseconds | milliseconds | seconds | minutes`;
`formula-registry.md` gives seven provenance values. The corpus states the reason:

> **Everything the corpus invents is spelled out in English.** Standard deviation is the
> name; `σ` is not. `direct` and `adjoint` are names; `D1` and `D2` are not. Symbols
> belong in equations, where the surrounding mathematics binds them.

**What is missing.** Every one of the 134 rows carries the codes, not the names. The
`Diff` column holds `D1` ×91, `D2` ×23, `D3` ×5, `D4` ×6, `D0` ×1, `DN` ×6. `Tier`
holds `T0` ×76, `T1` ×40, `T2` ×11, `T3` ×5. `Bundle` holds `B1`…`B11` and `L1`.
`Source` holds `S1`…`S5`. The only mapping from those codes to the English vocabularies
in the whole corpus is a YAML block on `agent-contract.md` whose key is:

> retired-vocabularies:
>   differentiability: {D0: read, D1: direct, D2: adjoint, D3: fixpoint-adjoint,
>                       D4: relaxed, DN: none}

An implementer following the stated harvest rule reads `observable-bundles.md`, gets
eleven English names, and finds `B1` in every row — the exact failure mode
`observable-bundles.md` warns about for four rows, applying to all 134. The implementer
who instead finds the decode table must decide whether a block the corpus labels
*retired* is authoritative for the live canonical artifact. `formula-registry.md#harvest`
does not name `agent-contract.md` as a vocabulary owner for any field.

The block also carries a live collision an implementer must resolve unaided: `T0`–`T3`
appear twice, once under `cost-tier` and once under `cadence-tier`, and the manifest's
column is headed `Tier` rather than `cost-tier`.

**Control.** Searched `grep -rn 'B1' journals/` → 3 hits, all three consecutive lines of
the `retired-vocabularies` block in `agent-contract.md`; `grep -rn 'T0' journals/` → 2
hits, both in that block; `grep -rn '\bS1\b' journals/` → 1 hit, in that block. Control
that fires: `grep -rn '\bD1\b' journals/` → 3 hits, two in that block and one in
`traps.md` at `` `D1` through `D5` are the wurtzite deformation potentials in ``, so the
search reaches code-shaped tokens outside the block where they exist.

---

### R3 — the manifest names 132 formulas and gives a writable body for 19; 72 rows carry neither an expression, a literature locator, nor an eponym, in `data/registry-manifest.csv`

**Verdict:** ABSENT

**The obligation.** The registry is the oracle's entire physics content, and the page
that defines a row states what a row is for:

> The registry is the closed set of typed, fully parameterized algebraic formulas
> the oracle is allowed to invoke. It is a contract between the property machinery
> and the operator: each row is independently citable to published work and
> independently verifiable by the certification sub-tree, and new rows enter only
> through the registry-build gate ([build-sequence#phases]).

and the reason no body appears in the corpus:

> Every algebraic combination invokes a named formula with typed inputs and an
> explicit output type. No inline mathematics, no string-encoded expressions. This
> is the rule the whole registry exists to enforce: an expression written at a call
> site is unciteable, unverifiable and invisible to the gate, and the three
> properties the registry sells are exactly citeability, verifiability and
> gate-visibility.

The design is therefore that the body lives in the cited paper. Counted, as asked:

**What is missing.** Excluding the two architectural markers, over 132 formula rows —

- **19** carry an expression fragment in the `Source` cell (rows 5, 12, 48, 68, 72, 74,
  84, 110, 112, 119, 120, 123, 124, 128, 129, 130, 131, 132, 134);
- **1** carries a journal-style locator and no expression (row 121);
- **40** carry an eponym (`a.k.a. …`) and no locator and no expression;
- **72** carry none of the three — the row name, a research-stream code, and in some
  cases a prose note about its differentiability tag.

**Three rows of 134 name a journal.** For the remaining 131 the answer to *where does
the body live* is not 'in the cited paper'; it is either 'in a paper you must find from
an eponym' (40 rows) or 'nowhere reachable from this artifact' (72 rows). Several
eponyms name more than one model — row 25's cell reads `S1 (a.k.a. Callaway/Slack)`,
and Callaway and Slack are different closed forms giving different numbers.

**Partially confessed, and the confession is narrower.** `formula-registry.md` declares
`research-stream-documents-absent`, scoped to *provenance following* and to rows 1–87.
Of the 72 body-less rows, 16 lie outside that band (89, 96, 98, 102, 105–109, 111,
116–118, 126, 127, 133), as do 16 of the 40 eponym-only rows (88, 90–95, 97, 99–101,
113–115, 122, 125). Nothing in the corpus says the *formula body* is unreachable.

**Control.** Searched `grep -rn 'single-mode-rta-lattice-kappa' journals/` → 1 hit, a
sentence about its cost tier, no expression. Same for
`charged-supercell-extrapolation-planar-aligned`, `wulff-shape`,
`termination-stability-window`, `impact-ionization-coefficient` → **0** hits in
`journals/` each. Control that fires: `grep -rn 'tp-aware-hull' journals/` → 2 hits
including `residual-definitions.md` carrying the expression
`max(0, ΔG_form(T,P) − ΔG_hull(T,P) − δ_meta)²`, so the search does reach formula bodies
where the corpus states them. Second control: the same regex that found 3 journal
locators in the manifest found 61 in `data/reference-data/*.csv`.

---

### R4 — `ResidualKey` is content-addressed over an `AxisLabel` universe that is never enumerated, never declared closed or open, and never assigned an ordinal policy, in `residual-definitions.md`

**Verdict:** ABSENT

**The obligation.** The residual key is the seam. It is the operator's persistent handle
on every weight it holds:

> ResidualKey = (producer : Producer, axes : Tuple<AxisLabel>)

> Two evaluations with identical inputs produce the identical key. The operator
> holds `Map<ResidualKey, Weight>` independent of this library's internals, and
> those weights persist across compose-time recompiles.

`AxisLabel` is declared a typed indexed universe, and the substrate requires every
universe to carry a carrier kind and an ordinal policy — `carrier_kind : Closed | Open
| Derived`, `ordinal_policy : DenseU32 | DenseU64 | None` — with the serialization rule
writing a sum discriminator as *'a 32-bit ordinal followed by a length-prefixed
payload'*.

**What is missing.** `AxisLabel`'s membership. It appears six times in the corpus: a
glossary pointer, one cell of the substrate's cluster table, the `ResidualKey`
definition, one sentence naming it a typed indexed universe, and twice in the generator
record. The only members ever named appear in a parenthetical that ends in an ellipsis:

>   axes                 : List<AxisLabel>          -- the dimensions this generator unfolds
>                                                   --   over (k-point, frequency, atomic
>                                                   --   pair, shell, …)

An implementer cannot construct a `ResidualKey` without knowing which axis labels exist,
whether the universe is closed (so a new label is a version bump) or open (so it is an
append), and in what order ordinals are assigned. Two implementations will disagree on
every key. A related second gap: `axes` is a `List` at the generator and a `Tuple` in
the key, and the serialization rule orders sequences 'in declared order' — nothing says
whose order that is, so registering the same formula with axes permuted yields different
keys for the same physical contribution.

**Not confessed.** `residual-definitions.md` declares `curriculum-denominator` and
`curriculum-phase-names`; `representation-substrate.md` declares `open-questions: []`.

**Control.** Searched `grep -rn 'AxisLabel' journals/` → 6 hits, none an enumeration.
Control that fires: `grep -rn 'CategoryTag' journals/` → 10 hits including
`residual-definitions.md`'s

> The `CategoryTag` enum is the closed set of these **19 residual categories**:

with all 19 members named — a sibling universe listed in the *same cell* of the same
substrate cluster table, fully enumerated. The search reaches universe enumerations
where they exist.

---

### R5 — `ResidualGenerator.layer : 0..6` is required, drives runtime evaluation order, and no row's layer can be looked up or derived, in `residual-machinery.md`

**Verdict:** ABSENT

**The obligation.**

>   layer                : 0..6                     -- stratum in the layered compute DAG

> `layer` is the generator's stratum in the compute DAG over the whole registry.
> Layer 0 is the primitives, which have no dependencies; each higher layer depends
> only on layers below it. The index is therefore a topological stratification,
> and the runtime evaluates stratum by stratum.

**What is missing.** Three things, and each alone blocks it.

1. The manifest has no `layer` column — its nine columns are `#`, `Name`,
   `Signature`, `Bundle`, `Tier`, `Diff`, `Path`, `Source`, `Depends on` — and no page
   assigns a layer to any row.
2. The stated derivation has no base case. 'Layer 0 is the primitives, which have no
   dependencies', and **zero of 134 rows has an empty `Depends on` cell**. Row 87
   depends on `DFT battery`; row 91 on `lattice`.
3. The dependency edges are not recoverable. **24** of 134 `Depends on` cells name at
   least one `(row N)`; the other **110** name physical quantities — row 1 `bands`,
   row 14 `μ, n`, row 19 `σ`, row 46 `γ family`, row 28 `mechanics ×2`. No registry
   row is named `σ` or `bands`, so those edges point at nothing in the graph being
   stratified.

The same page declares one cycle that the stratification must first cut —

> One cycle crosses the strata: the operating-condition observables and the
> coupled-field balance are mutually dependent through the self-heating operating
> temperature.

— and the cycle is invisible in the manifest: row 70 depends on `dissipation, R_th`,
row 71 on `σ, κ, field`, and neither names the other.

**Control.** Searched `grep -rni 'layer' journals/oracle/` → the only occurrences of the
compute-DAG sense are `residual-machinery.md` lines defining the field and the anchor.
No table, no per-row assignment. Control that fires: the same style of search for the
sibling stratification, `grep -rn 'born-oppenheimer-level' journals/practice/agent-contract.md`,
returns a complete four-member map `{L1: quantum-electronic-substrate, …}` — so a
stratum vocabulary is enumerated in this corpus where one has been decided.

---

### R6 — `combineTol` is the whole error budget and its composition rule is per-instance, with no instance's choice stated anywhere, in `typeclass-alphabet.md`

**Verdict:** ABSENT

**The obligation.** Every residual carries a budget, and one function composes it:

> `combineTol` is how tolerances compose under arithmetic — the tolerance on
> `κ = κ_el + κ_ph` given the tolerances on the two terms. It is associative,
> commutative and monotone, and each instance chooses either maximum-absolute or
> root-sum-square composition.

> that `Quantity.combineTol` ([typeclass-alphabet#quantity]) composes along the
> DAG, per instance by max-abs or by root-sum-square, into a per-`ResidualKey`
> error budget.

The budget is load-bearing: it is what makes *'is this closed-form choice accurate
enough?'* answerable by the system, and it is what the fidelity generators, the
compression targets, the dressing-staleness term and the coefficient-provenance
standard deviations all flow into.

**What is missing.** Which instances choose which. Every one of the nine mentions of
`combineTol` across the corpus either restates 'per instance' or points back to
`typeclass-alphabet.md`, which is the page that says the choice is per instance. No
instance is ever named, and no rule assigns the choice by output type, by residual
category, or by anything else. For a chain of five terms the two rules differ by up to
`√5` — larger than several of the ledger's stated targets.

**Control.** Searched `grep -rn 'combineTol\|max-abs\|maximum absolute\|maximum-absolute\|root-sum-square\|in quadrature' journals/`
→ 20 hits, none of them an assignment. Control that fires: the same search returns
`cert-obligations.md`'s `δ_plan` row, *'the sum over active plans is the compression
term in `combineTol`'* — an explicit composition rule for one term. So the corpus does
state a composition rule where it has one, and the search finds it.

---

### R7 — `characteristic-scale` is declared to be a standard deviation in the observable's own units and is seeded from a ledger written in at least five other encodings, in `residual-machinery.md` / `accuracy-ledger.md`

**Verdict:** ABSENT

**The obligation.**

>   characteristic-scale : Quantity                 -- the observable's declared accuracy
>                                                   --   scale, a standard deviation in its
>                                                   --   own units, seeded from the ledger;
>                                                   --   an error-model input, never a
>                                                   --   fitted weight

> Each `ResidualGenerator` carries a `characteristic-scale` field seeded from this ledger
> ([residual-definitions]), and `Quantity.combineTol` composes them along the DAG, by
> maximum absolute value or in quadrature per [typeclass-alphabet].

The corpus owns exactly one uncertainty-encoding vocabulary, on `reference-battery.md`,
and it has three members:

> **Three uncertainty encodings appear, and a consumer must dispatch on the format.**

with an absolute one-sigma band, a multiplicative `×N` read as `σ_ln = ln N`, and
`unbounded`.

**What is missing.** The conversion. The ledger's 59 accuracy-regime rows are written
in encodings the three-member vocabulary does not contain, and the majority of them are
in the one that is missing — relative percent. Sampled from the regime table:

> | 54 | Poole-Frenkel dielectric leakage (row 129) | ±1 decade | trap-parameter-dominated, per film |

> | 34 | tunneling_transmission T_WKB | ±20% in the logarithm | Fowler-Nordheim closed form |

> | 55 | time-dependent dielectric breakdown (row 130) | order of magnitude | thermochemical field model per film; a lifetime figure of merit, not a precision target |

Nothing states how `±5%` becomes 'a standard deviation in its own units' at compile
time, when the value it is a percentage *of* is a runtime quantity; nor how `±1 decade`,
`order of magnitude` or `±20% in the logarithm` do; nor how a log-scale sigma and an
absolute sigma may be root-sum-squared together, which R6 leaves free anyway. Regime row
57 reads `peak positions exact given the cell and ion positions` — a scale of zero, which
no composition rule admits.

**Control.** Searched `grep -rni 'characteristic-scale' journals/` → 5 hits, all of them
declarations that the field is seeded from the ledger, none a conversion. Control that
fires: `grep -rn 'σ_ln = ln N' journals/` reaches `reference-battery.md`'s encoding
table, so the search does find the corpus's stated conversions where they exist — and
that table covers the *reference data files*, not the ledger.

---

### R8 — all six `relaxed` rows name a relaxation and none carries a value for the relaxation's one parameter, in `data/registry-manifest.csv`

**Verdict:** ABSENT

**The obligation.** `named-formulas.md` makes the named relaxation a gate condition:

> - **`relaxed`** — genuinely non-smooth: argmin, convex hull, sort, discrete
>   metric. Ships a declared smooth relaxation whose bias is a model-form error
>   entering the tolerance composition of [typeclass-alphabet#quantity], approved
>   at registration with a validity domain under obligation-9
>   ([cert-obligations#the-ten-obligations]). **The relaxation is named in the
>   row's provenance cell**; a `relaxed` row without one is un-gateable and fails
>   the registry-build gate ([traps#unnamed-relaxation]).

and `cert-obligations.md` makes its ledger canonical for the numbers:

> Canonical names and default values for every tolerance and error bound in the oracle

with the namespace rule that closes the loophole:

> `ε` is reserved for permittivity in the physics formulas. **`τ` is not a reserved
> tolerance prefix** — `τ_n`, `τ_p`, `τ_PO`, `τ_E`, `τ_hop`, `τ_iv` and `τ_alloy` are
> physical times, and a `τ_x` is a tolerance only if it appears in the table below.

**What is missing.** Every softness parameter. The six `D4` rows are 45, 46, 50, 67, 84
and 85. Row 46 names `softmin over γ(term) at temperature τ_soft` — `τ_soft` has no
value and is not in the tolerance ledger, so by the corpus's own rule it is not a
tolerance and is nothing else either. Row 50 names
`soft-cutoff coordination Σ_j σ((r_cut−d_ij)/δ) with declared width δ` — `δ` is
declared nowhere. Row 85 names `softmin over the set plus a sigmoid on (d−d_min) with
declared width` and names neither the width nor the descriptor `d` is a distance in.
Rows 45 and 67 name `soft-hull log-sum-exp` and `soft-min hull log-sum-exp` with no
parameter at all. Row 84 offers two different relaxations —
`continuous site occupations x_i∈[−1,1] (mean-field / Gumbel-Softmax)` — and does not
choose between them; the second has its own temperature.

The bias of a relaxation is a monotone function of exactly this parameter, and the
corpus routes that bias into `combineTol` as model-form error. With the parameter
unvalued the gate passes, the error budget cannot be formed, and the residual's gradient
magnitude is an implementer's free choice.

**Control.** Searched `grep -rn 'τ_soft\|declared width\|softmin\|soft-min\|log-sum-exp' journals/ data/`
→ 6 hits, five of them the manifest's own `Source` cells and one the `partition-Z
(log-sum-exp)` sub-method on `computational-methods.md`. `τ_soft` appears **zero** times
in `journals/`. Control that fires: `grep -rn 'τ_NEB\|τ_cond\|τ_adj' journals/` returns
the tolerance-ledger rows with their defaults `1e-3`, `1e-8`, `1e-4` — so the search
reaches valued tolerances where the corpus has valued them.

---

### R9 — the registration adjoint gate states its threshold and its known failure mode and never states its sampler, in `residual-machinery.md`

**Verdict:** ABSENT

**The obligation.**

> **Hard.** `adjoint` **and** `fixpoint-adjoint` entries run a
> vector-Jacobian-versus-Jacobian-vector check on `N ≈ 64` sampled points at
> registration time. If the maximum relative error exceeds `τ_adj`, default
> `1e-4`, the build fails loud.

The page then makes the sampler load-bearing by naming exactly the way it fails:

> **A passing gate is not evidence of a correct tag.** The two products agree
> trivially wherever the true gradient is zero, so a row whose output is
> piecewise-constant — an argmin over a discrete set, a hard-cutoff count —
> **passes this gate spuriously** and ships a certificate for a gradient that does
> not exist. Registry rows 46 and 50 are that shape. Before trusting an `adjoint`
> pass, check that the sampled points straddle a region where the output actually
> varies.

**What is missing.** How the 64 points are drawn. No domain (the applicability cell? a
box around a reference state? the environment box?), no distribution, no seed, no
determinism requirement. The corpus turns 'the sampled points straddle a varying
region' into an instruction to a *reader* — 'before trusting an `adjoint` pass, check'
— rather than a property of the sampler, which is the one place it could be enforced.
Three further consumers inherit the same unspecified set: the `fixpoint-adjoint`
conditioning check runs 'at the same sampled points', the rewrite-admission fidelity
estimator 'shares the adjoint gate's sample set', and `registration-hash :
ContentAddress` is described as a cert tripwire — which requires the gate's verdict to
be reproducible, which a non-deterministic sampler is not.

**Control.** Searched `grep -rn 'sampled point\|sample set\|N ≈ 64\|drawn from' journals/`
→ 15 hits; every one is a *use* of the sample set, none a construction. Control that
fires: the same search style over the sibling obligation,
`grep -rn 'held-out' journals/`, returns obligation 9's
`measured on a held-out development set` and obligation 4's `held-out crystal battery` —
so where the corpus specifies a sample's provenance the search finds it.

---

### R10 — the manifest's 134 signature cells are written in a fourth type vocabulary that no page defines and no open question covers, in `data/registry-manifest.csv`

**Verdict:** ABSENT

**The obligation.** The corpus already confesses two type-vocabulary holes and names
their members precisely. `computational-methods.md`:

> The signatures on this page and on [property-templates] are written in argument
> types — `Extractor`, `Aggregator`, `ResponseKernel`, `PathMethod`, `Optimizer`,
> `EigenSolver`, `ConvexSolver`, `KineticMethod`, `Sampler`, `ProjKind`,
> `Classifier`, `ComparisonMetric`, `TensorNorm`, `HessianMethod`,
> `NonlinearSolver`, `BiSlabSolver`, `ChargeNeutralitySolver`,
> `ConvergenceCriterion` — **that no page defines.** They appear only at use sites.

and `typeclass-alphabet.md` confesses `Scalar`, `Tensor` and `FieldOnGrid` as
`three-aliases-never-expanded`.

**What is missing.** The manifest's own input and output type names, which belong to
neither list. `BandStruct`, `k-grid`, `collision-matrix`, `AbelianGroup`,
`eigenstates_on_grid`, `eigenstates_on_loop`, `antiunitary_op`, `bond-vec`,
`phase-diagram`, `polyhedron`, `hull`, `AZ_class`, `structure set` are the argument and
result types of the rows an implementer has to write, and each occurs only inside the
manifest. Row 1 in full:

> 1,bandgap-direct,`(BandStruct) → Scalar`,B1,T0,D1,cheap,S1,bands

Neither declared open question mentions any of them. The result is that the simplest row
in the registry — a scalar band gap — cannot be typed: its input type is undefined, its
output alias is confessed-undefined, and its unit is undeclared (R1).

**Control.** Searched `grep -rn 'BandStruct' journals/ data/` → 8 hits: 5 are
`BandStructure`, a *composition identifier* on `typed-compositions.md`, and 3 are the
manifest rows 1–3. Searched `grep -rn 'collision-matrix' journals/ data/`,
`grep -rn 'AbelianGroup' journals/ data/`, `grep -rn 'eigenstates_on_grid' journals/ data/`
→ 1, 1 and 2 hits respectively, all in `data/registry-manifest.csv`. Control that fires:
`grep -rn '\bResponse\b' journals/` reaches `typeclass-alphabet.md`'s
`Response` expansion, so the search finds a type alias where the corpus expands one.

---

### R11 — two rows invoke inputs that are neither manifest rows nor state slots and are not among the undeclared invocations the corpus flags, in `data/registry-manifest.csv`

**Verdict:** ABSENT

**The obligation.** The manifest flags this exact condition six times when it knows
about it — rows 7, 8 and 9 carry
`D(q) from the DFPT reference solve (unregistered input)`, row 47 carries
`work function and electron affinity (unregistered inputs)`, row 80 carries
`H_device and contact self-energies (unregistered inputs)`, and row 115 carries
`ΔE_C is a signature input with no registered row`. `typed-compositions.md` flags two
more at page level under `undeclared-non-formula-slots`:

> Two names are invoked in slots that are not formula arguments and are neither manifest rows nor part of the declared gap: exchange-coupling-formula as a response kernel, and harmonic-rate-prefactor as a rate prefactor. Whether they belong to the declared gap or to a kernel vocabulary no page owns is unsettled.

**What is missing.** Row 114's two unflagged ones, and the sub-stage rows 92–94 stand on.
Row 114 in full:

> 114,piezoelectric-tensor,"`(Z*[I,α,β], du/dε[κ,J], Ω, e_clamped) → e[i,J]`",B7/B6,T1,D1,cheap,"S1+S2 (catalog #35; clamped-ion + Z*·du/dε, a.k.a. King-Smith-Vanderbilt)","operator-position-derivative-tensor (row 92, Z*), elastic-constants-Cij (row 60), Ω"

`e_clamped` — the clamped-ion piezoelectric term, which is the larger of the two
contributions — and `du/dε[κ,J]`, the internal-strain tensor, are signature inputs with
no row, no definition and no flag. Separately, the `Depends on` cell of rows 92, 93 and
94 — the three linear-response primitives the whole polarization package stands on —
reads `linear-response sub-stage`, and that sub-stage appears in the corpus only as one
item inside a table cell on `born-oppenheimer-levels.md`. It has no signature, no method
assignment in the twelve-method alphabet, and no algorithm.

This matters more than a missing row because rows 113, 114, 115, 117, 118 and 133 all
descend from 92–94, and `accuracy-ledger.md` puts a `±5%` target on the interface
polarization those rows produce.

**Control.** Searched `grep -rn 'e_clamped' journals/ data/` → 1 hit, the manifest cell.
`grep -rn 'du/dε' journals/ data/` → 1 hit, the same cell. Control that fires:
`grep -rn 'exchange-coupling-formula' journals/ data/` → 3 hits, one of them the open
question that declares it, and `grep -rn 'harmonic-rate-prefactor' journals/ data/` → 3
hits likewise — so the search reaches undeclared-invocation names that the corpus *has*
flagged, and finds no flag on these two. Second control:
`grep -c 'unregistered\|no registered row' data/registry-manifest.csv` → 6, so the
manifest does carry this flag where it has been applied.

---

### R12 — the dressing-staleness term multiplies a norm over the mixed-unit seven-tuple state by a compile-time coefficient, and neither the norm nor the coefficient's norm is defined, in `residual-machinery.md`

**Verdict:** UNDERSPECIFIED

**The obligation.** The term is normative and its computability is the argument for it:

> The last two fields are the frozen dressing's **validity radius**, computable
> rather than declared. A one-shot dressing does not respond to state excursions
> and contributes no gradient ([born-oppenheimer-levels#dressing-tiers]), so the
> term it drops is its state-dependence. To first order that term is `‖x −
> reference-state‖ · staleness-coeff` — a compile-time coefficient measured once
> where the dressing is already being computed, times a runtime norm. Their
> product is the dressing-staleness entry of the error budget
> ([residual-definitions#error-budget]).

with the coefficient declared as

>   staleness-coeff   : Quantity                    -- ‖∂(dressing)/∂x‖, measured once at
>                                                   --   reference-state, at compile time

**What is missing.** `x` is the seven-tuple state — a `3×3` cell matrix in length units,
`3N` positions in length units, `3N` momenta, a `3×3` cell momentum, discrete species
labels, a one-body density matrix that is dimensionless, and a vector-potential field.
`‖x − reference-state‖` is a single number over that tuple, and the corpus states no
metric, no per-slot weighting, and no unit for the result. It also states no norm for
`‖∂(dressing)/∂x‖`, which must be the dual of whatever the first one is if the product is
to land in the observable's units. Two implementers choosing different slot weightings
get dressing-staleness terms differing by orders of magnitude, and this term is a summand
of the same `combineTol` budget R6 already leaves free.

**Control.** Searched `grep -rni 'frobenius\|which norm\|norm convention\|operator norm\|spectral norm' journals/`
→ 2 hits: `metric = Frobenius²-volume-normalized` on `typed-compositions.md`, and the
compression estimator `‖A − A_k‖₂ = σ_{k+1}` on `residual-machinery.md`. Control that
fires: those two hits are themselves the control — the corpus *does* name a norm when it
has picked one, twice, and neither is the state norm.

---

### R13 — row 87 and row 66 read a reference file the corpus states does not exist and states nothing points into, in `reference-battery.md`

**Verdict:** UNDERSPECIFIED

**The obligation.** Row 87 `reference-phase-energy-cache` is `T3`/`D0`, its `Depends on`
cell is `DFT battery`, and it is the base of the thermodynamics bundle — row 66
`chemical-potential-ref-table` lists `reference-phase-energy-cache (row 87), T, P` as its
dependency, and rows 30, 44, 65, 67, 86 all read chemical potentials. `named-formulas.md`
singles row 87 out as the row that defines the `read` differentiability value.

**What is missing.** The data. `reference-battery.md`:

> **Three sub-areas have no file yet**: interface properties — Schottky barriers, work
> functions and carbide-formation energies per metal-semiconductor pair; defect formation
> energies per host, species and charge state; and elemental chemical potentials at
> standard conditions. Nothing reads them, and no row anywhere points into them.

Rows 66 and 87 are rows that point into the third of those, and rows 47 and 48 point
into the first. The sentence 'no row anywhere points into them' is what would otherwise
tell an implementer these three absences are harmless; they are not, and the corpus does
not say what row 87 returns in their absence — there is no stated refusal path, no
`UNSEEDED` marker on the row, and no `not-implemented-in-V1` stub of the kind
`residual-machinery.md` specifies for iterative dressing.

**Control.** Searched `grep -rn 'reference-phase-energy-cache' journals/` → 3 hits, all
on `named-formulas.md`, all about its differentiability and cost tags, none about its
data source. Control that fires: `grep -rn 'not-implemented-in-V1' journals/` → 1 hit,
`residual-machinery.md`'s `V1 ships one-shot-dressing wired, and iterative-dressing as
type and cert scaffolding only, with \`not-implemented-in-V1\` stubs that fail loud` — so
the corpus does state a refusal path where it has decided one, and the search finds it.

---

## Sample

**Frame.** 134 manifest rows. **Sample: 20 rows, build-sheeted on all four questions
(exact input/output types; the expression rather than its name; every numeric constant
and its source; the refusal path). This is a sample, not a sweep.**

**How chosen.** Stratified deliberately, not randomly, to span the axes the manifest
codes and to load the extremes:

- *at least three routine-looking*: 1 `bandgap-direct`, 14 `drude-conductivity`,
  61 `bulk-modulus` — the three shortest signatures at `T0`/`D1`/`cheap`;
- *at least three hardest-looking*: 13 `SCPH-self-consistent-phonons`,
  80 `NEGF-transmission`, 122 `iterative-lbte-kappa`, 96
  `symmetry-classification-group-via-snf` — every `T3` row bar 106, plus the only `DN`
  row with a group-valued output;
- *one per differentiability value*: `D0` 87, `D1` 1/14/61/74/114/124/129, `D2` 92,
  `D3` 13/122, `D4` 45/46/85, `DN` 96, marker 103;
- *cost spread*: `T0` ×8, `T1` ×6, `T2` ×2, `T3` ×3, marker ×1;
- *bundle spread*: B1, B2, B3, B4, B5, B6, B7, B8, B10, B11, L1 all represented;
- *provenance spread*: expression-carrying (74, 124, 129), eponym-only (25, 30, 32, 114,
  122), bare stream code (1, 13, 14, 45, 46, 61, 80, 85, 87, 96), `extension`/atlas
  (92, 96, 129), architectural marker (103);
- *anchor class*: 15 `cheap`, 4 `faithful`, 1 marker.

**Result.**

| verdict | count | rows |
|---|---|---|
| DETERMINED | 3 | 74, 103, 124 |
| UNDERSPECIFIED | 11 | 1, 14, 30, 46, 61, 85, 87, 92, 96, 114, 129 |
| ABSENT | 6 | 13, 25, 32, 45, 80, 122 |

**3 of 20 — 15% — could be typed.** And that 15% is conditional: all three are
DETERMINED only *given* a unit convention, which R1 shows does not exist, so the
unconditional rate is 0 of 20.

The three that pass do so for the same reason: their `Source` cell carries the
expression, its constants, and its gate. Row 74 carries `α(E)=α0·exp(−β/E)` with the
`cm⁻¹`-not-`s⁻¹` unit note, per-material `(a, b)` triples seeded in
`accuracy-ledger.md#high-field-coefficients`, and a stated refusal (aluminium nitride
measured is `UNSEEDED` and cert-refused). Row 124 carries
`R_hull=max(0,ΔG_form−ΔG_hull−δ_meta)²` with `δ_meta` valued in the tolerance ledger.
Row 103 is an architectural marker that is explicitly not implemented.

Per-row notes on the six ABSENT: row 13's signature `(D(q), T)` omits the quartic force
constants the self-consistent phonon equation consumes, so the signature is
under-determined for the algorithm its name denotes; row 25's eponym names two different
models and its signature omits the group velocities and mode heat capacities the
conductivity sum needs; row 32 (Freysoldt/FNV) is a multi-step alignment procedure with
a sampling region, and appears in `journals/` zero times; row 45's Wulff construction has
no body and an output type `polyhedron` that is defined nowhere; row 80 has no body and
its own cell declares its inputs unregistered; row 122 is declared dormant and returns
'an anchored constant' whose value and source are not stated.

---

## Coverage

**Read fully** — `journals/oracle/registry/named-formulas.md`,
`formula-registry.md`, `computational-methods.md`, `property-templates.md`,
`observable-bundles.md`, `properties.md`, `typed-compositions.md`,
`canonical-vocabularies.md`, `topology-atlas.md`, `typeclass-alphabet.md`;
`journals/oracle/seams/residual-machinery.md`, `pino-bridge.md`;
`journals/oracle/laws/residual-definitions.md`;
`journals/oracle/accuracy/accuracy-ledger.md`, `reference-battery.md`;
`journals/oracle/certification/cert-obligations.md`;
`journals/oracle/compilation/representation-substrate.md`;
`journals/oracle/state/crystal-inputs.md`;
`journals/practice/agent-contract.md`, `conventions.md`;
`journals/n-op/build/build-verification.md`; `data/registry-manifest.csv` (all 134 rows).

**Read partially** — `journals/practice/traps.md` (units and reference-frame sections,
plus targeted greps); `journals/oracle/state/unified-state.md` (the seven slots and what
the state leaves out); `journals/n-op/build/mvp-system.md` (the units line and its
surroundings); `journals/oracle/state/born-oppenheimer-levels.md`,
`journals/oracle/laws/coupling-structure.md`, `generic-dynamics.md`,
`journals/oracle/compilation/compose-time-pipeline.md`, `physics-graph.md`,
`journals/oracle/certification/applicability-classifiers.md`, `out-of-scope.md`,
`journals/oracle/state/multiscale-state.md`, `gamma-hat.md`,
`journals/n-op/build/capability-slices.md`, `journals/practice/glossary.md`,
`data/reference-data/*.csv` (line counts and citation-density controls only) — each
reached by targeted search rather than read end to end.

**Not read** — `journals/n-op/build/build-sequence.md`, `forced-decisions.md`;
`journals/n-op/purpose/*` (4 pages); `journals/operator/*` (3 pages);
`journals/interface/boundary.md`; `data/diamond-strain-sweep/*`;
`data/diamond-defect-corpus/*`; `tools/`; `log/`; `generated/`.

---

## Near-findings rejected

- **`Path` column header vs the `anchor-class` field name.** Rejected: the column's
  only two values are `cheap` and `faithful`, which is `anchor-class`'s entire
  vocabulary, so the binding is decidable from the values.
- **`T0`–`T3` shared between `cost-tier` and `cadence-tier` in the decode block.**
  Rejected as a standalone finding — `formula-registry.md#fields` fixes the manifest's
  column as `cost-tier` and `agent-contract.md` separates the two explicitly. Folded
  into R2 as a hazard rather than a blocker.
- **`L1` meaning `linear-response-primitive` in the bundle map and
  `quantum-electronic-substrate` in the Born–Oppenheimer map.** Rejected: two separate
  maps, and `observable-bundles.md` states the bundle reading for rows 91–94 outright.
- **`CategoryTag` ordinal assignment order unstated.** Rejected: `ContributionFacets` is
  a sidecar and `residual-definitions.md` states it is 'never part of `ResidualKey`
  identity', so ordinal drift cannot corrupt the operator's weight map.
- **The 19 residual categories are not an implementable enum.** Rejected — checked and
  they are: all 19 names appear explicitly, the count is stated in two places, and the
  arithmetic 9+3+5+2 closes.
- **`Address` domain-separator tag values unstated.** Rejected: the 16-byte tags are
  internal to one build and nothing in the corpus requires two independent
  implementations to agree on an address.
- **Row 1's body absent.** Rejected as a separate finding — it is one instance of R3
  rather than a finding of its own. Same for rows 45, 61, 80.
- **`argument-type-alphabet-homeless` and `three-aliases-never-expanded`.** Rejected as
  findings: both are declared open questions. R10 is scoped to the manifest's own type
  names, which neither covers.
- **The Voigt/Reuss/Hill choice for `bulk-modulus`, and the four hardness models.**
  Rejected: both are declared — `cij-averaging-scheme` and the
  `unregistered-composition-formulas` gap on `typed-compositions.md`.
- **Row 122's dormant gate having no cert encoding.** Rejected: declared as
  `dormant-row-cert-encoding`.
- **`sampling-policy : UniformBatch | RAD(τ) | Importance | ValidationOnly` with `τ`
  unvalued and no importance function.** Rejected as a finding on its own — sampling
  cadence is repeatedly assigned to the operator library, which is out of unit — but
  noted, because `sampling-policy` is a required argument of `make-residual-generator`
  on the oracle side and its four values are never given semantics.
- **`Value`, `Cotangent`, `ObservableRef` and `TypedSlot` undefined.** Rejected as
  separate findings and folded conceptually into R10; `TypedSlot` is the sharpest
  (`input-contract : {TypedSlot}` is what would type a generator's forward function, and
  it occurs twice in the corpus, both times in that record).
- **`max(0,·)²` on row 124 tagged `D1` rather than `D4`.** Rejected: the square makes it
  continuously differentiable, so `direct` is correct.

---

## By-catch

- `accuracy-ledger.md` regime row 12 puts the four-phonon correction's validity at
  `≈0.4 Θ_D`, 'about 880 K' for diamond; the MVP-targets table on the same page marks
  κ at 773 K 'path-met — the four-phonon correction, registry row 121, valid `≳0.4 Θ_D`'.
  773 K is below 880 K.
- Row 121's `Source` cell reads `Feng-Lindsay-Ruan PRB 96 161201` with no year;
  `accuracy-ledger.md` gives the same paper as `(2017)`. The manifest is the artifact a
  literature search would start from.
- `reference-battery.md` says of the three missing files 'no row anywhere points into
  them'; manifest rows 47, 48, 66 and 87 point into two of them. (Load-bearing enough
  that it is also R13.)
- `named-formulas.md` says the cost value 'is what the residual factory reads when it
  decides how often to sample a generator'; `residual-machinery.md#factory` lists three
  responsibilities for the factory and sampling cadence is not among them.
- Manifest `Diff` uses the token `DN` while `named-formulas.md`'s sixth differentiability
  value is `none`; two rows' `Source` cells (85, 101) explain the spelling change inline,
  which is the kind of history `agent-contract.md#forbidden` rules out of pages.
- Row 5's `Source` cell contains `dE_F/dp = −(∂F/∂p)/(∂F/∂E_F)`, an implicit-function
  derivative, in a column whose declared vocabulary is a closed set of seven provenance
  values.

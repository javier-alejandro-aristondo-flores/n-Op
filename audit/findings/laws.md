# Cohesion audit — the laws

Subject: `journals/oracle/laws/` — `generic-dynamics`, `residual-definitions`,
`coupling-structure`.

Status: **resumed 2026-07-31 after a session limit; substantially more complete.**
Findings **L1–L21** are established directly and are complete as stated.

What changed on resumption:

- **L17** merges the principal's 19-category disjointness sweep — the gap my first draft
  named as the one that most weakened this subject. Every overlap re-verified against the
  primary text; two extended, one bounded downward. The sweep's own calibration (4.5 of 6)
  is reported unrounded in §5 and L17 carries that gate, not my 6-of-6.
- **L18–L21** are new. L18 closes the last of my own delegated-and-unreturned items (the
  bare symbols in `Positivity`). L19, L20 and L21 came from re-reading four sections my
  first pass skimmed; L20 was referred to me by the state subject after they traced the
  normative statement to my page, and L21 is on an owned topic that four other findings
  files touch from the sourcing angle while none examines the rule itself.
- **The inherited contradictions are triaged**, per the brief's first instruction on the
  inheritance: eight rows fall in my subject, six persist, two are resolved. The table
  opens §2.
- **L4, L6, L7, L11, L16** are each strengthened by primary text I had not read. The L4
  addition is the strongest internal evidence in the subject and was one section below the
  operator table the whole time.
- **§5 now reports two calibration numbers, not one.** The 6-of-6 calibrates reading at a
  named location. The instrument that chooses *which* locations to read is uncalibrated and
  demonstrably defective — three known misses, two of them found by other people. §7
  proposes the method rule that follows.

Four literature arms are running at the time of writing and their results are marked where
they land. §6 names exactly what remains unchecked. **This is still not a clean verdict
over the subject; it is a judgment over the part I closed, with the boundary stated.**

---

## 0 · Judgment

**The physics on these pages is mostly right. The claim the pages exist to make is not
established, and the corpus cannot currently tell the difference.**

The central bet — that one metriplectic equation expresses all the target physics as
extractions — is **asserted and never derived** (L1). The page that the derivation is
promised to live on contains no `L`, no `M`, no `δE/δx`, no `dx/dt`; it is a coverage
table over a different vocabulary. And the corpus's own consistency gate silently
substitutes the weaker proposition it *can* check ("realizable as typed compositions of
the method alphabet") for the stronger one it states. That substitution is the single most
important thing I found, because it means the bet has never been tested by anything,
including by the machinery built to test it.

Tested by hand, the bet holds for five of the nine regimes and fails for three. Structural,
Mechanical, Thermal, Transport and Thermodynamic are genuine extractions (N8). Electronic,
Magnetic and Chemical are **energy-descending flows**, which the corpus's own second
degeneracy condition forbids — `M·δE/δx = 0` makes *both* parts energy-conserving, and the
single-generator escape is granted to the Born–Oppenheimer level and to none of these
(L2, L3). Optical is misattributed to the dissipative operator while every other page
computes it from the reversible response (L13). These are not presentational slips; they
are the difference between a derivation and a relabeling.

**For at least two of those rows it is worse than undefended — it is impossible.** An
independent line of work returned a three-line impossibility proof for the Magnetic row:
no symmetric operator can both produce the Landau–Lifshitz damping term as written and
satisfy `M·δE/δx = 0`. It needs only the symmetry of `M`, and it holds for *every* choice
of entropy functional, so no assignment of `S_vib`/`S_electronic`/`S_config` rescues it.
The same work confirmed by independent means that `typed-compositions` carries no dynamics
for either the magnetic or the chemical regime, matching my mechanical sweep. So "asserted,
not derived" understates it for those rows: they are **not derivable on the stated state
space at all**, and are repairable only by adding a thermal variable to receive the
dissipated energy.

**On the structural guarantees, which you asked me to verify rather than accept: the
by-construction claim is false, and it is the most dangerous kind of false claim in this
corpus** (L4). The typed targets deliver antisymmetry of `L` and positive-semidefiniteness
of `M`. Neither implies either degeneracy condition — they are independent conditions on
the null spaces, and I show the mathematics. The two by-construction arguments the corpus
does give cover the γ̂ block and the Born–Oppenheimer level, and say nothing about the
generated cross-terms whose coefficients the operator *learns*.

**And the sentence the corpus offers in place of a construction does not reach those terms
either** (L19) — this is new on resumption and I had taken the sentence at face value the
first time. The conditions are scoped *"per tier / per level"*, which names **two different
partitions of the state** joined by a slash: the three tiers put `γ̂` and `R` together, the
four Born–Oppenheimer levels put them apart, and the page never says which is meant. Its
own two by-construction arguments are stated at **level** granularity — and on that
reading, a coupling is off-diagonal by definition, the MVP's headline channel
`electron-phonon` declares `pieces = [γ̂, R]` across two levels, and a condition scoped to
the generators *active at a level* does not see a block joining two of them. Under the
other reading the two arguments are at the wrong granularity to discharge anything. So the
reconciliation fails on both horns, and it fails precisely at the object L4 is about.

**And the corpus states my own mathematical claim, one section away, before declining to
apply it** — `generic-dynamics:161-164` says the generated cross-blocks "conserve energy by
antisymmetry but do **not** automatically satisfy Jacobi — that is an additional
condition", then restricts the class, keeps a flag, keeps a cert-side numerical check, and
disclaims the proof in writing. **Same blocks, same generator, same learned coefficients.**
One structural property gets a documented gap and a numerical check; the other gets "by
construction" and an unvalued `≈ 0`.

The corpus's own asymmetry convicts it: for positive-semidefiniteness it is careful — tight/loose closure, a runtime
guard, a valued tolerance — while for degeneracy, a strictly stronger condition on the
same learned coefficients, it grants an unqualified "by construction", removes the term
from the training loss on that basis, and checks it with `≈ 0`, **the only unvalued
threshold in the certification layer**.

**The two halves close into a loop, and this is the sharpest thing in the subject.**
`Degeneracy` — the residual whose whole purpose is to catch a violated degeneracy
condition — is designated cert-only, and removed from the training loss, on the stated
ground that it is *"identically zero by construction"*. That premise is false in general
(L4) and provably false for the Magnetic and Chemical rows in particular. **The one
tripwire that would have caught this is switched off by the very assertion that needed
checking.** And the switch-off is not even backstopped: what remains is a cert-side check
written `≈ 0` with no tolerance anywhere in the corpus — the only unvalued threshold in
the certification layer, on the corpus's own central structural claim.

Trace the loop as a closed cycle, because each step is separately documented and it is
the cycle that is the defect:

```
the central bet: every regime is an extraction of  dx/dt = L δE/δx + M δS/δx
        │  is never derived (L1) — the page it cites carries a different claim,
        │  and the only mechanical gate on it checks the weaker one
        ▼
the bet's structural content is the two degeneracy conditions
        │  claimed "identically zero by construction" (residual-definitions:109-112)
        │  — and never constructed (L4); false for Magnetic and Chemical (L2, L3)
        ▼
that claim removes `Degeneracy` from the training loss
        │  so nothing during training can observe the violation
        ▼
what remains is a cert-side tripwire written  ≈ 0
        │  with no tolerance in the ledger the corpus declares canonical for tolerances
        ▼
and `Degeneracy` is the only one of the 19 categories that scores the *library's own
constructed operators* rather than the candidate state — a self-test, not a residual.
        └─────────── so the corpus's only self-test is disabled by the assertion it exists
                     to test, and its replacement cannot fire. ───────────┘
```

Nothing outside the cycle closes it. `build-verification`'s consistency gate checks
realizability in the method alphabet (L1); the structure checker checks that the citation
resolves, which it does; and the tolerance ledger, which would have caught the unvalued
`≈ 0`, is governed by a rule — *"A tolerance stated anywhere in the corpus but absent
from this table is a defect in this table"* — that no checker implements.

**The category vocabulary that carries all of this is not a partition, and the schema
requires one** (L17). `ContributionFacets.category` is a single `CategoryTag` on a
sidecar map keyed by `ResidualKey`, and facets are explicitly excluded from key identity —
so `category` is a total single-valued function and the 19 categories must partition the
emitted contributions. They do not: six overlaps, and the page's only disjointness
argument covers one of the 171 pairs. The sharpest is that `ω² ≥ 0` and "dynamical
stability" are one condition in two categories, scored at two curriculum gates, where
**only one copy carries the applicability gate** — so the gate installed to stop the
oracle penalizing legitimate transition states is bypassed by its own duplicate from
training fraction 0.60, and the `traps` entry marked *enforced* against that hazard names
the anchor of the gated copy only. Two further members of the 19 do not denote what the
rest do: `EOM/Z` is ill-typed on an immutable discrete slot (L6, and the page's own
granularity list omits it), and `Degeneracy` is a library self-test. **The closed
vocabulary the corpus counts as 19 contains 17 residuals of a candidate state.**

**The error budget that would tell a consumer whether any of this is accurate enough is
composed by a rule that is invalid in the case the same page calls common** (L21).
`combineTol` may compose "per instance by max-abs or by root-sum-square", with no rule for
choosing; root-sum-square is sound only for independent errors, and the word *independent*
never appears in that sense anywhere in the corpus; and twenty-two lines away the page
declares that two contributions sharing **99% of their DAG ancestry** "is the common case".
Under near-total correlation root-sum-square under-estimates by `√n` — while remaining
monotone, which is the property the corpus names as the safeguard against exactly this. The
safeguard does not cover the failure it is offered against.

And in the smallest, earliest category — `Positivity`, one of only two live from training
fraction 0.00 — two of six members are bare symbols the corpus binds nowhere (L18). Each
has a reading, supported by the corpus's own usage elsewhere, under which the residual
penalizes correct physics: bare `ρ` means the *signed* charge density at five of five
sites in this corpus, and `σ ⪰ 0` reads either as the stress tensor, which is negative
under any compression, or as the conductivity tensor, which is positive semidefinite only
in its symmetric part.

Two further failures are structural rather than physical, and both bite the MVP:
a channel the MVP coupling spec activates cannot be constructed in the closed schema
(L7), and a residual category is defined over a state slot the corpus declares immutable
and discrete, making its functional derivative undefined rather than merely zero (L6).
The first of those turns out to reach further than I first reported: the **normative gauge
partition names that same non-existent channel as an owner of the longitudinal electrostatic
sector**, while seventeen lines earlier the page puts the ion–ion energy inside `E_KS`. One
of the two is wrong, in a passage whose stated purpose is to prove nothing is
double-counted — and the convention that would resolve it is written down once, for the
neighboring channel, and never generalized.

**One finding here is not mine and I am carrying it because it lives on my page** (L20).
The `Normative` gauge sentence derives transversality `∇·A = 0` from the "remaining
time-independent gauge freedom" of the Weyl gauge, and that derivation cannot work: the
residual freedom is time-independent by necessity, the obstruction `∂_t(∇·A) = −4πcρ` is
not, and a time-independent `∇²χ` cancels it at one instant only. I re-derived it rather
than taking the referral. The partition the page describes is correct standard physics;
the sentence justifying it is not. I also pass on the state subject's **corrections to the
principal's framing** of this item, because they lower its severity: Gauss's law is not
violated, and a static applied field is not homeless — transversality is vacuous at
`k = 0`, so a uniform field rides `A(t) = −cEt` and needs no Berry-phase machinery. What
is real is that the corpus has two routes for an applied field and states neither.

The sign work came out better than expected. The traps register has done its job: the
conventions it guards are right where it guards them. What it does not reach is
**unguarded**, and that is where the sign defects are — the Landau–Lifshitz damping term
is written with no sign at all (L2), Onsager reciprocity is named with no equation and so
without the magnetic-field reversal that makes it true (L11), and the Lie–Poisson bracket
is missing the factor that makes it real-valued (L10).

One thing I want on the record about how the corpus fails, because it recurs. Three of my
findings (L8, L14, L15) are places where the corpus **declared** a gap or restated a
value and the declaration itself is what causes the harm: an open question that describes
a name *rotation* as a *substitution* and so reads as triaged; a rationale that motivates
two categories which a frozen trajectory satisfies exactly; a value restated with its
disagreement dropped. A corpus this disciplined about honesty accrues a specific new
failure mode — the honest-looking note that is wrong about its own contents, and is
therefore trusted more than silence would have been.

**And one thing on the record about how *I* failed, because it is the most transferable
result here.** Three defects in my subject sat outside my method's scope rules, and **not
one was a reading failure** — in every case I read the right page, quoted it correctly,
and asked it the wrong question. Two were found by other people: L17 by the principal's
sweep, L20 by the state subject working on their own page and tracing the normative
statement back to mine. My traps-seam sweep reported *"nine enforced pointers, nine
resolving to text that carries the rule"* — true, and not the question; two of those nine
name sites whose rule is either duplicated without its gate (L17(1)) or false as written
(L20). **I built the corpus's characteristic defect into my own instrument**: I checked
that links resolve. My 6-of-6 calibration could not have caught this, because planting a
defect presupposes a location, and the location is what I was choosing badly. §5 now
reports two numbers instead of one, and §7 proposes the method rule that follows.

---

## 1 · Findings

### L1 — The central claim is never derived, and the only gate on it tests a different proposition

**Severity: high. Confidence: high.**

`generic-dynamics:54-56` states the corpus's central bet:

> Each traditional regime of multiphysics is recovered as an **extraction** of this
> single equation.

`generic-dynamics:127-128` says where the derivation lives:

> The per-regime derivation of each extraction from the unified structure is
> [typed-compositions].

**`typed-compositions` contains no such derivation.** Mechanical check over the whole
page:

```
grep -n "GENERIC|δE|δS|δ/δ|extraction|Poisson|friction|dx/dt|equation of motion|generic-dynamics" \
  journals/oracle/registry/typed-compositions.md
→ one hit, line 108, `cell-metric-extraction` (an unrelated extractor name)
```

The page never mentions `L`, `M`, `δE/δx`, `δS/δx`, `dx/dt`, GENERIC, or
`generic-dynamics`. What it actually contains is a coverage table over a *different*
vocabulary — the computational-method and template alphabet — and it says so itself
(`typed-compositions:45-50`): *"That is the validation that the closed vocabulary covers
the target scope."* Covering the target scope with a method alphabet and deriving the
regimes from a metriplectic equation are different claims.

This is a **dangling promise** in the exact sense `traps:137-141` defines: the citation
resolves to a real page, so the structure checker passes, and the promised content is not
there.

It is not an isolated pointer slip, because the corpus's own consistency gate makes the
same substitution. `build-verification:59-61`, item 4 of "Internal consistency, checked
statically":

> The nine regime extractions ([generic-dynamics#nine-regimes]) are **realizable as typed
> compositions of the template and method vocabularies**.

That is the weaker proposition. "Every regime can be computed by our method alphabet"
does not entail "every regime is an extraction of `dx/dt = L δE/δx + M δS/δx`". The
corpus states the strong claim, points at a page carrying the weak one, and mechanically
checks the weak one.

Reinforcing evidence from the substrate itself: of the primitives `typed-compositions`
actually composes over — `StateReadoutOf`, `AlgebraicOf`, `SpectrumOf`, `ResponseOfTo`,
`KineticEvolutionOf`, `PathStationaryOf`, `ConvexOptimization`, `ClassifyOf`,
`ComparisonOf`, `MicrokineticSteadyStateOf`, `SecondDerivativeOf`, `SpectralAggregateOf`,
`RadiativeEmissionOf` — at most two (`KineticEvolutionOf`, and `ResponseOfTo` read as
linear response of the reversible flow) are plausibly extractions of a dynamical
equation. `ConvexOptimization(objective = lower-convex-envelope)`,
`PathStationaryOf(method = climbing-image-NEB)`, `ClassifyOf(classifier =
space-group-detection)` and `ComparisonOf(metric = atom-matching)` are hull
computations, path optimizations, classifications and comparisons. None is a readout of
a trajectory or a fixed point of the two-generator equation.

**What would refute this.** A page anywhere in the corpus that writes, for even one
regime, the reduction from `dx/dt = L δE/δx + M δS/δx` to that regime's governing
equation — naming which block of `L` or `M` is active, which variables are held, and
what limit is taken. I swept `journals/` for `extraction` (12 hits, all either the anchor
names on `generic-dynamics` itself, the `build-verification` gate, or unrelated
`extractor` identifiers) and found none.

**Proposed correction.** Either (a) write the reduction, per regime, on
`generic-dynamics` or a new page, and repoint line 127; or (b) retract the pointer and
downgrade the claim to what the corpus can support — that each regime is *expressible*
in the method alphabet, and that the GENERIC form is the organizing narrative rather
than a derived one. (a) is the honest version of the current claim; (b) is honest about
the current evidence. What is not defensible is the present state, in which the strong
claim cites a page carrying the weak one.

---

### L2 — Three of the nine regimes are energy-descending flows, which the stated degeneracy condition forbids

**Severity: high. Confidence: high (structural argument), medium-high per row (see
pending undergraduate returns).**

`generic-dynamics:47-48` states the second degeneracy condition and its meaning:

> `M · δE/δx = 0` (the dissipative part conserves energy).

Under it, `dE/dt = ⟨δE/δx, L δE/δx⟩ + ⟨δE/δx, M δS/δx⟩ = 0 + ⟨M δE/δx, δS/δx⟩ = 0` —
energy is conserved by **both** parts. A flow that *decreases* `E` in the tier's own
variables is therefore not an extraction of the equation as stated, unless the tier
carries an entropy/heat variable that absorbs the energy, or unless the tier is declared
single-generator.

`generic-dynamics:132-153` provides that escape for exactly one level — the
`born-oppenheimer-surface`, declared "single-generator (Hamiltonian) at fixed entropy".
It provides it for no other. Three rows of the nine-regime table nevertheless state
energy-descending or energy-non-conserving dynamics:

| line | row | the descent |
|---|---|---|
| `:120` | Electronic | "SCF as **gradient flow** on `E_KS`" — a gradient flow descends `E_KS` by construction |
| `:121` | Magnetic | "`M` (orientation-preserving relaxation `S × (S × H_eff)`)" — built from `H_eff = −δE/δS`, i.e. from the energy gradient, and relaxes toward it |
| `:125` | Chemical/surface | "Master equation on configurations (`M` = rate matrix)" — see L3 |

Note the asymmetry this creates on the Electronic row alone: the same line assigns two
mutually exclusive structures to the same level. `TDKS as Liouville on γ̂ (pure L)` is
energy-conserving; `SCF as gradient flow on E_KS` is energy-descending. Both are placed
at `quantum-electronic-substrate`, and the per-tier section reconciles neither.

**I tried to kill this and it survived — but the near-miss is the useful part.** The
strongest counter-reading is on the Electronic row. At finite temperature the
self-consistent solution is the stationary point of `Ω = E − TS − μN`, and relaxation
toward it *can* be written as entropy ascent at fixed energy: `dγ̂/dt = M δS_el/δγ̂` with
`M δE/δγ̂ = 0` drives the occupations to Fermi–Dirac. That flow **is** GENERIC-admissible,
the corpus has the entropy functional for it (`S_electronic`, `generic-dynamics:81`), and
it would make the row correct.

The corpus did not write that. It wrote gradient flow on **`E_KS`** — descent on the
energy, not ascent on the entropy at fixed energy. The two have different fixed points
(zero-temperature minimum versus the finite-temperature Fermi–Dirac state), and at `T = 0`
there is no entropy to ascend, so the `T = 0` reading is pure energy descent and admits no
rescue. The finding stands, and it stands more usefully for having a named correction
attached to it.

The same shape applies to the other two: the Magnetic row has a known GENERIC form once a
thermal/bath variable absorbs the energy the damping removes, and the Chemical row has a
known correct dissipative structure that is not the rate matrix (L3). In all three cases
the corpus is one rewrite away from correct, not one derivation away.

**What would refute this.** A statement anywhere that these three regimes sit at tiers
carrying a thermal variable, together with the entropy functional that makes the descent
`M δS/δx` rather than `M δE/δx`. `generic-dynamics:65-82` lists three entropy terms
(`S_vib`, `S_electronic`, `S_config`); none is assigned to the magnetic or electronic
descent, and `multiscale-state:270-272` states the slow tier "has **no reversible
bracket**" without supplying an energy channel for the chemical one.

**Proposed correction.** For each of the three rows, either state the tier's entropy
variable and rewrite the term as `M δS/δx` — for Electronic that is a one-line change to
"entropy ascent at fixed energy toward Fermi–Dirac occupations" — or declare the row a
single-generator contraction as the BO level already is. The second is cheap and honest;
the first is the physics.

---

### L3 — "`M` = rate matrix" is false, and it is consumed downstream

**Severity: high. Confidence: high.**

`generic-dynamics:125` — Chemical/surface regime: "Master equation on configurations
(**`M` = rate matrix**)".

`M` in GENERIC must be **symmetric** and **positive semidefinite**. A continuous-time
Markov generator is neither in general: it is non-symmetric (rates differ in the two
directions unless the equilibrium distribution is uniform), and its spectrum is
non-positive rather than non-negative, so if any sign convention makes it semidefinite it
is `−W`, not `W`. Detailed balance makes `W` *symmetrizable* by a diagonal similarity —
not symmetric.

This is not confined to a table cell. `multiscale-state:262-272` builds the slow-tier
residual on it:

> This is the slow-tier specialization of `‖dx_i/dt − (L·δE/δx_i + M·δS/δx_i)‖²`.
> Generation and annihilation are both branches of the single dissipative
> master-equation generator: **`M` is the rate matrix**, from the chemical and surface
> extraction of [generic-dynamics#operators]. The slow tier has **no reversible
> bracket**.

Two further consequences at that site:

1. With no reversible bracket, degeneracy gives `dE/dt = 0` on the slow tier — the slow
   tier conserves energy under its own dynamics. Defect kinetics does not: Frenkel-pair
   generation costs energy and annihilation releases it.
2. `G^q_total` includes `G_irradiation`, an **external source**. GENERIC as stated is a
   closed-system formalism; a rate law with an external source is not `M δS/δx` for any
   `M`.

*(Literature on the correct dissipative structure for reaction networks and Markov
chains — the Onsager operator is a state-dependent object built from the rates, not the
rate matrix — pending undergraduate return.)*

**What would refute this.** A demonstration that the corpus means by "rate matrix" the
Onsager/Mielke operator rather than the Markov generator. Nothing in either page
suggests it, and `multiscale-state` writes the right-hand side as the plain kinetic law
`G − c·k_ann`.

---

### L4 — Degeneracy is claimed "by construction" and is constructed nowhere; the only check on it has no tolerance

**Severity: high. Confidence: high.**

`residual-definitions:109-112`:

> `Degeneracy` — `‖L δS/δx‖² + ‖M δE/δx‖²`. **Cert-only**: under the per-tier generator
> structure ([generic-dynamics#per-tier-generators]) it is **identically zero by
> construction**, so it is a generator-construction-bug tripwire and never a
> training-loss term.

That claim is what removes the degeneracy term from the training loss. Two independent
problems.

**(a) The construction does not exist.** What the coupling generator's typed targets
enforce (`coupling-structure:296-304`) is: `AntisymmForm` invariants projected onto the
antisymmetric component, `PSDSymmForm` invariants onto the positive-semidefinite cone.
Those give antisymmetry of `L` and positive-semidefiniteness of `M`. Neither implies
either degeneracy condition — antisymmetry is a linear condition on `L` and says nothing
about the null space containing `δS/δx`; PSD is a convex-cone condition on `M` and says
nothing about the null space containing `δE/δx`. The two by-construction arguments
`generic-dynamics:140-153` does give cover the `γ̂` Lie–Poisson block and the
Born–Oppenheimer level. Neither says anything about the generated cross-blocks and
cross-kernels — the `Σ_c Σ_{v ∈ realize(c)}` terms at `generic-dynamics:95` and `:100`,
which are precisely the terms the coupling generator produces.

**The corpus states my mathematical claim itself, one section away, and then does not apply
it.** `generic-dynamics:161-164`:

> Generated `AntisymmForm` cross-blocks ([coupling-structure#target-shapes]) **conserve
> energy by antisymmetry** but do **not** automatically satisfy Jacobi — that is an
> additional condition.

That sentence enumerates what antisymmetry buys on the generated cross-blocks, and what it
buys is `dE/dt|_L = 0` — **not** `L δS/δx = 0`. The page is explicit that antisymmetry
delivers one property and that a second structural property on the same blocks is "an
additional condition". Degeneracy is a third such property, on the same blocks, and it is
the one granted "by construction".

**And the Jacobi treatment is the template the degeneracy claim should have followed — on
the identical objects.** `generic-dynamics:164-168` continues:

> V1 restricts them to the semidirect-product / Lie–Poisson class, where Jacobi holds by
> construction, **or flags them**. The "Jacobi verified" artifact of
> [build-sequence#phases] is exact for canonical blocks and **a cert-side numerical check
> for generated cross-blocks; it is not a global symbolic proof.**

For generated cross-blocks the corpus therefore: names the gap, restricts the admissible
class, keeps a flag for what falls outside, keeps a numerical check, and **disclaims the
proof in writing**. For degeneracy — same blocks, same generator, same learned
coefficients — it grants an unqualified "by construction", removes the training term on
that basis, and checks with an unvalued `≈ 0`. This is a sharper comparison than the PSD
one below, because PSD is a different property of a different operator while Jacobi is
*the same set of terms*.

The corpus's own asymmetry is the tell twice over. For positive-semidefiniteness,
`coupling-structure:670-681` is careful: closure is "**tight at the operator level**"
(a PSD `G`-invariant representative exists, because the Reynolds image of a PSD seed is
PSD — this is correct: `R(B) = (1/|G|) Σ_g ρ(g)ᵀ B ρ(g)` is an average of PSD matrices)
but "**loose at the coefficient level**", because "the operator learns the basis
coefficients and could transiently leave the cone during training", so a runtime guard is
kept. Degeneracy is a strictly stronger and unrelated condition on the *same learned
coefficients*, and it is granted an unqualified "by construction" with no guard.

**(b) The one check that exists has no tolerance.** The tripwire appears exactly once in
the corpus, at `cert-obligations:72`, written:

> the cert-only degeneracy tripwire `‖L δS/δx‖² + ‖M δE/δx‖² ≈ 0` per tier

`≈ 0` — no threshold. Corpus-wide sweep for a degeneracy tolerance returns that line and
nothing else. It is absent from the tolerance ledger (`cert-obligations:130-155`), which
`residual-definitions:367-369` declares canonical: *"Every numeric tolerance named across
this library is valued once, in the tolerance ledger … which is canonical for that
list"*, and which `cert-obligations` itself governs with *"A tolerance stated anywhere in
the corpus but absent from this table is a defect in this table."* Every other obligation
in the ten carries a named, valued threshold; obligation 6's degeneracy half is the sole
exception.

So the structural guarantee that the corpus says holds by construction is (i) not
constructed, and (ii) checked by the only unvalued comparison in the certification layer.
This is the by-convention-wearing-by-construction case in its purest form.

**(c) The rule that would have caught the unvalued threshold cannot see it.** The
tolerance ledger's preamble (`cert-obligations:128-129`) states the namespace rule: *"a
`τ_x` is a tolerance only if it appears in the table below. [conventions] owns that
namespace rule."* The rule is defined over **names of the form `τ_x`**. The degeneracy
tripwire is written `≈ 0` and carries no name at all, so there is no token for the rule to
range over. An unnamed threshold is invisible to a namespace rule by construction — which
is why this one is the sole exception in a ledger of 18 valued rows, all of the others
named.

**(d) `Degeneracy` is not a residual of the candidate state; it is a self-test of the
library** *(observation returned by the principal's sweep; I verified the character of
each of the 19 against `:78-200`).* Every other category scores a property of the state
the oracle is evaluating. `Degeneracy` scores a property of the **constructed operators
`L` and `M`** — and under the corpus's own claim its value is independent of the state
entirely. `:109-112` says as much: *"a generator-construction-bug tripwire"*. So the
corpus's only check that targets its own machinery rather than the candidate is the one
disabled by an assertion about that machinery. Removing it leaves the library with no
self-test in the residual vocabulary at all.

**What would refute this.** Either a construction I missed that forces `L δS/δx = 0` and
`M δE/δx = 0` on generated cross-terms, or a valued degeneracy tolerance somewhere in
the corpus. **The tolerance sweep is now closed and returns neither.** I read the
tolerance ledger in full (`cert-obligations:130-155`, 18 rows) and swept every
`degenerac*` occurrence in `journals/` (16 sites): the only threshold attached to the
GENERIC degeneracy conditions anywhere in the corpus is the unvalued `≈ 0` at
`cert-obligations:72`.

**Independent convergence, worth recording.** The certification subject reached (b) by a
different route and states it as its finding **F11** (`audit/findings/certification.md`,
§F11), arriving from the ledger side — obligation 6's two ledger rows are `τ_equiv` and
`τ_method`, both about formula-pair agreement, and neither bounds the tripwire. Two
subjects converging on the same defect from opposite ends is the strongest form of
confirmation available inside a desk audit, and it is worth more than either report alone.
F11 also proposes the repair I would: name it `δ_degen` and make it **relative** to
`‖L‖·‖δS/δx‖ + ‖M‖·‖δE/δx‖`, since the absolute form inherits the assembly's units —
the same defect L5 identifies in `δ_PSD`. I adopt that proposal rather than restating my
own.

**Proposed correction.** Value the tripwire in the tolerance ledger, in the relative form
above; and either restore `Degeneracy` to the training loss for the generated blocks, or
state the construction that makes it unnecessary there. The corpus's own treatment of PSD
— documented assumption, tight/loose closure, runtime guard, valued tolerance — is the
template.

---

### L5 — `δ_PSD = 1e-9 absolute` is not well-posed

**Severity: medium-high. Confidence: high.**

`cert-obligations:134`:

| `δ_PSD` | assembled-super-block negative-eigenvalue guard (obligation 2) | `1e-9` **absolute** |

`λ_min(M_block)` is a dimensional quantity — `M` is the friction operator, and no unit
convention for it is stated anywhere in the corpus. A corpus-wide sweep for a units
declaration finds only `Hartree` in prose on `generic-dynamics:70`, `τ_SCF` in Ha, and
the advisory `traps:233-236` entry saying the Maxwell `4π` "rides the unit system". The
state page declares per-slot units unspecified (`unified-state:74-80`: *"per-slot dtype,
**unit**, index order and memory layout are recorded nowhere"*).

Two consequences:

1. **Unit-dependence.** The guard's meaning changes with the unit system. Every other
   tolerance in the ledger that could be scale-free is relative — `δ_sym` 1e-6 relative,
   `τ_equiv` 1e-4 relative, `τ_adj` 1e-4 relative, `τ_cons` 1e-8 relative, `τ_interp`
   1e-10 relative. `δ_PSD` is the only dimensional one, and it guards a dimensional
   quantity.
2. **It fires on round-off at any physical scale.** For a symmetric block with entries of
   magnitude `A` in double precision, computed eigenvalues carry error `O(ε_mach·‖M‖₂) ≈
   1e-16·A`. Phonon-phonon and electron-phonon scattering kernels carry rates of order
   `1e12 s⁻¹`, giving an eigenvalue round-off floor around `1e-4` — eight orders above
   the `1e-9` guard. In Hartree atomic units the same block is `O(1)` and the guard is
   meaningful. The guard is therefore either vacuous or permanently tripped depending on
   a convention the corpus never fixes.

**Proposed correction.** Make it relative: `λ_min(M_block) ≥ −δ_PSD·‖M_block‖` or
`λ_min/λ_max ≥ −δ_PSD`, and state the unit convention for `M` on `unified-state` or
`generic-dynamics`.

---

### L6 — `EOM/Z` is defined over a slot the corpus declares immutable and discrete

**Severity: medium. Confidence: high.**

`residual-definitions:84-85`, category 7 of 19:

> `EOM/Z` — same form on atomic-number labels; non-trivial only under
> **chemistry-active dynamics**, otherwise structurally null.

The "same form" is `‖dx_i/dt − (L δE/δx_i + M δS/δx_i)‖²`.

`unified-state:34` declares the slot:

> `Z_I,    species labels (**immutable**)         **discrete**`

and `multiscale-state:157` confirms it as a decision, not an accident:

> The species labels stay immutable ([unified-state#slots]) — atomic-number identity does
> not change as a vacancy forms

Three consequences:

1. **Flat contradiction.** A slot cannot be immutable and also carry "chemistry-active
   dynamics". `residual-definitions` lists `unified-state` in its `depends-on`.
2. **The residual is ill-typed, not merely null.** `δE/δZ` is a functional derivative
   with respect to a discrete label; there is no differentiable structure on an index set
   to take it over. The residual is not zero-valued, it is undefined.
3. **It inflates the closed vocabulary.** `CategoryTag` is declared a closed set of 19
   (`residual-definitions:204-207`), and that count is load-bearing elsewhere. One member
   can never be instantiated.

**Corroboration from the page's own granularity list** *(returned by the principal's
disjointness sweep; I verified the arithmetic myself).* `:254-255` enumerates what becomes
a separately-weightable contribution:

> The equation-of-motion violation per state component `i ∈ {h, R_I, P_I, Π_h, γ̂, A}`

**Six components. `Z` is absent.** The category list at `:78-85` gives seven micro
equation-of-motion categories, one per slot; the granularity list that says what is
actually emitted gives six. So the page contradicts itself on the count, and the side
that describes emission is the side that omits `Z`. The arithmetic: `9 + 3 + 5 + 2 = 19`
and `17 + 2 = 19` both check out **as counts of listed names**, so the total is internally
consistent — the defect is that one of the names denotes nothing emittable. Struck, the
vocabulary is **18**.

**The mechanism, which is worth more than the instance.** `:75-76` states the generation
rule — *"Seven per micro state-component degree of freedom ([unified-state#slots])"* — and
`unified-state` declares exactly seven slots, of which `Z` is the one typed discrete and
immutable. The defect was not authored; it was **generated by a schema symmetry applied to
a slot that does not support it**. That is a class: any "one X per slot" rule in this
corpus inherits the same exposure wherever a slot is not a differentiable manifold.

**What would refute this.** A page declaring `Z` relaxable to a continuous alchemical
coordinate (as in alchemical-derivative / thermodynamic-integration schemes). I found
none; `multiscale-state:153-160` takes the opposite route, promoting
`SiteDecoration.occupancy` into a slow fiber precisely so that `Z` need not move.

---

### L7 — `ion-ion electrostatic` is in the MVP coupling spec, absent from the channel table, and unrepresentable in the schema

**Severity: high. Confidence: high.**

The MVP `CouplingSpec` names four channels, in two places:

- `generic-dynamics:75-77`: "MVP set: electron-phonon, minimal coupling, **ion-ion
  electrostatic**."
- `coupling-structure:424-426`: "electron-phonon (short-range) + minimal coupling +
  **ion-ion electrostatic** + phonon-phonon scattering in `M`".

`coupling-structure:566-585` presents "The coverage-policy template table — **the 15
principled channels**". I enumerated all 15: electron-phonon (deformation-potential,
Fröhlich, piezoelectric acoustic), spin-orbit, magneto-elastic, minimal coupling,
phonon-phonon, radiative damping, exchange/Heisenberg, Zeeman, Stark, strain-electronic,
screened Coulomb, GW, TDDFT. **`ion-ion electrostatic` is not among them.** Under the
page's own coverage rule (`:486-488`) the active channels are those whose applicability
holds and whose invariant basis is non-empty — a channel with no template cannot be
active, so the MVP composition activates a channel the policy does not contain.

Worse, the schema cannot carry it either. The ion-ion interaction is bare Coulomb; the
corpus's own `MechanismRange` doc (`:540`) names the "**bare-Coulomb head**" as an
instance of `LongRangeStatic`. So `polynomial_sufficient = false` (`:548-554`), and the
well-formedness invariant at `:556-558` requires a `kernel_extension`. But `KernelExt.tag`
is a closed four-variant enum (`:605-606`):

```
tag : FroehlichLongRange | ScreenedCoulombRPA | GWQuasiparticleSelfEnergy | TDDFTXCKernel
```

None is the bare ion-ion Coulomb/Ewald head, and the generator contract at `:183` errors
on a mismatch: `if ¬polynomial_sufficient(c) ∧ ¬kernel_tag_matches_range(c): error
"kernel tag ≠ mechanism_range"`. The MVP's own channel is therefore unconstructible.

The result holds under the alternative reading too. In a charge-neutral crystal the
monopole `1/q²` head is canceled by the compensating background and what survives is the
dipole–dipole term, which is homogeneous of degree **0** in `q` but *direction-dependent*
at `q → 0` — the non-analytic term that produces longitudinal-optical/transverse-optical
splitting. `MechanismRange` carries only a scalar `pole_order` and cannot express a
degree-0 direction-dependent limit; and `polynomial_sufficient(LongRangeStatic(0)) =
true` (`:551`, *"a constant 'pole' is just a coefficient"*) would classify it as
polynomial-sufficient and then *forbid* it a kernel extension.

**Mitigating fact, checked.** The corpus does carry the LO-TO physics — but on a
different mechanism entirely: `born-oppenheimer-levels:79` lists "the
longitudinal-to-transverse-optical non-analytic correction" as a `one-shot-dressing`, and
`residual-machinery:73,248` carries a `LO-TO-NA-correction` dressing scheme. So
long-range non-polynomial physics reaches the corpus by two unrelated routes —
`KernelExt` on a coupling channel, and the dressing machinery — and **no page states
which physics goes down which route or why**. Fröhlich (a `KernelExt`, parametric in
`ε_∞, ε_static, Z*, ω_LO`) and LO-TO-NA (a dressing, parametric in Born charges) are two
matrix elements of the same underlying long-range Coulomb interaction and must share
`Z*`, `ε_∞` and `ω_LO`; nothing binds them.

**Third consequence, found on resumption: the gauge partition names this channel as an
owner of the longitudinal sector, and the page also gives that energy a different home.**
`generic-dynamics:189-193`, in the section marked **Normative**:

> The **longitudinal / electrostatic sector is owned by the matter functionals** — the
> Hartree term inside `E_KS[γ̂]` **and the ion–ion electrostatic channel** — and appears
> nowhere in `E_EM`, so no electrostatic energy is double-counted.

So the partition that keeps electrostatics out of `E_EM` assigns half of it to a channel
that is not in the template table and cannot be built in the schema. But 17 lines earlier,
`:172`, the same page puts the ion–ion energy somewhere else entirely:

> At `quantum-electronic-substrate` the active electronic energy is `E_KS[γ̂; R₀, h₀]` …
> carrying `∫ v_ext(R)·n + **V_II(R,h)**`

`V_II` is the ion–ion Coulomb energy, and here it rides inside `E_KS`. **One of the two
statements is wrong**, and the page never reconciles them:

- If `V_II` lives in `E_KS` (`:172`), then the `:192` clause names a second owner for
  energy already owned, and a constructible ion-ion channel would **double-count** it —
  in a passage whose whole purpose is to prove nothing is double-counted.
- If `V_II` lives in the channel (`:192`), the owner does not exist, and the longitudinal
  ion–ion sector is homeless: excluded from `E_EM` by the partition and assigned to a
  channel absent from the 15-row table.

The page knows how to state the disambiguation, because it states it for the neighboring
channel: `:179-182` says the electron-phonon channel contributes "the linear-order
cross-term … and the **beyond-reference part** of `E_coupling` — **not** the full
electron–ion energy." **No analogous sentence exists for ion-ion.** So the convention that
would resolve the double-count is stated once, for one channel, and not generalized.

*This is desk-provable and independent of whether the channel is constructible*, which
makes it the part of L7 that survives even if the schema is extended.

**Proposed correction.** Add the ion-ion electrostatic row to the template table with its
`mechanism_range`, and either extend `KernelExt.tag` with an Ewald/bare-Coulomb variant
or state explicitly that ion-ion electrostatics is carried outside the coupling machinery
(as LO-TO already is) and remove it from the two `CouplingSpec` lists. Separately, state
the routing rule between `KernelExt` and `one-shot-dressing`, and bind the shared
coefficients.

---

### L8 — `Polish` names two disjoint training bands across a seam both pages cite

**Severity: high. Confidence: high.**

`residual-definitions:281-289` — the residual-category gate:

```
[0.00, 0.10)  Warmup
[0.10, 0.60)  Refine
[0.60, 0.90)  Polish
[0.90, 1.00]  Cooldown
```

`residual-loss-design:327-332` — the source-weight curriculum:

| Warm-up, 0 to 0.10 | Refine, 0.10 to 0.60 | **Calibrate, 0.60 to 0.90** | **Polish, 0.90 to 1.00** |

`Polish` is `[0.60, 0.90)` on one page and `[0.90, 1.00]` on the other. The two bands are
disjoint. Both pages are canon, both cite each other over this exact seam
(`residual-definitions:313`, `residual-loss-design:339-341`), and both explicitly observe
that they "share their endpoints and they gate different things" — neither notices that
they also share a *name* that resolves to different intervals.

The corpus declares this as an open question, and **the declaration mis-describes it**.
`residual-definitions:49-51`:

> a further vocabulary substitutes **Calibrate for Cooldown**. The phase set is not
> agreed across the seam.

That is not what happened. The operator's vocabulary is *rotated*, not substituted:
`Calibrate` occupies the band the oracle calls `Polish`, and `Polish` occupies the band
the oracle calls `Cooldown`. A reader who reads the open question concludes two names
exist for one fourth phase — benign. The actual hazard is that a live name on both sides
of the seam binds to two disjoint intervals, so an operator implementer who reads
"Polish" and applies the oracle's Polish gate turns on `Algebraic/MethodEquivalence`,
`Static/Snapshot` and `Static/Thermodynamic` in the wrong third of training. The declared
open question conceals the only dangerous part of the disagreement.

**Proposed correction.** Beyond resolving the phase set: rewrite the open-question summary
to name the collision. A declared gap that understates its own hazard is worse than an
undeclared one, because it is read as already triaged.

---

### L9 — Obligation 6 cannot implement the equivalence-pair semantics it is cited for

**Severity: medium-high. Confidence: high.**

`residual-definitions:162-164` defines the equivalence pair as a **numerical** agreement:

> binds two formulas that share an *agreement theorem*, and trips on any disagreement
> beyond `τ_equiv`, the **numerical-agreement grade**

`cert-obligations:138` values it: `τ_equiv` = `1e-4` **relative**.

`cert-obligations:72`, the obligation that enforces it, states a **symbolic** check:

> two formulas claiming one quantity agree on the shared domain (**compare formula trees
> and coefficients** within tolerance)

Comparing formula trees is not comparing computed values. The corpus's own worked instance
makes the gap concrete — `typed-compositions:213-249` binds `ConductivityViaBTE`
(`KineticEvolutionOf`, `method = BTE-RTA`) to `ConductivityViaKubo` (`ResponseOfTo`,
`kernel = current-current-correlator`, `frequency = ω→0⁺`) and calls it "the worked
instance of that obligation". Those two are structurally different expressions; their
formula trees do not match under any tolerance, while their computed conductivities may
agree well. A tree-comparison implementation fails the pair it exists to certify, and
passes nothing.

*(Whether an agreement theorem exists for that pair at all, and whether `1e-4` relative is
attainable between two independent Brillouin-zone integrals, is pending undergraduate
return.)*

---

### L10 — `generic-dynamics` states the `γ̂` bracket in the form it later says is wrong, and states it without the factor that makes it a bracket

**Severity: medium. Confidence: high.** *(Inherited contradiction, unrepaired through the
restructure — `audit/inherited/contradictions.md`, `oracle-laws-seams` row 3.)*

Self-contradiction, live, on one page:

- `generic-dynamics:92`, the operator table: `· Liouville–von Neumann on γ̂   (1/iℏ) [Ĥ_KS, ·]`
- `generic-dynamics:142-143`: "written `[·, γ̂]` **not** the bare `[Ĥ_KS, ·]`"

The table states exactly the form the later section corrects, and gives the reason
(Jacobi and degeneracy hold by construction only in Lie–Poisson form). The inherited
register flagged this before the restructure; it survives verbatim.

Second, independent defect at the same site. `generic-dynamics:140-143` writes the
bracket as

> `{A,B}(γ̂) = Tr( γ̂ · [δA/δγ̂, δB/δγ̂] )`, giving `∂γ̂/∂t = −(i/ℏ)[Ĥ_KS, γ̂]`

The bracket as written does not give the stated equation of motion. Derivation, with
`X = δA/δγ̂`:

```
dA/dt = Tr( X · dγ̂/dt )                                     definition
Tr(γ̂[X,Ĥ]) = Tr(XĤγ̂) − Tr(Xγ̂Ĥ) = Tr(X[Ĥ,γ̂])              cyclicity
```

so the written bracket `{A,E} = Tr(γ̂[X,Ĥ]) = Tr(X[Ĥ,γ̂])` yields `dγ̂/dt = [Ĥ_KS, γ̂]` —
missing the `1/(iℏ)`. Reading it backwards from the stated result, the bracket must carry
that prefactor:

```
dA/dt = Tr( X · (−i/ℏ)[Ĥ,γ̂] ) = (−i/ℏ) Tr(γ̂[X,Ĥ])   ⟹   {A,B} = (1/iℏ) Tr(γ̂[δA/δγ̂, δB/δγ̂])
```

The omission is not cosmetic: for Hermitian `X, Y` the commutator `[X,Y]` is
anti-Hermitian, so `Tr(γ̂[X,Y])` is purely **imaginary**. As written the expression is not
a real-valued Poisson bracket at all. Dividing by `i` is what makes it real.

The same omission propagates to the degeneracy line at `:145`, which writes
`L_γ̂·δS_el/δγ̂ = [δS_el/δγ̂, γ̂]` where the operator is `(1/iℏ)[·, γ̂]`. There the factor
is harmless because the quantity is set to zero — and the degeneracy argument itself is
**correct**: for `S_el = −k_B Tr[γ̂ ln γ̂ + (1−γ̂)ln(1−γ̂)]`, `δS_el/δγ̂ = −k_B[ln γ̂ −
ln(1−γ̂)]`, a function of `γ̂` alone, which commutes with `γ̂`. ✓

**Proposed correction.** Delete or repair the table row at `:92`; add the `1/(iℏ)`
prefactor at `:140`.

---

### L11 — Onsager reciprocity is named with no form, in a corpus that computes Hall mobility

**Severity: medium-high. Confidence: high on the omission; **the consequence analysis is
now closed** — see the addendum. Previously marked pending undergraduate return.**

`residual-definitions:152-154`, category 14 of 19, in full:

> `Algebraic/Symmetries` — Onsager reciprocity; Maxwell relations; space-group
> equivariance of response tensors.

No equation. Onsager reciprocity in the presence of a magnetic field or a magnetization
is `L_ij(B) = L_ji(−B)` (Onsager 1931; Casimir 1945), **not** `L_ij = L_ji`. The corpus
carries `A` (the electromagnetic vector potential) as a state slot, lists `Magnetic` as
one of the nine regimes, and carries a `Zeeman` coupling channel. A residual implementing
naive symmetry of the transport matrix scores correct physics as a violation wherever
`B ≠ 0`.

Corpus-wide sweep for the field-reversal statement: `Onsager` appears at three sites
(`residual-definitions:152`, `typeclass-alphabet:100` "Onsager involution",
`coupling-structure:658` "Onsager/detailed-balance"). None states the argument reversal.
`typeclass-alphabet:100`'s "Onsager involution" is the closest, and an involution is
precisely what `B → −B` is — but the page names it without saying what is involuted.

The inherited register recorded this same gap before the restructure
(`audit/inherited/contradictions.md`, `appendix-a`: *"`residual-definitions:143` names
'Onsager reciprocity' with no form at all, so canon inherits the ambiguity without a way
to detect it"*), and it survives.

**Addendum — the consequence is live, not hypothetical, and it closes from the desk.** My
first draft left "does `B ≠ 0` actually arise here?" to an undergraduate. It does, and the
corpus answers it three ways:

- **`observable-bundles:68` lists `Hall mobility`** among the transport-bundle
  observables. The Hall coefficient *is* the antisymmetric part of the conductivity
  tensor; there is no Hall mobility at `B = 0`.
- **`coupling-structure:240` and `:580` carry `Zeeman`** as one of the 15 principled
  coupling channels, with `mechanism_range = ShortRange`, `polynomial_sufficient = true`.
- **`out-of-scope` excludes no magnetic-field case.** Control: I swept that page for
  `magnet*` and it returns **zero** hits, while the same sweep over `journals/` returns
  the Zeeman channel, the magneto-elastic channel and the Magnetic regime row — so the
  instrument finds magnetism where it exists, and the exclusion genuinely is not there.

So a residual implementing `L_ij = L_ji` scores the corpus's own Hall observable as a
violation, and the magnitude is not small: at `B ≠ 0` the antisymmetric part is the entire
Hall signal.

**This shares a root cause with L18**, and the two should be repaired together. `σ ⪰ 0` in
category 10 is not a well-defined test on a tensor with an antisymmetric part — the
eigenvalues are complex, so `λ_min(σ) ≥ 0` has no meaning — for exactly the reason
`L_ij = L_ji` is the wrong reciprocity statement. One correction covers both: state the
transport-symmetry conditions on the **symmetric part**, and state Onsager as
`L_ij(B) = L_ji(−B)`.

---

### L12 — The Thermal row writes the unweighted Hessian, contradicting the template page that owns the object

**Severity: low-medium. Confidence: high.** *(Downgraded and partly retracted — see the
correction note. My first version of this finding was wrong about `typed-compositions`.)*

`generic-dynamics:119`, Thermal regime: "**Eigendecomposition of `∂²E_BO/∂u²`**
(phonons)."

Phonon frequencies are eigenvalues of the **mass-weighted** dynamical matrix
`D_{IαJβ}(q) = (1/√(M_I M_J)) Σ_R Φ_{IαJβ}(R) e^{iq·R}`, not of the force-constant
Hessian. `∂²E_BO/∂u²` as written is the Hessian, and nothing on that line says `u` is a
mass-weighted displacement.

**Correction to my own finding.** I first reported this as a corpus-wide omission
propagating through `typed-compositions:180-181`. That is wrong, and a control probe
caught it: `property-templates:82` defines the template

> `HarmonicStiffnessHessianOf` | **the mass-weighted dynamical matrix**

and its signature (`:157-159`) takes an explicit `displacement-basis: Basis`. So
`typed-compositions`'s composition is correct — it invokes the template by name, and the
template carries the mass weighting. A reader following the corpus reaches the right
object.

What survives is narrower and is a **contradiction rather than an omission**: the Thermal
row on `generic-dynamics` writes the raw Hessian where the page that owns the object
specifies the mass-weighted dynamical matrix. For diamond the difference is a uniform
`1/M` scale on `ω²` with correct eigenvectors; for GaN, AlN, β-Ga₂O₃ and AlGaN the mass
weighting is not a scale factor and the eigenvectors differ too. The exposure is a reader
who takes the laws page literally without following through to the template.

Related but distinct, and still standing: `traps:227-231` guards the `√(2Mω)` single-mass
shorthand for the electron-phonon **vertex** as *advisory*. That entry is about a
different object and does not cover this line.

**Proposed correction.** One line: replace `∂²E_BO/∂u²` with the mass-weighted dynamical
matrix, or name the template.

---

### L16 — "Degeneracy" carries four meanings, and one collision makes an unenforced guarantee read as enforced

**Severity: upgraded from low to medium — see (b). Confidence: high.**

The corpus reserves a mechanism for exactly this — `glossary#overloaded`, backed by
`traps:660-669` (*"A short token collides with real physics"*) and `traps:671-679` (the
`GAP` collision). **`degeneracy` is not in it**, and it carries four unrelated meanings
here:

1. **GENERIC degeneracy** — the conditions `L δS/δx = 0`, `M δE/δx = 0`, and the residual
   category named `Degeneracy` (`residual-definitions:109`).
2. **Carrier degeneracy** — the doping threshold at which non-degenerate statistics fail:
   `multiscale-state:394` (*"crosses the host's degeneracy threshold"*),
   `traps:522-529`, `out-of-scope:55`.
3. **Eigenvalue degeneracy** — repeated eigenvalues, which is where `λ_min` stops being
   differentiable and which symmetry makes generic in a cubic crystal.
4. **Valley degeneracy** — `mvp-system:45`, *"The six-fold Δ valley degeneracy is what the
   effective-mass and transport rows consume."* A band-structure multiplicity, and the
   corpus's MVP material depends on it numerically.

**(a) The sweep hazard, met directly.** A sweep for a tolerance attached to GENERIC
degeneracy returned `multiscale-state:394`'s carrier-degeneracy threshold, which is sense
2. The sweep survived because I read the hits, but this is precisely the failure the
register describes — *"a sweep over one vocabulary silently collects rows from another,
and none of the four is wrong, so nothing fires."*

**(b) One collision has a consequence, and this is why the severity moves.**
`architectural-principles:63-66`, under the heading "Loud at compose time, absent at
runtime":

> **A degeneracy the oracle cannot stand behind is caught at compose time and refused
> with a numeric witness.**

Bound to sense 1 — and the corpus has a residual category literally named `Degeneracy`,
so that binding is the one a reader reaches for first — this sentence says a violated
GENERIC degeneracy condition is **caught at compose time and refused**. It is not.
`residual-definitions:109-112` makes `Degeneracy` a **runtime, cert-only** tripwire, and
`cert-obligations:72` files it under obligation 6, a certification obligation evaluated on
a compiled kernel, not a compose-time refusal. **The word collision manufactures the
impression that the guarantee L4 shows is unconstructed is enforced by the strongest
mechanism the corpus has.**

The charitable reading — that the sentence means a generic "degenerate case" — does not
rescue it, because that sense is unbound too: it is the one sense with no site anywhere
that defines it. Either way a reader on the corpus's own architectural-principles page
cannot determine what is refused at compose time.

**What would refute (b).** A qualifier at `architectural-principles:65` naming which
degeneracy, or a page stating that GENERIC degeneracy violations are compose-time
refusable. I found neither; `build-sequence:63` lists "degeneracy verified" as a phase-8
artifact, which is a build-time *verification* claim and not a refusal mechanism, and
`generic-dynamics:136` points at it as the thing the by-construction argument is meant to
discharge.

**Proposed correction.** Add `degeneracy` to `glossary#overloaded` with the four readings
and one reserved sense. This costs one row and it is the mechanism the corpus already
built. Separately and more urgently, qualify `architectural-principles:65` — that sentence
is load-bearing for the corpus's central promise and it currently reads as a guarantee the
corpus does not implement.

---

### L13 — Absorption is attributed to the dissipative operator; every other page computes it from the reversible response

**Severity: medium-high. Confidence: high.**

`generic-dynamics:122`, Optical regime:

> Response of `γ̂` to `A(t)` via `L`; **absorption via `M` (radiative damping)**

Two defects.

**(a) Absorption is not radiative damping.** Optical absorption in a solid is the
transfer of energy from the field into electronic excitations — `α(ω) = ω ε₂(ω)/(n c)`,
with `ε₂` the imaginary part of the response function. Its finite width in an extended
crystal comes from the *continuum of final states*, not from a friction operator.
Radiative damping is a different process: radiation reaction / spontaneous emission, the
*emission* channel. The corpus itself keeps them separate — the 15-channel table
(`coupling-structure:566-585`) carries `radiative damping` and `minimal coupling /
light-matter` as two distinct channels, and absorption belongs to the second.

**(b) It contradicts the corpus's only actual specification of how absorption is
computed.** `typed-compositions:143-148`:

```
DielectricFunction = ResponseOfTo(observable = γ̂, perturbation = A-ext,
                                  kernel = current-current-correlator, frequency = ω-mesh)
Absorption(ω)      = AlgebraicOf({DielectricFunction}, formula = absorption-from-dielectric)
```

A current-current correlator is a linear-response object built from the Hamiltonian
dynamics. No `M` appears, and no radiative-damping channel is invoked. Corpus-wide sweep:
`absorption` appears at `generic-dynamics:122` and at four sites on
`typed-compositions` — nowhere else in `journals/oracle/laws/`. The regime table and the
composition disagree about which generator produces the observable.

*(The transcribed form at `typed-compositions:310`, `α(ω) = (2ω/c)·Im(√ε)`, is correct:
`α = 2ωk/c` with `k = Im(√ε)` the extinction coefficient. Checked.)*

**Proposed correction.** Rewrite the row as response-via-`L`, with `ε₂` from the
current-current correlator, and reserve `M`/radiative damping for emission. If the
intent was that radiative damping supplies the *linewidth*, say that, and say it is not
the absorption mechanism.

---

### L14 — The curriculum fractions are inherited from a different schedule, and the rationale given for Warmup admits a trivial minimizer

**Severity: medium. Confidence: high on provenance; medium on the training consequence
(stated caveat below).**

**(a) Provenance.** The lead asked whether `0.10 / 0.60 / 0.90` is physically motivated or
inherited. It is inherited, and from a schedule that gates something else.
`residual-loss-design:327-338` uses the same three fractions for a **source-weight**
curriculum and gives them literature backing: *"This mirrors cascaded multi-fidelity
training and composite-loss curricula"*, with `:448-450` citing Meng & Karniadakis 2020,
Lu et al. 2022, Howard et al. 2022 and Elhamod et al. 2022. Those papers schedule the
relative weight of *data sources* (cheap → high-fidelity → experiment).

`residual-definitions:276-296` reuses the identical fractions to gate **which residual
categories participate** — a different object — and carries **no citation at all**; the
page has no external references. Its rationale (`:291-296`) is qualitative and motivates
an *ordering*, not these values: nothing in it would change if the boundaries were
0.05/0.50/0.95.

The corpus declares the coincidence as an open question in two places
(`training-stages:26-28`, `residual-loss-design:52-53`), but both ask *"is this one
schedule or two?"* Neither asks the question that matters here: where the numbers came
from, and whether they mean anything for category participation. They do not.

**(b) The Warmup rationale is unsound as written.** `residual-definitions:291-293`:

> Warmup keeps the network on hard physical constraints before the equation-of-motion
> surface, which dominates the loss landscape, turns on

Warmup admits `Conservation` + `Positivity` only. Consider the frozen trajectory
`x(t) = x(0)` with an admissible `x(0)`: every conserved quantity is constant, so every
`Conservation` residual is exactly zero; every `Positivity` bound holds, so every
`Positivity` residual is exactly zero. **The Warmup objective has a trivial global
minimizer that is maximally wrong dynamically** — "predict that nothing changes." The two
categories chosen to run before the dynamics turns on are precisely the two that a frozen
prediction satisfies perfectly. They are not "hard physical constraints" that shape the
dynamics; they are constraints the absence of dynamics satisfies.

**Caveat, stated because it is load-bearing.** This does not by itself predict a training
failure, because data supervision runs concurrently: `residual-loss-design:329` gives
Warm-up *"cheap high, residual weights moderate"*, so labeled data provides gradient
during the same window. The defect is in the oracle's **stated rationale** — which
presents these two categories as doing work they cannot do — and in the fact that the
oracle publishes this as the normative default schedule. A reader who follows the
rationale and raises residual weight during Warmup to "enforce hard constraints early" is
strengthening a pull toward the frozen solution.

**Proposed correction.** Either state the honest reason for Warmup's category set (they
are cheap and they are snapshot-checkable, so they cost little while the data terms do
the work), or move a category into Warmup that a frozen trajectory does not satisfy.
Separately, state that the fractions are inherited and carry no independent justification
for category gating — a number reused across two schedules should say so where it is
reused.

---

### L15 — The slope-kind guard cites Engel for two values the corpus's own ledger records Engel as reporting differently

**Severity: medium. Confidence: high on the mis-attribution; the correct values need the
papers (see §4).**

`coupling-structure:369-373`:

> The curated zero-point-renormalization amplitudes feeding the `coth` path
> ([accuracy-ledger#ahc-zpr]) are the **isochoric** electron-phonon values, tagged
> `isochoric`: **GaN −189 meV and AlN −399 meV (Engel PRB 106 094316 (2022); Miglio npj
> Comput. Mater. 6 167 (2020))**, diamond −345 meV indirect (Antonius PRL 112 215501
> (2014)).

The page it cites as owner records something different. `accuracy-ledger:225-227`, column
header "Isochoric (meV)":

| GaN | **−189 (Engel −171)** | … | Engel PRB 106 094316 (2022); Miglio npj CM 6 167 (2020); Nepal APL 87 (2005) |
| AlN | **−399 (Engel −377)** | … | Engel 2022; Miglio 2020 |
| diamond, indirect | **−345 (band −320…−366)** | … | Antonius PRL 112 215501 (2014); **Engel −323** |

The ledger carries the curated value *and* the disagreement. `coupling-structure` restates
the curated value and attaches **both** citations to it, dropping the recorded fact that
Engel reports −171 and −377, an 8–10% difference. The diamond row loses two complements:
the band spread −320…−366 and Engel's −323.

This is detectable inside the corpus without opening a paper, because the ledger states
both numbers. It is the corpus's own named hazard realized on my page —
`traps:743-754`, *"A number quoted without its complement … when a result is a
comparison, quote **both arms**"* — and it is the mis-citation class the brief warns the
2026-06-10 re-audit missed.

Two smaller defects at the same site:

- `coupling-structure:361-363` — *"they already fold in the lattice-expansion part that
  registry row 63 … carries separately, **which is 30–40% of the shift**"*. Corpus-wide
  sweep: that fraction appears at this one site and carries **no source and no
  uncertainty**. It is checkable against the ledger's own numbers and does not survive
  cleanly: GaN `49/238 = 21%`, AlN `85/484 = 18%`. Neither is in 30–40%. The claim is
  either about a different quantity than the ledger's rows or it is wrong; as written a
  reader cannot tell which.
- The five ZPR values are duplicated across an ownership boundary at all.
  `accuracy-ledger#ahc-zpr` owns them; restating them on `coupling-structure` is what let
  the Engel attribution drift. (Structure is not my subject, so I note the mechanism and
  do not pursue it.)

**What would refute this.** Engel PRB 106 094316 (2022) reporting −189/−399 after all,
which would make the ledger's parenthetical the error rather than this page's citation.
Either way one of the two pages is wrong, which is the finding.

**Proposed correction.** Attribute −189/−399 to Miglio alone, or write both values as the
ledger does. Source the 30–40% claim or delete it.

---

### L17 — The 19 categories are not disjoint, and the schema requires them to be

**Severity: high. Confidence: high.**
*(Sweep run by the principal after my draft closed; **the gap §6 named as the one that
most weakened this subject**. I have re-verified every overlap against the primary text
myself and re-derived the two physics implications — what is mine and what is theirs is
marked per item. The sweep's own calibration is reported in §5.)*

**The schema makes multiple categorization unrepresentable.** `residual-definitions:216-235`:

```
ResidualKey = (producer : Producer, axes : Tuple<AxisLabel>)

ContributionFacets =                         -- sidecar; not part of identity
  ( category : CategoryTag                   -- one of the 19 categories
  , … )
```

with `:229-230` — *"Facets are exposed through a parallel `Map<ResidualKey,
ContributionFacets>`"* — and `:234-235` — *"`ContributionFacets` is the value type of a
typed sidecar fiber and **never participates in `ResidualKey` identity**."*

`category` is a single `CategoryTag`, not a set; the facet map is keyed on `ResidualKey`;
and facets are excluded from key identity. So `category` is a **total single-valued
function on `ResidualKey`**, and the 19 categories must partition the emitted
contributions. Two contributions differing *only* in category collapse to one key, and a
map holds one value per key.

That makes overlapping category definitions unimplementable, and forces one of two
branches at every overlap — **neither of which the page ever chooses**:

| branch | how | consequence |
|---|---|---|
| **A — two producers** | the condition is emitted under two `NamedFormula`s | two keys, two categories, **two independent weights**: the condition is scored twice, at two curriculum gates, under whichever applicability mask each site happens to declare |
| **B — one producer** | one `NamedFormula` | one key, one facet record, one category: the second membership is **unrepresentable and silently dropped**, and nothing records which of the two survived |

**The page's only disjointness argument covers one pair out of 171.**
`residual-definitions:198-200`, in full:

> Categories 16 and 17 stay disjoint because they consume type-distinct inputs —
> snapshot versus snapshot-plus-environment — and the curriculum schedules them
> differently for that reason.

`C(19,2) = 171`. One pair is argued; 170 are asserted by silence. And the root cause is
visible in the page's own construction: **categories 8–15 are defined by enumeration**
(a list of named conditions) **and 16–17 by an input-type predicate**. A
predicate-defined category captures members of an enumeration-defined one whenever they
satisfy the predicate, and nothing in the page prevents it.

Six overlaps follow.

---

**(1) `ω² ≥ 0` in `Positivity` is "dynamical stability" in `Static/Snapshot`. This is the
one with teeth.**

- `:119`, category 10 — `Positivity` — … `ω² ≥ 0` …
- `:183`, category 16 — `Static/Snapshot` — … `elastic-stability-criteria`, **dynamical
  stability**, …

Dynamical stability of a crystal *is* the condition that every phonon frequency is real,
`ω²(q,ν) ≥ 0`. One physical condition, two categories.

The two copies **gate at different training fractions**, and the gate is cumulative
(`:284-286` reads "add"), so from 0.60 both are live at once:

| copy | category | first active |
|---|---|---|
| `ω² ≥ 0` | `Positivity` | **0.00** (Warmup — "Conservation + Positivity only") |
| dynamical stability | `Static/Snapshot` | **0.60** (Polish) |

**And the two copies carry different applicability masks.** The `Positivity` copy is
gated, with the reason stated (`:121-123`):

> `ω² ≥ 0` is **applicability-gated** to phases claimed dynamically stable, so it does
> not penalize the legitimate saddle and transition configurations a trajectory must
> traverse.

The `Static/Snapshot` copy at `:183` carries **no gate**. So from fraction 0.60 the
ungated duplicate penalizes exactly the configurations the gate was installed to protect.
**The gate installed to prevent a spurious penalty is bypassed by the duplicate.**

**And the penalized object is one the corpus computes by name, so this is concrete rather
than hypothetical.** `typed-compositions:230-241`:

```
ν_saddle = SpectrumOf(HarmonicStiffnessHessianOf(E_BO, saddle), …)
         … StateReadoutOf(ν_saddle, product-of-modes)
         … PathStationaryOf(…, method = climbing-image-NEB, n_images = 9)
```

The corpus computes the harmonic spectrum **at the saddle** and reduces it by
`product-of-modes` — harmonic transition-state theory, whose prefactor is defined only
because the saddle has **exactly one imaginary mode**. `ω² < 0` there is not an error
state; it is the quantity's defining feature, and the corpus values a tolerance for
reaching it (`τ_NEB` = `1e-3`, `cert-obligations:147`). So the corpus computes an object
that necessarily violates the ungated copy, on a path it certifies, from fraction 0.60
onward.

**The trap that guards this is aimed at one of the two copies — my own extension.**
`traps:394-398`:

> The `ω² ≥ 0` condition is applicability-gated to phases claimed stable. *Breaks:*
> legitimate saddle points — which transition-path calculations must traverse — score as
> violations. — **enforced**, [residual-definitions#**structural-categories**]

`structural-categories` is the anchor for the heading at `:107`, "Structural axes of
GENERIC — 3 categories", which covers categories 8–10. The duplicate at `:183` lives
under `constraint-categories` (`:177`). **The enforced pointer resolves correctly, names
a site that does carry the rule, and still fails — because the hazard has a second
instance outside the anchor it names.** This is a new shape of the register's
"enforced-as-prose" class: not an unmechanized marker, but a correctly-aimed one with an
uncovered second copy. It is why my §6 seam sweep passed this entry: I checked that the
pointer's target carries the rule, which it does.

---

**(2) Born elastic stability strictly implies the acoustic-limit part of dynamical
stability — and both are listed as separate members of category 16.**

`:183` lists `elastic-stability-criteria` and `dynamical stability` side by side.
`observable-bundles:91` confirms the first is Born stability; registry row 57 gives its
signature as `(C_ij) → bool-vec + slack`, so `C_ij` is its input.

**I derived the implication rather than taking it** (the sweep asserted it; the brief's
rule 1 requires the algebra). Born stability is positive-definiteness of `C` as a
quadratic form on symmetric strains. The acoustic branches at small `q` solve
`ρω²u = Γ(n)u·q²` with the Christoffel tensor `Γ_ik(n) = C_ijkl n_j n_l`. Then

```
u·Γ(n)·u = C_ijkl n_j u_i n_l u_k = C_ijkl ε_ij ε_kl ,   ε = sym(u⊗n)
```

because `C` is symmetric in `(ij)` and `(kl)` and so annihilates the antisymmetric part.
And `ε = 0` forces `u = 0`: `u_i n_j + u_j n_i = 0` contracted with `n_j` (|n| = 1) gives
`u = −(u·n)n`, and dotting with `n` gives `u·n = −(u·n)`, so `u·n = 0` and then `u = 0`.
Hence `C ≻ 0 ⟹ Γ(n) ≻ 0` for every direction — Born stability implies real acoustic
frequencies. **The converse fails**: `Γ(n) ⪰ 0` for all `n` is the Legendre–Hadamard /
strong-ellipticity condition, strictly weaker than `C ≻ 0`. So the implication is
one-way and strict.

Consequence: the two conditions are **not independent members**. `:253` makes "one failing
eigenmode of `C_ij` under `elastic-stability-criteria`" a separately-weightable
contribution, so an acoustic instability is scored once as a failing `C_ij` eigenmode
(cat 16, gate 0.60), once as `dynamical stability` (cat 16, gate 0.60), and once as
`ω² ≥ 0` (cat 10, gate 0.00) — **three independently-weighted contributions for one
physical defect, across two categories and two gates.** The effective weight on acoustic
instability is therefore set by an accident of enumeration, not by the operator's
curriculum.

---

**(3) The γ̂-trace admissibility term is filed under `Conservation` in the same sentence
that denies it is conservation, and it satisfies `Static/Snapshot` exactly.**

`:114-118`, category 9:

> Particle number includes the **static γ̂-trace admissibility** `‖Tr γ̂ − N_e‖²`, with
> `N_e` fixed by `SiteDecoration`, **checked per snapshot**: a candidate state must carry
> the right electron count, **not merely conserve whatever count it has along a
> trajectory**.

Category 16 is *"depends only on the geometric and electronic snapshot, with no
environment field"*. `Tr γ̂` is the electronic snapshot; `N_e` from `SiteDecoration` is
the geometric snapshot; no environment field appears. The term satisfies category 16's
predicate word for word — and the sentence filing it under `Conservation` is the sentence
that says it is not a conservation law. The page states the defect and files against it
anyway.

---

**(4) γ̂ Hermiticity and `0 ⪯ γ̂ ⪯ 1` are `Positivity` members that satisfy
`Static/Snapshot` too.**

`:128-132`:

> **γ̂ admissibility** — ensemble N-representability … `γ̂† = γ̂` and `0 ⪯ γ̂ ⪯ 1`,
> evaluated as per-block spectral bounds …

Functions of the electronic snapshot alone, no environment field: category 16's predicate
again. Together with (3) this is the root cause in its clearest form — **the predicate
category 16 is defined by is satisfied by members of categories 9 and 10, and the page's
sole disjointness argument defends only 16-against-17.**

---

**(5) "space-group equivariance" appears in two categories, and the qualifiers that are
supposed to separate them are not disjoint on the corpus's own objects.**

- `:153`, category 14 `Algebraic/Symmetries` — "space-group equivariance of **response
  tensors**"
- `:183-184`, category 16 `Static/Snapshot` — "space-group equivariance of **the
  snapshot**"

**I checked whether the qualifiers separate them and found a stronger overlap than the
sweep reported.** A *static* response tensor is by definition a function of the snapshot
alone, so its equivariance satisfies category 16's predicate while being category 14's
named subject. The overlap is not confined to one object — it is **total for the static
response tensors**. The elastic tensor is the sharpest instance because it is
additionally the input to a category-16 member by name: `generic-dynamics:118` defines it
as second strain-derivatives of `F`, `accuracy-ledger:149` gives its computation route as
"stress-strain or **perturbation theory**" (i.e. linear response), and registry row 57
makes `C_ij` the sole input to `elastic-stability-criteria`.

Gates: category 14 turns on at **0.10** (Refine, "add all EOM/* + all Algebraic/* except
MethodEquivalence"); category 16 at **0.60**. A sixfold difference in when the residual
first participates, decided by a rule no page states.

*Qualification I owe:* the corpus's only other uses of the token "response tensor"
(`observable-bundles:113-114`) are the high-frequency and electronic linear-response
tensors, not the elastic tensor. So there is a *reading* on which category 14 is narrow.
The corpus never says which reading is meant, and under the narrow one the dielectric
tensor still lands in both. The defect is the absent rule, and it survives either
reading.

---

**(6) Category 16's defining predicate is false of its own members — and the corpus says
so on its own applicability page.**

Category 16 is *"depends only on the geometric and electronic snapshot, **with no
environment field**"*, with four members: valence-bond-sum charge balance,
`elastic-stability-criteria`, dynamical stability, space-group equivariance of the
snapshot. Two of the four are environment-dependent, and both are provable **inside the
corpus**:

- **Dynamical stability.** `applicability-classifiers:133-141`, under the heading
  "**Swept-environment validity windows**": *"A predicate or formula validity window that
  depends on a **runtime-swept** `Environment` scalar — temperature, … **the `ω² ≥ 0`
  claimed-stable gate**, … — is re-evaluated **per training sample** in the loss mask."*
  The corpus declares this member environment-swept on one page and environment-free on
  another. *(This confirmation is mine — the sweep asserted the page said so; I read it.)*
- **`elastic-stability-criteria`.** Its input `C_ij` is defined at `generic-dynamics:118`
  as second strain-derivatives of **`F`**, the Helmholtz free energy — which my own N8
  entry already established fixes these as **isothermal** elastic constants. An
  isothermal constant is a function of temperature. Environment-dependent by the corpus's
  own definition of the object.

*(The physics agrees independently: dynamical stability is famously temperature-dependent
— bcc Ti/Zr/Hf and the cubic perovskites are harmonically unstable at 0 K and are the
observed high-temperature phases — and Born's criteria under finite stress require the
stress-corrected form. But the internal contradiction is airtight on its own and I rest
the finding there.)*

**What this does to the one defended pair.** Extensionally, 16 and 17 share no listed
member. But the *reason given* for their disjointness — type-distinct inputs — is false
of 16's own members, so the disjointness is a coincidence of the current lists rather
than a consequence of the criterion. Applied honestly, the criterion moves dynamical
stability and elastic stability into 17. **The single pair the page argues for is the
pair whose argument can be shown unsound.**

*Severity limit, stated because it bounds this sub-item:* 16 and 17 both first gate at
0.60, so the misclassification alone changes no curriculum timing. Its cost is that the
partition criterion cannot be trusted for any future member, and that it conceals the
environment-dependence of two residuals whose masks are then not written.

---

**What would refute L17.** A page stating the assignment rule — which category a
condition satisfying two definitions is filed under, and how the other membership is
represented — or a `CategoryTag` field typed as a set rather than a scalar. I swept
`residual-definitions` in full and the pages it declares as `depends-on` for an
assignment rule; the only text on the subject is `:198-200`, quoted above. For overlap
(1) specifically: a statement that the `Static/Snapshot` "dynamical stability" member
inherits the `Positivity` copy's applicability gate.

**Proposed corrections**, in dependency order:

1. **Make the assignment rule explicit or make the type a set.** Either state that a
   condition satisfying two definitions is filed under the earlier-numbered category and
   the other membership is a query over facets, or type `category : Set<CategoryTag>` —
   which then requires a stated rule for how the curriculum gate composes over a set.
2. **Overlap (1) is the urgent one and is separable from the rest.** Give the
   `Static/Snapshot` dynamical-stability member the same applicability gate as the
   `Positivity` copy, or delete it from category 16 and let `ω² ≥ 0` carry the condition
   alone. Until then the corpus scores correct transition states as violations from
   fraction 0.60. *Extend `traps:394-398` to name both sites*, or the trap will keep
   reading as enforced.
3. **Define categories 16–17 by enumeration like 8–15, or 8–15 by predicate like 16–17 —
   not one of each.** The mixed scheme is what generates the overlaps.
4. **Fix category 16's predicate**: "no environment field" is false of two of its four
   members. Either move them to 17 or restate the predicate as what actually distinguishes
   the pair.
5. Fold `elastic-stability-criteria`'s acoustic-limit content into one contribution, or
   state that the triple-scoring in (2) is intended and how the weights are meant to
   compose.

---

### L18 — `σ ⪰ 0` and `ρ ≥ 0` are bare symbols in the earliest-gated category, and the corpus's own usage makes both false

**Severity: medium-high. Confidence: high on the ambiguity and on the corpus's own usage;
medium on which reading the author intended, which is the point.**

*(This is the referent question §6 recorded as "delegated and not returned". I ran it
myself. It is the last of my own undelegated items.)*

`residual-definitions:119-120`, category 10 in full:

>  10. `Positivity` — `M ⪰ 0`, `f ∈ [0,1]`, `ρ ≥ 0`, `ω² ≥ 0`, `σ ⪰ 0`, `|S_i| = 1`.

Four of the six are bound by the surrounding pages: `M` is the friction operator, `f` the
occupation, `ω²` the squared phonon frequency, `S_i` the spin. **`ρ` and `σ` are bound by
nothing.** They appear in a list, not an equation, and each collides with several physical
quantities the corpus carries elsewhere.

**Corpus-wide symbol sweep, done by hand.** `σ` carries **seven** distinct senses in
`journals/`:

| sense | sites |
|---|---|
| standard deviation | `cert-obligations:69,145`; `reference-battery:87,92`; `accuracy-ledger:207`; `residual-loss-design:286,290`; `product:196` |
| **stress** | `reference-battery:115` (`σ_ij = σ_ji`, *"the stress tensor is symmetric"*); `multiscale-state:209-211` (`σ_stress`, `σ_yield`) |
| **electrical conductivity** | `typed-compositions:311` (`μ = σ/(n·e)`); `multiscale-state:414` (`σ(r) = q·n·μ₀`); `pino-bridge:119` (`σ(T)`) |
| displacement cross-section | `traps:209`; `multiscale-state:246,249,256` |
| capture cross-section | `multiscale-state:310`; `accuracy-ledger:142` |
| singular value | `residual-machinery:164` (`σ_{k+1}`) |
| stoichiometric coefficient | **`residual-definitions:151`** — `(Σ_r σ_r ln K_r)²`, **32 lines above `σ ⪰ 0` on this same page** |

and `ρ` carries **five**:

| sense | sites |
|---|---|
| **charge density** | `multiscale-state:353` (`∇·(ε∇φ) = −ρ`), `:358` (`∇·j + ∂ρ/∂t = 0`), `:403` (`ρ = q(p − n + N_D⁺ − N_A⁻)`), `:444` |
| group representation matrix `ρ(g)` | `cert-obligations:110`; **`coupling-structure:197,202`** — one of my own three pages |
| dislocation density `ρ_dis` | `multiscale-state:209-211,302` |
| mass density `ρ_m` | `multiscale-state:405,413,443`; `accuracy-ledger:400` |
| resistivity `ρ_c` | `accuracy-ledger:145` |

**The referent test, and it comes out badly.** `ρ` appears **bare** — no subscript, no
argument — at five sites in `journals/` outside this one, and at **five of five** it is
the **charge density**. That is the corpus's own answer to what bare `ρ` means. And the
charge density is **signed**: `multiscale-state:403` defines it as `ρ = q(p − n + N_D⁺ −
N_A⁻)`, which is negative throughout the p-side of every junction and throughout every
inversion layer. Under the reading the corpus's own usage supplies, **`ρ ≥ 0` is a
`Positivity` residual that penalizes correct physics over half of every device the corpus
targets.**

The charitable reading — `ρ` as the electron number density — does not survive contact
with the page either: the corpus writes electron density as `n` (`typed-compositions:311`,
`multiscale-state:403`), writes the one-body density matrix as `γ̂` throughout, and
already carries the occupation bound as `f ∈ [0,1]` **on the same line**. There is no
unclaimed non-negative density left for `ρ` to be.

`σ ⪰ 0` fails differently. The `⪰` is the matrix ordering the page uses for `M ⪰ 0` and
`0 ⪯ γ̂ ⪯ 1`, so `σ` is a tensor, which narrows seven senses to two:

- **Stress.** Then `σ ⪰ 0` is false. A crystal under hydrostatic compression has
  `σ = −P·I ≺ 0` in every principal direction, and the corpus evaluates states under
  pressure by design — `:188` carries the "temperature- and **pressure**-aware
  metastability" form. The corpus carries the stress tensor under exactly this symbol at
  `reference-battery:115`.
- **Conductivity.** Then `σ ⪰ 0` is *incomplete rather than false*, and incomplete in the
  way L11 already identified. What the second law gives is `E·σ·E ≥ 0`, a condition on the
  **symmetric part**. With a magnetic field or a magnetization the conductivity tensor
  acquires an antisymmetric Hall part, its eigenvalues are complex, and a literal
  `λ_min(σ) ≥ 0` check is not a well-defined test. Same root cause as L11: the corpus
  never carries the field-reversal structure of transport symmetry.

So each of the two bare symbols has a reading, supported by the corpus's own usage, under
which the residual scores correct physics as a violation — and no page states which
reading is meant.

**Why this ranks above a notation complaint.** `Positivity` is one of only **two**
categories active in Warmup, from training fraction 0.00. Two of its six members are
unbound symbols.

It also interacts with L14, and I state the interaction because it cuts both ways. L14
shows Warmup's two categories are exactly zeroed by a frozen trajectory. That argument
presumes the `Positivity` bounds hold on an admissible state. Under the charge-density
reading they do not — so Warmup is no longer trivially minimized, but only because the
residual is nonzero on correct states. **Both branches are bad, and they are the only two:
either Warmup's objective has a trivial global minimizer (L14), or it is minimized by
driving the charge density non-negative everywhere, which destroys the depletion region.**

**Controls run, because this finding rests on absences.**

| negative claimed | control | result |
|---|---|---|
| `σ`/`ρ` are absent from the overloaded-token register | read the register in full (`glossary#overloaded`) | **fires** — 10 entries, `graph`, `tier`, `layer`, `slot`, `cell`, `kernel`, `source`, `path`, `coverage-mask`, `GAP`. Every one is a **word**. The register has **no symbol entries at all**, so symbol collisions are outside its reach by construction — and `σ`'s seven senses exceed several word collisions it does register |
| no page binds `ρ` or `σ` for this list | Unicode-safe sweep for both symbols corpus-wide | **fires** — 30+ sites, tabulated above. The instrument finds the symbol everywhere it occurs; what it does not find is a binding for this line |
| bare `ρ` might mean something other than charge density | swept every bare-`ρ` occurrence, not only the convenient ones | **fires** — 5 of 5 are charge density; the counter-senses all carry a subscript or an argument |

**The corpus's own contract names the exact precondition this line fails.**
`agent-contract:142-144`:

> Everything the corpus invents is spelled out in English. Standard deviation is the name;
> `σ` is not. … **Symbols belong in equations, where the surrounding mathematics binds
> them.**

That rule governs corpus-invented *names*, so `residual-definitions:119` does not violate
it — the symbols here are physics, not invented tags, and I am not claiming a contract
breach. What the rule supplies is the standard: symbols are admissible *where the
surrounding mathematics binds them*. A comma-separated list is not surrounding
mathematics. The corpus wrote down the condition under which bare symbols are safe, and
this line is the case that does not meet it.

**What would refute this.** A page binding `ρ` and `σ` for the `Positivity` list — a
`named-formula` row, a slot declaration, or an entry in the overloaded register. I found
none.

**Proposed correction.** Spell both out, in the corpus's own idiom: replace `ρ ≥ 0` with
the quantity actually meant (if it is the electron density, write `n ≥ 0` and say so; if
it is the charge density, **delete it** — it is not a positivity constraint), and replace
`σ ⪰ 0` with "the symmetric part of the conductivity tensor is positive semidefinite",
which is the true statement and is `B`-safe. Separately: add `σ` and `ρ` to
`glossary#overloaded`, which currently registers no symbols at all — that is the same
one-row mechanism L16 asks for `degeneracy`.

*Subsidiary observation, not raised as a finding:* `|S_i| = 1` is an equality constraint
on a manifold and `f ∈ [0,1]` a two-sided bound; neither is a positivity condition. The
category name under-describes its own contents. Cosmetic, and noted so the sweep is
visible.

---

### L19 — The scoping that is offered as reconciling the degeneracy conditions is stated over two different partitions at once, and on the page's own reading it excludes the MVP's headline coupling

**Severity: high. Confidence: high.**
*(New on resumption. Found by re-reading the operator-assembly section against
`born-oppenheimer-levels` and `coupling-structure`. It is the load-bearing sentence
behind L4, and I had taken it at face value in my first draft.)*

`generic-dynamics:132-137` is the corpus's answer to how the degeneracy conditions are
supposed to hold at all:

> The two-generator form and its degeneracy conditions `L·δS/δx = 0`, `M·δE/δx = 0` hold
> **per tier / per level, with the generators active at that tier** — not as a single
> global bracket over all variables simultaneously. **This is what reconciles the written
> functionals with the degeneracy conditions** and with the "degeneracy verified" artifact
> of [build-sequence#phases]. The tiers are [multiscale-state#three-tiers] …

**"Per tier / per level" names two different partitions of the state, and they do not
agree.**

| partition | granularity | where `γ̂` and `R` sit |
|---|---|---|
| **tiers** — `multiscale-state#three-tiers` | micro / slow / macro | **both in micro** |
| **levels** — `born-oppenheimer-levels#hierarchy` | four levels over the micro seven-tuple | `γ̂` in `quantum-electronic-substrate`; `R` in `born-oppenheimer-surface` — **different levels** |

`born-oppenheimer-levels:31-34` is explicit that the second is a partition: *"The micro
seven-tuple partitions into four levels … The hierarchy is a **partition** of the
state-component space."* So the four levels subdivide the single micro tier, and a term
that is intra-tier can be inter-level. The slash conflates them, and the page never says
which one the conditions are scoped to.

**Which reading the page itself uses, from its own worked arguments.** The two
by-construction arguments immediately following, at `:140-153`, are both stated at
**level** granularity — *"The `γ̂`-block of `L` is the Lie–Poisson bracket"* and *"The
`born-oppenheimer-surface` level is single-generator"*. Neither is a tier-level statement.
So the page's own demonstrations use the level partition.

**And on that reading the scoping excludes the terms the operator learns.**
`coupling-structure:63-75` defines what a coupling is:

> a symmetry-respecting function from a tensor product of pieces of the state vector into
> one of three target shapes: … **`AntisymmForm`** — … lands as an **off-diagonal block
> of `L`**; **`PSDSymmForm`** — … lands as an **off-diagonal kernel of `M`**. …
> **Every cross-regime term in [generic-dynamics] is one instance of this object.**

Couplings are off-diagonal by construction. A degeneracy condition scoped to "the
generators active at that level" is a condition on that level's diagonal sub-block, and it
does not see a block joining two levels. So the question is whether any MVP coupling
spans two levels — and the MVP's headline channel does. `coupling-structure:219`, the
worked example, declares:

```
electron-phonon = CouplingChannel {
  pieces = [ StatePiece(γ̂, orbital), StatePiece(R, none) ]
  …
```

`γ̂` is `quantum-electronic-substrate`; `R` is `born-oppenheimer-surface`
(`born-oppenheimer-levels:39-40`). **Two levels.** And `generic-dynamics:100-102` names
this channel as one of exactly two MVP cross-kernels of `M`: *"MVP set: phonon-phonon and
electron-phonon scattering kernels."*

**The dilemma, and both horns fail.**

| reading | does the scoping reach the electron-phonon cross-kernel? | what then fails |
|---|---|---|
| **level** (the one the page's own arguments use) | **no** — the kernel joins two levels and belongs to neither level's active generator | the reconciliation offered at `:132-137` excludes the single largest learned object in the MVP `M`, which is exactly the object L4 shows has no construction |
| **tier** | yes — `γ̂` and `R` are both micro | then the two by-construction arguments at `:140-153` are stated at the wrong granularity to discharge anything, and no argument at tier granularity exists anywhere |

Either way `:132-137` does not do the work it says it does. **This is the load-bearing
sentence for L4**: it is what the corpus offers in place of a construction, and it is
offered specifically to reconcile the degeneracy conditions with the "degeneracy verified"
build artifact. L4 shows no construction covers the generated cross-terms; L19 shows the
scoping argument that would have localized the claim does not cover them either, on the
reading the page itself uses.

**Scope limit, stated so the finding is not read wider than it is.** Not every coupling is
cross-level. Of the four channels in the MVP `CouplingSpec` (`coupling-structure:424-426`)
— electron-phonon, minimal coupling, ion-ion electrostatic, phonon-phonon — **only
electron-phonon** is cross-level: minimal coupling is `γ̂ ↔ A`, both in
`quantum-electronic-substrate`; phonon-phonon is `R`-only, inside
`born-oppenheimer-surface`; and ion-ion electrostatic does not exist (L7). Intra-level
couplings are covered by the level-scoped statement and I make no claim against them.
The finding is that the one cross-level MVP channel is the corpus's headline coupling, its
only worked example, and one of two named cross-kernels in `M`. *(By inspection of their
names, `magneto-elastic` and `strain-electronic` in the 15-channel table also join `γ̂` to
`h`; the corpus does not declare their `pieces`, so I mark that as inference and do not
rest anything on it.)*

**What would refute this.** A statement saying which partition the degeneracy conditions
are scoped to, together with — under the level reading — a rule assigning each cross-level
coupling block to a level for the purpose of the conditions. I swept `generic-dynamics`,
`born-oppenheimer-levels`, `coupling-structure` and `multiscale-state` for an assignment
rule for cross-level blocks and found none. **Control:** the same sweep does find the
assignment rule for the other direction — `coupling-structure:63-73` says exactly which
target shape lands in `E_coupling`, in `L` and in `M` — so the instrument returns
assignment rules where they exist.

**Proposed correction.** Say "per level" or "per tier", not both. Then, under the level
reading, state the degeneracy conditions for cross-level blocks explicitly — the honest
form is that `L δS/δx = 0` and `M δE/δx = 0` must hold on the **assembled** operator
including off-diagonal blocks, which is the condition that actually has content and is the
one L4 asks to be constructed or checked. Under the tier reading, supply a
by-construction argument at tier granularity, since none exists.

---

### L20 — The normative gauge sentence derives transversality from a freedom that cannot deliver it, and my own seam sweep passed the site

**Severity: medium-high. Confidence: high (algebra re-derived here).**
*(Found by the **state** subject, `audit/findings/state.md`, which traced the normative
statement to my page and wrote: "The gauge finding's primary home is **postdoc-laws'**,
not mine." I accept the referral, re-derived the algebra myself rather than taking their
summary, and record my sweep's miss in §6.)*

`generic-dynamics:185-187`, under a heading the page marks **Normative**:

> The state's `A` is carried in the **Weyl gauge** `A₀ ≡ 0`, with the **remaining
> time-independent gauge freedom** fixed by transversality `∇·A = 0` — the Coulomb-gauge
> radiation field.

The sentence does not merely assert both conditions; it **derives** the second from the
first by spending residual freedom. That derivation cannot work, and the page's own
adjective is what proves it.

**Re-derived here, in the Gaussian convention the corpus fixes with its `1/8π` at `:71`.**
Residual gauge freedom preserving `A₀ ≡ 0` is `A → A + ∇χ`, `φ → φ − (1/c)∂_t χ`; keeping
`φ = 0` forces `∂_t χ = 0`, so `χ = χ(r)` — **time-independent**, exactly as the page says.
Such a shift moves `∇·A` by `∇²χ(r)`, a time-independent amount. But the obstruction is
time-dependent. With `φ = 0`, `E = −(1/c)∂_t A`, and Gauss's law `∇·E = 4πρ` gives

```
∂_t(∇·A) = −4πcρ    ⟹    ∇·A(r,t) = ∇·A(r,0) − 4πc ∫₀ᵗ ρ(r,t′) dt′
```

A time-independent `∇²χ` can cancel a time-dependent integral at **one instant only**.
So `∇·A ≡ 0` for all `t` requires `ρ ≡ 0`. Weyl and Coulomb are alternative, mutually
exclusive fixings: Weyl keeps `A₀ = 0` and lets `∇·A ≠ 0` carry the electrostatics;
Coulomb keeps `∇·A = 0` and lets `A₀ ≠ 0` carry it.

**What the page actually describes is sound; the sentence justifying it is not.**
Transverse `A` with the electrostatic sector in the matter functionals is **Coulomb gauge
with the non-dynamical scalar potential eliminated** — the standard nonrelativistic-QED
partition. `:189-195` states three times that the longitudinal sector is owned by the
Hartree term and the ion–ion channel and "appears nowhere in `E_EM`". That construction
is correct. What fails is one clause: the route by which the page claims to reach it.

**I am also passing on the state subject's corrections to the principal's framing, because
they change the severity ranking.** The register lists this as item #4 — *"Gauss's law
violated identically; dominant term silently absent"* — and that over-claims. Gauss's law
is **not** violated: the electrostatics is carried, correctly, in the matter functionals.
And a static applied field is **not** homeless: transversality in Fourier is `k·A_k = 0`,
which is **vacuous at `k = 0`**, so a uniform field rides `A(t) = −cEt`, satisfying
`A₀ ≡ 0` and `∇·A = 0` simultaneously and exactly. Berry-phase electric enthalpy is
therefore *not* required — it is needed only on the scalar-potential route, where `−E·r`
is non-periodic. **The corpus has two available routes and states neither**, which is a
class-3 defect, not the class-4 one the register records. *(I verified the `k = 0`
argument: `∇·A = 0` in Fourier is `ik·A_k = 0`, identically satisfied at `k = 0` for any
`A_0`. Correct.)*

**The truth value of my sentence depends on an unresolved definition on someone else's
page**, and this is why two readings could each be defended from real text. `unified-state:37`
types the slot `A ) external EM vector potential`, while `residual-definitions:74-89` gives
it an `EOM/A` equation of motion and `generic-dynamics:71,189` puts `E_EM[A]` inside the
system energy `E[x]`. On the **external** reading there are no sources in the cell, `ρ = 0`,
and the gauge sentence is consistent. On the **own-radiation-field** reading the obstruction
above is live. That slot-definition defect is the state subject's finding and stays theirs;
what is mine is that **my page's normative sentence has no determinate truth value until it
is resolved**, and the sentence is marked `Normative`.

**What would refute this.** A statement that `χ` may be time-dependent (it may not — that
reintroduces `A₀`), or that the corpus intends `ρ ≡ 0` in the cell, which is the external
reading and should then be stated at `generic-dynamics:186` rather than inferred.

**Proposed correction.** One sentence. Replace the derivation with the fixing: *"The
state's `A` is the transverse radiation field, `∇·A = 0`, with the non-dynamical scalar
potential eliminated; the longitudinal sector is carried by the matter functionals."* Drop
"Weyl" and drop "remaining time-independent gauge freedom" — the second is what makes the
claim false, and neither is needed for the partition the page actually wants. Separately,
state which route carries a uniform applied field.

---

### L21 — The per-residual error budget is composed by one of two rules with no selection rule, and the rule that is usually chosen is invalid in the case the page calls common

**Severity: medium-high. Confidence: high.**
*(New on resumption. `per-residual error composition` is an owned topic of my page. Checked
against the other six findings files first: `combineTol` appears in four of them, always
from the **sourcing** angle — which page supplies its inputs, whether the ledger holds
them. **None examines the composition rule itself.**)*

`residual-definitions:341-360` declares the budget:

> Every residual generator carries a `characteristic-scale` … It is the error-model input
> that `Quantity.combineTol` ([typeclass-alphabet#quantity]) composes along the DAG, **per
> instance by max-abs or by root-sum-square**, into a per-`ResidualKey` error budget.

with five summands: input standard deviation, model-form error, compression truncation,
dressing staleness, coefficient-provenance standard deviation.

`typeclass-alphabet:63-68` defines the mechanism:

> `combineTol` is how tolerances compose under arithmetic … It is associative, commutative
> and monotone, and **each instance chooses either maximum-absolute or root-sum-square
> composition**. **Monotonicity is the load-bearing property**: a combination can never
> come out *tighter* than its inputs, which is what stops a long composition from
> manufacturing precision it does not have.

**(a) The algebra checks out; the guarantee does not follow from it.** I verified the
stated properties for both rules. Max-abs `max(|a|,|b|)` and root-sum-square `√(a²+b²)`
are each associative, commutative, and monotone in the stated sense — `√(a²+b²) ≥ max(a,b)`
— so no combination is tighter than its inputs. ✓

But monotonicity is **not** what stops a composition from manufacturing precision. The way
an error budget manufactures precision is by **under-estimating the total**, and
root-sum-square under-estimates whenever the contributions are correlated. For `n`
contributions each of magnitude `ε` that are perfectly correlated, the true combined error
is `nε` while root-sum-square returns `√n·ε` — **too small by a factor `√n`**, and monotone
throughout, since `√n·ε ≥ ε` for every `n ≥ 1`. The stated safeguard is compatible with an
arbitrarily large under-estimate. Root-sum-square is valid **only for independent errors**,
and that is the condition the sentence should have named.

**(b) The word "independent" never appears in this sense anywhere in the corpus.** Control
sweep: `typeclass-alphabet.md` — **zero** occurrences of `independen*`; `accuracy-ledger.md`
— **zero**; `residual-definitions.md` — three, all unrelated (*"every independent
component"*, *"an independent weight"*, *"independent of this library's internals"*). The
instrument finds the word where it occurs, and it does not occur attached to the condition
that makes root-sum-square sound.

**(c) And the page declares the correlated case to be the common one — 22 lines later.**
`residual-definitions:318-322`, under "Granularity composes with hash-consing":

> Two contributions sharing **99% of their DAG ancestry** — for example, all
> Kramers–Kronig identities sharing one dielectric-function computation — **is the common
> case.**

Contributions sharing 99% of their ancestry have errors that are nearly perfectly
correlated, because almost the entire error is inherited from the shared computation.
**So the page states, on one screen, that the common case is near-total correlation, and
that the error budget may be composed by a rule valid only under independence — with no
rule for choosing.** These two paragraphs are 22 lines apart and cite the same machinery.

This is not a small numerical difference. For the five listed budget terms the two rules
differ by up to `√5 ≈ 2.2×`; along a DAG where "all Kramers–Kronig identities share one
dielectric-function computation", the shared-ancestry multiplicity is larger and so is the
gap. And the budget's consumer is a certification decision — `combineTol` is what a reader
consults to decide whether an answer is accurate enough (`residual-definitions:362-363`:
*"is this closed-form choice accurate enough?" is answerable by the system*). A
systematically optimistic budget answers that question wrongly in the safe-looking
direction.

**What is mine and what is a referral.** The composition rule lives on
`typeclass-alphabet`, which is not my page — **I report it to the principal and do not
chase it**: the defect there is two rules, no selection rule, no independence condition,
and a monotonicity claim that does not deliver what the sentence says it delivers. What is
mine is `residual-definitions:341-360`, which declares a five-term per-residual error
budget over that mechanism, on the page that also declares 99%-shared ancestry the common
case, and states neither the selection rule nor the independence condition.

**What would refute this.** A page stating when max-abs is required and when root-sum-square
is admissible — in particular a rule keyed on shared DAG ancestry, which is the information
the hash-consing stage already has. I swept `residual-definitions`, `typeclass-alphabet`,
`accuracy-ledger`, `residual-machinery` and `compose-time-pipeline` and found no selection
rule. **Control:** the same sweep does return the *cost* rule for the same stage
(`residual-definitions:323-330`, hash-consing gives upstream sharing "for free"), so the
instrument finds per-stage rules where they exist.

**Proposed correction.** On my page: state that the per-residual budget composes by
**max-abs** unless the contributions are demonstrably independent, and that shared DAG
ancestry — which the hash-consing stage already computes — is the criterion. Referral to
whoever owns `typeclass-alphabet`: replace *"each instance chooses either"* with the
condition under which each is valid, and correct the monotonicity sentence, which claims a
guarantee monotonicity does not provide.

---

## 2 · Findings that did not survive

### Triage of the inherited contradictions — the brief's first instruction, recorded

`audit/inherited/contradictions.md` carries 89 registered contradictions "deliberately
left unresolved", with the instruction to triage before trusting any of them: the corpus
was rewritten since, so a registered contradiction may persist, may be resolved, or may
have been mis-registered. Eight rows fall in my subject. All eight triaged:

| inherited row | verdict after re-reading canon | where it lands |
|---|---|---|
| `:26` the `γ̂`-block of `L` — table row vs the later correction | **persists verbatim** through the restructure | L10 |
| `:25` curriculum phase names and count — three vocabularies | **persists, and worse than registered**: the register saw a name *substitution*; it is a *rotation*, so `Polish` binds to two disjoint bands | L8 |
| `:199` / `:24` the curriculum fractions and their denominator | **persists**; canon declares the denominator an open question and never asks where the numbers came from | L14 |
| `:135` what SCF *is* dynamically — fixed-point iteration vs gradient flow | **persists**; `computational-methods:63-67` still classifies `SCF-mixing` and `Pulay-mixing` as `variational-minimization` sub-methods, not integrators, and `generic-dynamics:120` still says "gradient flow" | L2 |
| `:136` Onsager index placement under a magnetic field | **persists in the form the register predicted** — the appendix's three statements are gone with the appendix, and canon inherited the ambiguity by naming the law with no equation at all | L11 |
| `:14` where the gauge conventions are recorded | **resolved as registered** (a pointer conflict; `unified-state:40` now defers correctly to `generic-dynamics`) — **but the text it defers to is wrong**, which the inherited register could not have seen because it only compared pointers | L20 |
| `:159` **C11** Chynoweth ↔ BTE scored as method-equivalence | **resolved.** The claim was in a deleted appendix; canon (`residual-definitions:167-171`) correctly classifies cheap-Chynoweth vs Boltzmann/Monte-Carlo as a **consistency pair** with a model-gap envelope. Not raised. | — |
| `:163` **C15** superseded taxonomy counts ("the existing 5 categories") | **resolved as registered** — the superseded counts died with the appendices; canon says nineteen consistently. *Separately*, canon's nineteen is itself wrong for a different reason (L6, L17), which is not this row's defect and I do not credit it here. | — |

Six persist, two are resolved. **The `:14` row is the instructive one**: it was registered
as a pointer conflict, the pointer was duly fixed, and the fix retargeted it at a false
sentence. A register that compares pointers can certify a repair that makes the corpus no
better — the same failure my own seam sweep committed (§6).

### N1 — Strong correlation as an undeclared limitation. **Dismissed.**
The GENERIC state carries a one-body density matrix `γ̂`, and `E_BO(R,h) = min_γ̂
E_KS[γ̂; R,h]` presumes the electronic problem is a functional of `γ̂` alone. I expected
this to be an undeclared validity boundary. It is declared, and well:
`out-of-scope:26-28` — *"Strongly-correlated systems — frustrated Wigner crystals, spin
liquids, Mott physics. The one-body density matrix is mean-field by construction, and
ultra-wide-gap materials are large-gap and far from Mott physics."* The exclusion names
the mechanism and the reason it is safe for this material set. Correct.

### N2 — The spinor-parity pre-prune. **Checked, correct.**
`coupling-structure:186-187`: *"an odd total spinor count cannot form a Scalar /
PSDSymmForm / AntisymmForm invariant, so the basis is empty before any character is
computed."* Verified: under the double group the element `Ē` (rotation by `2π`) acts as
`−1` on a state with an odd number of spinors, while the trivial irrep has `Ē → +1`, so
the character inner product `⟨χ_T, χ_trivial⟩` vanishes identically. Correct as stated.

### N3 — The Reynolds/PSD closure argument. **Checked, correct.**
`coupling-structure:670-675`: *"a positive-semidefinite `G`-invariant representative
provably exists, because the Reynolds image of a positive-semidefinite seed is
positive-semidefinite."* Verified: `R(B) = (1/|G|) Σ_g ρ(g)ᵀ B ρ(g)` is an average of
congruence transforms of a PSD matrix, each PSD, so `R(B) ⪰ 0`; and `R(B)` is
`G`-invariant. The page's tight/loose split (existence is a theorem, the *learned*
combination still needs a runtime guard) is honest. This is the treatment L4 says
degeneracy should have received and did not. It also matches `traps:429-436`, which
requires the *congruence-action* Reynolds operator specifically.

### N4 — The generator cost model. **Checked, correct.**
`coupling-structure:199-206`: `|G| ≤ 192`, `dim(T) ≤ ~250`, character pre-prune `O(|G|) ≤
~200`, Reynolds projection `O(|G|·dim(T)²) ≤ ~12M`. Arithmetic: `192 × 250² = 12.0M` ✓.
`|G| = 192` is right for diamond: `O_h` has order 48, the double cover doubles it to 96,
time reversal doubles it again to 192 ✓.

### N5 — `polynomial_sufficient(LongRangeStatic(0)) = true` as a self-contained error.
**Dismissed as stated; survives only as part of L7.** Read literally against the type's
own definition (`1/|q|^p` with `p = 0`), the rule is correct — that expression *is* a
constant. The defect is not the rule but the type's inability to express a degree-0
*direction-dependent* limit, which is where the LO-TO term lives. Folded into L7 rather
than reported separately, because on its own terms the derivation is sound.

### N6 — Non-Markovian dynamics as wholly undeclared. **Partially dismissed.**
`out-of-scope:33` does declare one exclusion: *"Deep-defect non-Markovian dynamics — a
Markov master-equation closure is assumed."* That is narrow — it covers deep-defect
kinetics, not the Markovian assumption built into the GENERIC friction operator itself,
which the `LongRangeDynamical` / `MomentumFrequency` `KernelExt` route can violate. The
general case remains open.

**Judgment on resumption: not load-bearing enough to spend an undergraduate on, and I am
stating the reason rather than leaving it as an open pending.** Three things decide it.
(i) The corpus declares the one case where it bites — deep-defect kinetics — so this is a
*scope* question, not an undeclared gap of the kind the brief targets. (ii) A memory
kernel in `M` makes the dynamics non-Markovian but does not falsify any claim I checked;
GENERIC has a standard extension for it, so the likely finding is "the corpus should say
which it means", which is a weaker version of L5's under-specification. (iii) Where it
*would* matter is the `KernelExt` routing rule, and L7 already carries that defect from a
stronger angle — the routing rule between `KernelExt` and `one-shot-dressing` is unstated
outright. **Verdict: fold into L7's routing correction, do not pursue separately.** If
someone does pursue it, the question is narrow: does the corpus intend `M` to be
instantaneous, and if so where is that stated.

### N8 — The other five regime rows. **Checked; four correct, one with a caveat.**
The nine-regime table is the corpus's central claim, so I checked every row, not only the
four that failed (L2, L3, L13). The five that survive, with the comparison made:

- **Structural** (`:117`) — *"Critical points of `E` at `T = 0` (or `F` at `T > 0`); 1st
  derivatives."* Correct. A fixed point of the `T = 0` flow is `L δE/δx = 0`; for the
  nondegenerate symplectic blocks that gives `∂E/∂P = 0` (so `P = 0`) and `∂E/∂R = 0`
  (forces vanish) — exactly the critical-point condition. "Critical points" rather than
  "minima" is right, since saddles are wanted for the transition-state work.
- **Mechanical** (`:118`) — *"2nd strain-derivatives of `F` at equilibrium."* Correct,
  and better specified than it needed to be: naming `F` (Helmholtz) rather than `E` fixes
  these as **isothermal** elastic constants, which differ from the adiabatic ones by
  `C^S − C^T = TVα α/C_v`. Many specifications leave that ambiguous; this one does not.
- **Transport** (`:123`) — *"BTE on emergent carrier distribution: `L` (streaming) + `M`
  (collisions)."* Correct — this is the textbook GENERIC decomposition of the Boltzmann
  equation. *Caveat, not raised as a finding:* the collision operator is
  symmetric-positive-semidefinite in the **linearized** case under the
  equilibrium-weighted inner product (by detailed balance / the H-theorem); the row does
  not say "linearized". The nonlinear collision integral is also GENERIC-expressible, so
  the row is defensible either way, and I did not raise it.
- **Thermodynamic** (`:124`) — *"min `F` at fixed `(T, V, N)`; convex hull of `{F_φ}`."*
  Correct.
- **Chemical/surface, second clause** (`:125`) — *"minimum-energy-path search on
  `E_BO`"*: the endpoints and the saddle **are** critical points of `E`, so those are
  genuine extractions. The *path search* itself is an optimization over a space of paths
  and is not a readout of the equation — but the row does not claim it is a dynamics, so
  I left this inside L3 rather than raising it separately.

### N10 — The `Arabov arXiv 2603.29484 (2026)` citation. **Raised by me, killed, retracted.**
I flagged this to the principal as a fabrication candidate, on the reasoning that the
brief records a prior audit missing a fabricated citation and that a 2026 arXiv id with a
five-digit sequence number was worth a look. **It is real**: the principal resolved it to
"Thermal Conductivity and Temperature-Induced Band Gap Renormalization in Crystalline and
Amorphous Ga₂O₃" (Arabov, Li, Chen, Rybin, Shapeev), and it is on-topic for the β-Ga₂O₃
zero-point renormalization it backs at `accuracy-ledger:229`. Recorded here as a clean
negative so it is not re-raised. It was never in my subject; I should have checked before
flagging rather than after.

*Downstream note passed to me and worth carrying:* Rybin and Shapeev are moment-tensor-
potential authors, so that citation is plausibly the machine-learned potential behind the
`dft-mlip` rows in `material-constants.csv`. If any source behind my own PSD-closure
citations turns out to be MLIP-derived rather than measured or *ab initio*, "primary
source" means something weaker there than the assumption records imply. I have not
checked; it is a question for whoever runs that arm.

### N9 — Residual dimensional heterogeneity. **Not mine — referred to the principal.**
The oracle emits `Map<ResidualKey, Scalar>` unaggregated and dimensionally heterogeneous
(`‖dγ̂/dt − …‖²`, `‖Tr γ̂ − N_e‖²` dimensionless, hull distance in meV/atom), and
declares aggregation the operator's business (`residual-definitions:270-274`).
`characteristic-scale` (`residual-machinery:78`) is declared an **error-budget** input,
explicitly not a weight (`residual-definitions:344-346`), and
`residual-machinery:144` distinguishes it from the per-datum quantity. I found no page
that non-dimensionalizes residuals before summation. Whether that hole is real belongs to
whoever owns the loss and the seam, not to the laws — flagged, not chased.

**Status on resumption: still nobody's.** I re-checked the six other findings files for
it and it appears in none — `state.md:548` is the nearest neighbor and is a different
defect (`‖Δx‖` undefined on a heterogeneous state, not residual summation across
dimensions). So this referral was made and never landed. Recording it here so it is not
lost a second time: **the referral is open, and it is a candidate for the loss subject
rather than a laws finding.** L18 sharpens why it matters — if `ρ ≥ 0` and `σ ⪰ 0` are
charge density and a conductivity tensor, then two members of one category carry
different dimensions from each other, before any cross-category sum.

### N11 — "Residual generators remain **countable**" as a closed-vocabulary claim.
**Raised, weighed, dismissed as terminology — recorded because the sweep should be
visible.** `residual-definitions:332-339` reconciles unbounded emission with the
closed-vocabulary discipline by saying generators "remain **countable**: one per
`(formula, applicability cell)`". *Countable* is strictly weaker than what a closed
vocabulary needs — a countably infinite vocabulary is not closed, and the
`canonical-vocabularies` discipline the sentence invokes is about enumerable finite sets.
The set actually described **is** finite: a finite formula registry times a finite set of
applicability cells, plus two named subtypes. So the argument is sound and the word
understates it. I checked whether anything downstream consumes "countable" as a load-bearing
property and found nothing — no checker, no type, no obligation. **A word that understates
a true claim, consumed by nothing, is not worth a correction**, and calling it one would
dilute the findings that are. Noted, not raised.

### N7 — Numbering the categories 1–17 while declaring them "identified by name and never
by ordinal". **Dismissed as cosmetic.** `residual-definitions:68-69` states the rule and
the same list numbers its members. Real, but the ordinals are presentation-only: nothing
cites a category by number, and the `CategoryTag` enum is by name. Not worth a correction
on its own; noted so the sweep is visible.

---

## 3 · Shaped gaps

All three arose from the same blockage in the first session: the **source-verification arm
was not running**. The undergraduate assigned to it could not be launched (the session
subagent pool refused five dispatch attempts), the web-search budget was exhausted
(200/200), and direct fetches of the two publisher/catalog routes I tried returned HTTP
403 and an empty record respectively.

**Status on resumption: that arm is now running.** The undergraduate launched successfully
and is working all eight PSD-closure citations, including G1 (Jackson) and G2 (Öttinger),
under the routing rules — arXiv API, ar5iv, Crossref, institutional repositories, and a
later source that quotes the primary and says where from. Its verdicts are recorded below
as they land, and any gap it cannot close stays in the four-part form. These were always
cheaply fillable — each is closed by opening one book or one paper, not by redoing
reasoning.

### G1 — Does Jackson §17.2 exist in the edition cited?

| part | content |
|---|---|
| **what it would settle** | In Jackson, *Classical Electrodynamics*, **3rd edition (1998)**, what is section 17.2 — and does the 3rd edition contain a Chapter 17 at all? |
| **the conclusion without it** | I believe it does not, and that `coupling-structure:667` has cited a **2nd-edition** section number under the 3rd edition's year. My recollection is that the 3rd edition ends at Chapter 16, "Radiation Damping, Classical Models of Charged Particles", and that the radiation-damping material the corpus wants sits there; in the 2nd edition (1975) that material is Chapter 17, where a §17.2 does exist. I could not confirm this, and **my recollection is not evidence** — it is exactly the kind of claim this audit's own rules forbid me from banking. |
| **the branches** | If the 3rd edition has no Chapter 17: the citation is an edition slip, the reference resolves to nothing, and `[PSD-rad]` loses one of its three supports. If §17.2 exists in the 3rd edition and covers radiation reaction: the citation stands and this gap closes with no change. |
| **what depends on it** | Nothing else in this report. No finding of mine rests on this branch; it is recorded so it is not lost, and marked conditional. |

### G2 — Is Öttinger 2005 §5.3 where the GENERIC structural axioms live?

| part | content |
|---|---|
| **what it would settle** | What section 5.3 of Öttinger, *Beyond Equilibrium Thermodynamics* (2005), contains — and whether the properties of the friction matrix `M` (symmetry, positive-semidefiniteness, the degeneracy requirement) are stated there. |
| **the conclusion without it** | Unresolved, and it matters more than G1: **all three** PSD-closure assumptions at `coupling-structure:650-669` cite this one section for the "GENERIC M-block axiom", and it is the sole common support across them. The claims attributed to it are standard GENERIC content and are certainly *somewhere* in that book; whether §5.3 is that place is unverified. |
| **the branches** | If §5.3 states the `M`-block axioms: all three references stand and this closes with no change. If §5.3 is about something else (Öttinger's Chapter 5 may be devoted to a specific application rather than the structural framework, in which case the axioms are in the earlier structural chapter): three citations are wrong in the same way, on the page that carries the corpus's entire positive-semidefiniteness guarantee — a single-point failure across all three assumptions. |
| **what depends on it** | Finding **L4** is *strengthened* by the second branch but does not rest on it: L4's argument is that antisymmetry and PSD do not imply degeneracy, which is a mathematical statement independent of any citation. Nothing of mine is conditional on this. |

### G3 — What does Engel 2022 report for the GaN and AlN zero-point renormalization?

| part | content |
|---|---|
| **what it would settle** | The isochoric electron-phonon zero-point renormalization values reported in Engel, *Phys. Rev. B* **106**, 094316 (2022) for GaN and AlN. |
| **the conclusion without it** | The corpus disagrees with itself and one of the two pages is wrong regardless of which value is right. `accuracy-ledger:225-226` records "−189 (Engel −171)" and "−399 (Engel −377)" — the curated value with Engel's differing value beside it. `coupling-structure:371-372` restates −189 and −399 and attributes them to **Engel and Miglio jointly**. |
| **the branches** | If Engel reports −171/−377: `coupling-structure` has attached a citation to values that source does not report, and the fix is to attribute them to Miglio alone. If Engel reports −189/−399: the ledger's parentheticals are wrong and the fix is there instead. |
| **what depends on it** | Finding **L15**, which is stated so that it survives either branch — the finding is the internal disagreement, not the value. Only the *direction* of the proposed correction depends on this. |

## 4 · Acquisition requests

| source | what it settles | conclusion without it | what changes either way | findings waiting |
|---|---|---|---|---|
| **Öttinger, *Beyond Equilibrium Thermodynamics* (2005)** — the book, or its table of contents and §5.3 | Whether the three PSD-closure assumptions cite the right section for the GENERIC `M`-block axiom | Unverified; the physics is standard, the section number is not checked | Either three citations stand, or three fail identically at the single point they share | 0 conditional; sharpens L4 |
| **Engel, *Phys. Rev. B* 106, 094316 (2022)** | The GaN and AlN isochoric zero-point renormalization Engel actually reports | The corpus contradicts itself; one of two pages is wrong either way | Which page gets corrected | L15 (direction only) |
| **Jackson, *Classical Electrodynamics*, 3rd ed. (1998)** — table of contents | Whether §17.2 exists in the cited edition | Probably an edition slip; unconfirmed | Whether `[PSD-rad]` loses a reference | 0 |
| **Antonius et al., *PRL* 112, 215501 (2014)** | Whether the diamond indirect-gap ZPR is −345 meV as restated | Restated on my page from `accuracy-ledger`, which owns it; the band spread −320…−366 and Engel's −323 are dropped in the restatement | Whether the restatement is merely incomplete or also wrong | L15 (secondary) |

These are cheap. Öttinger and Jackson are answered by a table of contents; Engel and
Antonius by one number each. None requires re-deriving anything.

## 5 · Calibration result

**6 of 6 planted defects caught — on the derivational and internal-consistency arm only.
The primary-source-verification arm of my method is UNCALIBRATED.** Read both halves.

### Design, and its limitation stated up front

I planted six defects, one or more per brief-defined class, into a full scratch copy of
the corpus at
`/tmp/claude-1000/…/scratchpad/calib/`, answer key at `…/scratchpad/ANSWER-KEY.txt`.

The intended design was a **blind** auditor: a fresh agent with no exposure to the
original, given my method as a written procedure, sweeping the planted copy. That agent
could not be launched — the session's subagent pool was saturated on four separate
attempts. So I ran the sweep myself, and **I had already read the originals**, which means
recognition is a live confound and a raw "6 of 6" would be worth little.

I controlled for it the only way available: for each planted defect I record the
**specific documented check that fires**, and whether that check had **already been
exercised on genuine, unplanted content earlier in this audit**. A check that produced a
real finding before the planting is not retrofitted to the answer key. Five of six meet
that bar; the sixth (P2) is stronger still, because I had run that exact check on the
*unaltered* text and concluded it was correct — so the check demonstrably discriminates
rather than merely fires.

### Result, per planted defect

| # | class | planted | caught by | check previously exercised on |
|---|---|---|---|---|
| P1 | false (sign/physics) | the two degeneracy glosses swapped — `L·δS/δx = 0` labeled "conserves energy", `M·δE/δx = 0` labeled "conserves entropy" | derivation: `dS/dt\|_L = ⟨δS, LδE⟩ = −⟨LδS, δE⟩ = 0` iff `LδS = 0`, so that condition is the **entropy** one; and PSD of `M` gives `dS/dt\|_M = ⟨δS, MδS⟩ ≥ 0`, so `M` cannot "conserve entropy" — a second-law contradiction | L2, L4 (same derivation) |
| P2 | false (formula) | f-sum prefactor `(2/π)` → `(π/2)`, an error of `(π/2)² ≈ 2.47×` | prefactor re-derivation against `∫₀^∞ ω ε₂ dω = (π/2)ω_p²` | ran on the **unaltered** text and returned "correct" — see below |
| P3 | contradiction | `Positivity` lists `L ⪰ 0` instead of `M ⪰ 0` | symbol cross-consistency: `L` is declared antisymmetric (`generic-dynamics:44`); a real antisymmetric operator has `xᵀLx = 0` for all real `x`, so `L ⪰ 0` holds only for `L = 0` | L4, L7 |
| P4 | missing information | the `ω² ≥ 0` applicability gate deleted | enforced-pointer check: `traps:394-398` names `residual-definitions#structural-categories` as its **enforcement site**; with the bullet gone the pointer is a dangling promise | L1 (same check, on `typed-compositions`) |
| P5 | misinterpretable | `[0.10, 0.60]` made to overlap `[0.60, 0.90)` at 0.60 | interval-partition check: at exactly 0.60 two phases are active, so `Algebraic/MethodEquivalence` is simultaneously excluded and included | L8 (interval boundaries) |
| P6 | false (citation) | Öttinger 2005 "section 5.3" → "section 2.3", in the `PSD-ph-ph` assumption only | citation-vs-owner consistency: three assumptions cite the same source for the same axiom ten lines apart, one now disagrees | L15 (same check, ledger vs page) |

**P2 is the load-bearing one.** Before any defect was planted I checked the f-sum rule as
written in the corpus — `(2/π)∫ω·Im ε dω = ω_p²` — against the standard form and recorded
it as **correct**, which is why it appears in no finding. The same check then rejected the
planted `(π/2)`. A check that passes the true statement and fails the false one is
discriminating; a check that only ever fires is not.

### The disjointness sweep's calibration — inherited, reported as found

L17 rests on a sweep I did not run. Its calibration came back **4.5 of 6**, and the
qualitative note attached to it was *"two method failures exposed and fixed; one real
finding surfaced only after."* I report the number unrounded and I am not folding it into
my 6-of-6: **L17 carries a 4.5-of-6 gate, not a 6-of-6 one.**

Two things follow, and the second matters more.

- The half-point and the two exposed method failures mean the sweep's *negatives* are the
  weak part — an overlap the sweep did not find is weaker evidence of absence than the
  six it did find is evidence of presence. So I state L17 as **six overlaps found**, never
  as *"and there are no others."* The pairwise space is 171 and the sweep is not
  calibrated to clear it.
- **The positives are independently re-verified and do not inherit the 4.5.** Every
  overlap in L17 is a quotation from `residual-definitions` compared against another
  quotation from the same page or from `applicability-classifiers`, and I re-read every
  one against the primary text before landing it. Two I extended rather than accepted
  (the Born-stability implication in (2), which I derived; the response-tensor overlap in
  (5), which is broader than reported), and one I bounded downward — sub-item (6) has no
  curriculum consequence, because 16 and 17 gate together, and I say so in place rather
  than letting the finding carry more weight than it earns.

### What the calibration does NOT establish

**The source-verification arm is uncalibrated, and I am not rounding that up.** P6 was
caught because the *corpus contradicted itself* about a section number — not because I
opened Öttinger 2005 and looked at §5.3. Had all three assumptions been changed
consistently, internal consistency would have passed and only reading the book would have
caught it.

That arm carries real weight in this subject: the three `PSD closure` assumptions
(`coupling-structure:650-669`) rest on Öttinger 2005 §5.3, Callen–Welton 1951,
Giustino 2017, Maradudin & Fein 1962, De Groot & Mazur Ch. IV, Breuer & Petruccione Ch. 3,
Jackson §17.2 and Gatermann–Parrilo 2004, and **not one of those has been opened**. The
undergraduate assigned to it could not be launched. So on the four-class taxonomy my
calibrated coverage is:

| class | calibrated? |
|---|---|
| contradictions | yes (P3, P6) |
| misinterpretable | yes (P5) |
| missing information | yes (P4) |
| false — formula/physics/sign | yes (P1, P2) |
| false — **citation does not say what it is cited for** | **no** |

Anything in §6 that rests on a citation being what it claims is therefore asserted on an
uncalibrated arm, and I have marked those places rather than letting the 6-of-6 cover
them. L15 is the one finding of mine in that class, and it is stated so that it does not
depend on the arm: it rests on the corpus contradicting itself, not on my having read
Engel.

### The calibration missed a whole instrument, and the planted-defect design is why

**This is the most important result in §5 and it was not visible until resumption.** All
six planted defects were *content* defects — a swapped gloss, a wrong prefactor, a
contradicted symbol, a deleted bullet, an overlapping interval, a changed section number.
Every one of them is caught by reading the text at a named location. **So the calibration
exercised only the instruments that read text at named locations, and certified those.**

It never exercised the instrument that decides *which locations to read*. Two of my
sweeps failed there, and both failed the same way:

| sweep | what it tested | what it should have tested | miss |
|---|---|---|---|
| the traps↔laws seam, 9 entries | does the named anchor carry a rule? | is the hazard covered corpus-wide, and is the rule true? | **two** — `ω² ≥ 0` (L17(1)), gauge partition (L20) |
| the per-tier scoping sentence | is the by-construction argument sound? | does the sentence that scopes it reach the terms in question? | **one** — L19 |

None of these is a reading failure. In every case I read the right page, quoted it
correctly, and asked it the wrong question. A planted-defect calibration cannot detect
that, because **planting a defect presupposes a location, and the location is exactly what
was not being chosen well.** A calibration that would have caught it looks different: plant
a defect at a site the method's *scope rules* exclude, and see whether the method ever
arrives there.

So the honest statement of my calibration is now two numbers, not one:

| arm | result |
|---|---|
| reading a named location correctly | **6 of 6**, self-designed, recognition confounded, controlled as described above |
| **choosing which locations to read** | **uncalibrated, and demonstrated defective — 3 known misses, 2 of them found by other people** |
| primary-source verification | **uncalibrated** (see above) |

The 6-of-6 stands and it covers less than I implied when I wrote it. **Two of the three
scope misses were found by others** — L20 by the state subject, L17 by the principal's
sweep — which is direct evidence that the gap is not one I would have closed by working
longer in the same way.

### Confidence assignment, given the above

Every finding is stated so that it does **not** rest on the uncalibrated arm. Explicitly:

- **Full confidence, desk-provable, no source required** — L4 (that the degeneracy
  conditions are independent of antisymmetry and positive-semidefiniteness is a
  mathematical statement, shown in the finding); the unvalued `≈ 0` tripwire (checkable
  against the tolerance ledger and nothing else); L1 (a controlled mechanical sweep plus a
  full read of the page); L2, L3, L6, L7, L8, L9, L10, L13, L16 (all internal to the
  corpus or derivable).
- **Full confidence on the finding, conditional only on the direction of repair** — L15.
  Which of two pages is wrong needs Engel; *that* one of them is wrong does not.
- **Conditional, and marked as such** — the PSD-closure citation check (G1, G2, and the
  five remaining sources). No finding of mine is built on it; it is recorded as a gap
  because the corpus's soundness depends on it even though my report does not.
- **Corrected downward by my own control probe** — L12, from medium to low-medium, with
  the falsified half retracted in place.

The 6-of-6 is therefore not doing load-bearing work anywhere it has not earned. It
calibrates the derivational and internal-consistency arm, which is the arm every
full-confidence finding above actually uses.

## 6 · Evidence transcript

I am calling very little clean, so this section is short by construction. What follows is
what I actually compared, per class. The near-findings I considered and dismissed are in
§2 with their reasons.

**Class 4 — false claims (physics/formula).** Re-derived, not read for plausibility:
the two degeneracy conditions and their stated consequences (`dE/dt|_L = 0` from
antisymmetry; `dS/dt|_L = 0` iff `LδS = 0`; `dE/dt|_M = 0` iff `MδE = 0`;
`dS/dt|_M ≥ 0` from PSD) → underwrites L2, L4, and calibration P1. The γ̂ Lie–Poisson
bracket, forward and backward, including the reality argument → L10. The f-sum rule
prefactor `(2/π)∫ω·Im ε dω = ω_p²` against `∫₀^∞ ω ε₂ dω = (π/2)ω_p²` → **correct as
written**, no finding. `α(ω) = (2ω/c)·Im(√ε)` against `α = 2ωk/c` → **correct**. The
Fermi–Dirac entropy derivative `δS_el/δγ̂ = −k_B[ln γ̂ − ln(1−γ̂)]` and its commutation with
`γ̂` → **correct**, the corpus's degeneracy argument for that block holds. The Reynolds
congruence average preserving PSD → **correct** (N3). The spinor-parity prune via the
double-group character of `Ē` → **correct** (N2). Diamond `|G| = 48 × 2 × 2 = 192` and
`192 × 250² = 12M` → **correct** (N4). Landau–Lifshitz damping sign by vector algebra
(`S×(S×H) = S(S·H) − H|S|²`, so relaxation toward `H` needs the minus sign) → the corpus
states the term unsigned, folded into L2.

**Sign sweep — every signed quantity on the three pages.** You asked for this
explicitly, so here is the whole list rather than only the failures. Checked: 15 signed or
directional expressions; **12 correct, 3 defective**.

| expression | site | verdict |
|---|---|---|
| `dx/dt = L·δE/δx + M·δS/δx` — both terms **plus** | `gd:40` | **correct.** With `M ⪰ 0` this gives `dS/dt\|_M = ⟨δS, MδS⟩ ≥ 0`; a minus would run the second law backwards. Matches the Grmela–Öttinger convention. |
| `L·δS/δx = 0` glossed "reversible part conserves entropy" | `gd:47` | **correct** by derivation (this is what calibration P1 inverted) |
| `M·δE/δx = 0` glossed "dissipative part conserves energy" | `gd:48` | **correct** by derivation |
| `E_kin = Σ\|P_I\|²/2M_I + tr(Π_hᵀΠ_h)/2W`, both `+` | `gd:68` | **correct** — standard Parrinello–Rahman form with fictitious cell mass |
| `E_BO = **min**_γ̂ ⟨Ĥ_electronic⟩` | `gd:69` | **correct** — variational principle, minimum not maximum |
| `E_EM = (1/8π)∫(\|E_⊥\|² + \|B\|²)`, `+` | `gd:71` | **correct**, and the `1/8π` fixes Gaussian/Hartree atomic units — consistent with `τ_SCF` in Ha. (It also shows the corpus *can* fix a unit convention where it chooses to, which is what makes `δ_PSD`'s silence in L5 an omission rather than a house style.) |
| `S = S_vib + S_electronic + S_config`, all `+` | `gd:80-82` | **correct** |
| `∂γ̂/∂t = −(i/ℏ)[Ĥ_KS, γ̂]` | `gd:142` | **correct** von Neumann sign — verified against `iℏ ∂ρ/∂t = [H, ρ]` |
| `L_γ̂·δS_el/δγ̂ = [δS_el/δγ̂, γ̂] = 0` | `gd:145` | **correct** as a vanishing statement (prefactor issue is L10, sign is not at stake) |
| `T_e ≥ T_L` | `rd:124` | **correct** direction — carriers are heated by the field |
| `max(0, ∫α dx − 1)²` | `rd:126` | **correct** — penalizes the excess past the breakdown condition, zero below it |
| `max(0, ΔG_form − ΔG_hull − δ_meta)²` | `rd:189-192` | **correct** — `ΔG_form − ΔG_hull ≥ 0` by construction of a lower envelope, so the band gives exactly zero inside it; diamond at +25 against `δ_meta = 50` reads 0, agreeing with `cert-obligations:141` |
| `S × (S × H_eff)` — **no sign given** | `gd:121` | **DEFECT** (L2). `S×(S×H) = S(S·H) − H\|S\|²`, so relaxation *toward* `H_eff` requires the leading minus; the reader has a 50/50 choice and the wrong one relaxes away from the field |
| Onsager reciprocity — **no equation at all** | `rd:152` | **DEFECT** (L11). Without `L_ij(B) = L_ji(−B)` the naive symmetric form scores correct physics as a violation whenever `B ≠ 0` |
| Lie–Poisson bracket missing `1/(iℏ) = −i/ℏ` | `gd:140` | **DEFECT** (L10) — the omitted factor carries both the magnitude and the `−i`, and without it the bracket is imaginary rather than real |

The pattern: **every sign the traps register guards is right, and all three defects are in
places the register does not reach.** That is a working register and an incomplete one, in
the same result.

**Class 1 — contradictions.** Pairwise-compared, with the sites: the `γ̂` operator table
row against the per-tier correction on the same page (L10); `EOM/Z` against the `Z` slot
type on `unified-state` and the immutability decision on `multiscale-state` (L6); the
regime table's absorption attribution against `typed-compositions`'s dielectric route
(L13); "SCF as gradient flow" against `computational-methods:63-67`, which classifies
`SCF-mixing` and `Pulay-mixing` as `variational-minimization` sub-methods rather than
integrators (L2); obligation 6's symbolic method against `τ_equiv`'s numerical semantics
(L9); the `Polish` band on `residual-definitions` against the `Polish` band on
`residual-loss-design` (L8); `ion-ion electrostatic` in two `CouplingSpec` listings
against the 15-row template table, which I enumerated by hand (L7).

**Added on resumption, from a close read of `generic-dynamics:158-204` — the two sections
my first pass skimmed.** `V_II(R,h)` inside `E_KS` at `:172` against "the ion–ion
electrostatic channel" as owner of the longitudinal sector at `:192` — two homes for one
energy, on one page, in a passage arguing nothing is double-counted (L7, third
consequence); the Weyl-plus-Coulomb derivation at `:186-187` against the residual-freedom
algebra, re-derived here (L20); and the Jacobi paragraph at `:161-168` against the
degeneracy claim at `residual-definitions:109-112` — **the same generated cross-blocks,
one property disclaimed in writing with a numerical check and a flag, the other granted
"by construction" with an unvalued check** (L4). That last comparison is the strongest
internal evidence in my subject, and it was sitting one section below the operator table
the whole time.

**Class 4 — false claims, second pass (L21).** Re-derived rather than read: both
`combineTol` rules against the three properties the corpus claims for them — max-abs
`max(|a|,|b|)` and root-sum-square `√(a²+b²)` are each associative, commutative and
monotone, **correct as claimed**; then the claim monotonicity is offered *for* — that it
"stops a long composition from manufacturing precision it does not have" — against the
correlated case, where `n` perfectly-correlated contributions of size `ε` give a true error
`nε` and a root-sum-square estimate `√n·ε`, **monotone and `√n` too small**. So the
properties are right and the guarantee drawn from them is not. Then the corpus's own
statement that 99%-shared DAG ancestry "is the common case"
(`residual-definitions:318-322`) against the composition rule 22 lines later (`:348-350`).
Control on the negative: `independen*` returns **zero** hits in `typeclass-alphabet.md` and
`accuracy-ledger.md` and three unrelated hits in `residual-definitions.md`, while the same
instrument returns the per-stage *cost* rule where one exists — so the absence is the
corpus's, not the sweep's.

**Class 3 — missing information.** Swept for: a tolerance on the degeneracy tripwire
(corpus-wide, none exists — L4); a unit convention for `M` making `δ_PSD`'s "absolute"
meaningful (corpus-wide, none exists — L5); the magnetic-field reversal in the Onsager
statement (three `Onsager` sites, none carries it — L11); a sign on the Landau–Lifshitz
damping term (none — L2); mass weighting in the phonon extraction (neither
`generic-dynamics` nor `typed-compositions` carries it — L12); a source for the "30–40%"
lattice-expansion fraction (one site, uncited, and it does not reconcile with the
ledger's own 21%/18% — L15).

**Class 2 — misinterpretable.** Interval-partition check across every numeric range on
the pages (found the `Polish` collision, L8; the four category-gate bands themselves
partition correctly). **Bare symbols in the `Positivity` list (`σ ⪰ 0`, `ρ ≥ 0`) —
now closed, L18.** Method: sweep every occurrence of each symbol in `journals/`, sort the
hits into senses, then test which sense the *bare* form takes at every site that is not
the one under audit. `σ` returns seven senses, two of them on `residual-definitions`
itself; `ρ` returns five, and its bare form is the charge density at five of five sites —
which is signed, making the residual false under the corpus's own usage. Controls in the
finding. Also swept: the four members of category 16 against category 16's own predicate
(two fail — L17(6)); "space-group equivariance" against both categories that claim it
(L17(5)).

**Class 1 — contradictions, second pass over the category vocabulary.** The pairwise
disjointness question, which my first draft left open, is answered in L17 and I record the
comparisons: `ω² ≥ 0` (`:119`) against "dynamical stability" (`:183`) — one condition,
two categories, two gates, **one applicability mask**; `‖Tr γ̂ − N_e‖²` (`:114-118`)
against category 16's predicate (`:181-182`) — satisfied exactly, by a term the same
sentence denies is conservation; `γ̂† = γ̂` and `0 ⪯ γ̂ ⪯ 1` (`:128-132`) against the same
predicate — satisfied; `elastic-stability-criteria` against `dynamical stability` within
category 16 — the first strictly implies the acoustic limit of the second, derived in
place; category 16's *"no environment field"* against `applicability-classifiers:133-141`,
which declares the `ω² ≥ 0` gate **environment-swept**, and against
`generic-dynamics:118`, which makes `C_ij` an isothermal quantity. And the schema check:
`ContributionFacets.category` is scalar-typed on a map keyed by `ResidualKey` with facets
excluded from identity (`:216-235`), so multiple categorization is unrepresentable and one
of two bad branches is forced at every overlap.

**Class 2 and 3 — the scoping sentence, checked rather than assumed (L19).** My first pass
verified the *construction* the by-construction claim needs and did not check the sentence
that says **where** it has to hold. On resumption I read `generic-dynamics:132-137`
against the two partitions it names: `multiscale-state#three-tiers` (micro/slow/macro) and
`born-oppenheimer-levels#hierarchy` (four levels over the micro seven-tuple, declared a
*partition* at `born-oppenheimer-levels:34`). `γ̂` and `R` fall together under the first and
apart under the second, so the extent of the conditions differs by reading. Then: the
page's own two by-construction arguments (`:140-153`) are both at level granularity; a
coupling is defined as an **off-diagonal** block of `L` or kernel of `M`
(`coupling-structure:63-73`), with *"every cross-regime term … is one instance of this
object"* (`:75`); and the MVP's worked channel declares `pieces = [γ̂, R]` (`:219`), which
straddles two levels. Control run: swept the four pages for an assignment rule placing a
cross-level block at a level — **none**, while the same sweep *does* return the
target-shape assignment rule at `coupling-structure:63-73`, so the instrument finds
assignment rules where they exist.

**Every negative sweep here is control-probed.** Six of my findings rest on an *absence*
found by a pattern sweep, and an absence from a method that has not demonstrated it can
produce a presence is not a result. So each negative below was paired with a control that
had to fire before the negative was allowed to count.

| negative claimed | control run | control result | negative |
|---|---|---|---|
| `typed-compositions` contains no GENERIC content (**L1 — the headline**) | identical pattern against `generic-dynamics.md` | every alternative fires: `GENERIC` 4, `δE` 5, `δS` 7, `Poisson` 11, `friction` 4, `dx/dt` 3, `equation of motion` 2 — **including the Unicode `δ`**, which was the live risk given `traps:681-689`'s ASCII-character-class hazard | **confirmed** — 1 hit, `cell-metric-extraction`, unrelated |
| no tolerance on the degeneracy tripwire (L4) | tolerance-symbol pattern against the pages that carry tolerances | fires on `residual-definitions`, `coupling-structure`, `cert-obligations` | **confirmed** — the only co-occurrence is the `≈ 0` line itself; one further hit was `multiscale-state:394`'s *carrier* degeneracy, a word collision (→ L16) |
| no magnetic-field reversal on Onsager (L11) | pattern run against a file with the notation deliberately written into it | 3 hits | **confirmed** — zero corpus-wide |
| no unit convention making `δ_PSD`'s "absolute" meaningful (L5) | self-controlling: the same sweep returned `Hartree`, `Gaussian units`, `1/8π` | fires | **confirmed** — none applies to `M` |
| no mass weighting at the phonon extraction (L12) | pattern against the corpus | **fired — on `property-templates:82`** | **NEGATIVE FALSIFIED.** The control found what the finding claimed was absent. L12 corrected, downgraded, and partly retracted |

The fifth row is the reason the discipline is worth its cost. My original L12 asserted a
corpus-wide omission; the control probe located `HarmonicStiffnessHessianOf` defined as
"the mass-weighted dynamical matrix" on the page that owns the template, which falsified
half the finding. Five of six negatives survived control; **one did not, and it was one of
mine.**

**The traps↔laws seam, swept entry by entry.** §0 claims the register's guarded
conventions are right where it guards them; this is the basis. Every `traps` entry naming
one of my three pages as its enforcement site, checked against the text actually there:
*Entropy-production direction* (`dS/dt ≥ 0` from the H-theorem, so `−S[f]` non-increasing
— **correct**); *Gauge and electrostatic partition* → `generic-dynamics#gauge-partition`
(**present and consistent**); *Density-matrix admissibility is scored, not presupposed* →
`residual-definitions#structural-categories` (**present**: `γ̂† = γ̂`, `0 ⪯ γ̂ ⪯ 1`,
`Tr γ̂ = N_e`, idempotency gated to zero temperature); *Real phonon frequencies are gated
to claimed-stable phases* → same anchor (**present at the named site — and the entry
still fails; see the correction below**); *The hull residual is
temperature- and pressure-aware* → `residual-definitions#constraint-categories`
(**present**, with the metastability band and the +25 meV/atom diamond case);
*A model-versus-microscopic pair is a consistency pair* → `residual-definitions#pair-kinds`
(**present**); *Positive semidefiniteness is a condition on the assembly* →
`coupling-structure#psd-closure` (**present**, and the congruence-action requirement
matches); *Polarization-convention pairing* → `coupling-structure#polarization-pairing-guard`
(**present**, 3.4× agrees across both pages); *Zero-point renormalization is the isochoric
value* → `coupling-structure#slope-kind-guard` (**rule present and correct** — it is the
*values* restated beneath it that fail, L15). Nine enforced pointers, nine resolving to
text that carries the rule. No dangling promise on this seam.

**Correction to this sweep. Two of the nine passed and should not have, and the method
lesson is the most useful thing in this report.**

- **`ω² ≥ 0`** (`traps:394-398`) names `residual-definitions#structural-categories` as its
  enforcement site; that anchor covers categories 8–10, the rule is there, and the pointer
  resolves — so my test returned "present". But the same condition appears a second time
  at `:183` under `#constraint-categories`, **ungated**, and from training fraction 0.60
  the ungated copy does exactly what the trap says is broken (L17(1)).
- **Gauge and electrostatic partition** → `generic-dynamics#gauge-partition`. I recorded
  it as *"present and consistent"*. The anchor is present; the section is **not**
  consistent — its normative sentence derives transversality from time-independent
  residual freedom, which cannot deliver it (L20). I confirmed the section existed and
  said something about gauge. I did not check whether what it said was true. **The state
  subject found this on my page, and I did not.**

**Both misses have one shape: my test was `pointer → text`, and the right test is
`hazard → corpus` and `claim → physics`.** Verifying that a named site carries a rule
cannot discharge an `enforced` marker, because the marker is a claim about the corpus, not
about one anchor; and verifying that a section exists cannot discharge its content.

**This is the brief's own diagnosis, realized in my method rather than in the corpus.**
The brief opens by saying every existing check in this repository validates *links* and
none asks whether a claim is true. My traps-seam sweep was a link check. I built the
corpus's characteristic defect into my own instrument and then reported the result as an
evidence transcript for a clean verdict — *"Nine enforced pointers, nine resolving to text
that carries the rule. No dangling promise on this seam."* That sentence is true and it
was not the question.

**Revised status of the seam: 7 of 9 as far as I have taken it, not 9 of 9**, and the
seven are seven under the weak test. I have not re-run all nine under the strong one, and
I am recording that rather than implying coverage. Anyone re-running this seam should
apply the strong test to all nine.

This is the same shape as the L12 control failure and the third instance of it in this
report: a check that only confirms presence at a named location is not a check on absence
elsewhere, and a check that confirms a section exists is not a check that it is right.

**The existing gate sees none of this.** `python tools/check_structure.py --check` returns
`structure OK · 45 pages, 273 owned topics, 51 open questions`, exit 0, with all fifteen
findings in place — including L1, where the corpus's central claim cites a page that does
not contain it. That is the expected result and it is the point: the citation resolves, so
the structure checker passes. Nothing I did changed the checker's result.

**Not checked, and I am naming it rather than implying coverage.** Updated on resumption;
the first draft listed six items here and four are now closed.

| item | status |
|---|---|
| the referents of `σ` and `ρ` in category 10 | **closed by me** — L18 |
| pairwise disjointness of the 19 categories | **closed** — L17, from the principal's sweep, re-verified against primary text. Six overlaps *found*; the pairwise space is 171 and the sweep's 4.5-of-6 calibration does not clear the rest, so this is not "and there are no others" |
| the magnetic-field consequence of the Onsager omission | **closed by me** — L11 addendum, from `observable-bundles:68` and a controlled negative on `out-of-scope` |
| non-Markovian dynamics in `M` | **judged not load-bearing and folded into L7**, with the reason stated at N6 rather than left pending |
| every primary source behind the three PSD-closure assumptions — 8 citations | **arm running**, verdicts land in §3/§4 |
| the rotational sum rule's written form against Born–Huang | **arm running.** The principal's register carries a one-line result ("wrong as written; frame-dependent; nonzero on correct force constants") — **I have not banked it**, because rule 1 forbids resting a finding on a summary and the claim is algebraic |
| the correct dissipative structure for reaction networks and Markov chains | **arm running** — supports L3, which already stands without it on desk-provable grounds |
| whether an agreement theorem exists for the Kubo/BTE pair | **arm running** — supports L9, which already stands without it |

**Still genuinely unchecked, with nobody on it:** whether any source behind my citations is
machine-learned-potential-derived rather than measured or *ab initio* (N10's downstream
note); and the strong-form re-run of all nine traps-seam entries, which I recommend to
whoever picks this up — I re-ran two and both failed.

**The report is incomplete in exactly those places and should not be read as a clean
verdict over them.**

## 7 · Log-worthy advancements

Reported, not written — `log/timeline.md` has a single writer.

1. **The corpus's central claim has no derivation, and its only mechanical gate tests a
   weaker proposition** (L1). This is the most consequential item in my subject and it is
   a new realization of the dangling-promise class on the highest-stakes pointer in the
   corpus.
2. **"Enforced by construction" was verified and fails** (L4): typed targets give
   antisymmetry and PSD, which do not imply either degeneracy condition; and the sole
   check on it is the only unvalued threshold in the certification layer.
3. **A closed vocabulary cannot construct a channel its own MVP spec activates** (L7).
4. **The 19-category vocabulary is not a partition, and the schema requires one** (L17).
   Six overlaps; the page's sole disjointness argument covers one of 171 pairs; and the
   sharpest overlap **bypasses an applicability gate the corpus installed on purpose**,
   from training fraction 0.60.
5. **Two of the 19 are not residuals of a candidate state** — `EOM/Z` is ill-typed (L6)
   and `Degeneracy` is a library self-test (L4d). The closed vocabulary the corpus counts
   as 19 contains 17 of the kind the other 17 are.
6. **The scoping sentence offered in place of a construction is stated over two different
   partitions at once** (L19), and on the reading the page's own arguments use it excludes
   the MVP's headline coupling.
7. **The error budget's composition rule is unsound in the case the corpus calls common**
   (L21) — root-sum-square without an independence condition, on a DAG whose contributions
   the same page says usually share 99% of their ancestry. The monotonicity property the
   corpus names as the safeguard does not prevent the failure it is offered against. Four
   other findings files touch `combineTol` and all four ask who supplies its inputs; none
   asks whether the rule is right. This is the sentence L4 turns on, and it went unexamined
   through my first pass — I had checked the construction and not the statement that says
   where the construction has to hold.

**A third method rule, paid for the same way the register's other two were.** The register
records two rules bought by near-misses — *a finding rests on the primary text* and *every
negative needs a control*. Here is a third, and it is bought by three actual misses rather
than near ones:

> **A planted-defect calibration certifies reading, not scope.** Planting a defect
> presupposes a location; it therefore exercises only the instruments that read at
> locations already chosen, and it certifies those while saying nothing about the rule
> that chose them. Report scope coverage as a **separate arm**, and calibrate it
> differently: plant a defect at a site the method's own scope rules *exclude*, and see
> whether the method ever arrives.

My 6-of-6 was a reading score reported as a method score. Three defects in my subject
lived outside my scope rules and not one was a reading failure — in every case I read the
right page, quoted it correctly, and asked it the wrong question. **Two of the three were
found by other people** (L17 by the principal's sweep, L20 by the state subject), which is
the evidence that the gap would not have closed by working longer in the same way. The
specific bad scope rule, stated so it can be avoided: *checking that a pointer resolves to
text carrying a rule* — which is the corpus's own characteristic defect, reproduced inside
the instrument built to find it.

Three candidates for the **traps register**, each a hazard this subject demonstrated
rather than merely a defect:

- *A declared gap can understate its own hazard.* The `curriculum-phase-names` open
  question describes a name **rotation** as a name **substitution**, which reads as
  benign and conceals that `Polish` binds to two disjoint bands across a live seam (L8).
  A declared gap is trusted as triaged, so an inaccurate one is worse than none — the
  same argument the register already makes about dangling promises versus broken links.
- *A constraint set that the absence of dynamics satisfies teaches nothing* (L14).
  Warmup's `Conservation` + `Positivity` are both exactly zeroed by a frozen trajectory.
- *An absolute tolerance on a dimensional quantity is a unit convention in disguise*
  (L5). `δ_PSD = 1e-9 absolute` is either vacuous or permanently tripped depending on a
  convention the corpus never states; every other tolerance in the ledger that could be
  scale-free is relative.
- *An `enforced` pointer that resolves is still not enforcement.* The `ω² ≥ 0` entry names
  an anchor that does carry the rule, and the hazard reappears at a second site outside it
  (L17(1)). The register's own test has to be **hazard → corpus**, not **pointer → text**;
  the second form passes exactly when the first copy is correct, which is when a duplicate
  is most likely to have been written. This refines the principal's `enforced`-class gate:
  a marker should name a checker probe *over the hazard*, not a page that states the rule.
- *A closed vocabulary generated by a schema symmetry inherits the symmetry's exposure*
  (L6). "One equation-of-motion category per state slot" is a clean rule that silently
  produces an ill-typed member the moment one slot is not a differentiable manifold. Any
  "one X per Y" rule in this corpus carries the same hazard, and the generated member
  looks exactly like the authored ones.
- *A token collision can make an unenforced guarantee read as enforced* (L16b).
  `architectural-principles:65` — "a degeneracy the oracle cannot stand behind is caught
  at compose time and refused" — binds, for a reader who knows the residual category, to
  the one guarantee the corpus does **not** enforce. This is worse than an ambiguous name:
  the wrong branch is reassuring.
- *A safeguard can be stated against the wrong failure mode, and then it reads as coverage*
  (L21). The corpus names **monotonicity** as "the load-bearing property" that stops a long
  composition manufacturing precision it does not have. Monotonicity is real and it is not
  that property: the way an error budget manufactures precision is by under-estimating, and
  root-sum-square under-estimates correlated contributions by `√n` while staying monotone
  throughout. A named, true, load-bearing-sounding property attached to the wrong hazard is
  harder to catch than no property at all, because it terminates the reader's search.
- *A scoping qualifier that names two partitions scopes nothing* (L19). *"Per tier / per
  level"* reads as one qualifier and is two: the tiers and the Born–Oppenheimer levels
  partition the state differently, so a condition scoped this way has a different extent
  under each reading — and the corpus's most important structural guarantee sits on it.
  The corpus already has an owned-term rule that no token may name two things; **this is
  the same failure at the level of a phrase**, and the slash is what hides it. Generalizes
  beyond this instance: any `A / B` written as a gloss should be checked for whether `A`
  and `B` are actually coextensive.
- *The overloaded-token register has no symbol entries at all* (L18). Its ten rows are
  words. `σ` carries seven senses in this corpus and `ρ` five — collisions larger than
  several the register does list — and symbol collisions are outside its reach by
  construction, not by judgment. Either the register admits symbols or the corpus needs a
  second mechanism for them.

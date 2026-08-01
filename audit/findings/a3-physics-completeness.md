# Pass B — physical completeness

Auditor 3, principal's own sweep. Four angles were planned. **Two died on grounding**, and
saying so is the result — a premise killed before it was dispatched is the rule working, not
a wasted angle. What survives is narrower and better than what was planned.

Method: corpus first, literature second, always. Every finding quotes the corpus verbatim.

---

## P1 — the refusal set and the target envelope overlap at the product's operating point

**Verdict:** ABSENT as an aggregate. **STRONG.**

**What the product exists for.** `purpose-and-scope.md`:

> chips that must function inside, for instance, a jet turbine: temperatures above 500 °C, thermal cycling, mechanical vibration, high field, high current density, possibly radiation.

**What the oracle refuses.** The accuracy ledger, on the headline breakdown-field row:

> **Above 500 °C is cert-refused frontier**

and, in the same row's reasoning cell:

> The distribution-tail anchor data are absent, so above 500 °C is **not** a met target

and on the hot-carrier distribution row:

> Since no anchor data exist in V1 it **ships as identity**, and the high-field-by-high-temperature corner stays cert-refused

**The finding is not that these are hidden — each is recorded honestly in its own row.** The
finding is that **nothing in the corpus aggregates them.** No page states the union of what
the oracle refuses and compares it against the operating envelope the product is built to
serve. Each refusal is local to a ledger row; the overlap is only visible by reading across
rows, which is exactly why no single page confesses it.

Read together, the refusals cluster at one corner — **high field, high temperature** — and
that corner is the product's operating point, not an edge case.

**Why this is a completeness finding and not bookkeeping.** A consumer holding an oracle-file
can enumerate its contents; the environment-box stamp makes out-of-box use mechanically
detectable per call. But nothing tells a *reader of the specification* that the certified
envelope and the target envelope are substantially disjoint where it matters most. That is a
fact about the specification, and it is absent from it.

**Control.** Searched `grep -rn -i "cert-refused\|not a met target\|refused frontier" journals/` → hits in `out-of-scope.md` and `accuracy-ledger.md` only, each local to one row or one exclusion. Control that fires: `grep -rn -i "envelope" journals/` → the concept of a validity envelope *is* present and reachable by search, so the absence of an aggregate is not a search failure.

---

## P2 — noise observables are absent, and absence is not the corpus's discipline

**Verdict:** ABSENT. **MEDIUM.**

Thermal (Johnson–Nyquist) noise, shot noise and 1/f noise appear **nowhere** in the corpus —
not as observables, not as registry rows, not as bundles.

That alone would be unremarkable. What makes it a finding is that **the corpus's own
discipline is to declare what it excludes**, and it does so carefully, with reasons:

> - **Deep-defect non-Markovian dynamics** — a Markov master-equation closure is assumed.

> - **Strongly-correlated systems** — frustrated Wigner crystals, spin liquids, Mott
>   physics. The one-body density matrix is mean-field by construction, and ultra-wide-gap
>   materials are large-gap and far from Mott physics.

Creep, dislocation climb, total-ionizing-dose effects, amorphous films and general dopant
redistribution are each on that page with a stated reason. **Noise is not.** It is absent
rather than excluded, in a corpus that otherwise excludes explicitly — so a reader cannot
tell whether it was considered and dropped, or never considered.

**Scope caution, stated honestly.** Noise figures are a real device metric but plausibly
secondary to breakdown, thermal and reliability behaviour, all of which *are* covered. This
finding is about the corpus's own consistency of practice, not a claim that noise physics is
required.

**Control.** Searched `grep -rli "shot noise\|1/f\|Johnson-Nyquist\|thermal fluctuation" journals/` → zero files. Control that fires: `grep -rli "Johnson" journals/` → 2 files, both of which are **Johnson-Mehl-Avrami-Kolmogorov crystallization kinetics**, an unrelated Johnson. The control is what proved the token was reachable and the concept still absent — a naive reading of the first search would have been a false negative in the other direction.

---

## Premises killed by grounding — reported because a killed premise is a result

### P3 — harsh-environment failure modes are *not* missing

The planned angle was: *does any residual fire on cyclic mechanical fatigue, or on
electromigration under high current density?* **Both are carried.** `data/registry-manifest.csv`
row 83:

> 83,plastic-strain-fatigue-life,"`(Δε_p, c) → N_f`",B11,T0,D1,cheap,S3 (a.k.a. Coffin–Manson),thermal cycling

The signature takes a plastic-strain amplitude and a material constant and returns cycles to
failure, and the row's own dependency cell reads `thermal cycling`. Electromigration carries a
mean-time-to-failure row and an accuracy-ledger activation-energy entry. Radiation enters as an
environment field:

> | `radiation_flux` | `ParticleFlux` (cm⁻²s⁻¹) | read by the displacement and Frenkel-pair formulas |

And the exclusions are reasoned rather than silent — continuum creep and dislocation climb are
excluded because *"classical transition-state theory is adequate at an operating temperature of
600 K and above"*, and total-ionizing-dose is excluded while displacement damage is kept.

**The corpus's coverage of its own stated target environment is substantially stronger than a
skeptical prior assumed.** Recorded as a confirmed strength.

### P4 — the GENERIC form's Markovian, noiseless character is handled, not overlooked

The planned angle was that `dx/dt = L·δE/δx + M·δS/δx` is Markovian and carries no fluctuation
term, and that this is a structural limit rather than an omission. **The corpus addresses both.**

Non-Markovian dynamics is explicitly excluded with its closure named — *"a Markov
master-equation closure is assumed."* And fluctuation-dissipation is not missing from the
dynamics; it is doing load-bearing work as the justification for the friction operator's
positive-semidefiniteness:

> Assumption [PSD-e-ph]   — electron-phonon dissipation kernel M_{e-ph}

> Reference: Öttinger 2005 section 5.3 (DOI 10.1002/0471727903); Callen–Welton 1951

That is the correct and standard construction: the dissipative structure is *derived from*
fluctuation-dissipation while the fluctuating force itself is averaged out. For an oracle that
scores instantaneous lawful tendency rather than integrating trajectories, a deterministic
generator is the right object. **Premise withdrawn.**

---

## Coverage

| Area | Status |
|---|---|
| `purpose-and-scope.md` target envelope | read fully |
| `accuracy-ledger.md` refusal and frontier rows | read partially — the refusal-bearing rows and the tolerance and anchor tables; the full 400-plus-line ledger not read line by line |
| `out-of-scope.md` exclusions | read fully |
| `coupling-structure.md` positive-semidefiniteness assumptions | read partially — the assumption block |
| `multiscale-state.md` slow-tier kinetics | read partially |
| `data/registry-manifest.csv` | searched by content, not read row by row |
| The seven slots as irreducible degrees of freedom | **NOT READ — angle 3 not run.** Stated rather than left implicit |

## Near-findings rejected

- **Magnetic properties reach no observable bundle.** Real, but the corpus declares it
  accurately in its own frontmatter — *"magnetic properties are in scope with no residual
  grouping behind them."* An honest self-report, not a gap the audit found.
- **Flexoelectricity below the numerical-noise floor.** Excluded with a stated reason.
- **β-Ga₂O₃ hole transport cert-refused.** Declared, and folded into P1's aggregate rather than
  counted separately.

## By-catch

- The accuracy ledger's own open question `aln-high-temperature-conductivity-absence` records a
  possible over-refusal — an absence claim that may be too strong, costing coverage silently.
  The ledger's phrasing of the hazard is worth keeping: *"an unnecessary refusal costs coverage
  silently, and nothing will ever fire on it."*

---

# Angle 3 — are the seven slots irreducible?

Run separately, after the four angles above. The Coverage table records this angle as not run;
it has now been run and this section replaces that line.

The question tested: **is there a degree of freedom a real crystal in this program's target
regime actually has, which is neither one of the seven slots, nor legitimately emergent, nor
legitimately in another tier?**

**The closure claim does not survive.** Two such degrees of freedom exist. Four further
candidates were tested and died — two on grounding, two on literature — and they are reported
below because a killed premise is a result.

Method unchanged: corpus first, literature second. Blockquotes are verbatim corpus text only;
control searches and reasoning are in plain text.

---

### P5 — the vector potential has no conjugate momentum, and the energy functional reads it anyway

**Verdict:** ABSENT. **STRONG.**

**The closure claim under test.** `unified-state.md`:

> These seven are the **irreducible degrees of freedom of the micro tier**.

**Every other dynamical slot comes as a canonical pair; `A` does not.** The seven-tuple carries
positions with momenta and the cell with its momentum:

>          Π_h,    cell momentum (Parrinello–Rahman)  ∈ ℝ^{3×3}

and `generic-dynamics.md` names both pairings as symplectic blocks of the Poisson operator:

>   · symplectic on (R, P)         canonical ion phase space
>   · symplectic on (h, Π_h)       Parrinello–Rahman cell phase space

The residual vocabulary carries the cell momentum as a first-class degree of freedom of its own:

>   6. `EOM/Π_h` — same form on the cell-metric conjugate.

`A` enters with no partner:

>          A )     external EM vector potential       ∈ ℝ³ field A(r,t)

**And the corpus treats `A` as dynamical, not as a prescribed external drive.** Three
independent statements establish this. The Poisson operator carries a Maxwell block:

>   · Maxwell on A                 Hamiltonian form of the EM field

that block is asserted to be *canonical*, which is a claim about a conjugate pair:

> Canonical blocks (symplectic `(R,P)`, `(h,Π_h)`; Lie–Poisson `γ̂`; Maxwell `A`)

and the field has its own equation-of-motion residual category:

>   2. `EOM/A` — same form on the EM gauge potential.

**What is missing, and why it is a physics gap rather than a notation gap.** In the Coulomb
gauge the corpus fixes — `A₀ ≡ 0`, `∇·A = 0` — the transverse electromagnetic field is a
Hamiltonian system whose canonical coordinate is `A` and whose canonical momentum is
`Π = −E_⊥/4πc`. Both are independent initial data: for a free radiation field, `A` and `E_⊥`
are the two quadratures of each mode, and a state with `A ≠ 0, E_⊥ = 0` is a physically
different state from one with the same `A` and `E_⊥ ≠ 0`. `E_⊥` is not recoverable from `A` at
an instant, so it is not emergent under the corpus's own axiom; it belongs to no other tier;
and it is not one of the seven.

The corpus's own energy functional makes the gap self-evident. It is written as a functional of
`A` alone and its integrand contains `E_⊥`:

>      + E_EM[A]          (1/8π) ∫ (|E_⊥|² + |B|²) dr   — transverse sector only;

`B = ∇×A` is recoverable. `E_⊥` is not. So `E_EM[A]` is not a functional of `A`, and the whole
dynamical form

> dx/dt = L · δE/δx + M · δS/δx

loses its meaning on the `A` block: `δE/δx` requires `E` to be a function of the state, and the
`EOM/A` residual has no computable right-hand side.

**The obvious repair fails, and its failure is the point.** One might define `E_⊥ = −(1/c)∂A/∂t`
and have the caller supply the rate. That makes `E` a functional of `ẋ` rather than of `x`, so
`dx/dt = L·δE/δx` becomes an implicit equation in which the right-hand side needs the very
quantity it produces. The GENERIC structure the corpus is built on requires `E[x]`; a state
lacking `E_⊥` cannot supply one.

**Control.** Searched `grep -rn "Π_A" journals/` → 0 hits. Searched `grep -rn "conjugate"
journals/` → 2 hits: `conjugate-gradient`, an optimiser, and `EOM/Π_h — same form on the
cell-metric conjugate`. So the corpus uses the concept of a conjugate momentum slot exactly
once, and applies it to `h` rather than to `A`. Searched `grep -rn "E_⊥" journals/` → 2 hits,
both inside `generic-dynamics.md`, both inside the energy functional, never as a state slot.
Control that fires: `grep -rn "Π_h" journals/` returns the slot, its symplectic block, its
residual category and its kinetic-energy term — the full complement of places a conjugate
momentum appears when the corpus carries one. `A` has none of them.

**Literature.** The canonical pair `(A, −E_⊥/4πc)` for the transverse field in Coulomb gauge is
the standard nonrelativistic-QED construction — the same one the corpus names when it partitions
the electrostatic sector out. Cohen-Tannoudji, Dupont-Roc & Grynberg, *Photons and Atoms:
Introduction to Quantum Electrodynamics*, Wiley-Interscience 1989, ISBN 0-471-84526-4,
chapters I–II. **I could not verify a DOI for this book and am not supplying a guessed one**;
the ISBN is confirmed.

---

### P6 — the state cannot distinguish two isotopes, in a corpus whose flagship material has the largest known isotope effect

**Verdict:** ABSENT. **STRONG.**

**What the state carries.** Slot five is the atomic number:

>          Z_I,    species labels (immutable)         discrete

and the residual vocabulary says so explicitly:

>   7. `EOM/Z` — same form on atomic-number labels; non-trivial only under

The species vocabulary is elemental, not nuclidic:

> `AtomicSpecies` is the ordinary closed vocabulary of the elements, and it is the
> key universe of the pseudopotential set. Its membership is
> `{C, B, N, Al, Ga, O, H}`.

**What the state needs.** The energy functional divides by an ion mass:

> E[x] = E_kin(ions)      Σ_I |P_I|²/2M_I + tr(Π_hᵀΠ_h)/2W

`M_I` occurs exactly once in the corpus, at that line. Atomic number does not determine it —
¹²C and ¹³C share `Z = 6` and differ in mass by 8.3%. Every phonon frequency scales as
`M^(−1/2)`, so two states identical in all seven slots have different dynamical matrices,
different vibrational entropies and different thermal conductivities.

**The corpus knows this and records it, without a slot to put it in.** The accuracy ledger
quantifies the isotope dependence of a material constant it carries:

> The atomic weight matters at this precision — natural abundance gives 3.5157, pure carbon-12 gives 3.5125

and `traps.md` makes isotope a mandatory declaration on every thermal-conductivity reference row:

> solution, not to the relaxation-time approximation. Every conductivity column declares
> its isotope, boundary and relaxation-time-versus-iterative scope. — enforced,

So the corpus requires each reference datum to say which isotopic composition it was measured
at, and then offers no way to say which isotopic composition a *candidate state* has. A battery
row measured on ¹²C-enriched diamond and a prediction for natural diamond are compared as though
they described the same system.

**Not emergent, and not another tier's.** Isotopic mass is not recoverable by coarse-graining
from positions, momenta and atomic numbers on any timescale — it is independent input data. It
is not a slow, history-dependent quantity (it does not evolve at all), and it is not a
device-scale homogenised field. It fails every branch of the emergence axiom, so by the corpus's
own partition it must be first-class micro state. It is absent from the seven slots, and also
from all three top-level inputs: `SiteDecoration` carries species drawn from the elemental
vocabulary above, `Environment` has no isotope field, and `TheoryContext`'s pseudopotential map
is keyed by `AtomicSpecies`.

**Why it matters here specifically, rather than in principle.** Diamond is this corpus's MVP
material, and diamond has the largest isotope effect on thermal conductivity of any known solid;
thermal conductivity is one of the corpus's headline observables, carried by registry rows 25,
121 and 122, and it is the coefficient the macro tier's heat equation homogenises. This is not a
precision correction — it is a ~50% effect on a headline number, larger than most of the
accuracy targets in the ledger.

**Control.** Searched `grep -rn "isotop" journals/` → **1 hit** in the entire corpus, the
`traps.md` line quoted above, which demands the declaration rather than providing the slot.
Searched `grep -rn "mass number\|atomic mass\|nuclide" journals/` → 0 hits. Searched
`grep -rn "M_I" journals/` → 1 hit, the energy functional. Control that fires:
`grep -rn "mass" journals/` returns effective-mass tensors, mass densities, mass-weighted
dynamical matrices, mass-action and the `√(2Mω)` vertex-normalisation trap — 13 lines across
8 files —
so mass vocabulary is thoroughly reachable by search, and the absence of isotopic mass is real
rather than a search failure. Second control: `grep -rn "atomic weight" journals/` fires in
`accuracy-ledger.md`, which is how the quantified statement above was found.

**Literature.** Anthony, Banholzer, Fleischer, Wei, Kuo, Thomas & Pryor, "Thermal diffusivity of
isotopically enriched ¹²C diamond", *Phys. Rev. B* **42**, 1104 (1990),
DOI [10.1103/PhysRevB.42.1104](https://doi.org/10.1103/PhysRevB.42.1104) — a 0.1% ¹³C crystal
measured 50% higher room-temperature thermal diffusivity than a natural-abundance (1.1% ¹³C)
crystal. Wei, Kuo, Thomas, Anthony & Banholzer, "Thermal conductivity of isotopically modified
single crystal diamond", *Phys. Rev. Lett.* **70**, 3764 (1993),
DOI [10.1103/PhysRevLett.70.3764](https://doi.org/10.1103/PhysRevLett.70.3764). Most relevant to
this program's operating range, because it spans it: Olson, Pohl, Vandersande, Zoltan, Anthony &
Banholzer, "Thermal conductivity of diamond between 170 and 1200 K and the isotope effect",
*Phys. Rev. B* **47**, 14850 (1993),
DOI [10.1103/PhysRevB.47.14850](https://doi.org/10.1103/PhysRevB.47.14850).

---

## Premises killed — angle 3

### P7 — nuclear quantum effects: the corpus's reasoning survives the literature test

**Verdict:** premise withdrawn.

The planned attack was that ion positions and momenta are classical fields while hydrogen —
named in this corpus as its own silent killer, with a redistribution row and a desorption row —
is a light nucleus whose delocalisation and tunneling are large, so the nuclear wavefunction is
a degree of freedom the seven slots cannot carry.

**Grounded first.** `nuclear quantum` returns 0 hits; `path integral` returns 1 hit and it is
the Berry-phase polarization evaluator, unrelated. So the corpus makes exactly one claim in this
area, and it is scoped to reaction rates:

> - **Plasma-process surface damage; grain-boundary statistics; continuum creep and
>   dislocation climb; quantum-tunneling-corrected reaction rates** — classical
>   transition-state theory is adequate at an operating temperature of 600 K and above.

The relevant corpus row runs at that temperature:

>   hydrogen in diamond `E_diff = 1.7 eV` and `D(500 °C) ≈ 1e−13 cm²/s`, giving a redistribution

**Then tested against literature, and the corpus wins.** Herrero & Ramírez computed hydrogen and
muonium jump rates in diamond by quantum transition-state theory in the path-integral centroid
formalism, over a range extending to about 1000 K — *Phys. Rev. Lett.* **99**, 205504 (2007),
DOI [10.1103/PhysRevLett.99.205504](https://doi.org/10.1103/PhysRevLett.99.205504). Their
quantum effective barriers are renormalised relative to the zero-temperature classical
calculation and decrease with rising temperature, and the quantum and classical rates converge
at high temperature, as the classical limit requires. Their classical barriers for the BC→T
transition, 1.6–2.1 eV, bracket the corpus's own 1.7 eV. The corpus's number is the right kind
of object and its stated temperature justification is sound for this material at this operating
point.

Two honest qualifications. First, the study's convergence statement is qualitative in the text
available to me; I did not obtain a tabulated quantum-to-classical ratio at 773 K, so I am
reporting agreement in direction and magnitude rather than a verified numeric bound. Second, the
exclusion is worded for *tunneling*, and the effect the literature actually shows is
vibrational-mode quantisation of the barrier — a different mechanism that the wording does not
name. That is a scoping imprecision in an exclusion, not a missing degree of freedom, so it goes
to by-catch rather than becoming a finding.

**Withdrawn.** The corpus already treats nuclear motion quantum-mechanically where it matters
for thermodynamics — phonon spectra with Bose–Einstein occupations, the quasi-harmonic
approximation, zero-point renormalisation — and classically where it integrates. That is the
standard and defensible division, not an omission.

### P8 — the non-equilibrium distributions: emergence is defended, and the regime where it fails is refused

**Verdict:** premise withdrawn.

The planned attack was that the emergence axiom waves through the carrier and phonon
distributions too fast. The axiom:

> A quantity `y` is **emergent** from a tier — excluded from that tier's state — **iff** it is
> recoverable from that tier's state by coarse-graining **on the same timescale and the same

and its application:

> Phonon occupations `n_{q,s}`, the carrier distribution `f_n(k,r)`, and the electron and lattice
> temperatures are emergent at the micro timescale: they fast-equilibrate to a function of the

The attack looked promising because the corpus then runs Boltzmann transport *on* those
distributions —

>   · semiclassical streaming      on emergent distributions

— and a distribution slaved to the local state cannot stream.

**It dies on grounding.** The corpus states the position deliberately rather than by oversight,
and it refuses precisely the regime where the distribution becomes an independent degree of
freedom: the hot-carrier distribution tail is cert-refused above about 500 °C, the corresponding
learned correction ships as identity, and the anchor data are declared absent. In the
diffusive, near-equilibrium regime that remains, the deviation `δf` is the solution of a linear
problem in the local state and the driving field, so it is a derived object and the axiom holds.
The one place the argument is genuinely strained — steady-state versus transient on timescales
shorter than the momentum relaxation time — is unreachable for a scorer that never integrates.

**Withdrawn.** Recorded because it looked like the strongest available attack on the emergence
axiom and it is not one.

---

## Coverage — angle 3

| Page | Status |
|---|---|
| `unified-state.md` | read fully |
| `generic-dynamics.md` | read fully |
| `born-oppenheimer-levels.md` | read fully |
| `gamma-hat.md` | read fully |
| `multiscale-state.md` | read fully |
| `crystal-inputs.md` | read fully |
| `residual-definitions.md` | read fully |
| `out-of-scope.md` | read fully |
| `canonical-vocabularies.md` | read fully |
| `coupling-structure.md` | read partially — `CouplingSpec`, `TheoryContext`, channel record, invariant-generator cache key |
| `traps.md` | read partially — full anchor list; the units, lattice-transpose and conductivity-error sections |
| `accuracy-ledger.md` | searched by content — the mass-density, isotope and hot-carrier rows; the full ledger not read line by line |
| `computational-methods.md`, `typed-compositions.md`, `capability-slices.md`, `property-templates.md` | searched by content only |
| `data/registry-manifest.csv` | not read in this angle |

The line in the Coverage table above reading *"The seven slots as irreducible degrees of freedom
— NOT READ — angle 3 not run"* is superseded by this section.

## Near-findings rejected — angle 3

- **Nuclear spin and hyperfine structure.** `hyperfine` and `nuclear spin` each return 0 hits,
  against a control on `spin` that fires 30 times across 16 files (Pauli-spinor `γ̂`, spin–orbit
  schemes, spin-doubled groups, magnetic moments). So the corpus is silent rather than explicit.
  Rejected as a physics finding: hyperfine energies are of order neV against `kT ≈ 66 meV` at
  the operating point, and nuclear spin couples to no observable in scope. This is a
  documentation gap in a corpus that otherwise excludes explicitly — the same shape as P2 — not
  a missing degree of freedom.
- **A per-site defect charge state at the micro tier.** Rejected on physics: the cell's electron
  count is fixed by `‖Tr γ̂ − N_e‖²` and local charge is a readout of `γ̂`, so charge is
  genuinely emergent at the micro tier; charge-state *change* is correctly placed in the slow
  tier as `charge_dist[D]`, and each micro composition compiles at fixed charge.
- **Electron correlation beyond one-body.** The `γ̂` slot is mean-field by construction and the
  corpus excludes strongly-correlated systems with a stated reason. Excluded, not missing.
- **Core electrons.** Folded into the pseudopotential, which is a recorded `TheoryContext` axis
  with a content-pinned file digest. Handled.
- **The longitudinal electrostatic field.** Owned by the matter functionals under an explicit
  gauge partition, and the macro tier keeps `E(r) = −∇φ` emergent as quasi-static with a stated
  reason. Handled — and deliberately *not* conflated with P5, which is about the transverse
  radiation sector.
- **Surface coverage.** Listed as emergent, and correctly so: an adsorbate is an atom at a
  position, already carried by `R_I` and `Z_I`.

## By-catch — angle 3

- The tunneling exclusion is scoped to *tunneling* while the effect the hydrogen literature
  shows at 600–1000 K is vibrational-mode quantisation of the barrier. The exclusion's reasoning
  is right; its wording names the smaller of the two mechanisms.
- No page states whether the barriers entering the Arrhenius rows are bare electronic barriers
  on `E_BO` or zero-point-corrected free-energy barriers. `generic-dynamics.md` puts
  minimum-energy-path search on `E_BO`, which is electronic, and no formula adds a nuclear
  zero-point term.
- `coupling-structure.md` enumerates `SubDofTag` as `orbital | spin | sublattice | valley`,
  four members with no `charge`; `multiscale-state.md` states that `ChargeState` reuses a
  `SubDofTag = charge` "already admitted on the species labels". The member is used and not
  enumerated.
- The macro mesh's worked cell size of ~10 nm is far below diamond's phonon mean free path, so
  the homogenised Fourier closure `D_thermal = κ/(C_p·ρ_m)` with a bulk `κ` is being applied
  across cells where transport is ballistic. Off this angle's question, but it bears on the
  homogenisation map's validity.

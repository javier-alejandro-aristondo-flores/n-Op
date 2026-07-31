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

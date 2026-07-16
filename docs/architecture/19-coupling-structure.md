---
id: arch-19-coupling-structure
title: Coupling structure
status: draft
revision: 1
canonical-for:
  - CouplingChannel record
  - invariant-generator routine
  - coupling target shapes (Scalar | AntisymmForm | PSDSymmForm)
  - coupling coverage policy
  - CouplingSpec record
  - KernelExt extension family
  - polynomial-sufficiency flag
  - CoverageBound record
  - TheoryContext placement
depends-on:
  - arch-04-state
  - arch-05-generic
  - arch-06-physics-graph
  - arch-07-pipeline
  - arch-09-vocabularies
  - arch-11-residuals
  - arch-12-cert
  - arch-13-applicability
  - impl-07-residual-factory
referenced-by:
  - impl-09-cross-cutting
  - impl-10-build-sequence
  - arch-20-representations
  - arch-21-multiscale-state
research-sources: []
---
# Coupling structure

Cross-regime physics — electron-phonon, spin-orbit, magneto-elastic,
minimal coupling, phonon-phonon scattering, radiative damping, … —
is one kind of object with a small parameter space, not a hand-rolled
list of named terms.

## 19.1 The object

A **coupling** is a symmetry-respecting function from a tensor product
of pieces of the state vector (`arch-04-state`) into one of three
target shapes:

- **`Scalar`** — a real-valued function; lands in `E_coupling`
  (`arch-05-generic §5`).
- **`AntisymmForm`** — an antisymmetric 2-form on the tangent bundle;
  lands as an off-diagonal block of `L` (`arch-05-generic §5`).
- **`PSDSymmForm`** — a positive-semidefinite symmetric 2-form on the
  cotangent bundle; lands as an off-diagonal kernel of `M`
  (`arch-05-generic §5`).

Every cross-regime term in `arch-05-generic` is one instance of this
object.

## 19.2 The parameter axes

```
record CouplingChannel {
  pieces        : List<StatePiece>            -- ordered tensor factors
  target        : Scalar | AntisymmForm | PSDSymmForm
  order         : Nat                         -- # tensor factors (typically 2..4)
  derivative    : Ultralocal | Gradient(Nat)  -- spatial-derivative depth
  applicability : (Crystal, Environment) → Bool
  -- coverage-policy fields (§19.9–§19.10):
  mechanism_range  : MechanismRange               -- curated; source of truth for the next flag
  kernel_extension : Optional<KernelExt>          -- the non-polynomial part; present iff ¬polynomial_sufficient
  gauge_rule       : Optional<GaugeRule>          -- basis/gauge fixing (e.g. Wannier gauge); usually None
  provenance       : Optional<ProvenanceLedger>   -- where the coefficients came from; the normal annotation
}

record StatePiece {
  component : StateComponent                  -- one of γ̂, A, R, P, h, Π_h, Z
  sub-dof   : SubDofTag                       -- orbital | spin | sublattice | valley
                                              -- | strain | gauge | charge | none
}
```

`StateComponent` is the existing 7-tuple alphabet (`arch-04-state`).
`SubDofTag` enumerates the internal labels a component carries:
γ̂ carries `orbital`, `spin`, and (when applicable) `sublattice`,
`valley`; `h` carries `strain`; `A` carries `gauge`; etc. The
allowed `(component, sub-dof)` pairs are tabulated alongside the
state-component definition.

`order` and `derivative` declare the truncation. They are not part of
the underlying physical structure; they are the compose-time choice of
how high in the multipole / multi-tensor expansion to go.

The last four fields carry the coverage policy. `mechanism_range`
(§19.10) records whether the channel's mediating interaction is
short-range or long-range; from it the derived flag
`polynomial_sufficient` decides whether the symmetry-generated
polynomial basis is the *whole* coupling or only its short-range part.
When it is only a part, `kernel_extension` (§19.11) carries the
non-polynomial remainder. `gauge_rule` fixes a residual basis ambiguity
for the rare channels that have one; `provenance` records where the
numeric coefficients came from and is the ordinary annotation every
channel may carry. All four are `make-coupling-channel`-validated
(§19.8).

## 19.3 The invariant generator

```
generate-invariants : CrystalSymmetryGroup × CouplingChannel
                    → GeneratorOutput
```

Standard representation theory. Given the crystal's symmetry group
(`arch-09-vocabularies` lifts `CrystalSymmetryGroup` to a first-class
typeclass entity; Stage 2 already builds it from
`PeriodicityStructure × SiteDecoration`) and a channel specification,
this routine returns the finite basis of `target`-shaped
symmetry-invariant terms of the requested `order` and `derivative`.

Each `InvariantTerm` is a symbolic tensor expression carrying:

```
record InvariantTerm {
  channel         : CouplingChannel
  irrep-coefficients : IrrepCoefficientTable   -- the trivial-irrep coefficients
                                               -- of the underlying tensor product
  symbolic-form   : SymbolicTensor             -- the explicit term; stored as the
                                               -- root of a MerkleDAG[SymbolicTensorOps,
                                               -- TypedLeaf] per arch-20 §20.2
  generator-hash  : Address[InvariantTerm]     -- domain-separated content address
}
```

The generator returns a `GeneratorOutput`, not a bare list, because a
channel's full coupling may be the polynomial basis *plus* a
non-polynomial kernel (§19.10–§19.11):

```
record GeneratorOutput {
  polynomial_invariants : List<InvariantTerm>     -- the symmetry-generated basis
  polynomial_sufficient : Bool                     -- echoed certificate (derived, §19.10)
  kernel_extension      : Optional<KernelExt>      -- the non-polynomial remainder, if any (§19.11)
  gauge_rule            : Optional<GaugeRule>       -- a basis-fixing rule, if any
  output_hash           : Address[GeneratorOutput]  -- domain-separated; folds in all three above
}
```

The `polynomial_sufficient` flag is echoed into the output so that a
downstream stage holding only `polynomial_invariants` can never silently
treat a partial (short-range) basis as the complete coupling.

The generator is the *constructive* direction of the irrep machinery
that Stage 2 already uses *decompositionally* (`arch-07-pipeline §7.2`
block-diagonalizes operators by irrep). Same module; same primitives;
new direction.

**Contract.** The routine runs three integrity guards, a free O(1)
spinor-parity pre-prune, then the projector:

```
generate-invariants(G, c) :
  -- (0) well-formedness (§19.10): the flag and the kernel must agree
  if ¬polynomial_sufficient(c) ∧ c.kernel_extension = None: error "partial coverage, no kernel"
  if  polynomial_sufficient(c) ∧ c.kernel_extension ≠ None: error "sufficient channel carries a kernel"
  if ¬polynomial_sufficient(c) ∧ ¬kernel_tag_matches_range(c): error "kernel tag ≠ mechanism_range"
  -- (1) spinor-parity pre-prune: an odd total spinor count cannot form a Scalar / PSDSymmForm /
  --     AntisymmForm invariant, so the basis is empty before any character is computed
  if odd_spinor_count(c.pieces) ∧ c.target ∈ {Scalar, PSDSymmForm, AntisymmForm}: poly = []
  else: poly = trivial_irrep_projector(G, c.pieces, c.target, c.order, c.derivative)
  -- (2) return both parts; the kernel rides through untouched by the symmetry projector
  return GeneratorOutput{ poly, polynomial_sufficient(c), c.kernel_extension, c.gauge_rule, … }
```

**Emptiness and complexity.** Emptiness of `poly` is decided by the
character inner product `⟨χ_T, χ_trivial⟩_G = (1/|G|) Σ_g χ_T(g)`, a
single trace per group element — never forming `ρ(g)` explicitly. For
the MVP worst case (`|G| ≤ 192` with the double cover and time reversal,
`dim(T) ≤ ~250` at `order = 4, Gradient(1)`): the character pre-prune is
O(|G|) ≤ ~200 ops; the full Reynolds projection `P = (1/|G|) Σ_g ρ(g)`,
run only when the basis is non-empty, is O(|G|·dim(T)²) ≤ ~12M ops. The
result is cached on `Address[CrystalSymmetryGroup] × Address[CouplingChannel]`
(`arch-20-representations §20.4`), so per-composition cost is one-shot.
The cache key does **not** include the theory context (§19.11): the
polynomial basis is symmetry-determined and theory-independent.

> **Emptiness ≠ correctness.** A non-empty `poly` is *correct as far as
> it goes* but may still be only the short-range part of a long-range
> coupling. Whether `poly` is the *whole* coupling is the separate
> `polynomial_sufficient` question (§19.10), not the emptiness question.

## 19.4 Worked example — diamond electron-phonon

The library author declares one channel:

```
electron-phonon = CouplingChannel {
  pieces        = [ StatePiece(γ̂, orbital), StatePiece(R, none) ]
  target        = Scalar
  order         = 2
  derivative    = Ultralocal
  applicability = is-crystalline                     -- always true for diamond
}
```

At compose time:

1. **Stage 1** records the channel in `Stage1Sidecar.coupling-channels`.
2. **Stage 2** has already constructed the diamond symmetry group
   (Fd-3m + time-reversal).
3. **Stage 2.5** (new sub-stage, §19.5) runs
   `generate-invariants(Fd-3m+TR, electron-phonon)` and returns one
   `InvariantTerm`: the canonical `g_{nm,ν}(k,q)` matrix element
   written as a symmetry-respecting tensor.
4. **Stages 3–4** lower that `InvariantTerm` into a `FormulaApply`
   node attached to the `E_coupling` aggregator (a
   `MethodInvoke(hamiltonian-assemble, …)` node).

The symmetry group generates the admissible **form** of `g_{nm,ν}(k,q)` — which
invariants exist and their index structure. The **numerical values** (deformation
potentials, Fröhlich and anharmonic parameters) are supplied by the
`ProvenanceLedger` (DFPT / finite-difference / fits), outside the generative
structure: symmetry generates the form, provenance supplies the values.

Spin-orbit, magneto-elastic, minimal coupling (γ̂ ↔ A), Stark, Zeeman,
phonon-phonon, radiative damping — each one is a `CouplingChannel`
record with a different parameter assignment. None of those strings
appears as a value in any enum.

## 19.5 Stage 2.5 — invariant synthesis

A new sub-stage in `arch-07-pipeline §7.2`, executed between Stage 2's
block-diagonalization rewrite and Stage 3's algebraic simplification.

```
Inputs  : Stage1Sidecar.coupling-channels  : List<CouplingChannel>
          CrystalSymmetryGroup             (constructed in Stage 1+2)
Action  : For each channel c whose c.applicability holds, compute
          generate-invariants(group, c); attach the returned
          GeneratorOutput to the channel.
Outputs : Stage2_5Sidecar.invariants : Map<CouplingChannel, GeneratorOutput>
```

Consumed by Stages 3–4 when lowering invariants into `FormulaApply`
nodes targeted at the existing `E_coupling`, `L_assembly`,
`M_assembly` aggregator methods.

## 19.6 Composition

- **Within a single `target`.** Invariants compose by direct sum:
  `E_coupling = Σ_{c} Σ_{v ∈ invariants[c] | v.target = Scalar} v.symbolic-form`,
  and analogously for the L and M target shapes.
- **Across `target` shapes.** Composition is the existing E / L / M
  assembly in `arch-05-generic`.
- **Order truncation is monotone.** Order-`(n+1)` includes order-`n`
  as a prefix; the spec author chooses the cutoff per channel.
- **No channel-correlation primitive in V1.** If two physical
  mechanisms genuinely correlate (a cross-term in `M` between two
  scattering processes that are not independent), they are modeled as
  *one* `CouplingChannel` with a larger tensor product (more `pieces`),
  not two channels with an extra correlation parameter. This keeps the
  V1 algebra additive.
- **Kernel extensions add as one more summand.** When a channel carries
  a `kernel_extension` (§19.11), its lowered kernel node adds into the
  same aggregator as its polynomial invariants:
  `full_coupling = Σ poly_invariants + kernel_extension(q, ω)`. No new
  aggregator and no new composition primitive — the kernel is one summand
  in the existing direct sum. A long-range mechanism is therefore split
  into **two channels** — a short-range polynomial channel and a
  long-range kernel channel — rather than one channel that is partly
  polynomial and partly not (e.g. electron-phonon = a deformation-potential
  channel + a Fröhlich channel, the standard Verdi–Giustino SR/LR split,
  `arch-19 §19.10`).

## 19.7 Cert hooks

The invariant-generator structure simplifies two cert obligations
(`arch-12-cert`):

- **The symmetry-equivariance obligation.** Polynomial invariants are
  trivial-irrep basis vectors *by construction*; equivariance is
  automatic. Cert reduces to a numerical projection-residual check:
  `||v.symbolic-form − π_trivial v.symbolic-form|| < δ_sym` on a sampled
  evaluation. Failure indicates a generator bug, not a physics bug. A
  `kernel_extension` is **not** exempt: it is "scalar under the
  little-group of q" (`KernelExt.symmetry_law`, §19.11), so cert checks
  `‖K(Rq,ω) − D(R) K(q,ω) D(R)†‖ < δ_sym` over little-group elements `R` —
  a checkable equivariance, just not a polynomial one.
- **The positivity obligation** (antisymmetry of `L` / PSD of `M`).
  The `target` tag determines a projection rule applied at the
  generator step: `AntisymmForm` invariants are projected onto the
  antisymmetric component of the candidate tensor; `PSDSymmForm`
  invariants are projected onto the PSD cone. The projection is part
  of the generator's contract; cert numerically verifies the projected
  output matches the emitted `symbolic-form` within `δ_sym` (`arch-12 §12.0.2`).
  For `PSDSymmForm` channels, PSD *existence* is a structural theorem rather
  than a runtime search — see the documented assumptions in §19.12 — and the
  runtime PSD guard is checked on the **assembled dissipative super-block per
  mechanism** (diagonal + off-diagonal kernels together), not per off-diagonal
  kernel, via `arch-12 §12.0.1` obligation 2.

The polynomial checks are O(1) per invariant; both are integrated with
`SymmetryAdaptedHamiltonianOf` (`arch-09-vocabularies §9.2`) which
already lives in the symmetry machinery. The cert-obligation indices are now
fixed in `arch-12 §12.0.1`: equivariance = obligation 1, antisymmetry of `L` =
obligation 5 (conservation), PSD of `M` = obligation 2 (positivity).

## 19.8 Registration discipline

Channels register through the same factory pattern as residual
generators (`impl-07-residual-factory §7.3`):

```
make-coupling-channel(channel : CouplingChannel) → CouplingChannel
```

Returns the channel with its `applicability` validated as first-order
decidable on typeclass tags (the registration-time invariant from
`impl-04-formulas`). The channel's identity is `Address[CouplingChannel]`
under the canonical-serialization rule of `arch-20-representations §20.4`
(domain-separated, schema-versioned); identical channels collapse to one
address.

**Coefficient-provenance contract.** Symmetry generates the *form* of a channel's
invariants; the *values* (deformation potentials, Fröhlich and anharmonic
parameters, compact-model coefficients) enter through the channel's
`ProvenanceLedger` (§19.4 caveat). Each provenanced coefficient must carry:
`(value, σ, source, cost-class)` — where `cost-class ∈ {curated, per-material-DFPT,
fit}` declares its acquisition pipeline and `σ` its uncertainty (reusing the
reference-battery `σ` machinery, `arch-12 §12.1`). A **cert obligation refuses any
composition whose active channels carry coefficients without a `ProvenanceLedger`
entry** (an unprovenanced coefficient is a silent accuracy hole). For the MVP the
diamond coefficients are `curated`; other materials are `per-material-DFPT` and their
provenance is the gating data-acquisition task before that material is claimed.

**`slope-kind` tag — machine-checkable double-count guard for `dE_g/dT` (AHC).** Any
temperature-slope coefficient feeding `ahc-gap-renormalization` (registry row 120) additionally
carries `slope-kind ∈ {isochoric, total}`. The quoted experimental `dE_g/dT` slopes are mostly
*total* (they already fold in the lattice-expansion part that registry row 63 — `Ξ·strain` —
carries separately, ~30–40% of the shift). A **cert obligation refuses any composition in which a
`total`-tagged AHC slope and row-63's thermal-expansion T-path are both active on the same
observable** (double-counting the expansion contribution); an `isochoric`-tagged slope composes
with row 63 freely. The tag is a first-class field on the coefficient, so the check is a tag
comparison at compose time, not a reviewer caveat. The curated ZPR amplitudes feeding the `coth`
path (`docs/accuracy-ledger.md §1/§15`) are the **isochoric** electron-phonon values (Engel PRB 106
094316 (2022) / Miglio npj CM 6 167 (2020) AHC: GaN −189, AlN −399, diamond −345 meV), tagged
`isochoric`; the zero-point lattice-expansion part (Miglio: GaN −49, AlN −85 meV) is row 63's job —
so seeding a `total` magnitude into the e-ph `coth` path while row 63 is active is exactly the
double-count this guard refuses. (Wave-1 III-N audit: `docs/audits/2026-06-10-wave1-iii-n-audit.md`;
the prior `total` tag on isochoric Engel magnitudes was corrected there.)

**Polarization reference / proper-improper `e₃₁` self-consistency — machine-checkable pairing
guard.** Spontaneous polarization is reference-dependent; the 2DEG density `n_s` (registry row 115)
consumes an interface *difference* `ΔP` whose ±5% accuracy for AlGaN/GaN rests on an **accidental
cancellation** (Dreyer et al. PRX 6 021038 (2016) §V.D–E) between the spurious zinc-blende(ZB)-
reference term in `P_sp` and the proper-vs-improper `e₃₁` error — two large, opposite-sign
quantities — **not** generic reference-cancellation. The cancellation holds only under a
**self-consistent pairing**: either (a) ZB-reference `P_sp` + **proper** `e₃₁` + no ZB-correction
(the spec's path), or (b) layered-hexagonal-reference `P_sp` + `ΔP_corr` + **improper** `e₃₁`.
Because improper `e₃₁ ≈ 3.4× proper` for GaN/AlN, mixing conventions silently corrupts `n_s`. Each
polarization coefficient (`P_sp` row 113, `e₃₁` rows 114/117) therefore carries
`polarization-reference ∈ {ZB-proper, H-improper}`; a **cert obligation refuses any composition
whose active `P_sp` and `e₃₁` carry mismatched tags** (`arch-12 §12.0.3`). The ±5%-ΔP target also
carries an `is-AlGaN-GaN` validity scope — the cancellation **fails for high-In InGaN/GaN** and is
σ-degraded / cert-refused there. The spec's curated III-N coefficients (`docs/accuracy-ledger.md`)
are all `ZB-proper`.

**Learned-correction training contract (`Δα` EDF-tail and any PINO-fit residual coefficient).** A
coefficient whose `source` is a PINO-learned correction — the high-field EDF-tail correction
`Δα(E,T_L,T_e)` of the avalanche channel is the only V1 instance — is constrained two ways so it
cannot launder away its own supervision signal: (1) it is fit **only against external anchors**
(measurements or future BTE / full-band-MC points) and is **frozen with respect to the PINO
training loss** — gradients of the physics loss do not flow into it — because a correction trained
on the same residual it modifies can co-adapt to zero that residual and silently destroy the
obligation-9 domain it is meant to protect; (2) until such external anchors exist (the V1 corpus
has none — `docs/accuracy-ledger.md §49`), `Δα` **ships as the identity** (zero correction) and the
high-E×high-T corner stays **cert-refused** (`obligation 9`), making the ">500 °C breakdown =
cert-refused" stance load-bearing rather than decorative.

The active channels in a composition, **together with the theory frame
they are interpreted in**, are the **`CouplingSpec`**:

```
record CouplingSpec {
  channels       : SparseSet[CouplingRegistry]   -- the active channels (arch-20 §20.3)
  theory_context : TheoryContext                  -- the global theory frame (§19.11)
}
```

`CouplingSpec` was previously a bare `SparseSet[CouplingRegistry]`; it is
now a two-field record. Its `Address` is computed by the
`arch-20-representations §20.4` record rule, so two specs with identical
channel sets but different `theory_context` are guaranteed distinct
addresses — the theory frame is part of identity, automatically. The
`CouplingSpec` schema version is **bumped** (`arch-20 §20.9`) so old
bare-set addresses cannot collide with new record addresses. The spec is
carried alongside the composition request (`arch-07-pipeline §7.1`). The
diamond MVP's `CouplingSpec` is short: electron-phonon (short-range) +
minimal coupling + ion-ion electrostatic + phonon-phonon scattering
(in `M`), under the MVP default theory context (§19.11).

`theory_context` is **definitional input**: it is set at Stage 1, and it
must exist before Stage 2 builds the (possibly double-cover) symmetry
group, because the relativistic treatment determines whether the group
carries the spin SU(2) factor. A `make-theory-context(raw) → TheoryContext`
smart constructor (mirroring `make-coupling-channel`) **must** normalize
and validate before any `Address[TheoryContext]` is taken — this is
load-bearing for content addressing, not optional: it normalizes the
hybrid-functional double representation (a hybrid is always
`XCFunctionalTag.Hybrid` with `ManyBodyLevel.KohnSham`, never
`HybridAsManyBody`) and enforces relativistic PP/run consistency, so two
byte-distinct encodings of the same physics can never produce two
addresses.

## 19.9 Coverage policy (not a hand-curated registry)

The "coupling-channel template registry" is **not** an enumerated list of
coupling terms. A channel is a tuple in the parameter space
`(pieces, target, order, derivative, mechanism_range, applicability)`; the
registry is a **coverage policy** — a bounded subset of that space — plus
the runtime rule:

> the active channels for crystal `C` are those whose `applicability`
> holds and whose invariant basis is non-empty under the crystal's
> symmetry group `G_C`.

The invariant generator (§19.3) is the filter that culls structurally
empty tuples; the spec author never enumerates terms, only declares
bounds wide enough that generator + applicability prune to the right
active set automatically. The bound is the `CoverageBound`:

```
record CoverageBound {
  global_cap         : (max_order : Nat, max_derivative : Derivative)  -- (4, Gradient(1)) for the MVP
  per_mechanism_caps : PersistentMap<MechanismClass, (Nat, Derivative)> -- tighter inner pruning table
}
```

The MVP global cap is `(max_order = 4, max_derivative = Gradient(1))`.
The single driver of `order = 4` is lattice anharmonicity (4-phonon
scattering, significant for diamond/GaN above room temperature); every
other mechanism class fits inside `(2, Gradient(1))`, with a few reaching
`order = 3`. The per-mechanism inner table prunes tuples *before* the
character test so the generator never spends cycles on orders physics
never visits for that mechanism. Both are coverage-policy parameters, not
physical claims.

The principled template set (~15 rows) is the `mechanism_range` table of
§19.10 — which now includes the **piezoelectric acoustic** channel
(`LongRangeStatic(1)`, `1/q` pole) alongside the Fröhlich (`1/q²`) one, the second
long-range e-ph mechanism the wurtzite III-N members carry (`is-noncentrosymmetric`-gated — piezoelectric scattering needs a piezoelectric class, the arch-13 split;
inert for diamond). This **closed the former arch-18 coupling-channel coverage-policy item** (now recorded under `[arch-18-open-decisions]` Closed decisions).

## 19.10 Mechanism range and polynomial sufficiency

Some couplings are not polynomials of any finite degree in the state
variables: they are functions of the wavevector `q` and/or frequency `ω`
with an *essential* non-polynomial structure — a pole at `q = 0` (the
Fröhlich `1/|q|²` polar-optical coupling) or poles in `ω` (dynamical
screening: the screened Coulomb interaction `W(q,ω)`, the GW self-energy
`Σ(k,ω)`, the TDDFT kernel `f_xc(q,ω)`). For these, the generator's
polynomial basis is correct but **incomplete** — it captures the
short-range part and misses the long-range/dynamical part.

Whether a channel is complete is **not** decidable from
`(pieces, target, order, derivative)` and the symmetry group alone: the
short-range deformation-potential e-ph channel and the long-range
Fröhlich e-ph channel have *identical* signatures. Long-range-ness is a
property of the physical mechanism, so it is carried explicitly:

```
record MechanismRange =
  | ShortRange                          -- analytic / exponentially-localized mediator
  | LongRangeStatic(pole_order : Nat)   -- 1/|q|^p, ω-independent (Fröhlich p = 2, van der Waals, bare-Coulomb head)
  | LongRangeDynamical                  -- frequency-dependent screening: poles in ω (W, Σ, f_xc)
```

`mechanism_range` is curated once per template (the table below). The
flag `polynomial_sufficient` is then a total, O(1) **derived projection**:

```
polynomial_sufficient(c) =
  match c.mechanism_range with
  | ShortRange         => true
  | LongRangeStatic(0) => true            -- a constant "pole" is just a coefficient
  | LongRangeStatic(_) => false
  | LongRangeDynamical => false
```

with the well-formedness invariant enforced by `make-coupling-channel`:
`polynomial_sufficient(c) ⟺ (c.kernel_extension = None)`, and a non-sufficient
channel's `kernel_extension.tag` must match its `mechanism_range`.

`mechanism_range` says "this mechanism is long-range *when active*";
`applicability` (§19.2) independently says "this mechanism is active for
this crystal." They are orthogonal: a Fröhlich channel is long-range by
mechanism yet inert in a non-polar crystal (diamond, zero Born charges)
via `applicability`.

The coverage-policy template table (the 15 principled channels;
all `ShortRange`/polynomial-sufficient except where noted):

| Channel template | `mechanism_range` | `polynomial_sufficient` |
|---|---|---|
| electron-phonon (deformation-potential, SR) | `ShortRange` | true |
| electron-phonon (Fröhlich polar-optical, LR) | `LongRangeStatic(2)` | **false** |
| electron-phonon (piezoelectric acoustic, LR) | `LongRangeStatic(1)` | **false** |
| spin-orbit | `ShortRange` | true |
| magneto-elastic | `ShortRange` | true |
| minimal coupling / light-matter | `ShortRange` | true |
| phonon-phonon (anharmonic) | `ShortRange` | true |
| radiative damping | `ShortRange` | true |
| exchange / Heisenberg | `ShortRange` | true |
| Zeeman | `ShortRange` | true |
| Stark / electric-dipole | `ShortRange` | true |
| strain-electronic (Bir-Pikus) | `ShortRange` | true |
| screened Coulomb / RPA `W(q,ω)` | `LongRangeDynamical` | **false** |
| GW self-energy `Σ(k,ω)` | `LongRangeDynamical` | **false** |
| TDDFT `f_xc(q,ω)` | `LongRangeDynamical` | **false** |

The frequency-dependent screening channels are not in the diamond MVP
`CouplingSpec`; they are the forcing function for the schema. ALDA
`f_xc` is the degenerate corner of `LongRangeDynamical` (a constant
kernel): tag a channel by its *general* mechanism, not by the cheapest
approximation of it, so swapping ALDA → a tabulated kernel needs no
re-tag.

## 19.11 Extension types — `KernelExt`, `GaugeRule`, `TheoryContext`

**`KernelExt`** carries the non-polynomial part of a long-range coupling.
All four variants share one backbone: a section of a `BZ × ℝ_ω` fiber
bundle valued in a bounded-rank tensor — they differ only in tensor rank,
real-vs-complex value, and whether they are given parametrically or as a
tabulated grid. No new substrate primitive is needed; every field maps
onto the `arch-20-representations §20.1` primitives.

```
record KernelExt {
  tag           : FroehlichLongRange | ScreenedCoulombRPA | GWQuasiparticleSelfEnergy | TDDFTXCKernel
  domain        : MomentumOnly | MomentumFrequency | KpointFrequency | RealSpaceRadial
  value_rank    : Rank0 | Rank2_GG | Rank2_bands | Rank2_cart
  value_field   : RealField | ComplexField
  symmetry_law  : QSymmetryLaw                    -- "K is scalar under the little-group of q" — the bridge to symmetry
  representation : Parametric(KernelParams) | Tabulated(KernelGrid) | Hybrid(KernelParams, KernelGrid)
  provenance    : Optional<ProvenanceLedger>
}
```

`Parametric` kernels (Fröhlich: `ε_∞`, `ε_static`, Born charges `Z*`,
`ω_LO`; LRC `f_xc`: a single `α`) are tiny (< 1 KB). `Tabulated` kernels
(the RPA dielectric matrix, the GW self-energy) can be large: the
full-frequency dense dielectric matrix for diamond (`12³` q-mesh × 64
frequencies × 500 G-vectors, complex) is ≈ **440 GB** worst case,
dropping to ≈ 0.5 GB after a plasmon-pole model + irreducible-BZ
reduction. The grid is a `CacheEligible` sidecar attached by
`Address[TabulatedField]` (`arch-20 §20.6`) — folded into the channel's
identity by address, never by value, so content-addressing stays O(1).
**No MVP channel is tabulated** (the active set is all-polynomial;
Fröhlich for the polar members is `Parametric`); tabulated storage is a
V2 concern, and the 440 GB figure is the number the persistent-storage
tier must be designed against before those channels turn on.

**`GaugeRule`** resolves a residual continuous basis ambiguity (e.g. the
Wannier-gauge / orbital-projection choice for a downfolded channel). It is
`None` for every MVP channel and is recorded only when a P3 gauge-fixing
rule is genuinely attached.

**`TheoryContext`** is the global theory frame on `CouplingSpec` (§19.8).
A coupling constant is meaningful only relative to the simulation that
produced it — a `J_ij` under PBE is a different number than under HSE06 —
so the frame is part of the spec's identity:

```
record TheoryContext {
  xc_functional          : XCFunctionalTag                         -- closed C1 vocabulary (arch-09 §9.7)
  pseudopotential_set    : PersistentMap<AtomicSpecies, PPRecord>  -- closed discriminators; open file id (content-pinned)
  many_body_level        : ManyBodyLevel                            -- closed C1; sub-records for +U / GW / DMFT
  relativistic_treatment : RelativisticTreatment                    -- closed C1
}
```

The vocabularies backing these four fields (ten closed C1 vocabularies) are
defined in `arch-09-vocabularies §9.7`. The
theory context does **not** enter the `generate-invariants` cache key
(the polynomial basis is symmetry-only; the relativistic treatment's
one effect — spin-orbit — enters through the symmetry group's double
cover, captured by `Address[CrystalSymmetryGroup]`, not here). It does
**not** enter the runtime kernel either: by Stage 4 the theory choice has
already selected the symmetry group and conditioned the coefficient
values, so the lowered kernel is theory-agnostic. `theory_context` is
therefore solely metadata for the cert + provenance layer (§19.7).

The **MVP default theory context** is `GGA(PBE)` / PseudoDojo v0.4.1
norm-conserving (Ga with the `3d` semicore shell promoted to valence) /
`KohnSham` (plain DFT) / `ScalarRelativistic` (no explicit SOC; the MVP
set is non-magnetic with no SOC-dependent observable). PBE's known
underestimate of UWBG band gaps is handled by theory-conditioning the
reference-battery obligation (§19.7), not by upgrading the default;
`Hybrid(HSE06)` is the documented accuracy upgrade for gap-sensitive work.

## 19.12 PSD closure for `PSDSymmForm` channels

A `PSDSymmForm` channel lands as an off-diagonal block of the GENERIC
friction operator `M`, which must be positive-semidefinite so that
entropy production stays non-negative. The invariant generator returns a
basis of `G`-invariant *symmetric* tensors, but membership in that linear
subspace does not by itself guarantee any combination is PSD (a linear
condition vs. a convex-cone condition).

For the MVP `PSDSymmForm` channels (e-ph and ph-ph dissipation) plus the
near-term radiative-damping channel, PSD is **structurally
guaranteed by physics** — it is a documented assumption, not a runtime
search:

```
Assumption [PSD-e-ph]   — electron-phonon dissipation kernel M_{e-ph}
  Origin:    GENERIC M-block axiom + fluctuation-dissipation theorem
             + Fermi-golden-rule Gram structure (sum of squared coupling matrix elements)
  Reference: Öttinger 2005 §5.3 (DOI 10.1002/0471727903); Callen–Welton 1951
             (DOI 10.1103/PhysRev.83.34); Giustino 2017 (DOI 10.1103/RevModPhys.89.015003)
  Closure:   tight (a PSD G-invariant representative provably exists) / loose (learned coefficients not pinned)

Assumption [PSD-ph-ph] — phonon-phonon scattering kernel M_{ph-ph}
  Origin:    GENERIC axiom + Onsager/detailed-balance + FDT
  Reference: Öttinger 2005 §5.3; De Groot & Mazur Ch. IV (ISBN 978-0-486-64741-8);
             Maradudin & Fein 1962 (DOI 10.1103/PhysRev.128.2589)
  Closure:   tight / loose

Assumption [PSD-rad]    — radiative damping kernel M_{rad}
  Origin:    GENERIC axiom + Lindblad/GKSL completely-positive structure (rate Γ ≥ 0); FDT root
  Reference: Öttinger 2005 §5.3; Breuer & Petruccione 2002 Ch. 3 (ISBN 978-0-19-852063-4);
             Jackson 1998 §17.2
  Closure:   tight / loose (trivial sign check when the invariant basis has dimension 1)
```

The closure is **tight at the operator level** — a PSD `G`-invariant
representative provably exists (the Reynolds image of a PSD seed is PSD),
so the positivity obligation (§19.7) never runs a semidefinite-feasibility
search for these channels; feasibility is a theorem, recorded as the
assumption above. The closure is **loose at the coefficient level** — the
PINO learns the basis coefficients and could transiently leave the PSD
cone during training — so the positivity obligation **keeps** a cheap
per-evaluation guard `λ_min(M_block) ≥ −δ_PSD` on the assembled per-mechanism
super-block (`arch-12 §12.0.1` obligation 2; tolerances valued in `arch-12 §12.0.2`).

**Dormant SDP fallback (V2).** A future `PSDSymmForm` channel with no
structural PSD guarantee would, at registration, solve the semidefinite
feasibility program "find `c` with `Σ c_i B_i ⪰ 0`" (interior-point,
`O(dim^{3.5})`, microseconds-to-milliseconds at registration only;
block-diagonalizable along the irrep decomposition per Gatermann–Parrilo
2004, DOI 10.1016/j.jpaa.2003.12.011); infeasibility rejects the channel.
No MVP channel needs it; it is specified for forward-compatibility only.

---

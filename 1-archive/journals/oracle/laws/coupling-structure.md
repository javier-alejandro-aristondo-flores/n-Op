---
id: coupling-structure
title: "Coupling structure"
owns:
  - coupling target shapes
  - CouplingChannel record
  - invariant-generator routine
  - polynomial-sufficiency flag
  - CoverageBound record
  - coupling coverage policy
  - CouplingSpec record
  - KernelExt extension family
  - TheoryContext placement
  - coefficient-provenance contract
  - PSD closure assumptions
anchors:
  target-shapes: "The object and its three target shapes"
  channel-record: "The parameter axes"
  invariant-generator: "The invariant generator"
  generator-contract: "The generator contract"
  generator-cost: "Emptiness and cost"
  worked-example: "Worked example — diamond electron-phonon"
  form-vs-values: "Symmetry generates the form; provenance supplies the values"
  composition: "Composition"
  cert-hooks: "Cert hooks"
  registration: "Registration discipline"
  provenance-contract: "The coefficient-provenance contract"
  slope-kind-guard: "The slope-kind double-count guard"
  polarization-pairing-guard: "The polarization-reference pairing guard"
  couplingspec: "The CouplingSpec record"
  theory-context-placement: "TheoryContext placement"
  mvp-theory-context: "The MVP default theory context"
  coverage-policy: "Coverage policy"
  mechanism-range-table: "Mechanism range and polynomial sufficiency"
  kernel-ext: "Extension types"
  psd-closure: "PSD closure for friction channels"
depends-on:
  - accuracy-ledger
  - unified-state
  - generic-dynamics
  - physics-graph
  - compose-time-pipeline
  - canonical-vocabularies
  - cert-obligations
  - applicability-classifiers
  - representation-substrate
  - named-formulas
  - residual-machinery
  - crystal-inputs
  - traps
open-questions:
  - id: sub-dof-pair-table
    anchor: channel-record
    summary: "Which (StateComponent, SubDofTag) pairs are legal is stated nowhere, and make-coupling-channel cannot validate a StatePiece without that table."
---
# Coupling structure

Cross-regime physics — electron-phonon, spin-orbit, magneto-elastic, minimal
coupling, phonon-phonon scattering, radiative damping — is one kind of object
with a small parameter space, not a hand-rolled list of named terms.

## The object and its three target shapes

A **coupling** is a symmetry-respecting function from a tensor product of pieces
of the state vector ([unified-state#slots]) into one of three target shapes:

- **`Scalar`** — a real-valued function; lands in `E_coupling`
  ([generic-dynamics#functionals]).
- **`AntisymmForm`** — an antisymmetric 2-form on the tangent bundle; lands as
  an off-diagonal block of `L` ([generic-dynamics#operators]).
- **`PSDSymmForm`** — a positive-semidefinite symmetric 2-form on the cotangent
  bundle; lands as an off-diagonal kernel of `M`
  ([generic-dynamics#operators]).

Every cross-regime term in [generic-dynamics] is one instance of this object.

## The parameter axes

```
record CouplingChannel {
  pieces        : List<StatePiece>            -- ordered tensor factors
  target        : Scalar | AntisymmForm | PSDSymmForm
  order         : Nat                         -- # tensor factors (typically 2..4)
  derivative    : Ultralocal | Gradient(Nat)  -- spatial-derivative depth
  applicability : (Crystal, Environment) → Bool
  -- coverage-policy fields:
  mechanism_range  : MechanismRange               -- curated; source of truth for the next flag
  kernel_extension : Optional<KernelExt>          -- the non-polynomial part;
                                                  --   present iff ¬polynomial_sufficient
  gauge_rule       : Optional<GaugeRule>          -- basis/gauge fixing; usually None
  provenance       : Optional<ProvenanceLedger>   -- where the coefficients came from
}

record StatePiece {
  component : StateComponent                  -- one of γ̂, A, R, P, h, Π_h, Z
  sub-dof   : SubDofTag                       -- orbital | spin | sublattice | valley
                                              -- | strain | gauge | charge | none
}
```

`StateComponent` is the seven-slot alphabet ([unified-state#slots]). `SubDofTag`
enumerates the internal labels a component carries: γ̂ carries `orbital`, `spin`
and — where applicable — `sublattice` and `valley`; `h` carries `strain`; `A`
carries `gauge`. **Which `(component, sub-dof)` pairs are legal is not stated
anywhere in this corpus**, and `make-coupling-channel` cannot validate a
`StatePiece` without that table. `Crystal` and `Environment` are
[crystal-inputs#crystal-type].

`order` and `derivative` declare the truncation. They are not part of the
underlying physical structure; they are the compose-time choice of how high in
the multipole / multi-tensor expansion to go.

The last four fields carry the coverage policy. `mechanism_range` records
whether the channel's mediating interaction is short-range or long-range; from
it the derived flag `polynomial_sufficient` decides whether the
symmetry-generated polynomial basis is the *whole* coupling or only its
short-range part. When it is only a part, `kernel_extension` carries the
non-polynomial remainder. `gauge_rule` fixes a residual basis ambiguity for the
rare channels that have one. `provenance` records where the numeric coefficients
came from and is the ordinary annotation every channel may carry. All four are
validated by `make-coupling-channel`.

## The invariant generator

```
generate-invariants : CrystalSymmetryGroup × CouplingChannel
                    → GeneratorOutput
```

Standard representation theory. Given the crystal's symmetry group
([canonical-vocabularies#scope] lifts `CrystalSymmetryGroup` to a first-class
typeclass entity, built at compose time from `PeriodicityStructure ×
SiteDecoration`) and a channel specification, this routine returns the finite
basis of `target`-shaped symmetry-invariant terms at the requested `order` and
`derivative`.

Each `InvariantTerm` is a symbolic tensor expression carrying:

```
record InvariantTerm {
  channel            : CouplingChannel
  irrep-coefficients : IrrepCoefficientTable   -- trivial-irrep coefficients of the
                                               --   underlying tensor product
  symbolic-form      : SymbolicTensor          -- the explicit term; the root of a
                                               --   MerkleDAG[SymbolicTensorOps, TypedLeaf]
                                               --   per representation-substrate
  generator-hash     : Address[InvariantTerm]  -- domain-separated content address
}
```

The generator returns a `GeneratorOutput`, not a bare list, because a channel's
full coupling may be the polynomial basis *plus* a non-polynomial kernel:

```
record GeneratorOutput {
  polynomial_invariants : List<InvariantTerm>       -- the symmetry-generated basis
  polynomial_sufficient : Bool                      -- echoed certificate (derived)
  kernel_extension      : Optional<KernelExt>       -- the non-polynomial remainder
  gauge_rule            : Optional<GaugeRule>       -- a basis-fixing rule, if any
  output_hash           : Address[GeneratorOutput]  -- domain-separated; folds in all four
}
```

`polynomial_sufficient` is echoed into the output so that a downstream stage
holding only `polynomial_invariants` can never silently treat a partial
short-range basis as the complete coupling.

The generator is the **constructive** direction of the irrep machinery that the
compose-time pipeline already uses **decompositionally** to block-diagonalize
operators by irrep ([compose-time-pipeline#symmetry-quotient]). Same module, same
primitives, new direction.

## The generator contract

The routine runs three integrity guards, a free O(1) spinor-parity pre-prune,
then the projector:

```
generate-invariants(G, c) :
  -- (0) well-formedness: the flag and the kernel must agree
  if ¬polynomial_sufficient(c) ∧ c.kernel_extension = None: error "partial coverage, no kernel"
  if  polynomial_sufficient(c) ∧ c.kernel_extension ≠ None: error "sufficient channel carries a kernel"
  if ¬polynomial_sufficient(c) ∧ ¬kernel_tag_matches_range(c): error "kernel tag ≠ mechanism_range"
  -- (1) spinor-parity pre-prune: an odd total spinor count cannot form a Scalar /
  --     PSDSymmForm / AntisymmForm invariant, so the basis is empty before any
  --     character is computed
  if odd_spinor_count(c.pieces) ∧ c.target ∈ {Scalar, PSDSymmForm, AntisymmForm}: poly = []
  else: poly = trivial_irrep_projector(G, c.pieces, c.target, c.order, c.derivative)
  -- (2) return both parts; the kernel rides through untouched by the symmetry projector
  return GeneratorOutput{ poly, polynomial_sufficient(c), c.kernel_extension, c.gauge_rule, … }
```

## Emptiness and cost

Emptiness of `poly` is decided by the character inner product
`⟨χ_T, χ_trivial⟩_G = (1/|G|) Σ_g χ_T(g)` — a single trace per group element,
never forming `ρ(g)` explicitly.

For the MVP worst case (`|G| ≤ 192` with the double cover and time reversal,
`dim(T) ≤ ~250` at `order = 4, Gradient(1)`): the character pre-prune is
`O(|G|) ≤ ~200` operations; the full Reynolds projection `P = (1/|G|) Σ_g
ρ(g)`, run only when the basis is non-empty, is `O(|G|·dim(T)²) ≤ ~12M`
operations. The result is cached on `Address[CrystalSymmetryGroup] ×
Address[CouplingChannel]` ([representation-substrate#serialization]), so
per-composition cost is one-shot. The cache key does **not** include the theory
context: the polynomial basis is symmetry-determined and theory-independent.

> **Emptiness is not correctness.** A non-empty `poly` is correct as far as it
> goes, but may still be only the short-range part of a long-range coupling.
> Whether `poly` is the *whole* coupling is the separate `polynomial_sufficient`
> question, not the emptiness question.

## Worked example — diamond electron-phonon

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

At compose time ([compose-time-pipeline#always-cheap]):

1. **Symbolic lift** records the channel in the stage sidecar.
2. **Symmetry quotient** has already constructed the diamond symmetry group
   (Fd-3m + time reversal).
3. **Invariant synthesis** ([compose-time-pipeline#invariant-synthesis]) runs
   `generate-invariants(Fd-3m+TR, electron-phonon)` and returns one
   `InvariantTerm`: the canonical `g_{nm,ν}(k,q)` matrix element written as a
   symmetry-respecting tensor.
4. **Algebraic simplification and lowering** turn that `InvariantTerm` into a
   `FormulaApply` node ([physics-graph#node-kinds]) attached to the
   `E_coupling` aggregator.

Spin-orbit, magneto-elastic, minimal coupling (γ̂ ↔ A), Stark, Zeeman,
phonon-phonon and radiative damping are each a `CouplingChannel` record with a
different parameter assignment. None of those strings appears as a value in any
enum.

## Symmetry generates the form; provenance supplies the values

The symmetry group generates the admissible **form** of `g_{nm,ν}(k,q)` — which
invariants exist and their index structure. The **numerical values** —
deformation potentials, Fröhlich and anharmonic parameters — are supplied by the
channel's `ProvenanceLedger`, from density-functional perturbation theory,
finite differences or fits, outside the generative structure.

Symmetry generates the form; provenance supplies the values. Everything in the
provenance contract below rests on that separation.

## Composition

- **Within a single `target`.** Invariants compose by direct sum:
  `E_coupling = Σ_c Σ_{v ∈ invariants[c] | v.target = Scalar} v.symbolic-form`,
  and analogously for the two form-valued targets.
- **Across `target` shapes.** Composition is the `E` / `L` / `M` assembly of
  [generic-dynamics#operators].
- **Order truncation is monotone.** Order `n+1` includes order `n` as a prefix;
  the spec author chooses the cutoff per channel.
- **No channel-correlation primitive in V1.** If two physical mechanisms
  genuinely correlate — a cross-term in `M` between two scattering processes
  that are not independent — they are modeled as *one* `CouplingChannel` with a
  larger tensor product, not two channels plus a correlation parameter. This
  keeps the V1 algebra additive.
- **Kernel extensions add as one more summand.** When a channel carries a
  `kernel_extension`, its lowered kernel node adds into the same aggregator as
  its polynomial invariants: `full_coupling = Σ poly_invariants +
  kernel_extension(q, ω)`. No new aggregator and no new composition primitive.
  A long-range mechanism is therefore split into **two channels** — a
  short-range polynomial one and a long-range kernel one — rather than one
  channel that is partly polynomial and partly not. Electron-phonon coupling
  splits into a deformation-potential channel and a Fröhlich channel: the
  standard Verdi–Giustino short-range / long-range split.

## Cert hooks

The invariant-generator structure simplifies three cert obligations, which
[cert-obligations#coupling-derived-checks] collapses to projection-residual
checks.

- **Symmetry equivariance.** Polynomial invariants are trivial-irrep basis
  vectors *by construction*, so equivariance is automatic and cert reduces to a
  numerical projection-residual check
  `‖v.symbolic-form − π_trivial v.symbolic-form‖ < δ_sym` on a sampled
  evaluation. A failure indicates a generator bug, not a physics bug. A
  `kernel_extension` is **not** exempt: it is scalar under the little group of
  `q` (`KernelExt.symmetry_law`), so cert checks
  `‖K(Rq,ω) − D(R) K(q,ω) D(R)†‖ < δ_sym` over little-group elements `R` — a
  checkable equivariance, just not a polynomial one.
- **Positivity — antisymmetry of `L`, positive-semidefiniteness of `M`.** The
  `target` tag determines a projection rule applied at the generator step:
  `AntisymmForm` invariants are projected onto the antisymmetric component of
  the candidate tensor, `PSDSymmForm` invariants onto the positive-semidefinite
  cone. The projection is part of the generator's contract; cert verifies
  numerically that the projected output matches the emitted `symbolic-form`
  within `δ_sym`. For `PSDSymmForm` channels, existence is a structural theorem
  rather than a runtime search, and the runtime guard is checked on the
  **assembled dissipative super-block per mechanism** — diagonal and
  off-diagonal kernels together — not per off-diagonal kernel.

The polynomial checks are O(1) per invariant, and both integrate with the
symmetry-adapted Hamiltonian machinery ([canonical-vocabularies]) that already
exists. The cert-obligation indices are fixed in
[cert-obligations#the-ten-obligations]: equivariance is obligation 1,
antisymmetry of `L` is obligation 5 (conservation), positive-semidefiniteness
of `M` is obligation 2 (positivity).

## Registration discipline

Channels register through the same factory pattern as residual generators
([residual-machinery#factory-entry]):

```
make-coupling-channel(channel : CouplingChannel) → CouplingChannel
```

It returns the channel with its `applicability` validated as first-order
decidable on typeclass tags — the registration-time invariant of
[named-formulas#applicability-decidability]. The channel's identity is
`Address[CouplingChannel]` under the canonical-serialization rule of
[representation-substrate#serialization]: domain-separated and
schema-versioned, so identical channels collapse to one address.

## The coefficient-provenance contract

Symmetry generates the *form* of a channel's invariants; the *values* —
deformation potentials, Fröhlich and anharmonic parameters, compact-model
coefficients — enter through the channel's `ProvenanceLedger`. Each provenanced
coefficient carries:

```
(value, standard-deviation, provenance, cost-class)
```

where `cost-class ∈ {curated, per-material-DFPT, fit}` declares its acquisition
pipeline, `provenance` is the citation it rests on, and the standard deviation
reuses the reference-battery machinery ([cert-obligations#reference-cache]).

**A cert obligation refuses any composition whose active channels carry
coefficients without a `ProvenanceLedger` entry** — an unprovenanced coefficient
is a silent accuracy hole. For the MVP the diamond coefficients are `curated`;
other materials are `per-material-DFPT`, and their provenance is the gating
data-acquisition task before that material is claimed.

A coefficient whose `provenance` is a learned correction is additionally bound
by the rule that it is fit only against external anchors and frozen with respect
to the training loss ([traps#frozen-corrections]), and by the refusal that rule
rests on ([cert-obligations#composition-refusals]).

## The slope-kind double-count guard

Any temperature-slope coefficient feeding `ahc-gap-renormalization` (registry
row 120) additionally carries `slope-kind ∈ {isochoric, total}`.

Quoted experimental `dE_g/dT` slopes are mostly *total*: they already fold in
the lattice-expansion part that registry row 63
(`deformation-potential-gap-shift`) carries separately, which is 30–40% of the
shift. **A cert obligation refuses any composition in which a `total`-tagged
Allen–Heine–Cardona slope and row 63's thermal-expansion path are both
active on the same observable**; an `isochoric`-tagged slope composes with row
63 freely. The tag is a first-class field on the coefficient, so the check is a
tag comparison at compose time, not a reviewer's caveat.

The curated zero-point-renormalization amplitudes feeding the `coth` path
([accuracy-ledger#ahc-zpr]) are the **isochoric** electron-phonon values, tagged
`isochoric`: GaN −189 meV and AlN −399 meV (Engel PRB 106 094316 (2022); Miglio
npj Comput. Mater. 6 167 (2020)), diamond −345 meV indirect (Antonius PRL 112
215501 (2014)). The zero-point lattice-expansion part — GaN −49 meV, AlN −85 meV
(Miglio 2020) — is registry row 63's job. Seeding a `total` magnitude into the
electron-phonon `coth` path while row 63 is active is exactly the double count
this guard refuses.

## The polarization-reference pairing guard

Spontaneous polarization is reference-dependent. The two-dimensional
electron-gas sheet density `n_s` (registry row 115) consumes an interface
*difference* `ΔP` whose accuracy target for AlGaN/GaN rests on an **accidental
cancellation** (Dreyer et al., PRX 6 021038 (2016)) between the spurious
zinc-blende-reference term in `P_sp` and the proper-versus-improper `e₃₁` error
— two large, opposite-sign quantities. It is not a generic reference
cancellation.

The cancellation holds only under a **self-consistent pairing**: either
zinc-blende-reference `P_sp` with **proper** `e₃₁` and no zinc-blende
correction, which is this library's path; or layered-hexagonal-reference `P_sp`
with `ΔP_corr` and **improper** `e₃₁`. Because improper `e₃₁ ≈ 3.4×` proper for
GaN and AlN, mixing conventions silently corrupts `n_s`.

Each polarization coefficient — `P_sp` (registry row 113), `e₃₁` (registry rows
114 and 117) — therefore carries `polarization-reference ∈ {ZB-proper,
H-improper}`, and **a cert obligation refuses any composition whose active
`P_sp` and `e₃₁` carry mismatched tags**
([cert-obligations#composition-refusals]). The `ΔP` accuracy target also
carries an `is-AlGaN-GaN` validity scope: the cancellation fails for
high-indium InGaN/GaN, where the target is degraded and the composition
cert-refused. The curated III-nitride coefficients
([accuracy-ledger#polarization-coefficients]) are all `ZB-proper`.

## The CouplingSpec record

The active channels in a composition, **together with the theory frame they are
interpreted in**, are the `CouplingSpec`:

```
record CouplingSpec {
  channels       : SparseSet[CouplingRegistry]   -- the active channels
  theory_context : TheoryContext                 -- the global theory frame
}
```

Its `Address` is computed by the record rule of
[representation-substrate#serialization], so two specs with identical channel
sets but different `theory_context` are guaranteed distinct addresses: the
theory frame is part of identity, automatically. `CouplingSpec` carries its own
schema version, so its addresses cannot collide with those of any other
encoding of the same channel set. The spec travels alongside the composition
request ([compose-time-pipeline#symbolic-lift]).

The diamond MVP's `CouplingSpec` is short: electron-phonon (short-range) +
minimal coupling + ion-ion electrostatic + phonon-phonon scattering in `M`,
under the MVP default theory context.

## TheoryContext placement

`theory_context` is **definitional input**. It is set at the symbolic-lift
stage, and it must exist before the symmetry quotient builds the — possibly
double-cover — symmetry group,
because the relativistic treatment determines whether the group carries the spin
SU(2) factor.

A `make-theory-context(raw) → TheoryContext` smart constructor, mirroring
`make-coupling-channel`, **must** normalize and validate before any
`Address[TheoryContext]` is taken. This is load-bearing for content addressing,
not optional: it normalizes the hybrid-functional double representation — a
hybrid is always `XCFunctionalTag.Hybrid` with `ManyBodyLevel.KohnSham`, never
`HybridAsManyBody` — and enforces pseudopotential/run relativistic consistency,
so two byte-distinct encodings of the same physics can never produce two
addresses.

```
record TheoryContext {
  xc_functional          : XCFunctionalTag                         -- closed vocabulary
  pseudopotential_set    : PersistentMap<AtomicSpecies, PPRecord>  -- closed discriminators;
                                                                   --   open file id, content-pinned
  many_body_level        : ManyBodyLevel                           -- closed; sub-records for +U / GW / DMFT
  relativistic_treatment : RelativisticTreatment                   -- closed
}
```

The ten closed vocabularies backing these four fields are
[canonical-vocabularies#theory-context]. The theory context does **not** enter the
`generate-invariants` cache key: the polynomial basis is symmetry-only, and the
relativistic treatment's one effect — spin-orbit — enters through the symmetry
group's double cover, captured by `Address[CrystalSymmetryGroup]`. It does
**not** enter the runtime kernel either: by the lowering stage
([compose-time-pipeline#lowering-and-adjoint-synthesis]) the theory choice
has already selected the symmetry group and conditioned the coefficient values,
so the lowered kernel is theory-agnostic. `theory_context` is therefore solely
metadata for the cert and provenance layer.

## The MVP default theory context

`GGA(PBE)` / PseudoDojo v0.4.1 norm-conserving, with Ga's `3d` semicore shell
promoted to valence / `KohnSham` plain density-functional theory /
`ScalarRelativistic`, no explicit spin-orbit coupling, the MVP set being
non-magnetic with no spin-orbit-dependent observable.

PBE's underestimate of ultra-wide-bandgap band gaps is handled by
theory-conditioning the reference-battery obligation
([cert-obligations#the-ten-obligations]), not by upgrading the default.
`Hybrid(HSE06)` is the documented accuracy upgrade for gap-sensitive work.

## Coverage policy

The coupling-channel template set is **not** an enumerated list of coupling
terms. A channel is a tuple in the parameter space
`(pieces, target, order, derivative, mechanism_range, applicability)`; the
registry is a **coverage policy** — a bounded subset of that space — plus the
runtime rule:

> the active channels for crystal `C` are those whose `applicability` holds and
> whose invariant basis is non-empty under the crystal's symmetry group `G_C`.

The invariant generator is the filter that culls structurally empty tuples. The
spec author never enumerates terms; they declare bounds wide enough that
generator plus applicability prune to the right active set automatically. The
bound is the `CoverageBound`:

```
record CoverageBound {
  global_cap         : (max_order : Nat, max_derivative : Derivative)
  per_mechanism_caps : PersistentMap<MechanismClass, (Nat, Derivative)>
}
```

The MVP global cap is `(max_order = 4, max_derivative = Gradient(1))`. The
single driver of `order = 4` is lattice anharmonicity — four-phonon scattering,
significant for diamond and GaN above room temperature. Every other mechanism
class fits inside `(2, Gradient(1))`, with a few reaching `order = 3`. The
per-mechanism inner table prunes tuples *before* the character test, so the
generator never spends cycles on orders physics never visits for that mechanism.
Both are coverage-policy parameters, not physical claims.

Adding a new physical regime is a channel declaration under this policy, not a
code edit.

The **piezoelectric-acoustic** channel is `LongRangeStatic(1)` with a `1/q`
pole: the second long-range electron-phonon mechanism the wurtzite III-nitride
members carry, alongside Fröhlich's `1/q²`. It is gated on
`is-noncentrosymmetric` ([applicability-classifiers#polar-predicate-split]) —
piezoelectric scattering needs a piezoelectric class — and is inert for
diamond.

## Mechanism range and polynomial sufficiency

Some couplings are not polynomials of any finite degree in the state variables.
They are functions of the wavevector `q` and/or the frequency `ω` with an
*essential* non-polynomial structure: a pole at `q = 0` — the Fröhlich `1/|q|²`
polar-optical coupling — or poles in `ω`, as in dynamical screening (the
screened Coulomb interaction `W(q,ω)`, the GW self-energy `Σ(k,ω)`, the
time-dependent-density-functional-theory kernel `f_xc(q,ω)`). For these, the
generator's polynomial basis is correct but **incomplete**: it captures the
short-range part and misses the long-range or dynamical part.

Completeness is **not** decidable from `(pieces, target, order, derivative)` and
the symmetry group alone — the short-range deformation-potential
electron-phonon channel and the long-range Fröhlich electron-phonon channel have
*identical* signatures. Long-range-ness is a property of the physical mechanism,
so it is carried explicitly:

```
record MechanismRange =
  | ShortRange                          -- analytic / exponentially-localized mediator
  | LongRangeStatic(pole_order : Nat)   -- 1/|q|^p, ω-independent
                                        --   (Fröhlich p = 2, van der Waals, bare-Coulomb head)
  | LongRangeDynamical                  -- frequency-dependent screening: poles in ω
```

`mechanism_range` is curated once per template. `polynomial_sufficient` is then
a total, O(1) **derived projection**:

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

`mechanism_range` says *"this mechanism is long-range when active"*;
`applicability` independently says *"this mechanism is active for this
crystal."* They are orthogonal: a Fröhlich channel is long-range by mechanism
yet inert in a non-polar crystal such as diamond, with zero Born charges, by
applicability.

The coverage-policy template table — the 15 principled channels, all
short-range and polynomial-sufficient except where noted:

| Channel template | `mechanism_range` | `polynomial_sufficient` |
|---|---|---|
| electron-phonon (deformation-potential, short-range) | `ShortRange` | true |
| electron-phonon (Fröhlich polar-optical, long-range) | `LongRangeStatic(2)` | **false** |
| electron-phonon (piezoelectric acoustic, long-range) | `LongRangeStatic(1)` | **false** |
| spin-orbit | `ShortRange` | true |
| magneto-elastic | `ShortRange` | true |
| minimal coupling / light-matter | `ShortRange` | true |
| phonon-phonon (anharmonic) | `ShortRange` | true |
| radiative damping | `ShortRange` | true |
| exchange / Heisenberg | `ShortRange` | true |
| Zeeman | `ShortRange` | true |
| Stark / electric-dipole | `ShortRange` | true |
| strain-electronic (Bir–Pikus) | `ShortRange` | true |
| screened Coulomb / RPA `W(q,ω)` | `LongRangeDynamical` | **false** |
| GW self-energy `Σ(k,ω)` | `LongRangeDynamical` | **false** |
| TDDFT `f_xc(q,ω)` | `LongRangeDynamical` | **false** |

The frequency-dependent screening channels are not in the diamond MVP
`CouplingSpec`; they are the forcing function for the schema. The adiabatic
local-density kernel is the degenerate corner of `LongRangeDynamical`, a
constant kernel — so **tag a channel by its general mechanism, not by the
cheapest approximation of it**, and swapping that kernel for a tabulated one
needs no retag.

## Extension types

**`KernelExt`** carries the non-polynomial part of a long-range coupling. All
four variants share one backbone — a section of a `BZ × ℝ_ω` fiber bundle valued
in a bounded-rank tensor — and differ only in tensor rank, real-versus-complex
value, and whether they are given parametrically or as a tabulated grid. No new
substrate primitive is needed; every field maps onto the primitives of
[representation-substrate#primitives].

```
record KernelExt {
  tag            : FroehlichLongRange | ScreenedCoulombRPA
                 | GWQuasiparticleSelfEnergy | TDDFTXCKernel
  domain         : MomentumOnly | MomentumFrequency | KpointFrequency | RealSpaceRadial
  value_rank     : Rank0 | Rank2_GG | Rank2_bands | Rank2_cart
  value_field    : RealField | ComplexField
  symmetry_law   : QSymmetryLaw      -- "K is scalar under the little group of q"
  representation : Parametric(KernelParams) | Tabulated(KernelGrid)
                 | Hybrid(KernelParams, KernelGrid)
  provenance     : Optional<ProvenanceLedger>
}
```

`Parametric` kernels — Fröhlich's `ε_∞`, `ε_static`, Born charges `Z*`, `ω_LO`;
the long-range-corrected `f_xc`'s single `α` — are tiny, under 1 KB.
`Tabulated` kernels can be large: the full-frequency dense dielectric matrix
for diamond, at a `12³` q-mesh × 64 frequencies × 500 G-vectors, complex, is ≈
**440 GB** worst case, dropping to ≈ 0.5 GB after a plasmon-pole model and
irreducible-Brillouin-zone reduction. The grid is a cache-eligible sidecar
attached by `Address[TabulatedField]` ([representation-substrate#clusters]) —
folded into the channel's identity by address, never by value, so content
addressing stays O(1). **No MVP channel is tabulated**: the active set is
all-polynomial, and Fröhlich for the polar members is `Parametric`. Tabulated
storage is a V2 concern, and 440 GB is the number the persistent-storage tier
must be designed against before those channels turn on.

**`GaugeRule`** resolves a residual continuous basis ambiguity — for instance
the Wannier-gauge or orbital-projection choice for a downfolded channel. It is
`None` for every MVP channel, and is recorded only where a gauge-fixing rule is
genuinely attached.

## PSD closure for friction channels

A `PSDSymmForm` channel lands as an off-diagonal block of the GENERIC friction
operator `M`, which must be positive-semidefinite so that entropy production
stays non-negative. The invariant generator returns a basis of `G`-invariant
*symmetric* tensors, but membership in that linear subspace does not by itself
guarantee that any combination is positive-semidefinite: a linear condition
against a convex-cone condition.

For the MVP friction channels — electron-phonon and phonon-phonon dissipation —
plus the near-term radiative-damping channel, positive-semidefiniteness is
**structurally guaranteed by physics**. It is a documented assumption, not a
runtime search:

```
Assumption [PSD-e-ph]   — electron-phonon dissipation kernel M_{e-ph}
  Origin:    GENERIC M-block axiom + fluctuation-dissipation theorem
             + Fermi-golden-rule Gram structure (sum of squared coupling matrix elements)
  Reference: Öttinger 2005 section 5.3 (DOI 10.1002/0471727903); Callen–Welton 1951
             (DOI 10.1103/PhysRev.83.34); Giustino 2017 (DOI 10.1103/RevModPhys.89.015003)
  Closure:   tight at the operator level / loose at the coefficient level

Assumption [PSD-ph-ph] — phonon-phonon scattering kernel M_{ph-ph}
  Origin:    GENERIC axiom + Onsager/detailed-balance + fluctuation-dissipation
  Reference: Öttinger 2005 section 5.3; De Groot & Mazur Ch. IV (ISBN 978-0-486-64741-8);
             Maradudin & Fein 1962 (DOI 10.1103/PhysRev.128.2589)
  Closure:   tight / loose

Assumption [PSD-rad]    — radiative damping kernel M_{rad}
  Origin:    GENERIC axiom + Lindblad/GKSL completely-positive structure (rate Γ ≥ 0);
             fluctuation-dissipation root
  Reference: Öttinger 2005 section 5.3; Breuer & Petruccione 2002 Ch. 3
             (ISBN 978-0-19-852063-4); Jackson 1998 section 17.2
  Closure:   tight / loose (a trivial sign check when the invariant basis has dimension 1)
```

The closure is **tight at the operator level**: a positive-semidefinite
`G`-invariant representative provably exists, because the Reynolds image of a
positive-semidefinite seed is positive-semidefinite. The positivity obligation
therefore never runs a semidefinite-feasibility search for these channels —
feasibility is a theorem, recorded as the assumption above.

The closure is **loose at the coefficient level**: the operator learns the basis
coefficients and could transiently leave the cone during training. So the
positivity obligation keeps a cheap per-evaluation guard
`λ_min(M_block) ≥ −δ_PSD` on the assembled per-mechanism super-block
([cert-obligations#tolerance-ledger]).

**Dormant semidefinite-program fallback (V2).** A future `PSDSymmForm` channel
with no structural guarantee would, at registration, solve the semidefinite
feasibility program *"find `c` with `Σ c_i B_i ⪰ 0`"* — interior point,
`O(dim^{3.5})`, microseconds to milliseconds and at registration only,
block-diagonalizable along the irrep decomposition per Gatermann–Parrilo 2004
(DOI 10.1016/j.jpaa.2003.12.011). Infeasibility rejects the channel. No MVP
channel needs it; it is specified for forward compatibility.

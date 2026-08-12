---
id: traps
title: "Standing traps"
owns:
  - known-wrong values in the literature
  - convention-pairing hazards
  - verifier-soundness hazards
  - checker-soundness hazards
  - repair-pass discipline
anchors:
  what-a-trap-is: "What a trap is"
  addressing: "How a trap is cited"
  sign-conventions: "Sign conventions"
  bowing-sign: "Bowing coefficient sign"
  pyroelectric-sign: "Pyroelectric coefficient sign"
  breakdown-slope-sign: "Breakdown-field temperature slope"
  misfit-strain-sign: "Misfit strain sign"
  shear-piezo-sign: "Shear piezoelectric sign"
  entropy-direction: "Entropy-production direction"
  units: "Units, dimensions, and uncertainty encodings"
  displacement-cross-section: "Frenkel-pair yield needs a macroscopic cross-section"
  uncertainty-encodings: "Three uncertainty encodings, and one that is unassigned"
  thermal-expansion-form: "Thermal-expansion tensor form"
  vertex-normalization: "Electron-phonon vertex normalization"
  gaussian-units: "Gaussian units and the Maxwell source term"
  frames: "Reference frames and pairing rules"
  polarization-pairing: "Polarization-convention pairing"
  accidental-cancellation: "The polarization error budget rests on a cancellation"
  zero-point-renormalization-tag: "Zero-point renormalization is the isochoric value"
  diamond-valley-quarantine: "Diamond's direct-gap renormalization stays quarantined"
  gallium-oxide-axes: "Gallium oxide carries four axis systems"
  lattice-transpose: "Lattice matrices are stored by row"
  polarized-averaging: "Never average a polarized quantity"
  electron-affinity-termination: "Diamond electron affinity is termination-dependent"
  refusal-boundaries: "Certification refusal boundaries"
  unprovenanced-coefficient: "An unprovenanced coefficient refuses the composition"
  breakdown-without-anchors: "No breakdown claim without that carrier's coefficients"
  high-temperature-breakdown: "Breakdown above 500 degrees Celsius is refused"
  gallium-oxide-holes: "Gallium oxide holes are refused, not seeded"
  aluminum-nitride-avalanche: "Measured avalanche in aluminum nitride is unseeded"
  verifier-soundness: "Verifier soundness"
  density-matrix-admissibility: "Density-matrix admissibility is scored, not presupposed"
  gauge-partition: "Gauge and electrostatic partition"
  two-polar-predicates: "Two independent polar predicates"
  dynamical-stability-gate: "Real phonon frequencies are gated to claimed-stable phases"
  metastability-band: "The hull residual is temperature- and pressure-aware"
  consistency-not-equivalence: "A model-versus-microscopic pair is a consistency pair"
  frozen-corrections: "A learned correction is frozen against the loss it modifies"
  face-flux-discretization: "Drift-diffusion face flux is Scharfetter-Gummel"
  positive-semidefinite-assembly: "Positive semidefiniteness is a condition on the assembly"
  swept-environment-windows: "Validity windows are re-evaluated per training sample"
  lifted-values: "Values that are wrong if lifted naively"
  conductivity-error-decoupling: "The thermal-conductivity errors do not cancel"
  boron-arsenide-collision: "A conductivity figure that names the wrong material"
  three-phonon-high-temperature: "Three-phonon transport overpredicts nitrides at high temperature"
  impact-ionization-spread: "Impact-ionization prefactors span four orders of magnitude"
  image-force-lowering: "Image-force lowering"
  peak-not-saturation-velocity: "Peak velocity is not saturation velocity"
  gallium-oxide-critical-field: "Gallium oxide's critical field is an anisotropic triple"
  quasiharmonic-validity: "Quasiharmonic validity is per-material"
  alloy-disorder-limiter: "Alloy disorder is the dominant mobility limiter"
  degenerate-doping-assumptions: "Degenerate doping breaks two non-degenerate assumptions"
  diamond-oxidation-ceiling: "Diamond's high-temperature failure mode is oxidation"
  worked-examples: "A worked example is not one artifact"
  practice: "Practice"
  clearance-is-not-evidence: "A prior audit's clearance is not evidence"
  seed-from-the-source: "Seed from the source, never from a page that quotes it"
  names-are-addresses: "A registry name is an address"
  rename-orphans-prose: "A rename orphans every prose mention"
  structural-index-genericity: "Structural index analysis is generic-values-only"
  relaxed-rows-in-a-flow: "A relaxed row is refused inside an evolver"
  trajectory-safety: "Differentiation safety is trajectory safety for an evolver"
  pin-provenance-first: "Pin provenance before the ledger entry"
  adjoint-gate-passes-on-zero: "A passing adjoint gate is not evidence of a gradient"
  conditioning-invisible: "A conditioning failure is invisible to the adjoint gate"
  fixpoint-claim: "Fixed-point adjoint is a structural claim, not a fallback"
  no-derivative-claim: "No-derivative is the strongest claim in the vocabulary"
  unnamed-relaxation: "A relaxed row that names no relaxation is ungateable"
  token-collides-with-physics: "A short token collides with real physics"
  missing-data-marker: "The missing-data marker and its collisions"
  checker-not-looking: "A checker that finds nothing may not be looking"
  calibration-holes: "A calibration with holes is a green you cannot cash"
  checker-inherits-its-premise: "A checker inherits the soundness of its premise"
  vocabulary-has-an-owner: "Harvest a vocabulary from the schema that owns the field"
  sum-preserving-errors: "Sum-preserving arithmetic errors survive every eyeball"
  quote-both-arms: "A number quoted without its complement"
  dangling-over-invented: "A dangling pointer is safer than a plausible reconstruction"
  predating-gaps: "Not every gap a repair exposes was caused by the thing repaired"
  tolerance-in-the-address: "Never put a tolerance in the address"
  target-is-not-measurement: "A declared error target is not a measured error"
  exact-only-is-untested: "Exact-only is not a conservative gate"
depends-on:
  - agent-contract
  - conventions
  - glossary
  - accuracy-ledger
  - reference-battery
  - cert-obligations
  - out-of-scope
  - applicability-classifiers
  - cert-obligations
  - residual-definitions
  - residual-machinery
  - unified-state
  - generic-dynamics
  - multiscale-state
  - coupling-structure
  - representation-substrate
  - compose-time-pipeline
  - named-formulas
  - observable-bundles
  - mvp-system
open-questions:
  - id: rename-forwarding-mechanism
    anchor: rename-orphans-prose
    summary: "A registry name that changes in the data file orphans every prose mention of the old one. The discipline is to fix names before they land; whether the corpus also keeps a forwarding mechanism, and what it would be, is undecided."
---
# Standing traps

## What a trap is

A **trap** is a failure mode that survives ordinary review, because the wrong version
looks exactly as plausible as the right one. Every entry below is a hazard that is live
now: a value that is wrong in the literature a reader will consult, a convention that
inverts a result when lifted across a boundary, a gate that passes on the case it exists
to catch.

**Read this before changing anything involving a sign, a unit, a reference frame, or a
validity boundary.**

Two statuses:

- **enforced** — the rule is stated on the page named, so a reader following the corpus
  cannot get it wrong.
- **advisory** — correct here, and guarded nowhere else.

An `enforced` pointer is a claim about another page's *text*, not about its existence.
The structure checker confirms that the page and anchor exist; that the rule is actually
stated there is confirmed by reading. A pointer that resolves to a real page which does
not carry the rule is a **dangling promise**, and it is worse than a broken link because
it passes — see *A checker that finds nothing may not be looking*, below.

## How a trap is cited

**Each trap is addressed by name.** The name is the anchor:

```
[traps#pyroelectric-sign]
[traps#seed-from-the-source]
```

There are no trap numbers. A numbered register renumbers whenever an entry is inserted
or dropped, and every citation into it silently repoints — which is why the previous
register needed a dedicated check for contiguous numbering and for citations naming a
number that did not exist. A declared anchor cannot repoint: it either resolves or the
run fails ([agent-contract#citing]). The same argument the corpus applies to page ids —
descriptive phrases, never serials — applies to the addresses inside a page.

Adding a trap is adding a heading and an anchor. Nothing else moves.

## Sign conventions

### Bowing coefficient sign

The reference data writes aluminum-gallium-nitride spontaneous polarization bowing as
`+b·x(1−x)` with **b positive**. The primary literature defines the same physics as
`−b·x(1−x)` with **b negative** ("bowing always upward"). The two are equivalent through
the double negative. *Breaks:* lifting one convention's `b` into the other's form
inverts the bowing and corrupts interface charge at mid-to-high aluminum fraction. —
enforced, [accuracy-ledger#polarization-bowing]

### Pyroelectric coefficient sign

Seeded nitride spontaneous polarizations are negative in the zincblende-reference frame,
and their magnitude falls with rising temperature, so **`p = dP_sp/dT` is positive** in
the seeded frame. Raw literature quotes `p` negative under the positive-polarization
convention. *Breaks:* sheet-density drift over a harsh-environment temperature span — a
20 to 30 percent effect over ΔT ≈ 750 K, per the figure [accuracy-ledger] owns — runs
the wrong direction. — enforced, [accuracy-ledger#polarization-coefficients]

### Breakdown-field temperature slope

The slope is **positive**: breakdown field **rises** with temperature (diamond
+5×10⁻⁴/K, 4H silicon carbide +7×10⁻⁴/K). The widely repeated "drops about 20 percent"
claim conflates breakdown field with mobility collapse, and it is the version a reader
will meet first. *Breaks:* every high-temperature device claim predicts softening where
the material hardens. — enforced, [accuracy-ledger#observable-regimes]

### Misfit strain sign

Normalized corpus-wide to `ε_misfit = (a_film − a_sub)/a_sub`. *Breaks:*
Matthews-Blakeslee critical thickness, and every heterostructure strain sign. — advisory

### Shear piezoelectric sign

The `e₁₅` piezoelectric constant is literature-split (±) and is `UNSEEDED`, never
picked. *Breaks:* silently choosing a sign gives a wrong shear-piezoelectric response
with no provenance trail behind it. — enforced, [accuracy-ledger#residue]

### Entropy-production direction

The H-theorem gives `dS/dt ≥ 0`, so `−S[f]` is non-**increasing**. *Breaks:* the
monotonicity an entropy-monotone integrator or residual would enforce. — advisory

## Units, dimensions, and uncertainty encodings

### Frenkel-pair yield needs a macroscopic cross-section

The macroscopic displacement cross-section `Σ_d = N_atom·σ_d` (cm⁻¹) is required.
Without it the expression is a fluence (cm⁻²), not a concentration. *Breaks:* the
radiation channel is dimensionally invalid. — enforced, [multiscale-state#slow-kinetics]

### Three uncertainty encodings, and one that is unassigned

Absolute standard deviation, multiplicative `×N` (log-standard-deviation `ln N`), and
`unbounded`. A row whose uncertainty cell is unassigned **cannot** back a provenance
ledger coefficient. *Breaks:* consumers dispatch on the wrong uncertainty format, or a
certification run refuses exactly the compositions a seeding wave existed to enable. —
enforced, [reference-battery#row-schema]

### Thermal-expansion tensor form

Uses **compliance** `S = C⁻¹` and the `1/V` prefactor. *Breaks:* a dimensionally wrong
expansion tensor, propagating into gap-versus-temperature strain, shear modulus, and the
temperature-pressure hull. — advisory

### Electron-phonon vertex normalization

The `√(2Mω)` single-mass shorthand is valid for one species only; multi-species cells
need mass-weighted eigenvectors. *Breaks:* a per-species mass error in every
electron-phonon matrix element. — advisory

### Gaussian units and the Maxwell source term

The 4π in the source term rides the unit system. *Breaks:* factor-4π errors across the
electromagnetic sector. — advisory

## Reference frames and pairing rules

### Polarization-convention pairing

Use *exactly one* of (a) zincblende-reference spontaneous polarization + **proper**
`e₃₁` + no zincblende correction, or (b) layered-hexagonal spontaneous polarization +
the correction term + **improper** `e₃₁`. Never mix: improper `e₃₁` is about **3.4×**
proper for gallium nitride and aluminum nitride. *Breaks:* two-dimensional electron gas
sheet density silently corrupted about threefold in the piezoelectric term. — enforced,
[coupling-structure#polarization-pairing-guard]

### The polarization error budget rests on a cancellation

The ±5 percent polarization-difference target rests on an **accidental** cancellation,
not a generic one: the spurious zincblende-reference term and the proper/improper error
are large, opposite in sign, and nearly cancel **for aluminum-gallium-nitride on gallium
nitride only**. This is reinforced experimentally — off-axis holography shows
zincblende-frame theory bowing with the *opposite curvature sign* to measurement for
indium-gallium-nitride, so **bowing is not reference-invariant**. *Breaks:* extending
the ±5 percent figure to other alloy systems, or importing a bowing curvature across
reference frames. — enforced, [accuracy-ledger#observable-regimes]

### Zero-point renormalization is the isochoric value

The temperature-dependent gap renormalization is the isochoric value and carries a tag
saying so. The `coth` dressing is pure electron-phonon; lattice expansion belongs to the
thermal-expansion row, and a `total` tag co-activated with it is **refused**. The tag
rides the renormalization *amplitude*, not a total shift at temperature. *Breaks:* the
gap's temperature derivative double-counted, and intrinsic carrier concentration is
exponentially sensitive to the gap. — enforced, [coupling-structure#slope-kind-guard]

### Diamond's direct-gap renormalization stays quarantined

Diamond's direct-gap zero-point renormalization is a different valley from the indirect
gap and never substitutes for it. *Breaks:* about twofold overstated renormalization on
the load-bearing indirect gap. — enforced, [accuracy-ledger#ahc-zpr]

### Gallium oxide carries four axis systems

The crystal-physical frame is `e₂∥b`, `e₃∥c`, `e₁ = a*`, so the second and third
diagonal components are the `[010]` and `[001]` directions — but **plane-normal**
measurements lie along `a*` and `c*` and must never be relabeled `[100]` and `[001]`.
The high-field third axis is `c*`, about 13.8° off `[001]`. A fourth frame is live in
the reference data: the elastic tensors are seeded in `x∥a y∥b z∥c*`, whose first axis
is the *real* `a`, not `a*`; the two differ by 13.83°, so the `C₁₁` seeded there is not
along the crystal-physical `e₁`. Four frames, one material. Every value carries its
frame or it is not usable. *Breaks:* in a material about 2.5× anisotropic, values attach
to the wrong crystallographic direction. — enforced, [accuracy-ledger#monoclinic-frames]

### Lattice matrices are stored by row

Green-Lagrange strain is built from the deformation gradient, with `A_ref` the reference
lattice matrix, `A_def` the deformed one, `F` the deformation gradient and `I` the
identity:

```
M = A_ref⁻¹ A_def      F = Mᵀ      E_GL = ½ (FᵀF − I)
```

**Each row of a lattice matrix is a lattice vector**, so every transpose in that chain is
a chance to be wrong and stay plausible. Consider the slip that drops one — computing
`MᵀM` where the row convention calls for `MMᵀ`. The result is still a symmetric tensor of
the right magnitude, and it is quieter than that: `MᵀM` and `MMᵀ` are similar matrices
for any invertible `M`, so the two candidates have **identical principal strains, trace
and determinant**. Every invariant check on the strain — a volumetric strain, a
magnitude, a norm, a comparison against the applied deformation — passes exactly. Only
the principal *directions* move, and they surface only in the direction-resolved elastic
constants derived from the tensor.

The transpose-free form removes the hazard rather than warning about it. With the metric
tensor `G = A Aᵀ`, whose entries are the lattice-vector dot products:

```
E_GL = ½ (A_ref⁻¹ G_def A_ref⁻ᵀ − I)
```

No deformation gradient is ever formed, so no transpose is left to get wrong — which is
the construction-over-check preference applied to a formula ([conventions#verdicts]).
*Breaks:* a strain tensor silently corrupted by a storage convention, propagating into
every elastic constant derived from it. **This is a software defect, not a physics one.**
The equations above are correct; what is wrong sits between them and the array they are
evaluated over, so a reviewer checking the physics never reaches it. — advisory

### Never average a polarized quantity

Gallium oxide's absorption onset is polarization-dependent, spread over about 0.3 eV.
Seed the effective gap *and* the onsets as separate rows. *Breaks:* a single averaged gap
that matches no measurement, defeating direction-resolved certification. — advisory

### Diamond electron affinity is termination-dependent

Every use is termination-tagged. *Breaks:* Schottky-barrier and leakage paths silently
pick a surface that is not the device's. — advisory

## Certification refusal boundaries

### An unprovenanced coefficient refuses the composition

Any active channel without a provenance-ledger entry — value, uncertainty, source, cost
class — refuses. *Breaks:* a silent accuracy hole ships as a confident number. —
enforced, [cert-obligations#composition-refusals]

### No breakdown claim without that carrier's coefficients

No breakdown claim for a material without that material's provenanced ionization
coefficients **for that carrier**. A contested-but-provenanced value does not refuse; it
flags. *Breaks:* breakdown predicted for materials with no measured ionization
coefficient. — advisory

### Breakdown above 500 degrees Celsius is refused

Above 500 °C, breakdown is certification-refused and frontier — not a "±20 percent met"
target. The distribution-tail anchor data do not exist. *Breaks:* the project's headline
harsh-environment claim asserted where nothing anchors it. — enforced,
[accuracy-ledger#observable-regimes]

### Gallium oxide holes are refused, not seeded

Flat valence bands, small-polaron self-trapping, no band-like hole transport; the
about-3.5 eV ultraviolet luminescence is free-electron to self-trapped-hole
recombination, **not** band-edge. *Breaks:* seeding a hole mobility, ionization
coefficient or mobility-fit set for a material that has none. — enforced,
[out-of-scope#exclusions]

### Measured avalanche in aluminum nitride is unseeded

The available impact-ionization coefficient is Monte-Carlo and electron-only. The
*measured* value stays certification-refused. *Breaks:* a Monte-Carlo number presented
as measurement-grade. — enforced, [out-of-scope#exclusions]

## Verifier soundness

### Density-matrix admissibility is scored, not presupposed

`γ̂† = γ̂`, `0 ⪯ γ̂ ⪯ 1`, `Tr γ̂ = N_e`, and idempotency only where zero temperature is
claimed. *Breaks:* a candidate zeroes every equation-of-motion residual while being an
unphysical density matrix, and the oracle stops being sound as a verifier. — enforced,
[residual-definitions#structural-categories]

### Gauge and electrostatic partition

Weyl gauge `A₀ ≡ 0`; the transverse sector in the electromagnetic energy; the
longitudinal and electrostatic sector owned by Hartree plus ion-ion. *Breaks:*
electrostatic energy double-counted, and the vector-potential equation of motion becomes
gauge-dependent. — enforced, [unified-state#slots], [generic-dynamics#gauge-partition]

### Two independent polar predicates

`is-polar-material` (Born charges, longitudinal-transverse splitting) gates the
Fröhlich, polar-optical and Lyddane-Sachs-Teller machinery. `is-noncentrosymmetric`
(point group) gates spontaneous polarization, piezoelectricity, pyroelectricity and the
two-dimensional electron gas. They coincide on diamond and on wurtzite nitrides and
**split on gallium oxide** — centrosymmetric, yet Fröhlich-dominated. *Breaks:* a single
gate either invents spontaneous polarization for gallium oxide or kills its dominant
scattering channel. — enforced, [applicability-classifiers#polar-predicate-split]

### Real phonon frequencies are gated to claimed-stable phases

The `ω² ≥ 0` condition is applicability-gated to phases claimed stable. *Breaks:*
legitimate saddle points — which transition-path calculations must traverse — score as
violations. — enforced, [residual-definitions#structural-categories]

### The hull residual is temperature- and pressure-aware

It carries a metastability band, so metastable diamond reads zero residual. *Breaks:* a
naive convex hull tells the operator the flagship material should not exist. — enforced,
[residual-definitions#constraint-categories]

### A model-versus-microscopic pair is a consistency pair

Callaway against the full Boltzmann transport equation is a **consistency** pair, not an
equivalence pair. No agreement theorem exists for model-versus-microscopic pairs; the
obligation trips only on *excess*, and it is circular when the relaxation time is fitted
to the microscopic solution. *Breaks:* an obligation that either always trips or is
vacuously satisfied. — enforced, [residual-definitions#pair-kinds]

### A learned correction is frozen against the loss it modifies

The distribution-tail correction to the ionization coefficient is fit only to external
anchors; with no anchors it **ships as identity** and the corner stays
certification-refused. *Breaks:* the model co-adapts the correction to zero its own
residual, destroying supervision exactly in the unmeasured corner the validity domain
exists to protect. — enforced, [cert-obligations#composition-refusals]

### Drift-diffusion face flux is Scharfetter-Gummel

Not central differencing. At MV/cm fields with about 10 nm cells the cell Péclet number
is around 40. *Breaks:* the **residual operator itself** is wrong at the operating
point, so the operator is scored against a discretization artifact. — enforced,
[multiscale-state#eom-continuum]

### Positive semidefiniteness is a condition on the assembly

It is a condition on the assembled dissipative super-block per mechanism, and the
projector must be the congruence-action Reynolds operator — a bare orthogonal projection
does not preserve positive semidefiniteness. *Breaks:* per-kernel positivity holds while
the global friction operator fails it, and entropy production goes negative. — enforced,
[coupling-structure#psd-closure] for the assembly and
[cert-obligations#coupling-derived-checks] for the obligation that checks it

### Validity windows are re-evaluated per training sample

Swept-environment validity windows are re-evaluated per sample, each kernel tagged with
the environment box its structure is valid on. *Breaks:* a temperature sweep crosses a
quasiharmonic, ionization-fit or dynamical-stability boundary and leaves a stale kernel
silently in force. — enforced, [applicability-classifiers#swept-environment-windows]

## Values that are wrong if lifted naively

### The thermal-conductivity errors do not cancel

Decouple them. The relaxation-time approximation *under*estimates diamond conductivity
by 30 to 50 percent near 300 K; omitting four-phonon scattering *over*estimates by about
1 percent at 300 K, rising to about 30 percent at 1000 K. Anchor to the iterative
solution, not to the relaxation-time approximation. Every conductivity column declares
its isotope, boundary and relaxation-time-versus-iterative scope. — enforced,
[accuracy-ledger#kappa-battery]

### A conductivity figure that names the wrong material

The paper this corpus cites for diamond's high-temperature conductivity also carries a
headline pair of figures, **2200 falling to 1400 W/mK at room temperature**, which are
for **boron arsenide**. Diamond's own room-temperature conductivity is about 2200 W/mK,
quoted one paragraph away in the same paper. The two numbers collide numerically, so
anyone re-deriving the diamond anchor from that paper can land on the right number for
the wrong material and see nothing wrong — no unit is off, no order of magnitude is off,
and the figure agrees with what diamond is known to do. *Breaks:* the anchor for the
corpus's flagship material, undetectably. Read the sentence that names the material, not
the number. — advisory; the anchor this endangers is [accuracy-ledger#kappa-battery]

### Three-phonon transport overpredicts nitrides at high temperature

Measured gallium nitride conductivity falls as `T^−1.2` to `T^−1.5`, faster than
three-phonon theory. **Aluminum nitride above about 500 K is theory-only** — there is no
single-crystal measurement there. *Breaks:* nitride thermal budgets optimistic by about
1.7× at the operating point. — enforced, [accuracy-ledger#kappa-battery]

### Impact-ionization prefactors span four orders of magnitude

More than four orders, so the uncertainty is **at least ×3**, never ×1.5. *Breaks:*
breakdown field enters the Baliga figure of merit cubed, so a falsely tight ionization
uncertainty produces a falsely tight figure of merit. — enforced,
[accuracy-ledger#high-field-coefficients]

### Image-force lowering

`Δφ = √(qE/4πε_sε₀)` — diamond 0.16 eV at 10⁶ V/cm. Two wrong values circulate: one
carrying a √10 field-scaling error, and one about 13 percent high. *Breaks:*
barrier-derived contact resistance shifts by `e^(Δ/kT)`. — enforced,
[accuracy-ledger#observable-regimes]

### Peak velocity is not saturation velocity

Gallium nitride's 2.5×10⁷ cm/s is the **peak** velocity. Separately, aluminum nitride
electron mobility around 300 cm²/Vs is a doped and defective value, not an intrinsic
one. *Breaks:* velocity and mobility ceilings overstated by about 2× and about 3×. —
enforced, [accuracy-ledger#high-field-coefficients]

### Gallium oxide's critical field is an anisotropic triple

10.2, 4.8 and 7.6 MV/cm along `a`, `b` and `c*`. The widely quoted "about 8 MV/cm"
appears nowhere in the paper it is attributed to. *Breaks:* the scalar overstates the
weak `b` axis — the one that actually limits the device — by **1.67×**, and understates
`a` by 1.28×. — enforced, [accuracy-ledger#high-field-coefficients]

### Quasiharmonic validity is per-material

It does not follow a Debye-temperature-scaled rule. Diamond (Debye temperature about
2200 K) holds through about 800 °C; gallium nitride (about 600 K) fails near 500 °C;
aluminum nitride (about 1000 K) also fails at 500 °C. Those are 0.49, 1.29 and 0.77 of
the Debye temperature — no single fraction fits. The plausible "half the Debye
temperature" rule is back-fitted from diamond alone and contradicts its own gallium
nitride example, where half the Debye temperature is 27 °C rather than 500 °C.
**"Quasiharmonic suffices" is a diamond-only claim; for the nitrides the boundary is 500
°C and it is measured, not derived.** *Breaks:* thermal expansion,
gap-versus-temperature strain, shear modulus and the hull, for the flagship polar
materials at the design point. — enforced, [out-of-scope#exclusions]

### Alloy disorder is the dominant mobility limiter

For aluminum-gallium-nitride, alloy-disorder scattering dominates. *Breaks:* mobility
systematically optimistic for the flagship device's channel material. — enforced,
[accuracy-ledger#transport-coefficients]

### Degenerate doping breaks two non-degenerate assumptions

Degenerate p-type diamond breaks both: the Einstein relation becomes a declared
model-form error, and the Lyddane-Sachs-Teller dielectric constant with Fröhlich
screening must be gated on carrier density below degeneracy. *Breaks:* standard heavily
doped contact layers modeled with the wrong diffusion constant and an out-of-validity
dielectric function. — enforced, [multiscale-state#moment-closures],
[out-of-scope#exclusions]

### Diamond's high-temperature failure mode is oxidation

Air-oxidation at about 600 to 700 °C, not graphitization at about 1500 °C in vacuum.
*Breaks:* an about-800 °C error in the stated operating ceiling. — enforced,
[mvp-system#high-t-failure]

### A worked example is not one artifact

Worked examples hide errors, and they hide them in more than one file at a time. One
audit found, in a single derivation set, an exact charge-balance formula with the
exponential factor and the degeneracy misplaced — evaluating **about 100× low** — beside
an inverted activation fraction about 3× low; and, in a separate generator catalog, one
example that fired Fröhlich and polar-optical saturation velocity on **non-polar
diamond** in violation of its own polarity classifier, fed an n-type barrier into leakage
for a p-type contact (about 3.5 eV wrong), used the √10-erroneous image-force value, and
quoted a lattice conductivity 30 percent above the battery value. Five wrong things, two
files, one afternoon. *Breaks:* an example that looks pedagogical and teaches errors.
Do not read "the worked example" as a single artifact. — advisory

## Practice

### A prior audit's clearance is not evidence

A pass cleared thermal conductivity and the high-field parameters as sound, and missed a
conductivity overprediction, a mis-citation, and a **fabricated** citation. Re-verify
*values*, never verdicts: a later value-level correction outranks an earlier clearance,
and inheriting false confidence is the failure this rule exists to prevent. *Breaks:*
every downstream check that treats a clearance as a fact. — enforced,
[conventions#verdicts]

### Seed from the source, never from a page that quotes it

Values come from [accuracy-ledger#seed-provenance] and from the reference data under
[reference-data]. A page that quotes a value is quoting it; the
file is where it is changed and where a disagreement is settled. *Breaks:* a seeding wave
silently reverts a landed fix by re-deriving a value from prose. — enforced,
[conventions#artifacts]

### A registry name is an address

Registry formula names are hash-consed into content addresses. A rename after landing is
a substrate-wide rekey, not an edit: every cached kernel, certificate and address keyed
on the old name breaks. **Fix names before they land.** *Breaks:* the cache, the
certificates, and every address derived from them, all at once. — advisory

### A rename orphans every prose mention

A name that changes in the data file and nowhere else leaves every prose mention pointing
at nothing, and a reader who greps the old name concludes the row does not exist.
*A registry name is an address* is the discipline that avoids the
situation; it is a discipline, not
a check, and nothing currently catches a name that has already moved. *Breaks:* a
provenance trail that reads as absent rather than as renamed. — advisory

### Structural index analysis is generic-values-only

It can pass while the Jacobian is singular at the operating point. Pair structural
witnesses with sampled numerical spot-checks, and refuse loudly on failure. *Breaks:* an
evolver certified steppable that is singular exactly where the device operates. —
advisory

### A relaxed row is refused inside an evolver

A relaxed formula's forward relaxation bias becomes model error *of the vector field* and
compounds along the trajectory. *Breaks:* a relaxation acceptable for a pointwise score
integrates into a divergent trajectory. — advisory

### Differentiation safety is trajectory safety for an evolver

Rewrites that are exact almost everywhere but wrong on a measure-zero set are tolerable
for a pointwise scorer, not for a flow attracted to the bad set. *Breaks:* a rewrite that
is safe for scoring corrupts a trajectory. — advisory

### Pin provenance before the ledger entry

Record an unresolved conflict as a range, not as a pick. Open pins include contested
Schottky barriers, carbide onsets, and a Curie point sitting inside the operating
window. *Breaks:* a contested value enters the ledger as fact and propagates into
contact resistance and lifetime figures of merit. — enforced,
[reference-battery#wave-programme]

### A passing adjoint gate is not evidence of a gradient

Vector-Jacobian and Jacobian-vector products agree trivially wherever the true gradient
is zero, so a row whose output is piecewise constant — an argmin over a discrete set, a
hard-cutoff integer count — **passes the registration gate spuriously** and ships a
certificate for a gradient that does not exist. *Breaks:* the one gate that exists to
catch a missing gradient issues a pass instead. — enforced,
[residual-machinery#registration-gate]

### A conditioning failure is invisible to the adjoint gate

Both products solve against the *same* near-singular fixed-point Jacobian, so they agree
— on a gradient that is large and wrong. This is the mirror of *A passing adjoint gate
is not evidence of a gradient*: there the gate passes because the true gradient is zero,
here because both sides make the same error. A fixed-point row therefore carries a
second gate on the reciprocal condition number. *Breaks:* charge neutrality in a
wide-gap intrinsic semiconductor — this corpus's own subject — has the flattest
Fermi-level derivative there is, and the rows that compute it sit right on it. —
enforced, [residual-machinery#registration-gate]

### Fixed-point adjoint is a structural claim, not a fallback

`fixpoint-adjoint` asserts that the output is a converged fixed point whose adjoint
costs one linear solve **independent of the forward iteration count**. It is a
refinement of `adjoint`, not a tier below it and not a place to put rows whose gradient
is awkward. A finite difference is not a fixed point; neither is a transient partial
differential equation. Material written under other conventions inverts two of these
labels — `D3` for a finite-difference fallback and `D0` for a closed-form analytic
gradient — so a label lifted from outside this corpus is translated, never copied.
*Breaks:* a row promises an iteration-count-independent adjoint it cannot deliver. —
enforced, [named-formulas#diff-tags]

### No-derivative is the strongest claim in the vocabulary

`none` asserts that no relaxation **exists**, not merely that none has been written. It
is therefore the label most often wrong. Check for a real-valued output component, and
for an existing relaxation, before assigning it: a row whose output is a list of real
phases is smooth in the eigenstates away from the branch cut, and is produced by the
same eigendecomposition structure that other rows carry at `adjoint`. *Breaks:* a row
critical to the minimum viable product silently leaves the differentiable path. —
enforced, [named-formulas#diff-tags]

### A relaxed row that names no relaxation is ungateable

The approving obligation has nothing to approve, and the model-form bias never enters
the combined tolerance. *Breaks:* a relaxation ships with an undeclared, unbounded bias.
— enforced, [named-formulas#diff-tags]

### A short token collides with real physics

`D1` through `D5` are the wurtzite deformation potentials in
[accuracy-ledger#iii-n-electronic]. Any short alphanumeric token the corpus invents will
collide with a physical quantity somewhere, and no checker can separate the two by shape
— which is why
corpus-invented names are spelled out in English ([agent-contract#vocabulary]). Where
prose must quote a symbol, put it in backticks so a search for one does not return the
other. *Breaks:* a sweep over one vocabulary silently collects rows from another. —
enforced, [agent-contract#vocabulary]

### The missing-data marker and its collisions

Three unrelated objects a reader will meet in this domain wear the token `GAP`: a
computer-algebra system, the Gaussian Approximation Potential, and — in lowercase — the
band gap. A marker for missing data spelled the same way makes four. *Breaks:* a sweep
for missing data collects a language candidate and a machine-learned potential; a sweep
for the band gap collects all four; and none of the four is wrong, so nothing fires.
[glossary#overloaded] carries the reserved spelling of each. — enforced,
[glossary#overloaded]

### A checker that finds nothing may not be looking

A structure checker harvested section coordinates with a pattern requiring a dot, so about
twenty citations of one form were silently skipped while a green run was cited as evidence
that they resolved. A data checker captured a formula argument with an ASCII-only
character class, so an argument written `σ/(n·e)` was invisible to it. Both ran green the
whole time. **Before citing a clean run as evidence, plant a defect of exactly the class
you claim is absent and confirm the run fails.** *Breaks:* clearance-is-not-evidence,
applied to the tools that produce the clearance. — enforced, [conventions#verdicts]

### A calibration with holes is a green you cannot cash

The hazard above says a checker that finds nothing may not be looking, and a
calibration tool exists to answer it by planting a defect per check. One did not: four
finding classes of one checker and nine checks of another had **no probe at all**, while
two pages claimed one defect per check and a fired-probe ratio was cited corpus-wide as
warrant for believing a clean run. Every one of those checks turned out to work — the
defect was in what the calibration *established*. *Rule:* coverage is **derived from the
checker's source**, never from a list kept beside it; a list of what is covered drifts
exactly like the thing it describes. *Breaks:* the whole evidence chain, silently, because
a calibration is the one artifact whose incompleteness nothing downstream can detect. —
enforced, `apparatus/tools/check_the_checker.py`

### A checker inherits the soundness of its premise

A tolerance ledger asserted that a particular symbol denotes a tolerance throughout.
Reading that as a reserved namespace, a checker was written to flag every use of it absent
from the ledger. It fired **48 times on correct prose**: the same symbol names
Shockley-Read-Hall carrier lifetimes, a scattering time, an energy relaxation time. The
checker was correct with respect to its premise; the premise was false. Narrowing does not
help — a relaxation time of `1e-12` s is shaped exactly like a tolerance of `1e-12`.
*Rule:* before writing a checker, verify the invariant it rests on **against the corpus**,
not against the page that asserts it. *Breaks:* nothing in the corpus, and that is the
point — the damage is to the reader, who learns that the output is noise and starts
skimming past it, which is the disease this apparatus exists to treat. — enforced,
[conventions#verdicts]

### Harvest a vocabulary from the schema that owns the field

A closed-vocabulary check on the registry read the observable-bundle codes out of a table
and reported four rows as defects for carrying a linear-response primitive tag instead.
They are not defects: [named-formulas#formula-record] owns the `bundle` field's schema and
admits that tag, and [observable-bundles#linear-response-primitives] says the same thing
in the paragraph directly beneath its own table — the four rows are level-one
primitives feeding several bundles, so they carry the primitive tag *instead of* a
bundle, deliberately. Two pages, consulted by neither the check nor its author. *Rule:*
a vocabulary has an owner; find the page that defines the *type*, not the page that
lists the *values*. And when a check fires on data that has been stable for months,
suspect the check first. *Breaks:* worse than a false positive — the "fix" retagged four
correct rows, so a checker built on a partial vocabulary corrupted the data it was
written to protect. — enforced, [named-formulas#formula-record]

### Sum-preserving arithmetic errors survive every eyeball

A cost-tier distribution read 75/40/13/4 against an actual 76/40/11/5. It was wrong in
three of four entries and *still summed to 132*, so every check that verified the total
passed. The tally on the very next line was correct, because a checker compared it against
the source file; the tier line had no checker. *Rule:* a tally is checked against its
source or it is not checked — an internal consistency test on a distribution is not a test
of the distribution. *Breaks:* the assumption that a distribution which adds up has been
verified. — enforced, [conventions#counts]

### A number quoted without its complement

A result was cited here as "*faster*, and more accurate in 104 of 289 benchmarks",
concluding that soundness is not a tax — at three sites. The paper's **very next
sentence** reports that the unsound rule set won on accuracy in **135** cases. On
accuracy the sound version lost more often than it won; what the paper shows is that
soundness is *affordable* — free in time, roughly even in accuracy, and it solved one
benchmark the unsound set could not solve at all. Nothing in the quoted half was false.
*Rule:* when a result is a comparison, quote **both arms**, and read the sentence after
the one you are lifting. *Breaks:* the conclusion, not the datum — and undetectably,
because every number checks out against the source. — enforced,
[compose-time-pipeline#rewrite-admission]

### A dangling pointer is safer than a plausible reconstruction

When a citation points at something that does not exist, the honest repair is to find what
it meant *in the record* — not to infer what it must have meant and write that down. A
reference to "the declared mesh-uncertainty floor" was dangling; a repair pass replaced it
with a confident account of how the floor is computed. Archaeology then established that no
such floor was ever declared, in any commit. The reconstruction was invention, and it read
as settled fact where the dangling pointer at least read as broken. *Rule:* check the
record before filling a hole; if the record is empty, say the record is empty. *Breaks:* a
repair pass converts a visible gap into an invisible fabrication. — enforced,
[conventions#verdicts]

### Not every gap a repair exposes was caused by the thing repaired

Three of seven items recovered by archaeology after one such pass — a dangling
mesh-uncertainty reference, a blanket ±15 percent on breakdown field, and a
dressing-staleness term with no policy behind it — were byte-identical in landings months
earlier. Destroying the process artifacts destroyed the only surviving copy of their
*reasoning*, but the gaps predate that. *Rule:* date the defect before crediting it to the
change you are repairing. *Breaks:* a repair framed as restoring what a change dropped
silently reverts to a state that was already wrong, and the real defect survives with a
fresh timestamp on it. — advisory

### Never put a tolerance in the address

Content-addressed identity is an *equivalence* relation; numerical closeness is a
*tolerance* relation and is **not transitive** (`‖a−b‖≤ε` and `‖b−c‖≤ε` give `2ε`). A
tolerance relation induces a covering by maximal cliques, not a partition — so there is
no canonical representative and nothing to hash. Any proposal to round before hashing,
to deduplicate "close enough" objects, or to make node identity
bisimulation-up-to-tolerance destroys hash-consing, Merkle deduplication, constant-time
address equality and the cache at once. Carry the tolerance *beside* the address, as
evidence. *Breaks:* the single highest-consequence invariant in the substrate, in
exchange for a deduplication nobody asked for. — enforced,
[representation-substrate#identity-exact]

### A declared error target is not a measured error

A compression plan picks a rank to meet a truncation target; a truncated solve stops at
a tolerance. Those are intentions. What the composition actually achieved is a different
number, and only that one is evidence — the discarded singular value and the stopping
residual are both already computed, so the measurement is free. *Rule:* an intention
that nothing measures is not a measurement. *Breaks:* an error budget assembled from
what every stage *meant* to do. — enforced,
[representation-substrate#estimate-dont-decide]

### Exact-only is not a conservative gate

It is an untested one. The reference tool for float-accuracy rewriting carried
known-unsound rules for years; when the rules were simply deleted, the tool became
useless on a large part of its own benchmark suite. The fix was not exactness — it was
**side conditions discharged by an equivalence-class analysis**, intervals and
not-equals facts riding alongside an equality that stays exact over the reals — and the
sound version ran *faster* overall while roughly breaking even on accuracy (*A number
quoted without its complement* is the same result read honestly). *Breaks:* a rule set
kept small in the name of safety, which is neither safe nor small enough to be useful. —
enforced, [compose-time-pipeline#rewrite-admission]


---
id: cert-obligations
title: "Cert obligations"
owns:
  - the ten cert obligations
  - certificate artifact
  - cert evidence aggregation
  - tolerance ledger
  - composition-validity refusals
  - reference-cache backend
anchors:
  certificate-artifact: "The certificate artifact"
  the-ten-obligations: "The ten obligations"
  evidence-aggregation: "Evidence aggregation"
  coupling-derived-checks: "Coupling-derived checks"
  tolerance-ledger: "Tolerance ledger"
  composition-refusals: "Composition-validity refusals"
  reference-cache: "The reference cache"
depends-on:
  - accuracy-ledger
  - reference-battery
  - out-of-scope
  - typeclass-alphabet
  - coupling-structure
  - residual-machinery
  - residual-definitions
  - representation-substrate
  - compose-time-pipeline
  - generic-dynamics
  - conventions
  - named-formulas
open-questions:
  - id: surrogate-validity-scope
    anchor: the-ten-obligations
    summary: "Obligation 9 names a set of formulas that does not exist. It is stated as surrogate-net validity over the formulas tagged `relaxed`, but `relaxed` means genuinely non-smooth — argmin, soft hull, sort, discrete — and all six formulas carrying it are relaxations, not learned nets. The one learned surrogate in the registry, the quasi-particle-shift surrogate, is tagged `adjoint` and falls outside the obligation entirely. The obligation's checker body (declared input domain contains the query, surrogate uncertainty below tolerance, refresh current, measured on a held-out development set) describes a learned net, which a soft-hull relaxation is not. This page contradicts itself about it: the obligation reads `surrogate`, its tolerance-ledger row reads `relaxation validity`. Does obligation 9 rebind to the learned surrogates, split into surrogate-validity plus relaxation-validity, or rescope some other way?"
  - id: csv-to-sqlite-path
    anchor: reference-cache
    summary: "No page states how a reference row reaches the cache. The canonical archive is a set of CSVs; obligations 4 and 8 read a content-addressed SQLite cache in the same directory; there is no stated ingest step, no build target, and no statement of which artifact the obligation reads at runtime. A cache over a CSV archive is coherent, and this is not a physics gap — it is an unstated step in the corpus's own machine-readable path."
---
# Cert obligations

Cert is a first-class deliverable: a schema, a deterministic text renderer, a freeze
fixture with a tamper tripwire, and a high-precision oracle cross-check.

## The certificate artifact

The certificate emitted for any prediction is an **inert s-expression** carrying scalar
verdicts plus numeric witnesses for the failures. It executes nothing and decides
nothing; reading it is the whole of consuming it.

**Its schema is the cross-workstream contract** — the artifact the operator library
consumes, and the reason the oracle can be certified against a consumer that does not
exist yet. The freeze fixture, the tamper tripwire and the high-precision oracle
cross-check are checks *on* the schema, and are non-load-bearing: a prediction is
certified by the ten obligations below, not by them.

## The ten obligations

Each obligation is a **generic function over one typeclass axis** ([typeclass-alphabet]),
which is what lets one checker serve every formula that presents that axis rather than
one checker per formula. The axis is the second column; it is not a separate mapping, and
it is not restated anywhere else, because this list existed in three copies with three
different second columns and a retag reached one of them.

| # | Obligation | Typeclass axis and check | Complexity |
|---|---|---|---|
| 1 | symmetry equivariance | `Sampleable` × group action: a symmetry operation on the domain equals the orbit-induced action on the codomain under `approxEq`. Sample the form, apply the trivial-irrep projector, residual below `δ_sym` | `O(1)` per invariant |
| 2 | bounds (physical positivity) | `Quantity` ordering: the value is checked against each declared bound. Applicability evaluation plus a scalar range test; positive-semidefiniteness of `M` as `λ_min(M_block) ≥ −δ_PSD` on the assembled per-mechanism dissipative super-block | `O(path)` + `O(block)` |
| 3 | analytic limits, where closed-form answers exist | `HasAnalyticStructure`: evaluate the limit, check the witness predicate, compare to the closed form at `\|predicted − exact\|/σ < 3` | `O(1)` per formula |
| 4 | reference battery | content-side: look a row up by `(Property, Material, Environment)` in the frozen reference data on a held-out crystal battery ([reference-battery]) and compare under `approxEq` | `O(log n)` B-tree |
| 5 | conservation laws | `Integrable`: `integrate(measure)` equals the declared invariant within `τ_cons`. For antisymmetry of `L`, project the emitted form onto its antisymmetric component, residual below `δ_sym` | `O(1)` per invariant |
| 6 | GENERIC degeneracy and named-formula consistency across equivalent compositions | `Sampleable` + `approxEq`: two formulas claiming one quantity agree on the shared domain (compare formula trees and coefficients within tolerance), plus the cert-only degeneracy tripwire `‖L δS/δx‖² + ‖M δE/δx‖² ≈ 0` per tier — a generator-construction bug detector ([generic-dynamics], [residual-definitions]) | `O(\|G\|)` per equivalence |
| 7 | bulk-boundary correspondence | `DiscreteStructure` morphism: for a bulk carrying a given symmetry-indicator class, the slab must carry boundary states with the multiplicities a lookup table gives for `(indicator generator, boundary orientation)`. Elementary-band-representation table lookup plus multiplicity enumeration | `O(1)` + `O(#Wyckoff)` |
| 8 | reference-battery versioning | versioning discipline on obligation 4: per-entry provenance travels with the verdict, the row's schema version is compared by the reader, and the cert trips at `τ_battery` with the numerical witness | `O(log n)` + `O(1)` |
| 9 | surrogate validity | declared input domain contains the query · surrogate uncertainty below `δ_surrogate` · refresh current, measured on a held-out development set. **Which formulas this ranges over is the open question `surrogate-validity-scope`** — the obligation names a tag whose meaning does not match its checker body | forward pass over the development set |
| 10 | adjoint existence at registration | the registration-time adjoint gate ([residual-machinery]), enforced at registration and never at prediction: a DAG walk asserting every upstream node has a registered adjoint. It covers **both** `adjoint` and `fixpoint-adjoint`, because the second refines the first rather than replacing it and runs its gate plus a conditioning check ([named-formulas#diff-tags]) — gating only `adjoint` would exempt the stronger tier from the test the weaker one must pass | `O(#nodes)`, memoized |

## Evidence aggregation

The evidence produced by the ten obligations is one
`MerkleDAG[EvidenceOps, EvidencePayload]` per composition, in the substrate's sense
([representation-substrate]). Each obligation's output is a typed leaf attached as an
`EvidenceOps.attestation` node.

Aggregation across obligations is the **semilattice meet** of `EvidenceOps`, so a
composition's overall verdict is

- `Failed` if any obligation leaf is `Failed`,
- `Pending` if any leaf is `Pending` and none is `Failed`,
- `Passed` otherwise.

`Failed` absorbs, which is what licenses early exit. The attestation DAG's root
`Address` is the cert artifact the operator library consumes.

## Coupling-derived checks

When a formula node originates from the invariant generator ([coupling-structure]),
obligations 1, 2 and 5 collapse to projection-residual checks against the tolerances
below. These run alongside the generator during invariant synthesis, at `O(1)` to
`O(block)` per invariant.

- **Obligation 1, symmetry equivariance.** Invariants are trivial-irrep basis vectors by
  construction, so the check is that the emitted `InvariantTerm.symbolic-form` lies in
  the claimed subspace: `‖v − π_trivial v‖ / ‖v‖ < δ_sym` on a sampled evaluation. A
  failure here is a generator bug, not a physics bug.
- **Obligation 5, antisymmetry of `L`.** `AntisymmForm` invariants project onto the
  antisymmetric component; cert verifies the emitted form equals its projection within
  `δ_sym`. Antisymmetry is what conserves energy; Jacobi status is [generic-dynamics]'s.
- **Obligation 2, positive-semidefiniteness of `M`.** For `PSDSymmForm` targets the
  projector is the **congruence-action Reynolds operator**, averaging `ρ(g)ᵀ M ρ(g)`:
  only the congruence action preserves positive-semidefiniteness, and a bare orthogonal
  subspace projection does not. The condition is stated on the **assembled dissipative
  super-block per mechanism** — the diagonal kernels together with their off-diagonal
  cross-kernels — through a Schur-complement or Gram condition, and **not** per
  off-diagonal kernel in isolation, because an off-diagonal cross-kernel alone is not
  sign-definite. Cert checks `λ_min(M_block) ≥ −δ_PSD` on that super-block.
  [coupling-structure] holds the theorem that such a block exists; this is its runtime
  guard.

## Tolerance ledger

Canonical names and default values for every tolerance and error bound in the oracle
library. These are the inputs `Quantity.combineTol` ([typeclass-alphabet]) composes into
the per-observable error budget ([residual-definitions]).

`ε` is reserved for permittivity in the physics formulas. **`τ` is not a reserved
tolerance prefix** — `τ_n`, `τ_p`, `τ_PO`, `τ_E`, `τ_hop`, `τ_iv` and `τ_alloy` are
physical times, and a `τ_x` is a tolerance only if it appears in the table below.
[conventions] owns that namespace rule.

| Name | Meaning | Default |
|---|---|---|
| `δ_sym` | symmetry and antisymmetry projection residual (obligations 1, 5) | `1e-6` relative |
| `δ_PSD` | assembled-super-block negative-eigenvalue guard (obligation 2) | `1e-9` absolute |
| `τ_SCF,strict` | self-consistent-field gradient-norm convergence on the reference and compile side | `1e-8` Ha |
| `τ_SCF,train` | self-consistent-field convergence on the runtime and training path, looser | `1e-4` Ha |
| `τ_L3L4` | equilibrium-statistics-to-non-equilibrium same-pass fixed-point residual, at most 5 iterations | `1e-4` |
| `τ_equiv` | `Algebraic/MethodEquivalence` **equivalence-pair** agreement, for theorem-backed pairs (obligation 6) | `1e-4` relative |
| `τ_method` | `Algebraic/MethodEquivalence` **consistency-pair** model-gap envelope (obligation 6) | 10–20%, declared per formula pair |
| `δ_meta` | temperature-and-pressure hull metastability band ([residual-definitions]; the hull formula in the registry) | `50 meV/atom`, per-material overridable — diamond at +25 reads inside the band |
| `τ_adj` | registration adjoint vector-Jacobian-versus-Jacobian-vector gate, over `adjoint` and `fixpoint-adjoint` ([residual-machinery]) | `1e-4` relative |
| `τ_cond` | `fixpoint-adjoint` fixed-point-Jacobian conditioning guard at the same sampled points; below it, registration refuses | `1e-8` reciprocal condition number |
| `τ_trunc` | a-posteriori estimate of the gradient error a **truncated** inner solve introduces in an implicit-function adjoint — the error `τ_cond` cannot see, because `τ_cond` bounds the Jacobian's conditioning while `τ_trunc` bounds `‖J⁻¹‖·‖r_stop‖`, that conditioning times the stopping residual. Emitted by the fidelity generator ([residual-machinery]), not a threshold to configure | measured per instance; enters `combineTol` |
| `δ_surrogate` | obligation-9 validity margin, measured on a held-out development set. **What it ranges over is `surrogate-validity-scope`**: this row reads *relaxation* validity and the obligation reads *surrogate* validity | per formula |
| `τ_battery` | reference-battery agreement before the cert trips (obligation 8, [reference-battery]) | 3σ of the entry's declared uncertainty |
| `δ_plan` | per-compression-plan truncation error target ([compose-time-pipeline]); the sum over active plans is the compression term in `combineTol` | per plan, declared at plan selection |
| `τ_NEB` | `PathStationaryOf` climbing-image nudged-elastic-band force convergence | `1e-3` |
| `τ_cons` | obligation-5 conservation: `integrate(measure)` against the declared invariant | `1e-8` relative, following `τ_SCF,strict` |
| `τ_interp` | differential golden test between lowering and runtime: two evaluators of the same intermediate representation must agree | `1e-10` relative — tighter than any physics tolerance, because the two sides compute the same expression |

`τ_trunc`'s shape has literature behind it, and the transfer is by analogy rather than
directly. Computable a-posteriori estimates of the form (inverse-Jacobian bound) ×
(stopping residual) are given by Ehrhardt and Roberts, *IMA J. Appl. Math.* 89(1)
254–278 (2024), Theorem 9 — but they assume a strongly-convex lower-level
*optimization* problem, whereas a self-consistent-field inner solve is a general
nonlinear fixed point. Blondel et al. (NeurIPS 35, 2022) bound the same Jacobian error
for a general optimality condition, `‖J(x̂,θ) − ∂x*(θ)‖ < C‖x̂ − x*(θ)‖` — closer in
setting, but not a-posteriori computable, since it is stated in terms of the unknown
`x*`.

**Exhaustiveness of this table is a review rule, not a machine result.** A tolerance
stated anywhere in the corpus but absent from this table is a defect in this table, not
in the other page — and nothing enforces that. Separating a tolerance from a physical
time mechanically would need a namespace the corpus does not have, `tol_adj` against
`τ_adj`, and narrowing by value shape does not separate a `1e-12` second relaxation time
from a `1e-12` tolerance. So the rule is labeled as a rule rather than implied to be
checkable: **when you add a tolerance, add it here.**

## Composition-validity refusals

Four compose-time refusals are decided by tag and field comparison on the active
`CouplingSpec` and `ProvenanceLedger`, and are emitted as obligation leaves rather than
left to documentation. Each is a `Failed` verdict with a witness — the offending
coefficient or row pair.

- **Unprovenanced coefficient** (obligations 4 and 9, [coupling-structure]). Any active
  channel carrying a coefficient with no `ProvenanceLedger` entry refuses the
  composition. An unprovenanced coefficient is a silent accuracy hole.
- **Gap-slope double count** (obligation 6). Adiabatic-Hedin-Coulomb gap-renormalization
  slopes carry `slope-kind ∈ {isochoric, total}`. A composition in which a
  `total`-tagged slope and the thermal-expansion strain path are both active on the same
  observable is refused: the two paths would double-count the lattice-expansion part of
  `dE_g/dT`. The witness is the `(slope coefficient, thermal-expansion instance,
  observable)` triple. An `isochoric`-tagged slope passes.
  [accuracy-ledger#ahc-zpr] holds the tagged values and the composition rule.
- **Learned correction without an anchor** (obligation 9). A learned correction
  coefficient — in V1, the high-field distribution-tail correction ([coupling-structure])
  — is admissible only if external anchor data back its declared validity domain. With
  no anchors it ships as identity, and any query inside the unanchored
  high-field-by-high-temperature corner trips obligation 9 with a domain witness.
  [out-of-scope#exclusions] carries that stance.
- **Polarization-convention pairing** (obligation 6, [coupling-structure]). Each
  spontaneous-polarization and piezoelectric coefficient carries
  `polarization-reference ∈ {ZB-proper, H-improper}`, and a composition whose active
  pair carries **mismatched** tags is refused. The witness is the tag pair. Mixing a
  zincblende-reference spontaneous polarization with an improper `e₃₁` breaks the
  cancellation the ±5% interface-polarization target rests on and corrupts the
  two-dimensional-electron-gas sheet density; the magnitudes, the cancellation and the
  scope restriction to aluminum-gallium-nitride on gallium nitride are
  [accuracy-ledger#polarization-coefficients]. The curated III-nitride coefficients are
  `ZB-proper`.

## The reference cache

Obligation 4 and its versioning discipline in obligation 8 read from a single
content-addressed store, the **`SqliteReferenceCache`**: a process-local SQLite file at
the cache inside [reference-data], opened in write-ahead-log mode for
concurrent reads from the training process and the cert evaluator.

```
table entries (
  key             TEXT  PRIMARY KEY,   -- ContentAddress over (observable, value, sigma, provenance, coverage-mask)
  observable      TEXT  NOT NULL,      -- ObservableRef serialization
  value           BLOB  NOT NULL,      -- typed payload (scalar, tensor, curve)
  sigma           REAL  NOT NULL,
  provenance      TEXT  NOT NULL,      -- JSON: { source, doi?, fetched-at, version }
  coverage_mask   BLOB  NOT NULL,      -- RoaringCoverageMask serialization
  schema_version  INT   NOT NULL
)
```

- **Key construction.** A `ContentAddress` over the canonical serialization of
  `(observable, value, sigma, provenance, coverage_mask)`, SHA-256 backed per
  [representation-substrate]. Identical payloads collapse to one row; a tampered payload
  changes the key and trips the obligation-8 freeze comparison.
- **Schema versioning.** `schema_version` bumps on any column addition. Readers refuse
  rows whose `schema_version` exceeds the linked-in schema, which forces an explicit
  migration step rather than silent drift. The type-level schema version enters every
  `Address`; the per-row column is compared by the obligation-8 reader and is never part
  of the key.
- **Write discipline.** Write-once per key. An update produces a new row with a new key,
  deletes are disallowed on the cert path, and an obsolete row is tombstoned through
  `provenance.version`.
- **Why SQLite.** Single-file, ACID, no daemon, ubiquitous; write-ahead-log mode serves
  the read-heavy cert workload; `O(log n)` B-tree lookup scales from the MVP's roughly
  ten-row diamond battery to the long-tail target of about 10⁴ rows with no
  infrastructure change.

The **canonical archive those rows describe is a set of CSVs**, and
[reference-battery#why-csv] owns that decision. How a CSV row becomes a cache row is
`csv-to-sqlite-path`.

This cache and the evidence DAG are the **persistent components of the oracle library**;
everything else is recomputed from the graph.

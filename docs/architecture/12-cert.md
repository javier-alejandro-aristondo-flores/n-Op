---
id: arch-12-cert
title: Cert obligations
status: draft
revision: 1
canonical-for:
  - ten cert obligations
  - reference-cache backend
depends-on:
  - arch-05-generic
  - arch-07-pipeline
  - arch-10-typeclasses
  - arch-11-residuals
  - arch-16-pino-bridge
  - arch-19-coupling-structure
  - arch-20-representations
  - impl-07-residual-factory
referenced-by:
  - arch-06-physics-graph
  - arch-07-pipeline
  - arch-09-vocabularies
  - arch-11-residuals
  - arch-13-applicability
  - arch-16-pino-bridge
  - arch-17-out-of-scope
  - arch-18-open-decisions
  - arch-19-coupling-structure
  - arch-20-representations
  - impl-06-compositions
  - impl-07-residual-factory
  - impl-08-cert-detail
  - impl-09-cross-cutting
  - mvp-03-capabilities
research-sources: []
---
# Cert obligations

Cert is a first-class deliverable: schema, deterministic text renderer, freeze
fixture + tamper tripwire, and a high-precision oracle cross-check. The
certificate emitted for any prediction is an inert s-expression carrying scalar
verdicts plus numeric witnesses for failures.

1. Symmetry equivariance.
2. Bounds (physical positivity).
3. Analytic limits (where closed-form answers exist).
4. Reference battery (frozen reference data on a held-out crystal battery).
5. Conservation laws.
6. GENERIC degeneracy + named-formula consistency across equivalent
   compositions.
7. Bulk-boundary correspondence (a `DiscreteStructure` morphism: for a bulk
   classified as `X_BS = k`, the slab must carry boundary states with
   multiplicities given by a lookup table indexed on
   `(k_generator, boundary_orientation)`).
8. Reference-battery-versioned (versioning discipline on obligation 4; reads
   `physics/library/cert/reference-data/`, looks up rows by
   `(Property, Material, Environment)`, trips at `|predicted − reference|/σ > 3`
   with the row's provenance).
9. Surrogate-net validity (for D4 surrogate formulas).
10. Adjoint-existence at registration (the registration-time adjoint gate,
    `impl-07-residual-factory §7.5`).

Each obligation maps onto a Layer-0 axis (§10), making the cert checkers generic
functions over the typeclasses.

The cert evidence produced by the ten obligations is one
`MerkleDAG[EvidenceOps, EvidencePayload]` per composition, in the
substrate's sense (`arch-20-representations §20.2`, §20.3 row for
cluster C4). Each obligation's output is a typed leaf attached as an
`EvidenceOps.attestation` node; aggregation across obligations is the
semilattice meet of `EvidenceOps`, so a composition's overall verdict
is `Failed` if any obligation leaf is `Failed`, `Pending` if any leaf
is `Pending` and none is `Failed`, and `Passed` otherwise. The
attestation DAG's root `Address` is the cert artifact `/informed-
operator` consumes.

## 12.0.1 Coupling-derived simplifications (obligations 1, 2, 5)

When a formula node originates from the invariant generator
(`arch-19-coupling-structure §19.3`), obligations 1, 2, and 5 collapse to
projection-residual checks (tolerances named in §12.0.2):

- **Obligation 1 (symmetry equivariance).** Invariants are
  trivial-irrep basis vectors by construction. Cert verifies the
  emitted `InvariantTerm.symbolic-form` lies in the claimed subspace:
  `||v − π_trivial v|| / ||v|| < δ_sym` on a sampled evaluation. Failure
  is a generator bug, not a physics bug.
- **Obligation 5 (antisymmetry of `L` — a conservation property).**
  `AntisymmForm` invariants project onto the antisymmetric component; cert
  verifies the emitted form equals its projection within `δ_sym`. (Antisymmetry
  conserves energy; Jacobi status per `arch-05-generic`.)
- **Obligation 2 (PSD of `M` — a bounds/positivity property).** For
  `PSDSymmForm` targets the projector is the **congruence-action Reynolds
  operator** (averaging `ρ(g)ᵀ M ρ(g)`) — only the congruence action preserves
  positive-semidefiniteness; a bare orthogonal subspace projection does not. The
  PSD condition is stated on the **assembled dissipative super-block per
  mechanism** (the diagonal kernels together with their off-diagonal
  cross-kernels), via a Schur-complement / Gram condition — **not** per
  off-diagonal kernel in isolation (an off-diagonal cross-kernel alone is not
  sign-definite). Cert checks `λ_min(M_block) ≥ −δ_PSD` on that assembled
  super-block. PSD *existence* is the structural theorem of `arch-19 §19.12`;
  this is its runtime guard.

These checks are `O(1)`–`O(block)` per invariant and run alongside the generator
at Stage 2.5.

## 12.0.2 Tolerance ledger

Canonical names and default values for every tolerance / error bound in `/physics`.
The symbol `δ` / `τ` denotes a *tolerance* throughout; `ε` is reserved for
permittivity in the physics formulas (this ends the `ε` collision noted in
`arch-19`). These values are the inputs `arch-10-typeclasses` `Quantity.combineTol`
composes into the per-observable error budget (`arch-11-residuals §11.7`).

| Name | Meaning | Default |
|---|---|---|
| `δ_sym` | symmetry / antisymmetry projection residual (obligations 1, 5) | `1e-6` relative |
| `δ_PSD` | assembled-super-block negative-eigenvalue guard (obligation 2) | `1e-9` absolute |
| `τ_SCF,strict` | SCF / minimization gradient-norm convergence (reference / compile side) | `1e-8` Ha |
| `τ_SCF,train` | SCF convergence on the runtime / training path (looser) | `1e-4` Ha |
| `τ_L3L4` | L3↔non-equilibrium same-pass fixed-point residual (≤ 5 iters) | `1e-4` |
| `τ_equiv` | `Algebraic/MethodEquivalence` **equivalence-pair** agreement (theorem-backed pairs, obligation 6) | `1e-4` relative |
| `τ_method` | `Algebraic/MethodEquivalence` **consistency-pair** model-gap envelope (obligation 6) | `10–20%`, declared per formula pair |
| `δ_meta` | T,P-hull metastability band (`arch-11 §11.1` item 17, registry row 124) | `50 meV/atom`, per-material overridable (diamond +25 reads R=0) |
| `τ_adj` | registration adjoint vJp-vs-JvP gate (`impl-07-residual-factory §7.5`) | `1e-4` relative |
| `δ_surrogate` | D4 surrogate / relaxation validity (obligation 9), measured on a dev set | per-formula |

## 12.0.3 Composition-validity refusals (machine-checkable, not reviewer caveats)

Four compose-time refusals are decided by tag/field comparison on the active `CouplingSpec` +
`ProvenanceLedger`, emitted as obligation leaves rather than left to documentation. Each is a
`Failed` verdict with a witness (the offending coefficient / row pair).

- **Unprovenanced-coefficient refusal** (obligation 4/9 family, `arch-19-coupling-structure §19.8`).
  Any active channel carrying a coefficient with no `ProvenanceLedger` entry refuses the
  composition — an unprovenanced coefficient is a silent accuracy hole.
- **AHC `slope-kind` double-count refusal** (obligation 6, named-formula consistency).
  `ahc-gap-renormalization` (row 120) slopes carry `slope-kind ∈ {isochoric, total}`
  (`arch-19 §19.8`). A composition in which a `total`-tagged AHC slope and row 63's
  thermal-expansion (`Ξ·strain`) T-path are both active on the same observable is refused — the
  two paths would double-count the lattice-expansion part of `dE_g/dT`. Witness: the
  `(row 120 coeff, row 63 instance, observable)` triple. An `isochoric`-tagged slope passes.
- **Learned-correction-without-anchor refusal** (obligation 9, surrogate validity). A PINO-learned
  correction coefficient (V1: the EDF-tail `Δα`, `arch-19 §19.8`) is admissible only if external
  anchor data back its declared validity domain; with no anchors it ships as identity and any query
  inside the unanchored high-E×high-T corner trips obligation 9 with a domain witness (the
  ">500 °C breakdown = cert-refused, not met" stance).
- **Polarization-convention pairing refusal** (obligation 6, named-formula consistency;
  `arch-19 §19.8`). Each spontaneous-polarization (`P_sp`, row 113) and piezoelectric (`e₃₁`,
  rows 114/117) coefficient carries `polarization-reference ∈ {ZB-proper, H-improper}`. A
  composition whose active `P_sp` and `e₃₁` carry **mismatched** tags is refused — mixing a
  ZB-reference `P_sp` with an improper `e₃₁` (or vice versa) breaks the Dreyer accidental
  cancellation (PRX 6 021038 (2016)) and corrupts the 2DEG `n_s` (improper `e₃₁ ≈ 3.4× proper`).
  Witness: the `(P_sp coeff, e₃₁ coeff)` tag pair. The ±5%-ΔP target is additionally scoped
  `is-AlGaN-GaN`; a high-In InGaN/GaN composition (where the cancellation is incomplete) is
  σ-degraded or refused. The curated III-N coefficients are `ZB-proper` (`docs/accuracy-ledger.md`).

## 12.1 `SqliteReferenceCache` — backend for obligations 4 + 8

The reference battery (obligation 4) and its versioning discipline
(obligation 8) read from a single content-addressed store, the
**`SqliteReferenceCache`**: a process-local SQLite file at
`physics/library/cert/reference-data/cache.sqlite`, opened in WAL mode
for concurrent reads from the training process and the cert evaluator.

```
table entries (
  key             TEXT  PRIMARY KEY,   -- ContentAddress over (observable, value, sigma, provenance, coverage-mask)
  observable      TEXT  NOT NULL,      -- ObservableRef serialization
  value           BLOB  NOT NULL,      -- typed payload (scalar, tensor, curve)
  sigma           REAL  NOT NULL,
  provenance      TEXT  NOT NULL,      -- JSON: { source, doi?, fetched-at, version }
  coverage_mask   BLOB  NOT NULL,      -- RoaringCoverageMask serialization (arch-16-pino-bridge §16.2.1)
  schema_version  INT   NOT NULL
)
```

- **Key construction.** `ContentAddress` over the canonical serialization
  of `(observable, value, sigma, provenance, coverage_mask)` (SHA-256
  backed, per `arch-20-representations §20.4`). Identical payloads
  collapse to one row; tampered payloads change the key and trip the
  obligation-8 freeze comparison.
- **Schema versioning.** `schema_version` bumps on any column add;
  readers refuse rows whose `schema_version` exceeds the linked-in
  schema, forcing an explicit migration step rather than silent drift.
- **Write discipline.** Write-once per key; updates produce a new row
  with a new key. Deletes are disallowed in the cert path; obsolete
  rows are tombstoned via `provenance.version`.
- **Why SQLite.** Single-file, ACID, no daemon, ubiquitous; WAL mode
  serves the read-heavy cert workload; scales from the MVP's
  ~10-row diamond battery to the long-tail target of ~10⁴ rows
  without infrastructure changes.

The cache is the only persistent component of `/physics`; everything
else is recomputed from the graph.

---

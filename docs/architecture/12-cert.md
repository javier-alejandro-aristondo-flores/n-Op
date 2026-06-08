---
id: arch-12-cert
title: Cert obligations
status: draft
revision: 1
canonical-for:
  - ten cert obligations
  - reference-cache backend
depends-on: []
referenced-by:
  - arch-16-pino-bridge
  - impl-09-cross-cutting
  - arch-19-coupling-structure
  - arch-20-representations
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
10. Adjoint-existence at registration (the gate of §11).

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

## 12.0.1 Coupling-derived simplifications (obligations 1, 5)

When a formula node originates from the invariant generator
(`arch-19-coupling-structure §19.3`), obligations 1 and 5 collapse to
projection-residual checks:

- **Obligation 1 (symmetry equivariance).** Invariants are
  trivial-irrep basis vectors by construction. Cert verifies the
  emitted `InvariantTerm.symbolic-form` lies in the claimed subspace:
  `||v − π_trivial v|| / ||v|| < ε` on a sampled evaluation. Failure
  is a generator bug, not a physics bug.
- **Obligation 5 (antisymmetry of L, PSD of M).** The
  `InvariantTerm.channel.target` tag determines the projection rule:
  `AntisymmForm` invariants project onto the antisymmetric component;
  `PSDSymmForm` invariants project onto the PSD cone. Cert verifies
  the emitted form equals its projection within `ε`.

Both checks are O(1) per invariant and run alongside the generator at
Stage 2.5.

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

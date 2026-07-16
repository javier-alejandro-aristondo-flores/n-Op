# Applicability Classifiers

Research stratum that seeded arch-13. It contributed the applicability-predicate concept
(`applicability : (Crystal, Environment) → Bool`, evaluated per-sample so the loss never
supervises a property the crystal doesn't admit), the 10-predicate example table — now
arch-13 §13.1, reconciled with the two-polar-predicate split — and the V1 masking rationale
(spurious supervision; loss-balance pathology).

Normative content: [arch-13-applicability]. The PINO-loss-mechanics discussion (GradNorm/NTK
weighting) was informed-operator territory and lives in
`informed-operator/design/residual-loss-methodology.md`'s domain.

## Changelog

- **2026-07-16 (strata rewrite):** example table and integration content migrated to arch-13
  §13.1 (2026-07 reconciliation, B4); this file shrunk to the pointer above. Original open
  questions (soft `[0,1]` classifiers; classifier composition under perturbation) carried into
  arch-13's deferred list.

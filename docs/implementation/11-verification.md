---
id: impl-11-verification
title: Verification
status: draft
revision: 1
canonical-for:
  - verification gates
depends-on: []
referenced-by: []
research-sources: []
---
# Verification

### 15.1 Internal consistency (static)

The spec is internally consistent when:

1. Every observable in §6 invokes only methods (§2), templates (§3), and
   registry formulas (§4) — no inline math, no ad-hoc combinators.
2. Every method/template/formula has a typed signature with no string-encoded
   parameters.
3. The directory tree (Phase 0) contains every concept named in this plan and in
   `architecture.md`.
4. The nine regime extractions (`arch-05-generic`) are realizable as the
   compositions in `impl-06-compositions`.
5. Every residual category (§7) is grounded in a GENERIC identity or a named
   formula.
6. Every cert obligation (§10) corresponds to a residual category or an algebraic
   identity, and maps to a Layer-0 axis.
7. The counts here match `arch-09-vocabularies` exactly (12 methods, 20 templates,
   110 formulas, 11 bundles, 19 residual categories, 10 cert obligations).

Once the Phase-0 skeleton exists, items 1–7 are checkable mechanically by walking
the tree and the registry manifest.

### 15.2 Runtime gates

Five sequential gates validate the built system:

1. **Registration sanity.** All 110 formulas instantiate as `ResidualGenerator`
   records without error; every D2 entry passes the registration-time adjoint
   gate (`impl-07-residual-factory §7.5`); every D4 entry carries an
   obligation-9 rationale; D0/D1 entries register without an adjoint (none
   needed).
2. **End-to-end worked example — Diamond–W Schottky at 500 °C.** Input: diamond
   bulk + W contact + Si substrate, `Environment(T = 773 K, field = 1 MV/cm)`.
   The DAG layers fire in order; the L3 ↔ non-equilibrium cycle (charge balance
   ↔ self-heating) closes via a same-pass fixed point in ≤ 5 iterations; roughly
   three dozen residuals fire and are accounted for in the cert manifest. Output:
   Schottky barrier, drift velocity, electron temperature, self-heating ΔT,
   predicted MTTF. The run completes within its declared cost budget and cert
   obligations 1, 2, 3, 5, 8 emit verdicts.
3. **Curriculum sanity (synthetic).** A three-phase training run on Si bulk
   (~5 observables, ~1k samples) completes without GradNorm divergence, without a
   Layer-3 ↔ non-equilibrium fixed-point failure, and without an adjoint-cert
   reset mid-training.
4. **Cross-regime cert obligations fire.** Obligation-6 (BTE-σ ≡ Kubo-σ on an
   equilibrium reference); obligation-9 (a D4 query outside its declared domain
   trips with a witness); obligation-10 (a synthetic D2 formula with a broken
   adjoint is refused at registration — loud, at build time); obligation-7
   (non-topological diamond emits NA with rationale; a contrived Z₂ system emits
   the predicted edge-state count).
5. **`/informed-operator` integration smoke test.** `Validate` with `gradient =
   Skip` populates label values for ~10 Si observables; `Validate` with
   `gradient = Compute` returns finite per-residual scalars and finite
   cotangents of the declared shape on a randomly-initialized state; `Import`
   accepts a synthetic VASP-formatted payload and returns `TargetEntry` records
   with coverage masks. All return within their typed contracts.

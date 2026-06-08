---
id: impl-09-cross-cutting
title: Cross-cutting design rules
status: draft
revision: 2
canonical-for:
  - cross-cutting rules
depends-on:
  - arch-08-bo-levels
  - arch-09-vocabularies
  - arch-11-residuals
  - arch-12-cert
  - arch-16-pino-bridge
  - arch-19-coupling-structure
  - impl-07-residual-factory
referenced-by: []
research-sources: []
---
# Cross-cutting design rules

These rules cut across formulas, methods, residuals, cert, and the
pino-bridge surface. They are not architectural decisions — those live in
`arch-*`. They are reusable patterns that show up in more than one place
in the implementation.

## 9.1 Method equivalence as a residual, not a path-selector

Several observables admit multiple formulas that should agree on their
shared domain (conductivity via BTE-RTA vs Kubo; thermal conductivity via
QHA+Callaway vs DFPT+3-phonon-BTE; effective mass from `k·p` vs DFT
band-curvature). The discipline under the always-cheap pipeline
(`arch-07-pipeline`) and the granularity rule (`arch-11-residuals`)
is:

- All applicable formulas for an observable are instantiated as
  `FormulaApply` nodes (`arch-06-physics-graph §6.2`); hash-consing
  collapses shared subgraphs.
- Equivalence is enforced via the `Algebraic/MethodEquivalence`
  residual category (`arch-11-residuals §11.1`), one `ResidualLeaf`
  per agreeing pair.
- Cert obligation 6 (`arch-12-cert`) consumes the
  `Algebraic/MethodEquivalence` leaf; if `|f₁ − f₂| > tolerance` it
  trips with both values as witnesses.
- The `Observable` output role (`arch-06-physics-graph §6.3`)
  designates which compose-time-selected formula is the *exposed*
  value to downstream consumers; selection is by `ContributionFacets`
  precedence (declared dressing tier, then registration order). The
  unselected formulas still contribute their residual leaves.

The architecture never averages observables and never silently selects
between formulas at runtime; both are exposed in the graph and the
disagreement is a typed residual.

## 9.2 Same-type → shared interpretation; type-change → explicit stage

Elements that are *parallel interpretations of one signature* — the 17
`CategoryTag`s (`arch-11-residuals §11.1`), the dressing tiers within L1
(`arch-08-bo-levels §8.1`), the 10 cert obligations
(`arch-12-cert`), source/dressing tags on `ContributionFacets`,
applicability guards (`arch-13-applicability`) — share one interface
with multiple handlers.

Elements that *compose into a pipeline with a type change between
stages* — the γ̂ encoding pipeline (`arch-15-gamma-hat`), the 4 BO
levels (`arch-08-bo-levels`), the 5-stage compose-time pipeline
(`arch-07-pipeline`), the synthesis → property → PINO layering — stay
explicit multi-stage structures.

Rule of thumb: same type ⇒ one interface, many handlers; type changes
between stages ⇒ keep the stages.

## 9.3 Provenance tags are not weighting axes

`ContributionFacets` (`arch-11-residuals §11.5`) attaches `(category,
bundle, dressing)` to every `ResidualLeaf` as a sidecar — purely
queryable provenance, never part of `ResidualKey` identity and never
the basis for a per-residual loss weight. Loss weighting lives in
`/informed-operator`'s curriculum schedule (`arch-11-residuals §11.4`),
keyed by `CategoryTag` participation gates only. A facet field exists
to answer "which residuals belong to bundle B?", not "what is the
weight of residual r?".

## 9.4 Couplings are declared channels; terms are generated

Cross-regime physics is not a hand-rolled list. The library author
declares `CouplingChannel` records (`arch-19-coupling-structure`),
each specifying `{pieces, target, order, derivative, applicability}`.
The Stage-2.5 invariant synthesizer takes the crystal's symmetry
group and the active channels and *generates* the explicit
`InvariantTerm`s — symmetry-respecting tensors that become
`FormulaApply` nodes in the graph. Adding a new physical regime
(piezoelectricity, magnon-phonon coupling, …) is a channel
declaration, not a code edit. Channels register through the same
factory pattern as residual generators (`impl-07-residual-factory §7.3`):
content-addressed by parameter tuple, applicability validated as
first-order decidable.

---

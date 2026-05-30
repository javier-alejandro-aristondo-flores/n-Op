# Applicability Classifiers

## Concept

Every property, observable, and residual in `/physics`'s closed registries carries an **applicability classifier** — a typed predicate over the crystal and environment:

```
applicability : (Crystal, Environment) → Bool
```

The classifier tells the PINO loss machinery whether a given training sample even *admits* the property in question. Properties that don't apply are masked out per-sample; they don't contribute to gradient updates and don't penalize the model for failing to predict something that isn't physically meaningful for that crystal.

This is what makes the architecture **compositional across crystal types**: the same `/physics` interface accepts diamond, GaN, AlN, c-BN, Ga₂O₃, AlGaN alloys, refractory contact metals — and each property's classifier figures out whether it's a meaningful question for the specific crystal in question.

## Examples

| Property | Applicability predicate | Notes |
|---|---|---|
| **Band gap** | `is-insulator-or-semiconductor(Crystal)` | Metals have no gap (or a closed gap); the property is undefined |
| **Magnetic moment per site** | `has-magnetic-order(Crystal)` | Non-magnetic systems have zero or fluctuating moments not corresponding to a physical observable |
| **Schottky barrier height** | `has-metal-semiconductor-interface(Crystal)` | Only meaningful for heterostructures with at least one metal and at least one semiconductor adjacent |
| **Defect formation energy for species X** | `defect-species-meaningful(X, Crystal)` | A boron substitutional in copper is not a meaningful "defect" the same way it is in diamond |
| **Superconducting Tc** | `is-superconductor(Crystal)` | The vast majority of materials are not superconducting; predicting a finite Tc for them is wrong, not noisy |
| **Polar-optical phonon scattering rate** | `is-polar-material(Crystal)` | Non-polar materials (like diamond) have no LO-TO splitting and no Fröhlich coupling |
| **Carbide formation rate at interface** | `interface-includes-carbide-former(Crystal)` | Pt/diamond never forms a carbide; Ti/diamond does |
| **Bulk modulus** | `is-three-dimensional-solid(Crystal)` | Layered materials (h-BN, graphene) have direction-dependent moduli; the scalar property is ill-defined |
| **Carrier mobility** | `is-conductor-or-semiconductor(Crystal)` | Wide-gap insulators at low T have effectively zero free carriers |
| **Thermal expansion coefficient (isotropic)** | `has-cubic-or-isotropic-symmetry(Crystal)` | Anisotropic crystals require a tensor; the scalar form is wrong |

## Type-system role

Each classifier is a **typed function** with explicit dependencies on Crystal and Environment fields. The registry compiles a per-property mask:

```
mask : (Crystal, Environment) × Registry → Bitmask[|registry|]
```

The PINO training loop reads the mask per-sample and zeros the loss contribution of any property where the predicate is false.

## Why this matters for V1

Without applicability classifiers, two failure modes appear:

1. **Spurious supervision** — the PINO is trained against "predicted band gap = X" for a metallic sample where the ground truth is "gap is meaningless." Either the label is zero (training the model to predict zero gap for metals, which is fine but uninformative) or the label is N/A (training is corrupted by missing-label noise). Both degrade learning.

2. **Loss-balance pathology** — observables that apply to many materials dominate the loss surface; observables that apply to few materials get zero gradient signal. GradNorm (outer balancing) doesn't help because the issue is per-sample, not per-source-family.

The classifier mask resolves both: every property contributes loss only on samples where it's defined; GradNorm balances across always-defined source families; per-property NTK-initialized inner weights account for varying applicability frequency.

## Open design questions

- **Classifier composition.** When a Crystal undergoes a perturbation that changes its classifier output (e.g., a structural phase transition closes a band gap), does the classifier evaluate against the *current* state or the *initial* state? Recommendation: current state, but with a hysteresis flag for trajectory-aware training.
- **Soft classifiers.** Some properties (deep-trap density, defect activation energy in a semi-insulating regime) have continuous applicability. A soft predicate `applicability : (Crystal, Env) → [0, 1]` might be more faithful for these. Defer to V2 — boolean classifier in V1 with explicit out-of-scope-when-marginal documentation.
- **Composite predicates.** When two properties have related applicability (e.g., Schottky barrier requires both `has-metal-semiconductor-interface` and `is-thermally-stable-at(T_op)`), should classifiers compose via logical AND or be flattened into a single per-property predicate? V1 recommendation: flatten; V2 may revisit.

## Integration with the residual-generator factory

The `ResidualGenerator` record gains an `applicability` slot:

```
ResidualGenerator {
  ...
  applicability : (Crystal, Environment) → Bool
  ...
}
```

The factory `make-residual-generator` reads the applicability predicate from the formula's metadata at registration time. The PINO training loop dispatches per-sample.

## Status

V1 commitment: every entry in the formula registry, every entry in the 11 observable bundles, and every applicable cert obligation gets an explicit `applicability` field. Stub predicates (always-true) are acceptable for V1.0; refinement happens incrementally as material-specific edge cases emerge from training.

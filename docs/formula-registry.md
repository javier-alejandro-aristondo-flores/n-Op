# n-Op — Formula Registry (index)

The closed registry of named formulas is the load-bearing contract between the
property machinery and the PINO. The canonical, machine-readable list is
[`../physics/library/formulas/registry-manifest.csv`](../physics/library/formulas/registry-manifest.csv).
This file is the human-readable index over it.

## What the registry is

Every algebraic combination in `/physics` invokes a **named formula** with a
typed signature and an explicit output type — no inline math, no string-encoded
expressions. Each formula is independently citable to published references and
independently verifiable by the cert sub-tree. New formulas enter only through a
controlled, cert-validated process; the registry is a contract, not a
convenience.

## Counts

- **102 substantive formulas** (rows 1–102).
- **2 architectural markers** (rows 103–104) for relations enforced *by
  construction* and therefore **not** residualized: force = −∇energy (an
  autodiff identity) and equivariance (a structural constraint). They appear in
  the manifest so the decision is recorded, not so they generate loss.

Of the substantive rows:

- **Rows 1–87** are grounded directly in the domain research under
  `physics/research/` (the observable catalog, heterostructure/CSP,
  defects/surfaces/interfaces, non-equilibrium/high-field, and the
  residual-generator catalog).
- **Rows 88–102** are the **linear-response and topology-atlas extensions**:
  the long-range Coulomb directional-limit correction, the charged-supercell
  finite-size schemes, the linear-response primitives (Born effective charges
  Z\*, high-frequency dielectric ε∞, electronic susceptibility χ∞, lattice
  Coulomb scalar), the composition-dependent excess-free-energy basis, and the
  topology atlas (symmetry-indicator group via Smith Normal Form, elementary
  band representations, compatibility relations, Chern / Z₂ / Wilson-loop
  invariants, boundary-mode multiplicity).

## Columns

The manifest is a CSV with one row per formula:

| Column | Meaning |
|---|---|
| `#` | Row number (stable identifier). |
| `Name` | Behavior-named identifier (person-attribution names appear only as parenthetical literature pointers). |
| `Signature` | Typed `(inputs) → output`, with units. |
| `Bundle` | Observable bundle membership, `B1`–`B11` (see `architecture.md §8.4`). |
| `Tier` | Cost tier `T0`–`T3`. |
| `Diff` | Differentiability tag `D0`–`D4`. |
| `Path` | `cheap` (approximate, for label generation) or `faithful` (physically accurate, for residual loss). |
| `Source` | Provenance: the research grounding, or "extension" / "topology atlas" for rows 88–102. |
| `Depends on` | Upstream formulas / primitives. |

## Tag legend

**Cost tiers** — `T0` closed-form (≤10 µs) · `T1` small linear algebra / 1D
quadrature (≤10 ms) · `T2` Brillouin-zone / mesh integral (≤10 s) · `T3`
self-consistent loop or PDE solve (≤10 min).

**Differentiability** — `D0` no autodiff needed (pure read) · `D1` analytic
forward derivative · `D2` adjoint required (validated at registration) · `D3`
implicit-function adjoint via fixed-point linearization · `D4` autodiff relaxed
(surrogate-net bridge or finite-difference fallback, approved at registration).

## How a formula becomes a residual

At library load time the residual-generator factory reads each formula record
and produces a `ResidualGenerator` (see `implementation-plan.md §8`). The tags
drive everything downstream: the cost tier sets sampling cadence, the
differentiability tag sets whether the residual is gradient-bearing and triggers
the registration-time adjoint gate for `D2` entries, the path selects
cheap-generate vs faithful-residual behavior, and the applicability classifier
masks the residual per training sample.

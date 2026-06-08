---
id: arch-19-coupling-structure
title: Coupling structure
status: draft
revision: 1
canonical-for:
  - CouplingChannel record
  - invariant-generator routine
  - coupling target shapes (Scalar | AntisymmForm | PSDSymmForm)
depends-on:
  - arch-04-state
  - arch-05-generic
  - arch-06-physics-graph
  - arch-07-pipeline
  - arch-09-vocabularies
  - arch-11-residuals
  - arch-12-cert
  - arch-13-applicability
  - impl-07-residual-factory
referenced-by:
  - impl-09-cross-cutting
  - impl-10-build-sequence
  - arch-20-representations
research-sources: []
---
# Coupling structure

Cross-regime physics — electron-phonon, spin-orbit, magneto-elastic,
minimal coupling, phonon-phonon scattering, radiative damping, … —
is one kind of object with a small parameter space, not a hand-rolled
list of named terms.

## 19.1 The object

A **coupling** is a symmetry-respecting function from a tensor product
of pieces of the state vector (`arch-04-state`) into one of three
target shapes:

- **`Scalar`** — a real-valued function; lands in `E_coupling`
  (`arch-05-generic §5`).
- **`AntisymmForm`** — an antisymmetric 2-form on the tangent bundle;
  lands as an off-diagonal block of `L` (`arch-05-generic §5`).
- **`PSDSymmForm`** — a positive-semidefinite symmetric 2-form on the
  cotangent bundle; lands as an off-diagonal kernel of `M`
  (`arch-05-generic §5`).

Every cross-regime term in `arch-05-generic` is one instance of this
object.

## 19.2 The parameter axes

```
record CouplingChannel {
  pieces        : List<StatePiece>            -- ordered tensor factors
  target        : Scalar | AntisymmForm | PSDSymmForm
  order         : Nat                         -- # tensor factors (typically 2..4)
  derivative    : Ultralocal | Gradient(Nat)  -- spatial-derivative depth
  applicability : (Crystal, Environment) → Bool
}

record StatePiece {
  component : StateComponent                  -- one of γ̂, A, R, P, h, Π_h, Z
  sub-dof   : SubDofTag                       -- orbital | spin | sublattice | valley
                                              -- | strain | gauge | charge | none
}
```

`StateComponent` is the existing 7-tuple alphabet (`arch-04-state`).
`SubDofTag` enumerates the internal labels a component carries:
γ̂ carries `orbital`, `spin`, and (when applicable) `sublattice`,
`valley`; `h` carries `strain`; `A` carries `gauge`; etc. The
allowed `(component, sub-dof)` pairs are tabulated alongside the
state-component definition.

`order` and `derivative` declare the truncation. They are not part of
the underlying physical structure; they are the compose-time choice of
how high in the multipole / multi-tensor expansion to go.

## 19.3 The invariant generator

```
generate-invariants : CrystalSymmetryGroup × CouplingChannel
                    → List<InvariantTerm>
```

Standard representation theory. Given the crystal's symmetry group
(`arch-09-vocabularies` lifts `CrystalSymmetryGroup` to a first-class
typeclass entity; Stage 2 already builds it from
`PeriodicityStructure × SiteDecoration`) and a channel specification,
this routine returns the finite basis of `target`-shaped
symmetry-invariant terms of the requested `order` and `derivative`.

Each `InvariantTerm` is a symbolic tensor expression carrying:

```
record InvariantTerm {
  channel         : CouplingChannel
  irrep-coefficients : IrrepCoefficientTable   -- the trivial-irrep coefficients
                                               -- of the underlying tensor product
  symbolic-form   : SymbolicTensor             -- the explicit term
  generator-hash  : Address[InvariantTerm]     -- domain-separated content address
}
```

The generator is the *constructive* direction of the irrep machinery
that Stage 2 already uses *decompositionally* (`arch-07-pipeline §7.2`
block-diagonalizes operators by irrep). Same module; same primitives;
new direction.

## 19.4 Worked example — diamond electron-phonon

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

At compose time:

1. **Stage 1** records the channel in `Stage1Sidecar.coupling-channels`.
2. **Stage 2** has already constructed the diamond symmetry group
   (Fd-3m + time-reversal).
3. **Stage 2.5** (new sub-stage, §19.5) runs
   `generate-invariants(Fd-3m+TR, electron-phonon)` and returns one
   `InvariantTerm`: the canonical `g_{nm,ν}(k,q)` matrix element
   written as a symmetry-respecting tensor.
4. **Stages 3–4** lower that `InvariantTerm` into a `FormulaApply`
   node attached to the `E_coupling` aggregator (a
   `MethodInvoke(hamiltonian-assemble, …)` node).

The author never wrote `g_{nm,ν}(k,q)`. The symmetry group did.

Spin-orbit, magneto-elastic, minimal coupling (γ̂ ↔ A), Stark, Zeeman,
phonon-phonon, radiative damping — each one is a `CouplingChannel`
record with a different parameter assignment. None of those strings
appears as a value in any enum.

## 19.5 Stage 2.5 — invariant synthesis

A new sub-stage in `arch-07-pipeline §7.2`, executed between Stage 2's
block-diagonalization rewrite and Stage 3's algebraic simplification.

```
Inputs  : Stage1Sidecar.coupling-channels  : List<CouplingChannel>
          CrystalSymmetryGroup             (constructed in Stage 1+2)
Action  : For each channel c whose c.applicability holds, compute
          generate-invariants(group, c); attach the returned
          List<InvariantTerm> to the channel.
Outputs : Stage2_5Sidecar.invariants : Map<CouplingChannel, List<InvariantTerm>>
```

Consumed by Stages 3–4 when lowering invariants into `FormulaApply`
nodes targeted at the existing `E_coupling`, `L_assembly`,
`M_assembly` aggregator methods.

## 19.6 Composition

- **Within a single `target`.** Invariants compose by direct sum:
  `E_coupling = Σ_{c} Σ_{v ∈ invariants[c] | v.target = Scalar} v.symbolic-form`,
  and analogously for the L and M target shapes.
- **Across `target` shapes.** Composition is the existing E / L / M
  assembly in `arch-05-generic`.
- **Order truncation is monotone.** Order-`(n+1)` includes order-`n`
  as a prefix; the spec author chooses the cutoff per channel.
- **No channel-correlation primitive in V1.** If two physical
  mechanisms genuinely correlate (a cross-term in `M` between two
  scattering processes that are not independent), they are modeled as
  *one* `CouplingChannel` with a larger tensor product (more `pieces`),
  not two channels with an extra correlation parameter. This keeps the
  V1 algebra additive.

## 19.7 Cert hooks

The invariant-generator structure simplifies two cert obligations
(`arch-12-cert`):

- **Obligation 1 (symmetry equivariance).** Invariants are
  trivial-irrep basis vectors *by construction*; equivariance is
  automatic. Cert reduces to a numerical projection-residual check:
  `||v.symbolic-form − π_trivial v.symbolic-form|| < ε` on a sampled
  evaluation. Failure indicates a generator bug, not a physics bug.
- **Obligation 5 (conservation / antisymmetry of L / PSD of M).**
  The `target` tag determines a projection rule applied at the
  generator step: `AntisymmForm` invariants are projected onto the
  antisymmetric component of the candidate tensor; `PSDSymmForm`
  invariants are projected onto the PSD cone. The projection is part
  of the generator's contract; cert numerically verifies the projected
  output matches the emitted `symbolic-form` within `ε`.

Both checks are O(1) per invariant; both are integrated with
`SymmetryAdaptedHamiltonianOf` (`arch-09-vocabularies §8.2`) which
already lives in the symmetry machinery.

## 19.8 Registration discipline

Channels register through the same factory pattern as residual
generators (`impl-07-residual-factory §7.3`):

```
make-coupling-channel(channel : CouplingChannel) → CouplingChannel
```

Returns the channel with its `applicability` validated as first-order
decidable on typeclass tags (the registration-time invariant from
`impl-04-formulas`). The channel's identity is `Address[CouplingChannel]`
under the canonical-serialization rule of `arch-20-representations §20.4`
(domain-separated, schema-versioned); identical channels collapse to one
address.

The set of *active* channels in a composition is the **`CouplingSpec`** —
a `SparseSet[CouplingRegistry]` (`arch-20-representations §20.3`) whose
identity is its Merkle root, carried alongside the existing composition
request (`arch-07-pipeline §7.1`). The diamond MVP's `CouplingSpec` is
short: electron-phonon + minimal coupling + ion-ion electrostatic +
phonon-phonon scattering (in M).

## 19.9 Open — coupling-channel template registry

The principled set of `CouplingChannel` *templates* covering the
physics regimes (~10 entries) — orbital-phonon, spin-orbit, spin-strain,
gauge-matter (minimal coupling), multipole-external-field
(Zeeman / Stark), ion-ion electrostatic, plus sub-DOF variants — is not
enumerated here. Tracked as an open decision in
`arch-18-open-decisions §7`. The actual `InvariantTerm`s are generated
by the Stage-2.5 synthesizer; the registry only lists which channels
to instantiate.

---

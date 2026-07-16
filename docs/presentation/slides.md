# Catch-Up Slides — `/physics`

Conventions:

- `CONSTANT_NAME` for values and variables.
- `FUNCTION_NAME()` for routines.
- `:=` for assignment.
- `==` for equality, `IS_NEAR_ZERO()` etc. for tolerance checks.

---

## Slide 1 — Setup

```
INPUTS:
    LATTICE      := PERIODICITY + WYCKOFF_DECORATION
    ENVIRONMENT  := { TEMPERATURE, PRESSURE, FIELD, ... }
    CONDITIONS   := jet_turbine_class()   // hot, high-field, cycled

GOAL:
    OPERATOR.predict_next_state(CURRENT_STATE) -> NEXT_STATE
```

A crystal under harsh conditions, with a multiphysics state that changes
over time. The goal is an operator that predicts the next state. Running
this forward with full DFT/MD at every step is too expensive, so something
cheaper is needed that still respects the physics.

---

## Slide 2 — Propose and check

```
TRADITIONAL:
    NEXT_STATE := SIMULATE(CURRENT_STATE, DT)        // expensive

PROPOSE_AND_CHECK:
    NEXT_STATE := PROPOSE(CURRENT_STATE)              // produced externally
    ASSERT( IS_CONSISTENT_WITH_LAWS(NEXT_STATE) )     // checked here
```

The question changes from "what does the lattice do next?" to "is this
candidate next state consistent with the laws?". Producing a next state
is harder than checking one.

---

## Slide 3 — State

```
STATE := {
    CELL_VECTORS,         // shape of the box
    ION_POSITIONS,
    ION_MOMENTA,
    CELL_MOMENTUM,        // box can deform
    SPECIES_LABELS,       // immutable
    DENSITY_MATRIX,       // ELECTRON_STATE
    EM_POTENTIAL,
}
```

These are the irreducible degrees of freedom. Vibrations, carrier
distributions, lattice temperatures, and currents are emergent —
coarse-grainings, semiclassical limits, or averages over the irreducible
state:

```
EMERGENT_PHONONS    := COARSE_GRAIN(ION_POSITIONS, ION_MOMENTA)
EMERGENT_CARRIERS   := SEMICLASSICAL_LIMIT(DENSITY_MATRIX)
EMERGENT_TEMPERATURE := AVERAGE_OVER(MOMENTA)
```

Storing them as part of the state would force constraint manifolds back
to the irreducible variables and undo the savings.

---

## Slide 4 — ELECTRON_STATE storage

The dense one-body density matrix is `O(N_R * N_R)`, hundreds of MB per
snapshot. Stored as orbitals it drops by roughly 25x:

```
NAIVE:    SIZE(DENSE_ELECTRON_STATE)        // ~460 MB per k-mesh
ACTUAL:   SIZE(ELECTRON_STATE_AS_ORBITALS)  // ~18 MB per k-mesh
```

And every measurement of `ELECTRON_STATE` returns a much smaller object:

```
MEASURE_DENSITY(ELECTRON_STATE)         -> Field         // small
MEASURE_BAND_STRUCTURE(ELECTRON_STATE)  -> BandSet       // small
MEASURE_ENERGY(ELECTRON_STATE)          -> Scalar        // tiny
```

So the dense form is never built. The encoding keeps cheap views and
requires them to agree.

---

## Slide 5 — Views

Each view is a change of representation chosen by the sub-problem:

```
ELECTRON_STATE_PERIODIC_VIEW    := AS_PERIODIC_VIEW(ELECTRON_STATE)     // periodic bulk
ELECTRON_STATE_POSITION_VIEW    := AS_POSITION_VIEW(ELECTRON_STATE)     // defects, surfaces
ELECTRON_STATE_LOCALIZED_VIEW   := AS_LOCALIZED_VIEW(ELECTRON_STATE)    // interfaces, dangling bonds
ELECTRON_STATE_LOW_RANK_VIEW    := AS_LOW_RANK_VIEW(ELECTRON_STATE)     // low-rank screening
ELECTRON_STATE_SYMMETRY_VIEW    := AS_SYMMETRY_VIEW(ELECTRON_STATE)     // quotient by space group
```

Transcoders move between views; the views and transcoders form a small
diagram.

---

## Slide 6 — Pullback

Every view has to give the same answer to the same physical query:

```
                       STATE
                      /     \
           AS_PERIODIC_VIEW()   AS_POSITION_VIEW()
                      \     /
                       v   v
            CHARGE_DENSITY := MEASURE_DENSITY(...)
```

```
DENSITY_VIA_PERIODIC_VIEW := MEASURE_DENSITY( AS_PERIODIC_VIEW(STATE) )
DENSITY_VIA_POSITION_VIEW := MEASURE_DENSITY( AS_POSITION_VIEW(STATE) )

ASSERT( DENSITY_VIA_PERIODIC_VIEW == DENSITY_VIA_POSITION_VIEW )
```

The object that sits above every view, forced to agree through every
measurement, is what category theory calls a pullback.

---

## Slide 7 — Residual

Same shape as the previous slide, different labels. One leg goes through
the law, the other through the state. The gap between them is the
residual:

```
                     CANDIDATE
                    /         \
            APPLY_LAW()       READ_FROM_STATE()
                    \         /
                     v       v
       PREDICTED_DENSITY    OBSERVED_DENSITY
                     \      /
                      v    v
              RESIDUAL := DIFF(PREDICTED, OBSERVED)

              ASSERT( IS_NEAR_ZERO(RESIDUAL) )
```

```
PREDICTED := APPLY_LAW(CANDIDATE)         // what the law gives for this candidate
OBSERVED  := READ_FROM_STATE(CANDIDATE)   // what the candidate's own values give

RESIDUAL  := DIFF(PREDICTED, OBSERVED)
ASSERT( IS_NEAR_ZERO(RESIDUAL) )
```

A few examples in this form:

```
// Charge continuity
ASSERT( IS_NEAR_ZERO( DIFF(
    APPLY_CONTINUITY_LAW(CANDIDATE),
    READ_DENSITY_RATE(CANDIDATE)
)))

// Translation invariance
ASSERT( IS_NEAR_ZERO(
    SUM_OVER_FORCE_CONSTANTS( READ_FORCE_CONSTANT_MATRIX(CANDIDATE) )
))

// Mechanical stability
ASSERT( IS_POSITIVE_DEFINITE( READ_STIFFNESS_TENSOR(CANDIDATE) ))
```

Each one is a single check on a candidate. None of them runs a trajectory.

---

## Slide 8 — Cost

```
SIMULATION:
    PREDICTED := INTEGRATE_LAWS_FORWARD( INITIAL_STATE, T_LONG )
    // many steps, full evolution

RESIDUAL:
    PREDICTED := APPLY_LAW( CANDIDATE )
    // one call, on a single candidate
```

Both produce a value of the same type. Simulation arrives at it through
full integration; the residual reaches it with a single call to
`APPLY_LAW` and compares. The check lives in a small output (a scalar,
a field, a band structure); the simulation that would produce the same
output is many times larger.

```
SIZE( DENSE_ELECTRON_STATE   )  ==  460 MB    // would-be simulation footprint
SIZE( ORBITAL_ELECTRON_STATE )  ==   18 MB    // actual encoded size
RATIO                           ==  ~25x
```

The same gap shows up between running a kinetic transport solve and
checking detailed balance: same physics, very different cost.

---

## Slide 9 — Residual metadata

Each residual published by `/physics` carries metadata describing what it
costs and how its derivative is delivered:

```
RESIDUAL := {
    NAME,
    SIGNATURE     : (CANDIDATE) -> Scalar,
    COST_TIER     : T0 | T1 | T2 | T3,    // per-step / per-batch / per-epoch / on-demand
    DIFF_TAG      : D0 | D1 | D2 | D3 | D4, // closed-form / native / adjoint / finite-diff / non-diff
    BUNDLE        : B1..B11,
}
```

Two example partitions over the same catalog:

```
CHEAP_AND_FAST := [                       // T0, closed-form
    TRANSLATION_INVARIANCE_CHECK,
    DIFFUSION_MOBILITY_LINK,
    MECHANICAL_STABILITY_CHECK,
    POSITIVITY_OF_DENSITY,
    ENERGY_OPERATOR_REAL_VALUED,
]

EXPENSIVE_AND_FAITHFUL := [               // T2-T3, kinetic/many-body
    FAITHFUL_VIBRATION_SPECTRUM,
    FAITHFUL_TRANSPORT_CONDUCTIVITY,
    FAITHFUL_BAND_GAP_CORRECTION,
]
```

How a consumer schedules these — every step, periodically, on demand —
is the consumer's choice. `/physics` only publishes the residuals and
their tags.

---

## Slide 10 — API

`/physics` exposes a contract, not a training set:

```
PHYSICS_API := {
    STATE_TYPE          : <the 7-field struct>,
    RESIDUAL_CATALOG    : List[Residual],         // each tagged per slide 9
    PULLBACK_CHECK      : (STATE) -> Bool,        // views agree
    METADATA            : { COST_TIER, DIFF_TAG, BUNDLE, ... },
}

VALID_STATE_PREDICATE := (STATE) ->
    all( IS_NEAR_ZERO( R(STATE) ) for R in RESIDUAL_CATALOG )
```

The library defines what a valid state is and gives a way to test
candidates. How candidates are produced and how the test is used
downstream are the consumer's choices.

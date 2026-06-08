# The Pullback Diagram (CS Pseudocode Style)

One picture, two readings. No math symbols — everything as algorithm names,
function calls, and assignments.

## Convention

- `CONSTANT_NAME` — a value or variable.
- `FUNCTION_NAME()` — a routine that returns a value.
- `:=` — assignment.
- `==` — value equality (in assertions).
- `ASSERT(...)` — what must hold.

---

## Reading 1 — Slide 6 (γ̂ across bases must agree)

The same physical object, asked the same question through two different
bases, must give the same answer.

```
                       STATE
                      /     \
           AS_PERIODIC_VIEW()   AS_POSITION_VIEW()
                      \     /
                       \   /
                        v v
            CHARGE_DENSITY := MEASURE_DENSITY(...)
```

Read as code:

```
STATE := <candidate snapshot>

ELECTRON_STATE_PERIODIC_VIEW := AS_PERIODIC_VIEW(STATE)
ELECTRON_STATE_POSITION_VIEW := AS_POSITION_VIEW(STATE)

DENSITY_VIA_PERIODIC_VIEW := MEASURE_DENSITY(ELECTRON_STATE_PERIODIC_VIEW)
DENSITY_VIA_POSITION_VIEW := MEASURE_DENSITY(ELECTRON_STATE_POSITION_VIEW)

ASSERT( DENSITY_VIA_PERIODIC_VIEW == DENSITY_VIA_POSITION_VIEW )
```

The two paths down through the diagram are different *implementations* of
the same logical query. Forcing them to agree is the **pullback condition**.

---

## Reading 2 — Slide 7 (residual = same shape, relabeled)

Now the two arrows are not "two bases" but "two ways of computing what the
observable should be":

- one path goes through the **law** (what physics predicts for this
  observable, given the candidate);
- one path goes through the **state** (what the candidate's own values
  evaluate to).

```
                     CANDIDATE
                    /         \
            APPLY_LAW()       READ_FROM_STATE()
                    \         /
                     \       /
                      v     v
       PREDICTED_DENSITY    OBSERVED_DENSITY
                      \     /
                       \   /
                        v v
              RESIDUAL := DIFF(PREDICTED, OBSERVED)

              ASSERT( IS_NEAR_ZERO(RESIDUAL) )
```

Read as code:

```
CANDIDATE := <proposed next state under test>

PREDICTED_DENSITY := APPLY_LAW(CANDIDATE)        // continuity, GENERIC, etc.
OBSERVED_DENSITY  := READ_FROM_STATE(CANDIDATE)  // direct measurement

RESIDUAL := DIFF(PREDICTED_DENSITY, OBSERVED_DENSITY)

ASSERT( IS_NEAR_ZERO(RESIDUAL) )
```

Same picture as reading 1 — two arrows down to the same observable, with the
requirement that they agree. Only the labels change.

---

## Why this is the whole point

Running a full simulation = **building** `PREDICTED_DENSITY` step by step,
all the way from initial conditions, integrating the laws forward.

Running the residual check = **calling** `APPLY_LAW(CANDIDATE)` once on the
candidate under test and comparing to `READ_FROM_STATE(CANDIDATE)`.

```
SIMULATION:    PREDICTED := INTEGRATE_LAWS_FORWARD(INITIAL_STATE, T_LONG)
                            // expensive: many steps, full state evolution

RESIDUAL:      PREDICTED := APPLY_LAW(CANDIDATE)
                            // cheap: one call, returns the same observable
```

Both produce a value of type `Density`. The simulation builds it; the
residual just checks it. That's where the speedup lives.

---

## Slide-7 examples (drop-in residuals)

Same shape, different `APPLY_LAW` / `READ_FROM_STATE` pairs:

```
// Charge continuity
ASSERT( IS_NEAR_ZERO(
    DIFF( APPLY_CONTINUITY_LAW(CANDIDATE), READ_DENSITY_RATE(CANDIDATE) )
) )

// Translation invariance (vibration)
ASSERT( IS_NEAR_ZERO(
    SUM_OVER_FORCE_CONSTANTS( READ_FORCE_CONSTANT_MATRIX(CANDIDATE) )
) )

// Mechanical stability (mechanics)
ASSERT( IS_POSITIVE_DEFINITE(
    READ_STIFFNESS_TENSOR(CANDIDATE)
) )
```

Each one is a one-liner check on a candidate. None of them requires running
a trajectory.

---

## Open choice (still to confirm)

The bottom-of-diagram observable. Currently `CHARGE_DENSITY` is used because
it threads slides 6 and 7 with the same observable. Alternatives:

- `TOTAL_ENERGY` — universal scalar, recomputed from every basis.
- `BAND_GAP` — small object, easy to compare across bases.

Recommend keeping `CHARGE_DENSITY` so the picture recurs identically across
slides 6 and 7, only the side labels changing.

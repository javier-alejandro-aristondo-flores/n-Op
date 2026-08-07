"""Prediction intervals with a finite-sample coverage guarantee.

Split conformal prediction: hold out a calibration set, measure the distribution of
absolute residuals on it, and take the appropriate quantile as the half-width. Under
exchangeability the resulting interval covers the truth with the nominal probability, for
*any* underlying model and *any* sample size -- no distributional assumption, no asymptotics.
That is the property worth having at n = 1,131, where an asymptotic interval would be a
guess.

## Exchangeability is the thing that can break, and here it would

The guarantee needs the calibration points and the test point to be exchangeable. This
corpus violates that in a specific, known way: a shape and its 47 octahedral images are the
*same calculation*, so a calibration set containing one image of a test shape is not
exchangeable with it -- it contains the answer. The residual would look far smaller than it
is and the interval would be too narrow, silently.

So calibration folds are **orbit-grouped**, like every other split in this library. Whole
orbits go into calibration or into fitting, never across. That is the same correction the
grouped cross-validation needed, for the same reason, and `symmetry.py` records why the
labeler had to be fixed before it was true.

## Ensembles supply the score; conformal supplies the guarantee

A deep ensemble gives an epistemic signal -- where its members disagree, the prediction is
uncertain -- but its spread is not calibrated and does not become calibrated by being
averaged. So the ensemble is pooled first and conformal is applied to the pooled predictor
("pool then calibrate"), leaving conformal as the sole source of the coverage claim.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import locations  # noqa: F401


@dataclass(frozen=True)
class Interval:
    """A conformal half-width and the coverage it was calibrated for."""

    half_width: float
    nominal: float
    calibration_size: int

    def around(self, prediction: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return prediction - self.half_width, prediction + self.half_width


def calibrate(residuals: np.ndarray, nominal: float = 0.90) -> Interval:
    """The split-conformal half-width from calibration residuals.

    The quantile index is `ceil((n + 1) * nominal) / n`, not simply `nominal`. The finite-
    sample correction is what makes the guarantee exact rather than approximate, and at
    n = 200 it is worth about half a percent of coverage -- small, but the whole point of
    using conformal is that the guarantee is not approximate.
    """
    residuals = np.asarray(residuals, dtype=float)
    n = len(residuals)
    if n < 20:
        raise ValueError(f"{n} calibration points is too few for a 90% interval")
    level = min(np.ceil((n + 1) * nominal) / n, 1.0)
    return Interval(half_width=float(np.quantile(residuals, level)),
                    nominal=nominal, calibration_size=n)


def empirical_coverage(prediction: np.ndarray, truth: np.ndarray,
                       interval: Interval) -> float:
    low, high = interval.around(prediction)
    return float(np.mean((truth >= low) & (truth <= high)))


def split_by_orbit(orbit: np.ndarray, index: np.ndarray, fraction: float = 0.25,
                   seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Divide an index into fitting and calibration parts, keeping orbits whole.

    Orbits are shuffled and taken until the calibration share is reached, rather than taking
    the first ones: `GroupKFold` is unshuffled and would correlate the calibration set with
    whatever order the corpus happens to be in.
    """
    generator = np.random.default_rng(seed)
    orbits = np.unique(orbit[index])
    generator.shuffle(orbits)

    wanted = int(round(fraction * len(index)))
    chosen, taken = [], 0
    for label in orbits:
        if taken >= wanted:
            break
        chosen.append(label)
        taken += int((orbit[index] == label).sum())

    mask = np.isin(orbit[index], chosen)
    return index[~mask], index[mask]


def ensemble_mean(predictions: list[np.ndarray]) -> np.ndarray:
    """Pool an ensemble before calibrating it, never after."""
    return np.mean(np.stack(predictions, axis=0), axis=0)


def ensemble_spread(predictions: list[np.ndarray]) -> np.ndarray:
    """Member disagreement -- an epistemic signal, and explicitly not a calibrated one."""
    return np.std(np.stack(predictions, axis=0), axis=0, ddof=1)


if __name__ == "__main__":
    # Calibrate the calibrator. A coverage claim from a routine nobody has watched fail is
    # not evidence, so this checks the guarantee holds on data built to a known answer and
    # that it *breaks* in the way theory says when exchangeability is violated.
    from corpus import load

    generator = np.random.default_rng(0)
    corpus = load()

    truth = generator.normal(size=4000)
    prediction = truth + generator.normal(scale=0.3, size=4000)
    fit_part, calibration_part = np.arange(3000), np.arange(3000, 4000)
    interval = calibrate(np.abs(prediction - truth)[calibration_part])
    coverage = empirical_coverage(prediction[fit_part], truth[fit_part], interval)
    print(f"synthetic, exchangeable: half-width {interval.half_width:.4f}, "
          f"coverage {coverage:.3f} (nominal 0.900)")
    assert 0.87 <= coverage <= 0.93, "the calibrator does not deliver nominal coverage"

    # The probe that must fire: calibrate on residuals that are systematically smaller than
    # the test ones, as leakage through symmetry images would make them, and confirm
    # coverage collapses. If this passes, the guarantee is not measuring anything.
    optimistic = calibrate(np.abs(prediction - truth)[calibration_part] * 0.3)
    broken = empirical_coverage(prediction[fit_part], truth[fit_part], optimistic)
    print(f"leakage probe (calibration residuals shrunk 3.3x): coverage {broken:.3f}")
    assert broken < 0.80, "the coverage check cannot detect an over-narrow interval"

    fitting, calibration = split_by_orbit(corpus.orbit, np.arange(len(corpus)))
    shared = set(corpus.orbit[fitting]) & set(corpus.orbit[calibration])
    print(f"\norbit-grouped calibration split: {len(fitting)} fit, "
          f"{len(calibration)} calibrate, {len(shared)} orbits shared")
    assert not shared, "an orbit straddles the calibration boundary"
    print("calibration passed -- both probes fire, and no orbit straddles the split")

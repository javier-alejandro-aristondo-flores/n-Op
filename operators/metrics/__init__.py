"""comparison metrics, field errors and curve distances and unit-level aggregates"""

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

type Field = NDArray[np.float64] | NDArray[np.float32]


def Relative_L2(prediction: Field, truth: Field) -> float:
    """the L2 error divided by the L2 size of the truth"""
    difference = np.asarray(prediction, dtype=np.float64) - np.asarray(truth, dtype=np.float64)
    return float(np.linalg.norm(difference.ravel()) / np.linalg.norm(np.asarray(truth, dtype=np.float64).ravel()))


def Mean_Squared_Error(prediction: Field, truth: Field) -> float:
    """the mean squared difference"""
    difference = np.asarray(prediction, dtype=np.float64) - np.asarray(truth, dtype=np.float64)
    return float(np.mean(difference * difference))


def Masked_Mean_Squared_Error(prediction: Field, truth: Field, mask: NDArray[np.bool_]) -> float:
    """the mean squared difference over the entries the mask selects"""
    selected = np.asarray(mask, dtype=np.bool_)
    if not bool(selected.any()):
        raise ValueError("a completion loss needs at least one hidden entry to score")
    difference = (np.asarray(prediction, dtype=np.float64) - np.asarray(truth, dtype=np.float64))[selected]
    return float(np.mean(difference * difference))


def Mean_Absolute_Error(prediction: Field, truth: Field) -> float:
    """the mean absolute difference"""
    difference = np.asarray(prediction, dtype=np.float64) - np.asarray(truth, dtype=np.float64)
    return float(np.mean(np.abs(difference)))


def Normalized_Mean_Absolute_Error(prediction: Field, truth: Field) -> float:
    """the mean absolute error divided by the mean absolute truth"""
    truth_values = np.asarray(truth, dtype=np.float64)
    return float(Mean_Absolute_Error(prediction, truth) / np.mean(np.abs(truth_values)))


def Mean_Removed_Relative_L2(prediction: Field, truth: Field) -> float:
    """relative L2 error after each field loses its own spatial mean"""
    prediction_values = np.asarray(prediction, dtype=np.float64)
    truth_values = np.asarray(truth, dtype=np.float64)
    return Relative_L2(prediction_values - prediction_values.mean(), truth_values - truth_values.mean())


def Mean_Removed_Mean_Squared_Error(prediction: Field, truth: Field) -> float:
    """mean squared error after each field loses its own spatial mean"""
    prediction_values = np.asarray(prediction, dtype=np.float64)
    truth_values = np.asarray(truth, dtype=np.float64)
    return Mean_Squared_Error(prediction_values - prediction_values.mean(), truth_values - truth_values.mean())


def Mean_Removed_Mean_Absolute_Error(prediction: Field, truth: Field) -> float:
    """mean absolute error after each field loses its own spatial mean"""
    prediction_values = np.asarray(prediction, dtype=np.float64)
    truth_values = np.asarray(truth, dtype=np.float64)
    return Mean_Absolute_Error(prediction_values - prediction_values.mean(), truth_values - truth_values.mean())


def Mean_Discrepancy(prediction: Field, truth: Field) -> float:
    """how far the prediction's spatial mean sits from the truth's, signed"""
    prediction_mean = float(np.mean(np.asarray(prediction, dtype=np.float64)))
    return prediction_mean - float(np.mean(np.asarray(truth, dtype=np.float64)))


def Delta_Mean_Squared_Error(prediction: Field, truth: Field, cheap_input: Field) -> float:
    """squared error over the squared error the cheap input already carried"""
    identity_error = Mean_Squared_Error(cheap_input, truth)
    if identity_error <= 0.0:
        raise ValueError("the cheap input already equals the truth, so there is no correction to score")
    return Mean_Squared_Error(prediction, truth) / identity_error


def Delta_R_Squared(prediction: Field, truth: Field, cheap_input: Field) -> float:
    """the share of the correction's squared size the prediction explains"""
    return 1.0 - Delta_Mean_Squared_Error(prediction, truth, cheap_input)


def Mean_Squared_Error_With_Moment_Normalized_Magnetization(
    predicted_density: Field,
    truth_density: Field,
    predicted_magnetization: Field | None = None,
    truth_magnetization: Field | None = None,
    absolute_moment: float | None = None,
) -> float:
    """the density error plus the magnetization error divided by the run's own absolute moment squared"""
    density_error = Mean_Squared_Error(predicted_density, truth_density)
    # a spin-restricted run carries no magnetization channel, and the term is masked away
    if predicted_magnetization is None or truth_magnetization is None:
        return density_error
    if absolute_moment is None or absolute_moment <= 0.0:
        raise ValueError("the magnetization term needs the run's own integrated absolute moment")
    magnetization_error = Mean_Squared_Error(predicted_magnetization, truth_magnetization)
    return density_error + magnetization_error / (absolute_moment * absolute_moment)


def Mode_Radius_Grid(shape: tuple[int, ...]) -> NDArray[np.float64]:
    """the integer-mode radius at every real-transform output entry"""
    axes = [np.minimum(np.arange(extent), extent - np.arange(extent)) for extent in shape[:-1]]
    # the real transform keeps only half of the last axis, and it starts at zero
    axes.append(np.arange(shape[-1] // 2 + 1))
    grids = np.meshgrid(*axes, indexing="ij")
    return np.sqrt(sum(np.asarray(grid, dtype=np.float64) ** 2 for grid in grids))


def Frequency_Split_Relative_L2(prediction: Field, truth: Field, cutoff_modes: float) -> tuple[float, float]:
    """relative L2 error of the below-cutoff and above-cutoff mode bands"""
    prediction_modes = np.fft.rfftn(np.asarray(prediction, dtype=np.float64))
    truth_modes = np.fft.rfftn(np.asarray(truth, dtype=np.float64))
    radius = Mode_Radius_Grid(np.asarray(prediction).shape)
    below_cutoff = radius <= cutoff_modes

    def Band_Error(mask: NDArray[np.bool_]) -> float:
        """the masked band's relative L2 error, in spectral form"""
        difference = np.linalg.norm((prediction_modes - truth_modes)[mask])
        size = np.linalg.norm(truth_modes[mask])
        return float(difference / size) if size > 0 else 0.0

    return Band_Error(below_cutoff), Band_Error(~below_cutoff)


def Periodic_Box_Mean(values: NDArray[np.float64], window: int) -> NDArray[np.float64]:
    """the periodic moving average over a cubic window, by circular convolution"""
    spectrum = np.fft.rfftn(values)
    # one axis at a time, since a box window is the product of its per-axis windows
    for axis, extent in enumerate(values.shape):
        kernel = np.zeros(extent, dtype=np.float64)
        # the window is centered by wrapping its left half around to the end
        offsets = (np.arange(window) - window // 2) % extent
        kernel[offsets] = 1.0 / window
        kernel_modes = np.fft.rfft(kernel) if axis == values.ndim - 1 else np.fft.fft(kernel)
        shape = [1] * values.ndim
        shape[axis] = kernel_modes.shape[0]
        spectrum = spectrum * kernel_modes.reshape(shape)
    return np.fft.irfftn(spectrum, s=values.shape, axes=tuple(range(values.ndim)))


def Structural_Similarity_3d(prediction: Field, truth: Field, window: int = 7, data_range: float = 1.0) -> float:
    """mean three-dimensional structural similarity over periodic windows"""
    first_field = np.asarray(prediction, dtype=np.float64)
    second_field = np.asarray(truth, dtype=np.float64)
    # the stabilizers keep the ratio finite where a window is flat
    stabilizer_one = (0.01 * data_range) ** 2
    stabilizer_two = (0.03 * data_range) ** 2
    mean_one = Periodic_Box_Mean(first_field, window)
    mean_two = Periodic_Box_Mean(second_field, window)
    # variance as the mean of squares less the square of the mean, per window
    variance_one = Periodic_Box_Mean(first_field * first_field, window) - mean_one * mean_one
    variance_two = Periodic_Box_Mean(second_field * second_field, window) - mean_two * mean_two
    covariance = Periodic_Box_Mean(first_field * second_field, window) - mean_one * mean_two
    numerator = (2 * mean_one * mean_two + stabilizer_one) * (2 * covariance + stabilizer_two)
    denominator = (mean_one**2 + mean_two**2 + stabilizer_one) * (variance_one + variance_two + stabilizer_two)
    return float(np.mean(numerator / denominator))


def Curve_L1(prediction: NDArray[np.float64], truth: NDArray[np.float64], spacing: float) -> float:
    """integrated absolute curve difference, over the truth's own integral"""
    difference = float(np.sum(np.abs(prediction - truth)) * spacing)
    size = float(np.sum(np.abs(truth)) * spacing)
    return difference / size


def Wasserstein_1d(prediction: NDArray[np.float64], truth: NDArray[np.float64], spacing: float) -> float:
    """the one-dimensional transport distance between unit-mass curves"""
    first_field = prediction / (np.sum(prediction) * spacing)
    second_field = truth / (np.sum(truth) * spacing)
    # in one dimension the transport cost is the area between the cumulative curves
    cumulative_gap = np.cumsum(first_field - second_field) * spacing
    return float(np.sum(np.abs(cumulative_gap)) * spacing)


def Gap_Edge_Energies(
    curve: NDArray[np.float64],
    energies: NDArray[np.float64],
    gap_reference: float = 0.0,
    support_fraction: float = 0.01,
) -> tuple[float, float]:
    """the energies where a state-density curve's support ends below and resumes above the gap"""
    carried = np.asarray(curve, dtype=np.float64)
    peak = float(carried.max())
    if peak <= 0.0:
        raise ValueError("a curve with no positive support anywhere has no band edges to read")
    supported = carried >= support_fraction * peak
    occupied_side = np.asarray(energies, dtype=np.float64)[supported & (energies <= gap_reference)]
    empty_side = np.asarray(energies, dtype=np.float64)[supported & (energies >= gap_reference)]
    if occupied_side.size == 0 or empty_side.size == 0:
        raise ValueError("a curve with no support on one side of the reference has no band edge there")
    return float(occupied_side.max()), float(empty_side.min())


def Gap_Edge_Error(
    prediction: NDArray[np.float64],
    truth: NDArray[np.float64],
    energies: NDArray[np.float64],
    gap_reference: float = 0.0,
    support_fraction: float = 0.01,
) -> float:
    """how far the predicted curve puts the two band edges, averaged over the pair"""
    predicted_valence, predicted_conduction = Gap_Edge_Energies(prediction, energies, gap_reference, support_fraction)
    true_valence, true_conduction = Gap_Edge_Energies(truth, energies, gap_reference, support_fraction)
    return 0.5 * (abs(predicted_valence - true_valence) + abs(predicted_conduction - true_conduction))


def Fraction_Within(errors: NDArray[np.float64], tolerance: float) -> float:
    """the fraction of absolute errors at or below the tolerance"""
    return float(np.mean(np.abs(errors) <= tolerance))


def Median_Per_Unit(values: NDArray[np.float64], unit_keys: Sequence[str]) -> NDArray[np.float64]:
    """each exchangeable unit's own median, so copies inside one unit count once"""
    by_unit: dict[str, list[float]] = {}
    for value, unit_key in zip(values, unit_keys):
        by_unit.setdefault(unit_key, []).append(float(value))
    return np.asarray([float(np.median(carried)) for _, carried in sorted(by_unit.items())], dtype=np.float64)


def Median_And_Interquartile(values: NDArray[np.float64]) -> tuple[float, float]:
    """the median and the interquartile range"""
    lower, median, upper = np.percentile(values, [25.0, 50.0, 75.0])
    return float(median), float(upper - lower)


def Bootstrap_Confidence_Interval(
    values: NDArray[np.float64],
    draws: int = 2000,
    coverage: float = 0.95,
    seed: int = 20260828,
) -> tuple[float, float]:
    """a percentile bootstrap interval for the mean over exchangeable units"""
    generator = np.random.default_rng(seed)
    # resampling the units with replacement, one row per draw
    samples = generator.choice(values, size=(draws, values.shape[0]), replace=True)
    means = samples.mean(axis=1)
    tail = 100.0 * (1.0 - coverage) / 2.0
    lower_bound, upper_bound = np.percentile(means, [tail, 100.0 - tail])
    return float(lower_bound), float(upper_bound)

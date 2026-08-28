"""Comparison metrics: field errors, curve distances, and unit-level aggregates."""

import numpy as np
from numpy.typing import NDArray

type Field = NDArray[np.float64] | NDArray[np.float32]


def Relative_L2(prediction: Field, truth: Field) -> float:
    """Returns the L2 error divided by the L2 size of the truth."""
    difference = np.asarray(prediction, dtype=np.float64) - np.asarray(truth, dtype=np.float64)
    return float(np.linalg.norm(difference.ravel()) / np.linalg.norm(np.asarray(truth, dtype=np.float64).ravel()))


def Mean_Absolute_Error(prediction: Field, truth: Field) -> float:
    """Returns the mean absolute difference."""
    difference = np.asarray(prediction, dtype=np.float64) - np.asarray(truth, dtype=np.float64)
    return float(np.mean(np.abs(difference)))


def Normalized_Mean_Absolute_Error(prediction: Field, truth: Field) -> float:
    """Returns the mean absolute error divided by the mean absolute truth."""
    truth_values = np.asarray(truth, dtype=np.float64)
    return float(Mean_Absolute_Error(prediction, truth) / np.mean(np.abs(truth_values)))


def Mean_Removed_Relative_L2(prediction: Field, truth: Field) -> float:
    """Returns the relative L2 error after removing each field's own spatial mean."""
    prediction_values = np.asarray(prediction, dtype=np.float64)
    truth_values = np.asarray(truth, dtype=np.float64)
    return Relative_L2(prediction_values - prediction_values.mean(), truth_values - truth_values.mean())


def Mode_Radius_Grid(shape: tuple[int, ...]) -> NDArray[np.float64]:
    """Returns the integer-mode radius at every rfftn output entry."""
    axes = [np.minimum(np.arange(extent), extent - np.arange(extent)) for extent in shape[:-1]]
    axes.append(np.arange(shape[-1] // 2 + 1))
    grids = np.meshgrid(*axes, indexing="ij")
    return np.sqrt(sum(np.asarray(grid, dtype=np.float64) ** 2 for grid in grids))


def Frequency_Split_Relative_L2(prediction: Field, truth: Field, cutoff_modes: float) -> tuple[float, float]:
    """Returns relative L2 errors of the below-cutoff and above-cutoff mode bands."""
    prediction_modes = np.fft.rfftn(np.asarray(prediction, dtype=np.float64))
    truth_modes = np.fft.rfftn(np.asarray(truth, dtype=np.float64))
    radius = Mode_Radius_Grid(np.asarray(prediction).shape)
    below_cutoff = radius <= cutoff_modes

    def Band_Error(mask: NDArray[np.bool_]) -> float:
        """Returns the masked-band relative L2 error in spectral form."""
        difference = np.linalg.norm((prediction_modes - truth_modes)[mask])
        size = np.linalg.norm(truth_modes[mask])
        return float(difference / size) if size > 0 else 0.0

    return Band_Error(below_cutoff), Band_Error(~below_cutoff)


def Periodic_Box_Mean(values: NDArray[np.float64], window: int) -> NDArray[np.float64]:
    """Returns the periodic moving average over a cubic window via circular convolution."""
    spectrum = np.fft.rfftn(values)
    for axis, extent in enumerate(values.shape):
        kernel = np.zeros(extent, dtype=np.float64)
        offsets = (np.arange(window) - window // 2) % extent
        kernel[offsets] = 1.0 / window
        kernel_modes = np.fft.rfft(kernel) if axis == values.ndim - 1 else np.fft.fft(kernel)
        shape = [1] * values.ndim
        shape[axis] = kernel_modes.shape[0]
        spectrum = spectrum * kernel_modes.reshape(shape)
    return np.fft.irfftn(spectrum, s=values.shape, axes=tuple(range(values.ndim)))


def Structural_Similarity_3d(prediction: Field, truth: Field, window: int = 7, data_range: float = 1.0) -> float:
    """Returns the mean three-dimensional structural similarity over periodic windows."""
    first_field = np.asarray(prediction, dtype=np.float64)
    second_field = np.asarray(truth, dtype=np.float64)
    stabilizer_one = (0.01 * data_range) ** 2
    stabilizer_two = (0.03 * data_range) ** 2
    mean_one = Periodic_Box_Mean(first_field, window)
    mean_two = Periodic_Box_Mean(second_field, window)
    variance_one = Periodic_Box_Mean(first_field * first_field, window) - mean_one * mean_one
    variance_two = Periodic_Box_Mean(second_field * second_field, window) - mean_two * mean_two
    covariance = Periodic_Box_Mean(first_field * second_field, window) - mean_one * mean_two
    numerator = (2 * mean_one * mean_two + stabilizer_one) * (2 * covariance + stabilizer_two)
    denominator = (mean_one**2 + mean_two**2 + stabilizer_one) * (variance_one + variance_two + stabilizer_two)
    return float(np.mean(numerator / denominator))


def Curve_L1(prediction: NDArray[np.float64], truth: NDArray[np.float64], spacing: float) -> float:
    """Returns the integrated absolute curve difference divided by the truth's integral."""
    difference = float(np.sum(np.abs(prediction - truth)) * spacing)
    size = float(np.sum(np.abs(truth)) * spacing)
    return difference / size


def Wasserstein_1d(prediction: NDArray[np.float64], truth: NDArray[np.float64], spacing: float) -> float:
    """Returns the one-dimensional transport distance between unit-mass curves."""
    first_field = prediction / (np.sum(prediction) * spacing)
    second_field = truth / (np.sum(truth) * spacing)
    cumulative_gap = np.cumsum(first_field - second_field) * spacing
    return float(np.sum(np.abs(cumulative_gap)) * spacing)


def Fraction_Within(errors: NDArray[np.float64], tolerance: float) -> float:
    """Returns the fraction of absolute errors at or below the tolerance."""
    return float(np.mean(np.abs(errors) <= tolerance))


def Median_And_Interquartile(values: NDArray[np.float64]) -> tuple[float, float]:
    """Returns the median and the interquartile range."""
    lower, median, upper = np.percentile(values, [25.0, 50.0, 75.0])
    return float(median), float(upper - lower)


def Bootstrap_Confidence_Interval(
    values: NDArray[np.float64],
    draws: int = 2000,
    coverage: float = 0.95,
    seed: int = 20260828,
) -> tuple[float, float]:
    """Returns a percentile bootstrap interval for the mean over exchangeable units."""
    generator = np.random.default_rng(seed)
    samples = generator.choice(values, size=(draws, values.shape[0]), replace=True)
    means = samples.mean(axis=1)
    tail = 100.0 * (1.0 - coverage) / 2.0
    lower_bound, upper_bound = np.percentile(means, [tail, 100.0 - tail])
    return float(lower_bound), float(upper_bound)

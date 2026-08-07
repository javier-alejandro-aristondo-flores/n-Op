"""Family B -- a Fourier neural operator on the Brillouin zone.

An FNO learns a map between function spaces by stacking integral-kernel layers
parametrized in Fourier space. Its core assumption is that the domain is periodic, and it
is normally an approximation: people apply FNOs to rectangles and pad.

**Here the assumption is exactly true.** The Brillouin zone *is* a torus. A crystal's
eigenvalue field satisfies `E(k + G) = E(k)` for every reciprocal lattice vector `G`, not
approximately but by construction, so the FFT kernel is the physically correct operator and
there is nothing to pad. That is unusual enough to be worth stating, and it is the reason
the spec mandates this family alongside the branch-trunk one.

## What it cannot do, and why it is built anyway

It is **mesh-bound**. The layers act on the 7x7x7 grid; there is no way to query an
arbitrary k. That fails the seam's load-bearing requirement -- "given per-channel lists of
query coordinates, the operator returns that channel's values at exactly those points" --
which only the branch-trunk trunk can satisfy.

It is built because §4.4 requires both families behind one interface "so the frozen exams,
not the builder's taste, choose the winner", and because on a smooth periodic domain the
literature expects the FNO to win on-mesh accuracy. If it does, that is a real result about
where the operator's value lies; if the choice is left to taste, nothing has been learned.

## Unfolding, and why it is lossless

Gate 4's table stores 172 k-points: one representative of each pair `{k, -k}` after time
reversal folded the 343 = 7^3 mesh. `E(k) = E(-k)` holds exactly for a nonmagnetic crystal,
so unfolding back to the full grid invents nothing. Folding the *output* back is done by
averaging over each pair, which additionally forces the prediction to obey time reversal --
a symmetry the model then cannot violate.

## Mode count

The recommendation and the ceiling both come from the mesh. A 7-point axis carries 4
independent Fourier magnitudes, so 4 is the hard upper bound; the default here is **2**,
which the spec recommends because mode truncation is the FNO's main implicit regularizer
and over-setting it is the documented overfitting driver at this sample count.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch import nn

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import locations  # noqa: E402, F401
from corpus import N_BANDS  # noqa: E402
from differentiation import (TrainingReport, fit, parameter_count,  # noqa: E402
                             predict_in_batches, seed_everything)
from symmetry import MESH, _fold  # noqa: E402

STRAIN_SCALE = 0.05          # shared with the branch-trunk family, and for the same reason
ENERGY_SCALE = 10.0          # eV


def unfolding(grid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Maps between the folded 172-point list and the full 7x7x7 mesh.

    Returns `(scatter, average)`:

    * `scatter[n]` is the folded index of full-grid point `n`, so
      `field_172[scatter].reshape(7, 7, 7, bands)` unfolds a field;
    * `average` is a `(172, 343)` matrix whose row `i` averages the full-grid points that
      fold onto `i`, so `average @ full` folds a prediction back while imposing
      `E(k) = E(-k)` on it.
    """
    index_of = {_fold(row): i for i, row in enumerate(grid)}
    if len(index_of) != len(grid):
        raise ValueError("the k-grid keys are not distinct after folding")

    scatter = np.empty(MESH ** 3, dtype=int)
    n = 0
    for a in range(MESH):
        for b in range(MESH):
            for c in range(MESH):
                scatter[n] = index_of[_fold(np.array([a, b, c]))]
                n += 1

    average = np.zeros((len(grid), MESH ** 3))
    for full, folded in enumerate(scatter):
        average[folded, full] = 1.0
    average /= average.sum(axis=1, keepdims=True)
    return scatter, average


class _SpectralConvolution(nn.Module):
    """One integral-kernel layer, parametrized on the retained Fourier modes.

    The first two axes are full complex transforms, so both signs of each frequency are
    retained; the third is a real transform and carries only non-negative ones. With a
    7-point axis and `modes = 2` that keeps frequencies {0, +1, -1} on the first two and
    {0, +1} on the third.
    """

    def __init__(self, channels: int, modes: int):
        super().__init__()
        if modes > (MESH + 1) // 2:
            raise ValueError(f"{modes} modes exceeds Nyquist for a {MESH}-point axis")
        full = list(range(modes)) + list(range(MESH - modes + 1, MESH))
        half = list(range(modes))
        self.register_buffer("axis_full", torch.tensor(full, dtype=torch.long))
        self.register_buffer("axis_half", torch.tensor(half, dtype=torch.long))
        scale = 1.0 / channels
        shape = (channels, channels, len(full), len(full), len(half))
        self.real = nn.Parameter(scale * torch.randn(*shape))
        self.imaginary = nn.Parameter(scale * torch.randn(*shape))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        transformed = torch.fft.rfftn(x, dim=(-3, -2, -1))
        i = self.axis_full[:, None, None]
        j = self.axis_full[None, :, None]
        k = self.axis_half[None, None, :]

        kept = transformed[:, :, i, j, k]
        weight = torch.complex(self.real, self.imaginary)
        mixed = torch.einsum("bixyz,ioxyz->boxyz", kept, weight)

        out = torch.zeros_like(transformed)
        out[:, :, i, j, k] = mixed
        return torch.fft.irfftn(out, s=(MESH, MESH, MESH), dim=(-3, -2, -1))


class _Module(nn.Module):
    """The torch side. Never leaves this file; see `differentiation.py`."""

    def __init__(self, n_strain: int, channels: int, modes: int, layers: int,
                 average: np.ndarray, target_mean: float):
        super().__init__()
        self.lift = nn.Linear(N_BANDS, channels)
        self.spectral = nn.ModuleList(
            [_SpectralConvolution(channels, modes) for _ in range(layers)])
        self.pointwise = nn.ModuleList(
            [nn.Conv3d(channels, channels, kernel_size=1) for _ in range(layers)])
        # FiLM: the strain 6-vector modulates every channel of every layer. `gamma` is
        # built as 1 + delta with the producing layer zero-initialized, so the network
        # starts as the identity modulation and strain conditioning is learned rather than
        # imposed at random.
        self.film = nn.ModuleList(
            [nn.Sequential(nn.Linear(n_strain, channels), nn.GELU(),
                           nn.Linear(channels, 2 * channels)) for _ in range(layers)])
        for block in self.film:
            nn.init.zeros_(block[-1].weight)
            nn.init.zeros_(block[-1].bias)
        self.project = nn.Sequential(nn.Linear(channels, channels), nn.GELU(),
                                     nn.Linear(channels, N_BANDS))
        self.register_buffer("average", torch.tensor(average, dtype=torch.float32))
        self.bias = nn.Parameter(torch.tensor(float(target_mean)))
        self.channels = channels

    def forward(self, strain: torch.Tensor, field: torch.Tensor) -> torch.Tensor:
        # field arrives as (batch, 7, 7, 7, bands)
        x = self.lift(field).permute(0, 4, 1, 2, 3)             # (batch, channels, 7,7,7)
        for spectral, pointwise, film in zip(self.spectral, self.pointwise, self.film):
            modulation = film(strain)
            gamma, beta = modulation.chunk(2, dim=-1)
            gamma = (1.0 + gamma)[:, :, None, None, None]
            beta = beta[:, :, None, None, None]
            x = torch.nn.functional.gelu(gamma * (spectral(x) + pointwise(x)) + beta)
        out = self.project(x.permute(0, 2, 3, 4, 1))            # (batch, 7,7,7, bands)
        flat = out.reshape(out.shape[0], MESH ** 3, N_BANDS)
        return torch.einsum("kn,bnc->bkc", self.average, flat) + self.bias


@dataclass
class SpectralOperator:
    """Mode 1 on the torus: (strain, PBE field) -> the PBE->HSE06 residual field.

    Same interface as `BranchTrunkOperator`, so `training.py` and `exams.py` take either
    without knowing which -- which is what lets the exams choose between them.
    """

    channels: int = 24
    modes: int = 2
    layers: int = 2
    seed: int = 0

    def __post_init__(self):
        self._module: _Module | None = None
        self._scatter: np.ndarray | None = None
        self._average: np.ndarray | None = None
        self.report: TrainingReport | None = None

    def _inputs(self, strains: np.ndarray, pbe_referenced: np.ndarray) -> dict:
        unfolded = pbe_referenced[:, self._scatter, :].reshape(
            len(pbe_referenced), MESH, MESH, MESH, N_BANDS)
        return {"strain": strains / STRAIN_SCALE, "field": unfolded / ENERGY_SCALE}

    def train_on(self, strains: np.ndarray, pbe_referenced: np.ndarray,
                 correction: np.ndarray, kfrac: np.ndarray, kweights: np.ndarray,
                 train_index: np.ndarray, validation_index: np.ndarray,
                 seed: int | None = None, grid: np.ndarray | None = None,
                 **options) -> TrainingReport:
        if grid is None:
            # Derive the integer mesh from the fractional coordinates rather than reloading
            # the corpus: the caller already has kfrac, and `load()` recomputes 1,131
            # canonical strains on the way to something this does not need.
            grid = np.array([_fold(np.rint(row * MESH).astype(int)) for row in kfrac])
        self._scatter, self._average = unfolding(grid)

        resolved_seed = self.seed if seed is None else seed
        seed_everything(resolved_seed)
        self._module = _Module(n_strain=strains.shape[1], channels=self.channels,
                               modes=self.modes, layers=self.layers,
                               average=self._average,
                               target_mean=float(correction[train_index].mean()))

        self.report = fit(self._module, self._inputs(strains, pbe_referenced), correction,
                          kweights, train_index=train_index,
                          validation_index=validation_index, seed=resolved_seed,
                          base_field=pbe_referenced, **options)
        return self.report

    def predict(self, strains: np.ndarray, pbe_referenced: np.ndarray) -> np.ndarray:
        if self._module is None:
            raise RuntimeError("train_on has not been called")
        return predict_in_batches(self._module, self._inputs(strains, pbe_referenced))

    def predict_hse_field(self, strains: np.ndarray,
                          pbe_referenced: np.ndarray) -> np.ndarray:
        from corpus import vbm_of

        field = pbe_referenced + self.predict(strains, pbe_referenced)
        return field - vbm_of(field)[:, None, None]

    @property
    def parameters(self) -> int:
        return parameter_count(self._module) if self._module is not None else 0


if __name__ == "__main__":
    from corpus import load

    corpus = load()

    # The unfolding must be exact before anything is trained on it.
    scatter, average = unfolding(corpus.grid)
    unfolded = corpus.energies_pbe[:, scatter, :]
    refolded = np.einsum("kn,bnc->bkc", average, unfolded)
    print(f"unfold/refold round trip, largest error: "
          f"{np.abs(refolded - corpus.energies_pbe).max():.3e} eV")
    assert np.abs(refolded - corpus.energies_pbe).max() < 1e-12, "unfolding is lossy"
    print(f"full mesh {MESH**3} points -> {len(corpus.grid)} folded classes")

    subset = np.arange(32)
    pbe = corpus.referenced("pbe")
    correction = corpus.correction()

    operator = SpectralOperator()
    report = operator.train_on(corpus.strains, pbe, correction, corpus.kfrac,
                               corpus.weights, train_index=subset,
                               validation_index=subset, grid=corpus.grid,
                               epochs=400, batch_size=32, patience=400)

    error = np.abs(operator.predict(corpus.strains[subset], pbe[subset])
                   - correction[subset])
    from baselines import COEFFICIENTS, apply_stretch, fit_stretch

    oracle = np.array([[fit_stretch(corpus, int(i))[k] for k in COEFFICIENTS]
                       for i in subset])
    oracle_error = np.abs(apply_stretch(pbe[subset], oracle)
                          - corpus.referenced("hse")[subset])

    print(f"\nparameters                       {operator.parameters:,}")
    print(f"epochs run                       {report.epochs_run}")
    print(f"B2 per-shape stretch (the floor) {oracle_error.mean() * 1000:.2f} meV MAE")
    print(f"this model                       {error.mean() * 1000:.2f} meV MAE")
    assert error.mean() < oracle_error.mean(), (
        f"the spectral model cannot overfit 32 shapes to better than the stretch "
        f"({error.mean() * 1000:.1f} vs {oracle_error.mean() * 1000:.1f} meV)")
    print("\ncapacity check passed")

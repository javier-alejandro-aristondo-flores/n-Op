"""Family A -- the branch-and-trunk operator, in the DeepONet lineage.

A branch network reads the input function and returns latent coefficients; a trunk network
reads the *evaluation location* and returns basis functions; the prediction is their inner
product. The reason to want it here is the trunk: it is a function of k, so it can be
queried at any k, not only at the 172 mesh points. That is the seam's load-bearing
requirement -- "given per-channel lists of query coordinates, the operator returns that
channel's values at exactly those points" -- and the spectral family cannot satisfy it.

**Continuous-k output is experimental and unvalidated, and stays labeled so.** There is no
off-mesh ground truth without new density-functional theory, and none is in scope. The
trunk will happily return a number at any k; nothing here says it is right.

## What is predicted

Mode 1's target is the residual field, per the spec's §3:

    dE(k, b) = E_HSE(k, b) - E_PBE(k, b)          both referred to their own valence maximum

The correction is a ~1.2 eV object carrying ~325 meV of structured variation, so learning
it on top of the known PBE field is a far smaller ask than relearning a ~40 eV spectrum.

## The model contains its own baseline

The trunk is given the PBE eigenvalue at the point it is evaluating, alongside the k
features and the band identity. With that input the network can represent

    dE = slope * E_PBE + intercept,   one branch occupied, one unoccupied

exactly -- which is the two-branch stretch of baselines B1 and B2. So the operator strictly
contains the model it must beat, and any failure to beat it is a training failure rather
than an expressivity one. That is worth having: it converts an ambiguous negative result
into a diagnosable one.

## Sizing

The spec caps parameters well under a million and recommends 1e4-1e5 at this sample count,
because 1,131 shapes with correlated symmetry augmentation is a small-data regime where
capacity is the main overfitting driver. The default below is about 19,000.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch import nn

# Run as a script, `models/` is on the path but the library root is not. One line here
# beats requiring every caller to know that.
if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import locations  # noqa: E402, F401  -- puts the repository on the import path
from corpus import N_BANDS, N_OCCUPIED
from seam import (TrainingReport, fit, parameter_count,  # noqa: F401
                             predict_in_batches, seed_everything)

#: Harmonics used to build periodic k features. The Brillouin zone is a torus and
#: fractional coordinates have period one, so cos/sin of 2*pi*m*f is exactly periodic --
#: no boundary artifact, unlike a raw coordinate.
HARMONICS = (1, 2)

#: Fixed input scales. **Not** fitted per fold, and deliberately not centered.
#:
#: Both inputs have a physically distinguished origin: zero strain is the undeformed cell,
#: and zero energy is the valence-band maximum every field is referred to. Subtracting a
#: fold-dependent mean moves those origins around, and dividing by a fold-dependent
#: per-component standard deviation is worse -- in the axis-and-skew families the third
#: normal component barely varies, so its standard deviation is 0.0025, and general-stretch
#: shapes standardized against it arrive **32 standard deviations** from the training data.
#: That is not extrapolation the network can be blamed for; it is manufactured by the
#: preprocessing. A fixed scale keeps the six components commensurate, keeps the origin
#: where the physics puts it, and makes the features identical in every fold.
STRAIN_SCALE = 0.05          # the sweep's typical strain magnitude
ENERGY_SCALE = 10.0          # eV, the spectrum's own scale


def kpoint_features(kfrac: np.ndarray) -> np.ndarray:
    """Periodic features of fractional k, shape (n_k, 6 * len(HARMONICS)).

    Fractional coordinates are used rather than Cartesian because periodicity is exact in
    them: `f` and `f + 1` are the same point. A raw coordinate would put a discontinuity
    across the zone boundary that the network would have to spend capacity undoing.
    """
    columns = []
    for harmonic in HARMONICS:
        angle = 2.0 * np.pi * harmonic * kfrac
        columns.extend([np.cos(angle), np.sin(angle)])
    return np.concatenate(columns, axis=1)


def _mlp(sizes: list[int]) -> nn.Sequential:
    layers: list[nn.Module] = []
    for i, (a, b) in enumerate(zip(sizes[:-1], sizes[1:])):
        layers.append(nn.Linear(a, b))
        if i < len(sizes) - 2:
            layers.append(nn.GELU())
    return nn.Sequential(*layers)


class _Module(nn.Module):
    """The torch side. Never leaves this file; see `differentiation.py`."""

    def __init__(self, n_strain: int, n_trunk_features: int, latent: int, width: int,
                 target_mean: float):
        super().__init__()
        self.branch = _mlp([n_strain, width, width, latent])
        self.trunk = _mlp([n_trunk_features, width, width, latent])
        self.latent = latent
        self.bias = nn.Parameter(torch.tensor(float(target_mean)))
        # A small last layer keeps the initial prediction near the target mean rather than
        # near zero, which matters when the target has a 1.2 eV offset and the loss is L1.
        for module in (self.branch[-1], self.trunk[-1]):
            nn.init.normal_(module.weight, std=1e-2)
            nn.init.zeros_(module.bias)

    def forward(self, strain: torch.Tensor, trunk_features: torch.Tensor) -> torch.Tensor:
        coefficients = self.branch(strain)                       # (batch, latent)
        basis = self.trunk(trunk_features)                       # (batch, nk, nb, latent)
        contracted = torch.einsum("bl,bkml->bkm", coefficients, basis)
        return contracted / self.latent ** 0.5 + self.bias


@dataclass
class BranchTrunkOperator:
    """Mode 1: (strain, PBE field) -> the PBE->HSE06 residual field.

    Arrays in, arrays out. The torch module is private and no graph escapes.
    """

    latent: int = 64
    width: int = 64
    seed: int = 0

    def __post_init__(self):
        self._module: _Module | None = None
        self._kfeatures: np.ndarray | None = None
        self._pretrained: dict | None = None
        self.report: TrainingReport | None = None

    # -- feature construction ----------------------------------------------

    def _trunk_features(self, strains: np.ndarray,
                        pbe_referenced: np.ndarray | None) -> np.ndarray:
        """Per (shape, k, band): periodic k features, band identity, and the PBE eigenvalue.

        The band one-hot is what lets the network keep a separate occupied and unoccupied
        branch, which is the form the physics baseline takes.

        **The energy column exists only in Mode 1.** Modes 2 and 3 have no cheap field at
        inference -- that is the whole point of them -- so the trunk reduces to a function
        of the evaluation location alone and the branch carries strain by itself, which is
        the textbook branch-trunk arrangement.
        """
        n = len(strains)
        n_k, n_b = len(self._kfeatures), N_BANDS
        k_part = np.broadcast_to(self._kfeatures[None, :, None, :],
                                 (n, n_k, n_b, self._kfeatures.shape[1]))
        band_part = np.broadcast_to(np.eye(n_b)[None, None, :, :], (n, n_k, n_b, n_b))
        occupied = np.broadcast_to(
            (np.arange(n_b) < N_OCCUPIED).astype(float)[None, None, :, None],
            (n, n_k, n_b, 1))
        columns = [k_part, band_part, occupied]
        if pbe_referenced is not None:
            columns.append(pbe_referenced[..., None] / ENERGY_SCALE)
        return np.concatenate(columns, axis=3)

    def _inputs(self, strains: np.ndarray,
                pbe_referenced: np.ndarray | None) -> dict:
        return {
            "strain": strains / STRAIN_SCALE,
            "trunk_features": self._trunk_features(strains, pbe_referenced),
        }

    # -- the numpy-facing interface ----------------------------------------

    def warm_start_from(self, other: "BranchTrunkOperator") -> None:
        """Copy another operator's weights. The multifidelity schedule of §6.5.

        Mode 3 learns strain -> the cheap PBE field, which is abundant and free here; Mode 2
        then learns strain -> the expensive HSE field starting from those weights rather
        than from noise. The two targets differ by a ~1.2 eV correction on a ~40 eV
        spectrum, so almost everything Mode 3 learned about the shape of a band structure
        transfers.
        """
        if other._module is None:
            raise RuntimeError("the source operator has not been trained")
        self._pretrained = {k: v.detach().clone()
                            for k, v in other._module.state_dict().items()}
        self._kfeatures = other._kfeatures

    def train_on(self, strains: np.ndarray, pbe_referenced: np.ndarray | None,
                 correction: np.ndarray, kfrac: np.ndarray, kweights: np.ndarray,
                 train_index: np.ndarray, validation_index: np.ndarray,
                 seed: int | None = None, **options) -> TrainingReport:
        self._kfeatures = kpoint_features(kfrac)
        inputs = self._inputs(strains, pbe_referenced)

        # Seed *before* construction. `fit` seeds too, but only after this point, so
        # without this line the initial weights depend on how many models were built
        # earlier in the same process -- and they do: the identical configuration scored
        # 93.8 meV as the sixth model in one script and 85.0 meV as the first in another.
        # That is 8.8 meV of scatter from process history alone, against a 20 meV
        # significance floor.
        resolved_seed = self.seed if seed is None else seed
        seed_everything(resolved_seed)
        self._module = _Module(
            n_strain=strains.shape[1],
            n_trunk_features=inputs["trunk_features"].shape[-1],
            latent=self.latent, width=self.width,
            target_mean=float(correction[train_index].mean()))
        if self._pretrained is not None:
            self._module.load_state_dict(self._pretrained)

        # The PBE field goes through so an auxiliary gap term can reconstruct the HSE
        # field it scores. Unused, and costing one tensor, when `gap_weight` is zero --
        # which is the default, because §6.4's no-region-weighting rule is the shipped
        # configuration and any gap term is a logged variant.
        self.report = fit(self._module, inputs, correction, kweights,
                          train_index=train_index, validation_index=validation_index,
                          seed=resolved_seed, base_field=pbe_referenced, **options)
        return self.report

    def predict(self, strains: np.ndarray,
                pbe_referenced: np.ndarray | None = None) -> np.ndarray:
        """The prediction, shape (n, n_k, n_band), float64 eV.

        In Mode 1 this is the residual field; in Modes 2 and 3 it is the field itself.
        """
        if self._module is None:
            raise RuntimeError("train_on has not been called")
        return predict_in_batches(self._module, self._inputs(strains, pbe_referenced))

    def predict_hse_field(self, strains: np.ndarray,
                          pbe_referenced: np.ndarray | None = None) -> np.ndarray:
        """The shipped field, re-referenced to its own valence maximum.

        Mode 1 adds the predicted correction to the PBE field it was given; Modes 2 and 3
        predict the field directly, so there is nothing to add.
        """
        from corpus import vbm_of

        prediction = self.predict(strains, pbe_referenced)
        field = prediction if pbe_referenced is None else pbe_referenced + prediction
        return field - vbm_of(field)[:, None, None]

    @property
    def parameters(self) -> int:
        return parameter_count(self._module) if self._module is not None else 0


if __name__ == "__main__":
    # The spec's capacity diagnostic: before scaling anything, confirm the model can
    # overfit a small subset. A model that cannot drive training error toward zero on 32
    # shapes has a capacity or optimization problem, and tuning it on 1,131 would be
    # debugging the wrong thing.
    from corpus import load

    corpus = load()
    seed_everything(0)
    subset = np.arange(32)
    pbe = corpus.referenced("pbe")
    correction = corpus.correction()

    operator = BranchTrunkOperator()
    report = operator.train_on(
        corpus.strains, pbe, correction, corpus.kfrac, corpus.weights,
        train_index=subset, validation_index=subset,
        epochs=600, batch_size=32, patience=600, verbose=True)

    prediction = operator.predict(corpus.strains[subset], pbe[subset])
    error = np.abs(prediction - correction[subset])

    # The threshold has to be one the problem can meet, and 20 meV is not it: that is the
    # gate's *gap* significance floor, and this is a per-eigenvalue field error over 172
    # k-points and 8 bands. The honest reference is the best any stretch-shaped model can
    # do -- the per-shape two-branch stretch fitted directly on the answer, which is
    # baseline B2 and which this architecture contains as a special case. If the model
    # cannot beat what it contains, it has an optimization problem.
    from baselines import COEFFICIENTS, apply_stretch, fit_stretch

    oracle = np.array([[fit_stretch(corpus, int(i))[k] for k in COEFFICIENTS]
                       for i in subset])
    oracle_field = apply_stretch(pbe[subset], oracle)
    oracle_error = np.abs(oracle_field - corpus.referenced("hse")[subset])

    print(f"\nparameters                       {operator.parameters:,}")
    print(f"epochs run                       {report.epochs_run}")
    print(f"target spread on subset          {correction[subset].std() * 1000:.1f} meV sd")
    print(f"B2 per-shape stretch (the floor) {oracle_error.mean() * 1000:.2f} meV MAE")
    print(f"this model                       {error.mean() * 1000:.2f} meV MAE")
    print(f"worst eigenvalue error           {error.max() * 1000:.2f} meV")
    assert error.mean() < oracle_error.mean(), (
        f"the model cannot overfit 32 shapes to better than the stretch it contains "
        f"({error.mean() * 1000:.1f} vs {oracle_error.mean() * 1000:.1f} meV) -- "
        "capacity or optimization is wrong, and tuning on the full corpus would be "
        "debugging the wrong thing")
    print("\ncapacity check passed -- the model beats the baseline it contains")

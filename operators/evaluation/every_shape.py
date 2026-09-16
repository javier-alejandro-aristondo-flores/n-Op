"""the memorization floor computed within each grid shape a parametric campaign's own test role holds"""

import numpy as np

from operators.data import Nearest_Training_Run
from operators.evaluation.scoring import ScoredRun
from operators.metrics import Relative_L2
from operators.training import FieldCache, Shape_Groups, Strain_Assignments_By_Run


def Every_Shape_Nearest_Neighbor_Runs(
    training_cache: FieldCache, test_cache: FieldCache, functional: str
) -> list[ScoredRun]:
    """the memorization floor computed within each grid shape, since a copy needs a shape to match its truth"""
    assignments = Strain_Assignments_By_Run()
    training_groups = Shape_Groups(training_cache)
    scored: list[ScoredRun] = []
    for grid_shape, test_fields in Shape_Groups(test_cache).items():
        training_fields = training_groups.get(grid_shape)
        # a shape the training role never produced has no candidate this floor could copy
        if not training_fields:
            continue
        training_parameters = np.stack([field.parameters for field in training_fields])
        test_parameters = np.stack([field.parameters for field in test_fields])
        nearest = Nearest_Training_Run(training_parameters, test_parameters)
        for position, cached_field in enumerate(test_fields):
            copied = training_fields[int(nearest[position])].Flattened_Values()[0]
            truth = cached_field.Flattened_Values()[0]
            scored.append(
                ScoredRun(
                    identifier=cached_field.identifier,
                    unit_key=cached_field.unit_key,
                    campaign="strain_atlas",
                    family=assignments[cached_field.run_path].family,
                    errors={"relative_l2": Relative_L2(copied, truth)},
                    covariate_values={
                        "functional": functional,
                        "grid_shape": "x".join(str(extent) for extent in grid_shape),
                    },
                )
            )
    return scored

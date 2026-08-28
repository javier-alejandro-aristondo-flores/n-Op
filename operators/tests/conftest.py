"""the corpus-mount guard for every pool-marked test"""

import pytest

from operators.data import POOL_ROOT


def pytest_runtest_setup(item: pytest.Item) -> None:
    """fails a pool-marked test before it runs when the corpus is not mounted"""
    if item.get_closest_marker("pool") is not None and not POOL_ROOT.exists():
        pytest.fail("the corpus at /Pool/VASP_DATA is not mounted on this machine")

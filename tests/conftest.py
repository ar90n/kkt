import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

DATA_ROOT = Path(__file__).parent / "data"

PYPROJECT_DATASET = [
    {
        "path": DATA_ROOT / "pyproject.toml",
        "expect": {"slug": "kkt-kernel", "title": "title", "competition": "titanic"},
    }
]


@pytest.fixture(params=PYPROJECT_DATASET)
def pyproject_data(request):
    yield request.param


@pytest.fixture
def kaggle_api():
    def _f(status: str, failureMessage: str, user: str):
        api_mock = MagicMock()
        api_mock.config_values = MagicMock()
        api_mock.config_values.__getitem__.side_effect = lambda _: user
        api_mock.kernel_status = MagicMock(
            return_value={"status": status, "failureMessage": failureMessage}
        )
        api_mock.competitions_list = MagicMock(return_value=["comp"])
        api_mock.authenticate = MagicMock()
        return api_mock

    yield _f

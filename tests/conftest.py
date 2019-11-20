from pathlib import Path

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

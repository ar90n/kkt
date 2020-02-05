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


def rename_dot_git(root: Path) -> None:
    dot_git_path = root / "dot_git"
    Path(dot_git_path).rename(".git")


@pytest.fixture(params=PYPROJECT_DATASET)
def pyproject_data(request):
    yield request.param


@pytest.fixture
def kaggle_api():
    def _f(status: str, failureMessage: str, user: str):
        api_mock = MagicMock()

        def _get_or_default(obj, key, default):
            return obj.get(key, default)

        api_mock.get_or_default = _get_or_default
        api_mock.config_values = MagicMock()
        api_mock.config_values.__getitem__.side_effect = lambda _: user
        api_mock.kernel_status = MagicMock(
            return_value={"status": status, "failureMessage": failureMessage}
        )
        api_mock.competitions_list = MagicMock(return_value=["comp"])
        api_mock.authenticate = MagicMock()
        api_mock.error = MagicMock()
        api_mock.kernel_push_with_http_info = MagicMock()

        def _process_response(*args, **kwargs):
            slug = api_mock.kernel_push_with_http_info.mock_calls[0][2][
                "kernel_push_request"
            ].slug
            ref = f"/{slug}"
            url = f"https://www.kaggle.com/{slug}"
            versionNumber = "1"
            error = None
            return {
                "error": error,
                "ref": ref,
                "url": url,
                "versionNumber": versionNumber,
            }

        api_mock.process_response = MagicMock(side_effect=_process_response)
        return api_mock

    yield _f

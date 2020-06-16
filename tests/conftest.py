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
def kaggle_api(requests_mock):
    def _f(status: str, failureMessage: str, user: str, is_update: bool = False):
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

        def _kernel_push_with_http_info(*args, **kwargs):
            slug = kwargs["kernel_push_request"].slug
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

        api_mock.kernel_push_with_http_info = MagicMock(
            side_effect=_kernel_push_with_http_info
        )

        requests_mock.get(
            "https://www.kaggleusercontent.com/kf/342432/abd", text="data"
        )

        def _kernel_output_with_http_info(*args, **kwargs):
            return {
                "files": [
                    {
                        "url": "https://www.kaggleusercontent.com/kf/342432/abd",
                        "fileName": "abc.wheel",
                    }
                ],
                "log": '[{"stream_name": "stdout", "data": "abc"} ]',
                "nextPageToken": None,
            }

        api_mock.kernel_output_with_http_info = MagicMock(
            side_effect=_kernel_output_with_http_info
        )

        def _datasets_create_new_with_http_info(*args, **kwargs):
            request = args[0]
            return {
                "ref": f"/{request.owner_slug}/{request.slug}-install",
                "url": f"https://www.kaggle.com/{request.owner_slug}/{request.slug}",
                "status": "ok",
                "error": None,
                "invalidTags": [],
            }

        api_mock.datasets_create_new_with_http_info = MagicMock(
            side_effect=_datasets_create_new_with_http_info
        )

        def _datasets_create_version_with_http_info(*args, **kwargs):
            owner_slug, dataset_slug, request = args
            return {
                "ref": f"/{owner_slug}/{dataset_slug}-install",
                "url": f"https://www.kaggle.com/{owner_slug}/{dataset_slug}",
                "status": "ok",
                "error": None,
                "invalidTags": [],
            }

        api_mock.upload_files = MagicMock()

        def _dataset_status(*args, **kwargs):
            return {} if is_update else None

        api_mock.dataset_status = MagicMock(side_effect=_dataset_status)

        api_mock.datasets_create_version_with_http_info = MagicMock(
            side_effect=_datasets_create_version_with_http_info
        )

        api_mock.process_response = MagicMock(side_effect=lambda x: x)
        return api_mock

    yield _f

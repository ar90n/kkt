import pytest

from kkt.exception import MetaDataNotFound
from kkt.commands.status import status, status_impl


@pytest.mark.parametrize(
    "given, expected",
    [
        (
            {"status": "complete", "failureMessage": None, "user": "user"},
            "status: complete",
        ),
        (
            {"status": "running", "failureMessage": None, "user": "user"},
            "status: running",
        ),
        (
            {"status": "complete", "failureMessage": "failed", "user": "user"},
            "status: complete\nmessage: failed",
        ),
    ],
)
def test_status_impl(given, expected, kaggle_api):
    api = kaggle_api(**given)
    actual = status_impl(api, {})
    assert expected == actual

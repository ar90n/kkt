import pytest

import kkt
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


def test_commands_status(chshared_datadir, cli_runner, kaggle_api, monkeypatch):
    api = kaggle_api("complete", None, "user")
    monkeypatch.setattr("kkt.commands.kkt_command.get_kaggle_api", lambda: api)

    ret = cli_runner.invoke(status, [])
    assert "status: complete\n" == ret.output

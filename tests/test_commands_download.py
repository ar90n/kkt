import re
import pytest
from tempfile import TemporaryDirectory

from kkt.commands.download import download


@pytest.mark.parametrize(
    "given, expected",
    [
        (
            {"status": "complete", "failureMessage": None, "user": "user"},
            {"output": r"^save to:/.*/abc.wheel$"},
        ),
        (
            {"status": "running", "failureMessage": None, "user": "user"},
            {"output": r"^Kernel has not been completed yet.$"},
        ),
    ],
)
def test_commands_install(
    chshared_datadir, given, expected, cli_runner, kaggle_api, monkeypatch
):
    api = kaggle_api(**given)
    monkeypatch.setattr("kkt.commands.kkt_command.get_kaggle_api", lambda: api)

    with TemporaryDirectory() as tmp_dir:
        ret = cli_runner.invoke(download, ["--quiet", str(tmp_dir)])
        for l in ret.output.strip().split("\n"):
            assert re.match(expected["output"], l)

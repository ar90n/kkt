import os
import pytest
from pathlib import Path

import kkt
from kkt.repo import Repo
from kkt.exception import MetaDataNotFound, FoundUncommitedFiles
from kkt.commands.install import install


@pytest.mark.parametrize(
    "given, expected",
    [
        (
            {"user": "kkt", "slug": "test01", "is_update": False},
            {
                "output": "\n".join(
                    [
                        "ref: /kkt/test01-requirements-install",
                        "url: https://www.kaggle.com/kkt/test01-requirements",
                        "",
                    ]
                ),
            },
        ),
        (
            {"user": "kkt", "slug": "test01", "is_update": True},
            {
                "output": "\n".join(
                    [
                        "ref: /kkt/test01-requirements-install",
                        "url: https://www.kaggle.com/kkt/test01-requirements",
                        "",
                    ]
                ),
            },
        ),
    ],
)
def test_commands_install(
    given, expected, virtualenv, chdatadir, cli_runner, kaggle_api, monkeypatch
):
    api = kaggle_api(None, None, given["user"], given["is_update"])
    monkeypatch.setattr("kkt.commands.kkt_command.get_kaggle_api", lambda: api)

    proj_path = chdatadir / given["slug"]
    os.chdir(proj_path)

    ret = cli_runner.invoke(install, ["--quiet"])
    assert expected["output"] == ret.output

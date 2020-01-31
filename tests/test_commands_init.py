import io

import pytest

from kkt.commands.init import init, init_impl
from kkt.parser import KktParser


@pytest.mark.parametrize(
    "given, expected",
    [
        (
            ["comp", "0", "slug", "", "", "", "", "", "", "", ""],
            {
                "meta_data": {
                    "competition": "comp",
                    "slug": "slug",
                    "code_file": "script.py",
                    "kernel_type": "script",
                    "is_private": True,
                    "enable_gpu": False,
                    "enable_internet": False,
                    "dataset_sources": [],
                    "competition_sources": ["comp"],
                },
                "enable_git_tag": False,
            },
        )
    ],
)
def test_init_impl(given, expected, monkeypatch, kaggle_api):
    monkeypatch.setattr("sys.stdin", io.StringIO("\n".join(given)))
    api = kaggle_api(None, None, None)
    actual = init_impl(api)
    assert actual == expected


def test_commands_init(chdatadir, cli_runner, kaggle_api, monkeypatch):
    api = kaggle_api("complete", None, "user")
    monkeypatch.setattr("kkt.commands.kkt_command.get_kaggle_api", lambda: api)
    stdin_value = "\n".join(
        [
            "y",
            "comp",
            "0",
            "slug",
            "test.py",
            "script",
            "N",
            "y",
            "y",
            "y",
            "data",
            "N",
            "y",
        ]
    )

    ret = cli_runner.invoke(init, [], input=stdin_value)

    expected_kkt = {
        "meta_data": {
            "competition": "comp",
            "slug": "slug",
            "code_file": "test.py",
            "kernel_type": "script",
            "is_private": False,
            "enable_gpu": True,
            "enable_internet": True,
            "dataset_sources": ["data"],
            "kernel_data_sources": [],
            "competition_sources": ["comp"],
            "keywords": [],
        },
        "enable_git_tag": True,
    }

    pyproject_path = chdatadir / "pyproject.toml"
    actual_kkt = KktParser(pyproject_path).read()
    assert expected_kkt == actual_kkt

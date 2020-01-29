import io

import pytest

from kkt.commands.init import init_impl


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

import os
import pytest
from pathlib import Path

import kkt
from kkt.repo import Repo
from kkt.exception import MetaDataNotFound, FoundUncommitedFiles
from kkt.commands.push import push
from .conftest import rename_dot_git


@pytest.mark.parametrize(
    "given, expected",
    [
        (
            {
                "user": "kkt",
                "slug": "without_git",
                "environ": {"KKT_ENV002": "ENV002"},
                "target": ".",
            },
            {
                "output": "\n".join(
                    [
                        "ref: /kkt/without_git",
                        "url: https://www.kaggle.com/kkt/without_git",
                        "version: 1",
                        "",
                    ]
                ),
                "meta_data": {
                    "category_ids": ["without_git"],
                    "kernel_data_sources": [],
                    "id": "test",
                    "competition": "without_git",
                    "competition_sources": ["without_git_comp"],
                    "dataset_sources": [
                        "without_git_data",
                        "kkt/without_git-requirements",
                    ],
                    "enable_gpu": True,
                    "enable_internet": True,
                    "is_private": False,
                    "kernel_type": "script",
                    "language": "python",
                    "enable_constraint": False,
                },
                "environment_variables": {"ENV001": "ENV001", "ENV002": "ENV002"},
            },
        ),
        (
            {
                "user": "kkt",
                "slug": "without_git",
                "environ": {"KKT_ENV002": "ENV002"},
                "target": ".nest",
            },
            {
                "output": "\n".join(
                    [
                        "ref: /kkt/without_git_nest",
                        "url: https://www.kaggle.com/kkt/without_git_nest",
                        "version: 1",
                        "",
                    ]
                ),
                "meta_data": {
                    "category_ids": ["without_git"],
                    "kernel_data_sources": [],
                    "id": "test",
                    "competition": "without_git",
                    "competition_sources": ["without_git_comp"],
                    "dataset_sources": [
                        "without_git_data",
                        "kkt/without_git_nest-requirements",
                    ],
                    "enable_gpu": False,
                    "enable_internet": True,
                    "is_private": True,
                    "kernel_type": "script",
                    "language": "python",
                    "enable_constraint": False,
                },
                "environment_variables": {"ENV001": "ENV001", "ENV002": "ENV002"},
            },
        ),
    ],
)
def test_commands_push(
    given, expected, virtualenv, chdatadir, cli_runner, kaggle_api, monkeypatch
):
    api = kaggle_api(None, None, given["user"])
    monkeypatch.setattr("kkt.commands.kkt_command.get_kaggle_api", lambda: api)

    proj_path = chdatadir / given["slug"]
    os.chdir(proj_path)

    os.environ["KKT_ENV002"] = "ENV002"
    ret = cli_runner.invoke(push, ["--target", given["target"]])
    assert expected["output"] == ret.output

    expected_meta_data = expected["meta_data"]
    push_request = api.kernel_push_with_http_info.mock_calls[0][2][
        "kernel_push_request"
    ]
    assert expected_meta_data["is_private"] == push_request.is_private
    assert expected_meta_data["enable_internet"] == push_request.enable_internet
    assert expected_meta_data["enable_gpu"] == push_request.enable_gpu
    assert expected_meta_data["kernel_type"] == push_request.kernel_type
    assert expected_meta_data["language"] == push_request.language
    assert expected_meta_data["dataset_sources"] == push_request.dataset_data_sources
    assert (
        expected_meta_data["competition_sources"]
        == push_request.competition_data_sources
    )
    assert expected_meta_data["kernel_data_sources"] == push_request.kernel_data_sources
    assert expected_meta_data["competition"] == push_request.category_ids[0]

    print(push_request)
    expected_envs = expected["environment_variables"]
    actual_kernel_output = virtualenv.run(
        f"python -c '{push_request.text}'", capture=True
    )
    actual_kernel_output = "\n".join(actual_kernel_output.split("\n")[2:])
    expect_kernel_output = f"""Successfully installed kkt-commands-push-test-without-git-0.1.0
{expected_envs["ENV001"]}
{expected_envs["ENV002"]}
"""
    assert actual_kernel_output == expect_kernel_output


@pytest.mark.parametrize(
    "given, expected",
    [
        (
            {"user": "kkt", "slug": "with_git"},
            {
                "output": "\n".join(
                    [
                        "ref: /kkt/with_git",
                        "url: https://www.kaggle.com/kkt/with_git",
                        "version: 1",
                        "",
                    ]
                ),
                "git_tag": "kernel_version_1",
            },
        )
    ],
)
def test_commands_push_with_git(
    given, expected, virtualenv, chdatadir, cli_runner, kaggle_api, monkeypatch
):
    api = kaggle_api(None, None, given["user"])
    monkeypatch.setattr("kkt.commands.kkt_command.get_kaggle_api", lambda: api)

    proj_path = chdatadir / given["slug"]
    os.chdir(proj_path)

    rename_dot_git(Path.cwd())

    ret = cli_runner.invoke(push, [])
    assert expected["output"] == ret.output

    repo = Repo(Path.cwd())
    assert expected["git_tag"] == repo.git_repo.tags[0].name


def test_commands_push_failed_with_git(chdatadir, cli_runner, kaggle_api, monkeypatch):
    api = kaggle_api(None, None, "kkt")
    monkeypatch.setattr("kkt.commands.kkt_command.get_kaggle_api", lambda: api)

    proj_path = chdatadir / "with_git"
    os.chdir(proj_path)

    rename_dot_git(Path.cwd())
    (Path.cwd() / "tmp").open("a").close()

    ret = cli_runner.invoke(push, [])
    assert "" == ret.output
    assert isinstance(ret.exception, FoundUncommitedFiles)
    assert ["tmp"] == ret.exception.args[0]

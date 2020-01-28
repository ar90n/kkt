import pytest
from pathlib import Path

from kkt.repo import Repo
from kkt.exception import FoundUncommitedFiles


def rename_dot_git(root: Path) -> None:
    dot_git_path = root / "dot_git"
    Path(dot_git_path).rename(".git")


def test_repo(chdatadir):
    rename_dot_git(chdatadir)

    repo = Repo(chdatadir)
    assert repo.git_repo is not None

    repo.validate()
    repo.attach_version_tag(10, {}, {})


def test_repo_validate_failed(chdatadir):
    rename_dot_git(chdatadir)
    (chdatadir / "tmp").open("a").close()

    repo = Repo(chdatadir)
    with pytest.raises(FoundUncommitedFiles) as e:
        repo.validate()
    assert e.value.args[0] == ["tmp"]

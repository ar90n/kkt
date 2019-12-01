import re
from pathlib import Path

from git import Repo as GitRepo

from .exception import AlreadyPushed, FoundUncommitedFiles


def _create_tag(version: int) -> str:
    return "kernel_version_{}".format(version)


class Repo:
    def __init__(self, path: Path) -> None:
        self.path = path

    @property
    def git_repo(self):
        return GitRepo(self.path)

    def _check_uncommited_files(self) -> None:
        untracked_files = self.git_repo.untracked_files
        modified_files = [_.a_path for _ in self.git_repo.index.diff(None)]
        staged_files = [_.a_path for _ in self.git_repo.index.diff("HEAD")]
        uncommitted_files = [*untracked_files, *modified_files, *staged_files]
        if 0 < len(uncommitted_files):
            raise FoundUncommitedFiles(uncommitted_files)

    def _check_already_pushed(self) -> None:
        tag = self.git_repo.git.describe()
        if re.match("^kernel_version_\d+$", tag) is not None:
            raise AlreadyPushed()

    def validate(self):
        self._check_uncommited_files()
        self._check_already_pushed()

    def attach_version_tag(self, version: int) -> None:
        tag = _create_tag(version)
        self.git_repo.create_tag(tag, message=tag)

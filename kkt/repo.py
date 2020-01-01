import re
from pathlib import Path
from typing import Dict

from tomlkit import dumps as dumps_as_toml

from git import Repo as GitRepo

from .exception import AlreadyPushed, FoundUncommitedFiles


def _create_tag(version: int) -> str:
    return "kernel_version_{}".format(version)


def _create_message(meta_data: Dict, env_variables: Dict) -> str:
    meta_data_dump = dumps_as_toml(meta_data)
    env_variables_dump = dumps_as_toml(env_variables)
    return f"[tool.kkt.meta_data]\n{meta_data_dump}\n\n[tool.kkt.environment_variables]\n{env_variables_dump}"


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

    def validate(self):
        self._check_uncommited_files()

    def attach_version_tag(
        self, version: int, meta_data: Dict, env_variables: Dict
    ) -> None:
        tag = _create_tag(version)
        message = _create_message(meta_data, env_variables)
        self.git_repo.create_tag(tag, message=message)

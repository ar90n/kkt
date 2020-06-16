import os
import re
from pathlib import Path
from typing import Dict

from kaggle import KaggleApi
from kaggle.models.kaggle_models_extended import KernelPushResponse

from .. import kernel_proc
from ..resource import get_dataset_slug
from ..builders import get_builder
from ..exception import MetaDataNotFound
from ..repo import Repo
from .kkt_command import kkt_command


def create_kernel_body(meta_data: Dict, pkg_dataset, env_variables: Dict) -> str:
    enable_internet = meta_data.get("enable_internet", False)
    kernel_type = meta_data.get("kernel_type", "script")
    code_file_path = Path(meta_data.get("code_file", "main.py"))
    if not code_file_path.is_absolute():
        code_file_path = Path.cwd() / code_file_path

    kernel_builder = get_builder(kernel_type, enable_internet)
    with code_file_path.open() as fp:
        return kernel_builder(fp, pkg_dataset, env_variables)


def push_impl(
    api: KaggleApi, meta_data: Dict, env_variables: Dict
) -> KernelPushResponse:

    dataset_slug = get_dataset_slug(api, meta_data)
    dataset_name = dataset_slug.split("/")[-1]

    kernel_body = create_kernel_body(meta_data, dataset_name, env_variables)
    kernel_push_param = kernel_proc.KernelPushParams.of(api, meta_data)
    kernel_push_param.dataset_data_sources.append(dataset_slug)
    return kernel_proc.push(api, kernel_push_param, kernel_body)


def get_env_variables(env_variables: Dict) -> Dict:
    result = {**env_variables}
    for k, v in os.environ.items():
        m = re.match(r"^KKT_(.+)$", k)
        if m:
            update_key = m.groups()[0]
            result[update_key] = v
    return result


@kkt_command()
def push(api: KaggleApi, kkt: Dict, pyproject_path: Path, **kwargs: Dict) -> None:
    repo = Repo(pyproject_path.parent)
    enable_git_tag: bool = kkt.get("enable_git_tag", False)
    if enable_git_tag:
        repo.validate()

    if "meta_data" not in kkt:
        raise MetaDataNotFound()

    meta_data = kkt["meta_data"].value
    env_variables = get_env_variables(kkt.get("environment_variables", {}))

    result = push_impl(api, meta_data, env_variables)
    kernel_proc.print_response(result)

    if enable_git_tag and result.versionNumber:
        repo.attach_version_tag(result.versionNumber, meta_data, env_variables)

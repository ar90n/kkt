import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List

import click
from kaggle import KaggleApi
from kaggle.models.kaggle_models_extended import KernelPushResponse

from .. import kernel_proc
from ..builders.packaging_system import get_dependencies
from ..exception import InstallKernelError, MetaDataNotFound
from ..resource import get_username, get_dataset_slug
from .kkt_command import kkt_command
from ..fetch import PackageLocation, fetch_packages


def create_kernel_body(install_pkgs: List[str]) -> str:
    return f"""
import subprocess

def pip_freeze():
    args = ["pip", "freeze"]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    run_result = proc.communicate()
    return run_result[0].decode("utf-8").split("\\n")

def pip_install(pkgs):
    if len(pkgs) == 0:
        return
    args = ["pip", "install", *pkgs]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    return proc.communicate()[0].decode("utf-8")

def pip_download(pkgs):
    if len(pkgs) == 0:
        return ""
    args = ["pip", "download", "--no-deps", *pkgs]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    return proc.communicate()[0].decode("utf-8")

freeze_before_install = pip_freeze()
print(pip_install({install_pkgs}))
freeze_after_install = pip_freeze()

diff_pkgs = set(freeze_after_install) - set(freeze_before_install)
print(pip_download(diff_pkgs))
"""


def create_kernel_push_params(
    api: KaggleApi, meta_data: Dict
) -> kernel_proc.KernelPushParams:
    slug = meta_data["slug"]
    install_kernel_slug = f"{slug}-install"
    install_kernel_meta_data = {
        **meta_data,
        "slug": install_kernel_slug,
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": False,
        "enable_internet": True,
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
        "keywords": [],
    }
    return kernel_proc.KernelPushParams.of(api, install_kernel_meta_data)


def get_owner_slug_from(response: KernelPushResponse):
    return response.ref.split("/")[1]


def get_kernel_slug_from(response: KernelPushResponse):
    return response.ref.split("/")[2]


def get_error_messages(logs: Dict) -> List[str]:
    result = []
    for log in logs:
        stream_name = log.get("stream_name", "stderr")
        data = log.get("data", "")
        if stream_name == "stderr" and not (
            data.startswith("[NbConvertApp]") or data.startswith("WARNING:")
        ):
            result.append(data)
    return result


def _get_package_locations(list_response: Dict[str, Any]) -> List[PackageLocation]:
    return [
        PackageLocation(item["url"], item["fileName"])
        for item in list_response["files"]
    ]


def wait_for_install_kernel_completion(
    api: KaggleApi, kernel_slug: str, quiet: bool = False
) -> Dict[str, Any]:
    while True:
        owner_slug = get_username(api)
        response = api.process_response(
            api.kernel_output_with_http_info(owner_slug, kernel_slug)
        )

        if response["log"] != "":
            logs = json.loads(response["log"])
            err_messages = get_error_messages(logs)
            if 0 < len(err_messages):
                raise InstallKernelError(err_messages)
            if 0 < len(logs):
                return response

        if not quiet:
            click.echo("Wait for install kernel completion...")
        time.sleep(10)


def upload_requirement_pkgs(
    api: KaggleApi, meta_data: Dict, target_dir: Path, quiet: bool = False
):
    slug = get_dataset_slug(api, meta_data)
    _, dataset_slug = slug.split("/")[-2:]
    license_name = "CC0-1.0"
    status = api.dataset_status(slug)
    if status is None:
        return kernel_proc.create_dataset(
            api,
            dataset_slug=dataset_slug,
            license_name=license_name,
            target_dir=target_dir,
            quiet=quiet,
        )
    else:
        return kernel_proc.update_dataset(
            api, dataset_slug=dataset_slug, target_dir=target_dir, quiet=quiet,
        )


def push_install_kernel(
    api: KaggleApi, meta_data: Dict, quiet: bool = False
) -> KernelPushResponse:
    enable_constraint = meta_data.get("enable_constraint", False)

    kernel_push_params = create_kernel_push_params(api, meta_data)
    dependencies = get_dependencies(enable_constraint)
    kernel_body = create_kernel_body(dependencies)
    kernel_response = kernel_proc.push(api, kernel_push_params, kernel_body)
    if not quiet:
        kernel_proc.print_response(kernel_response)
        click.echo("Pushing install kernel successed.")

    return kernel_response


@kkt_command()
def install(
    api: KaggleApi, kkt: Dict, pyproject_path: Path, quiet: bool = False, **kwargs: Dict
) -> None:
    if "meta_data" not in kkt:
        raise MetaDataNotFound()
    meta_data = kkt["meta_data"].value
    kernel_response = push_install_kernel(api, meta_data, quiet)

    kernel_slug = get_kernel_slug_from(kernel_response)
    kernel_output = wait_for_install_kernel_completion(
        api, kernel_slug=kernel_slug, quiet=quiet
    )

    with TemporaryDirectory() as tmp_dir:
        target_dir = Path(tmp_dir)
        pkg_locations = _get_package_locations(kernel_output)
        fetch_files = fetch_packages(pkg_locations, target_dir, quiet=quiet)
        if len(fetch_files) == 0:
            click.echo("Extra required packages are nothing.")
            return

        ret = upload_requirement_pkgs(
            api, meta_data, target_dir=target_dir, quiet=quiet
        )

    kernel_proc.print_response(ret)

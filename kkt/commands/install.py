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


def create_kernel_body(
    python_pkgs: List[str],
    extra_python_pkgs: List[str],
    extra_deb_pkgs: List[str],
    prologue: str,
) -> str:
    return f"""{prologue}
import os
import sys
import subprocess
from pathlib import Path

def pip_freeze():
    args = [sys.executable, "-m", "pip", "freeze"]
    output = subprocess.run(args, capture_output=True, encoding='utf-8', check=True).stdout
    return output.split("\\n")

def pip_install(pkgs, ignore_error=False):
    if len(pkgs) == 0:
        return
    args = [sys.executable, "-m", "pip", "install", *pkgs]
    try:
        ret = subprocess.run(args, capture_output=True, encoding='utf-8', check=True).stdout
    except subprocess.CalledProcessError as e:
        ret = str(e.stdout)
    return ret

def deb_install(pkgs):
    if len(pkgs) == 0:
        return
    args = ["apt-get", "install", "-y", *pkgs]
    return subprocess.run(args, capture_output=True, encoding='utf-8', check=True).stdout

def pip_download(pkgs):
    Path("./pip").mkdir(exist_ok=True)
    if len(pkgs) == 0:
        return ""
    args = [sys.executable, "-m", "pip", "download", "--no-deps", "-d", "pip", *pkgs]
    return subprocess.run(args, capture_output=True, encoding='utf-8', check=True).stdout

def deb_download(pkgs):
    dst_dir_path = Path("./deb")
    dst_dir_path.mkdir(exist_ok=True)
    if len(pkgs) == 0:
        return ""
    args = ["apt-get", "-o", "Dir::Cache::archives='/kaggle/working/deb/'", "install", "-y", *pkgs]
    os.system(" ".join(args))
    (dst_dir_path / "lock").unlink()
    (dst_dir_path / "partial").rmdir()

deb_download({extra_deb_pkgs})

freeze_before_install = pip_freeze()
print(pip_install({python_pkgs}))
print(pip_install({extra_python_pkgs}), True)
freeze_after_install = pip_freeze()
diff_pkgs = set(freeze_after_install) - set(freeze_before_install)
print(pip_download(diff_pkgs))
"""


def create_kernel_push_params(
    api: KaggleApi, meta_data: Dict
) -> kernel_proc.KernelPushParams:
    install_kernel_slug = get_install_slug(meta_data)
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


def get_install_slug(meta_data: Dict) -> str:
    return f"{meta_data['slug']}-install"


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
            data.startswith("[NbConvertApp]")
            or data.startswith("WARNING:")
            or data.startswith("  Running command")
        ):
            result.append(data)
    return result


def _get_package_locations(list_response: Dict[str, Any]) -> List[PackageLocation]:
    return [
        PackageLocation(item["url"], item["fileName"])
        for item in list_response["files"]
    ]


def wait_for_install_kernel_completion(
    api: KaggleApi, meta_data: Dict, kernel_slug: str, quiet: bool = False
) -> Dict[str, Any]:
    owner_slug = get_username(api)
    while True:
        response = api.process_response(
            api.kernel_output_with_http_info(owner_slug, kernel_slug)
        )

        if response["log"] != "":
            time.sleep(1)  # wait for completion of synchlonizing kernel status
            result = kernel_proc.status(api, kernel_slug)
            if result["status"] != "complete" or result["failureMessage"]:
                logs = json.loads(response["log"])
                err_messages = get_error_messages(logs)
                raise InstallKernelError(err_messages)
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
    api: KaggleApi,
    meta_data: Dict,
    enable_constraint: bool,
    extra_dependencies: List[str],
    extra_deb_dependencies: List[str],
    quiet: bool = False,
) -> KernelPushResponse:
    kernel_push_params = create_kernel_push_params(api, meta_data)
    dependencies = get_dependencies(enable_constraint)
    prologue = meta_data.get("prologue", "")
    kernel_body = create_kernel_body(
        dependencies, extra_dependencies, extra_deb_dependencies, prologue
    )
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
    enable_constraint = kkt.get("enable_constraint", False)
    extra_dependencies = kkt.get("extra_dependencies", [])
    extra_deb_dependencies = kkt.get("extra_deb_dependencies", [])
    kernel_response = push_install_kernel(
        api,
        meta_data,
        enable_constraint,
        extra_dependencies,
        extra_deb_dependencies,
        quiet,
    )

    kernel_slug = get_kernel_slug_from(kernel_response)
    kernel_output = wait_for_install_kernel_completion(
        api, meta_data=meta_data, kernel_slug=kernel_slug, quiet=quiet
    )

    with TemporaryDirectory() as tmp_dir:
        target_dir = Path(tmp_dir)
        (target_dir / "pip").mkdir(exist_ok=True)
        (target_dir / "deb").mkdir(exist_ok=True)

        pkg_locations = _get_package_locations(kernel_output)
        fetch_files = fetch_packages(pkg_locations, target_dir, quiet=quiet)
        if len(fetch_files) == 0:
            click.echo("Extra required packages are nothing.")
            return

        ret = upload_requirement_pkgs(
            api, meta_data, target_dir=target_dir, quiet=quiet
        )

    kernel_proc.print_response(ret)

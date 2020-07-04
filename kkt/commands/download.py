from pathlib import Path
from typing import Any, Dict, List

import click
from kaggle import KaggleApi

from .. import kernel_proc
from ..exception import MetaDataNotFound
from .kkt_command import kkt_command
from ..fetch import PackageLocation, fetch_packages


def _get_package_locations(list_response: Dict[str, Any]) -> List[PackageLocation]:
    return [
        PackageLocation(item["url"], item["fileName"])
        for item in list_response["files"]
    ]


def _print_paths(paths: List[Path]) -> None:
    for p in paths:
        click.echo(f"save to:{str(p)}")


@kkt_command()
@click.argument("dst_dir")
def download(
    api: KaggleApi, kkt: Dict, pyproject_path: Path, quiet: bool = False, **kwargs
) -> None:
    if "meta_data" not in kkt:
        raise MetaDataNotFound()
    meta_data = kkt["meta_data"].value

    dst_dir = kwargs.get("dst_dir")
    if dst_dir is None:
        raise ValueError("DST_DIR is None")
    dst_dir_path = Path(dst_dir)

    kernel_slug = meta_data["slug"]
    status = kernel_proc.status(api, kernel_slug)
    if status["status"] != "complete":
        click.echo("Kernel has not been completed yet.")
        return

    list_response = kernel_proc.list_outputs(api, kernel_slug)
    pkg_locations = _get_package_locations(list_response)
    download_files = fetch_packages(pkg_locations, dst_dir_path, quiet)
    for p in download_files:
        click.echo(f"save to:{str(p)}")

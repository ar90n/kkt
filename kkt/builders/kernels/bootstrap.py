import json
from typing import Dict, Iterable


BOOTSTRAP_TEMPLATE: str = """def __bootstrap__():
    import sys
    import base64
    import gzip
    import tarfile
    import os
    import io
    import subprocess
    from pathlib import Path
    from tempfile import TemporaryDirectory

    pkg_dataset_path = Path.cwd().parent / "input" / "{pkg_dataset}"

    # install deb packages
    deb_pkgs_path = pkg_dataset_path / "deb"
    deb_path_list = [str(p) for p in deb_pkgs_path.glob("*.deb")]
    if 0 < len(deb_path_list):
        output = subprocess.run(["dpkg", "-i", *deb_path_list], capture_output=True, encoding="utf-8", check=True).stdout
        print(output)

    # install required packages
    pip_pkgs_path = pkg_dataset_path / "pip"
    pkg_path_list = []
    for p in pip_pkgs_path.glob("*"):
        if p.is_dir():
            pkg_config_files = [str(p.parent) for p in p.glob("**/*") if p.name in ["pyproject.toml", "setup.py"]]
            pkg_root_dir = min(pkg_config_files, key=len)
            pkg_path_list.append(pkg_root_dir)
        else:
            pkg_path_list.append(str(p))
    if 0 < len(pkg_path_list):
        output = subprocess.run(["pip", "install", "--no-deps", *pkg_path_list], capture_output=True, encoding="utf-8", check=True).stdout
        print(output)

    if 0 < len({dependencies}):
        args = ["pip", "install", *{dependencies}]
        output = subprocess.run(args, capture_output=True, encoding="utf-8", check=True).stdout
        print(output)

    # this is base64 encoded source code
    tar_io = io.BytesIO(gzip.decompress(base64.b64decode("{pkg_encoded}")))
    with TemporaryDirectory() as temp_dir:
        with tarfile.open(fileobj=tar_io) as tar:
            for member in tar.getmembers():
                pkg_path = Path(temp_dir) / f"{{member.name}}"
                content_bytes = tar.extractfile(member).read()
                pkg_path.write_bytes(content_bytes)
                output = subprocess.run(["pip", "install", "--no-deps", pkg_path], capture_output=True, encoding="utf-8", check=True).stdout
                print(output)

    sys.path.append("/kaggle/working")
    os.environ.update({env_variables})
__bootstrap__()"""


def create_bootstrap_code(
    pkg_encoded: str,
    pkg_dataset: str,
    env_variables: Dict,
    dependencies: Iterable[str],
    enable_internet: bool = False,
) -> str:
    return BOOTSTRAP_TEMPLATE.format(
        pkg_encoded=pkg_encoded,
        pkg_dataset=pkg_dataset,
        env_variables=json.dumps(env_variables),
        dependencies=json.dumps(dependencies),
        encoding="utf8",
    )

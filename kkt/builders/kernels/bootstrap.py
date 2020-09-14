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
    try:
        from kaggle_secrets import UserSecretsClient
        from kaggle_web_client import BackendError
        has_kaggle_packages = True
    except ImportError:
        has_kaggle_packages = False


    pkg_dataset_path = Path.cwd().parent / "input" / "{pkg_dataset}"

    # install deb packages
    deb_pkgs_path = pkg_dataset_path / "deb"
    deb_path_list = [str(p) for p in deb_pkgs_path.glob("*.deb")]
    if 0 < len(deb_path_list):
        output = subprocess.run(["dpkg", "-i", *deb_path_list], capture_output=True, encoding="utf-8", check=True).stdout
        print(output)

    # install required packages
    pkg_path_list = []
    def _find_pkgs(dir):
        children = list(dir.glob("*"))
        if 0 < len([p.name for p in children if p.name in ["pyproject.toml", "setup.py"]]):
            pkg_path_list.append(str(dir))
            return

        for p in children:
            if p.is_dir():
                _find_pkgs(p)
            else:
                pkg_path_list.append(str(p))
    pip_pkgs_path = pkg_dataset_path / "pip"
    _find_pkgs(pip_pkgs_path)

    if 0 < len(pkg_path_list):
        output = subprocess.run(["pip", "install", "--no-deps", *pkg_path_list], capture_output=True, encoding="utf-8", check=True).stdout
        print(output)

    if {enable_internet} and 0 < len({dependencies}):
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

    # Add secrets to environment variables
    if {enable_internet} and has_kaggle_packages:
        user_secrets = UserSecretsClient()
        for k in {secret_keys}:
            try:
                os.environ[k] = user_secrets.get_secret(k)
            except BackendError:
                pass

    # Update environment variables
    os.environ.update({env_variables})
__bootstrap__()"""


def create_bootstrap_code(
    pkg_encoded: str,
    pkg_dataset: str,
    env_variables: Dict,
    dependencies: Iterable[str],
    secret_keys: Iterable[str],
    enable_internet: bool = False,
) -> str:
    return BOOTSTRAP_TEMPLATE.format(
        pkg_encoded=pkg_encoded,
        pkg_dataset=pkg_dataset,
        env_variables=json.dumps(env_variables),
        dependencies=json.dumps(dependencies),
        secret_keys=json.dumps(secret_keys),
        enable_internet=enable_internet,
        encoding="utf8",
    )

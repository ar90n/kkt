import json
from typing import Dict


BOOTSTRAP_TEMPLATE: str = """def __bootstrap__():
    import sys
    import base64
    import gzip
    import tarfile
    import os
    import io
    from pathlib import Path
    from tempfile import TemporaryDirectory

    # install required packages
    pkg_dataset_path = Path.cwd().parent / "input" / "{pkg_dataset}"
    pkg_path_list = []
    for p in pkg_dataset_path.glob("*"):
        if p.is_dir():
            pkg_config_files = [str(p.parent) for p in p.glob("**/*") if p.name in ["pyproject.toml", "setup.py"]]
            pkg_root_dir = min(pkg_config_files, key=len)
            pkg_path_list.append(pkg_root_dir)
        else:
            pkg_path_list.append(str(p))
    if 0 < len(pkg_path_list):
        pkg_paths = " ".join(pkg_path_list)
        os.system(f"pip install --no-deps {{pkg_paths}}")

    # this is base64 encoded source code
    tar_io = io.BytesIO(gzip.decompress(base64.b64decode("{pkg_encoded}")))
    with TemporaryDirectory() as temp_dir:
        with tarfile.open(fileobj=tar_io) as tar:
            for member in tar.getmembers():
                pkg_path = Path(temp_dir) / f"{{member.name}}"
                content_bytes = tar.extractfile(member).read()
                pkg_path.write_bytes(content_bytes)
                os.system("pip install --no-deps {{pkg_path}}".format(pkg_path=pkg_path))

    sys.path.append("/kaggle/working")
    os.environ.update({env_variables})
__bootstrap__()"""


def create_bootstrap_code(
    pkg_encoded: str,
    pkg_dataset: str,
    env_variables: Dict,
    enable_internet: bool = False,
) -> str:
    return BOOTSTRAP_TEMPLATE.format(
        pkg_encoded=pkg_encoded,
        pkg_dataset=pkg_dataset,
        env_variables=json.dumps(env_variables),
        encoding="utf8",
    )

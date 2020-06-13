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

    # this is base64 encoded source code
    tar_io = io.BytesIO(gzip.decompress(base64.b64decode("{pkg_encoded}")))
    with TemporaryDirectory() as temp_dir:
        with tarfile.open(fileobj=tar_io) as tar:
            for member in tar.getmembers():
                pkg_path = Path(temp_dir) / f"{{member.name}}"
                content_bytes = tar.extractfile(member).read()
                pkg_path.write_bytes(content_bytes)
                os.system("pip install {install_options} {{pkg_path}}".format(pkg_path=pkg_path))

    sys.path.append("/kaggle/working")
    os.environ.update({env_variables})
__bootstrap__()"""


def create_bootstrap_code(
    pkg_encoded: str, env_variables: Dict, enable_internet: bool = False
) -> str:
    install_options = "" if enable_internet else "--no-deps"
    return BOOTSTRAP_TEMPLATE.format(
        pkg_encoded=pkg_encoded,
        install_options=install_options,
        env_variables=json.dumps(env_variables),
        encoding="utf8",
    )

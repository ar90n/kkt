from typing import Dict

BOOTSTRAP_TEMPLATE: str = """def __bootstrap__():
    import sys
    import base64
    import gzip
    import os
    from pathlib import Path
    from tempfile import TemporaryDirectory

    # this is base64 encoded source code
    pkg_encoded: str = "{pkg_encoded}"

    with TemporaryDirectory() as temp_dir:
        pkg_path = Path(temp_dir) / "{pkg_name}"
        pkg_path.write_bytes(gzip.decompress(base64.b64decode(pkg_encoded)))
        os.system("pip install {install_options} {{pkg_path}}".format(pkg_path=pkg_path))

    sys.path.append("/kaggle/working")
    os.environ.update({env_variables})
__bootstrap__()"""


def create_bootstrap_code(
    pkg_name: str, pkg_encoded: str, env_variables: Dict, enable_internet: bool = False
):
    install_options = "" if enable_internet else "--no-deps"
    return BOOTSTRAP_TEMPLATE.format(
        pkg_encoded=pkg_encoded,
        pkg_name=pkg_name,
        install_options=install_options,
        env_variables=env_variables,
        encoding="utf8",
    )

SCRIPT_TEMPLATE: str = """def __bootstrap__():
    import base64
    import gzip
    import os
    from pathlib import Path
    from typing import Dict
    from tempfile import TemporaryDirectory

    def run(command):
        os.system("export PYTHONPATH=${{PYTHONPATH}}:/kaggle/working && " + command)

    # this is base64 encoded source code
    pkg_name: str = "{pkg_name}"
    pkg_encoded: str = "{pkg_encoded}"

    with TemporaryDirectory() as temp_dir:
        pkg_path = Path(temp_dir) / pkg_name
        pkg_path.write_bytes(gzip.decompress(base64.b64decode(pkg_encoded)))
        run("pip install --no-deps {{pkg_path}} -t /kaggle/working".format(pkg_path=pkg_path))

__bootstrap__()

{kernel_body}
"""


def create_script_kernel(kernel_body: str, pkg_name: str, pkg_encoded: str):
    return SCRIPT_TEMPLATE.format(
        pkg_encoded=pkg_encoded,
        pkg_name=pkg_name,
        kernel_body=kernel_body,
        encoding="utf8",
    )

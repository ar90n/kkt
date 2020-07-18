import pytest
import json
from io import StringIO

from kkt.builders import get_builder
from kkt.exception import NotSupportedKernelType


def test_build_script_kernel(virtualenv, chshared_datadir):
    script_kernel_builder = get_builder("script")

    script = """import os
import kkt_test_shared_data
print("ABC:", os.environ.get("ABC"))
print("version:", kkt_test_shared_data.__version__)
"""
    script = script_kernel_builder(
        StringIO(script), "dataset", {"ABC": "1234"}, False, True
    )
    actual = virtualenv.run(f"python -c '{script}'", capture=True)
    actual = "\n".join(actual.split("\n")[6:])

    version = "0.1.0"
    expect = f"""Successfully installed kkt-test-shared-data-{version}
ABC: 1234
version: {version}
"""
    assert expect == actual


def test_build_notebook_kernel(chshared_datadir):
    notebook_kernel_builder = get_builder("notebook")

    base_notebook = {
        "cells": [{"source": ["import sys"], "outputs": [], "cell_type": "code"}]
    }
    str_io = StringIO(json.dumps(base_notebook))
    notebook = notebook_kernel_builder(str_io, "dataset", {}, True, True)
    notebook = json.loads(notebook)
    for cell in notebook["cells"]:
        src = "".join((cell["source"]))
        obj = compile(src, "<string>", "exec")
        assert obj is not None


def test_build_not_supported_kernel(chshared_datadir):
    with pytest.raises(NotSupportedKernelType):
        get_builder("not supported")

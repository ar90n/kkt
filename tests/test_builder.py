import pytest
import json
from io import StringIO

from kkt.builders import get_builder
from kkt.exception import NotSupportedKernelType


def test_build_script_kernel(chshared_datadir):
    script_kernel_builder = get_builder("script")

    str_io = StringIO("import sys")
    script = script_kernel_builder(str_io, {})
    obj = compile(script, "<string>", "exec")
    assert obj is not None


def test_build_notebook_kernel(chshared_datadir):
    notebook_kernel_builder = get_builder("notebook")

    base_notebook = {
        "cells": [{"source": ["import sys"], "outputs": [], "cell_type": "code"}]
    }
    str_io = StringIO(json.dumps(base_notebook))
    notebook = notebook_kernel_builder(str_io, {})
    notebook = json.loads(notebook)
    for cell in notebook["cells"]:
        src = "".join((cell["source"]))
        obj = compile(src, "<string>", "exec")
        assert obj is not None


def test_build_not_supported_kernel(chshared_datadir):
    with pytest.raises(NotSupportedKernelType):
        get_builder("not supported")

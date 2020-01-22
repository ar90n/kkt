import os
import pytest

from kkt.builders.packaging import poetry_packaging

@pytest.fixture
def cwd(datadir):
    lwd = os.getcwd()
    os.chdir(datadir)
    try:
        yield datadir
    finally:
        os.chdir(lwd)

def test_poetry_packaging(cwd):
    pkg_name, pkg_encoded = poetry_packaging()
    assert 'test_packaging-0.1.0-py3-none-any.whl' == pkg_name
    assert pkg_encoded.startswith("H4sIA")

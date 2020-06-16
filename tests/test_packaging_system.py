import pytest

from kkt.builders.packaging_system import build_packages, get_dependencies


def test_build_packages(chshared_datadir):
    pkg = build_packages()
    assert 1 == len(pkg)
    assert "kkt_test_shared_data-0.1.0-py3-none-any.whl" == pkg[0].name
    assert pkg[0].content.startswith(b"PK\x03\x04")


@pytest.mark.parametrize(
    "enable_constraint, expected",
    [(True, ["numpy<2.0.0,>=1.18.0"]), (False, ["numpy"])],
)
def test_get_dependencies(chshared_datadir, enable_constraint, expected):
    dependencies = get_dependencies(enable_constraint)
    assert dependencies == expected

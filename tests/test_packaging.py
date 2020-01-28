from kkt.builders.packaging import poetry_packaging


def test_poetry_packaging(chshared_datadir):
    pkg_name, pkg_encoded = poetry_packaging()
    assert "kkt_test_shared_data-0.1.0-py3-none-any.whl" == pkg_name
    assert pkg_encoded.startswith("H4sIA")

import pytest

from kkt.parser import KktParser
from kkt.exception import KktSectionNotFound, MandatoryKeyNotFound


@pytest.mark.parametrize(
    "given, expected",
    [
        (
            {"name": "normal.toml", "key": "."},
            {
                "meta_data": {
                    "slug": "normal",
                    "competition": "normal",
                    "code_file": "notebook.ipynb",
                    "kernel_type": "notebook",
                    "is_private": False,
                    "enable_gpu": True,
                    "enable_internet": True,
                    "dataset_sources": ["normal_data"],
                    "kernel_data_sources": ["normal"],
                    "competition_sources": ["normal"],
                    "keywords": ["normal"],
                },
                "enable_git_tag": True,
            },
        ),
        (
            {"name": "mandatory.toml", "key": "."},
            {
                "meta_data": {
                    "slug": "mandatory",
                    "code_file": "mandatory.py",
                    "kernel_type": "script",
                    "is_private": True,
                    "enable_gpu": False,
                    "enable_internet": False,
                    "dataset_sources": [],
                    "kernel_data_sources": [],
                    "competition_sources": [],
                    "keywords": [],
                },
                "enable_git_tag": False,
            },
        ),
        (
            {"name": "multi_target.toml", "key": ".first"},
            {
                "meta_data": {
                    "slug": "multi_data_first",
                    "code_file": "notebook.ipynb",
                    "kernel_type": "notebook",
                    "competition": "multi_data",
                    "is_private": False,
                    "enable_gpu": True,
                    "enable_internet": True,
                    "dataset_sources": ["multi_data_data"],
                    "kernel_data_sources": ["multi_data"],
                    "competition_sources": ["multi_data"],
                    "keywords": ["multi_data"],
                },
                "enable_git_tag": False,
            },
        ),
        (
            {"name": "multi_target.toml", "key": ".second"},
            {
                "meta_data": {
                    "slug": "multi_data_second",
                    "code_file": "script.py",
                    "kernel_type": "script",
                    "competition": "multi_data",
                    "is_private": False,
                    "enable_gpu": False,
                    "enable_internet": True,
                    "dataset_sources": ["multi_data_data"],
                    "kernel_data_sources": ["multi_data"],
                    "competition_sources": ["multi_data"],
                    "keywords": ["multi_data"],
                },
                "enable_git_tag": False,
            },
        ),
        (
            {"name": "multi_target.toml", "key": ".first.third"},
            {
                "meta_data": {
                    "slug": "multi_data_first.third",
                    "code_file": "notebook.ipynb",
                    "kernel_type": "notebook",
                    "competition": "multi_data",
                    "is_private": False,
                    "enable_gpu": True,
                    "enable_gpu": True,
                    "enable_internet": True,
                    "dataset_sources": ["multi_data_data"],
                    "kernel_data_sources": ["multi_data"],
                    "competition_sources": ["multi_data"],
                    "keywords": ["multi_data"],
                },
                "enable_git_tag": False,
            },
        ),
    ],
)
def test_kkt_parser_read(given, expected, chdatadir):
    path = chdatadir / given["name"]
    parser = KktParser(path)
    assert parser.path == path

    kkt = parser.read(key=given["key"])
    assert kkt == expected


@pytest.mark.parametrize(
    "given, expected",
    [
        ({"name": "empty.toml"}, KktSectionNotFound),
        ({"name": "no_mandatory.toml"}, MandatoryKeyNotFound),
    ],
)
def test_kkt_parser_failed(given, expected, chdatadir):
    path = chdatadir / given["name"]
    parser = KktParser(path)

    with pytest.raises(expected):
        parser.read()


@pytest.mark.parametrize("given", ["normal.toml"])
def test_kkt_parser_write(given, chdatadir):
    path = chdatadir / given
    parser = KktParser(path)

    kkt = {**parser.read(), "slug": "modify"}
    parser.write(kkt)

    kkt2 = parser.read()
    assert kkt == kkt2

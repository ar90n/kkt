# from kaggle_kernel_tool import __version__
# from kaggle_kernel_tool.parser import KktParser
#
#
# def test_version():
#    assert __version__ == "0.1.0"
#
#
# def test_pyproject_parse(pyproject_data):
#    pyproject_path = pyproject_data["path"]
#    expect = pyproject_data["expect"]
#
#    parser = KktParser(pyproject_path)
#    assert pyproject_path == parser.path
#
#    actual = parser.read()
#    assert expect["slug"] == actual["slug"]
#    assert expect["title"] == actual["title"]
#    assert expect["competition"] == actual["competition"]
#
#
# def test_kernel_push():
#    pass

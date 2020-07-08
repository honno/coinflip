"""Interfacing for examples_iter

An option `--example <regex>` allows developers to pass a regular expression to
filter the examples being tested in methods named `test_randtest_on_example`
(i.e. in `test_examples.py`).
"""
from .examples import Example
from .examples import examples_iter


def pytest_addoption(parser):
    parser.addoption(
        "--example", action="store", default=".*",
    )


def pytest_generate_tests(metafunc):
    if metafunc.function.__name__ == "test_randtest_on_example":
        title_substr = metafunc.config.getoption("example")
        metafunc.parametrize(Example._fields, examples_iter(title_substr))

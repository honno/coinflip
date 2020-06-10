from .test_examples import Example
from .test_examples import iterexamples
from .test_examples import test_stattest_on_example

__all__ = ["parametrize_example_tests"]


def parametrize_example_tests(metafunc):
    title_substr = metafunc.config.getoption("example")
    metafunc.parametrize(Example._fields, iterexamples(title_substr))


def pytest_addoption(parser):
    parser.addoption(
        "--example", action="store", default=None,
    )


def pytest_generate_tests(metafunc):
    if metafunc.function is test_stattest_on_example:
        parametrize_example_tests(metafunc)

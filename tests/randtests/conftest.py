from .examples import Example
from .examples import examples_iter


def pytest_addoption(parser):
    parser.addoption(
        "--example", action="store", default=".*",
    )


def pytest_generate_tests(metafunc):
    if metafunc.function.__name__ == "test_stattest_on_example":
        title_substr = metafunc.config.getoption("example")
        metafunc.parametrize(Example._fields, examples_iter(title_substr))

from ..conftest import parametrize_example_tests
from .test_dj import test_stattest_on_example


def pytest_generate_tests(metafunc):
    if metafunc.function is test_stattest_on_example:
        parametrize_example_tests(metafunc)

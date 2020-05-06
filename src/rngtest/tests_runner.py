from click import echo

from rngtest.stattests.frequency import frequency
from rngtest.stattests.runs import runs

__all__ = ["ls_tests", "run_test", "run_all_tests"]


STATTESTS = [
    frequency,
    # frequency_in_block,
    runs,
    # runs_in_block,
]


def ls_tests():
    for stattest in STATTESTS:
        name = stattest.__name__

        yield name


def run_test(series, stattest_str):
    for func in STATTESTS:
        if stattest_str == func.__name__:
            _run_test(series, func)
            break


def _run_test(series, stattest):
    result = stattest(series)
    echo(str(result))


def run_all_tests(series):
    for stattest in STATTESTS:
        _run_test(series, stattest)

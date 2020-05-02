from prng.stattests.frequency import frequency
from prng.stattests.frequency import frequency_in_block
from prng.stattests.runs import runs
from prng.stattests.runs import runs_in_block

__all__ = ["ls_tests", "run_test", "run_all_tests"]


STATTESTS = [
    frequency,
    frequency_in_block,
    runs,
    runs_in_block,
]


def ls_tests():
    for stattest in STATTESTS:
        name = stattest.__name__

        yield name


def run_test(series, test: str):
    for stattest in STATTESTS:
        if test == stattest.__name__:
            stattest(series)
            break


def run_all_tests(series):
    for stattest in STATTESTS:
        _run_test(series, stattest)

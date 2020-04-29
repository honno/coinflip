from prng.stattests.frequency import frequency
from prng.stattests.frequency import frequency_in_block
from prng.stattests.runs import runs
from prng.stattests.runs import runs_in_block

__all__ = ["run_tests"]


def run_tests(s):
    frequency(s)
    frequency_in_block(s)
    runs(s)
    runs_in_block(s)

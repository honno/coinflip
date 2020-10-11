import pytest

from coinflip import generators
from coinflip.tests_runner import list_tests

# TODO make this deterministic
RNG = generators.python()
bits = [next(RNG) for _ in range(1000000)]

randtests = [func for _, func in list_tests()]


@pytest.mark.parametrize(["randtest"], [(randtest,) for randtest in randtests])
@pytest.mark.timeout(300)  # i.e. 5 minutes
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_million_bits(randtest):
    randtest(bits)

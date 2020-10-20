from pytest import mark

from coinflip import generators
from coinflip.tests_runner import list_tests

# TODO make this deterministic
RNG = generators.python()
bits = [next(RNG) for _ in range(1000000)]

randtests = [func for _, func in list_tests()]


@mark.parametrize(["randtest"], [(randtest,) for randtest in randtests])
@mark.timeout(120)  # i.e. 2 minutes
def test_million_bits(randtest):
    randtest(bits)

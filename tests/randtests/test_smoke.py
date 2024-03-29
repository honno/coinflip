from pytest import mark

from coinflip import generators
from coinflip.cli.runner import list_tests

# TODO make this deterministic for Hypothesis
RNG = generators.Python()
bits = [next(RNG) for _ in range(1000000)]

randtests = [(func,) for _, func in list_tests()]


@mark.parametrize(["randtest"], randtests)
@mark.timeout(1)
def test_thousand_bits(randtest):
    randtest(bits[:1000])


@mark.slow
@mark.parametrize(["randtest"], randtests)
@mark.timeout(300)  # 5 minutes
def test_million_bits(randtest):
    randtest(bits)

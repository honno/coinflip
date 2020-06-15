from functools import wraps

from . import Implementation
from .r4nd0m.SourceCode.RandomnessTests import RandomnessTester

__all__ = ["testmap"]

_tester = RandomnessTester(None)


def bits_str(stattest):
    @wraps(stattest)
    def wrapper(bits, *args, **kwargs):
        bits_str = "".join(str(bit) for bit in bits)

        result = stattest(bits_str, *args, **kwargs)

        return result

    return wrapper


@bits_str
def monobits(bits):
    return _tester.monobit(bits)


@bits_str
def frequency_within_block(bits, blocksize=128):
    return _tester.block_frequency(bits, block_size=blocksize)


@bits_str
def runs(bits):
    return _tester.independent_runs(bits)


@bits_str
def longest_runs(bits):
    return _tester.longest_runs(bits)


@bits_str
def discrete_fourier_transform(bits):
    return _tester.spectral(bits)


@bits_str
def binary_matrix_rank(bits, nrows=32, ncols=32):
    if nrows != ncols:
        raise NotImplementedError()

    return _tester.matrix_rank(bits, nrows)


@bits_str
def non_overlapping_template_matching(
    bits, template=[0, 0, 0, 0, 0, 0, 0, 0, 1], nblocks=8
):
    template_str = "".join(str(bit) for bit in template)

    return _tester.non_overlapping_patterns(
        bits, pattern=template_str, num_blocks=nblocks
    )


@bits_str
def overlapping_template_matching(bits, blocksize=1032):
    return _tester.overlapping_patterns(bits, block_size=blocksize)


@bits_str
def maurers_universal(bits):
    return _tester.universal(bits)


testmap = {
    "monobits": Implementation(monobits),
    "frequency_within_block": Implementation(frequency_within_block),
    "runs": Implementation(runs),
    "longest_runs": Implementation(longest_runs),
    "discrete_fourier_transform": Implementation(discrete_fourier_transform),
    "binary_matrix_rank": Implementation(binary_matrix_rank),
    "non_overlapping_template_matching": Implementation(
        non_overlapping_template_matching
    ),
    "overlapping_template_matching": Implementation(
        overlapping_template_matching, fixedkwargs={"template": [1 for _ in range(9)]}
    ),
    "maurers_universal": Implementation(
        maurers_universal, missingkwargs=["blocksize", "init_nblocks"]
    ),
}

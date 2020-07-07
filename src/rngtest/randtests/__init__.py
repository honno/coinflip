"""Statistical tests for randomness"""
from rngtest.randtests.fourier import discrete_fourier_transform
from rngtest.randtests.frequency import frequency_within_block
from rngtest.randtests.frequency import monobits
from rngtest.randtests.matrix import binary_matrix_rank
from rngtest.randtests.runs import longest_runs
from rngtest.randtests.runs import runs
from rngtest.randtests.template import non_overlapping_template_matching
from rngtest.randtests.template import overlapping_template_matching
from rngtest.randtests.universal import maurers_universal

__all__ = [
    "monobits",
    "frequency_within_block",
    "runs",
    "longest_runs",
    "binary_matrix_rank",
    "discrete_fourier_transform",
    "non_overlapping_template_matching",
    "overlapping_template_matching",
    "maurers_universal",
]

from rngtest.stattests.fourier import discrete_fourier_transform
from rngtest.stattests.frequency import frequency_within_block
from rngtest.stattests.frequency import monobits
from rngtest.stattests.matrix import binary_matrix_rank
from rngtest.stattests.runs import longest_runs
from rngtest.stattests.runs import runs
from rngtest.stattests.template import non_overlapping_template_matching
from rngtest.stattests.template import overlapping_template_matching
from rngtest.stattests.universal import maurers_universal

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

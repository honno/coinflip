from coinflip._randtests.complexity import linear_complexity
from coinflip._randtests.cusum import cusum
from coinflip._randtests.entropy import approximate_entropy
from coinflip._randtests.excursions import random_excursions
from coinflip._randtests.excursions import random_excursions_variant
from coinflip._randtests.fourier import spectral
from coinflip._randtests.frequency import frequency_within_block
from coinflip._randtests.frequency import monobit
from coinflip._randtests.matrix import binary_matrix_rank
from coinflip._randtests.runs import longest_runs
from coinflip._randtests.runs import runs
from coinflip._randtests.serial import serial
from coinflip._randtests.template import non_overlapping_template_matching
from coinflip._randtests.template import overlapping_template_matching
from coinflip._randtests.universal import maurers_universal

__all__ = [
    "monobit",
    "frequency_within_block",
    "runs",
    "longest_runs",
    "binary_matrix_rank",
    "spectral",
    "non_overlapping_template_matching",
    "overlapping_template_matching",
    "maurers_universal",
    "linear_complexity",
    "serial",
    "approximate_entropy",
    "cusum",
    "random_excursions",
    "random_excursions_variant",
]

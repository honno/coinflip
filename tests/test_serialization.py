import pickle

from hypothesis import given
from hypothesis import strategies as st
from pytest import mark

from coinflip._randtests.common.typing import *
from coinflip._randtests.cusum import CusumTestResult
from coinflip._randtests.entropy import ApproximateEntropyTestResult
from coinflip._randtests.excursions import RandomExcursionsMultiTestResult
from coinflip._randtests.excursions import RandomExcursionsVariantMultiTestResult
from coinflip._randtests.fourier import SpectralTestResult
from coinflip._randtests.frequency import FrequencyWithinBlockTestResult
from coinflip._randtests.frequency import MonobitTestResult
from coinflip._randtests.matrix import BinaryMatrixRankTestResult
from coinflip._randtests.runs import LongestRunsTestResult
from coinflip._randtests.runs import RunsTestResult
from coinflip._randtests.serial import SerialMultiTestResult
from coinflip._randtests.template import NonOverlappingTemplateMatchingMultiTestResult
from coinflip._randtests.template import OverlappingTemplateMatchingTestResult
from coinflip._randtests.universal import UniversalTestResult
from coinflip.collections import Bins


def test_bins_pickle():
    bins = Bins([0, 1, 2, 3, 4])
    bins[100] += 1

    pickled_bins = pickle.dumps(bins)

    bins2 = pickle.loads(pickled_bins)

    assert bins2 == bins


# TODO expand this
st.register_type_strategy(
    Face,
    st.one_of(st.booleans(), st.characters(), st.floats(), st.integers(), st.text()),
)


@mark.parametrize(
    "cls",
    [
        MonobitTestResult,
        FrequencyWithinBlockTestResult,
        RunsTestResult,
        LongestRunsTestResult,
        BinaryMatrixRankTestResult,
        SpectralTestResult,
        NonOverlappingTemplateMatchingMultiTestResult,
        OverlappingTemplateMatchingTestResult,
        UniversalTestResult,
        SerialMultiTestResult,
        ApproximateEntropyTestResult,
        CusumTestResult,
        RandomExcursionsMultiTestResult,
        RandomExcursionsVariantMultiTestResult,
    ],
)
@given(st.data())
def test_results(cls, data):
    data.draw(st.builds(cls))

from dataclasses_json.cfg import global_config
from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st
from pytest import mark

import coinflip.serialize
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
from coinflip.typing import *

print(global_config.encoders)

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
def test_serialization(cls, data):
    try:
        result = data.draw(st.builds(cls))
    except IndexError:  # building array-likes with no elements TODO filter strategy
        assume(False)

    result.to_json()

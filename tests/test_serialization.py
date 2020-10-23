import json
from dataclasses import asdict
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import numpy as np
from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st
from pytest import mark
from rich import inspect

from coinflip._randtests.common.result import TestResult
from coinflip._randtests.cusum import CusumTestResult
from coinflip._randtests.entropy import ApproximateEntropyTestResult
from coinflip._randtests.excursions import RandomExcursionsTestResult
from coinflip._randtests.excursions import RandomExcursionsVariantTestResult
from coinflip._randtests.fourier import SpectralTestResult
from coinflip._randtests.frequency import FrequencyWithinBlockTestResult
from coinflip._randtests.frequency import MonobitTestResult
from coinflip._randtests.matrix import BinaryMatrixRankTestResult
from coinflip._randtests.runs import LongestRunsTestResult
from coinflip._randtests.runs import RunsTestResult
from coinflip._randtests.serial import FirstSerialTestResult
from coinflip._randtests.serial import SecondSerialTestResult
from coinflip._randtests.template import NonOverlappingTemplateMatchingTestResult
from coinflip._randtests.template import OverlappingTemplateMatchingTestResult
from coinflip._randtests.universal import UniversalTestResult


@st.composite
def any(draw):
    strategy = draw(
        st.sampled_from([st.booleans, st.characters, st.floats, st.integers, st.text,])
    )

    return draw(strategy())


@st.composite
def integers(draw, *args, **kwargs):
    _num = draw(st.integers(*args, **kwargs))
    cls = draw(st.sampled_from([int, np.int64]))

    try:
        num = cls(_num)
    except OverflowError:
        num = _num

    return num


@st.composite
def floats(draw, *args, **kwargs):
    _num = draw(st.floats(*args, **kwargs))
    cls = draw(st.sampled_from([float, np.float64]))

    return cls(_num)


st.register_type_strategy(Any, any())
st.register_type_strategy(int, integers())
st.register_type_strategy(float, floats())


# FAILING https://github.com/lidatong/dataclasses-json/issues/250
@mark.parametrize(
    "cls",
    [
        MonobitTestResult,
        FrequencyWithinBlockTestResult,
        RunsTestResult,
        LongestRunsTestResult,
        BinaryMatrixRankTestResult,
        SpectralTestResult,
        NonOverlappingTemplateMatchingTestResult,
        OverlappingTemplateMatchingTestResult,
        UniversalTestResult,
        FirstSerialTestResult,
        SecondSerialTestResult,
        ApproximateEntropyTestResult,
        CusumTestResult,
        RandomExcursionsTestResult,
        RandomExcursionsVariantTestResult,
    ],
)
@given(data=st.data())
def test_results(cls, data):
    try:
        result = data.draw(st.builds(cls))
    except IndexError:  # building array-likes with no elements TODO filter strategy
        assume(False)

    result.to_json()

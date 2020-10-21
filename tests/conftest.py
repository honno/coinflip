"""Settings profiles for hypothesis tests

Defines profiles which can be accessed by the `--hypothesis-profile=<profile>`
option in the `pytest` CLI.

Notes
-----
See `hypothesis settings profile guide
https://hypothesis.readthedocs.io/en/latest/settings.html?highlight=profiles#settings-profiles`_
for more information on profiles.
"""
from datetime import timedelta

from hypothesis import settings
from pytest import mark

settings.register_profile(
    "fast", max_examples=2, stateful_step_count=4, deadline=timedelta(minutes=2)
)

settings.register_profile(
    "debug", max_examples=1, stateful_step_count=1, deadline=timedelta(minutes=5)
)


def pytest_addoption(parser):
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="Run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-slow"):
        skip_slow = mark.skip(reason="Needs --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

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

from hypothesis import Phase
from hypothesis import settings

settings.register_profile(
    "ci",
    max_examples=1,
    stateful_step_count=1,
    deadline=timedelta(minutes=2),
    phases=(Phase.reuse, Phase.generate, Phase.target),
)

settings.register_profile("slow", deadline=timedelta(hours=1))

settings.register_profile(
    "fast", max_examples=1, stateful_step_count=1, deadline=timedelta(minutes=2)
)
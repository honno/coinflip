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

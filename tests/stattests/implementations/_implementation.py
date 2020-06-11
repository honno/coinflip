from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import NamedTuple

__all__ = ["Implementation"]


class Implementation(NamedTuple):
    stattest: Callable
    missingkwargs: List[str] = []
    fixedkwargs: Dict[str, Any] = {}

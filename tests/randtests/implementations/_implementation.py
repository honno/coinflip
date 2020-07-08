from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import NamedTuple

__all__ = ["Implementation", "ImplementationError"]


class Implementation(NamedTuple):
    """Contains template for specifying a randtest implementation"""

    randtest: Callable
    missingkwargs: List[str] = []
    fixedkwargs: Dict[str, Any] = {}


class ImplementationError(NotImplementedError):
    """Error raised when an implemention has allowed input it cannot process"""

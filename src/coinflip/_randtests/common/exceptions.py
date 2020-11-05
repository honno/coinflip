__all__ = [
    "TestError",
    "TestNotImplementedError",
    "TestInputError",
    "NonBinarySequenceError",
]


class TestError(Exception):
    """Base class for test-related errors"""


class TestNotImplementedError(TestError, NotImplementedError):
    """Error if test is not implemented to handle valid parameters"""


class TestInputError(TestError, ValueError):
    """Error if test cannot handle (invalid) parameters"""


class NonBinarySequenceError(TestInputError):
    """Error if sequence does not contain only 2 distinct values"""

    def __str__(self):
        return "Sequence does not contain only 2 distinct values (i.e. binary)"

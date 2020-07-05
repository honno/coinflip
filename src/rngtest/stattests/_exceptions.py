__all__ = [
    "TestError",
    "TestNotImplementedError",
    "TestInputError",
    "NonBinarySequenceError",
]


class TestError(Exception):
    pass


class TestNotImplementedError(TestError, NotImplementedError):
    pass


class TestInputError(TestError, ValueError):
    pass


class NonBinarySequenceError(TestInputError):
    """Error if sequence does not contain only 2 values"""

    def __str__(self):
        return "Sequence does not contain only 2 values (i.e. binary)"

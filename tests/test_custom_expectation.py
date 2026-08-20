"""Test that custom expectations can be added easily."""

import pandas as pd

from dqlite.core.engine import validate
from dqlite.core.result import ExpectationResult
from dqlite.expectations.base import Expectation
from dqlite.backends.base import Backend
from dqlite import expect


class IsEvenExpectation(Expectation):
    """Example custom expectation: values must be even numbers."""

    def __init__(self, column: str):
        self.column = column

    @property
    def expectation_type(self) -> str:
        return "is_even"

    def evaluate(self, data, backend: Backend) -> ExpectationResult:
        df = data
        series = df[self.column]
        odd_count = int((series % 2 != 0).sum())
        total = len(df)

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=self.column,
            success=odd_count == 0,
            unexpected_count=odd_count,
            unexpected_percent=(odd_count / total * 100) if total > 0 else 0,
            details={"odd_values_found": odd_count},
        )


class TestCustomExpectations:
    """Test that users can easily extend dq-lite."""

    def test_custom_expectation_passes(self):
        df = pd.DataFrame({"num": [2, 4, 6, 8]})
        result = validate(df, expectations=[IsEvenExpectation("num")])
        assert result.success is True

    def test_custom_expectation_fails(self):
        df = pd.DataFrame({"num": [2, 3, 6, 8]})
        result = validate(df, expectations=[IsEvenExpectation("num")])
        assert result.success is False
        assert result.results[0].unexpected_count == 1

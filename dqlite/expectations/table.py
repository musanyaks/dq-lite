"""Table-level expectations."""

from typing import Any

from dqlite.expectations.base import Expectation
from dqlite.core.result import ExpectationResult
from dqlite.backends.base import Backend


class TableExpectationBuilder:
    """Fluent builder for table expectations."""

    def row_count(self) -> "RowCountBuilder":
        return RowCountBuilder()

    def column_count(self, expected: int) -> "ColumnCountExpectation":
        return ColumnCountExpectation(expected)

    def has_columns(self, columns: list) -> "HasColumnsExpectation":
        return HasColumnsExpectation(columns)


class RowCountBuilder:
    """Intermediate builder for row count constraints."""

    def between(self, min_val: int, max_val: int) -> "RowCountBetweenExpectation":
        return RowCountBetweenExpectation(min_val, max_val)

    def greater_than(self, threshold: int) -> "RowCountGreaterThanExpectation":
        return RowCountGreaterThanExpectation(threshold)


class RowCountBetweenExpectation(Expectation):
    """Expect row count to be within range."""

    def __init__(self, min_val: int, max_val: int):
        self.min_val = min_val
        self.max_val = max_val

    @property
    def expectation_type(self) -> str:
        return "row_count_between"

    def evaluate(self, data: Any, backend: Backend) -> ExpectationResult:
        count = backend.get_row_count(data)
        in_range = self.min_val <= count <= self.max_val

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=None,
            success=in_range,
            unexpected_count=0 if in_range else abs(count - self.min_val),
            details={"min": self.min_val, "max": self.max_val, "actual": count},
        )


class RowCountGreaterThanExpectation(Expectation):
    """Expect row count to exceed threshold."""

    def __init__(self, threshold: int):
        self.threshold = threshold

    @property
    def expectation_type(self) -> str:
        return "row_count_greater_than"

    def evaluate(self, data: Any, backend: Backend) -> ExpectationResult:
        count = backend.get_row_count(data)
        passes = count > self.threshold

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=None,
            success=passes,
            unexpected_count=0 if passes else self.threshold - count,
            details={"threshold": self.threshold, "actual": count},
        )


class ColumnCountExpectation(Expectation):
    """Expect specific number of columns."""

    def __init__(self, expected: int):
        self.expected = expected

    @property
    def expectation_type(self) -> str:
        return "column_count"

    def evaluate(self, data: Any, backend: Backend) -> ExpectationResult:
        count = backend.get_column_count(data)
        matches = count == self.expected

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=None,
            success=matches,
            unexpected_count=0 if matches else abs(count - self.expected),
            details={"expected": self.expected, "actual": count},
        )


class HasColumnsExpectation(Expectation):
    """Expect table to contain specific columns."""

    def __init__(self, columns: list):
        self.columns = columns

    @property
    def expectation_type(self) -> str:
        return "has_columns"

    def evaluate(self, data: Any, backend: Backend) -> ExpectationResult:
        existing = set(backend.get_column_names(data))
        missing = [c for c in self.columns if c not in existing]

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=None,
            success=len(missing) == 0,
            unexpected_count=len(missing),
            details={"required": self.columns, "missing": missing, "found": list(existing)},
        )


def expect_table() -> TableExpectationBuilder:
    """Entry point for table expectations."""
    return TableExpectationBuilder()

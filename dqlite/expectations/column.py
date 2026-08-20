"""Column-level expectations."""

from typing import Any, Optional, List, Union, Pattern
import re

from dqlite.expectations.base import Expectation
from dqlite.core.result import ExpectationResult
from dqlite.backends.base import Backend


class ColumnExpectationBuilder:
    """Fluent builder for column expectations."""

    def __init__(self, column: str):
        self.column = column

    def not_null(self) -> "NotNullExpectation":
        return NotNullExpectation(self.column)

    def unique(self) -> "UniqueExpectation":
        return UniqueExpectation(self.column)

    def between(self, min_val: Any, max_val: Any) -> "BetweenExpectation":
        return BetweenExpectation(self.column, min_val, max_val)

    def in_set(self, allowed: List[Any]) -> "InSetExpectation":
        return InSetExpectation(self.column, allowed)

    def matches_regex(self, pattern: Union[str, Pattern]) -> "RegexMatchExpectation":
        return RegexMatchExpectation(self.column, pattern)

    def type_(self, expected_type: str) -> "TypeExpectation":
        return TypeExpectation(self.column, expected_type)


class NotNullExpectation(Expectation):
    """Expect column values to be non-null."""

    def __init__(self, column: str):
        self.column = column

    @property
    def expectation_type(self) -> str:
        return "not_null"

    def evaluate(self, data: Any, backend: Backend) -> ExpectationResult:
        null_count, total = backend.count_nulls(data, self.column)
        unexpected = null_count

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=self.column,
            success=unexpected == 0,
            unexpected_count=unexpected,
            unexpected_percent=(unexpected / total * 100) if total > 0 else 0,
            details={"null_count": null_count, "total_rows": total},
        )


class UniqueExpectation(Expectation):
    """Expect column values to be unique."""

    def __init__(self, column: str):
        self.column = column

    @property
    def expectation_type(self) -> str:
        return "unique"

    def evaluate(self, data: Any, backend: Backend) -> ExpectationResult:
        duplicate_count, total = backend.count_duplicates(data, self.column)

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=self.column,
            success=duplicate_count == 0,
            unexpected_count=duplicate_count,
            unexpected_percent=(duplicate_count / total * 100) if total > 0 else 0,
            details={"duplicate_count": duplicate_count, "total_rows": total},
        )


class BetweenExpectation(Expectation):
    """Expect numeric values to fall within a range."""

    def __init__(self, column: str, min_val: Any, max_val: Any):
        self.column = column
        self.min_val = min_val
        self.max_val = max_val

    @property
    def expectation_type(self) -> str:
        return "between"

    def evaluate(self, data: Any, backend: Backend) -> ExpectationResult:
        out_of_range, total = backend.count_out_of_range(
            data, self.column, self.min_val, self.max_val
        )

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=self.column,
            success=out_of_range == 0,
            unexpected_count=out_of_range,
            unexpected_percent=(out_of_range / total * 100) if total > 0 else 0,
            details={
                "min": self.min_val,
                "max": self.max_val,
                "out_of_range": out_of_range,
            },
        )


class InSetExpectation(Expectation):
    """Expect values to be within an allowed set."""

    def __init__(self, column: str, allowed: List[Any]):
        self.column = column
        self.allowed = set(allowed)

    @property
    def expectation_type(self) -> str:
        return "in_set"

    def evaluate(self, data: Any, backend: Backend) -> ExpectationResult:
        unexpected, total = backend.count_not_in_set(data, self.column, self.allowed)

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=self.column,
            success=unexpected == 0,
            unexpected_count=unexpected,
            unexpected_percent=(unexpected / total * 100) if total > 0 else 0,
            details={"allowed": list(self.allowed), "unexpected": unexpected},
        )


class RegexMatchExpectation(Expectation):
    """Expect string values to match a regex pattern."""

    def __init__(self, column: str, pattern: Union[str, re.Pattern]):
        self.column = column
        self.pattern = pattern if isinstance(pattern, str) else pattern.pattern

    @property
    def expectation_type(self) -> str:
        return "matches_regex"

    def evaluate(self, data: Any, backend: Backend) -> ExpectationResult:
        non_matching, total = backend.count_regex_mismatch(data, self.column, self.pattern)

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=self.column,
            success=non_matching == 0,
            unexpected_count=non_matching,
            unexpected_percent=(non_matching / total * 100) if total > 0 else 0,
            details={"pattern": self.pattern, "non_matching": non_matching},
        )


class TypeExpectation(Expectation):
    """Expect column to have a specific dtype."""

    def __init__(self, column: str, expected_type: str):
        self.column = column
        self.expected_type = expected_type

    @property
    def expectation_type(self) -> str:
        return "type_"

    def evaluate(self, data: Any, backend: Backend) -> ExpectationResult:
        actual_type = backend.get_column_type(data, self.column)
        matches = actual_type == self.expected_type

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=self.column,
            success=matches,
            unexpected_count=0 if matches else 1,
            unexpected_percent=0 if matches else 100,
            details={"expected": self.expected_type, "actual": actual_type},
        )

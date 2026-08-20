"""dq-lite: Lightweight data quality validation framework."""

from dqlite.core.engine import validate
from dqlite.core.result import ValidationResult
from dqlite.expectations.column import ColumnExpectationBuilder


def expect(column_name: str) -> ColumnExpectationBuilder:
    """Entry point for building column expectations."""
    return ColumnExpectationBuilder(column_name)


__all__ = ["validate", "ValidationResult", "expect"]

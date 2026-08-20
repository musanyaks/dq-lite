"""Abstract backend interface."""

from abc import ABC, abstractmethod
from typing import Any, Set, Tuple


class Backend(ABC):
    """Abstract base for execution backends."""

    @abstractmethod
    def count_nulls(self, data: Any, column: str) -> Tuple[int, int]:
        """Return (null_count, total_rows)."""
        pass

    @abstractmethod
    def count_duplicates(self, data: Any, column: str) -> Tuple[int, int]:
        """Return (duplicate_count, total_rows)."""
        pass

    @abstractmethod
    def count_out_of_range(
        self, data: Any, column: str, min_val: Any, max_val: Any
    ) -> Tuple[int, int]:
        """Return (out_of_range_count, total_rows)."""
        pass

    @abstractmethod
    def count_not_in_set(self, data: Any, column: str, allowed: Set) -> Tuple[int, int]:
        """Return (unexpected_count, total_rows)."""
        pass

    @abstractmethod
    def count_regex_mismatch(self, data: Any, column: str, pattern: str) -> Tuple[int, int]:
        """Return (non_matching_count, total_rows)."""
        pass

    @abstractmethod
    def get_column_type(self, data: Any, column: str) -> str:
        """Return column dtype as string."""
        pass

    @abstractmethod
    def get_row_count(self, data: Any) -> int:
        """Return total row count."""
        pass

    @abstractmethod
    def get_column_count(self, data: Any) -> int:
        """Return total column count."""
        pass

    @abstractmethod
    def get_column_names(self, data: Any) -> list:
        """Return list of column names."""
        pass

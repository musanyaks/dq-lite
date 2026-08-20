"""Polars execution backend — community contribution welcome."""

from typing import Any, Set, Tuple

from dqlite.backends.base import Backend


class PolarsBackend(Backend):
    """Backend for Polars DataFrames."""

    def count_nulls(self, data: Any, column: str) -> Tuple[int, int]:
        raise NotImplementedError("Polars backend: implement count_nulls")

    def count_duplicates(self, data: Any, column: str) -> Tuple[int, int]:
        raise NotImplementedError("Polars backend: implement count_duplicates")

    def count_out_of_range(
        self, data: Any, column: str, min_val: Any, max_val: Any
    ) -> Tuple[int, int]:
        raise NotImplementedError("Polars backend: implement count_out_of_range")

    def count_not_in_set(self, data: Any, column: str, allowed: Set) -> Tuple[int, int]:
        raise NotImplementedError("Polars backend: implement count_not_in_set")

    def count_regex_mismatch(self, data: Any, column: str, pattern: str) -> Tuple[int, int]:
        raise NotImplementedError("Polars backend: implement count_regex_mismatch")

    def get_column_type(self, data: Any, column: str) -> str:
        raise NotImplementedError("Polars backend: implement get_column_type")

    def get_row_count(self, data: Any) -> int:
        raise NotImplementedError("Polars backend: implement get_row_count")

    def get_column_count(self, data: Any) -> int:
        raise NotImplementedError("Polars backend: implement get_column_count")

    def get_column_names(self, data: Any) -> list:
        raise NotImplementedError("Polars backend: implement get_column_names")

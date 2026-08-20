"""Pandas execution backend."""

from typing import Any, Tuple, Set
import re

from dqlite.backends.base import Backend


class PandasBackend(Backend):
    """Backend for pandas DataFrames."""

    def _get_df(self, data: Any):
        return data

    def count_nulls(self, data: Any, column: str) -> Tuple[int, int]:
        df = self._get_df(data)
        null_count = int(df[column].isna().sum())
        total = len(df)
        return null_count, total

    def count_duplicates(self, data: Any, column: str) -> Tuple[int, int]:
        df = self._get_df(data)
        total = len(df)
        unique = df[column].nunique()
        duplicate_count = total - unique
        return duplicate_count, total

    def count_out_of_range(
        self, data: Any, column: str, min_val: Any, max_val: Any
    ) -> Tuple[int, int]:
        df = self._get_df(data)
        series = df[column]
        # Handle nulls gracefully
        mask = series.notna() & ((series < min_val) | (series > max_val))
        out_of_range = int(mask.sum())
        total = len(df)
        return out_of_range, total

    def count_not_in_set(self, data: Any, column: str, allowed: Set) -> Tuple[int, int]:
        df = self._get_df(data)
        series = df[column]
        mask = series.notna() & (~series.isin(allowed))
        unexpected = int(mask.sum())
        total = len(df)
        return unexpected, total

    def count_regex_mismatch(self, data: Any, column: str, pattern: str) -> Tuple[int, int]:
        df = self._get_df(data)
        series = df[column].astype(str)
        # Nulls are considered non-matching
        regex = re.compile(pattern)
        mask = series.notna() & (~series.apply(lambda x: bool(regex.match(x))))
        non_matching = int(mask.sum())
        total = len(df)
        return non_matching, total

    def get_column_type(self, data: Any, column: str) -> str:
        df = self._get_df(data)
        return str(df[column].dtype)

    def get_row_count(self, data: Any) -> int:
        return len(self._get_df(data))

    def get_column_count(self, data: Any) -> int:
        return len(self._get_df(data).columns)

    def get_column_names(self, data: Any) -> list:
        return list(self._get_df(data).columns)

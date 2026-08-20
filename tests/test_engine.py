"""Tests for the validation engine."""

import pytest
import pandas as pd

from dqlite.core.engine import validate
from dqlite.core.result import ValidationResult
from dqlite import expect
from dqlite.expectations.table import expect_table


class TestValidate:
    """Test suite for validate() function."""

    def test_empty_dataframe_passes_no_expectations(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = validate(df, expectations=[])
        assert isinstance(result, ValidationResult)
        assert result.success is True

    def test_not_null_expectation_passes(self):
        df = pd.DataFrame({"id": [1, 2, 3]})
        result = validate(df, expectations=[
            expect("id").not_null()
        ])
        assert result.success is True
        assert result.results[0].unexpected_count == 0

    def test_not_null_expectation_fails(self):
        df = pd.DataFrame({"id": [1, None, 3]})
        result = validate(df, expectations=[
            expect("id").not_null()
        ])
        assert result.success is False
        assert result.results[0].unexpected_count == 1

    def test_between_expectation_passes(self):
        df = pd.DataFrame({"age": [0, 50, 120]})
        result = validate(df, expectations=[
            expect("age").between(0, 120)
        ])
        assert result.success is True

    def test_between_expectation_fails(self):
        df = pd.DataFrame({"age": [-5, 50, 200]})
        result = validate(df, expectations=[
            expect("age").between(0, 120)
        ])
        assert result.success is False
        assert result.results[0].unexpected_count == 2

    def test_unique_expectation_passes(self):
        df = pd.DataFrame({"email": ["a@x.com", "b@x.com", "c@x.com"]})
        result = validate(df, expectations=[
            expect("email").unique()
        ])
        assert result.success is True

    def test_unique_expectation_fails(self):
        df = pd.DataFrame({"email": ["a@x.com", "a@x.com", "c@x.com"]})
        result = validate(df, expectations=[
            expect("email").unique()
        ])
        assert result.success is False

    def test_in_set_expectation_passes(self):
        df = pd.DataFrame({"status": ["active", "inactive", "active"]})
        result = validate(df, expectations=[
            expect("status").in_set(["active", "inactive", "pending"])
        ])
        assert result.success is True

    def test_in_set_expectation_fails(self):
        df = pd.DataFrame({"status": ["active", "deleted", "active"]})
        result = validate(df, expectations=[
            expect("status").in_set(["active", "inactive"])
        ])
        assert result.success is False
        assert result.results[0].unexpected_count == 1

    def test_regex_expectation_passes(self):
        df = pd.DataFrame({"email": ["a@b.com", "c@d.org"]})
        result = validate(df, expectations=[
            expect("email").matches_regex(r".+@.+\..+")
        ])
        assert result.success is True

    def test_regex_expectation_fails(self):
        df = pd.DataFrame({"email": ["a@b.com", "invalid"]})
        result = validate(df, expectations=[
            expect("email").matches_regex(r".+@.+\..+")
        ])
        assert result.success is False

    def test_row_count_expectation(self):
        df = pd.DataFrame({"a": [1, 2, 3, 4, 5]})
        result = validate(df, expectations=[
            expect_table().row_count().between(3, 10)
        ])
        assert result.success is True

    def test_row_count_expectation_fails(self):
        df = pd.DataFrame({"a": [1]})
        result = validate(df, expectations=[
            expect_table().row_count().greater_than(5)
        ])
        assert result.success is False

    def test_multiple_expectations_mixed_results(self):
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "age": [25, None, 30],
        })
        result = validate(df, expectations=[
            expect("id").not_null(),
            expect("age").not_null(),
        ])
        assert result.success is False  # age has null
        assert result.results[0].success is True  # id passes
        assert result.results[1].success is False  # age fails

    def test_statistics_present(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = validate(df, expectations=[
            expect("a").not_null()
        ])
        assert "evaluation_time_seconds" in result.statistics
        assert result.statistics["evaluated_expectations"] == 1
        assert result.statistics["successful_expectations"] == 1

    def test_result_to_dict(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = validate(df, expectations=[
            expect("a").not_null()
        ])
        d = result.to_dict()
        assert "success" in d
        assert "results" in d
        assert "statistics" in d

    def test_result_to_markdown(self):
        df = pd.DataFrame({"a": [1, None, 3]})
        result = validate(df, expectations=[
            expect("a").not_null()
        ])
        md = result.to_markdown()
        assert "FAIL" in md or "PASS" in md
        assert "not_null" in md

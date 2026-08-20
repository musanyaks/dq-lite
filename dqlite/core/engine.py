"""Core validation engine."""

from typing import List, Any, Dict, Optional
import time

from dqlite.core.result import ValidationResult, ExpectationResult
from dqlite.core.registry import ExpectationRegistry
from dqlite.backends.base import Backend
from dqlite.backends.pandas_backend import PandasBackend


def validate(
    data: Any,
    expectations: List[Any],
    backend: Optional[Backend] = None,
) -> ValidationResult:
    """
    Run a suite of expectations against a dataset.

    Args:
        data: Dataset to validate (DataFrame, table, etc.)
        expectations: List of expectation objects to evaluate
        backend: Execution backend. Auto-detected if not provided.

    Returns:
        ValidationResult with detailed pass/fail information.
    """
    start_time = time.time()

    # Auto-detect backend
    if backend is None:
        backend = _detect_backend(data)

    results: List[ExpectationResult] = []

    for expectation in expectations:
        try:
            result = expectation.evaluate(data, backend)
            results.append(result)
        except Exception as e:
            results.append(
                ExpectationResult(
                    expectation_type=expectation.__class__.__name__,
                    column=getattr(expectation, "column", None),
                    success=False,
                    details={"error": str(e)},
                )
            )

    elapsed = time.time() - start_time

    return ValidationResult(
        success=all(r.success for r in results),
        results=results,
        statistics={
            "evaluated_expectations": len(results),
            "successful_expectations": sum(1 for r in results if r.success),
            "unsuccessful_expectations": sum(1 for r in results if not r.success),
            "evaluation_time_seconds": round(elapsed, 4),
        },
    )


def _detect_backend(data: Any) -> Backend:
    """Auto-detect the appropriate backend for the data."""
    type_name = type(data).__module__

    if "pandas" in type_name:
        return PandasBackend()
    elif "polars" in type_name:
        from dqlite.backends.polars_backend import PolarsBackend
        return PolarsBackend()

    # Default to pandas
    return PandasBackend()

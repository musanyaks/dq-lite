"""Validation result models."""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExpectationResult:
    """Result of a single expectation check."""

    expectation_type: str
    column: Optional[str]
    success: bool
    unexpected_count: int = 0
    unexpected_percent: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Aggregate result of a validation run."""

    success: bool
    results: List[ExpectationResult] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "statistics": self.statistics,
            "results": [
                {
                    "expectation_type": r.expectation_type,
                    "column": r.column,
                    "success": r.success,
                    "unexpected_count": r.unexpected_count,
                    "unexpected_percent": r.unexpected_percent,
                    "details": r.details,
                }
                for r in self.results
            ],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def to_markdown(self) -> str:
        lines = [
            "# Data Quality Report",
            "",
            f"**Overall:** {'PASS ✅' if self.success else 'FAIL ❌'}",
            f"**Total Checks:** {len(self.results)}",
            f"**Passed:** {sum(1 for r in self.results if r.success)}",
            f"**Failed:** {sum(1 for r in self.results if not r.success)}",
            "",
            "| Expectation | Column | Status | Unexpected |",
            "|-------------|--------|--------|------------|",
        ]
        for r in self.results:
            status = "✅" if r.success else "❌"
            col = r.column or "-"
            lines.append(f"| {r.expectation_type} | {col} | {status} | {r.unexpected_count} |")
        return "\n".join(lines)

    def to_github_annotation(self) -> List[Dict[str, Any]]:
        """Format for GitHub Actions annotations."""
        annotations = []
        for r in self.results:
            if not r.success:
                annotations.append(
                    {
                        "file": "data_quality",
                        "line": 1,
                        "title": f"{r.expectation_type} failed",
                        "message": f"Column '{r.column}': {r.unexpected_count} unexpected values ({r.unexpected_percent:.2f}%)",
                        "annotation_level": "failure",
                    }
                )
        return annotations

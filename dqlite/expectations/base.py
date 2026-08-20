"""Base expectation class."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from dqlite.core.result import ExpectationResult
from dqlite.backends.base import Backend


class Expectation(ABC):
    """Abstract base class for all expectations."""

    def __init_subclass__(cls, **kwargs):
        """Auto-register subclasses."""
        super().__init_subclass__(**kwargs)
        # Lazy import to avoid circular dependency
        from dqlite.core.registry import ExpectationRegistry

        ExpectationRegistry.register(cls)

    @abstractmethod
    def evaluate(self, data: Any, backend: Backend) -> ExpectationResult:
        """Evaluate the expectation against data using the given backend."""
        pass

    @property
    @abstractmethod
    def expectation_type(self) -> str:
        """Return the expectation type name."""
        pass

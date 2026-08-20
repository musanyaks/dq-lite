"""Auto-discovery of expectation classes."""

from typing import Type, Dict
from dqlite.expectations.base import Expectation


class ExpectationRegistry:
    """Auto-discovers and registers expectation classes."""

    _registry: Dict[str, Type[Expectation]] = {}
    _discovered: bool = False

    @classmethod
    def discover(cls) -> None:
        """Auto-discover all expectation subclasses."""
        if cls._discovered:
            return

        # Import built-in expectations to trigger registration
        import dqlite.expectations.column  # noqa
        import dqlite.expectations.table   # noqa

        cls._discovered = True

    @classmethod
    def register(cls, expectation_class: Type[Expectation]) -> Type[Expectation]:
        """Decorator to register an expectation class."""
        cls._registry[expectation_class.__name__] = expectation_class
        return expectation_class

    @classmethod
    def get(cls, name: str) -> Type[Expectation]:
        cls.discover()
        if name not in cls._registry:
            raise KeyError(f"Unknown expectation: {name}. Registered: {list(cls._registry.keys())}")
        return cls._registry[name]

    @classmethod
    def list_expectations(cls) -> Dict[str, Type[Expectation]]:
        cls.discover()
        return dict(cls._registry)

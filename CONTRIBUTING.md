# Contributing to dq-lite

Thank you for considering a contribution! This project is designed to be easy to extend.

## Development Setup

```bash
git clone https://github.com/yourname/dq-lite.git
cd dq-lite
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

## Running Tests

```bash
make test        # Run pytest with coverage
make lint        # Run black, ruff, mypy
make format      # Auto-format code
make all         # Run everything (test + lint)
```

## Adding a New Expectation

1. Create a file in `dqlite/expectations/column.py` or `dqlite/expectations/table.py`
2. Inherit from `Expectation`
3. Implement `evaluate(self, data, backend)`
4. Add tests in `tests/test_engine.py`
5. Update the README example

The class auto-registers via `__init_subclass__` — no manual registration needed.

## Adding a New Backend

1. Create `dqlite/backends/<name>_backend.py`
2. Inherit from `Backend`
3. Implement all abstract methods
4. Add backend detection in `dqlite/core/engine.py:_detect_backend()`
5. Add tests and benchmark against Pandas backend

## Adding a Domain Example

1. Create `examples/<domain>/<example>.py`
2. Include a `create_sample_data()` function
3. Show realistic expectations for that domain
4. Add a README section

## Good First Issues

- [Polars backend](https://github.com/yourname/dq-lite/issues/1)
- [DuckDB backend](https://github.com/yourname/dq-lite/issues/2)
- [JSON output format](https://github.com/yourname/dq-lite/issues/3)
- [dbt integration](https://github.com/yourname/dq-lite/issues/4)
- [Add 5 more built-in expectations](https://github.com/yourname/dq-lite/issues/5)

## Code of Conduct

Be respectful. Assume good intent. Focus on the problem, not the person.

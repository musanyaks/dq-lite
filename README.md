# dq-lite 

[![CI](https://github.com/musanyaks/dq-lite/actions/workflows/ci.yml/badge.svg)](https://github.com/musanyaks/dq-lite/actions)

> **Lightweight data quality validation — fast, pluggable, CI-native.**

Validate millions of rows in seconds. Add domain-specific checks in 20 lines. Fail pull requests on bad data.



## Why dq-lite?

| | dq-lite | Great Expectations |
|--|---------|-------------------|
| 10M rows | ~3s | ~45s |
| Dependencies | 5 | 47 |
| Setup time | `pip install dq-lite` | 20+ minutes |
| Learning curve | 10 minutes | 2 hours |
| CI integration | Native GitHub annotations | Complex |

**dq-lite** is for teams that want data quality gates without the ceremony.

---

## Quick Start

```bash
pip install dq-lite
```

```python
import pandas as pd
from dqlite import validate, expect

df = pd.read_csv("orders.csv")

result = validate(df, expectations=[
    expect("user_id").not_null().unique(),
    expect("age").between(0, 120),
    expect("email").matches_regex(r".+@.+\..+"),
    expect("status").in_set(["active", "inactive", "pending"]),
])

print(result.to_markdown())
```

---

## CLI Usage

```bash
# Validate a CSV with default checks
dqlite validate-csv data.csv

# With a custom config
dqlite validate-csv data.csv --config checks.yaml

# Output JSON for CI
dqlite validate-csv data.csv --format json --output report.json

# Generate starter config
dqlite init dqlite.yaml
```

---

## Write Your Own Check

```python
from dqlite.expectations.base import Expectation
from dqlite.core.result import ExpectationResult
from dqlite.backends.base import Backend

class IsValidIBAN(Expectation):
    def __init__(self, column: str):
        self.column = column

    @property
    def expectation_type(self) -> str:
        return "is_valid_iban"

    def evaluate(self, data, backend: Backend) -> ExpectationResult:
        # Your validation logic here
        from schwifty import IBAN

        df = data
        invalid = (~df[self.column].apply(lambda x: IBAN(x).is_valid)).sum()

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=self.column,
            success=invalid == 0,
            unexpected_count=int(invalid),
            details={},
        )
```

Save to `dqlite/expectations/custom/` — it auto-registers on import.

---

## Backends

| Backend | Status | Notes |
|---------|--------|-------|
| Pandas | ✅ Ready | Default, fully featured |
| Polars | 🚧 Stub | [Good first issue](https://github.com/yourname/dq-lite/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) |
| DuckDB | 🚧 Planned | Community contribution welcome |
| PySpark | 🚧 Planned | Community contribution welcome |
| Snowflake | 🚧 Planned | Via SQL backend |

---

## Examples by Domain

- [E-commerce order pipeline](examples/ecommerce/)
- [Healthcare HL7/FHIR records](examples/healthcare/)
- [Custom plugin (credit card validation)](examples/custom_expectation_plugin.py)

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Data Quality
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install dq-lite
      - run: dqlite validate-csv data.csv --config checks.yaml
```

Failed expectations produce inline PR annotations.

### Slack Notifications

```python
from dqlite.integrations.slack_reporter import send_report

send_report("https://hooks.slack.com/...", result, title="Daily ETL Check")
```

---

## Roadmap

- [ ] Polars backend
- [ ] DuckDB backend
- [ ] SQL backend (BigQuery, Snowflake, Postgres)
- [ ] dbt integration
- [ ] Great Expectations migration helper
- [ ] Web dashboard for historical results

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Key points:

- `make test` runs the full suite in <30s
- `make lint` checks formatting
- Every expectation needs a test in `tests/`
- Add your domain example to `examples/`

---

## License

MIT

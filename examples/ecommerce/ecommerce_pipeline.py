"""E-commerce order pipeline data quality checks.

This example demonstrates how to validate a typical e-commerce
order dataset before loading it into a data warehouse.
"""

import pandas as pd
from dqlite import validate, expect
from dqlite.expectations.table import expect_table


def create_sample_orders() -> pd.DataFrame:
    """Generate sample order data."""
    return pd.DataFrame({
        "order_id": ["ORD-001", "ORD-002", "ORD-003", "ORD-004"],
        "user_id": [1001, 1002, 1003, 1004],
        "product_id": ["P-100", "P-200", "P-300", "P-400"],
        "quantity": [2, 1, 5, 0],
        "price": [29.99, 149.99, 9.99, 49.99],
        "status": ["completed", "completed", "pending", "completed"],
        "email": ["user1@store.com", "user2@store.com", "bad-email", "user4@store.com"],
        "created_at": ["2024-01-15", "2024-01-16", "2024-01-17", "2024-01-18"],
    })


def main():
    df = create_sample_orders()

    print(f"Validating {len(df)} orders...\n")

    result = validate(df, expectations=[
        # Table-level checks
        expect_table().row_count().greater_than(0),
        expect_table().has_columns(["order_id", "user_id", "product_id", "status"]),

        # Column-level checks
        expect("order_id").not_null(),
        expect("order_id").unique(),
        expect("user_id").not_null(),
        expect("quantity").between(1, 100),  # Will fail: one order has quantity 0
        expect("price").between(0.01, 10000),
        expect("status").in_set(["pending", "completed", "cancelled", "refunded"]),
        expect("email").matches_regex(r".+@.+\..+"),  # Will fail: "bad-email"
    ])

    # Print results
    print(result.to_markdown())
    print(f"\nOverall: {'PASS ✅' if result.success else 'FAIL ❌'}")

    if not result.success:
        print("\nIssues found:")
        for r in result.results:
            if not r.success:
                print(f"  - {r.expectation_type} on '{r.column}': {r.details}")

    return result


if __name__ == "__main__":
    main()

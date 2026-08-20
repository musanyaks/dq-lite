"""Example: How to write a custom expectation plugin.

Save this file to dqlite/expectations/custom/your_domain.py
and it will be auto-discovered on import.
"""

from dqlite.expectations.base import Expectation
from dqlite.core.result import ExpectationResult
from dqlite.backends.base import Backend


class IsValidCreditCardExpectation(Expectation):
    """Validate credit card numbers using Luhn algorithm.

    Usage:
        from dqlite import validate
        from dqlite.expectations.custom.payments import IsValidCreditCardExpectation

        result = validate(df, expectations=[
            IsValidCreditCardExpectation("card_number")
        ])
    """

    def __init__(self, column: str):
        self.column = column

    @property
    def expectation_type(self) -> str:
        return "is_valid_credit_card"

    def _luhn_check(self, card_number: str) -> bool:
        """Validate card number with Luhn algorithm."""
        if not card_number or not card_number.isdigit():
            return False
        digits = [int(d) for d in card_number]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        total = sum(odd_digits)
        for d in even_digits:
            d *= 2
            if d > 9:
                d -= 9
            total += d
        return total % 10 == 0

    def evaluate(self, data, backend: Backend) -> ExpectationResult:
        df = data
        series = df[self.column].astype(str).str.replace(" ", "")
        invalid = int((~series.apply(self._luhn_check)).sum())
        total = len(df)

        return ExpectationResult(
            expectation_type=self.expectation_type,
            column=self.column,
            success=invalid == 0,
            unexpected_count=invalid,
            unexpected_percent=(invalid / total * 100) if total > 0 else 0,
            details={"invalid_cards": invalid},
        )


# The class is auto-registered when imported because it inherits from Expectation
# and __init_subclass__ triggers registration.

"""Money value object.

A :class:`Money` wraps a decimal amount and an ISO 4217 currency code. The
amount is stored as a :class:`decimal.Decimal` to avoid binary floating-point
errors, and the currency is validated at construction. The module depends only
on the standard library.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.domain.exceptions import InvalidValue
from app.domain.value_object import ValueObject


class Money(ValueObject):
    """An immutable, validated amount in a single currency.

    Attributes:
        amount: The monetary amount as a :class:`decimal.Decimal`.
        currency: The ISO 4217 currency code (three uppercase letters).
    """

    amount: Decimal
    currency: str

    def __init__(
        self,
        amount: Decimal | int | str,
        currency: str,
    ) -> None:
        """Initialize the money.

        Args:
            amount: The monetary amount. Decimals are used verbatim; integers
                and strings are parsed with :class:`decimal.Decimal`.
            currency: The ISO 4217 currency code.

        Raises:
            InvalidValue: When the amount cannot be parsed as a decimal or the
                currency is not a valid ISO 4217 code.
        """
        try:
            parsed_amount = amount if isinstance(amount, Decimal) else Decimal(amount)
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise InvalidValue(f"{amount!r} is not a valid decimal amount") from exc
        normalized_currency = currency.strip().upper()
        if len(normalized_currency) != 3 or not normalized_currency.isalpha():
            raise InvalidValue(f"{currency!r} is not a valid ISO 4217 currency code")
        object.__setattr__(self, "amount", parsed_amount)
        object.__setattr__(self, "currency", normalized_currency)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Args:
            name: The attribute being assigned.
            value: The value being assigned.

        Raises:
            TypeError: Always raised because money is immutable.
        """
        raise TypeError(f"{type(self).__name__} instances are immutable")

    def __str__(self) -> str:
        """Return the amount and currency code."""
        return f"{self.amount} {self.currency}"

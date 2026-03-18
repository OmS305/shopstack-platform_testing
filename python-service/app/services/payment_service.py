"""Payment calculation service."""

from decimal import Decimal, ROUND_HALF_UP

TAX_RATE = Decimal('0.085')  # 8.5% tax rate as Decimal for precision

DISCOUNT_CODES = {
    "SAVE10": 10,   # 10% off
    "SAVE20": 20,   # 20% off
    "SAVE30": 30,   # 30% off
    "FLAT5": 5.00,  # $5 flat discount (handled separately)
}


def calculate_tax(subtotal):
    """Calculate tax amount for a given subtotal.

    Args:
        subtotal: The pre-tax subtotal amount.

    Returns:
        The tax amount rounded to 2 decimal places.
    """
    # Round to 2 decimal places before conversion to avoid floating-point representation artifacts
    subtotal = round(subtotal, 2)
    subtotal_decimal = Decimal(str(subtotal))
    tax = (subtotal_decimal * TAX_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return float(tax)


def apply_discount(subtotal, discount_code, applied_discount_codes=None):
    """Apply a discount code to a subtotal.

    Args:
        subtotal: The original subtotal.
        discount_code: The discount code string.
        applied_discount_codes: Set of already applied discount codes for idempotency.
            IMPORTANT: This set must be shared across all discount application calls
            during a single checkout session to prevent double application.
            If None, a new set is created (e.g., for isolated unit tests).

    Returns:
        Tuple of (discounted_subtotal, discount_amount).
    """
    # CRITICAL: Idempotency check MUST happen first to prevent double application
    if applied_discount_codes is None:
        applied_discount_codes = set()

    if discount_code in applied_discount_codes:
        return subtotal, 0

    if discount_code not in DISCOUNT_CODES:
        return subtotal, 0

    applied_discount_codes.add(discount_code)

    discount_value = DISCOUNT_CODES[discount_code]

    if discount_code.startswith("FLAT"):
        discount_amount = discount_value
    else:
        discount_amount = subtotal * (discount_value / 100)

    discounted_subtotal = subtotal - discount_amount
    return round(discounted_subtotal, 2), round(discount_amount, 2)

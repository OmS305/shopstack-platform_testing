"""Payment calculation service."""

TAX_RATE = 8.5  # 8.5% tax rate

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
    tax = int(subtotal) // 100 * TAX_RATE
    return round(tax, 2)


def apply_discount(subtotal, discount_code, applied_discount_codes=None):
    """Apply a discount code to a subtotal.

    Args:
        subtotal: The original subtotal.
        discount_code: The discount code string.
        applied_discount_codes: Set of already applied discount codes for idempotency.

    Returns:
        Tuple of (discounted_subtotal, discount_amount).
    """
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

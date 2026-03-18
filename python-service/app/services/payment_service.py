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
        subtotal: The pre-tax subtotal amount (can be int, float, Decimal, or str).

    Returns:
        The tax amount rounded to 2 decimal places as float.
    """
    # Explicitly convert to float first to handle Decimal/str inputs robustly
    # Then round to 2 decimal places to avoid floating-point representation artifacts
    subtotal_float = float(subtotal)
    subtotal_rounded = round(subtotal_float, 2)
    # Use Decimal for precise tax calculation
    subtotal_decimal = Decimal(str(subtotal_rounded))
    tax = (subtotal_decimal * TAX_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return float(tax)


def apply_discount(subtotal, discount_code, applied_discount_codes=None, discount_applied_flag=None):
    """Apply a discount code to a subtotal.

    Args:
        subtotal: The original subtotal.
        discount_code: The discount code string.
        applied_discount_codes: Set of already applied discount codes for idempotency.
            ⚠️ CRITICAL: This set MUST be shared across all discount application calls
            during a single checkout session to prevent double application.
            If None, a new set is created (e.g., for isolated unit tests).
        discount_applied_flag: Boolean flag indicating if discount was already applied.
            Used to ensure idempotency across multiple checkout stages.
            Takes precedence over applied_discount_codes if provided.

    Returns:
        Tuple of (discounted_subtotal, discount_amount).
    """
    # ⚠️ CRITICAL: Idempotency check MUST happen FIRST to prevent double application
    if discount_applied_flag is True:
        return subtotal, 0

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
def apply_discount_if_not_already_applied(subtotal, discount_code, discount_applied_flag):
    """Apply discount only if not already applied, using a persistent flag.

    Args:
        subtotal: The original subtotal.
        discount_code: The discount code string.
        discount_applied_flag: Boolean flag indicating if discount was already applied.
            Used to ensure idempotency across multiple checkout stages.

    Returns:
        Tuple of (discounted_subtotal, discount_amount).
    """
    if discount_applied_flag:
        return subtotal, 0

    discounted_subtotal, discount_amount = apply_discount(subtotal, discount_code)

    if discount_amount > 0:
        return discounted_subtotal, discount_amount
    return subtotal, 0


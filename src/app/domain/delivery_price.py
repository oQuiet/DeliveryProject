from decimal import ROUND_HALF_UP, Decimal


def calculate_delivery_price(
    weight: Decimal, content_price_usd: Decimal, usd_rate: Decimal
) -> Decimal:
    price = (weight * Decimal("0.5") + content_price_usd * Decimal("0.01")) * usd_rate

    return price.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

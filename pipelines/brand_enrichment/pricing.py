from typing import Literal

PriceTier = Literal["low", "mid", "premium", "luxury"]

def classify_price(price: float) -> PriceTier:
    if price < 1000:
        return "low"
    elif price < 3000:
        return "mid"
    elif price < 5000:
        return "premium"
    else:
        return "luxury"
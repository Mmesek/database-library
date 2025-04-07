import re
from decimal import Decimal


def currency(value: str) -> str:
    if "$" in value:
        return "USD"
    if "€" in value:
        return "EUR"
    if "£" in value:
        return "GBP"
    if "PLN" in value:
        return "PLN"
    return clean(value, currency=True)


def pair(value: str) -> str:
    if "PERP-INTX" in value:
        return value.replace("-INTX", "")
    return value.split("-", 1)[0].replace("-INTX", "")


def asset_pair(value: str) -> str:
    if "PERP-INTX" in value:
        return "USDC"
    return value.split("-", 1)[1].replace("-INTX", "")


VALUE = re.compile(r"-?\W?(\d*(?:\.|,|\w)?(?:\d*)?\.?\d*?) ?(.*)?")
NOTE = re.compile(
    r"(?P<type>Bought|Sold|Converted) (?P<src>\d+\.?\d+) (?P<asset>.*)"
    r" (?:for|to) "
    r"(?P<dest_quantity>\d+\.?\d+) (?P<dest_asset>\w+)"
    r"(?: on (?P<pair>.*\-.*) at (?P<rate>\d+\.?\d+) (?P<rate_pair>.*\/.*))?"
)


def clean(value: str, currency: bool = False) -> str:
    if not value:
        if currency:
            return None
        return 0
    v = value.replace("\xa0", "")
    r = VALUE.findall(v)
    return r[0][currency].replace(",", ".")


def number(value: str) -> Decimal:
    return Decimal(clean(value if value != "N/A" else "") or "0")

import re
from decimal import Decimal
from datetime import UTC, datetime
import dateparser
import pytz
from calendar import month_abbr


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
    r"(?P<type>Bought|Sold|Converted) (?P<src>\d+\.?\d*) (?P<asset>.*)"
    r" (?:for|to) "
    r"(?P<dest_quantity>\d+\.?\d*) (?P<dest_asset>\w+)"
    r"(?: on (?P<pair>\w+(?:-\w+)?))?(?: at (?P<rate>\d+\.?\d*) (?P<rate_pair>.*\/.*))?"
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
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(value)
    except:
        return Decimal(clean(value if value != "N/A" else "") or "0")


MONTH_ABBR_TRANSLATINS = {
    "sty": month_abbr[1],
    "lut": month_abbr[2],
    "mar": month_abbr[3],
    "kwi": month_abbr[4],
    "maj": month_abbr[5],
    "cze": month_abbr[6],
    "lip": month_abbr[7],
    "sie": month_abbr[8],
    "wrz": month_abbr[9],
    "paź": month_abbr[10],
    "lis": month_abbr[11],
    "gru": month_abbr[12],
}


def parse_date(ds: str):
    for key, translation in MONTH_ABBR_TRANSLATINS.items():
        ds = ds.replace(key, translation)
    dt = dateparser.parse(ds)
    if not dt.tzinfo:
        dt = dt.astimezone(pytz.timezone("Europe/Warsaw"))
    # dt = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, tzinfo=dt.tzinfo)
    return dt

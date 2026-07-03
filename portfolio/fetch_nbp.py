import httpx
from pandas.tseries.offsets import BusinessDay
from pandas import bdate_range
from datetime import datetime

from functools import lru_cache


def is_business(date: datetime):
    return bool(len(bdate_range(date, date)))


HOLIDAYS = [datetime(2025, 1, 6), datetime(2025, 6, 19), datetime(2026, 5, 3)]


@lru_cache(maxsize=None)
def fetch(currency: str, year: int, month: int, day: int, previous_day: bool = True, avg: bool = True):
    date = datetime(year, month, day)
    if previous_day or not is_business(date):
        date = date - BusinessDay(1)
    if date in HOLIDAYS:
        date = date - BusinessDay(1)
    res = httpx.request(
        "GET",
        f"https://api.nbp.pl/api/exchangerates/rates/{'a' if avg else 'c'}/{currency}/{date.year}-{date.month:0>2}-{date.day:0>2}/?format=json",
    )
    try:
        res = res.json()
    except:
        d = date - BusinessDay(1)
        return fetch(currency, d.year, d.month, d.day)
    if avg:
        return res["rates"][0]["mid"]
    else:
        return res["rates"][0]["bid"], res["rates"][0]["ask"]

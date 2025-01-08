import httpx
from pandas.tseries.offsets import BusinessDay
from pandas import bdate_range
from datetime import datetime


def is_business(date: datetime):
    return bool(len(bdate_range(date, date)))


def fetch(currency: str, year: int, month: int, day: int, previous_day: bool = True):
    date = datetime(year, month, day)
    if previous_day or not is_business(date):
        date = date - BusinessDay(1)
    res = httpx.request(
        "GET",
        f"https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{date.year}-{date.month:0>2}-{date.day:0>2}/?format=json",
    ).json()
    return res["rates"][0]["mid"]

from portfolio.models import Transaction
import pandas as pd
import re
from decimal import Decimal
from countryinfo import CountryInfo


CURRENCY = "PLN"
PATTERN = re.compile(r"(?P<quantity>\d+\.?(?:\d+)?)\/?(?P<divider>\d+\.?(?:\d+)?)? @ (?P<price>\d+\.?(?:\d+)?)")
r = pd.read_excel("xtb.xlsx", "CASH OPERATION HISTORY", header=10)
for row in list(r.iterrows())[:-1]:
    note = row[1]["Komentarz"]
    g = PATTERN.findall(note)
    quantity = g[0][0] if g else None
    total = g[0][1] if g else None
    price = g[0][2] if g else None
    if not price:
        # print(row[1]["Czas"], row[1]["Typ"], note, row[1]["Kwota"])
        continue
    t = Transaction(
        exchange="XTB",
        category=row[1]["Typ"],
        buying=True if "OPEN BUY" in note else False,
        timestamp=row[1]["Czas"],
        asset=row[1]["Symbol"],
        quantity=Decimal(quantity),
        price=Decimal(price),
        currency=CountryInfo(row[1]["Symbol"].split(".")[-1]).currencies()[0],
        rate=Decimal(row[1]["Kwota"]) / (Decimal(price) * Decimal(quantity)),
        rate_currency="PLN",
        note=note,
    )
    t.print()

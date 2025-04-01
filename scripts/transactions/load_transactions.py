# https://github.com/EnchantedGoldenApple/Steam-History-Exporter

import csv

months = {
    "stycznia": 1,
    "lutego": 2,
    "marca": 3,
    "kwietnia": 4,
    "maja": 5,
    "czerwca": 6,
    "lipca": 7,
    "sierpnia": 8,
    "września": 9,
    "października": 10,
    "listopada": 11,
    "grudnia": 12,
}

import re

AMOUNT = re.compile(r"(\d+) transakcji\(-e\)")
ROWS = ["Date", "Items", "Type", "Total", "Wallet Change", "Wallet Balance", "Expenses"]
OUTPUT_ROWS = [
    "date",
    "items",
    "amount",
    "type",
    "funding",
    "total",
    "change",
    "balance",
    "expenses",
]

market = []
shop = []

with open("steam_history.csv", "r", newline="", encoding="utf-8") as file:
    for row in csv.DictReader(file.readlines()[1:], ROWS):
        if all([i == "" for i in row.values()]):
            continue
        try:
            day, month, year = row["Date"].split(" ")
            month = months[month]
            date = f"{year}-{month:02}-{int(day):02}"
        except:
            date = row["Date"]
        m = AMOUNT.match(row["Type"])
        items = (
            ", ".join(row["Items"].split("\n"))
            if "Rynek Społeczności Steam" != row["Items"]
            else "Item"
        )
        amount = m.group(1) if m else 1
        funding = row["Type"].split("\n")[-1]
        type_ = (
            "Market"
            if m or "Transakcja na rynku" in row["Type"]
            else row["Type"].split("\n")[0]
        )
        total = row["Total"].replace("\nKwota", "")
        if items == "Item":
            collection = market
        else:
            collection = shop
        entry = {
            "date": date,
            "amount": amount,
            "total": total,
            "change": row["Wallet Change"],
            "balance": row["Wallet Balance"],
            "expenses": row["Expenses"],
        }
        if items != "Item":
            entry["items"] = items
            entry["type"] = type_
            entry["funding"] = funding
        collection.append(entry)

with open("steam_market_history.csv", "w", newline="", encoding="utf-8") as output:
    writer = csv.DictWriter(
        output,
        [
            "date",
            "amount",
            "total",
            "change",
            "balance",
            "expenses",
        ],
    )
    writer.writeheader()
    writer.writerows(market)

with open("steam_shop_history.csv", "w", newline="", encoding="utf-8") as output:
    writer = csv.DictWriter(output, OUTPUT_ROWS)
    writer.writeheader()
    writer.writerows(shop)

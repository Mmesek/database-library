from portfolio.models import Transaction
from collections import Counter
import csv
import json


def load_statement(file: str, x=False):
    PATH = "data/statements/"
    if "coinbase" in file:
        SCHEMA = "Coinbase"
        FILE = PATH + file
    else:
        SCHEMA = "Revolut"
        if x:
            SCHEMA += " X"
        FILE = PATH + file
    FILE += ".csv"

    with open("portfolio/schema.json") as file:
        schema = json.load(file)

    schema = schema[SCHEMA]

    with open(FILE) as file:
        lines = file.readlines()
        fields = [i.strip() for i in lines[schema["fieldnames"]].split(",")]
        rows = [row for row in csv.DictReader(lines[schema["start"] :], fields)]
    return rows, schema


def save(transactions: list[Transaction]):
    transactions.sort(key=lambda x: x.timestamp)
    save_to_db(transactions)
    summarize(transactions)


def save_to_db(transactions: list[Transaction]):
    from utils.db import make_session

    session = make_session("Portfolio", start_fresh=True)
    # from sqlalchemy import insert
    # stmt = insert(Transaction).values(transactions)
    # stmt = stmt.on_conflict_do_nothing()
    # session.execute(stmt)
    session.add_all(instances=transactions)

    session.commit()


def summarize(transactions: list[Transaction]):
    c = Counter()
    for t in transactions:
        c[t.asset] += t.quantity
        # t.print()
    for i in c:
        print(i, f"{c[i]:.40f}".rstrip("0").rstrip("."))

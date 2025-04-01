import csv, datetime, json, re

from mailbox import Message, mbox, mboxMessage
from bs4 import BeautifulSoup

from portfolio.load import VALUE, clean
from portfolio.models import Transaction

INBOX = "INBOX"
OUTPUT = "coinbase.csv"
EXCHANGE = "Coinbase"
CATEGORY = "CRYPTO"
FROM = "Coinbase <no-reply@mail.coinbase.com>"
SUBJECT = "zrealizowane"
PATTERN = re.compile(r"Zlecenie (.*) PERP zostało zrealizowane")

with open("portfolio/mail-scheme.json") as f:
    MAPPER = json.load(f)


def parse_body(email: Message):
    t = {}
    for m in email.get_payload():
        c = m.get_payload(decode=True)

        if bs := BeautifulSoup(c, features="lxml").body:
            for row in bs("tr")[1:]:
                k, v = row("td")
                if k.text.strip() in MAPPER:
                    t[MAPPER[k.text.strip()]] = v.text

    price, src_currency = VALUE.match(t["price"]).groups()
    return Transaction(
        exchange=EXCHANGE,
        category=CATEGORY,
        asset=t["asset"],
        price=price,
        currency=src_currency,
        fee=clean(t["fee"]),
        timestamp=datetime.datetime.fromisoformat(t["timestamp"].rstrip(" UTC").replace(" +", "+")),
        buying=any(i in t["type"].lower() for i in ["buy"]),
        quantity=clean(t["amount"]),
        total=clean(t["value"]),
    )


def parse_mail(msg: mboxMessage) -> Transaction:
    if msg.get("from") == FROM and SUBJECT in msg.get("subject"):
        return parse_body(msg)


def dump_results(msgs: list[Transaction]):
    with open(OUTPUT, "w", newline="", encoding="utf-8") as file:
        f = csv.DictWriter(file, msgs[0].keys())
        f.writeheader()
        f.writerows(msgs)


def parse_mbox():
    return [parse_mail(msg) for msg in mbox(INBOX).itervalues()]


if __name__ == "__main__":
    parse_mbox()

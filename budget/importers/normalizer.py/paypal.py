import csv
import os
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pytz import timezone


def strip_None(d):
    nd = {}
    for k, v in d.items():
        if v is not None:
            nd[k] = v
    return nd


def get_decimal(d: dict, *key: str):
    for k in key:
        value = d.get(k) or None
        if value:
            break
    value = None if value == "0,00" else value
    if value:
        return Decimal(value.replace(",", ".").replace("\xa0", "").replace(" ", ""))


def format_date(date: str, d: dict):
    date = date.split(" ", 1)
    if len(date) > 1:
        date, rest = date
    else:
        date = date[0]
        rest = f'{d.get("Godzina", "00:00")} {d.get("Strefa czasowa", "Europe/Warsaw")}'
    try:
        hour, tz = rest.split(" ", 1)
    except ValueError:
        hour = rest
        tz = "Europe/Warsaw"
    tz = tz.replace("CEST", "Europe/Warsaw").replace("CET", "Europe/Warsaw")

    if "/" in date:
        m, _d, y = date.split("/")
    elif "." in date:
        _d, m, y = date.split(".")
    else:
        y, m, _d = date.split("-")
    try:
        date = f"{y}-{m:0>2}-{_d:0>2} {hour}"
        _date = datetime.fromisoformat(date)
    except ValueError:
        date = f"{_d}-{m:0>2}-{y:0>2} {hour}"
        _date = datetime.fromisoformat(date)
    return _date.astimezone(timezone(tz))


@dataclass
class Paypal:
    date: datetime
    name: str
    type: str
    currency: str
    brutto: Decimal
    fee: Decimal
    netto: Decimal
    from_email: str
    to_email: str
    transaction_number: str
    item_name: str
    taxes: Decimal
    additional_transaction_number: str
    invoice_id: str
    amount: int
    confirmation: str
    balance: Decimal
    topic: str
    note: str
    balance_change: str
    transfer_fee: Decimal

    def __init__(self, d: dict, reverse: bool = False):
        self.date = format_date(d.get("datetime", d.get("Data")), d)
        self.name = d["Nazwa"]
        self.currency = d["Waluta"]
        self.brutto = get_decimal(d, "Brutto")
        self.type = d.get("Opis", d.get("Typ", None))

        self.from_email = d["Z adresu e-mail"] or None
        self.fee = get_decimal(d, "Opłata")
        self.netto = get_decimal(d, "Netto")
        self.invoice_id = d.get("Numer faktury") or None

        self.item_name = d.get("Nazwa przedmiotu") or None
        self.taxes = get_decimal(d, "Podatek of sprzedaży", "Kwota podatku")
        self.balance = get_decimal(d, "Saldo")
        self.topic = d.get("Temat") or None
        self.note = d.get("Uwaga") or None
        self.balance_change = d.get("Wpływ na saldo") or None

        self.to_email = d.get("Na adres e-mail", "themmesek@gmail.com")
        self.transaction_number = d.get("Numer transakcji") or None
        self.additional_transaction_number = d.get("Pomocniczy numer transakcji") or None
        self.amount = int(d.get("Ilość") or "1")
        self.confirmation = d.get("Numer potwierdzenia") or None
        self.transfer_fee = get_decimal(d, "Koszt wysyłki oraz koszty manipulacyjne")

        if reverse and "+" not in d["Brutto"]:
            # self.to_email, self.from_email = self.from_email, self.to_email
            self.brutto = -self.brutto
        # if self.brutto < 0:
        #    self.to_email, self.from_email = self.from_email, self.to_email

    def secondary_fields(self):
        return {
            "topic": self.topic,
            "note": self.note,
            "change": self.balance_change,
            "to_email": self.to_email,
            "amount": self.amount,
            "confirmation": self.confirmation,
        }

    def to_normalized(self):
        return {
            "Data": self.date.date(),
            "Godzina": self.date.strftime("%H:%M:%S"),
            "Strefa Czasowa": self.date.tzname(),
            "Opis": self.type or self.note or self.topic,
            "Waluta": self.currency,
            "Brutto": self.brutto,
            "Opłata": self.fee,
            "Netto": self.netto,
            "Saldo": self.balance,
            "Numer Transakcji": self.transaction_number,
            "Z adresu e-mail": self.from_email,
            "Nazwa": self.name,
            "Nazwa Banku": None,
            "Rachunek Bankowy": None,
            "Koszt wysyłki oraz koszty manipulacyjne": self.transfer_fee,
            "Kwota podatku": self.taxes,
            "Numer faktury": self.invoice_id,
            "Pomocniczy numer transakcji": self.additional_transaction_number,
        }


CURRENCY = "USD"
BALANCE = {"EUR": 0, "PLN": 0, "USD": 0, "GBP": 0}


def add(ds, o: Paypal):
    ds.append(o.to_normalized())
    if o.currency == CURRENCY:
        change = o.netto or o.brutto
        print("Adding", change, "to balance of", BALANCE[o.currency] + change, "/", o.balance, o.currency)
    return o.netto or o.brutto


def load(filepath: str, delimiter: str = ","):
    global BALANCE
    ROWS = []
    with open(filepath, "r", newline="", encoding="utf-8") as file:
        lines = file.readlines()
        line = (
            lines[0]
            .strip()
            .replace("'", "")
            .replace('"', "")
            .replace("\r\n", "")
            .replace("\n", "")
            .replace("\ufeff", "")
        )
        fields = [f.strip() for f in line.split(delimiter)]
        r = csv.DictReader(lines[1:], fields, delimiter=delimiter)
        for row in r:
            s = Paypal(row, delimiter == ";")

            if s.type == "Przedmiot z koszyka":
                # print("Disregarding", s.netto or s.brutto)
                continue

            if row.get("before_conversion"):
                b = Paypal(row, delimiter == ";")
                b.brutto = Decimal(row.get("before_conversion").replace(",", "."))
                if s.brutto < 0:
                    b.brutto = -b.brutto
                b.currency = row.get("original_currency")
                b.from_email = s.from_email
                add(ROWS, b)
                if not row.get("partial_currency"):
                    s.brutto = -s.brutto
                    BALANCE[s.currency] += add(ROWS, s)
                    s.brutto = -s.brutto

            if row.get("partial_currency"):
                p = Paypal(row, delimiter == ";")
                p.brutto = Decimal(row.get("partial").replace(",", "."))
                p.currency = row.get("partial_currency")
                p.from_email = s.from_email
                BALANCE[p.currency] += add(ROWS, p)

            BALANCE[s.currency] += add(ROWS, s)

        # print(BALANCE)
    return ROWS


from collections import Counter


def main():
    rows = []
    c = Counter()
    for file in os.listdir("data/statements/paypal2/"):
        single_rows = load(f"data/statements/paypal2/{file}")
        single_rows = sorted(single_rows, key=lambda x: (x["Data"], x["Godzina"]))

        w = Counter()
        f = {}
        for row in single_rows:
            if row["Waluta"] not in f:
                f[row["Waluta"]] = row["Saldo"]
            w[row["Waluta"]] = row["Saldo"] or 0
            c[row["Waluta"]] += row.get("Netto") or row["Brutto"]
        print("starting", f)
        print("balance", w)
        print("running", c)
        print("difference", c - w)
        print()

        fields = list(single_rows[0].keys())
        with open(f"data/statements/output/{file}", "w", newline="", encoding="utf-8") as file:
            w = csv.DictWriter(file, fields)
            w.writeheader()
            w.writerows(single_rows)
        rows.extend(single_rows)

    rows = sorted(rows, key=lambda x: (x["Data"], x["Godzina"]))
    with open("data/statements/output/consolidated.csv", "w", newline="", encoding="utf-8") as file:
        w = csv.DictWriter(file, fields)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()

# ['datetime',                          'Nazwa',                    'Waluta', 'Brutto',                    'Z adresu e-mail', 'before_conversion', 'original_currency', 'partial', 'partial_currency']
# ['Data', 'Godzina', 'Strefa czasowa', 'Nazwa', 'Opis',            'Waluta', 'Brutto', 'Opłata', 'Netto', 'Z adresu e-mail',                    'Numer transakcji',                            'Kwota podatku', 'Pomocniczy numer transakcji', 'Numer faktury',                                 'Saldo',                                                                        'Nazwa banku', 'Rachunek bankowy', 'Koszt wysyłki oraz koszty manipulacyjne']
# ['Data', 'Godzina', 'Strefa czasowa', 'Nazwa', 'Typ',   'Status', 'Waluta', 'Brutto', 'Opłata', 'Netto', 'Z adresu e-mail', 'Na adres e-mail', 'Numer transakcji', 'Nazwa przedmiotu', 'Podatek od sprzedaży', 'Pomocniczy numer transakcji', 'Numer faktury', 'Ilość', 'Numer potwierdzenia', 'Saldo', 'Temat', 'Uwaga', 'Źródło płatności', 'Wpływ na saldo', 'Filtr ryzyka']
# ['Data', 'Godzina', 'Strefa czasowa', 'Nazwa', 'Typ',   'Status', 'Waluta', 'Brutto', 'Opłata', 'Netto', 'Z adresu e-mail', 'Na adres e-mail', 'Numer transakcji', 'Nazwa przedmiotu', 'Podatek od sprzedaży', 'Pomocniczy numer transakcji', 'Numer faktury',          'Numer potwierdzenia', 'Saldo', 'Temat', 'Uwaga', 'Źródło płatności', 'Wpływ na saldo', 'Filtr ryzyka']

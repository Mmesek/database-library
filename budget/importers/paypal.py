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


def get_decimal(i):
    i = i or None
    i = None if i == "0,00" else i
    return Decimal(i.replace(",", ".").replace("\xa0", "").replace(" ", "")) if i else None


@dataclass
class Paypal:
    date: datetime
    name: str
    type: str
    status: str
    currency: str
    brutto: str
    fee: str
    netto: str
    from_email: str
    to_email: str
    transaction_number: str
    item_name: str
    taxes: str
    additional_transaction_number: str
    invoice_id: str
    amount: str
    confirmation: str
    balance: str
    topic: str
    note: str
    payment_source: str
    balance_change: str
    risk: str
    bank_name: str
    bank_number: str
    transfer_fee: str

    def __init__(self, d: dict, reverse: bool = False):
        date: str = d.get("datetime", d.get("Data"))
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
            _d, m, y = date.split("-")
        date = f"{y}-{m:0>2}-{_d:0>2} {hour}"

        _date = datetime.fromisoformat(date)
        self.date = _date.astimezone(timezone(tz))
        self.name = d["Nazwa"]
        self.currency = d["Waluta"]
        brutto = d["Brutto"].replace(",", ".").replace("\xa0", "").replace(" ", "")
        self.raw_brutto = Decimal(brutto)
        self.brutto = self.raw_brutto
        # if "-" in brutto:
        #    self.brutto = -self.brutto
        self.type = d.get("Opis", d.get("Typ", None))

        self.from_email = d["Z adresu e-mail"] or None
        self.fee = get_decimal(d.get("Opłata"))
        self.netto = get_decimal(d.get("Netto"))
        self.item_name = d.get("Nazwa przedmiotu") or None
        # if not self.item_name and self.from_email and "@" not in self.from_email:
        #    self.item_name = self.name
        #    self.name = self.from_email
        #    self.from_email = None

        self.taxes = get_decimal(d.get("Podatek of sprzedaży", d.get("Kwota podatku")))
        self.invoice_id = d.get("Numer faktury") or None
        self.balance = get_decimal(d.get("Saldo"))
        self.topic = d.get("Temat") or None
        self.note = d.get("Uwaga") or None
        self.payment_source = d.get("Źródło płatności") or None
        self.balance_change = d.get("Wpływ na saldo") or None

        self.to_email = d.get("Na adres e-mail", "themmesek@gmail.com")
        self.status = None if d.get("Status", "Zakończono") == "Zakończono" else d.get("Status")
        self.transaction_number = d.get("Numer transakcji") or None
        self.additional_transaction_number = d.get("Pomocniczy numer transakcji") or None
        self.amount = d.get("Ilość") or None
        self.confirmation = d.get("Numer potwierdzenia") or None
        self.risk = d.get("Filtr ryzyka") or None
        self.bank_name = d.get("Nazwa banku") or None
        self.bank_number = d.get("Rachunek bankowy") or None
        self.transfer_fee = get_decimal(d.get("Koszt wysyłki oraz koszty manipulacyjne"))

        if reverse and "+" not in brutto:
            self.to_email, self.from_email = self.from_email, self.to_email
            self.brutto = -self.brutto
        if self.brutto < 0:
            self.from_email, self.to_email = self.to_email, self.from_email

    def as_list(self):
        return {
            "datetime": self.date,
            "name": self.name,
            "brutto": self.brutto,
            "currency": self.currency,
            "type": self.type,
        }

    def secondary_fields(self):
        return {
            "fee": self.fee,
            "from_email": self.from_email,
            "taxes": self.taxes,
            "invoice": self.invoice_id,
            "balance": self.balance,
            "topic": self.topic,
            "note": self.note,
            "payment_source": self.payment_source,
            "change": self.balance_change,
        }

    def minor_fields(self):
        return {
            "to_email": self.to_email,
            "transaction": self.transaction_number,
            "transaction_extra": self.additional_transaction_number,
            "amount": self.amount,
            "confirmation": self.confirmation,
            "status": self.status,
            "risk": self.risk,
            "bank": self.bank_name,
            "bank_number": self.bank_number,
            "transfer_fee": self.transfer_fee,
        }

    def to_normalized(self):
        return {
            "Data": self.date.date(),
            "Godzina": self.date.strftime("%H:%M:%S"),
            "Strefa Czasowa": self.date.tzname(),
            "Opis": self.type,
            "Waluta": self.currency,
            "Brutto": self.brutto,
            "Opłata": self.fee,
            "Netto": self.netto,
            "Saldo": self.balance,
            "Numer Transakcji": self.transaction_number,
            "Z adresu e-mail": self.from_email,
            "Nazwa": self.name,
            "Nazwa Banku": self.bank_name,
            "Rachunek Bankowy": self.bank_number,
            "Koszt wysyłki oraz koszty manipulacyjne": self.transfer_fee,
            "Kwota podatku": self.taxes,
            "Numer faktury": self.invoice_id,
            "Pomocniczy numer transakcji": self.additional_transaction_number,
        }


def load(filepath: str, delimiter: str = ","):
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
        # balance = 0
        for row in r:
            if row.get("Typ", row.get("Opis")) == "Przedmiot z koszyka":
                continue
            # if row.get("Status", "Zakończono") != "Zakończono":
            #    continue
            s = Paypal(row, delimiter == ";")
            # if s.currency == "USD":
            #    balance += s.brutto
            #    print(s.brutto, balance - (s.balance or 0), s.balance_change)

            if row.get("before_conversion"):
                b = Paypal(row, delimiter == ";")
                b.brutto = Decimal(row.get("before_conversion").replace(",", "."))
                if s.brutto < 0:
                    b.brutto = -b.brutto
                b.currency = row.get("original_currency")
                b.from_email = s.from_email
                ROWS.append(b.to_normalized())
                if not row.get("partial_currency"):
                    s.brutto = -s.brutto
                    ROWS.append(s.to_normalized())
                    s.brutto = -s.brutto

            if row.get("partial_currency"):
                p = Paypal(row, delimiter == ";")
                p.brutto = Decimal(row.get("partial").replace(",", "."))
                p.currency = row.get("partial_currency")
                p.from_email = s.from_email
                ROWS.append(p.to_normalized())

            ROWS.append(s.to_normalized())
    return ROWS


from collections import Counter


def main():
    deli = ";"
    rows = []
    for file in os.listdir("data/statements/paypal/"):
        single_rows = load(f"data/statements/paypal/{file}", deli)
        deli = ","
        single_rows = sorted(single_rows, key=lambda x: (x["Data"], x["Godzina"]))

        c = Counter()
        w = {}
        for row in single_rows:
            w[row["Waluta"]] = row["Saldo"]
            c[row["Waluta"]] += row.get("Netto") or row["Brutto"]
        print(w)
        print(c)

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

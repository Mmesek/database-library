from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from dateutil import tz
import csv
from . import models


@dataclass
class Row:
    timestamp: datetime
    title: str
    wallet: str
    amount: Decimal
    currency: str
    source: str
    wallet_number: str = None
    balance: Decimal = None
    description: str = None

    def as_operation(self):
        return models.Operation(timestamp=self.timestamp, description=self.description)

    def as_transaction(self):
        return models.Transaction(amount=self.amount)


ROWS = []
LOCAL_TZ = tz.gettz("Europe/Warsaw")


def from_mbank(file, currency: str):
    for i in csv.DictReader(file[1:], file[0].split(";"), delimiter=";"):
        year, month, day = i.get("#Data operacji").split("-")
        r = Row(
            timestamp=datetime(int(year), int(month), int(day), tzinfo=LOCAL_TZ),
            title=i.get("#Tytuł"),
            description=i.get("#Opis operacji"),
            amount=Decimal(i.get("#Kwota", "0").replace(",", ".").replace(" ", "")),
            balance=Decimal(i.get("#Saldo po operacji", "0").replace(",", ".").replace(" ", "")),
            currency=currency,
            wallet=i.get("#Nadawca/Odbiorca").replace("'", "").replace('"', "").strip(),
            wallet_number=i.get("#Numer konta").replace("'", "").replace('"', "").strip(),
            source="MBank - " + currency,
        )
        ROWS.append(r)
    return ROWS


def from_manual_pp(file):
    for i in csv.DictReader(file[1:], file[0].split(";"), delimiter=";"):
        date = i.get("date").split(" ")
        day, month, year = date[0].split("-")

        if len(date) > 1:
            hours = date[1].split(":")
        else:
            hours = [0, 0, 0]

        if len(hours) > 2:
            hour, minute, second = hours
        else:
            hour, minute = hours
            second = 0

        r = Row(
            timestamp=datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=LOCAL_TZ),
            title=i.get("title"),
            amount=-Decimal(i.get("price", "0").replace(",", ".").replace(" ", "").replace("+", "-")),
            currency=i.get("currency"),
            wallet=i.get("trader").replace("'", "").replace('"', "").strip(),
            source="Paypal - " + i.get("currency"),
        )
        ROWS.append(r)
        if i.get("before_conversion"):
            o = Row(
                timestamp=datetime(
                    int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=LOCAL_TZ
                ),
                title=i.get("title"),
                amount=-Decimal(i.get("before_conversion", "0").replace(",", ".").replace(" ", "").replace("+", "-")),
                currency=i.get("original_currency"),
                wallet=i.get("trader").replace("'", "").replace('"', "").strip(),
                source="Paypal - " + i.get("original_currency"),
            )
            ROWS.append(o)
        if i.get("partial_currency"):
            p = Row(
                timestamp=datetime(
                    int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=LOCAL_TZ
                ),
                title=i.get("title"),
                amount=-Decimal(i.get("partial", "0").replace(",", ".").replace(" ", "").replace("+", "-")),
                currency=i.get("partial_currency"),
                wallet=i.get("trader").replace("'", "").replace('"', "").strip(),
                source="Paypal - " + i.get("partial_currency"),
            )
            ROWS.append(p)
    return ROWS


def from_paypal(file):
    for i in csv.DictReader(file[1:], file[0].split(","), delimiter=","):
        month, day, year = i.get('"Data"').split("/")
        hour, minute, second = i.get('"Godzina"').split(":")
        r = Row(
            timestamp=datetime(
                int(year),
                int(month),
                int(day),
                int(hour),
                int(minute),
                int(second),
                tzinfo=tz.gettz(i.get('"Strefa czasowa"')),
            ),
            title=i.get('"Tytuł"'),
            description=i.get('"Opis"') or i.get('"Temat"') or i.get('"Typ"') or i.get('"Nazwa przedmiotu"'),
            amount=Decimal(i.get('"Netto"', "0").replace(",", ".").replace(" ", "")),
            balance=Decimal(i.get('"Saldo"', "0").replace(",", ".").replace(" ", "")),
            currency=i.get('"Waluta"'),
            wallet=i.get('"Nazwa"').replace("'", "").replace('"', "").strip(),
            wallet_number=i.get('"Z adresu e-mail"').replace("'", "").replace('"', "").strip(),
            source="Paypal - " + i.get('"Waluta"'),
        )
        ROWS.append(r)
    return ROWS


'"Nazwa","Opis",        "Waluta","Brutto","Opłata","Netto","Z adresu e-mail",                  "Numer transakcji",                                          "Pomocniczy numer transakcji","Numer faktury",                      "Saldo",'.split()
'"Nazwa","Temat","Typ", "Waluta","Brutto","Opłata","Netto","Z adresu e-mail","Na adres e-mail","Numer transakcji","Nazwa przedmiotu","Podatek od sprzedaży","Pomocniczy numer transakcji","Numer faktury","Numer potwierdzenia","Saldo","Uwaga","Źródło płatności","Wpływ na saldo"'.split()

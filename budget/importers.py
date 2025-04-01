import csv
from datetime import datetime, timezone
from . import models
from dateutil import tz
from decimal import Decimal

# NOTE:
# Paypal importer doesn't import currency conversions correctly
# They seem to be somewhat imported
# but with wrong values
# in fact, none of them do
# Paypal's tricky
# MBank misses that information altogether
# Implicit stuff?


def load_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.readlines()


WALLETS = {}


def get_wallet(session, name, cc):
    if not name:
        return None
    if name in WALLETS:
        return WALLETS[name]
    r = session.query(models.Wallet).filter(models.Wallet.name == name).first()
    if not r:
        r = models.Wallet(name=name, currency=cc)
        session.add(r)

    WALLETS[name] = r
    return r


def mbank(file, session, wallet: models.Wallet):
    fieldnames = "#Data operacji;#Data księgowania;#Opis operacji;#Tytuł;#Nadawca/Odbiorca;#Numer konta;#Kwota;#Saldo po operacji;".split(
        ";"
    )
    r = csv.DictReader(file[1:], fieldnames, delimiter=";")
    b = 0
    x = 0
    for i in r:
        name = (
            i.get("#Nadawca/Odbiorca").replace("'", "").replace('"', "").strip()
            or i.get("#Numer konta").replace("'", "").replace('"', "").strip()
        )
        title = i.get("#Tytuł", "")
        desc = i.get("#Opis operacji")
        amount = Decimal(i.get("#Kwota", "0").replace(",", ".").replace(" ", ""))
        if not name.strip():
            if title.startswith("PP") or title.startswith("PAYPAL"):
                name = "Paypal PLN"
            elif "KARTY" in desc:
                name = title.split(" ", 1)[0]
            elif "ZAKUP" in desc:
                name = title
            elif "OPŁATA" in desc or "PROWIZJA" in desc:
                name = "Opłaty"
            elif "ODSETEK" in desc:
                name = "Odsetki"
            elif "BLIK" in desc:
                name = "BLIK"
            else:
                print(name)
                print(title)
                print(desc)
                print(i.get("#Kwota", "0"))
                x += 1
                b += amount
                name = "Bank"
        _wallet = get_wallet(session, name, wallet.currency)
        sender = wallet if amount < 0 else _wallet
        recipent = wallet if amount > 0 else _wallet
        transactions = [models.Transaction(amount=amount, wallet=wallet)]
        if _wallet:
            transactions.append(models.Transaction(amount=-amount, wallet=_wallet))
        year, month, day = i.get("#Data operacji").split("-")
        session.add(
            models.Operation(
                timestamp=datetime(int(year), int(month), int(day)),
                description=desc + (": " + title if i.get("#Tytuł", None) else ""),
                transactions=transactions,
                sender=sender,
                recipent=recipent,
            )
        )
    session.commit()


def manual_paypal(file, session, wallet: models.Wallet):
    # NOTE: Possible bug with currencies
    fieldnames = "date;trader;title;price;currency;before_conversion;original_currency;partial;partial_currency;".split(
        ";"
    )
    WALLETS["Paypal PLN"] = wallet
    r = csv.DictReader(file[1:], fieldnames, delimiter=";")
    for i in r:
        # print(i.get("price"), i.get("currency"))
        _wallet = None
        final_amount = -Decimal(i.get("price").replace(",", ".").replace(" ", "").replace("+", "-"))
        final_currency = i.get("currency")
        print(final_amount, final_currency)
        # print(i.get("before_conversion"), i.get("original_currency"))
        try:
            original_amount = -Decimal(
                i.get("before_conversion", "0").replace(",", ".").replace(" ", "").replace("+", "-")
            )
        except:
            original_amount = None
        from_currency = i.get("original_currency", None)
        if original_amount:
            print(original_amount, from_currency)
        # print(i.get("partial"), i.get("partial_currency"))
        try:
            partial_amount = -Decimal(i.get("partial", "0").replace(",", ".").replace(" ", "").replace("+", "-"))
        except:
            partial_amount = None
        partial_currency = i.get("partial_currency", None)
        if partial_currency:
            print(partial_amount, partial_currency)
        if final_currency != wallet.currency:
            final_wallet = get_wallet(session, "Paypal " + final_currency, final_currency)
        else:
            final_wallet = wallet
        if from_currency and from_currency != final_currency:
            from_wallet = get_wallet(session, "Paypal " + from_currency, from_currency)

        if partial_currency:
            partial_wallet = get_wallet(session, "Paypal " + partial_currency, partial_currency)
        else:
            partial_wallet = None

        _wallet = get_wallet(session, i.get("trader").strip() or "Paypal", final_currency)
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
        _tz = tz.gettz("Europe/Warsaw")
        # amount = -Decimal(i.get("price", "0").replace(",", ".").replace(" ", "").replace("+", "-"))
        transactions = []
        if "February 2017" in i.get("title"):
            print(
                "February",
                partial_amount,
                partial_currency,
                partial_wallet is not None,
                "+",
                original_amount,
                from_currency,
                from_wallet is not None,
                "=",
                final_amount,
                final_currency,
                final_wallet is not None,
            )
        if _wallet:
            # This adds a positive value to destination wallet
            transactions.append(models.Transaction(amount=-final_amount, wallet=_wallet))

        if partial_wallet:
            # This adds negative value to partial source wallet
            transactions.append(models.Transaction(amount=partial_amount, wallet=partial_wallet))
        # elif from_currency:
        elif not from_currency:
            # This adds negative value to whole source wallet (In case there is no partial)
            transactions.append(models.Transaction(amount=final_amount, wallet=final_wallet))

        if from_currency:
            # This adds negative value to source wallet. It's unknown how much partial was worth. HOWEVER IT ADDS DESPITE FINAL WALLET
            transactions.append(models.Transaction(amount=original_amount, wallet=from_wallet))
            sender = from_wallet
        else:
            sender = wallet if final_amount < 0 else _wallet

        if wallet.currency != final_currency and final_amount > 0:
            recipent = get_wallet(session, "Paypal " + final_currency, final_currency)
        else:
            recipent = wallet if final_amount > 0 else _wallet

        # print(year, month, day, hour, minute, second, _tz)

        session.add(
            models.Operation(
                timestamp=datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=_tz),
                description=i.get("title", ""),
                transactions=transactions,
                sender=sender,
                recipent=recipent,
            )
        )
    session.commit()


def paypal(file, session, wallet):
    fieldnames = '"Data","Godzina","Strefa czasowa","Opis","Waluta","Brutto","Opłata","Netto","Saldo","Numer transakcji","Z adresu e-mail","Nazwa","Nazwa banku","Rachunek bankowy","Koszt wysyłki oraz koszty manipulacyjne","Kwota podatku","Numer faktury","Pomocniczy numer transakcji"'.split(
        ","
    )
    WALLETS["Paypal PLN"] = wallet
    r = csv.DictReader(file[1:], fieldnames, delimiter=",")
    for i in r:
        _wallet = None
        src_wallet = None
        month, day, year = i.get('"Data"').split("/")
        hour, minute, second = i.get('"Godzina"').split(":")
        _tz = tz.gettz(i.get('"Strefa czasowa"'))
        desc = i.get('"Opis"')
        currency = i.get('"Waluta"')
        # Recipent doesn't match currency on conversions
        amount = Decimal(i.get('"Netto"', "0").replace(",", ".").replace(" ", ""))
        name = i.get('"Nazwa"') or i.get('"Z adresu e-mail"')

        src_wallet = get_wallet(session, "Paypal " + currency, currency)
        if name:
            _wallet = get_wallet(session, name, currency)
        # else:
        # _wallet, src_wallet = src_wallet, _wallet

        sender = wallet if amount < 0 else _wallet
        recipent = wallet if amount > 0 else _wallet

        if i.get('"Opłata"') != "0,00":
            print(desc, i.get('"Opłata"'))

        transactions = [models.Transaction(amount=amount, wallet=src_wallet)]
        if _wallet:
            transactions.append(models.Transaction(amount=-amount, wallet=_wallet))

        session.add(
            models.Operation(
                timestamp=datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=_tz),
                description=desc,
                transactions=transactions,
                sender=sender,
                recipent=recipent,
            )
        )
    session.commit()


def paypal_new(file, session, wallet):
    fieldnames = '"Data","Godzina","Strefa czasowa","Nazwa","Typ","Status","Waluta","Brutto","Opłata","Netto","Z adresu e-mail","Na adres e-mail","Numer transakcji","Nazwa przedmiotu","Podatek od sprzedaży","Pomocniczy numer transakcji","Numer faktury","Numer potwierdzenia","Saldo","Temat","Uwaga","Źródło płatności","Status analizy autoryzacji","Możliwość skorzystania z ochrony","Wpływ na saldo","Filtr ryzyka"'.split(
        ","
    )

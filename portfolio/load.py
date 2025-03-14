from calendar import month_abbr
import dateparser
import pytz
from decimal import Decimal

from portfolio.models import Transaction
from portfolio.loaders.helpers import save, load_statement
from portfolio.loaders.utils import currency, number, NOTE


MONTH_ABBR_TRANSLATINS = {
    "sty": month_abbr[1],
    "lut": month_abbr[2],
    "mar": month_abbr[3],
    "kwi": month_abbr[4],
    "maj": month_abbr[5],
    "cze": month_abbr[6],
    "lip": month_abbr[7],
    "sie": month_abbr[8],
    "wrz": month_abbr[9],
    "paź": month_abbr[10],
    "lis": month_abbr[11],
    "gru": month_abbr[12],
}

def parse_date(ds: str):
    for key, translation in MONTH_ABBR_TRANSLATINS.items():
        ds = ds.replace(key, translation)
    dt = dateparser.parse(ds)
    if not dt.tzinfo:
        dt = dt.astimezone(pytz.timezone("Europe/Warsaw"))
    return dt

FUNCTIONS = {"currency": currency, "date": parse_date}

class Parser:
    def __init__(self, row: dict[str, str], schema: dict[str, str]):
        self.t = {}
        self.row = row
        for key, locator in schema.items():
            if type(locator) is dict:
                self.t[key] = self.parse_dict(locator)
            elif type(locator) is str:
                self.t[key] = self.parse_str(locator)

    def parse_dict(self, locator: dict[str, str | dict | list[str]]) -> bool:
        match locator["TYPE"]:
            case "ANY":
                value = self.row[locator["KEY"]].lower()
                if type(locator["ANY"]) is dict:
                    for k, v in locator["ANY"].items():
                        if type(v) is not list or k == "DEFAULT":
                            continue
                        if any(i.lower() in value for i in v):
                            return k
                    else:
                        return locator["ANY"]["DEFAULT"]
                else:
                    return any(i.lower() in value for i in locator["ANY"])

    def parse_str(self, locator: str) -> str:
        _type, value = locator.split(":", 1)
        match _type:
            case "KEY":
                return self.row[value].replace(",", ".")
            case "STRING":
                return value
            case "FUNC":
                f, v = value.split(":", 1)
                return FUNCTIONS[f](self.row[v])

    def __getitem__(self, id):
        return self.t[id]


if __name__ == "__main__":
    rows, schema = load_statement(True)
    transactions: list[Transaction] = []
    for row in rows:
        d = Parser(row, schema)
        quantity = abs(number(d["quantity"]))
        total = number(d["total"])
        value = number(d["subtotal"])
        if abs(value) > abs(total):
            total, value = value, total

        t = Transaction(
            type=d["type"],
            external_id=d["id"],
            timestamp=d["timestamp"],
            exchange=d["exchange"],
            category=d["category"],
            asset=d["asset"],
            currency=d["currency"],
            quantity=quantity if d["buy"] else -quantity,
            total=value,
            value=total,
            fee=number(d["fee"]),
            note=d["note"],
        )
        if any(i in d["note"].lower() for i in ["buy", "kupno", "withdraw", "sent"]):
            t.total = -abs(t.total)

        transactions.append(t)
        if d["trade"]:
            match = NOTE.match(t.note)
            transactions.insert(
                -1, t.convert(match.group("dest_asset"), number(match.group("dest_quantity")), number(d["fee"]))
            )
    save(transactions)

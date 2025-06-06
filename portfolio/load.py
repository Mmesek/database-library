from calendar import month_abbr
from collections import defaultdict
from datetime import UTC, datetime

from portfolio.models import Transaction
from portfolio.loaders.helpers import save, load_statement
def fix_transfers(seen: dict[datetime, list[Transaction]]):
    transactions: list[Transaction] = []
    seen = defaultdict(lambda: list())
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
            note="LIQUIDATION" if d["note"] == "UNKNOWN_LIQUIDITY_INDICATOR" else d["note"],
        )
        if t.type == "TRANSFER":
            seen[t.timestamp].append(t)

        try:
            prc = Decimal(d["price"])
            t.price = prc
        except Exception:
            pass
        if any(i in d["note"].lower() for i in ["withdraw", "sent", "sold", "send", "wychodzący", "withdrew"]):
            t.total = -abs(t.total)
        if d["type"] == "STAKING":
            t.total = Decimal()

        transactions.append(t)
        if t.note == "LIQUIDATION":  # No convertion on Liquidation - we lost
            continue

        if d["trade"] or (("DEPOSIT" in t.type or "WITHDRAW" in t.type) and "perp" in t.exchange.lower()):
            match = NOTE.match(t.note)
            if not match:
                tc = t.convert(d["currency"], value, number(d["fee"]))
            else:
                price = number(match.group("rate"))
                quantity = number(match.group("src"))
                if quantity != abs(t.quantity):
                    if t.quantity < 0:
                        t.quantity = -quantity
                    else:
                        t.quantity = quantity
                total = price * quantity
                if not t.fee:
                    value = total - t.fee if d["buy"] else total + t.fee
                tc = t.convert(
                    match.group("dest_asset"), total or number(match.group("dest_quantity")), number(d["fee"])
                )
            if not tc.quantity:
                continue

            if ("DEPOSIT" in t.type or "WITHDRAW" in t.type) and "perp" in t.exchange.lower():
                tc.exchange = "COINBASE"
                tc.asset = t.asset
                tc.quantity = -t.quantity

            if d["buy"]:
                transactions.insert(-1, tc)
            else:
                transactions.append(tc)
    for ts in seen:
        note = seen[ts][0].note
        for t in seen[ts]:
            if " to " in note or " from " in note:
                break
            t.type = "SELL"
            if not t.note:
                t.note = ""
            t.note += " LIQUIDATION"
            t.note.strip()
            t.exchange = "COINBASE Advanced"

    return transactions


if __name__ == "__main__":
    t = []
    t += parse(*load_statement(True))
    t += parse(*load_statement(False))
    t += parse(*load_statement(False, x=True))
    save(t)

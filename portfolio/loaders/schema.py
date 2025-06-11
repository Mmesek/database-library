from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from portfolio.loaders.utils import parse_date, number, NOTE
from portfolio.models import Transaction

OUTGOING = ["withdraw", "sent", "sold", "send", "wychodzący", "withdrew", "debited"]


@dataclass
class Schema:
    id: str
    timestamp: datetime
    exchange: str
    category: str
    type: str
    buy: bool
    trade: bool
    asset: str
    quantity: Decimal
    price: Decimal
    currency: str
    note: str
    fee: Decimal
    total: Decimal
    subtotal: Decimal
    is_api: bool = False

    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = parse_date(self.timestamp)
        self.quantity = abs(number(self.quantity))
        self.quantity = self.quantity if self.buy else -self.quantity
        self.fee = number(self.fee)

        value = number(self.subtotal)
        total = number(self.total)
        if abs(value) > abs(total):
            total, value = value, total
        self.total = total
        self.subtotal = value

        if self.note == "UNKNOWN_LIQUIDITY_INDICATOR":
            self.note = "LIQUIDATION"

        self.price = number(self.price)

        if any(i in self.note.lower() for i in OUTGOING):
            self.total = -abs(self.total)
        if self.type == "STAKING":
            self.total = Decimal()

        if "/" in self.currency:
            self.currency = self.currency.replace(self.asset, "").replace("/", "")

        if self.type == "TRANSFER" and all(i not in self.note for i in [" to ", " from "]):
            self.exchange = "COINBASE PERPETUALS"
            self.type = "SELL"
            if not self.note:
                self.note = ""
            self.note += " LIQUIDATION"
            self.note.strip()

    def to_transaction(self):
        return Transaction(
            type=self.type,
            external_id=self.id,
            timestamp=self.timestamp,
            exchange=self.exchange,
            category=self.category,
            asset=self.asset,
            currency=self.currency,
            quantity=self.quantity,
            total=self.total,
            value=self.subtotal,
            fee=self.fee,
            note=self.note,
            price=self.price,
            is_api=self.is_api,
        )

    def convert(self, asset: str, quantity: Decimal, price: str = None, currency: str = None):
        return Schema(
            self.id,
            self.timestamp,
            self.exchange,
            self.category,
            self.type,
            None,
            None,
            asset,
            (quantity if self.quantity < 0 else -quantity) if isinstance(quantity, Decimal) else quantity,
            price or self.price,
            currency or self.asset,
            self.note,
            self.fee,
            -self.total,
            self.subtotal,
            is_api=self.is_api,
        )

    def handle_conversion(self, transaction: Transaction):
        match = NOTE.match(self.note)
        if not match:
            tc = transaction.convert(self.currency, self.subtotal, self.fee)
        else:
            g = match.groupdict()
            _tc = self.convert(
                g.get("dest_asset"),
                g.get("dest_quantity"),
                price=g.get("rate", None),
                currency=g.get("rate_pair", None),
            )
            quantity = number(match.group("src"))
            # if quantity != abs(self.quantity):
            #    if self.quantity < 0:
            #        self.quantity = -quantity
            #    else:
            #        self.quantity = quantity
            # quantity = quantity if self.quantity < 0 else -quantity

            _tc.total = _tc.price * quantity
            # if not tc.price:
            #    tc.price = tc.total / quantity
            tc = transaction.convert(g.get("dest_asset"), -_tc.quantity, self.fee)
            tc.price = _tc.price
            transaction.price = _tc.price
            # tc.currency = _tc.currency # NOTE: Disabled for simplicity, # TODO enable for prod

        if not tc.quantity:
            return

        if ("DEPOSIT" in self.type or "WITHDRAW" in self.type) and "perp" in self.exchange.lower():
            tc.exchange = "COINBASE"
            tc.asset = self.asset
            tc.quantity = -self.quantity

        # t = tc.to_transaction()
        # t.price = tc.price
        return tc

    def should_convert(self, transaction: Transaction, is_trade: bool):
        if self.note == "LIQUIDATION":  # No convertion on Liquidation - we lost
            return
        if self.type == "PERPETUAL":
            transaction.price = self.price
            if transaction.total != Decimal(0) and transaction.price != Decimal(0):
                transaction.quantity = self.total / self.price if self.price else 0
                transaction.asset = "USDC"
                # return transaction.convert("USDC", self.total / self.price if self.price else 0, self.fee)
        if is_trade or (("DEPOSIT" in self.type or "WITHDRAW" in self.type) and "perp" in self.exchange.lower()):
            return self.handle_conversion(transaction)

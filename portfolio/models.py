from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column as Column

from mlib.database import ID, Timestamp, Base

# Operation,  Asset, Quantity, Price, Currency,    Net,   Tar, Brutto
#   Deposit,    EUR,      300,     1,      EUR,    300,     0,    300
#       Buy,    BTC,        2,   100,      EUR,    199,     1,   -200
#    Reward,    ALT,        2,   0.5,      EUR,      1,     0,      0
#    Reward,    ALT,        1,   0.6,      EUR,    0.6,     0,      0
#      Sell,    BTC,        1,   100,      EUR,    100,     0,    100
# -----------------|-Holding-|--Avg-|---------|-Value-|-Fees-|----Sum
#               BTC,        1,   100,      EUR,     99,     1,     99
#               AKT,        3,  0.53,      EUR,    1.6,     0,      0
#               EUR,      200,     1,      EUR,    200,     0,    200


class Transaction(Timestamp, ID, Base):
    exchange: Mapped[str]
    """Where this transaction took place"""
    category: Mapped[str]
    """Type of this transaction"""
    type: Mapped[str]
    # buying: Mapped[bool]
    # """Whether this transaction represents buying or selling"""
    asset: Mapped[str]
    """Name of the asset"""
    quantity: Mapped[Decimal]
    """Quantity of the exchange"""
    currency: Mapped[str] = Column(nullable=True)
    """Currency of the transaction"""
    rate_currency: Mapped[str] = Column(default="PLN")
    """Currency which applies it's rate"""
    note: Mapped[str | None] = Column(default=None, nullable=True)
    """Transaction note"""
    price: Mapped[Decimal] = Column(default=Decimal())
    """Price per 1 asset"""
    rate: Mapped[Decimal] = Column(default=Decimal(1))
    """Exchange rate to rate_currency applicable for this transaction"""
    fee: Mapped[Decimal] = Column(default=Decimal())
    """Fee of this transaction"""
    value: Mapped[Decimal] = Column(default=Decimal())
    """Value of this transaction. Without fee for Buy orders, with for sell orders"""
    total: Mapped[Decimal] = Column(
        default=Decimal())  # Should we rename it to change?
    """Balance change, including fees for Buy orders"""
    external_id: Mapped[str] = Column(default=None, nullable=True)

    def __post_init__(self):
        if type(self.total) is not Decimal:
            self.total = Decimal(self.total.replace(",", ""))
        if type(self.quantity) is not Decimal:
            self.quantity = Decimal(self.quantity.replace(",", ""))
        if type(self.fee) is not Decimal:
            self.fee = Decimal(self.fee.replace(",", ""))
        if not self.price and self.quantity:
            self.price = Decimal(
                (abs(self.total) - self.fee) / abs(self.quantity))
        if type(self.price) is not Decimal:
            self.price = Decimal(self.price.replace(",", ""))
        if not self.fee:
            self.fee = Decimal()

    @property
    def cost(self):
        """Total cost in `currency`. Should equal `total` - `fee`"""
        value = self.price * self.quantity
        return value  # return -value if self.buying else value

    # @property
    # def converted(self):
    #    """Total cost in `rate_currency`"""
    #    value = round(self.cost * self.rate, 2)
    #    return -value if self.buying else value

    @property
    def raw_cost(self):
        """
        BUY  = -10 - 2 = -12
        SELL =  10 - 2 =   8
        """
        return self.total - self.fee

    # def profit(self):
    #    return self.total - self.fee if self.buying else self.total
    def convert(self, asset: str, quantity: Decimal, fee):
        return Transaction(
            type=self.type,
            timestamp=self.timestamp,
            external_id=self.external_id,
            exchange=self.exchange,
            category=self.category,
            asset=asset,
            quantity=quantity if self.quantity < 0 else -quantity,
            note=self.note,
            currency=self.currency,
            total=-self.value,
            fee=fee,
            value=self.total,
        )

    def print(self):
        print(
            self.timestamp,
            " BUY" if self.buying else "SELL",
            f"{self.asset:>8} {abs(self.total):>6.4} {self.currency}"
            + (f" -> {abs(self.converted):>6.4} {self.rate_currency}" if self.currency !=
               self.rate_currency else ""),
            self.quantity,
        )

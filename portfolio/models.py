from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column as Column

from mlib.database import ID, Timestamp, Base


class Transaction(ID, Timestamp, Base):
    exchange: Mapped[str]
    """Where this transaction took place"""
    category: Mapped[str]
    """Type of this transaction"""
    buying: Mapped[bool]
    """Whether this transaction represents buying or selling"""
    asset: Mapped[str]
    """Name of the asset"""
    quantity: Mapped[Decimal]
    """Quantity of the exchange"""
    price: Mapped[Decimal]
    """Price per 1 asset"""
    currency: Mapped[str]
    """Currency of the transaction"""
    rate: Mapped[Decimal] = Column(default=Decimal(1))
    """Exchange rate to rate_currency applicable for this transaction"""
    rate_currency: Mapped[str] = Column(default="PLN")
    """Currency which applies it's rate"""
    note: Mapped[str | None] = Column(default=None, nullable=True)
    """Transaction note"""
    fee: Mapped[Decimal] = Column(default=0)
    """Fee of this transaction"""
    total: Mapped[Decimal] = Column(default=0)
    """Total paid, including fees"""

    def __post_init__(self):
        if type(self.quantity) is not Decimal:
            self.quantity = Decimal(self.quantity.replace(",", ""))
        if type(self.price) is not Decimal:
            self.price = Decimal(self.price.replace(",", ""))
        if type(self.fee) is not Decimal:
            self.fee = Decimal(self.fee.replace(",", ""))
        if type(self.total) is not Decimal:
            self.total = Decimal(self.total.replace(",", ""))

    @property
    def cost(self):
        """Total cost in `currency`. Should equal `total` - `fee`"""
        value = self.price * self.quantity
        return -value if self.buying else value

    @property
    def converted(self):
        """Total cost in `rate_currency`"""
        value = round(self.cost * self.rate, 2)
        return -value if self.buying else value

    def convert(self, asset: str, quantity: Decimal, fee: Decimal = 0):
        return Transaction(
            self.exchange,
            self.category,
            not self.buying,
            asset,
            quantity,
            self.cost / quantity,
            self.currency,
            self.rate,
            self.rate_currency,
            fee=fee,
            total=self.total,
            timestamp=self.timestamp,
        )

    def print(self):
        print(
            self.timestamp,
            " BUY" if self.buying else "SELL",
            f"{self.asset:>8} {abs(self.total):>6.4} {self.currency}"
            + (f" -> {abs(self.converted):>6.4} {self.rate_currency}" if self.currency != self.rate_currency else ""),
            self.quantity,
        )

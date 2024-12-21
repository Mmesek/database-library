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

    @property
    def cost(self):
        """Total cost in `currency`"""
        value = self.price * self.quantity
        return -value if self.buying else value

    @property
    def converted(self):
        """Total cost in `rate_currency`"""
        value = round(self.cost * self.rate, 2)
        return -value if self.buying else value

    def convert(self, asset: str, quantity: Decimal):
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
        )

    def print(self):
        print(
            self.timestamp,
            " BUY" if self.buying else "SELL",
            f"{self.asset:>8} {abs(self.cost):>6.4} {self.currency}"
            + (f" -> {abs(self.converted):>6.4} {self.rate_currency}" if self.currency != self.rate_currency else ""),
        )

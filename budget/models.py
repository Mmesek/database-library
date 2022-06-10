from collections import Counter
from datetime import datetime
from decimal import Decimal

from sqlmodel import Relationship, Field

from ..utils.mixins import *


class Wallet(Name, table=True):
    outgoing: list["Transaction"] = Relationship(back_populates="sender")
    """List of all outgoing transactions"""
    incoming: list["Transaction"] = Relationship(back_populates="recipent")
    """List of all incoming transactions"""

    @property
    def total_sent(self) -> Counter:
        """Total outgoing amounts by currency"""
        c = Counter()
        for t in self.outgoing:
            c.update({t.currency: t.amount})
        return c

    @property
    def total_received(self) -> Counter:
        """Total incoming amounts by currency"""
        c = Counter()
        for t in self.outgoing:
            c.update({t.currency: t.amount})
        return c

    @property
    def balance(self) -> Decimal:
        """Remaining Balance (Received minus Sent)"""
        return self.total_received - self.total_sent


class Transaction(ID, table=True):
    date: datetime
    """Date of operation"""
    amount: Decimal
    """Amount transfered"""
    currency: str
    """Currency transfered"""
    description: str
    """Operation's description"""
    sender_id: int = Field(foreign_key="wallet.id")
    """Wallet's source. Outgoing"""
    recipent_id: int = Field(foreign_key="wallet.id")
    """Wallet's destination. Incoming"""
    sender: Wallet
    """Sender's wallet"""
    recipent: Wallet
    """Recipent's Wallet"""

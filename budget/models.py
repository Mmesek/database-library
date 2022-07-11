from typing import List, Optional
from collections import Counter
from decimal import Decimal

from sqlmodel import Relationship, Field

from ..utils.mixins import Name, Timestamp, ID


class Wallet(Name, table=True):
    outgoing: List["Transaction"] = Relationship(
        back_populates="sender", sa_relationship_kwargs={"foreign_keys": "Transaction.sender_id"}
    )
    """List of all outgoing transactions"""
    incoming: List["Transaction"] = Relationship(
        back_populates="recipent", sa_relationship_kwargs={"foreign_keys": "Transaction.recipent_id"}
    )
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
        for t in self.incoming:
            c.update({t.currency: t.amount})
        return c

    @property
    def balance(self) -> Decimal:
        """Remaining Balance (Received minus Sent)"""
        return self.total_received - self.total_sent

    def add(self, value: float, currency: str, description: str) -> Decimal:
        """Add funds to Wallet"""
        self.incoming.append(Transaction(amount=value, currency=currency, description=description))
        return self.balance.get(currency, 0)

    def transfer(
        self, amount: float, currency: str, description: str, recipent_id: int = None, recipent: "Wallet" = None
    ) -> Decimal:
        """
        Transfer funds to another Wallet if there are enough funds in current Wallet

        Parameters
        ----------
        amount:
            Amount to transfer out of this wallet
        currency:
            Currency to transfer. Requires this currency being present on this wallet
        description:
            Description of this transaction
        recipent_id:
            Target's Wallet ID. Leave empty when using `recipent`
        recipent:
            Target's Wallet. Leave empty when using `recipent_id`
        """
        if self.balance.get(currency, 0) >= amount:
            self.outgoing.append(
                Transaction(
                    amount=amount,
                    currency=currency,
                    description=description,
                    recipent_id=recipent_id,
                    recipent=recipent,
                )
            )
        else:
            print("Not enough funds to transfer")
        return self.balance.get(currency, 0)


class Transaction(Timestamp, ID, table=True):
    amount: Decimal
    """Amount transfered"""
    currency: str = Field(max_length=3)
    """Currency transfered"""
    description: str
    """Operation's description"""

    sender_id: Optional[int] = Field(foreign_key="wallet.id")
    """Wallet's source. Outgoing"""
    recipent_id: Optional[int] = Field(foreign_key="wallet.id")
    """Wallet's destination. Incoming"""

    sender: Optional[Wallet] = Relationship(
        back_populates="outgoing", sa_relationship_kwargs={"foreign_keys": "Transaction.sender_id"}
    )
    """Sender's wallet"""
    recipent: Optional[Wallet] = Relationship(
        back_populates="incoming", sa_relationship_kwargs={"foreign_keys": "Transaction.recipent_id"}
    )
    """Recipent's Wallet"""

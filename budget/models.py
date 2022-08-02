from typing import List, Optional
from decimal import Decimal

from sqlmodel import Relationship, Field, SQLModel

from ..utils.mixins import Name, Timestamp, ID


class Wallet(Name, table=True):
    currency: str = Field(max_length=3)
    """Wallet's Currency in Alpha 2 (Currency Code) notation (3 letters)"""
    transactions: List["Transaction"] = Relationship(back_populates="wallet")
    """List of all transactions"""
    # operations: List["Operation"] = Relationship(link_model=Transaction)  # NOTE: No clue if it'll work!
    # """List of all operations associated with this Wallet"""
    outgoing: List["Operation"] = Relationship(
        back_populates="sender", sa_relationship_kwargs={"foreign_keys": "Operation.sender_id"}
    )
    """List of all outgoing transactions"""
    incoming: List["Operation"] = Relationship(
        back_populates="recipent", sa_relationship_kwargs={"foreign_keys": "Operation.recipent_id"}
    )
    """List of all incoming transactions"""

    @property
    def total_sent(self) -> Decimal:
        return sum([i.amount for i in self.transactions if i.amount < 0])

    @property
    def total_received(self) -> Decimal:
        return sum([i.amount for i in self.transactions if i.amount > 0])

    @property
    def balance(self) -> Decimal:
        """Current Balance"""
        return sum([i.amount for i in self.transactions])

    def transfer(
        self, amount: float, description: str = None, target: "Wallet" = None, operation: "Operation" = None
    ) -> Decimal:
        """
        Transfer funds to another Wallet if there are enough funds in current Wallet

        Parameters
        ----------
        amount:
            Amount to transfer out of this wallet. Raises ValueError on insufficent funds
        description:
            Description of this transaction
        target:
            Target's Wallet.
        operation:
            Operation new Transaction should be attachted to. Otherwise creates new Operation
        """
        if self.balance < amount:
            raise ValueError("Current wallet doesn't have enough funds to transfer out", self.balance, amount)
        elif amount < 0 and target and target.balance < abs(amount):
            raise ValueError("Target's wallet doesn't have enough funds to transfer in", target.balance, amount)

        if not operation:
            operation = Operation(description=description, sender=self, recipent=target)
            self.outgoing.append(operation)

        operation.transactions.append(Transaction(amount=-amount, wallet=self))
        if target:
            operation.transactions.append(Transaction(amount=amount, wallet=target))

        return self.balance

    def history(self):
        for i in sorted(self.outgoing + self.incoming, key=lambda x: x.timestamp):
            print(
                i.timestamp,
                i.amount,
                i.sender.name if i.sender else None,
                i.recipent.name if i.recipent else None,
                i.description,
            )

    def sent(self):
        for i in self.outgoing:
            print(i.timestamp, i.amount, i.recipent.name if i.recipent else None, i.description)

    def received(self):
        for i in self.incoming:
            print(i.timestamp, i.amount, i.sender.name if i.sender else None, i.description)


class Operation(Timestamp, ID, table=True):
    description: str
    """Operation's description"""
    transactions: List["Transaction"] = Relationship(back_populates="operation")
    """List of Operation details"""

    sender_id: Optional[int] = Field(foreign_key="wallet.id")
    """Source Wallet. Outgoing"""
    recipent_id: Optional[int] = Field(foreign_key="wallet.id")
    """Destination Wallet. Incoming"""

    sender: Optional[Wallet] = Relationship(
        back_populates="outgoing", sa_relationship_kwargs={"foreign_keys": "Operation.sender_id"}
    )
    """Sender's wallet"""
    recipent: Optional[Wallet] = Relationship(
        back_populates="incoming", sa_relationship_kwargs={"foreign_keys": "Operation.recipent_id"}
    )
    """Recipent's Wallet"""

    @property
    def amount(self) -> Decimal:
        """Amount transfered in this operation"""
        # NOTE: If wallet's currency differs, it's not reflected here. TODO
        return sum([i.amount for i in self.transactions if i.amount > 0])


class Transaction(SQLModel, table=True):
    operation_id: int = Field(foreign_key="operation.id", primary_key=True)
    """Operation ID this Transaction is for"""
    operation: Operation = Relationship(back_populates="transactions")
    """Operation this Transaction is for"""
    amount: Decimal
    """Amount transfered"""

    wallet_id: int = Field(foreign_key="wallet.id", nullable=True, primary_key=True)
    """Wallet's ID"""
    wallet: Wallet = Relationship(back_populates="transactions")
    """Affected Wallet"""

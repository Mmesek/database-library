from typing import List
from decimal import Decimal

from sqlmodel import Relationship, Field, SQLModel

from ..utils.mixins import Name, Timestamp, ID


class Wallet(Name, table=True):
    currency: str = Field(max_length=3)
    """Wallet's Currency in Alpha 2 (Currency Code) notation (3 letters)"""
    transactions: List["Transaction"] = Relationship(back_populates="wallet")
    """List of all transactions"""
    operations: List["Operation"] = Relationship(link_model="Transaction")  # NOTE: No clue if it'll work!
    """List of all operations associated with this Wallet"""

    @property
    def balance(self) -> Decimal:
        """Current Balance"""
        return sum([i.amount for i in self.transactions])

    def transfer(
        self, amount: float, description: str = None, target: "Wallet" = None, operation: "Operation" = None
    ) -> "Operation":
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
            raise ValueError("Current wallet doesn't have enough funds to transfer out")
        elif amount < 0 and target.balance < abs(amount):
            raise ValueError("Target's wallet doesn't have enough funds to transfer in")

        if not operation:
            operation = Operation(description=description)
        self.transactions.append(Transaction(amount=-amount, operation=operation))
        if target:
            target.transactions.append(Transaction(amount=amount, operation=operation))
        return operation


class Operation(Timestamp, ID, table=True):
    description: str
    """Operation's description"""
    transactions: List["Transaction"] = Relationship(back_populates="transaction")
    """List of Operation details"""

    @property
    def amount(self) -> Decimal:
        """Amount transfered in this operation"""
        # NOTE: If wallet's currency differs, it's not reflected here. TODO
        return sum([i.amount for i in self.transactions if i.amount > 0])


class Transaction(SQLModel, table=True):
    operation_id: int = Field(foreign_key="transaction.id")
    """Operation ID this Transaction is for"""
    operation: Operation = Relationship(back_populates="transactions")
    """Operation this Transaction is for"""
    amount: Decimal
    """Amount transfered"""

    wallet_id: int = Field(foreign_key="wallet.id")
    """Wallet's ID"""
    wallet: Wallet = Relationship(back_populates="transactions")
    """Affected Wallet"""

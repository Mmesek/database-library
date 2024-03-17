from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from mlib.database import Base
from mlib.utils import percent_of, deduce_percentage

# ZUS Thresholds
LUMP_LOW_THRESHOLD = 60000
LUMP_HIGH_THRESHOLD = 300000

# ZUS modifiers
LUMP_LOW_MULTIPLIER = 60
LUMP_MID_MULTIPLIER = 100
LUMP_HIGH_MULTIPLIER = 180

# ZUS Base percent
BASE_LUMP_PERCENT = 9
BASE_SCALE_PERCENT = 9
BASE_LINEAR_PERCENT = 4.9

# Deductible costs
LINEAR_DEDUCTIBLE_PER_YEAR = 10200


class Contrahent(Base):
    id: Mapped[str] = mapped_column(primary_key=True)
    """VAT ID - Country Prefix + NIP"""
    name: Mapped[str]
    nip: Mapped[Optional[str]]
    regon: Mapped[Optional[str]]
    address: Mapped[Optional[str]]
    zip_code: Mapped[Optional[str]]


class Invoice(Base):
    id: Mapped[str] = mapped_column(primary_key=True)
    """Invoice's ID"""
    contrahent_id: Mapped[str] = mapped_column(ForeignKey("Contrahent.id"))
    """Sender of this Invoice"""
    timestamp: Mapped[datetime]
    """When was this invoice created"""
    items: Mapped[list["Invoice_Item"]] = relationship(back_populates="invoice", cascade="all, delete-orphan")


class Invoice_Item(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("Invoice.id"))
    """Related Invoide"""
    invoice: Mapped[Invoice] = relationship(back_populates="items")
    item: Mapped[str]
    """Item on Invoice"""
    type: Mapped[str]
    """Type of this item"""
    quantity: Mapped[int]
    netto: Mapped[Decimal]
    """Value without VAT"""
    vat: Mapped[Decimal]
    """VAT percentage applied to this item"""
    brutto: Mapped[Optional[Decimal]]
    """Value after adding VAT"""
    total_netto: Mapped[Decimal]
    total_vat: Mapped[Decimal]
    total_brutto: Mapped[Decimal]

    def __init__(
        self, item: str, type: str, quantity: int = 1, netto: float = None, vat: float = 23, brutto: float = None
    ):
        self.item = item
        self.type = type
        if not netto and brutto:
            self.netto = round(deduce_percentage(brutto, vat), 2)
        else:
            self.netto = netto
        self.vat = vat
        if not brutto and netto:
            self.brutto = round(netto + percent_of(netto, vat), 2)
        else:
            self.brutto = brutto
        self.quantity = quantity
        self.total_netto = self.netto * quantity
        self.total_brutto = self.brutto * quantity
        self.total_vat = round(self.total_brutto - self.total_netto, 2)

    def deductible(self, percent: float = 12):
        """Can only deduce on scale or linear"""
        return round(percent_of(self.total_netto, percent))


class ZUS(Base):
    date: Mapped[datetime] = mapped_column(primary_key=True)
    """Month in which it's applicable"""
    name: Mapped[str]
    min: Mapped[Decimal] = mapped_column(default=0)
    """Minimum value"""
    percent: Mapped[Decimal] = mapped_column(default=0)
    min_pay: Mapped[Decimal] = mapped_column(default=0)
    average_pay: Mapped[Decimal] = mapped_column(default=0)
    base: Mapped[Decimal] = mapped_column(default=None)

    def on_lump(self, amount: Decimal, months: int = 12) -> Decimal:
        amount = self.base or amount
        if months:
            amount *= months
        if not self.name == "health":
            return round(percent_of(amount, self.percent), 2)
        if amount < LUMP_LOW_THRESHOLD:
            return round(percent_of(percent_of(self.average_pay, LUMP_LOW_MULTIPLIER), BASE_LUMP_PERCENT), 2)
        elif amount >= LUMP_LOW_THRESHOLD and amount < LUMP_HIGH_THRESHOLD:
            return round(percent_of(percent_of(self.average_pay, LUMP_MID_MULTIPLIER), BASE_LUMP_PERCENT), 2)
        else:
            return round(percent_of(percent_of(self.average_pay, LUMP_HIGH_MULTIPLIER), BASE_LUMP_PERCENT), 2)

    def on_scale(self, amount: Decimal) -> Decimal:
        amount = self.base or amount
        return round(percent_of(amount, BASE_SCALE_PERCENT), 2)

    def on_linear(self, amount: Decimal) -> Decimal:
        amount = self.base or amount
        return round(percent_of(amount, BASE_LINEAR_PERCENT), 2)

    def deductible(self, amount: Decimal, percent: float = 7.75):
        """Not quite sure"""
        return round(percent_of(self.on_scale(amount), percent))


class Tax(Base):
    name: Mapped[str] = mapped_column(primary_key=True)
    percent: Mapped[Decimal]
    not_taxed: Mapped[Optional[Decimal]] = mapped_column(default=None)
    cap: Mapped[Optional[Decimal]] = mapped_column(default=None)
    # tax_after_cap: Mapped[Optional["Tax"]] = mapped_column(ForeignKey("Tax.name"))
    # next_tax: Mapped["Tax"] = relationship()
    min: Mapped[Optional[Decimal]] = mapped_column(default=None)

    def per_month(self, amount: Decimal, total: Decimal = 0) -> Decimal:
        if total + amount <= (self.not_taxed or 0):
            # This month is tax excempt
            return 0
        elif total <= (self.not_taxed or 0):
            amount = max(total + amount - (self.not_taxed or 0), 0)
        if not self.cap or total + amount <= self.cap:
            # Tax below cap
            return round(percent_of(amount, self.percent), 2)
        elif total + amount > self.cap:
            # Tax above cap
            return round(percent_of(amount, 32), 2)
            # return self.next_tax.per_month(amount, total)
        # high = _total - self.cap
        high = (total + amount) - (self.cap)
        low = max(amount - high, 0)
        return round(percent_of(low, 12) + percent_of(high, 32), 2)

    def per_year(self, amount: Decimal) -> Decimal:
        total = amount
        low = min(self.cap, total)
        high = total - low
        return round(percent_of(low - self.not_taxed, 12) + percent_of(high, 32), 2)

    def deductible(self, amount):
        """Deductible on scale and linear, equal tax percentage"""
        return round(percent_of(amount, self.percent))

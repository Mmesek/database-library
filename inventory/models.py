from datetime import datetime
from decimal import Decimal
from ..utils.mixins import Name, URL


class Item(Name, table=True):
    date: datetime
    """Date when this item was obtained"""
    price: Decimal
    """Cost of this item"""


class Wishlist(URL, Name, table=True):
    date: datetime
    """Date when this item was added to wishlist"""
    lowest_price: Decimal
    """Lowest price of this item"""
    current_price: Decimal
    """Last fetched price of this item"""

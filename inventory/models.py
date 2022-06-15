from decimal import Decimal
from ..utils.mixins import Name, URL, Price, Timestamp


class Item(Timestamp, Price, Name, table=True):
    pass

class Wishlist(Timestamp, Price, URL, Name, table=True):
    lowest_price: Decimal
    """Lowest price of this item"""

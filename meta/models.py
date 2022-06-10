from datetime import datetime
from ..utils.mixins import ID


class Quote(ID, table=True):
    author: str
    quote: str
    added_date: datetime

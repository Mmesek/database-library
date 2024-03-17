from decimal import Decimal

import httpx
from bs4 import BeautifulSoup
from howlongtobeatpy import HowLongToBeat, HowLongToBeatEntry
from sqlalchemy import select, text
from mlib.database import SQL

from bundles.models import Game, Wishlist, Price

engine = SQL(location="192.168.1.102", name="Keys", db="postgresql+psycopg", echo=False)
session = engine.session()

BAZAR = "https://bazar.lowcygier.pl/?type=&title="
HLTB = HowLongToBeat()


def sanitize(game):
    return game.replace(" ", "+").replace("!", "").replace("?", "").replace("'", "+").replace(".", "")


def get_hltb(game):
    try:
        result: HowLongToBeatEntry = HLTB.search(game)[0]
        return result.main_story, result.completionist
    except:
        return 0, 0


def get_price(game):
    try:
        data = httpx.get(BAZAR + sanitize(game), timeout=10)
        data.raise_for_status()
        soup = BeautifulSoup(data.text, "html.parser")
        lis = soup.find("div", id="w0", class_="list-view")
        return lis.find("p", class_="prc").text.replace(" zł", "").replace(",", ".")
    except:
        return 0.0


games = list(session.execute(text(r'SELECT DISTINCT game FROM "WishlistedGames"')).scalars())
for game in games:
    if _game := session.execute(select(Game).where(Game.name == game)).scalar():
        wl = session.execute(select(Wishlist).where(Wishlist.game_id == _game.id)).scalar()
        prc = Price(game_id=_game.id, price=Decimal(get_price(game)), currency="PLN", timestamp=None)
        session.merge(prc)
        if not wl.hltb_story:
            wl.hltb_story, wl.hltb_total = get_hltb(game)

session.commit()

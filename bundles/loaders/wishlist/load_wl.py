from sqlalchemy import select, text
from mlib.database import SQL
from bundles.models import Game, Wishlist

engine = SQL(location="192.168.1.102", name="Keys", echo=False)
session = engine.session()

with open("data/games/wl.txt", "r", newline="", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        # session.add(Wishlist_2(game=line, timestamp=None, interest_scale=1, played_before=False))
        game = session.execute(
            text(
                r"""
SELECT set_limit(0.8);
SELECT "Game".name, "Game".id 
FROM "Game"
WHERE lower("Game".name) % lower(:name_1)
ORDER BY SIMILARITY(name, lower(:name_1)) DESC
"""
            ),
            {"name_1": line},
        ).first()
        if not game:
            session.add(Game(name=line, keys=[]))
        if game:
            stmt = select(Wishlist).where(Wishlist.game_id == game.id)
            wl_game = session.execute(stmt).scalar()
            if not wl_game:
                print("Adding", game[0])
                session.add(
                    Wishlist(
                        game_id=game[1],
                        timestamp=None,
                        interest_scale=1,
                        played_before=False,
                        hltb_story=None,
                        hltb_total=None,
                    )
                )

session.commit()

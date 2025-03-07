import os
import re

import sqlalchemy
from fasthtml.common import (
    A,
    Button,
    Div,
    Form,
    Input,
    Option,
    Select,
    Style,
    Title,
    fast_app,
    picolink,
    serve,
)
from fastsql import Database

app, rt = fast_app(
    hdrs=(
        picolink,
        Style('button[type="submit"], input:not([type="checkbox"], [type="radio"]), select, textarea { width: auto;}'),
    )
)

HOST = os.getenv("HOST", "postgres")
db = Database(f"postgresql+pg8000://postgres:postgres@{HOST}/Keys")

NAME = re.compile(r"(January|February|March|April|May|June|July|August|September|October|November|December) (\d\d\d\d)")


@app.get
def index():
    return Div(
        Title("Keys"),
        Input(
            name="title",
            hx_get="/search",
            placeholder="Title",
            hx_target="#gamelist",
            hx_swap="innerHTML",
        ),
        Div(id="gamelist"),
    )


def get_href(bundle_name: str):
    groups = NAME.search(bundle_name)
    if groups and "choice" in bundle_name.lower():
        href = (f"https://www.humblebundle.com/membership/{groups[1].lower()}-{groups[2]}",)
    elif "humble" in bundle_name.lower():
        href = "https://www.humblebundle.com/home/purchases"
    else:
        href = "https://www.fanatical.com/en/product-library"
    return A(bundle_name, href=href, target="_blank", rel="noopener noreferrer")


def make_game_href(game: str, bundle_href: str):
    return A(
        game,
        href=bundle_href + "/" + game.lower().replace(" ", "").replace("'", ""),
        target="_blank",
        rel="noopener noreferrer",
    )


@app.get
def search(title: str):
    if title:
        _games = db.execute(
            sqlalchemy.text(
                'SELECT id, bundle, game, price FROM "BundledGames" WHERE "game" ILIKE :title LIMIT 10'
            ).bindparams(title=f"%{title}%")
        ).all()
    else:
        _games = db.execute(
            sqlalchemy.text('SELECT id, bundle, game, price FROM "BundledGames" ORDER BY date DESC LIMIT 10')
        )
    return Div(
        *[
            Div(
                Form(
                    Div(make_game_href(game[2], get_href(game[1]).get("href")))
                    if "choice" in game[1].lower()
                    else game[2],
                    Div(get_href(game[1])),
                    Input(hidden=True, id="search", value=title),
                    Input(
                        placeholder="Key",
                        id="key",
                        style="width: 20em",
                    ),
                    Input(
                        placeholder="Price",
                        value=game[3] or 0.5,
                        id="price",
                        style="width: 5em",
                    ),
                    Select(
                        Option("PLN"),
                        Option("EUR"),
                        Option("USD"),
                        id="currency",
                    ),
                    Input(placeholder="Locks", id="locks", style="width: 5em"),
                    Button(
                        "Redeem",
                        id="id",
                        value=str(game[0]),
                        hx_post="/redeem",
                        type="submit",
                    ),
                    hx_post="/redeem",
                    hx_swap="outerHTML",
                ),
                cls="box",
            )
            for game in _games
        ],
        cls="row",
    )


@app.post
def redeem(form: dict):
    print(form)
    if not form.get("key", None):
        return "Key is missing!"
    db.execute(
        sqlalchemy.text(
            'UPDATE "Key" SET used_date = now(), key = :key, locks = :locks WHERE "Key".id = :key_id'
        ).bindparams(
            key=form["key"],
            locks=form["locks"],
            key_id=int(form["id"]),
        )
    )
    if form["price"]:
        db.execute(
            sqlalchemy.text(
                'INSERT INTO "Transaction" (key_id, price, currency) VALUES (:key_id, :price, :currency)'
            ).bindparams(
                key_id=int(form["id"]),
                price=float(form["price"]),
                currency=form["currency"],
            )
        )
    db.conn.commit()
    return "Done"


if __name__ == "__main__":
    serve(reload=False)

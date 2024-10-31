from fasthtml.common import (
    fast_app,
    Div,
    P,
    serve,
    Button,
    Input,
    Form,
    Select,
    Option,
)
from fastsql import Database
import sqlalchemy

app, rt = fast_app()
db = Database("postgresql+pg8000://postgres:postgres@r4/Keys")


@app.get
def index():
    return Div(
        Input(
            name="title",
            hx_get="/search",
            placeholder="Title",
            hx_target="#gamelist",
            hx_swap="innerHTML",
        ),
        Div(id="gamelist"),
    )


@app.get
def search(title: str):
    _games = db.execute(
        sqlalchemy.text(
            'SELECT id, bundle, game FROM "BundledGames" WHERE "game" ILIKE :title LIMIT 10'
        ).bindparams(title=f"%{title}%")
    ).all()
    return Div(
        *[
            Div(
                Form(
                    P(game[2]),
                    P(game[1]),
                    Input(placeholder="Key", id="key"),
                    Input(placeholder="Price", value=0.5, id="price"),
                    Select(
                        Option("PLN"),
                        Option("EUR"),
                        Option("USD"),
                        id="currency",
                    ),
                    Button(
                        "Redeem",
                        id="id",
                        value=str(game[0]),
                        hx_post="/redeem",
                        type="submit",
                    ),
                    hx_post="/redeem",
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
            'UPDATE "Key" SET used_date = now(), key = :key WHERE "Key".id = :key_id'
        ).bindparams(key=form["key"], key_id=int(form["id"]))
    )
    db.execute(
        sqlalchemy.text(
            'INSERT INTO "Transaction" (key_id, price, currency) VALUES (:key_id, :price, :currency)'
        ).bindparams(
            key_id=int(form["id"]),
            price=float(form["price"]),
            currency=form["currency"],
        )
    )
    return "Hello!"


if __name__ == "__main__":
    serve()

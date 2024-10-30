import reflex as rx
import sqlalchemy


class GameList(rx.State):
    game: str
    games: list[str]
    price: float
    currency: str
    key: str
    key_id: str

    def search(self, text: str):
        self.games = []
        self.game = text
        with rx.session() as session:
            _games = session.exec(
                sqlalchemy.text(
                    'SELECT id, bundle, game FROM "BundledGames" WHERE "game" ILIKE :title LIMIT 10'
                ).bindparams(title=f"%{text}%")
            ).all()

        for game in _games:
            self.games.append((game[0], game[1], game[2]))

    def redeem(self, form):
        with rx.session() as session:
            session.exec(
                sqlalchemy.text(
                    'UPDATE "Key" SET used_date = now(), key = :key WHERE "Key".id = :key_id'
                ).bindparams(key=form["key"], key_id=int(form["key_id"]))
            )
            session.exec(
                sqlalchemy.text(
                    'INSERT INTO "Transaction" (key_id, price, currency) VALUES (:key_id, :price, :currency)'
                ).bindparams(
                    key_id=int(form["key_id"]),
                    price=float(form["price"]),
                    currency=form["currency"],
                )
            )
            session.commit()
        self.search(self.game)


def game_list(title: str, bundle: str, key_id: int):
    return rx.form(
        rx.hstack(
            rx.text(title, style={"maxWidth": "20em", "minWidth": "20em"}),
            rx.text(
                bundle,
                style={"maxWidth": "20em", "minWidth": "20em", "align": "center"},
            ),
            rx.input(name="key_id", value=key_id, type="hidden"),
            rx.input(required=True, name="key", on_change=GameList.set_key),
            rx.input(
                value=0.5,
                name="price",
                type="float",
                on_change=GameList.set_price,
                style={"maxWidth": "4em"},
            ),
            rx.select(
                ["PLN", "EUR", "USD"],
                default_value="PLN",
                name="currency",
                style={"maxWidth": "3em"},
            ),
            rx.button("Sold", type="submit"),
        ),
        on_submit=GameList.redeem,
        reset_on_submit=True,
    )


def games():
    return rx.box(rx.foreach(GameList.games, lambda x: game_list(x[2], x[1], x[0])))


def index():
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.input(
                    placeholder="Title",
                    on_change=GameList.search,
                    required=True,
                ),
                align="center",
            ),
            games(),
        )
    )


app = rx.App()
app.add_page(index)

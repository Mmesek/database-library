from mlib.database import SQL, AsyncSQL
from utils.env import HOST


def make_session(
    database: str, driver: str = "postgresql+psycopg", class_: type[SQL | AsyncSQL] = SQL, start_fresh: bool = False
):
    engine = class_(driver, location=HOST, name=database, echo=False)
    if start_fresh:
        engine.drop_tables()
        engine.create_tables()
    return engine.session()

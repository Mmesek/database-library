from mlib.database import SQL, AsyncSQL
from utils.env import HOST


def make_session(database: str, driver: str = "postgresql+psycopg", class_: type[SQL | AsyncSQL] = SQL):
    engine = class_(driver, location=HOST, name=database, echo=False)
    return engine.session()

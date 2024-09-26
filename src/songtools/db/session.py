from environs import Env
from sqlalchemy import create_engine, Engine
from songtools import config

env = Env()


def get_engine() -> Engine:
    # Only supporting postgres for this project
    db_host = config.db.host
    db_port = config.db.port
    db_name = config.db.name
    db_user = config.db.user
    db_password = config.db.password

    db_url = (
        f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    return create_engine(db_url)


def get_in_memory_engine() -> Engine:
    return create_engine("sqlite:///:memory:")

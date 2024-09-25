from environs import Env
from sqlalchemy import create_engine, Engine

env = Env()


def get_engine(is_memory: False) -> Engine:
    if is_memory:
        # For testing purposes
        return create_engine("sqlite:///:memory:")

    # Only supporting postgres for this project
    db_host = env.str("DB_HOST")
    db_port = env.str("DB_PORT")
    db_name = env.str("DB_NAME")
    db_user = env.str("DB_USER")
    db_password = env.str("DB_PASS")

    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    return create_engine(db_url)

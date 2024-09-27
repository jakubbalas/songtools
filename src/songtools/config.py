from dataclasses import dataclass

from environs import Env
from enum import Enum


env = Env()

Environment = Enum("Environment", ["TEST", "DEV", "PROD"])


@dataclass
class DbConfig:
    host: str
    port: str
    name: str
    user: str
    password: str


class Config:
    db = DbConfig(
        host=env.str("DB_HOST"),
        port=env.str("DB_PORT"),
        name=env.str("DB_NAME"),
        user=env.str("DB_USER"),
        password=env.str("DB_PASS"),
    )

    backlog_path: str = env.str("BACKLOG_PATH")


config = Config()
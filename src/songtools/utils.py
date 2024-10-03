import click
from pathlib import Path
from datetime import datetime
from songtools import config as config


FILE_NAME = f"songtools-{int(datetime.now().timestamp())}.log"


COLOR_CFG = {
    "OK": {"fg": "green", "bg": "black"},
    "INFO": {"fg": "white", "bg": "black"},
    "CHECK": {"fg": "yellow", "bg": "black"},
    "ERR": {"fg": "red", "bg": "black"},
}


def echo(msg: str, msg_type: str = "INFO") -> None:
    if msg_type not in COLOR_CFG:
        raise ValueError(f"Unknown message type {msg_type}")

    click.secho(msg, fg=COLOR_CFG[msg_type]["fg"], bg=COLOR_CFG[msg_type]["bg"])

    if config.log_store and msg_type in config.log_store_type:
        with open(Path(config.log_dir) / FILE_NAME, "a+") as f:
            f.writelines([f"[{msg_type}] {msg}"])

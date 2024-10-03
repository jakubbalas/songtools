import click
from pathlib import Path
from songtools.backlog import (
    clean_preimport_folder,
    load_backlog_folder_files,
    load_backlog_folder_metadata,
)
from songtools.db.session import get_engine


@click.group()
def app():
    pass


@app.group()
def backlog():
    pass


@backlog.command()
def load_songs():
    # TODO: implement
    click.echo("Loading songs")


@backlog.command()
@click.argument("folder_path")
def clean_folder(folder_path):
    click.echo("Cleaning songs")
    clean_preimport_folder(Path(folder_path))
    click.echo("Done")


@backlog.command()
@click.argument("folder_path")
def load_backlog_folder_init(folder_path):
    click.echo("Loading songs")
    load_backlog_folder_files(Path(folder_path), get_engine())
    click.echo("Done")


@backlog.command()
@click.option(
    "--path-filter",
    default=None,
    help="String to filter the paths for loading metadata",
)
def load_backlog_folder_meta(path_filter):
    click.echo("Loading metadata")
    load_backlog_folder_metadata(get_engine(), path_filter=path_filter)
    click.echo("Done")


if __name__ == "__main__":
    app()

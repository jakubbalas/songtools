import click
from pathlib import Path
from songtools.backlog import (
    clean_preimport_folder,
    delete_song_folder,
    load_backlog_folder_files,
    load_backlog_folder_metadata, dedup_song_folder,
)
from songtools.db.session import get_engine


@click.group()
def app() -> None:
    pass


@app.group()
def backlog() -> None:
    pass


@backlog.command()
def load_songs() -> None:
    # TODO: implement
    click.echo("Loading songs")


@backlog.command()
@click.argument("folder_path")
@click.option(
    "--path-select",
    default=None,
    help="Select which subfolders to clean",
)
def clean_folder(folder_path: str, path_select: str) -> None:
    click.echo("Cleaning songs")
    base_folder = Path(folder_path)
    if not path_select:
        clean_preimport_folder(base_folder)
    else:
        for p in base_folder.glob(path_select):
            click.echo(p)
            clean_preimport_folder(p)
    click.echo("Done")


@backlog.command()
@click.argument("folder_path")
@click.option(
    "--path-select",
    default=None,
    help="Select which subfolders to load to the db",
)
def load_backlog_folder_init(folder_path: str, path_select: str) -> None:
    click.echo("Loading songs")
    base_folder = Path(folder_path)
    if not path_select:
        load_backlog_folder_files(base_folder, get_engine())
    else:
        for p in base_folder.glob(path_select):
            click.echo(p)
            load_backlog_folder_files(p, get_engine())
    click.echo("Done")


@backlog.command()
@click.option(
    "--path-select",
    default=None,
    help="String to filter the paths for loading metadata",
)
def load_backlog_folder_meta(path_select: str) -> None:
    click.echo("Loading metadata")
    load_backlog_folder_metadata(get_engine(), path_select=path_select)
    click.echo("Done")


@backlog.command()
@click.argument(
    "path",
)
def delete_folder(path: str) -> None:
    click.echo("Deleting folder")
    delete_song_folder(Path(path), get_engine())
    click.echo("Done")

@backlog.command()
@click.argument(
    "path",
)
def dedup_folder(path: str) -> None:
    click.echo("Removing duplicates from folder")
    dedup_song_folder(Path(path), get_engine())
    click.echo("Done")


if __name__ == "__main__":
    app()

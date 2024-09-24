import click
from pathlib import Path
from songtools.backlog import clean_preimport_folder


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


if __name__ == "__main__":
    app()

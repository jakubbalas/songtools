import click


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
def clean_folder():
    # TODO: implement
    click.echo("Cleaning songs")


if __name__ == "__main__":
    app()

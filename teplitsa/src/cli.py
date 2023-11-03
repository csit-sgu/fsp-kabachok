import click


@click.group()
def cli():
    pass


@cli.group()
def pin():
    pass


@pin.command()
def storage():
    click.echo("Starting breaking storage teplitsa")


@pin.command()
def cpu():
    click.echo("Starting breaking CPU teplitsa")


@pin.command()
def conn():
    click.echo("Starting breaking connection teplitsa")


@pin.command()
def ram():
    click.echo("Starting breaking RAM teplitsa")


@pin.command()
def timeout():
    click.echo("Starting breaking timeout teplitsa")

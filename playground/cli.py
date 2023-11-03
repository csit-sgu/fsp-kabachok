import asyncio

import click

from playground import cpu_intensive, long_sleep, many_inserts


@click.group()
def cli():
    pass


@cli.group()
def pin():
    pass


@pin.command()
def storage():
    click.echo("Starting breaking storage playground")
    asyncio.get_event_loop().run_until_complete(
        many_inserts(url="localhost", port=4003)
    )


@pin.command()
def cpu():
    click.echo("Starting breaking CPU playground")
    asyncio.get_event_loop().run_until_complete(
        cpu_intensive(url="localhost", port=4000)
    )


@pin.command()
def conn():
    click.echo("Starting breaking connection playground")
    asyncio.get_event_loop().run_until_complete(
        long_sleep(url="localhost", port=4002)
    )


@pin.command()
def ram():
    click.echo("Starting breaking RAM playground")


@pin.command()
def timeout():
    click.echo("Starting breaking timeout playground")

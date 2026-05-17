import click


@click.group()
def cli():
    """NanoRec - Declarative ML recommendation framework."""
    pass


# Import and add commands
from cli.generate import generate
from cli.deploy import deploy

cli.add_command(generate)
cli.add_command(deploy)

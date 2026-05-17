"""Project initialization command (stub)."""

import click
from nanorec.cli.main import cli


@cli.command()
@click.argument("project_name")
def init(project_name: str):
    """Create a new NanoRec project (to be implemented)."""
    click.echo(f"init stub: {project_name}")

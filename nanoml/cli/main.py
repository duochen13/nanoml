"""NanoML CLI main entry point."""

import click
from nanoml.__version__ import __version__


@click.group()
@click.version_option(version=__version__, prog_name="nanoml")
def cli():
    """
    NanoML - Production ML Recommendation Systems Made Easy

    Build, deploy, and scale ML recommendation systems with a single command.
    """
    pass


# Commands will be added in subsequent tasks
from nanoml.cli import init as _init_module  # noqa: E402, F401
from nanoml.cli import validate as _validate_module  # noqa: E402, F401
from nanoml.cli import generate as _generate_module  # noqa: E402, F401

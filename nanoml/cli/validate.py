"""Configuration validation command."""

from pathlib import Path

import click

from nanoml.cli.main import cli
from nanoml.core import ConfigLoader, ConfigValidationError


@cli.command()
@click.option(
    "--config",
    "-c",
    default="config.yaml",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file",
    show_default=True
)
def validate(config: Path):
    """
    Validate NanoML configuration file.

    Checks config.yaml against the schema and reports any errors.
    """
    click.echo(f"Validating configuration: {config}")

    try:
        loader = ConfigLoader()
        config_dict = loader.load(config)

        # Show summary
        click.secho("✅ Configuration is valid", fg="green")
        click.echo("")
        click.echo("Summary:")
        click.echo(f"  Environment: {config_dict['environment']}")
        click.echo(f"  Project: {config_dict['project']['name']}")
        click.echo(f"  Version: {config_dict['project']['version']}")

        # Show ML config if present
        if "ml" in config_dict:
            ml_config = config_dict["ml"]
            if "features" in ml_config:
                features = ml_config["features"].get("required_features", [])
                click.echo(f"  Required features: {len(features)}")

    except FileNotFoundError as e:
        click.secho(f"❌ Config file not found: {config}", fg="red", err=True)
        raise click.Abort()

    except ConfigValidationError as e:
        click.secho(f"❌ Configuration validation failed:", fg="red", err=True)
        click.echo(str(e), err=True)
        raise click.Abort()

    except Exception as e:
        click.secho(f"❌ Unexpected error: {e}", fg="red", err=True)
        raise click.Abort()

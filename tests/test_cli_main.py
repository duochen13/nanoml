from click.testing import CliRunner
from nanoml.cli.main import cli


def test_cli_help():
    """CLI should show help message."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "NanoML" in result.output
    assert "init" in result.output
    assert "validate" in result.output


def test_cli_version():
    """CLI should show version."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output

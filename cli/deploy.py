import click
import subprocess
from pathlib import Path
from core.config import load_config
from providers.aws.config import AWSConfig


@click.command()
@click.option(
    "--provider",
    type=click.Choice(["local", "aws"]),
    help="Infrastructure provider"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Synthesize but don't deploy"
)
def deploy(provider: str, dry_run: bool):
    """Deploy NanoRec infrastructure.

    Deploys to local (Docker Compose) or AWS (CDK).
    """
    # Load config
    config_path = Path.cwd() / "nanorec.yaml"

    if not config_path.exists():
        click.echo("❌ No nanorec.yaml found", err=True)
        raise click.Abort()

    config = load_config(config_path)

    # Determine provider
    if provider is None:
        provider = config.infrastructure.get("provider", "local")

    if provider not in ["local", "aws"]:
        click.echo(f"❌ Invalid provider: {provider}", err=True)
        click.echo("Must be one of: local, aws", err=True)
        raise click.Abort()

    click.echo(f"Deploying to {provider}...")

    if provider == "local":
        deploy_local()
    elif provider == "aws":
        deploy_aws(config_path, dry_run)

    click.echo("✅ Deployment complete!")


def deploy_local():
    """Deploy to local infrastructure (Docker Compose)."""
    click.echo("Starting local infrastructure...")

    # Run docker-compose up
    result = subprocess.run(
        ["docker-compose", "up", "-d"],
        cwd="deployment",
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        click.echo(f"❌ Docker Compose failed: {result.stderr}", err=True)
        raise click.Abort()

    click.echo("✓ Local services started")


def deploy_aws(config_path: Path, dry_run: bool):
    """Deploy to AWS (CDK)."""
    click.echo("Loading AWS configuration...")

    aws_config = AWSConfig.from_file(config_path)

    click.echo(f"  Region: {aws_config.region}")
    click.echo(f"  Account: {aws_config.account_id or 'default'}")

    # Synthesize CDK
    click.echo("Synthesizing CDK stacks...")

    cdk_dir = Path(__file__).parent.parent / "providers" / "aws" / "infrastructure"

    synth_result = subprocess.run(
        ["cdk", "synth"],
        cwd=cdk_dir,
        capture_output=True,
        text=True
    )

    if synth_result.returncode != 0:
        click.echo(f"❌ CDK synth failed: {synth_result.stderr}", err=True)
        raise click.Abort()

    click.echo("✓ CDK synthesized")

    if dry_run:
        click.echo("Dry run - skipping deployment")
        return

    # Deploy CDK
    click.echo("Deploying CDK stacks...")

    deploy_result = subprocess.run(
        ["cdk", "deploy", "--all", "--require-approval", "never"],
        cwd=cdk_dir,
        capture_output=True,
        text=True
    )

    if deploy_result.returncode != 0:
        click.echo(f"❌ CDK deploy failed: {deploy_result.stderr}", err=True)
        raise click.Abort()

    click.echo("✓ CDK deployed")

"""Project initialization command."""

import re
import shutil
from pathlib import Path
from typing import Optional

import click
from jinja2 import Environment, FileSystemLoader

from nanorec.cli.main import cli


@cli.command()
@click.argument("project_name")
@click.option(
    "--template",
    default="default",
    help="Project template to use",
    show_default=True
)
@click.option(
    "--description",
    default="A NanoRec recommendation system",
    help="Project description",
    show_default=True
)
def init(project_name: str, template: str, description: str):
    """
    Create a new NanoRec project.

    PROJECT_NAME must be lowercase with hyphens (e.g., my-recommender)
    """
    # Validate project name
    if not re.match(r"^[a-z][a-z0-9-]*$", project_name):
        click.secho(
            f"❌ Invalid project name: {project_name}\n"
            "Project name must be lowercase, start with a letter, "
            "and contain only letters, numbers, and hyphens.",
            fg="red",
            err=True
        )
        raise click.Abort()

    # Check if directory already exists
    project_dir = Path(project_name)
    if project_dir.exists():
        click.secho(
            f"❌ Directory already exists: {project_name}",
            fg="red",
            err=True
        )
        raise click.Abort()

    # Get template directory
    templates_dir = Path(__file__).parent.parent / "templates"
    template_dir = templates_dir / template

    if not template_dir.exists():
        click.secho(
            f"❌ Template not found: {template}",
            fg="red",
            err=True
        )
        raise click.Abort()

    # Create project
    click.echo(f"Creating NanoRec project: {project_name}")

    try:
        _scaffold_project(
            project_dir=project_dir,
            template_dir=template_dir,
            project_name=project_name,
            description=description,
        )

        click.secho("✅ Project created!", fg="green")
        click.echo("")
        click.echo("Next steps:")
        click.echo(f"  cd {project_name}")
        click.echo("  make setup    # Install dependencies")
        click.echo("  make run      # Start local infrastructure")

    except Exception as e:
        # Cleanup on failure
        if project_dir.exists():
            shutil.rmtree(project_dir)
        click.secho(f"❌ Failed to create project: {e}", fg="red", err=True)
        raise click.Abort()


def _scaffold_project(
    project_dir: Path,
    template_dir: Path,
    project_name: str,
    description: str,
) -> None:
    """
    Scaffold project from template.

    Args:
        project_dir: Target project directory
        template_dir: Source template directory
        project_name: Project name
        description: Project description
    """
    project_dir.mkdir(parents=True)

    # Setup Jinja2 environment
    project_template_dir = template_dir / "project"
    env = Environment(
        loader=FileSystemLoader(str(project_template_dir)),
        keep_trailing_newline=True,
    )

    # Template variables
    context = {
        "project_name": project_name,
        "project_version": "0.1.0",
        "description": description,
    }

    # Copy all template files
    for template_path in project_template_dir.rglob("*"):
        if template_path.is_file():
            # Get relative path from template root
            rel_path = template_path.relative_to(project_template_dir)

            # Determine target path (remove .jinja2 extension if present)
            target_path = project_dir / rel_path
            if target_path.suffix == ".jinja2":
                target_path = target_path.with_suffix("")

            # Create parent directories
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Render template if it's a .jinja2 file
            if template_path.suffix == ".jinja2":
                template = env.get_template(str(rel_path))
                content = template.render(**context)
                target_path.write_text(content)
            else:
                # Copy non-template files directly
                shutil.copy2(template_path, target_path)

    # Create empty directories that need to exist
    (project_dir / ".nanorec").mkdir(exist_ok=True)
    (project_dir / ".nanorec" / "generated").mkdir(exist_ok=True)
    (project_dir / ".nanorec" / "cache").mkdir(exist_ok=True)

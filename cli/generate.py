import click
from pathlib import Path
from core.config import load_config
from core.generated_manager import GeneratedManager
from generators.flink_job import FlinkJobGenerator
from generators.feast_config import FeastConfigGenerator
from generators.airflow_dag import AirflowDAGGenerator


@click.command()
@click.option(
    "--clean",
    is_flag=True,
    help="Clean generated directory before generating"
)
def generate(clean: bool):
    """Generate Flink jobs, Feast configs, and Airflow DAGs from definitions.

    Reads:
    - features/definitions.py -> Flink jobs + Feast configs
    - components/*.py -> Airflow DAGs

    Writes to:
    - .nanoml/generated/flink/
    - .nanoml/generated/feast/
    - .nanoml/generated/airflow/
    """
    # Find project root
    project_root = Path.cwd()
    config_path = project_root / "nanoml.yaml"

    if not config_path.exists():
        click.echo("No nanoml.yaml found in current directory", err=True)
        click.echo("Run this command from a NanoML project root", err=True)
        raise click.Abort()

    # Load config
    config = load_config(config_path)
    click.echo(f"Generating code for project: {config.name}")

    # Initialize generated directory
    manager = GeneratedManager(project_root)

    if clean:
        click.echo("Cleaning generated directory...")
        manager.clean()
    else:
        manager.init()

    # Generate Flink jobs
    features_file = project_root / "features" / "definitions.py"
    if features_file.exists():
        click.echo("Generating Flink streaming job...")
        flink_gen = FlinkJobGenerator()
        flink_output = flink_gen.run(features_file, project_root)
        click.echo(f"  Generated {flink_output.relative_to(project_root)}")

        # Generate Feast configs
        click.echo("Generating Feast configuration...")

        feast_store_gen = FeastConfigGenerator(output_type="store")
        store_output = feast_store_gen.run(features_file, project_root)
        click.echo(f"  Generated {store_output.relative_to(project_root)}")

        feast_features_gen = FeastConfigGenerator(output_type="features")
        features_output = feast_features_gen.run(features_file, project_root)
        click.echo(f"  Generated {features_output.relative_to(project_root)}")
    else:
        click.echo("No features/definitions.py found, skipping Flink/Feast generation")

    # Generate Airflow DAGs (look for pipeline.py or similar)
    components_files = list((project_root / "components").glob("*.py"))
    if components_files:
        click.echo("Generating Airflow DAG...")
        for comp_file in components_files:
            if comp_file.name == "__init__.py":
                continue

            airflow_gen = AirflowDAGGenerator()
            dag_output = airflow_gen.run(comp_file, project_root)
            click.echo(f"  Generated {dag_output.relative_to(project_root)}")
    else:
        click.echo("No component files found, skipping Airflow generation")

    click.echo("\nCode generation complete!")
    click.echo(f"Generated code location: {manager.generated_root.relative_to(project_root)}")

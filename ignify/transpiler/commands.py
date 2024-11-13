"""Transpiler commands."""

import asyncio

import click

from .. import config
from . import transpiler as ts


def transpile(config: config.ResolvedConfig):
    """Transpile Python modules to Ignition modules."""
    python_modules = ts.get_python_modules(config)
    ignition_modules = ts.get_ignition_modules(config)

    missing_in_ignition, missing_in_python = ts.compare_modules(
        python_modules, ignition_modules
    )

    if not missing_in_ignition and not missing_in_python:
        click.echo(click.style("No modules to transpile", fg="green"))
        return

    click.echo(click.style("Transpiling modules", fg="green"))

    asyncio.run(ts.write_ignition_modules(missing_in_ignition))
    click.echo(click.style("Transpiled modules", fg="green"))


@click.command(
    name="txp", short_help="Transpile Python modules to Ignition modules."
)
def transpiler():
    """Transpile Python modules to Ignition modules."""
    conf = config.get_config()
    transpile(conf)


@click.command()
def compare():
    """Compare Python and Ignition modules."""
    conf = config.get_config()

    python_modules = ts.get_python_modules(conf)
    ignition_modules = ts.get_ignition_modules(conf)

    missing_in_ignition, missing_in_python = ts.compare_modules(
        python_modules, ignition_modules
    )

    click.echo(
        click.style("Comparing Python and Ignition modules", fg="green")
    )
    click.echo(
        click.style(
            f"Python project: {conf.python_project_path_abs}", fg="blue"
        )
    )
    click.echo(
        click.style(
            f"Ignition project: {conf.ignition_project_path_abs}", fg="blue"
        )
    )

    if not missing_in_ignition and not missing_in_python:
        click.echo(click.style("All modules match", fg="green"))
        return

    click.echo(click.style("Missing in Ignition", fg="red"))
    click.echo("\n".join([str(i.rel_path) for i in missing_in_ignition]))

    click.echo(click.style("Missing in Python", fg="red"))
    click.echo("\n".join([str(i.rel_path) for i in missing_in_python]))


@click.command()
@click.option(
    "--abs-path",
    is_flag=True,
    help="Get absolute paths instead of relative ones.",
    default=False,
)
def list_python_modules(abs_path: bool):
    """List python modules in the project."""

    conf = config.get_config()

    click.echo(click.style("Listing Python project files", fg="green"))
    click.echo(
        click.style(f"Location: {conf.python_project_path_abs}", fg="blue")
    )

    files = ts.get_python_modules(conf.python_project_path_abs, conf)

    click.echo(
        "\n".join(
            [
                str(i.rel_path if not abs_path else i.python_abs_path)
                for i in files
            ]
        )
    )


@click.command()
@click.option(
    "--abs-path",
    is_flag=True,
    help="Get absolute paths instead of relative ones.",
    default=False,
)
def list_ignition_modules(abs_path: bool):
    """List Ignition modules."""

    conf = config.get_config()

    click.echo(click.style("Listing Ignition project files", fg="green"))
    click.echo(
        click.style(f"Location: {conf.ignition_project_path_abs}", fg="blue")
    )
    click.echo(
        "\n".join(
            [
                str(i.rel_path if not abs_path else i.ignition_abs_path)
                for i in ts.get_ignition_modules(conf)
            ]
        )
    )

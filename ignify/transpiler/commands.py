"""Transpiler commands."""

import asyncio

import click

from .. import config
from . import transpiler as ts


@click.command(
    name="txp", short_help="Transpile Python modules to Ignition modules."
)
@click.option(
    "--no-rm",
    is_flag=True,
    help="Prevent any deletion of Ignition modules.",
    default=False,
)
def transpiler(no_rm: bool):
    """Transpile Python modules to Ignition modules."""
    conf = config.get_config()

    python_modules = ts.get_python_modules(conf)
    ignition_modules = ts.get_ignition_modules(conf)

    missing_in_ignition, missing_in_python, matching_modules = (
        ts.compare_modules(python_modules, ignition_modules)
    )

    different_content = asyncio.run(ts.deep_compare_modules(matching_modules))
    modules_to_copy = missing_in_ignition | set(different_content)

    if not missing_in_ignition and not missing_in_python:
        click.echo(click.style("No modules to transpile", fg="green"))
        return

    click.echo(click.style("Transpiling modules", fg="blue"))

    asyncio.run(ts.write_ignition_modules(modules_to_copy))
    click.echo(click.style(f"Transpiled {len(modules_to_copy)}", fg="green"))


@click.command()
def compare():
    """Compare Python and Ignition modules."""
    conf = config.get_config()

    python_modules = ts.get_python_modules(conf)
    ignition_modules = ts.get_ignition_modules(conf)

    missing_in_ignition, missing_in_python, matching_modules = (
        ts.compare_modules(python_modules, ignition_modules)
    )

    different_content = asyncio.run(ts.deep_compare_modules(matching_modules))

    click.echo(
        click.style(
            "Comparing Python and Ignition modules", fg="blue", bold=True
        )
    )

    if not missing_in_ignition and not missing_in_python:
        click.echo(click.style("All modules match", fg="green"))
        return

    click.echo(click.style("Missing in Ignition:", fg="red"))
    click.echo(
        "- " + "\n- ".join([str(i.rel_path) for i in missing_in_ignition])
    )

    click.echo(click.style("Missing in Python:", fg="red"))
    click.echo(
        "- " + "\n- ".join([str(i.rel_path) for i in missing_in_python])
    )

    click.echo(click.style("Matching but different content:", fg="red"))
    click.echo(
        "- " + "\n- ".join([str(i.rel_path) for i in different_content])
    )


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

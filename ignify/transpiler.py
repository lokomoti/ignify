"""Transpiler module."""

from dataclasses import dataclass
from pathlib import Path

import click

from . import config

IGNITION_SCRIPTS_DIR = Path("ignition/script-python")
RESOURCE_FILE = "resource.json"


@dataclass
class Module:
    """Module."""

    abs_path: Path
    rel_path: Path

    @property
    def name(self) -> str:
        """Get module name."""
        return self.rel_path.name

    def __hash__(self) -> int:
        """Hash."""
        return str(self.rel_path).__hash__()
    
    def __eq__(self, other) -> bool:
        """Equality."""
        if isinstance(other, Module):
            return self.rel_path == other.rel_path
        return False


def get_python_modules(directory: Path) -> list[Module]:
    """Get Python modules."""
    return [
        Module(file.absolute(), file.relative_to(directory))
        for file in directory.rglob("*.py")
    ]


def _get_ignition_resource_files(directory: Path) -> list[Path]:
    """Get Ignition resource files."""
    return [file for file in directory.rglob(RESOURCE_FILE)]


def _create_ignition_module(resource_file: Path, base_path: Path) -> Module:
    """Create Ignition module."""
    return Module(
        resource_file.parent / "code.py",
        Path(str(resource_file.parent.relative_to(base_path)) + ".py"),
    )


def get_ignition_modules(directory: Path) -> list[Module]:
    """Get Ignition modules."""
    directory = directory / IGNITION_SCRIPTS_DIR
    resource_files = _get_ignition_resource_files(directory)
    return [
        _create_ignition_module(file, directory) for file in resource_files
    ]


def compare_modules(
    python_modules: list[Module], ignition_modules: list[Module]
) -> tuple[set[Module], set[Module]]:
    """Compare Python and Ignition modules."""
    
    python_modules = {module for module in python_modules}
    ignition_modules = {module for module in ignition_modules}

    missing_in_ignition = python_modules - ignition_modules
    missing_in_python = ignition_modules - python_modules

    return missing_in_ignition, missing_in_python


@click.command()
def compare():
    """Compare Python and Ignition modules."""
    conf = config.get_config()

    python_modules = get_python_modules(conf.python_project_path_abs)
    ignition_modules = get_ignition_modules(conf.ignition_project_path_abs)

    missing_in_ignition, missing_in_python = compare_modules(
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

    click.echo(click.style("Missing in Ignition", fg="red"))
    click.echo("\n".join([str(i.rel_path) for i in missing_in_ignition]))

    click.echo(click.style("Missing in Python", fg="red"))
    click.echo("\n".join([str(i.rel_path) for i in missing_in_python]))


@click.command()
def list_python_modules():
    """List python modules in the project."""

    conf = config.get_config()

    click.echo(click.style("Listing Python project files", fg="green"))
    click.echo(
        click.style(f"Location: {conf.python_project_path_abs}", fg="blue")
    )

    files = get_python_modules(conf.python_project_path_abs)

    click.echo("\n".join([str(i.rel_path) for i in files]))


@click.command()
def list_ignition_modules():
    """List Ignition modules."""

    conf = config.get_config()

    click.echo(click.style("Listing Ignition project files", fg="green"))
    click.echo(
        click.style(f"Location: {conf.ignition_project_path_abs}", fg="blue")
    )
    click.echo(
        "\n".join(
            [
                str(i.rel_path)
                for i in get_ignition_modules(conf.ignition_project_path_abs)
            ]
        )
    )

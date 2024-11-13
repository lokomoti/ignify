import click
from .transpiler import commands

from . import config


@click.group()
def cli():
    """Ignify CLI."""
    pass


cli.add_command(config.write_default_config)
cli.add_command(config.check_config)
cli.add_command(commands.list_python_modules)
cli.add_command(commands.list_ignition_modules)
cli.add_command(commands.compare)
cli.add_command(commands.transpiler)

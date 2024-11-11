import click

from . import config, transpiler


@click.group()
def cli():
    """Ignify CLI."""
    pass


cli.add_command(config.write_default_config)
cli.add_command(config.check_config)
cli.add_command(transpiler.list_python_modules)
cli.add_command(transpiler.list_ignition_modules)
cli.add_command(transpiler.compare)

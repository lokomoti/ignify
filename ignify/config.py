"""Config module."""

from pathlib import Path

import click
import yaml
from pydantic import BaseModel, ValidationError

from .exceptions import ConfigNotFoundError, InvalidConfigError

CONFIG_FILE_NAME = "ignify.yaml"
DEFAULT_IGNITION_INSTALL_DIR = Path(
    "C:/Program Files/Inductive Automation/Ignition"
)
IGNITION_PROJECTS_DIR = Path("data/projects")


class Transpiler(BaseModel):
    """Transpiler configuration."""

    ignition_install_dir: str = (
        DEFAULT_IGNITION_INSTALL_DIR  # Path to the Ignition install directory
    )
    ignition_project: (
        str  # Path to the Ignition project or name of the project
    )
    python_project: Path  # Path to the Python project or root of the project


class Config(BaseModel):
    """Configuration."""

    transpiler: Transpiler
    # Add more configurations here later


class ResolvedConfig(Config):
    """Resolved configuration."""

    ignition_project_path_abs: Path
    python_project_path_abs: Path


def _read_config(path: Path):
    """Read YAML config from specific path."""

    try:
        return yaml.safe_load(path.read_text())

    except FileNotFoundError as error:
        message = "Error: yml config file not found."
        raise FileNotFoundError(error, message) from error


def _find_file(file) -> Path:
    """Find file in current location or in parent folders location."""

    # Check if config file exists in the same location
    config_file = Path(file)
    if config_file.exists():
        return config_file

    # Check if config file exists in parent directories
    current_dir = Path.cwd()
    for parent in current_dir.parents:
        config_file = parent / file
        if config_file.exists():
            return config_file

    raise FileNotFoundError("Config file not found.")


def _load_config(path: Path) -> Config:
    """Load config file."""

    try:
        return Config(**_read_config(path))
    except ValidationError as error:
        raise InvalidConfigError(validation_error=error) from error


def _resolve_config(config: Config) -> ResolvedConfig:
    """Validate configuration."""

    # Validate presence of Ignition project
    ign_path = (
        Path(config.transpiler.ignition_install_dir)
        / IGNITION_PROJECTS_DIR
        / Path(config.transpiler.ignition_project)
    )
    if not ign_path.exists():
        raise InvalidConfigError(f"Ignition project not found: {ign_path}")

    # Validate presence of Python project
    try:
        py_path = _find_file(Path(config.transpiler.python_project))
    except FileNotFoundError as error:
        raise InvalidConfigError("Python project not found") from error

    return ResolvedConfig(
        transpiler=config.transpiler,
        ignition_project_path_abs=ign_path,
        python_project_path_abs=py_path,
    )


def get_config() -> ResolvedConfig:
    """Get configuration."""
    try:
        config_file = _find_file(CONFIG_FILE_NAME)
        config = _load_config(config_file)
        return _resolve_config(config)
    except FileNotFoundError as error:
        raise ConfigNotFoundError(error) from error


@click.command()
def check_config() -> None:
    """Check config file."""

    try:
        get_config()
        click.echo("Config file is valid.")
    except InvalidConfigError as error:
        click.echo(f"Invalid config file: {error}")
    except ConfigNotFoundError:
        click.echo(
            "Please create a config file using 'ignify config write-default-config'."
        )


@click.command()
def write_default_config(path: Path = Path.cwd()) -> None:
    """Write default config to file."""

    config = Config(
        transpiler=Transpiler(
            ignition_project="path/to/ignition/project",
            python_project="path/to/python/project",
        )
    )
    with open(path, "w") as file:
        yaml.dump(config.model_dump(), file)

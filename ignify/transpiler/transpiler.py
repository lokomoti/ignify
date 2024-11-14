"""Transpiler module."""

import asyncio
import filecmp
from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path
from typing import Iterable, Optional

from .. import config

IGNITION_SCRIPTS_DIR = Path("ignition/script-python")
RESOURCE_FILE = "resource.json"


class ModuleType(StrEnum):
    """Module type."""

    PYTHON = auto()
    IGNITION = auto()


@dataclass
class Module:
    """Module."""

    rel_path: Path
    config: config.ResolvedConfig

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

    def _abs_path(self, type: ModuleType) -> Path:
        """Get absolute path."""
        if type == ModuleType.PYTHON:
            return self.config.python_project_path_abs / self.rel_path
        return (
            self.config.ignition_project_path_abs
            / IGNITION_SCRIPTS_DIR
            / self.rel_path.with_suffix("")
            / "code.py"
        )

    @property
    def ignition_abs_path(self) -> Path:
        """Get Ignition absolute path."""
        return self._abs_path(ModuleType.IGNITION)

    @property
    def python_abs_path(self) -> Path:
        """Get Python absolute path."""
        return self._abs_path(ModuleType.PYTHON)


def get_python_modules(config: config.ResolvedConfig) -> list[Module]:
    """Get Python modules."""
    directory = config.python_project_path_abs
    return [
        Module(file.relative_to(directory), config)
        for file in directory.rglob("*.py")
    ]


def _get_ignition_resource_files(directory: Path) -> list[Path]:
    """Get Ignition resource files."""
    return [file for file in directory.rglob(RESOURCE_FILE)]


def _create_ignition_module(
    resource_file: Path, config: config.ResolvedConfig
) -> Module:
    """Create Ignition module."""
    base_path = config.ignition_project_path_abs / IGNITION_SCRIPTS_DIR
    return Module(
        Path(str(resource_file.parent.relative_to(base_path)) + ".py"), config
    )


def get_ignition_modules(config: config.ResolvedConfig) -> list[Module]:
    """Get Ignition modules."""
    resource_files = _get_ignition_resource_files(
        config.ignition_project_path_abs / IGNITION_SCRIPTS_DIR
    )
    return [_create_ignition_module(file, config) for file in resource_files]


def _write_ignition_module(module: Module):
    """Write Ignition module."""
    # Ensure the directory exists
    module.ignition_abs_path.parent.mkdir(parents=True, exist_ok=True)
    code = module.python_abs_path.read_text(encoding="utf-8")
    module.ignition_abs_path.write_text(code, encoding="utf-8")
    module.ignition_abs_path.parent.joinpath(RESOURCE_FILE).write_text(
        "", encoding="utf-8"
    )


async def write_ignition_module(module: Module):
    """Write Ignition module."""
    await asyncio.to_thread(_write_ignition_module, module)


async def write_ignition_modules(modules: Iterable[Module]):
    """Write Ignition modules."""
    await asyncio.gather(
        *[write_ignition_module(module) for module in modules]
    )


def compare_modules(
    python_modules: list[Module], ignition_modules: list[Module]
) -> tuple[set[Module], set[Module], set[Module]]:
    """Compare Python and Ignition modules."""
    python_modules = set(python_modules)
    ignition_modules = set(ignition_modules)

    missing_in_ignition = python_modules - ignition_modules
    missing_in_python = ignition_modules - python_modules
    matching_modules = python_modules & ignition_modules

    return missing_in_ignition, missing_in_python, matching_modules


async def _deep_compare_module(module: Module) -> Optional[Module]:
    """Deep compare module.

    Returns the module if the content does not match, otherwise None.
    """
    is_same = await asyncio.to_thread(
        filecmp.cmp,
        module.python_abs_path,
        module.ignition_abs_path,
        shallow=False,
    )
    return None if is_same else module


async def deep_compare_modules(modules: list[Module]) -> list[Module]:
    """Deep compare modules.

    Args:
        modules (list[Module]): Modules to compare.

    Returns:
        list[Module]: Modules that have different content.
    """
    tasks = [_deep_compare_module(module) for module in modules]
    results = await asyncio.gather(*tasks)
    different_modules = [module for module in results if module is not None]

    return different_modules

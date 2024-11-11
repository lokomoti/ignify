"""Exceptions for Ignify."""

from pydantic import ValidationError


class ConfigError(Exception):
    """Raised when there is an error with the configuration."""

    pass


class ConfigNotFoundError(ConfigError):
    """Raised when config was not found."""

    pass


class InvalidConfigError(ConfigError):
    """Raised when config is invalid."""

    def __init__(
        self, message: str, validation_error: ValidationError = None
    ) -> None:
        self.validation_error = validation_error
        super().__init__(
            message if validation_error is None else self._parse_errors()
        )

    def _parse_errors(self) -> str:
        """Parse errors from the validation error."""
        return "\n" + "\n".join(
            [
                f"{error["msg"]} - {".".join(error["loc"])}"
                for error in self.validation_error.errors()
            ]
        )

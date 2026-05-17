class DataLoaderNodeError(ValueError):
    """Base class for data-loader node failures."""


class DataLoaderNotFoundError(DataLoaderNodeError):
    """Raised when ``loader_name`` is not registered."""

    def __init__(self, loader_name: str) -> None:
        super().__init__(f"Data loader '{loader_name}' is not registered.")


class DataLoaderConfigError(DataLoaderNodeError):
    """Raised when a loader-specific config block fails validation."""

    def __init__(self, loader_name: str, reason: str) -> None:
        super().__init__(f"Invalid config for data loader '{loader_name}': {reason}")


class DataLoaderExecutionError(DataLoaderNodeError):
    """Raised when a registered loader fails while reading data."""

    def __init__(self, loader_name: str, reason: str) -> None:
        super().__init__(f"Data loader '{loader_name}' failed: {reason}")


class DataLoaderRegistrationError(DataLoaderNodeError):
    """Raised when two loaders register under the same name."""

    def __init__(self, loader_name: str, existing: type, incoming: type) -> None:
        super().__init__(
            f"Data loader '{loader_name}' already registered by "
            f"{existing.__module__}.{existing.__qualname__}; refusing to "
            f"replace with {incoming.__module__}.{incoming.__qualname__}."
        )

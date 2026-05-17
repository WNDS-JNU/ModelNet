"""Registry and base interfaces for extensible data loaders.

Concrete dataset integrations should subclass :class:`DataLoader`, declare a
Pydantic ``config_model``, and register the class with ``@register_loader``.
The generic workflow node handles validation, pagination metadata, and event
translation around that small loader surface.

Fork recipe (add a new dataset without touching ``node.py`` or the frontend):

1. Create ``loaders/<your_loader>.py``.
2. Define a Pydantic ``Config(BaseModel)`` with ``ConfigDict(extra="forbid")``;
   any user-facing knob lives here so the node can validate it before
   ``load()`` is ever called.
3. Subclass ``DataLoader[Config]`` with ``name``, ``description``, and
   ``config_model`` class vars, then implement ``load(config, options)``;
   delegate paging/shuffling to :func:`page_items` and return a
   :class:`DataLoaderResult` with ``DataLoaderItem`` rows.
4. Decorate the class with ``@register_loader("<your_loader>")`` and add
   ``from .<your_loader> import <YourLoader>`` to ``loaders/__init__.py`` so
   importing the package triggers the registration side effect.

Names are unique across the registry — duplicate ``@register_loader`` calls
raise :class:`DataLoaderRegistrationError` to catch silent fork conflicts.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, NotRequired, TypedDict

from pydantic import BaseModel, ConfigDict

from .exc import DataLoaderNotFoundError, DataLoaderRegistrationError


class EmptyLoaderConfig(BaseModel):
    """Default config model for loaders with no custom configuration."""

    model_config = ConfigDict(extra="forbid")


class DataLoaderItem(TypedDict):
    """Normalized row shape emitted by all data loaders."""

    id: str
    data: dict[str, Any]
    question: NotRequired[str]
    answer: NotRequired[str]
    metadata: NotRequired[dict[str, Any]]


@dataclass(frozen=True, slots=True)
class DataLoaderRunOptions:
    """Common paging and sampling options applied consistently by loaders."""

    limit: int
    offset: int
    shuffle: bool
    seed: int | None


@dataclass(frozen=True, slots=True)
class DataLoaderResult:
    """Result returned by a concrete loader before node output assembly."""

    dataset: str
    split: str
    items: list[DataLoaderItem]
    total: int
    metadata: dict[str, Any]


class DataLoader[ConfigT: BaseModel](ABC):
    """Base class for dataset-specific loaders.

    Loader classes are intentionally small: parse ``loader_config`` with
    ``config_model``, read/normalize the source data, and return
    :class:`DataLoaderResult`. The workflow node owns all graphon-specific event
    handling, so loaders remain easy to fork and unit test.
    """

    name: ClassVar[str]
    config_model: ClassVar[type[ConfigT]]
    description: ClassVar[str] = ""

    def parse_config(self, raw_config: dict[str, Any]) -> ConfigT:
        return self.config_model.model_validate(raw_config)

    @abstractmethod
    def load(self, config: ConfigT, options: DataLoaderRunOptions) -> DataLoaderResult:
        """Load and normalize dataset rows."""


_LOADERS: dict[str, type[DataLoader[Any]]] = {}


def register_loader(name: str) -> Callable[[type[DataLoader[Any]]], type[DataLoader[Any]]]:
    """Register a loader implementation under a stable DSL name."""

    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("loader name must not be blank")

    def decorator(cls: type[DataLoader[Any]]) -> type[DataLoader[Any]]:
        existing = _LOADERS.get(normalized_name)
        if existing is not None and existing is not cls:
            raise DataLoaderRegistrationError(normalized_name, existing, cls)
        _LOADERS[normalized_name] = cls
        return cls

    return decorator


def get_loader(name: str) -> DataLoader[Any]:
    """Return a new loader instance for ``name``."""

    normalized_name = name.strip()
    try:
        loader_cls = _LOADERS[normalized_name]
    except KeyError as exc:
        raise DataLoaderNotFoundError(normalized_name) from exc
    return loader_cls()


def list_loaders() -> list[dict[str, str]]:
    """List registered loaders for tests and future frontend discovery."""

    return [
        {
            "name": name,
            "description": loader_cls.description,
        }
        for name, loader_cls in sorted(_LOADERS.items())
    ]


def page_items[ItemT](
    items: Sequence[ItemT],
    *,
    options: DataLoaderRunOptions,
) -> list[tuple[int, ItemT]]:
    """Apply deterministic shuffle + offset/limit to a sequence.

    The returned index is the original item index before shuffling. Loaders use
    it to construct stable fallback ids while still supporting seeded sampling.
    """

    indexed_items = list(enumerate(items))
    if options.shuffle:
        rng = random.Random(options.seed)  # noqa: S311 - deterministic sampling, not security-sensitive.
        rng.shuffle(indexed_items)
    start = options.offset
    end = options.offset + options.limit
    return indexed_items[start:end]

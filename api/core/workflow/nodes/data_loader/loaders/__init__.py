"""Built-in data loaders for the generic data-loader node.

Importing this package runs the ``@register_loader`` side effects, populating
the registry before any ``DataLoaderNode`` instance resolves a loader by name.
To fork in a new dataset, drop a module under this package and add a single
``from .<your_loader> import <YourLoader>`` line below — see
:mod:`core.workflow.nodes.data_loader.registry` for the four-step recipe.
"""

from .inline_json import InlineJsonDataLoader
from .jsonl_file import JsonlFileDataLoader

__all__ = ["InlineJsonDataLoader", "JsonlFileDataLoader"]

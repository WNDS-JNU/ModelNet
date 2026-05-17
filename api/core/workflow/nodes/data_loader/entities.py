"""Typed DSL surface for the extensible ``data-loader`` workflow node.

The node intentionally separates common run controls from dataset-specific
configuration. ``DataLoaderNodeData`` owns pagination, deterministic shuffling,
and the selected ``loader_name``; concrete loaders own ``loader_config`` through
their own Pydantic models in ``loaders/``. New dataset loaders should register a
loader class instead of forking this node unless they need a dedicated frontend
or a different node type.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator

from graphon.entities.base_node_data import BaseNodeData
from graphon.enums import NodeType

from . import DATA_LOADER_NODE_TYPE


class DataLoaderNodeData(BaseNodeData):
    """Configuration shared by all data-loader implementations.

    ``loader_config`` stays open at this layer because each loader validates it
    with its own Pydantic config model at run time. This lets a fork add a new
    dataset by registering a loader class and config model without changing the
    generic node schema.
    """

    type: NodeType = DATA_LOADER_NODE_TYPE

    loader_name: str = Field(default="inline_json", min_length=1)
    loader_config: dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=100, gt=0, le=10000)
    offset: int = Field(default=0, ge=0)
    shuffle: bool = False
    seed: int | None = None

    @field_validator("loader_name")
    @classmethod
    def _loader_name_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("loader_name must not be blank")
        return stripped

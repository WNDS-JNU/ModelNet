"""Extensible data-loader workflow node package."""

DATA_LOADER_NODE_TYPE = "data-loader"

from .node import DataLoaderNode

__all__ = ["DATA_LOADER_NODE_TYPE", "DataLoaderNode"]

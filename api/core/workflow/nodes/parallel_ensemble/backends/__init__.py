"""Backend implementations registered into ``BackendRegistry``.

P2.9 will wire ``pkgutil.walk_packages`` over this directory so
importing the package triggers every ``@register_backend`` decorator
side-effect; for the current SPI freeze window we explicitly import
the modules that own built-in spec classes so ``ModelRegistry._load``
can dispatch built-in ``backend`` entries.
"""

from __future__ import annotations

from . import llama_cpp as llama_cpp
from . import vllm as vllm
from . import vllm_chat as vllm_chat

__all__: list[str] = ["llama_cpp", "vllm", "vllm_chat"]

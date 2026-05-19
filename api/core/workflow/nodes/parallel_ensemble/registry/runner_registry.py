"""Runner registry — sibling of ``BackendRegistry``.

Same shape; separate class to keep the two namespaces distinct (a
backend named ``token_step`` and a runner named ``token_step`` are not
the same thing, even though they often appear together).
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

from ..exceptions import DuplicateRegistrationError, UnknownRunnerError

if TYPE_CHECKING:
    from ..spi.runner import EnsembleRunner


class RunnerRegistry:
    """Process-wide map ``runner_name → EnsembleRunner subclass``."""

    _runners: dict[str, type[EnsembleRunner]] = {}

    @classmethod
    def register(cls, name: str, runner_cls: type[EnsembleRunner]) -> None:
        if name in cls._runners:
            raise DuplicateRegistrationError("runner", name)
        cls._runners[name] = runner_cls

    @classmethod
    def get(cls, name: str) -> type[EnsembleRunner]:
        try:
            return cls._runners[name]
        except KeyError as exc:
            cls._load_builtin_runners()
            try:
                return cls._runners[name]
            except KeyError:
                raise UnknownRunnerError(name, list(cls._runners)) from exc

    @classmethod
    def _load_builtin_runners(cls) -> None:
        """Import built-ins if registration side effects have not run yet."""
        builtins = {
            "dynamic_collab_route": (
                "core.workflow.nodes.parallel_ensemble.runners.dynamic_collab_route",
                "DynamicCollabRouteRunner",
            ),
            "token_step": (
                "core.workflow.nodes.parallel_ensemble.runners.token_step",
                "TokenStepRunner",
            ),
        }
        for name, (module_name, class_name) in builtins.items():
            if name in cls._runners:
                continue
            module = importlib.import_module(module_name)
            runner_cls = getattr(module, class_name)
            cls._runners.setdefault(name, runner_cls)

    @classmethod
    def known_runners(cls) -> list[str]:
        return sorted(cls._runners)

    @classmethod
    def reset_for_testing(cls) -> None:
        cls._runners = {}


def register_runner(name: str):
    """Decorator form of :meth:`RunnerRegistry.register`."""

    def deco(runner_cls: type[EnsembleRunner]) -> type[EnsembleRunner]:
        runner_cls.name = name
        RunnerRegistry.register(name, runner_cls)
        return runner_cls

    return deco

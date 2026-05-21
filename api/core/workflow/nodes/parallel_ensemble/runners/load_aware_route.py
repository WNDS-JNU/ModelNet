"""Load-aware response routing runner for ModelNet sources."""

from __future__ import annotations

import time
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from services.model_net_load_service import route_model_from_load

from ..exceptions import ParallelEnsembleError
from ..registry.runner_registry import register_runner
from ..spi.aggregator import Aggregator
from ..spi.backend import GenerationParams, ModelBackend, TokenStepParams
from ..spi.capability import Capability
from ..spi.requirements import Requirement, ValidationIssue
from ..spi.runner import DoneEvent, EnsembleRunner, SourceInput
from ..spi.trace import ResponseTraceEntry, TraceCollector


class LoadAwareRouteConfig(BaseModel):
    """Configuration for Prometheus-backed one-shot model routing."""

    model_config = ConfigDict(extra="forbid")

    required_capabilities: list[str] = Field(default_factory=list)
    include_unhealthy: bool = False
    top_k: int = Field(default=1, gt=0)


def _generation_params(params: TokenStepParams) -> GenerationParams:
    out: GenerationParams = {
        "max_tokens": params.max_tokens,
        "top_k": params.top_k,
    }
    if params.temperature is not None:
        out["temperature"] = params.temperature
    if params.top_p is not None:
        out["top_p"] = params.top_p
    if params.stop:
        out["stop"] = list(params.stop)
    if params.seed is not None:
        out["seed"] = params.seed
    out.update(dict(params.extra))
    return out


@register_runner("load_aware_route")
class LoadAwareRouteRunner(EnsembleRunner[LoadAwareRouteConfig]):
    """Select the least-loaded eligible model, then generate one response."""

    config_class: ClassVar[type[BaseModel]] = LoadAwareRouteConfig
    aggregator_scope: ClassVar[str] = "route"
    required_capabilities: ClassVar[frozenset[Capability]] = frozenset()
    optional_capabilities: ClassVar[frozenset[Capability]] = frozenset()

    i18n_key_prefix: ClassVar[str] = "parallelEnsemble.runners.loadAwareRoute"
    ui_schema: ClassVar[dict] = {
        "required_capabilities": {"control": "multi_select", "options": []},
        "include_unhealthy": {"control": "switch"},
        "top_k": {"control": "number_input", "min": 1, "step": 1},
    }

    def __init__(self, executor: Any, aggregator_config: BaseModel) -> None:
        del executor
        self._aggregator_config = aggregator_config

    @classmethod
    def requirements(cls, config: LoadAwareRouteConfig) -> list[Requirement]:
        del config
        return []

    @classmethod
    def validate_selection(
        cls,
        config: LoadAwareRouteConfig,
        model_aliases: list[str],
        registry: Any,
    ) -> list[ValidationIssue]:
        del config, registry
        if not model_aliases:
            return [
                {
                    "severity": "error",
                    "requirement": {
                        "kind": "needs_model_alias",
                        "value": True,
                        "rationale": "load_aware_route needs at least one source to route",
                    },
                    "message": "load_aware_route requires at least one model alias",
                    "i18n_key": "parallelEnsemble.errors.tooFewModels",
                }
            ]
        return []

    def run(
        self,
        sources: dict[str, SourceInput],
        backends: dict[str, ModelBackend],
        aggregator: Aggregator,
        config: LoadAwareRouteConfig,
        trace: TraceCollector,
    ) -> Any:
        del aggregator
        if not sources or not backends:
            raise ParallelEnsembleError("load_aware_route requires at least one source")

        alias_to_source_ids: dict[str, list[str]] = {}
        for source_id, backend in backends.items():
            alias_to_source_ids.setdefault(backend.id, []).append(source_id)

        route = route_model_from_load(
            candidate_aliases=list(alias_to_source_ids),
            required_capabilities=config.required_capabilities,
            policy={
                "top_k": config.top_k,
                "include_unhealthy": config.include_unhealthy,
            },
        )
        selected_alias = route.get("selected_alias")
        if not isinstance(selected_alias, str) or selected_alias not in alias_to_source_ids:
            reason = route.get("fallback_reason") or "no model selected"
            raise ParallelEnsembleError(f"load_aware_route failed: {reason}")

        selected_source_id = alias_to_source_ids[selected_alias][0]
        source = sources[selected_source_id]
        backend = backends[selected_source_id]
        start = time.perf_counter()
        result = backend.generate(source["prompt"], _generation_params(source["params"]))
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        trace.record_response(
            ResponseTraceEntry(
                source_id=selected_source_id,
                text=result.get("text", ""),
                finish_reason=result.get("finish_reason", ""),
                tokens_count=0,
                elapsed_ms=elapsed_ms,
                error=None,
            )
        )
        trace.record_summary("selected_alias", selected_alias)
        trace.record_summary("selected_source_id", selected_source_id)
        trace.record_summary("route", route)

        yield DoneEvent(
            kind="done",
            text=result.get("text", ""),
            metadata={
                "selected_alias": selected_alias,
                "selected_source_id": selected_source_id,
                "route": route,
                "finish_reason": result.get("finish_reason", ""),
            },
        )

"""Dynamic collaborative routing based on pairwise model relationships.

This runner implements the response-level serial routing method from
``Dynamic Model Routing Based on Collaborative Relationship`` while reusing
the existing ``parallel-ensemble`` SPI:

* token-model-source renders the initial task prompt and chooses aliases;
* the model registry instantiates one backend per source;
* this runner calls the existing ``ModelBackend.generate`` method for
  initial answers, binary judgements, and refinement hops;
* TraceCollector stores route diagnostics in the usual ensemble trace.
"""

from __future__ import annotations

import json
import random
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any, ClassVar, Literal, TypedDict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..exceptions import ParallelEnsembleError
from ..registry.runner_registry import register_runner
from ..spi.aggregator import Aggregator
from ..spi.backend import GenerationParams, GenerationResult, ModelBackend, TokenStepParams
from ..spi.capability import Capability
from ..spi.requirements import Requirement, ValidationIssue
from ..spi.runner import DoneEvent, EnsembleRunner, RunnerEvent, SourceInput
from ..spi.trace import ResponseTraceEntry, TraceCollector

DEFAULT_JUDGE_PROMPT_TEMPLATE = (
    "这是问题: {question} , 这是回答: {answer} . "
    "请你作为一个通用领域的专家, 告诉我回答是否令你满意. "
    "你只需回复我认可或者不认可, 不需要输出其他任何内容."
)

DEFAULT_REFINE_PROMPT_TEMPLATE = (
    "这是问题: {question} , 这是回答: {answer} . "
    "请你作为一个通用领域的专家, 结合你自己的理解优化该回答. "
    "你只需要按照问题中对回复的格式要求输出并优化回复, 不需要输出其他任何内容."
)


class DynamicCollabRouteConfig(BaseModel):
    """Config for the dynamic collaborative route runner."""

    model_config = ConfigDict(extra="forbid")

    initial_source_id: str | None = None
    """Optional first-hop source. Empty means the first configured source."""

    collaboration_graph_json: str = ""
    """JSON graph or graph-builder artifact. Empty means all-to-all."""

    supplemental_graph_json: str = ""
    """Optional C' graph used when the primary graph has no candidates."""

    max_hops: int = Field(default=3, ge=0)
    """Maximum number of refinement hops after the initial answer."""

    seed: int | None = None
    """Seed for choosing among multiple rejecting candidate models."""

    judge_max_tokens: int = Field(default=8, gt=0)
    """Small generation budget for the binary approval judgement."""

    judge_prompt_template: str = DEFAULT_JUDGE_PROMPT_TEMPLATE
    refine_prompt_template: str = DEFAULT_REFINE_PROMPT_TEMPLATE

    @field_validator("initial_source_id", mode="before")
    @classmethod
    def _blank_source_means_default(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("collaboration_graph_json", "supplemental_graph_json", mode="before")
    @classmethod
    def _blank_graph_means_empty(cls, value: object) -> object:
        if value is None:
            return ""
        return value

    @field_validator("judge_prompt_template", "refine_prompt_template", mode="after")
    @classmethod
    def _template_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("prompt template must not be blank")
        return value


class _Judgement(TypedDict):
    source_id: str
    text: str
    accepted: bool
    parsed: Literal["accepted", "rejected", "unparseable"]
    error: str | None


@register_runner("dynamic_collab_route")
class DynamicCollabRouteRunner(EnsembleRunner[DynamicCollabRouteConfig]):
    """Response-level serial dynamic route runner."""

    config_class: ClassVar[type[BaseModel]] = DynamicCollabRouteConfig
    aggregator_scope: ClassVar[str] = "route"
    required_capabilities: ClassVar[frozenset[Capability]] = frozenset()
    optional_capabilities: ClassVar[frozenset[Capability]] = frozenset({Capability.CHAT_TEMPLATE})

    i18n_key_prefix: ClassVar[str] = "parallelEnsemble.runners.dynamicCollabRoute"
    ui_schema: ClassVar[dict] = {
        "initial_source_id": {"control": "text_input"},
        "collaboration_graph_json": {"control": "textarea"},
        "supplemental_graph_json": {"control": "textarea"},
        "max_hops": {"control": "number_input", "min": 0, "step": 1},
        "seed": {"control": "number_input", "step": 1},
        "judge_max_tokens": {"control": "number_input", "min": 1, "step": 1},
        "judge_prompt_template": {"control": "textarea"},
        "refine_prompt_template": {"control": "textarea"},
    }

    def __init__(
        self,
        executor: ThreadPoolExecutor,
        aggregator_config: BaseModel,
    ) -> None:
        self._executor = executor
        self._aggregator_config = aggregator_config

    @classmethod
    def requirements(cls, config: DynamicCollabRouteConfig) -> list[Requirement]:
        del config
        return []

    @classmethod
    def validate_selection(
        cls,
        config: DynamicCollabRouteConfig,
        model_aliases: list[str],
        registry: Any,
    ) -> list[ValidationIssue]:
        del config, registry
        if not model_aliases:
            return [
                {
                    "severity": "error",
                    "requirement": {
                        "kind": "needs_chat_template",
                        "value": False,
                        "rationale": "dynamic_collab_route needs at least one source to produce the initial answer",
                    },
                    "message": "dynamic_collab_route requires at least one model alias",
                    "i18n_key": "parallelEnsemble.errors.tooFewModels",
                }
            ]
        return []

    def run(
        self,
        sources: dict[str, SourceInput],
        backends: dict[str, ModelBackend],
        aggregator: Aggregator,
        config: DynamicCollabRouteConfig,
        trace: TraceCollector,
    ) -> Iterator[RunnerEvent]:
        del aggregator

        run_start = time.perf_counter()
        source_ids = list(sources)
        if not source_ids:
            raise ParallelEnsembleError("dynamic_collab_route requires at least one source")

        initial_source_id = config.initial_source_id or source_ids[0]
        if initial_source_id not in sources:
            raise ParallelEnsembleError(
                f"initial_source_id={initial_source_id!r} is not one of the configured sources {source_ids!r}"
            )

        graph, supplemental_graph = _parse_graph_config(
            config.collaboration_graph_json,
            config.supplemental_graph_json,
            known_sources=set(source_ids),
        )
        rng = random.Random(config.seed)  # noqa: S311 - deterministic experiment routing, not security randomness.

        question = sources[initial_source_id]["prompt"]
        route: list[str] = [initial_source_id]
        route_steps: list[dict[str, Any]] = []
        backend_errors: dict[str, str] = {}

        answer = self._generate_or_raise(
            phase="initial",
            source_id=initial_source_id,
            backend=backends[initial_source_id],
            prompt=question,
            params=_generation_params(sources[initial_source_id]["params"]),
            trace=trace,
            backend_errors=backend_errors,
        )["text"]

        current_source_id = initial_source_id
        stopped_by = "max_hops" if config.max_hops == 0 else "consensus"

        for hop_index in range(config.max_hops):
            candidates = _candidate_source_ids(
                current_source_id=current_source_id,
                graph=graph,
                all_sources=source_ids,
                visited=set(route),
            )
            candidate_graph = "all_to_all" if graph is None else "collaboration"
            if not candidates and supplemental_graph is not None:
                candidates = _candidate_source_ids(
                    current_source_id=current_source_id,
                    graph=supplemental_graph,
                    all_sources=source_ids,
                    visited=set(route),
                )
                candidate_graph = "supplemental"
            if not candidates:
                stopped_by = "no_candidates"
                route_steps.append(
                    {
                        "hop": hop_index + 1,
                        "current_source_id": current_source_id,
                        "candidate_graph": candidate_graph,
                        "candidates": [],
                        "judgements": [],
                        "rejecting_sources": [],
                    }
                )
                break

            judgements = [
                self._judge(
                    source_id=sid,
                    backend=backends[sid],
                    prompt=_render_template(
                        config.judge_prompt_template,
                        question=question,
                        answer=answer,
                    ),
                    max_tokens=config.judge_max_tokens,
                    base_params=sources[sid]["params"],
                    trace=trace,
                    backend_errors=backend_errors,
                )
                for sid in candidates
            ]
            rejecting_sources = [
                item["source_id"]
                for item in judgements
                if item["error"] is None and not item["accepted"]
            ]

            step: dict[str, Any] = {
                "hop": hop_index + 1,
                "current_source_id": current_source_id,
                "candidate_graph": candidate_graph,
                "candidates": candidates,
                "judgements": judgements,
                "rejecting_sources": rejecting_sources,
            }
            if not rejecting_sources:
                stopped_by = "consensus"
                route_steps.append(step)
                break

            next_source_id = rng.choice(rejecting_sources)
            step["selected_source_id"] = next_source_id
            refine_prompt = _render_template(
                config.refine_prompt_template,
                question=question,
                answer=answer,
            )
            try:
                refined = self._generate_or_raise(
                    phase=f"refine_hop_{hop_index + 1}",
                    source_id=next_source_id,
                    backend=backends[next_source_id],
                    prompt=refine_prompt,
                    params=_generation_params(sources[next_source_id]["params"]),
                    trace=trace,
                    backend_errors=backend_errors,
                )
            except Exception as exc:
                stopped_by = "refine_error"
                step["error"] = f"{type(exc).__name__}: {exc}"
                route_steps.append(step)
                break

            answer = refined["text"]
            current_source_id = next_source_id
            route.append(next_source_id)
            route_steps.append(step)
        else:
            stopped_by = "max_hops"

        elapsed_ms = int((time.perf_counter() - run_start) * 1000)
        trace.record_summary("stopped_by", stopped_by)
        trace.record_summary("tokens_count", 0)
        trace.record_summary("total_elapsed_ms", elapsed_ms)
        trace.record_summary("route", route)
        trace.record_summary("hops_count", max(0, len(route) - 1))
        trace.record_summary("route_steps", route_steps)
        trace.record_summary("backend_count", len(backends))
        trace.record_summary("error_count", len(backend_errors))

        yield DoneEvent(
            kind="done",
            text=answer,
            metadata={
                "stopped_by": stopped_by,
                "elapsed_ms": elapsed_ms,
                "route": route,
                "hops_count": max(0, len(route) - 1),
            },
        )

    def _judge(
        self,
        *,
        source_id: str,
        backend: ModelBackend,
        prompt: str,
        max_tokens: int,
        base_params: TokenStepParams,
        trace: TraceCollector,
        backend_errors: dict[str, str],
    ) -> _Judgement:
        try:
            result = self._generate_or_raise(
                phase="judge",
                source_id=source_id,
                backend=backend,
                prompt=prompt,
                params=_generation_params(base_params, max_tokens=max_tokens),
                trace=trace,
                backend_errors=backend_errors,
            )
        except Exception as exc:
            return {
                "source_id": source_id,
                "text": "",
                "accepted": True,
                "parsed": "unparseable",
                "error": f"{type(exc).__name__}: {exc}",
            }

        accepted, parsed = _parse_judgement(result["text"])
        return {
            "source_id": source_id,
            "text": result["text"],
            "accepted": accepted,
            "parsed": parsed,
            "error": None,
        }

    @staticmethod
    def _generate_or_raise(
        *,
        phase: str,
        source_id: str,
        backend: ModelBackend,
        prompt: str,
        params: GenerationParams,
        trace: TraceCollector,
        backend_errors: dict[str, str],
    ) -> GenerationResult:
        start = time.perf_counter()
        try:
            result = backend.generate(prompt, params)
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            error = f"{type(exc).__name__}: {exc}"
            backend_errors[f"{phase}:{source_id}"] = error
            trace.record_response(
                ResponseTraceEntry(
                    source_id=f"{phase}:{source_id}",
                    text=None,
                    finish_reason="error",
                    tokens_count=0,
                    elapsed_ms=elapsed_ms,
                    error=error,
                )
            )
            raise

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        trace.record_response(
            ResponseTraceEntry(
                source_id=f"{phase}:{source_id}",
                text=result.get("text", ""),
                finish_reason=result.get("finish_reason", ""),
                tokens_count=_usage_tokens(result.get("metadata", {})),
                elapsed_ms=elapsed_ms,
                error=None,
            )
        )
        return result


def _generation_params(base: TokenStepParams, max_tokens: int | None = None) -> GenerationParams:
    params: GenerationParams = {"max_tokens": max_tokens or base.max_tokens}
    if base.temperature is not None:
        params["temperature"] = base.temperature
    if base.top_p is not None:
        params["top_p"] = base.top_p
    if base.stop:
        params["stop"] = list(base.stop)
    if base.seed is not None:
        params["seed"] = base.seed
    return params


def _usage_tokens(metadata: dict[str, Any]) -> int:
    usage = metadata.get("usage")
    if isinstance(usage, dict):
        total = usage.get("total_tokens")
        if isinstance(total, int):
            return total
    return 0


def _parse_graph_config(
    collaboration_raw: str,
    supplemental_raw: str,
    *,
    known_sources: set[str],
) -> tuple[dict[str, list[str]] | None, dict[str, list[str]] | None]:
    if not collaboration_raw.strip():
        return None, _parse_graph(
            supplemental_raw,
            known_sources=known_sources,
            field_name="supplemental_graph_json",
        )

    try:
        data = json.loads(collaboration_raw)
    except json.JSONDecodeError as exc:
        raise ParallelEnsembleError(f"collaboration_graph_json is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ParallelEnsembleError("collaboration_graph_json must be a JSON object")

    if "collaboration_graph" in data:
        primary = _normalize_graph(
            data.get("collaboration_graph"),
            known_sources=known_sources,
            field_name="collaboration_graph_json.collaboration_graph",
        )
        embedded_supplemental = _normalize_graph(
            data.get("supplemental_graph"),
            known_sources=known_sources,
            field_name="collaboration_graph_json.supplemental_graph",
            allow_missing=True,
        )
        explicit_supplemental = _parse_graph(
            supplemental_raw,
            known_sources=known_sources,
            field_name="supplemental_graph_json",
        )
        return primary, explicit_supplemental or embedded_supplemental

    return _normalize_graph(
        data,
        known_sources=known_sources,
        field_name="collaboration_graph_json",
    ), _parse_graph(
        supplemental_raw,
        known_sources=known_sources,
        field_name="supplemental_graph_json",
    )


def _parse_graph(raw: str, *, known_sources: set[str], field_name: str) -> dict[str, list[str]] | None:
    if not raw.strip():
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ParallelEnsembleError(f"{field_name} is not valid JSON: {exc}") from exc
    return _normalize_graph(data, known_sources=known_sources, field_name=field_name)


def _normalize_graph(
    data: object,
    *,
    known_sources: set[str],
    field_name: str,
    allow_missing: bool = False,
) -> dict[str, list[str]] | None:
    if data is None and allow_missing:
        return None
    if not isinstance(data, dict):
        raise ParallelEnsembleError(f"{field_name} must be a JSON object")

    graph: dict[str, list[str]] = {}
    for source_id, candidates in data.items():
        if not isinstance(source_id, str) or source_id not in known_sources:
            raise ParallelEnsembleError(f"{field_name} keys must be known source_id strings")
        if not isinstance(candidates, list):
            raise ParallelEnsembleError(f"{field_name} entry {source_id!r} must be a list")
        normalized_candidates: list[str] = []
        for item in candidates:
            if not isinstance(item, str) or item not in known_sources:
                raise ParallelEnsembleError(f"{field_name} candidates must be known source_id strings")
            if item != source_id:
                normalized_candidates.append(item)
        graph[source_id] = normalized_candidates
    return graph


def _candidate_source_ids(
    *,
    current_source_id: str,
    graph: dict[str, list[str]] | None,
    all_sources: list[str],
    visited: set[str],
) -> list[str]:
    if graph is None:
        candidates = all_sources
    else:
        candidates = graph.get(current_source_id, [])
    return [
        source_id
        for source_id in candidates
        if source_id != current_source_id and source_id not in visited
    ]


def _render_template(template: str, *, question: str, answer: str) -> str:
    try:
        return template.format(question=question, answer=answer)
    except KeyError as exc:
        raise ParallelEnsembleError(
            "dynamic_collab_route prompt templates may only reference {question} and {answer}"
        ) from exc


def _parse_judgement(text: str) -> tuple[bool, Literal["accepted", "rejected", "unparseable"]]:
    normalized = text.strip().lower()
    if not normalized:
        return True, "unparseable"

    reject_markers = ("不认可", "不满意", "不同意", "否", "reject", "rejected", "not approve", "not satisfied")
    accept_markers = ("认可", "满意", "同意", "是", "approve", "approved", "accept", "accepted", "satisfied")
    if any(marker in normalized for marker in reject_markers):
        return False, "rejected"
    if any(marker in normalized for marker in accept_markers):
        return True, "accepted"
    return True, "unparseable"

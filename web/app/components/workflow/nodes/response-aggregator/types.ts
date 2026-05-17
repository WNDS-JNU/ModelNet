import type { CommonNodeType, ModelConfig, ValueSelector } from '@/app/components/workflow/types'

export const RESPONSE_AGGREGATOR_NODE_TYPE = 'response-aggregator' as const

// Static + dynamic weight surfaces mirror backend ``AggregationInputRef.
// weight`` (Pydantic ``float | list[str]``). The ``list[str]`` branch is a
// ``VariableSelector`` resolved at runtime against the variable pool —
// same shape as ``variable_selector`` so the runtime resolver doesn't
// have to special-case malformed input. ADR-v3-15.
export type AggregationInputRef = {
  source_id: string
  variable_selector: ValueSelector
  weight: number | ValueSelector
  // Numeric fallback when a dynamic weight selector fails to resolve.
  // ``null`` (default) = fail-fast: the backend raises
  // ``WeightResolutionError`` and the node FAILs.
  fallback_weight: number | null
  // Per-source pass-through metadata, surfaced to strategies via
  // ``SourceAggregationContext.source_meta`` server-side; UI keeps the
  // dict shape so DSL authors can ride extra context (e.g.
  // ``{"confidence_tier": "high"}``) without DSL edits.
  extra: Record<string, unknown>
}

export type ResponseAggregatorNodeType = CommonNodeType & {
  inputs: AggregationInputRef[]
  instruction: string
  model: ModelConfig
}

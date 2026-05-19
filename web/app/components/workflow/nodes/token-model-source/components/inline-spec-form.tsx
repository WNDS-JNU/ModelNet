'use client'
// Form for the "Custom model" mode (inline_spec). The fields below
// mirror the built-in parallel-ensemble backends; the server-side
// ``BackendRegistry.get_spec_class(...)`` remains authoritative and
// validates the payload again at run time.
import type { ChangeEvent, FC } from 'react'
import type { InlineModelSpec } from '../types'
import { Button } from '@langgenius/dify-ui/button'
import { cn } from '@langgenius/dify-ui/cn'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@langgenius/dify-ui/dropdown-menu'
import { Switch } from '@langgenius/dify-ui/switch'
import * as React from 'react'
import { useCallback, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Input from '@/app/components/base/input'
import Field from '@/app/components/workflow/nodes/_base/components/field'
import { post } from '@/service/base'

const i18nPrefix = 'nodes.tokenModelSource.inlineSpec'

// Built-in backends registered server-side today. Kept as a static list
// until a backend-metadata endpoint exists. Each row carries a label key
// so the dropdown can show a friendlier name than the raw registry key.
const KNOWN_BACKENDS: ReadonlyArray<{ id: string, labelKey: string }> = [
  { id: 'llama_cpp', labelKey: `${i18nPrefix}.backends.llamaCpp` },
  { id: 'vllm', labelKey: `${i18nPrefix}.backends.vllm` },
  { id: 'vllm_chat', labelKey: `${i18nPrefix}.backends.vllmChat` },
]

const BUILTIN_COMPLETION_BACKENDS = new Set(['llama_cpp', 'vllm', 'vllm_chat'])

// Match a ``scheme://host`` prefix without any port / path / query /
// fragment trailing it. Constrained to the chars URL schemes and
// hostnames actually use so the regex stays linear-time (no ``.*``
// tail to backtrack into a sibling quantifier).
const SCHEME_HOST_PREFIX = /^[a-z][a-z\d+\-.]*:\/\/[^/:?#]+/i

// Split a stored ``model_url`` (single string round-tripped to the
// backend's ``AnyUrl``) into the two edit boxes the panel surfaces.
// The port is whatever digits follow ``scheme://host:`` before any
// path / query / fragment; everything else stays in ``base`` so a
// user-typed path / query string survives the round-trip.
const parseModelUrl = (full: string): { base: string, port: string } => {
  const m = full.match(SCHEME_HOST_PREFIX)
  if (!m || !m[0])
    return { base: full, port: '' }
  const schemeHost = m[0]
  const rest = full.slice(schemeHost.length)
  if (!rest.startsWith(':'))
    return { base: full, port: '' }
  // Walk digits manually after the colon — avoids the ``\d+`` /
  // ``.*`` backtracking pair that ``regexp/no-super-linear-backtracking``
  // flags, and stops cleanly at the first non-digit (path / EOL).
  let i = 1
  while (i < rest.length) {
    const ch = rest.charCodeAt(i)
    if (ch < 48 || ch > 57)
      break
    i++
  }
  const port = rest.slice(1, i)
  if (!port)
    return { base: full, port: '' }
  return { base: schemeHost + rest.slice(i), port }
}

// Re-insert ``port`` between scheme://host and any path / query /
// fragment the user typed into ``base``. Empty port returns ``base``
// verbatim so the saved URL stays minimal when the user hasn't
// pinned one.
const joinModelUrl = (base: string, port: string): string => {
  if (!port)
    return base
  const m = base.match(SCHEME_HOST_PREFIX)
  if (!m || !m[0])
    return `${base}:${port}`
  const schemeHost = m[0]
  return `${schemeHost}:${port}${base.slice(schemeHost.length)}`
}

const buildModelsProbeUrl = (raw: string): string | null => {
  if (!raw)
    return null
  try {
    const u = new URL(raw)
    if ((u.protocol !== 'http:' && u.protocol !== 'https:') || !u.host)
      return null

    const pathPrefix = u.pathname.replace(/\/+$/, '')
    let probePath = '/v1/models'
    if (pathPrefix) {
      if (pathPrefix.endsWith('/v1/models'))
        probePath = pathPrefix
      else if (pathPrefix.endsWith('/v1'))
        probePath = `${pathPrefix}/models`
      else
        probePath = `${pathPrefix}/v1/models`
    }

    return `${u.protocol}//${u.host}${probePath}`
  }
  catch {
    return null
  }
}

type ProbeModelInfoResponse = {
  model_name: string
  EOS?: string
}

type Props = {
  readonly: boolean
  value: InlineModelSpec
  onChange: (patch: Partial<InlineModelSpec>) => void
}

const InlineSpecForm: FC<Props> = ({ readonly, value, onChange }) => {
  const { t } = useTranslation()
  const [backendOpen, setBackendOpen] = useState(false)
  const [typeOpen, setTypeOpen] = useState(false)
  const [isProbing, setIsProbing] = useState(false)
  const [probeError, setProbeError] = useState<string | null>(null)
  const [probeOk, setProbeOk] = useState(false)

  // Probe target is only well-formed when the URL has both a scheme +
  // host. We don't replicate ``isWellFormedUrl``
  // from default.ts because that lives in a sibling module; the
  // server-side validator catches malformed URLs in any case. Here we
  // just gate the button on the minimum pieces the user has to type
  // to make the probe meaningful.
  const probeUrl = useMemo(() => {
    const raw = value.model_url?.trim() ?? ''
    return buildModelsProbeUrl(raw)
  }, [value.model_url])

  const handleProbeModelInfo = useCallback(async () => {
    if (!probeUrl)
      return
    setIsProbing(true)
    setProbeError(null)
    setProbeOk(false)
    try {
      // Server-side proxy: the original implementation called
      // ``fetch(probeUrl)`` from the browser, which only works for
      // llama.cpp because it enables CORS by default. vLLM / TGI /
      // SGLang / hosted routers do not, so the request was blocked
      // before it left the browser. The console endpoint reissues
      // the GET through ``ssrf_proxy`` so the same egress / SSRF
      // guards apply and CORS is no longer a barrier — the OpenAI-
      // compat response shape (``data[].id``) is parsed server-side;
      // if the URL / model name matches ``model_net.yaml``, the
      // endpoint also returns the registered ``EOS`` value.
      // ``silent: true`` suppresses the global error toast so the
      // panel can show the diagnostic inline like before.
      const resp = await post<ProbeModelInfoResponse>(
        '/workflow/probe-model-info',
        { body: { url: value.model_url ?? '' } },
        { silent: true },
      )
      if (!resp?.model_name)
        throw new Error('no model in response')
      const patch: Partial<InlineModelSpec> = { model_name: resp.model_name }
      if (typeof resp.EOS === 'string' && resp.EOS.length > 0)
        patch.EOS = resp.EOS
      onChange(patch)
      setProbeOk(true)
    }
    catch (e) {
      // Dify's ``post`` helper rejects with the raw ``Response`` on a
      // non-2xx (the BaseHTTPException body carries ``code`` / ``message``);
      // unwrap the upstream diagnostic so the user sees the same level
      // of detail the old direct-fetch surfaced ("HTTP 503 from
      // upstream", "no model in response", etc.).
      let message = 'fetch failed'
      if (e instanceof Response) {
        try {
          const parsed = await e.json() as { message?: string }
          if (parsed?.message)
            message = parsed.message
          else
            message = `HTTP ${e.status}`
        }
        catch {
          message = `HTTP ${e.status}`
        }
      }
      else if (e instanceof Error) {
        message = e.message
      }
      setProbeError(message)
    }
    finally {
      setIsProbing(false)
    }
  }, [probeUrl, value.model_url, onChange])

  const handleText = useCallback(
    (key: keyof InlineModelSpec) =>
      (e: ChangeEvent<HTMLInputElement>) => {
        // Empty-string is preserved on text inputs so the panel red-line
        // can show "required field"; the user has to type something to
        // get past ``checkValid``.
        onChange({ [key]: e.target.value } as Partial<InlineModelSpec>)
      },
    [onChange],
  )

  const handleOptionalText = useCallback(
    (key: keyof InlineModelSpec) =>
      (e: ChangeEvent<HTMLInputElement>) => {
        const raw = e.target.value
        onChange({ [key]: raw === '' ? null : raw } as Partial<InlineModelSpec>)
      },
    [onChange],
  )

  const handleNumber = useCallback(
    (key: keyof InlineModelSpec, requireInteger = false) =>
      (e: ChangeEvent<HTMLInputElement>) => {
        const raw = e.target.value
        if (raw === '') {
          onChange({ [key]: undefined } as Partial<InlineModelSpec>)
          return
        }
        const n = Number(raw)
        if (!Number.isFinite(n))
          return
        if (requireInteger && !Number.isInteger(n))
          return
        onChange({ [key]: n } as Partial<InlineModelSpec>)
      },
    [onChange],
  )

  const handleBackendPick = useCallback(
    (id: string) => {
      const patch: Partial<InlineModelSpec> = { backend: id }
      if (id === 'vllm' || id === 'vllm_chat') {
        patch.type = 'normal'
        patch.stop_think = null
        patch.model_arch = undefined
        patch.expose_raw_logits = false
      }
      onChange(patch)
      setBackendOpen(false)
    },
    [onChange],
  )

  const handleTypePick = useCallback(
    (next: 'normal' | 'think') => {
      // Switching away from ``think`` drops ``stop_think`` so a stale
      // value cannot bleed back through if the user toggles modes.
      onChange(
        next === 'think'
          ? { type: 'think' }
          : { type: 'normal', stop_think: null },
      )
      setTypeOpen(false)
    },
    [onChange],
  )

  // ``KNOWN_BACKENDS`` is a non-empty const list, so the fallback is
  // always defined; the non-null assertion just narrows the type for
  // the readonly-array case (TS treats ``a[0]`` as ``T | undefined``).
  const selectedBackend
    = KNOWN_BACKENDS.find(b => b.id === value.backend) ?? KNOWN_BACKENDS[0]!
  const isLlamaCpp = value.backend === 'llama_cpp'
  const isBuiltInCompletionBackend = BUILTIN_COMPLETION_BACKENDS.has(value.backend)

  return (
    <div className="space-y-3">
      <Field
        title={t(`${i18nPrefix}.backend.label`, { ns: 'workflow' })}
        tooltip={t(`${i18nPrefix}.backend.tooltip`, { ns: 'workflow' })}
        required
      >
        <DropdownMenu open={backendOpen} onOpenChange={setBackendOpen}>
          <DropdownMenuTrigger
            disabled={readonly}
            className={cn(
              'flex w-full items-center justify-between rounded-lg bg-components-input-bg-normal px-3 py-2',
              readonly
                ? 'cursor-not-allowed bg-components-input-bg-disabled!'
                : 'cursor-pointer hover:bg-state-base-hover-alt',
              backendOpen && 'bg-state-base-hover-alt',
            )}
          >
            <span className="truncate system-sm-regular text-components-input-text-filled">
              {t(selectedBackend.labelKey, {
                ns: 'workflow',
                defaultValue: selectedBackend.id,
              })}
            </span>
            <span
              aria-hidden
              className={cn(
                'i-ri-arrow-down-s-line h-4 w-4 text-text-quaternary',
                backendOpen && 'text-text-secondary',
              )}
            />
          </DropdownMenuTrigger>
          <DropdownMenuContent placement="bottom-start" sideOffset={4}>
            {KNOWN_BACKENDS.map(b => (
              <DropdownMenuItem
                key={b.id}
                onClick={() => handleBackendPick(b.id)}
              >
                <div className="flex grow flex-col px-1">
                  <span className="system-sm-medium text-text-secondary">
                    {t(b.labelKey, { ns: 'workflow', defaultValue: b.id })}
                  </span>
                  <span className="system-xs-regular text-text-tertiary">{b.id}</span>
                </div>
                {b.id === value.backend && (
                  <span aria-hidden className="i-ri-check-line h-4 w-4 text-text-accent" />
                )}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </Field>

      <Field
        title={t(`${i18nPrefix}.modelName.label`, { ns: 'workflow' })}
        tooltip={t(`${i18nPrefix}.modelName.tooltip`, { ns: 'workflow' })}
        required
      >
        <Input
          value={value.model_name}
          onChange={handleText('model_name')}
          disabled={readonly}
          placeholder={t(`${i18nPrefix}.modelName.placeholder`, {
            ns: 'workflow',
            defaultValue: 'llama-3.1-8b-instruct',
          })}
        />
      </Field>

      <Field
        title={t(`${i18nPrefix}.modelUrl.label`, { ns: 'workflow' })}
        tooltip={t(`${i18nPrefix}.modelUrl.tooltip`, { ns: 'workflow' })}
        required
      >
        {/* URL + port split into two inputs, plus a probe button that
            hits the URL's OpenAI-compatible ``/v1/models`` endpoint
            and auto-fills ``model_name`` from the first entry. The
            probe preserves any path prefix before ``/v1`` because
            hosted routers can scope one model per URL path. The wire
            still carries one ``model_url`` string so the backend
            ``model_url: AnyUrl`` field stays the canonical schema; the
            split is purely a UX
            upgrade over a single text box. Round-tripping via
            parse/joinModelUrl preserves a user-typed path / query
            string when present. ``Field`` accepts only one child, so
            wrap the row + probe-button block in a single outer div. */}
        <div>
          <div className="flex gap-2">
            <div className="flex-1">
              <Input
                value={parseModelUrl(value.model_url ?? '').base}
                onChange={(e) => {
                  const { port } = parseModelUrl(value.model_url ?? '')
                  onChange({ model_url: joinModelUrl(e.target.value, port) })
                }}
                disabled={readonly}
                placeholder={t(`${i18nPrefix}.modelUrl.placeholder`, {
                  ns: 'workflow',
                  defaultValue: 'http://219.222.20.79',
                })}
              />
            </div>
            <div className="w-24">
              <Input
                type="number"
                min={1}
                step={1}
                value={parseModelUrl(value.model_url ?? '').port}
                onChange={(e) => {
                  const { base } = parseModelUrl(value.model_url ?? '')
                  const raw = e.target.value
                  // Reject fractional input so the port box mirrors the
                  // server-side integer contract; allow empty so the
                  // user can clear it.
                  if (raw !== '' && (!Number.isFinite(Number(raw)) || !Number.isInteger(Number(raw))))
                    return
                  onChange({ model_url: joinModelUrl(base, raw) })
                }}
                disabled={readonly}
                placeholder={t(`${i18nPrefix}.modelPort.placeholder`, {
                  ns: 'workflow',
                  defaultValue: '8080',
                })}
              />
            </div>
          </div>
          <div className="mt-2 flex items-center gap-2">
            <Button
              variant="secondary"
              size="small"
              type="button"
              disabled={readonly || isProbing || !probeUrl}
              onClick={handleProbeModelInfo}
            >
              {isProbing
                ? t(`${i18nPrefix}.probeModel.loading`, {
                    ns: 'workflow',
                    defaultValue: 'Fetching…',
                  })
                : t(`${i18nPrefix}.probeModel.action`, {
                    ns: 'workflow',
                    defaultValue: 'Fetch model info',
                  })}
            </Button>
            {probeError && (
              <span
                role="status"
                className="system-xs-regular text-text-destructive"
                data-testid="probe-error"
              >
                {t(`${i18nPrefix}.probeModel.errorPrefix`, {
                  ns: 'workflow',
                  defaultValue: 'Probe failed:',
                })}
                {' '}
                {probeError}
              </span>
            )}
            {probeOk && !probeError && !isProbing && (
              <span
                role="status"
                className="system-xs-regular text-text-success"
                data-testid="probe-ok"
              >
                {t(`${i18nPrefix}.probeModel.success`, {
                  ns: 'workflow',
                  defaultValue: 'Filled from server.',
                })}
              </span>
            )}
          </div>
        </div>
      </Field>

      <Field
        title={t(`${i18nPrefix}.eos.label`, { ns: 'workflow' })}
        tooltip={t(`${i18nPrefix}.eos.tooltip`, { ns: 'workflow' })}
        required
      >
        <Input
          value={value.EOS ?? ''}
          onChange={handleText('EOS')}
          disabled={readonly}
          placeholder={t(`${i18nPrefix}.eos.placeholder`, {
            ns: 'workflow',
            defaultValue: '<|eot_id|>',
          })}
        />
      </Field>

      {isLlamaCpp && (
        <Field
          title={t(`${i18nPrefix}.modelArch.label`, { ns: 'workflow' })}
          tooltip={t(`${i18nPrefix}.modelArch.tooltip`, { ns: 'workflow' })}
        >
          <Input
            value={value.model_arch ?? ''}
            onChange={handleText('model_arch')}
            disabled={readonly}
            placeholder={t(`${i18nPrefix}.modelArch.placeholder`, {
              ns: 'workflow',
              defaultValue: 'llama',
            })}
          />
        </Field>
      )}

      {isLlamaCpp && (
        <Field
          title={t(`${i18nPrefix}.type.label`, { ns: 'workflow' })}
          tooltip={t(`${i18nPrefix}.type.tooltip`, { ns: 'workflow' })}
        >
          <DropdownMenu open={typeOpen} onOpenChange={setTypeOpen}>
            <DropdownMenuTrigger
              disabled={readonly}
              className={cn(
                'flex w-full items-center justify-between rounded-lg bg-components-input-bg-normal px-3 py-2',
                readonly
                  ? 'cursor-not-allowed bg-components-input-bg-disabled!'
                  : 'cursor-pointer hover:bg-state-base-hover-alt',
                typeOpen && 'bg-state-base-hover-alt',
              )}
            >
              <span className="truncate system-sm-regular text-components-input-text-filled">
                {t(`${i18nPrefix}.type.${value.type ?? 'normal'}`, {
                  ns: 'workflow',
                  defaultValue: value.type ?? 'normal',
                })}
              </span>
              <span
                aria-hidden
                className={cn(
                  'i-ri-arrow-down-s-line h-4 w-4 text-text-quaternary',
                  typeOpen && 'text-text-secondary',
                )}
              />
            </DropdownMenuTrigger>
            <DropdownMenuContent placement="bottom-start" sideOffset={4}>
              <DropdownMenuItem onClick={() => handleTypePick('normal')}>
                <span className="grow px-1 system-sm-medium text-text-secondary">
                  {t(`${i18nPrefix}.type.normal`, {
                    ns: 'workflow',
                    defaultValue: 'normal',
                  })}
                </span>
                {value.type === 'normal' && (
                  <span aria-hidden className="i-ri-check-line h-4 w-4 text-text-accent" />
                )}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleTypePick('think')}>
                <span className="grow px-1 system-sm-medium text-text-secondary">
                  {t(`${i18nPrefix}.type.think`, {
                    ns: 'workflow',
                    defaultValue: 'think',
                  })}
                </span>
                {value.type === 'think' && (
                  <span aria-hidden className="i-ri-check-line h-4 w-4 text-text-accent" />
                )}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </Field>
      )}

      {isLlamaCpp && value.type === 'think' && (
        <Field
          title={t(`${i18nPrefix}.stopThink.label`, { ns: 'workflow' })}
          tooltip={t(`${i18nPrefix}.stopThink.tooltip`, { ns: 'workflow' })}
        >
          <Input
            value={value.stop_think ?? ''}
            onChange={handleOptionalText('stop_think')}
            disabled={readonly}
            placeholder={t(`${i18nPrefix}.stopThink.placeholder`, {
              ns: 'workflow',
              defaultValue: '</think>',
            })}
          />
        </Field>
      )}

      {isLlamaCpp && (
        <Field
          title={t(`${i18nPrefix}.exposeRawLogits.label`, { ns: 'workflow' })}
          tooltip={t(`${i18nPrefix}.exposeRawLogits.tooltip`, { ns: 'workflow' })}
        >
          <Switch
            checked={!!value.expose_raw_logits}
            onCheckedChange={(next: boolean) => onChange({ expose_raw_logits: next })}
            size="md"
            disabled={readonly}
          />
        </Field>
      )}

      {isBuiltInCompletionBackend && !isLlamaCpp && (
        <div className="system-xs-regular text-text-tertiary">
          {t(`${i18nPrefix}.backend.vllmHint`, {
            ns: 'workflow',
            defaultValue:
              'vLLM backends use OpenAI-compatible endpoints. Use vllm for raw /v1/completions and vllm_chat for /v1/chat/completions.',
          })}
        </div>
      )}

      <Field
        title={t(`${i18nPrefix}.requestTimeout.label`, { ns: 'workflow' })}
        tooltip={t(`${i18nPrefix}.requestTimeout.tooltip`, { ns: 'workflow' })}
      >
        <Input
          type="number"
          min={1}
          step={100}
          value={value.request_timeout_ms ?? ''}
          onChange={handleNumber('request_timeout_ms', true)}
          disabled={readonly}
          placeholder={t(`${i18nPrefix}.requestTimeout.placeholder`, {
            ns: 'workflow',
            defaultValue: '30000',
          })}
        />
      </Field>
      {/* Per-source ensemble weight is configured on the consumer side
         ``ParallelEnsembleConfig.token_sources[].weight`` (see
         api/core/workflow/nodes/parallel_ensemble/node.py:_resolve_weights);
         the inline spec's ``weight`` field would never be read at run
         time, so surfacing it here would only mislead. */}
    </div>
  )
}

export default React.memo(InlineSpecForm)

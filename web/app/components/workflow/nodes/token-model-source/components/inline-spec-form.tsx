'use client'
// Form for the "Custom model" mode (inline_spec). Backend-specific
// fields below are tuned for ``llama_cpp`` because that is the only
// registered backend today. Adding a second backend means: (1)
// register it server-side (api/core/workflow/nodes/parallel_ensemble/
// backends/), (2) extend ``KNOWN_BACKENDS`` here, and (3) branch the
// fields render on ``backend`` if the spec class needs different
// inputs. The server-side ``BackendRegistry.get_spec_class(...)``
// validates the payload either way, so a typo'd backend name fails
// loudly at run time even without a frontend edit.
import type { ChangeEvent, FC } from 'react'
import type { InlineModelSpec } from '../types'
import { cn } from '@langgenius/dify-ui/cn'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@langgenius/dify-ui/dropdown-menu'
import { Switch } from '@langgenius/dify-ui/switch'
import * as React from 'react'
import { useCallback, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Input from '@/app/components/base/input'
import Field from '@/app/components/workflow/nodes/_base/components/field'

const i18nPrefix = 'nodes.tokenModelSource.inlineSpec'

// Backends registered server-side today. Kept as a static list because
// only ``llama_cpp`` is implemented; a /backends endpoint would be a
// premature abstraction with one entry. Each row carries a label
// override path so the dropdown can show a friendlier name than the
// raw registry key without the user noticing the gap.
const KNOWN_BACKENDS: ReadonlyArray<{ id: string, labelKey: string }> = [
  { id: 'llama_cpp', labelKey: `${i18nPrefix}.backends.llamaCpp` },
]

type Props = {
  readonly: boolean
  value: InlineModelSpec
  onChange: (patch: Partial<InlineModelSpec>) => void
}

const InlineSpecForm: FC<Props> = ({ readonly, value, onChange }) => {
  const { t } = useTranslation()
  const [backendOpen, setBackendOpen] = useState(false)
  const [typeOpen, setTypeOpen] = useState(false)

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
      onChange({ backend: id })
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
        <Input
          value={value.model_url ?? ''}
          onChange={handleText('model_url')}
          disabled={readonly}
          placeholder={t(`${i18nPrefix}.modelUrl.placeholder`, {
            ns: 'workflow',
            defaultValue: 'http://127.0.0.1:8080',
          })}
        />
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

      {value.type === 'think' && (
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

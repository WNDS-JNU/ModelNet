import type { InlineModelSpec } from '../../types'
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import * as React from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { post } from '@/service/base'
import { DEFAULT_INLINE_SPEC } from '../../types'
import InlineSpecForm from '../inline-spec-form'

// The probe button now goes through the server-side
// ``/console/api/workflow/probe-model-info`` endpoint to bypass CORS
// on hosted OpenAI-compatible servers (vLLM / TGI / SGLang / etc.).
// Mock the Dify ``post`` helper so each case can pin a specific
// upstream-shaped response / failure mode without a real network call.
vi.mock('@/service/base', () => ({
  post: vi.fn(),
}))
const mockedPost = post as unknown as ReturnType<typeof vi.fn>

// dify-ui DropdownMenu / Switch render inline in the test env via the
// FloatingPortal stub from ``vitest.setup.ts`` — no extra portal-root
// wiring needed here. Mirrors the model-alias-select test pattern.

const buildValue = (overrides: Partial<InlineModelSpec> = {}): InlineModelSpec => ({
  ...DEFAULT_INLINE_SPEC,
  ...overrides,
})

const renderForm = (overrides: Partial<{
  readonly: boolean
  value: InlineModelSpec
  onChange: (patch: Partial<InlineModelSpec>) => void
}> = {}) => {
  const onChange = overrides.onChange ?? vi.fn()
  const result = render(
    <InlineSpecForm
      readonly={overrides.readonly ?? false}
      value={overrides.value ?? buildValue()}
      onChange={onChange}
    />,
  )
  return { ...result, onChange }
}

// Each ``Field`` wraps its content below the title row in a sibling
// div, so ``getByText(title)`` returns the title node (no input child)
// and a simple ``closest`` walk overshoots. Query inputs by their
// placeholder instead — the form ships distinctive ``defaultValue``
// placeholders the i18n stub forwards verbatim into the rendered
// attribute, so a regex against the placeholder substring is unique
// per field.
const inputByPlaceholder = (placeholderKey: RegExp): HTMLInputElement => {
  return screen.getByPlaceholderText(placeholderKey) as HTMLInputElement
}

describe('token-model-source/inline-spec-form', () => {
  describe('Rendering', () => {
    it('renders all required fields with the expected placeholders', () => {
      renderForm({
        value: buildValue({
          model_name: 'llama-3.1-8b',
          model_url: 'http://127.0.0.1:8080',
          EOS: '<|eot_id|>',
        }),
      })
      // model_name + model_url + model_port + EOS + model_arch +
      // request_timeout — six distinct placeholders the i18n stub
      // renders into the ``placeholder`` attribute. Asserting *which*
      // placeholders exist beats counting raw inputs (other primitives
      // like the dify-ui Switch can render their own internal input
      // nodes).
      expect(screen.getByPlaceholderText(/modelName\.placeholder/)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/modelUrl\.placeholder/)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/modelPort\.placeholder/)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/eos\.placeholder/)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/modelArch\.placeholder/)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/requestTimeout\.placeholder/)).toBeInTheDocument()
    })

    it('renders the dropdown trigger labelled with the current backend', () => {
      renderForm({ value: buildValue({ backend: 'llama_cpp' }) })
      // The label-key returned by the i18n stub is
      // ``workflow.nodes.tokenModelSource.inlineSpec.backends.llamaCpp``
      // — substring-match the suffix for stability.
      expect(screen.getByText(/inlineSpec\.backends\.llamaCpp/)).toBeInTheDocument()
    })

    it('omits stop_think when type=normal', () => {
      renderForm({ value: buildValue({ type: 'normal' }) })
      // Each Field's label text contains its i18n key; absence of the
      // stop-think label proves the Field did not render.
      expect(screen.queryByText(/inlineSpec\.stopThink/)).not.toBeInTheDocument()
    })

    it('renders stop_think input when type=think', () => {
      renderForm({ value: buildValue({ type: 'think', stop_think: '</think>' }) })
      expect(screen.getByText(/inlineSpec\.stopThink/)).toBeInTheDocument()
    })

    it('disables all controls when readonly=true', () => {
      const { container } = renderForm({ readonly: true })
      // Every form-bearing element should be disabled — inputs,
      // dropdown triggers, and the switch.
      container.querySelectorAll('input').forEach((i) => {
        expect((i as HTMLInputElement).disabled).toBe(true)
      })
      container.querySelectorAll('button').forEach((b) => {
        expect((b as HTMLButtonElement).disabled).toBe(true)
      })
    })
  })

  describe('Text field patches', () => {
    it('patches model_name on text change', () => {
      const { onChange } = renderForm()
      fireEvent.change(inputByPlaceholder(/modelName\.placeholder/), {
        target: { value: 'llama-3.1-8b' },
      })
      expect(onChange).toHaveBeenLastCalledWith({ model_name: 'llama-3.1-8b' })
    })

    it('patches the URL host (model_url base) without a port pinned', () => {
      // Empty starting URL → port is also empty → composed URL is
      // the typed host verbatim, no synthetic ``:`` slipped in.
      const { onChange } = renderForm({ value: buildValue({ model_url: '' }) })
      fireEvent.change(inputByPlaceholder(/modelUrl\.placeholder/), {
        target: { value: 'http://localhost' },
      })
      expect(onChange).toHaveBeenLastCalledWith({ model_url: 'http://localhost' })
    })

    it('preserves the existing port when only the URL host is edited', () => {
      // Round-trip case: user already pinned :8080 and is changing
      // the host. The composer must reinsert the same port — without
      // it the saved URL would silently lose the port.
      const { onChange } = renderForm({
        value: buildValue({ model_url: 'http://219.222.20.79:8080' }),
      })
      fireEvent.change(inputByPlaceholder(/modelUrl\.placeholder/), {
        target: { value: 'http://otherhost' },
      })
      expect(onChange).toHaveBeenLastCalledWith({ model_url: 'http://otherhost:8080' })
    })

    it('patches EOS verbatim — including angle-bracket markers', () => {
      const { onChange } = renderForm()
      fireEvent.change(inputByPlaceholder(/eos\.placeholder/), {
        target: { value: '<|eot_id|>' },
      })
      expect(onChange).toHaveBeenLastCalledWith({ EOS: '<|eot_id|>' })
    })

    it('preserves empty string for required text fields (no auto-coerce to null)', () => {
      // Required fields keep ``""`` so the panel red-line surfaces the
      // missing value — coercing to null would silently swallow the
      // bug and let the user save an incomplete config.
      const { onChange } = renderForm({
        value: buildValue({ model_name: 'old-name' }),
      })
      fireEvent.change(inputByPlaceholder(/modelName\.placeholder/), {
        target: { value: '' },
      })
      expect(onChange).toHaveBeenLastCalledWith({ model_name: '' })
    })

    it('coerces empty stop_think to null (optional field, server treats null = unset)', () => {
      const { onChange } = renderForm({
        value: buildValue({ type: 'think', stop_think: '</think>' }),
      })
      fireEvent.change(inputByPlaceholder(/stopThink\.placeholder/), {
        target: { value: '' },
      })
      expect(onChange).toHaveBeenLastCalledWith({ stop_think: null })
    })
  })

  describe('Port input — composed with the URL host', () => {
    // The panel surfaces URL + port as two separate boxes but writes
    // a single ``model_url`` string to the wire (LlamaCppSpec.model_url
    // is ``AnyUrl`` server-side). Pin the composition rules here so a
    // future edit can't silently drop a colon, lose the port, or
    // generate a URL pydantic would 422 on.
    const portInput = () => inputByPlaceholder(/modelPort\.placeholder/)

    it('renders the parsed port from a stored URL with one', () => {
      renderForm({ value: buildValue({ model_url: 'http://219.222.20.79:8080' }) })
      expect((portInput() as HTMLInputElement).value).toBe('8080')
    })

    it('renders empty port for a URL without one', () => {
      renderForm({ value: buildValue({ model_url: 'http://219.222.20.79' }) })
      expect((portInput() as HTMLInputElement).value).toBe('')
    })

    it('appends a port to a URL that did not have one', () => {
      const { onChange } = renderForm({
        value: buildValue({ model_url: 'http://219.222.20.79' }),
      })
      fireEvent.change(portInput(), { target: { value: '9000' } })
      expect(onChange).toHaveBeenLastCalledWith({ model_url: 'http://219.222.20.79:9000' })
    })

    it('replaces an existing port when the port box changes', () => {
      const { onChange } = renderForm({
        value: buildValue({ model_url: 'http://219.222.20.79:8080' }),
      })
      fireEvent.change(portInput(), { target: { value: '9000' } })
      expect(onChange).toHaveBeenLastCalledWith({ model_url: 'http://219.222.20.79:9000' })
    })

    it('clearing the port drops it from the composed URL', () => {
      const { onChange } = renderForm({
        value: buildValue({ model_url: 'http://219.222.20.79:8080' }),
      })
      fireEvent.change(portInput(), { target: { value: '' } })
      expect(onChange).toHaveBeenLastCalledWith({ model_url: 'http://219.222.20.79' })
    })

    it('does not emit for fractional port input (integer-only)', () => {
      const { onChange } = renderForm({
        value: buildValue({ model_url: 'http://219.222.20.79:8080' }),
      })
      fireEvent.change(portInput(), { target: { value: '80.5' } })
      expect(onChange).not.toHaveBeenCalled()
    })

    it('preserves a user-typed path when composing port', () => {
      // Edge case: user added a path to the URL box. The composer
      // must reinsert the port between scheme://host and the path,
      // not append it after the path (which would produce invalid
      // URLs).
      const { onChange } = renderForm({
        value: buildValue({ model_url: 'http://219.222.20.79/v1' }),
      })
      fireEvent.change(portInput(), { target: { value: '8080' } })
      expect(onChange).toHaveBeenLastCalledWith({
        model_url: 'http://219.222.20.79:8080/v1',
      })
    })
  })

  describe('Type dropdown — think/normal toggle', () => {
    // Each ``DropdownMenuItem`` renders its label text directly in
    // jsdom (via the FloatingPortal stub). Click the trigger, then
    // the row by its label.

    const openTypeMenu = () => {
      // The type trigger is the second dropdown trigger in the form
      // (backend is first). Both render as buttons before the menu
      // opens; pick the one labelled with ``inlineSpec.type``. The
      // i18n stub formats labels as ``<key>:<json-opts>``, so anchor
      // the regex with a backslash-colon (rather than ``$``) to
      // match only the trigger row, not menu rows that may share
      // the label.
      const triggerLabel = screen.getByText(/inlineSpec\.type\.(normal|think):/)
      const trigger = triggerLabel.closest('button') as HTMLButtonElement
      fireEvent.click(trigger)
    }

    it('switching to think emits { type: "think" } without touching stop_think', () => {
      const { onChange } = renderForm({ value: buildValue({ type: 'normal' }) })
      openTypeMenu()
      // The menu surfaces the same labels — narrow by walking the
      // menuitem ancestor of the "think" option (the trigger row also
      // renders that text when the current selection is think).
      const thinkLabel = screen
        .getAllByText(/inlineSpec\.type\.think/)
        .find(el => el.closest('[role="menuitem"]'))
      expect(thinkLabel).toBeDefined()
      fireEvent.click(thinkLabel!.closest('[role="menuitem"]') as HTMLElement)
      expect(onChange).toHaveBeenLastCalledWith({ type: 'think' })
    })

    it('switching to normal also drops stop_think to null', () => {
      // Switching away from think must clear stop_think so a stale
      // value cannot bleed back through if the user toggles modes.
      const { onChange } = renderForm({
        value: buildValue({ type: 'think', stop_think: '</think>' }),
      })
      openTypeMenu()
      const normalLabel = screen
        .getAllByText(/inlineSpec\.type\.normal/)
        .find(el => el.closest('[role="menuitem"]'))
      fireEvent.click(normalLabel!.closest('[role="menuitem"]') as HTMLElement)
      expect(onChange).toHaveBeenLastCalledWith({ type: 'normal', stop_think: null })
    })
  })

  describe('Numeric coercion — request_timeout_ms', () => {
    const timeoutInput = () =>
      inputByPlaceholder(/requestTimeout\.placeholder/)

    it('emits a number for valid positive integer input', () => {
      const { onChange } = renderForm()
      fireEvent.change(timeoutInput(), { target: { value: '60000' } })
      expect(onChange).toHaveBeenLastCalledWith({ request_timeout_ms: 60000 })
    })

    it('emits undefined when the input is cleared', () => {
      const { onChange } = renderForm({
        value: buildValue({ request_timeout_ms: 30000 }),
      })
      fireEvent.change(timeoutInput(), { target: { value: '' } })
      expect(onChange).toHaveBeenLastCalledWith({ request_timeout_ms: undefined })
    })

    it('does not emit for fractional input (integer-only)', () => {
      const { onChange } = renderForm()
      fireEvent.change(timeoutInput(), { target: { value: '1500.5' } })
      expect(onChange).not.toHaveBeenCalled()
    })

    it('does not emit a garbage number for non-numeric input', () => {
      // jsdom <input type="number"> coerces non-numeric strings to ''
      // before they reach onChange, so the change event we observe
      // here carries ``value=""``. That fires the "empty" branch
      // which intentionally emits ``undefined``. The pin we want
      // here is "no garbage number lands on the patch" — i.e. no
      // ``NaN`` and no string slip-through.
      const onChange = vi.fn()
      renderForm({ onChange })
      fireEvent.change(timeoutInput(), { target: { value: 'abc' } })
      // Whether or not the browser fires change, the payload must
      // never carry a finite-non-integer ``request_timeout_ms``.
      for (const call of onChange.mock.calls) {
        const patch = call[0] as { request_timeout_ms?: unknown }
        if ('request_timeout_ms' in patch) {
          expect(
            patch.request_timeout_ms === undefined
            || (
              typeof patch.request_timeout_ms === 'number'
              && Number.isInteger(patch.request_timeout_ms)
              && patch.request_timeout_ms > 0
            ),
          ).toBe(true)
        }
      }
    })
  })

  describe('Expose-raw-logits switch', () => {
    // dify-ui ``Switch`` renders as a ``role="switch"`` button.
    // ``onCheckedChange`` fires on click; we assert the patch.
    it('toggles expose_raw_logits on click', () => {
      const { onChange } = renderForm({
        value: buildValue({ expose_raw_logits: false }),
      })
      const sw = screen.getByRole('switch')
      fireEvent.click(sw)
      expect(onChange).toHaveBeenLastCalledWith({ expose_raw_logits: true })
    })

    it('reflects the current value via aria-checked', () => {
      renderForm({ value: buildValue({ expose_raw_logits: true }) })
      const sw = screen.getByRole('switch')
      expect(sw.getAttribute('aria-checked')).toBe('true')
    })
  })

  describe('Weight field — should NOT exist', () => {
    // Per design, runtime weight is configured on the consumer
    // (``ParallelEnsembleConfig.token_sources[].weight``); the inline
    // spec's ``weight`` would be dead code. Pin the absence so a
    // future edit can't silently bring it back and create two
    // overlapping knobs.
    it('does not render a weight input', () => {
      renderForm()
      expect(screen.queryByText(/inlineSpec\.weight/)).not.toBeInTheDocument()
    })
  })

  describe('Probe model info button', () => {
    // The button hands the raw ``model_url`` to the console endpoint
    // ``/workflow/probe-model-info``; the server constructs the
    // ``/v1/models`` URL and proxies via ssrf_proxy so CORS-blocked
    // backends (vLLM / TGI / hosted routers) work the same as
    // llama.cpp. These tests mock the Dify ``post`` helper so each
    // case can pin a specific upstream-shaped response without a
    // real network call; the URL-building logic itself lives
    // server-side and is verified in the backend test suite.

    const probeButton = () =>
      screen.getByRole('button', { name: /probeModel\.(action|loading)/ })

    // Build a ``Response`` body that mirrors Dify's BaseHTTPException
    // serialisation (``{code, message, status}``), since the frontend
    // unwraps ``message`` from a rejected ``Response`` to populate the
    // error banner. Generic non-Response rejects fall through to the
    // ``e instanceof Error`` branch.
    const httpErrorResponse = (status: number, message: string) =>
      new Response(JSON.stringify({ code: 'probe_model_upstream_error', message, status }), {
        status,
        headers: { 'Content-Type': 'application/json' },
      })

    beforeEach(() => {
      mockedPost.mockReset()
      // Default to a happy server that returns the user's example
      // payload shape (server already pulled ``data[0].id``).
      mockedPost.mockResolvedValue({ model_name: 'Llama-3.1-8B-Instruct-Q8_0.gguf' })
    })

    it('is disabled when the URL is blank', () => {
      renderForm({ value: buildValue({ model_url: '' }) })
      expect((probeButton() as HTMLButtonElement).disabled).toBe(true)
    })

    it('is disabled when the URL is not a well-formed http(s) URL', () => {
      renderForm({ value: buildValue({ model_url: 'not-a-url' }) })
      expect((probeButton() as HTMLButtonElement).disabled).toBe(true)
    })

    it('is enabled when the URL has a scheme + host (no port)', () => {
      // A bare ``http://host`` is still a valid URL — the user may
      // be running llama.cpp on the default port 80 or behind a
      // reverse proxy. The probe target ``${url}/v1/models`` is
      // still well-formed server-side, so the button stays enabled.
      renderForm({ value: buildValue({ model_url: 'http://219.222.20.79' }) })
      expect((probeButton() as HTMLButtonElement).disabled).toBe(false)
    })

    it('is disabled while readonly', () => {
      renderForm({ readonly: true })
      expect((probeButton() as HTMLButtonElement).disabled).toBe(true)
    })

    it('POSTs the raw model_url to the console endpoint and dispatches model_name', async () => {
      const { onChange } = renderForm({
        value: buildValue({ model_url: 'http://219.222.20.79:30834' }),
      })
      await act(async () => {
        fireEvent.click(probeButton())
      })
      expect(mockedPost).toHaveBeenCalledWith(
        '/workflow/probe-model-info',
        { body: { url: 'http://219.222.20.79:30834' } },
        // ``silent: true`` blocks the global error toast so the inline
        // banner is the sole error surface — pin so a future refactor
        // can't drop it and accidentally double-notify.
        { silent: true },
      )
      await waitFor(() => {
        expect(onChange).toHaveBeenCalledWith({
          model_name: 'Llama-3.1-8B-Instruct-Q8_0.gguf',
        })
      })
      // Success banner replaces the loading state once the promise
      // resolves; pin so a future refactor can't silently drop the
      // user feedback.
      expect(screen.getByTestId('probe-ok')).toBeInTheDocument()
    })

    it('dispatches EOS when the probe endpoint resolves it from the registry', async () => {
      mockedPost.mockResolvedValue({
        model_name: 'meta-llama-31-8b-instruct-q80',
        EOS: '<|end_of_text|>',
      })
      const { onChange } = renderForm({
        value: buildValue({ model_url: 'http://219.222.20.79:30834' }),
      })

      await act(async () => {
        fireEvent.click(probeButton())
      })

      await waitFor(() => {
        expect(onChange).toHaveBeenCalledWith({
          model_name: 'meta-llama-31-8b-instruct-q80',
          EOS: '<|end_of_text|>',
        })
      })
    })

    it('forwards a hosted-router URL verbatim (path prefix preserved on the wire)', async () => {
      // The server is responsible for appending ``/v1/models`` while
      // preserving any path prefix (e.g. ``/tencent/Hunyuan…``). The
      // frontend's only job is to hand over the raw model_url unchanged
      // — pin that contract so a future refactor doesn't start
      // mangling the URL client-side and double-process it.
      renderForm({
        value: buildValue({
          model_url: 'https://inference.cluster.aimodelnetwork.cn/tencent/Hunyuan-7B-Instruct-AWQ-Int4',
        }),
      })
      await act(async () => {
        fireEvent.click(probeButton())
      })
      expect(mockedPost).toHaveBeenCalledWith(
        '/workflow/probe-model-info',
        { body: { url: 'https://inference.cluster.aimodelnetwork.cn/tencent/Hunyuan-7B-Instruct-AWQ-Int4' } },
        { silent: true },
      )
    })

    it('surfaces the upstream error message when the server rejects with a Response', async () => {
      mockedPost.mockRejectedValue(httpErrorResponse(502, 'HTTP 503 from upstream'))
      const { onChange } = renderForm({
        value: buildValue({ model_url: 'http://219.222.20.79:30834' }),
      })
      await act(async () => {
        fireEvent.click(probeButton())
      })
      await waitFor(() => {
        expect(screen.getByTestId('probe-error')).toHaveTextContent(/HTTP 503 from upstream/)
      })
      // No model_name update when the probe failed.
      expect(onChange).not.toHaveBeenCalled()
    })

    it('surfaces "no model in response" when the server reports an empty list', async () => {
      mockedPost.mockRejectedValue(httpErrorResponse(502, 'no model in response'))
      const { onChange } = renderForm({
        value: buildValue({ model_url: 'http://219.222.20.79:30834' }),
      })
      await act(async () => {
        fireEvent.click(probeButton())
      })
      await waitFor(() => {
        expect(screen.getByTestId('probe-error')).toHaveTextContent(/no model/i)
      })
      expect(onChange).not.toHaveBeenCalled()
    })

    it('surfaces an error banner when post rejects with a plain Error (network down)', async () => {
      mockedPost.mockRejectedValue(new Error('network down'))
      renderForm({
        value: buildValue({ model_url: 'http://219.222.20.79:30834' }),
      })
      await act(async () => {
        fireEvent.click(probeButton())
      })
      await waitFor(() => {
        expect(screen.getByTestId('probe-error')).toHaveTextContent(/network down/)
      })
    })

    it('falls back to HTTP <status> when the error Response body has no message', async () => {
      // Edge case — a proxy / gateway in front of the console might
      // strip the JSON body. The user still deserves a non-empty
      // signal, so the frontend synthesises ``HTTP <status>`` from
      // the Response's status code.
      mockedPost.mockRejectedValue(new Response('', { status: 504 }))
      renderForm({
        value: buildValue({ model_url: 'http://219.222.20.79:30834' }),
      })
      await act(async () => {
        fireEvent.click(probeButton())
      })
      await waitFor(() => {
        expect(screen.getByTestId('probe-error')).toHaveTextContent(/HTTP 504/)
      })
    })

    it('clears any prior error on a successful retry', async () => {
      // First probe fails, second succeeds — the error banner must
      // come down on the success, otherwise the user gets stale
      // negative feedback after a correct retry.
      mockedPost
        .mockRejectedValueOnce(httpErrorResponse(502, 'HTTP 500 from upstream'))
        .mockResolvedValueOnce({ model_name: 'retry-model' })

      renderForm({ value: buildValue({ model_url: 'http://219.222.20.79:30834' }) })
      await act(async () => {
        fireEvent.click(probeButton())
      })
      await waitFor(() => {
        expect(screen.getByTestId('probe-error')).toBeInTheDocument()
      })
      await act(async () => {
        fireEvent.click(probeButton())
      })
      await waitFor(() => {
        expect(screen.queryByTestId('probe-error')).not.toBeInTheDocument()
        expect(screen.getByTestId('probe-ok')).toBeInTheDocument()
      })
    })
  })
})

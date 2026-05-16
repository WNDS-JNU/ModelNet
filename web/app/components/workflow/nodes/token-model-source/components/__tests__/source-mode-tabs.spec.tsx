import type { SourceMode } from '../../use-config'
import { fireEvent, render, screen } from '@testing-library/react'
import * as React from 'react'
import { describe, expect, it, vi } from 'vitest'
import SourceModeTabs from '../source-mode-tabs'

const renderTabs = (overrides: Partial<{
  readonly: boolean
  value: SourceMode
  onChange: (mode: SourceMode) => void
}> = {}) => {
  const onChange = overrides.onChange ?? vi.fn()
  const result = render(
    <SourceModeTabs
      readonly={overrides.readonly ?? false}
      value={overrides.value ?? 'registered'}
      onChange={onChange}
    />,
  )
  return { ...result, onChange }
}

// The i18n stub returns ``<ns>.<key>:<json-opts>`` for keys with
// options; tab labels carry a ``defaultValue`` opt so the labels are
// stable substrings the tests can key off.
const registeredTab = () =>
  screen.getByText(/sourceMode\.registered:/).closest('button') as HTMLButtonElement
const inlineTab = () =>
  screen.getByText(/sourceMode\.inline:/).closest('button') as HTMLButtonElement

describe('token-model-source/source-mode-tabs', () => {
  describe('Rendering', () => {
    it('renders exactly two tabs (registered + inline)', () => {
      const { container } = renderTabs()
      const buttons = container.querySelectorAll('button')
      expect(buttons).toHaveLength(2)
    })

    it('renders both label keys with the correct i18n prefix', () => {
      renderTabs()
      expect(screen.getByText(/sourceMode\.registered/)).toBeInTheDocument()
      expect(screen.getByText(/sourceMode\.inline/)).toBeInTheDocument()
    })
  })

  describe('Active state', () => {
    // The active tab carries the accent text colour class; the
    // inactive tab carries the tertiary colour. Pin both so a future
    // refactor can't silently swap the visual signal.

    it('applies the accent style to the registered tab when value=registered', () => {
      renderTabs({ value: 'registered' })
      expect(registeredTab().className).toMatch(/text-text-accent/)
      expect(inlineTab().className).toMatch(/text-text-tertiary/)
    })

    it('applies the accent style to the inline tab when value=inline', () => {
      renderTabs({ value: 'inline' })
      expect(inlineTab().className).toMatch(/text-text-accent/)
      expect(registeredTab().className).toMatch(/text-text-tertiary/)
    })
  })

  describe('Click → onChange', () => {
    it('emits "inline" when the inline tab is clicked from registered', () => {
      const { onChange } = renderTabs({ value: 'registered' })
      fireEvent.click(inlineTab())
      expect(onChange).toHaveBeenCalledTimes(1)
      expect(onChange).toHaveBeenCalledWith('inline')
    })

    it('emits "registered" when the registered tab is clicked from inline', () => {
      const { onChange } = renderTabs({ value: 'inline' })
      fireEvent.click(registeredTab())
      expect(onChange).toHaveBeenCalledTimes(1)
      expect(onChange).toHaveBeenCalledWith('registered')
    })

    it('does not emit when the already-active tab is clicked again', () => {
      // No-op clicks shouldn't churn the parent's setInputs path —
      // every onChange re-renders the panel, which is wasteful for
      // a no-op transition.
      const { onChange } = renderTabs({ value: 'registered' })
      fireEvent.click(registeredTab())
      expect(onChange).not.toHaveBeenCalled()
    })
  })

  describe('Readonly', () => {
    it('disables both tabs when readonly=true', () => {
      renderTabs({ readonly: true })
      expect(registeredTab().disabled).toBe(true)
      expect(inlineTab().disabled).toBe(true)
    })

    it('does not emit on click when readonly=true (HTML disabled semantics)', () => {
      // The ``button`` element's ``disabled`` attribute should
      // block clicks at the DOM level; this assertion guards against
      // a future change that swapped ``button`` for a ``div``
      // without re-implementing the gate.
      const { onChange } = renderTabs({ readonly: true })
      fireEvent.click(inlineTab())
      expect(onChange).not.toHaveBeenCalled()
    })
  })
})

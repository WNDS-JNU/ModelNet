import type { BackendInfo } from '../../parallel-ensemble/types'
import type { TokenModelSourceNodeType } from '../types'
import { renderHook } from '@testing-library/react'
import { BlockEnum } from '@/app/components/workflow/types'
import { createNodeCrudModuleMock } from '../../__tests__/use-config-test-utils'
import { DEFAULT_INLINE_SPEC, DEFAULT_SAMPLING_PARAMS } from '../types'
import useConfig from '../use-config'

const mockSetInputs = vi.hoisted(() => vi.fn())
const mockUseLocalModels = vi.hoisted(() => vi.fn())

vi.mock('@/app/components/workflow/hooks', () => ({
  useNodesReadOnly: () => ({ nodesReadOnly: false }),
}))

vi.mock('@/app/components/workflow/nodes/_base/hooks/use-node-crud', () => ({
  ...createNodeCrudModuleMock<TokenModelSourceNodeType>(mockSetInputs),
}))

vi.mock('../../parallel-ensemble/use-registries', () => ({
  useLocalModels: () => mockUseLocalModels(),
}))

const createPayload = (
  overrides: Partial<TokenModelSourceNodeType> = {},
): TokenModelSourceNodeType => ({
  title: 'Token Model Source',
  desc: '',
  type: BlockEnum.TokenModelSource,
  model_alias: '',
  prompt_template: 'Answer: {{#start.q#}}',
  sampling_params: { ...DEFAULT_SAMPLING_PARAMS },
  extra: {},
  inline_spec: { ...DEFAULT_INLINE_SPEC },
  ...overrides,
})

describe('token-model-source/useConfig', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUseLocalModels.mockReturnValue({
      data: { models: [] satisfies BackendInfo[] },
      isLoading: false,
    })
  })

  describe('Inline model alias defaults', () => {
    it('should default an empty model_alias to the inline model_name', () => {
      const { result } = renderHook(() => useConfig('token-source', createPayload()))

      result.current.handleInlineSpecChange({ model_name: 'Llama-3.1-8B-Instruct-Q8_0.gguf' })

      expect(mockSetInputs).toHaveBeenCalledWith(expect.objectContaining({
        model_alias: 'Llama-3.1-8B-Instruct-Q8_0.gguf',
        inline_spec: expect.objectContaining({
          model_name: 'Llama-3.1-8B-Instruct-Q8_0.gguf',
        }),
      }))
    })

    it('should keep the derived alias in sync while it still matches the previous model_name', () => {
      const { result } = renderHook(() => useConfig('token-source', createPayload({
        model_alias: 'old-model',
        inline_spec: { ...DEFAULT_INLINE_SPEC, model_name: 'old-model' },
      })))

      result.current.handleInlineSpecChange({ model_name: 'new-model' })

      expect(mockSetInputs).toHaveBeenCalledWith(expect.objectContaining({
        model_alias: 'new-model',
        inline_spec: expect.objectContaining({
          model_name: 'new-model',
        }),
      }))
    })

    it('should preserve a user-provided model_alias when model_name changes', () => {
      const { result } = renderHook(() => useConfig('token-source', createPayload({
        model_alias: 'custom-alias',
        inline_spec: { ...DEFAULT_INLINE_SPEC, model_name: 'old-model' },
      })))

      result.current.handleInlineSpecChange({ model_name: 'new-model' })

      expect(mockSetInputs).toHaveBeenCalledWith(expect.objectContaining({
        model_alias: 'custom-alias',
        inline_spec: expect.objectContaining({
          model_name: 'new-model',
        }),
      }))
    })
  })
})

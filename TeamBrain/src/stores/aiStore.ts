import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

export type AIAction = 'continue' | 'summarize' | 'rewrite' | 'translate' | 'brainstorm'

export interface AIConfig {
  api_key: string
  base_url: string
  model: string
  monthly_budget: number
}

export interface AIUsage {
  total_tokens: number
  budget_limit: number
  month: number
  year: number
}

interface AIState {
  config: AIConfig
  usage: AIUsage | null
  generatedContent: string | null
  generating: boolean
  error: string | null

  setConfig: (config: Partial<AIConfig>) => void
  setUsage: (usage: AIUsage) => void
  setGeneratedContent: (content: string | null) => void
  setGenerating: (generating: boolean) => void
  setError: (error: string | null) => void
  resetGenerated: () => void
}

export const useAIStore = create<AIState>()(
  immer((set) => ({
    config: {
      api_key: '',
      base_url: 'https://api.openai.com/v1',
      model: 'gpt-3.5-turbo',
      monthly_budget: 1000000,
    },
    usage: null,
    generatedContent: null,
    generating: false,
    error: null,

    setConfig: (config) => set((state) => { Object.assign(state.config, config) }),
    setUsage: (usage) => set((state) => { state.usage = usage }),
    setGeneratedContent: (content) => set((state) => { state.generatedContent = content }),
    setGenerating: (generating) => set((state) => { state.generating = generating }),
    setError: (error) => set((state) => { state.error = error }),
    resetGenerated: () => set((state) => {
      state.generatedContent = null
      state.error = null
    }),
  }))
)

import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

export interface SearchResult {
  page_id: string
  page_title: string
  notebook_id: string
  notebook_name: string
  snippet: string
  rank: number
}

interface SearchFilters {
  notebook_id: string | null
  date_from: string | null
  date_to: string | null
  tag: string | null
}

interface SearchState {
  query: string
  results: SearchResult[]
  filters: SearchFilters
  loading: boolean
  error: string | null

  setQuery: (query: string) => void
  setResults: (results: SearchResult[]) => void
  setFilters: (filters: Partial<SearchFilters>) => void
  resetFilters: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearSearch: () => void
}

const defaultFilters: SearchFilters = {
  notebook_id: null,
  date_from: null,
  date_to: null,
  tag: null,
}

export const useSearchStore = create<SearchState>()(
  immer((set) => ({
    query: '',
    results: [],
    filters: { ...defaultFilters },
    loading: false,
    error: null,

    setQuery: (query) => set((state) => { state.query = query }),
    setResults: (results) => set((state) => { state.results = results }),
    setFilters: (filters) => set((state) => { Object.assign(state.filters, filters) }),
    resetFilters: () => set((state) => { state.filters = { ...defaultFilters } }),
    setLoading: (loading) => set((state) => { state.loading = loading }),
    setError: (error) => set((state) => { state.error = error }),
    clearSearch: () => set((state) => {
      state.query = ''
      state.results = []
      state.filters = { ...defaultFilters }
      state.error = null
    }),
  }))
)

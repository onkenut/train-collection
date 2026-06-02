import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

export interface Notebook {
  id: string
  name: string
  icon: string
  cover_color: string
  sort_order: number
  created_at: string
  updated_at: string
}

interface NotebookState {
  notebooks: Notebook[]
  currentNotebookId: string | null
  loading: boolean
  error: string | null
  expandedIds: Set<string>

  setNotebooks: (notebooks: Notebook[]) => void
  setCurrentNotebook: (id: string | null) => void
  addNotebook: (notebook: Notebook) => void
  updateNotebook: (id: string, updates: Partial<Notebook>) => void
  removeNotebook: (id: string) => void
  reorderNotebooks: (ids: string[]) => void
  toggleExpand: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useNotebookStore = create<NotebookState>()(
  immer((set) => ({
    notebooks: [],
    currentNotebookId: null,
    loading: false,
    error: null,
    expandedIds: new Set<string>(),

    setNotebooks: (notebooks) => set((state) => { state.notebooks = notebooks }),
    setCurrentNotebook: (id) => set((state) => { state.currentNotebookId = id }),
    addNotebook: (notebook) => set((state) => { state.notebooks.push(notebook) }),
    updateNotebook: (id, updates) => set((state) => {
      const idx = state.notebooks.findIndex((n) => n.id === id)
      if (idx !== -1) Object.assign(state.notebooks[idx], updates)
    }),
    removeNotebook: (id) => set((state) => {
      state.notebooks = state.notebooks.filter((n) => n.id !== id)
      if (state.currentNotebookId === id) state.currentNotebookId = null
    }),
    reorderNotebooks: (ids) => set((state) => {
      const map = new Map(state.notebooks.map((n) => [n.id, n]))
      state.notebooks = ids.map((id, i) => {
        const n = map.get(id)
        if (n) n.sort_order = i
        return n!
      }).filter(Boolean)
    }),
    toggleExpand: (id) => set((state) => {
      const next = new Set(state.expandedIds)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      state.expandedIds = next
    }),
    setLoading: (loading) => set((state) => { state.loading = loading }),
    setError: (error) => set((state) => { state.error = error }),
  }))
)

import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

export type ViewMode = 'edit' | 'preview' | 'split'

interface EditorState {
  viewMode: ViewMode
  isDirty: boolean
  isSaving: boolean
  aiPanelOpen: boolean
  versionPanelOpen: boolean
  lastSavedAt: string | null

  setViewMode: (mode: ViewMode) => void
  setDirty: (dirty: boolean) => void
  setSaving: (saving: boolean) => void
  toggleAIPanel: () => void
  toggleVersionPanel: () => void
  setAIPanelOpen: (open: boolean) => void
  setVersionPanelOpen: (open: boolean) => void
  setLastSavedAt: (time: string) => void
}

export const useEditorStore = create<EditorState>()(
  immer((set) => ({
    viewMode: 'edit',
    isDirty: false,
    isSaving: false,
    aiPanelOpen: false,
    versionPanelOpen: false,
    lastSavedAt: null,

    setViewMode: (mode) => set((state) => { state.viewMode = mode }),
    setDirty: (dirty) => set((state) => { state.isDirty = dirty }),
    setSaving: (saving) => set((state) => { state.isSaving = saving }),
    toggleAIPanel: () => set((state) => { state.aiPanelOpen = !state.aiPanelOpen }),
    toggleVersionPanel: () => set((state) => { state.versionPanelOpen = !state.versionPanelOpen }),
    setAIPanelOpen: (open) => set((state) => { state.aiPanelOpen = open }),
    setVersionPanelOpen: (open) => set((state) => { state.versionPanelOpen = open }),
    setLastSavedAt: (time) => set((state) => { state.lastSavedAt = time }),
  }))
)

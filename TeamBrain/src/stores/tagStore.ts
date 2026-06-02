import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

export interface Tag {
  id: string
  name: string
  color: string
}

interface TagState {
  tags: Tag[]
  selectedTagId: string | null
  loading: boolean

  setTags: (tags: Tag[]) => void
  setSelectedTag: (id: string | null) => void
  addTag: (tag: Tag) => void
  removeTag: (id: string) => void
  setLoading: (loading: boolean) => void
}

export const useTagStore = create<TagState>()(
  immer((set) => ({
    tags: [],
    selectedTagId: null,
    loading: false,

    setTags: (tags) => set((state) => { state.tags = tags }),
    setSelectedTag: (id) => set((state) => { state.selectedTagId = id }),
    addTag: (tag) => set((state) => { state.tags.push(tag) }),
    removeTag: (id) => set((state) => {
      state.tags = state.tags.filter((t) => t.id !== id)
      if (state.selectedTagId === id) state.selectedTagId = null
    }),
    setLoading: (loading) => set((state) => { state.loading = loading }),
  }))
)

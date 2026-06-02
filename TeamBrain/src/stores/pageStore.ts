import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

export interface Page {
  id: string
  notebook_id: string
  parent_id: string | null
  title: string
  icon: string
  sort_order: number
  is_template: boolean
  metadata: Record<string, string>
  created_at: string
  updated_at: string
}

export interface Block {
  id: string
  page_id: string
  type: string
  content: string
  properties: Record<string, any>
  sort_order: number
  parent_block_id: string | null
  created_at: string
  updated_at: string
}

interface PageState {
  pages: Page[]
  currentPageId: string | null
  currentBlocks: Block[]
  loading: boolean
  error: string | null

  setPages: (pages: Page[]) => void
  setCurrentPage: (id: string | null) => void
  setBlocks: (blocks: Block[]) => void
  addPage: (page: Page) => void
  updatePage: (id: string, updates: Partial<Page>) => void
  removePage: (id: string) => void
  movePage: (id: string, parentId: string | null, sortOrder: number) => void
  updateBlock: (id: string, updates: Partial<Block>) => void
  addBlock: (block: Block) => void
  removeBlock: (id: string) => void
  reorderBlocks: (pageId: string, blockIds: string[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  getChildren: (parentId: string | null) => Page[]
}

export const usePageStore = create<PageState>()(
  immer((set, get) => ({
    pages: [],
    currentPageId: null,
    currentBlocks: [],
    loading: false,
    error: null,

    setPages: (pages) => set((state) => { state.pages = pages }),
    setCurrentPage: (id) => set((state) => { state.currentPageId = id }),
    setBlocks: (blocks) => set((state) => { state.currentBlocks = blocks }),
    addPage: (page) => set((state) => { state.pages.push(page) }),
    updatePage: (id, updates) => set((state) => {
      const idx = state.pages.findIndex((p) => p.id === id)
      if (idx !== -1) Object.assign(state.pages[idx], updates)
    }),
    removePage: (id) => set((state) => {
      const removeIds = new Set<string>()
      const collectChildren = (parentId: string) => {
        removeIds.add(parentId)
        state.pages.filter((p) => p.parent_id === parentId).forEach((p) => collectChildren(p.id))
      }
      collectChildren(id)
      state.pages = state.pages.filter((p) => !removeIds.has(p.id))
      if (state.currentPageId && removeIds.has(state.currentPageId)) {
        state.currentPageId = null
        state.currentBlocks = []
      }
    }),
    movePage: (id, parentId, sortOrder) => set((state) => {
      const page = state.pages.find((p) => p.id === id)
      if (page) {
        page.parent_id = parentId
        page.sort_order = sortOrder
      }
    }),
    updateBlock: (id, updates) => set((state) => {
      const idx = state.currentBlocks.findIndex((b) => b.id === id)
      if (idx !== -1) Object.assign(state.currentBlocks[idx], updates)
    }),
    addBlock: (block) => set((state) => { state.currentBlocks.push(block) }),
    removeBlock: (id) => set((state) => {
      state.currentBlocks = state.currentBlocks.filter((b) => b.id !== id)
    }),
    reorderBlocks: (pageId, blockIds) => set((state) => {
      const map = new Map(state.currentBlocks.map((b) => [b.id, b]))
      state.currentBlocks = blockIds.map((id, i) => {
        const b = map.get(id)
        if (b) b.sort_order = i
        return b!
      }).filter(Boolean)
    }),
    setLoading: (loading) => set((state) => { state.loading = loading }),
    setError: (error) => set((state) => { state.error = error }),
    getChildren: (parentId) => {
      return get().pages.filter((p) => p.parent_id === parentId)
    },
  }))
)

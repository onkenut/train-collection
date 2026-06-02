import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

export type ActivePanel = 'none' | 'ai' | 'version' | 'search'

interface UIState {
  sidebarCollapsed: boolean
  sidebarMobileOpen: boolean
  activePanel: ActivePanel
  theme: 'dark' | 'light'
  contextMenu: ContextMenuState | null

  setSidebarCollapsed: (collapsed: boolean) => void
  toggleSidebar: () => void
  setSidebarMobileOpen: (open: boolean) => void
  setActivePanel: (panel: ActivePanel) => void
  togglePanel: (panel: ActivePanel) => void
  setTheme: (theme: 'dark' | 'light') => void
  toggleTheme: () => void
  showContextMenu: (menu: ContextMenuState) => void
  hideContextMenu: () => void
}

export interface ContextMenuState {
  x: number
  y: number
  type: 'notebook' | 'page'
  targetId: string
  items: ContextMenuItem[]
}

export interface ContextMenuItem {
  label: string
  icon?: string
  action: string
  danger?: boolean
  divider?: boolean
}

export const useUIStore = create<UIState>()(
  immer((set) => ({
    sidebarCollapsed: false,
    sidebarMobileOpen: false,
    activePanel: 'none',
    theme: (localStorage.getItem('theme') as 'dark' | 'light') || 'dark',
    contextMenu: null,

    setSidebarCollapsed: (collapsed) => set((state) => { state.sidebarCollapsed = collapsed }),
    toggleSidebar: () => set((state) => { state.sidebarCollapsed = !state.sidebarCollapsed }),
    setSidebarMobileOpen: (open) => set((state) => { state.sidebarMobileOpen = open }),
    setActivePanel: (panel) => set((state) => { state.activePanel = panel }),
    togglePanel: (panel) => set((state) => {
      state.activePanel = state.activePanel === panel ? 'none' : panel
    }),
    setTheme: (theme) => set((state) => {
      state.theme = theme
      localStorage.setItem('theme', theme)
      document.documentElement.classList.remove('dark', 'light')
      document.documentElement.classList.add(theme)
    }),
    toggleTheme: () => set((state) => {
      state.theme = state.theme === 'dark' ? 'light' : 'dark'
      localStorage.setItem('theme', state.theme)
      document.documentElement.classList.remove('dark', 'light')
      document.documentElement.classList.add(state.theme)
    }),
    showContextMenu: (menu) => set((state) => { state.contextMenu = menu }),
    hideContextMenu: () => set((state) => { state.contextMenu = null }),
  }))
)

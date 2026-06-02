import { useNavigate } from 'react-router-dom'
import { Settings, Moon, Sun, ChevronLeft, ChevronRight } from 'lucide-react'
import { useUIStore } from '@/stores/uiStore'
import { SearchBar } from './SearchBar'
import { NotebookTree } from './NotebookTree'
import { PageTree } from './PageTree'
import { TagList } from './TagList'
import { useNotebookStore } from '@/stores/notebookStore'
import { cn } from '@/lib/utils'

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar, theme, toggleTheme, sidebarMobileOpen, setSidebarMobileOpen } = useUIStore()
  const { currentNotebookId } = useNotebookStore()
  const navigate = useNavigate()

  const sidebarWidth = sidebarCollapsed ? 'w-14' : 'w-64'

  return (
    <>
      {!sidebarMobileOpen && (
        <div className="hidden md:block">
          <aside
            className={cn(
              'h-screen flex flex-col border-r transition-all duration-300',
              sidebarWidth
            )}
            style={{
              background: 'var(--color-bg-secondary)',
              borderColor: 'var(--color-border)',
            }}
          >
            <div className="flex items-center justify-between px-3 py-3" style={{ borderBottom: '1px solid var(--color-border)' }}>
              {!sidebarCollapsed && (
                <h1
                  className="text-base font-bold tracking-tight"
                  style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-accent)' }}
                >
                  MindVault
                </h1>
              )}
              <button
                onClick={toggleSidebar}
                className="p-1.5 rounded-lg transition-colors"
                style={{ color: 'var(--color-text-muted)' }}
                onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-bg-tertiary)' }}
                onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
              >
                {sidebarCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
              </button>
            </div>

            {!sidebarCollapsed && (
              <div className="px-3 py-2">
                <SearchBar />
              </div>
            )}

            <div className="flex-1 overflow-y-auto px-2 py-1">
              <NotebookTree />
              {currentNotebookId && !sidebarCollapsed && (
                <div className="mt-2" style={{ borderTop: '1px solid var(--color-border)', paddingTop: '8px' }}>
                  <PageTree notebookId={currentNotebookId} />
                </div>
              )}
            </div>

            <div className="px-2 py-2" style={{ borderTop: '1px solid var(--color-border)' }}>
              {!sidebarCollapsed && <TagList />}
            </div>

            <div
              className="flex items-center justify-between px-3 py-2"
              style={{ borderTop: '1px solid var(--color-border)' }}
            >
              {!sidebarCollapsed && (
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => navigate('/settings')}
                    className="p-1.5 rounded-lg transition-colors"
                    style={{ color: 'var(--color-text-muted)' }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-bg-tertiary)' }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
                  >
                    <Settings size={16} />
                  </button>
                  <button
                    onClick={toggleTheme}
                    className="p-1.5 rounded-lg transition-colors"
                    style={{ color: 'var(--color-text-muted)' }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-bg-tertiary)' }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
                  >
                    {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
                  </button>
                </div>
              )}
            </div>
          </aside>
        </div>
      )}

      {sidebarMobileOpen && (
        <div
          className="fixed inset-0 z-40 md:hidden"
          style={{ background: 'rgba(0,0,0,0.5)' }}
          onClick={() => setSidebarMobileOpen(false)}
        >
          <aside
            className="w-72 h-full animate-slide-in-right"
            style={{ background: 'var(--color-bg-secondary)' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-3 py-3" style={{ borderBottom: '1px solid var(--color-border)' }}>
              <h1
                className="text-base font-bold"
                style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-accent)' }}
              >
                MindVault
              </h1>
            </div>
            <div className="px-3 py-2"><SearchBar /></div>
            <div className="overflow-y-auto px-2 py-1">
              <NotebookTree />
              {currentNotebookId && (
                <div className="mt-2" style={{ borderTop: '1px solid var(--color-border)', paddingTop: '8px' }}>
                  <PageTree notebookId={currentNotebookId} />
                </div>
              )}
            </div>
            <div className="px-2 py-2"><TagList /></div>
          </aside>
        </div>
      )}
    </>
  )
}

import { useUIStore } from '@/stores/uiStore'
import { Sidebar } from './Sidebar'
import { RightPanel } from './RightPanel'
import { cn } from '@/lib/utils'

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const { sidebarCollapsed, activePanel } = useUIStore()

  return (
    <div className="h-screen flex overflow-hidden" style={{ background: 'var(--color-bg-primary)' }}>
      <Sidebar />
      <main
        className={cn(
          'flex-1 flex flex-col min-w-0 transition-all duration-300',
          sidebarCollapsed ? 'ml-0' : 'ml-0'
        )}
      >
        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 min-w-0 overflow-y-auto">
            {children}
          </div>
          {activePanel !== 'none' && <RightPanel />}
        </div>
      </main>
    </div>
  )
}

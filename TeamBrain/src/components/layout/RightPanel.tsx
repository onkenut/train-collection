import { X } from 'lucide-react'
import { useUIStore } from '@/stores/uiStore'
import { AIPanel } from '@/components/ai/AIPanel'
import { VersionPanel } from '@/components/version/VersionPanel'

export function RightPanel() {
  const { activePanel, setActivePanel } = useUIStore()

  if (activePanel === 'none') return null

  const titles: Record<string, string> = {
    ai: 'AI 助手',
    version: '版本历史',
    search: '搜索',
  }

  return (
    <div
      className="w-[400px] flex-shrink-0 flex flex-col border-l animate-slide-in-right"
      style={{
        background: 'var(--color-bg-secondary)',
        borderColor: 'var(--color-border)',
      }}
    >
      <div
        className="flex items-center justify-between px-4 py-3"
        style={{ borderBottom: '1px solid var(--color-border)' }}
      >
        <h3
          className="text-sm font-semibold"
          style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}
        >
          {titles[activePanel] || ''}
        </h3>
        <button
          onClick={() => setActivePanel('none')}
          className="p-1 rounded-lg transition-colors"
          style={{ color: 'var(--color-text-muted)' }}
          onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-bg-tertiary)' }}
          onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
        >
          <X size={16} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {activePanel === 'ai' && <AIPanel />}
        {activePanel === 'version' && <VersionPanel />}
      </div>
    </div>
  )
}

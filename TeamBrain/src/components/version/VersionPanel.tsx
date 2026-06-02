import { useState, useEffect } from 'react'
import { Clock, RotateCcw, Copy } from 'lucide-react'
import { usePageStore } from '@/stores/pageStore'
import { versionApi, type PageVersion } from '@/api/endpoints'
import { useToast } from '@/components/common/Toast'
import { VersionPreview } from './VersionPreview'

export function VersionPanel() {
  const { currentPageId } = usePageStore()
  const [versions, setVersions] = useState<PageVersion[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const toast = useToast()

  useEffect(() => {
    if (currentPageId) loadVersions()
  }, [currentPageId])

  async function loadVersions() {
    if (!currentPageId) return
    setLoading(true)
    try {
      const data = await versionApi.list(currentPageId)
      setVersions(data)
      if (data.length > 0) setSelectedId(data[0].id)
    } catch {
      toast.error('加载版本历史失败')
    } finally {
      setLoading(false)
    }
  }

  async function handleRestore(versionId: string) {
    if (!confirm('确定恢复到该版本？当前内容将被替换。')) return
    try {
      await versionApi.restore(versionId)
      toast.success('已恢复到该版本')
      loadVersions()
    } catch {
      toast.error('恢复失败')
    }
  }

  async function handleCopy(versionId: string) {
    try {
      await versionApi.copy(versionId)
      toast.success('已复制为新页面')
    } catch {
      toast.error('复制失败')
    }
  }

  const selectedVersion = versions.find((v) => v.id === selectedId)

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="animate-pulse flex items-start gap-3">
                <div className="w-3 h-3 rounded-full mt-1" style={{ background: 'var(--color-bg-tertiary)' }} />
                <div className="flex-1">
                  <div className="h-3 rounded w-2/3 mb-1" style={{ background: 'var(--color-bg-tertiary)' }} />
                  <div className="h-3 rounded w-1/3" style={{ background: 'var(--color-bg-tertiary)' }} />
                </div>
              </div>
            ))}
          </div>
        ) : versions.length === 0 ? (
          <div className="flex flex-col items-center py-8">
            <Clock size={24} style={{ color: 'var(--color-text-muted)' }} />
            <p className="text-xs mt-2" style={{ color: 'var(--color-text-muted)' }}>暂无版本历史</p>
          </div>
        ) : (
          <div className="py-2">
            {versions.map((v) => (
              <div key={v.id} className="relative px-4 py-2">
                <div
                  className="flex items-start gap-3 cursor-pointer group"
                  onClick={() => setSelectedId(v.id)}
                >
                  <div className="flex flex-col items-center mt-1">
                    <div
                      className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                      style={{
                        background: selectedId === v.id ? 'var(--color-accent)' : 'var(--color-bg-hover)',
                        boxShadow: selectedId === v.id ? '0 0 0 3px var(--color-accent-light)' : 'none',
                      }}
                    />
                    <div className="w-px flex-1 mt-1" style={{ background: 'var(--color-border)', minHeight: '20px' }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div
                      className="text-xs font-medium mb-0.5"
                      style={{ color: selectedId === v.id ? 'var(--color-accent)' : 'var(--color-text-secondary)' }}
                    >
                      {formatTime(v.created_at)}
                    </div>
                    <div className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                      {v.char_count} 字符
                    </div>
                    <div className="flex items-center gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleRestore(v.id) }}
                        className="p-1 rounded transition-colors"
                        style={{ color: 'var(--color-text-muted)' }}
                        onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-bg-tertiary)' }}
                        onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
                        title="恢复此版本"
                      >
                        <RotateCcw size={12} />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleCopy(v.id) }}
                        className="p-1 rounded transition-colors"
                        style={{ color: 'var(--color-text-muted)' }}
                        onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-bg-tertiary)' }}
                        onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
                        title="复制为新页面"
                      >
                        <Copy size={12} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedVersion && (
        <div
          className="border-t p-4"
          style={{ borderColor: 'var(--color-border)', maxHeight: '200px', overflowY: 'auto' }}
        >
          <VersionPreview version={selectedVersion} />
        </div>
      )}
    </div>
  )
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHour = Math.floor(diffMs / 3600000)
  const diffDay = Math.floor(diffMs / 86400000)

  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  if (diffHour < 24) return `${diffHour} 小时前`
  if (diffDay < 7) return `${diffDay} 天前`
  return d.toLocaleDateString('zh-CN')
}

import { useState, useEffect } from 'react'
import { versionApi, type PageVersion, type VersionDiff } from '@/api/endpoints'
import { useToast } from '@/components/common/Toast'

interface VersionDiffProps {
  pageId: string
  leftVersionId: string
  rightVersionId: string
}

export function VersionDiff({ pageId, leftVersionId, rightVersionId }: VersionDiffProps) {
  const [leftVersion, setLeftVersion] = useState<PageVersion | null>(null)
  const [rightVersion, setRightVersion] = useState<PageVersion | null>(null)
  const [diff, setDiff] = useState<VersionDiff | null>(null)
  const [mode, setMode] = useState<'side-by-side' | 'inline'>('side-by-side')
  const [loading, setLoading] = useState(false)
  const toast = useToast()

  useEffect(() => {
    loadDiff()
  }, [leftVersionId, rightVersionId])

  async function loadDiff() {
    setLoading(true)
    try {
      const [left, right, diffResult] = await Promise.all([
        versionApi.get(leftVersionId),
        versionApi.get(rightVersionId),
        versionApi.diff(leftVersionId, rightVersionId),
      ])
      setLeftVersion(left)
      setRightVersion(right)
      setDiff(diffResult)
    } catch {
      toast.error('加载版本差异失败')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-sm" style={{ color: 'var(--color-text-muted)' }}>加载差异...</div>
      </div>
    )
  }

  if (!diff) return null

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
            {formatVersionTime(leftVersion?.created_at)} → {formatVersionTime(rightVersion?.created_at)}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setMode('side-by-side')}
            className="text-xs px-2 py-1 rounded transition-colors"
            style={{
              background: mode === 'side-by-side' ? 'var(--color-bg-tertiary)' : 'transparent',
              color: mode === 'side-by-side' ? 'var(--color-text-primary)' : 'var(--color-text-muted)',
            }}
          >
            并排
          </button>
          <button
            onClick={() => setMode('inline')}
            className="text-xs px-2 py-1 rounded transition-colors"
            style={{
              background: mode === 'inline' ? 'var(--color-bg-tertiary)' : 'transparent',
              color: mode === 'inline' ? 'var(--color-text-primary)' : 'var(--color-text-muted)',
            }}
          >
            内联
          </button>
        </div>
      </div>

      <div className="flex gap-2 text-xs mb-2" style={{ color: 'var(--color-text-muted)' }}>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded" style={{ background: 'rgba(239,68,68,0.2)' }} /> 删除
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded" style={{ background: 'var(--color-accent-light)' }} /> 新增
        </span>
      </div>

      {mode === 'side-by-side' ? (
        <div className="grid grid-cols-2 gap-2">
          <div
            className="rounded-lg p-3 text-xs font-mono max-h-64 overflow-y-auto"
            style={{ background: 'var(--color-bg-tertiary)', whiteSpace: 'pre-wrap' }}
          >
            {diff.deletions.map((line, i) => (
              <div key={i} className="px-1 rounded" style={{ background: 'rgba(239,68,68,0.15)', color: 'var(--color-danger)' }}>
                - {line}
              </div>
            ))}
          </div>
          <div
            className="rounded-lg p-3 text-xs font-mono max-h-64 overflow-y-auto"
            style={{ background: 'var(--color-bg-tertiary)', whiteSpace: 'pre-wrap' }}
          >
            {diff.additions.map((line, i) => (
              <div key={i} className="px-1 rounded" style={{ background: 'var(--color-accent-light)', color: 'var(--color-accent)' }}>
                + {line}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div
          className="rounded-lg p-3 text-xs font-mono max-h-64 overflow-y-auto"
          style={{ background: 'var(--color-bg-tertiary)', whiteSpace: 'pre-wrap' }}
        >
          {diff.deletions.map((line, i) => (
            <div key={`d-${i}`} className="px-1 rounded" style={{ background: 'rgba(239,68,68,0.15)', color: 'var(--color-danger)' }}>
              - {line}
            </div>
          ))}
          {diff.additions.map((line, i) => (
            <div key={`a-${i}`} className="px-1 rounded" style={{ background: 'var(--color-accent-light)', color: 'var(--color-accent)' }}>
              + {line}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function formatVersionTime(iso?: string): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

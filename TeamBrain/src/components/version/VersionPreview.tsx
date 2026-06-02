import type { PageVersion } from '@/api/endpoints'

interface VersionPreviewProps {
  version: PageVersion
}

export function VersionPreview({ version }: VersionPreviewProps) {
  let content: string
  try {
    const parsed = JSON.parse(version.snapshot)
    content = typeof parsed === 'string' ? parsed : JSON.stringify(parsed, null, 2)
  } catch {
    content = version.snapshot
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium" style={{ color: 'var(--color-text-secondary)' }}>
          版本预览
        </span>
        <span className="text-xs font-mono" style={{ color: 'var(--color-text-muted)' }}>
          {version.char_count} 字符
        </span>
      </div>
      <div
        className="text-xs rounded-lg p-3 max-h-36 overflow-y-auto"
        style={{
          background: 'var(--color-bg-tertiary)',
          color: 'var(--color-text-secondary)',
          fontFamily: "'JetBrains Mono', monospace",
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-all',
        }}
      >
        {content.slice(0, 1000)}
        {content.length > 1000 && <span style={{ color: 'var(--color-text-muted)' }}>... (已截断)</span>}
      </div>
    </div>
  )
}

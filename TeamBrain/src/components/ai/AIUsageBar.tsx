import { useEffect } from 'react'
import { useAIStore } from '@/stores/aiStore'
import { aiApi } from '@/api/endpoints'

export function AIUsageBar() {
  const { usage, setUsage } = useAIStore()

  useEffect(() => {
    async function loadUsage() {
      try {
        const data = await aiApi.getUsage()
        setUsage(data)
      } catch {
        // ignore
      }
    }
    loadUsage()
  }, [setUsage])

  if (!usage) return null

  const percent = Math.min((usage.total_tokens / usage.budget_limit) * 100, 100)
  const isOver = percent >= 90

  return (
    <div className="rounded-lg p-3" style={{ background: 'var(--color-bg-tertiary)' }}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium" style={{ color: 'var(--color-text-secondary)' }}>
          本月 Token 用量
        </span>
        <span
          className="text-xs font-mono"
          style={{ color: isOver ? 'var(--color-danger)' : 'var(--color-text-muted)' }}
        >
          {formatTokens(usage.total_tokens)} / {formatTokens(usage.budget_limit)}
        </span>
      </div>
      <div
        className="h-2 rounded-full overflow-hidden"
        style={{ background: 'var(--color-bg-secondary)' }}
      >
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${percent}%`,
            background: isOver
              ? 'var(--color-danger)'
              : percent > 60
                ? 'var(--color-warning)'
                : 'var(--color-accent)',
          }}
        />
      </div>
      <div className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>
        {percent.toFixed(1)}% 已使用
        {isOver && <span style={{ color: 'var(--color-danger)' }}> · 接近预算上限</span>}
      </div>
    </div>
  )
}

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return String(n)
}

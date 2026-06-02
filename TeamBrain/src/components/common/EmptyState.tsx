import { FileText, Search } from 'lucide-react'

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full py-16 px-4">
      <div
        className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4"
        style={{ background: 'var(--color-bg-tertiary)' }}
      >
        {icon || <FileText size={28} style={{ color: 'var(--color-text-muted)' }} />}
      </div>
      <h3
        className="text-lg font-semibold mb-1"
        style={{ color: 'var(--color-text-secondary)', fontFamily: "'Outfit', sans-serif" }}
      >
        {title}
      </h3>
      {description && (
        <p className="text-sm text-center max-w-xs" style={{ color: 'var(--color-text-muted)' }}>
          {description}
        </p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

export function SearchEmptyState({ query }: { query: string }) {
  return (
    <EmptyState
      icon={<Search size={28} style={{ color: 'var(--color-text-muted)' }} />}
      title="未找到结果"
      description={query ? `没有找到与 "${query}" 匹配的内容` : '试试输入关键词搜索'}
    />
  )
}

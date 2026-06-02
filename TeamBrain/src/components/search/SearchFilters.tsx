import { useSearchStore } from '@/stores/searchStore'
import { useNotebookStore } from '@/stores/notebookStore'
import { useTagStore } from '@/stores/tagStore'

export function SearchFilters() {
  const { filters, setFilters, resetFilters } = useSearchStore()
  const { notebooks } = useNotebookStore()
  const { tags } = useTagStore()

  const hasActiveFilters = filters.notebook_id || filters.date_from || filters.date_to || filters.tag

  return (
    <div
      className="rounded-lg p-4 space-y-4"
      style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
          过滤条件
        </h3>
        {hasActiveFilters && (
          <button
            onClick={resetFilters}
            className="text-xs transition-colors"
            style={{ color: 'var(--color-accent)' }}
          >
            重置
          </button>
        )}
      </div>

      <div>
        <label className="text-xs font-medium mb-1.5 block" style={{ color: 'var(--color-text-muted)' }}>
          笔记本
        </label>
        <select
          value={filters.notebook_id || ''}
          onChange={(e) => setFilters({ notebook_id: e.target.value || null })}
          className="input-base"
        >
          <option value="">全部笔记本</option>
          {notebooks.map((nb) => (
            <option key={nb.id} value={nb.id}>{nb.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="text-xs font-medium mb-1.5 block" style={{ color: 'var(--color-text-muted)' }}>
          修改日期
        </label>
        <div className="flex gap-2">
          <input
            type="date"
            value={filters.date_from || ''}
            onChange={(e) => setFilters({ date_from: e.target.value || null })}
            className="input-base flex-1"
          />
          <span className="self-center text-xs" style={{ color: 'var(--color-text-muted)' }}>至</span>
          <input
            type="date"
            value={filters.date_to || ''}
            onChange={(e) => setFilters({ date_to: e.target.value || null })}
            className="input-base flex-1"
          />
        </div>
      </div>

      <div>
        <label className="text-xs font-medium mb-1.5 block" style={{ color: 'var(--color-text-muted)' }}>
          标签
        </label>
        <select
          value={filters.tag || ''}
          onChange={(e) => setFilters({ tag: e.target.value || null })}
          className="input-base"
        >
          <option value="">全部标签</option>
          {tags.map((tag) => (
            <option key={tag.id} value={tag.name}>{tag.name}</option>
          ))}
        </select>
      </div>
    </div>
  )
}

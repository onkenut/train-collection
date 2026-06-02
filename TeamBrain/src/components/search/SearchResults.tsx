import { useNavigate } from 'react-router-dom'
import { FileText, BookOpen } from 'lucide-react'
import type { SearchResult } from '@/api/endpoints'
import { useNotebookStore } from '@/stores/notebookStore'
import { SearchEmptyState } from '@/components/common/EmptyState'

interface SearchResultsProps {
  results: SearchResult[]
  query: string
  loading?: boolean
}

export function SearchResults({ results, query, loading }: SearchResultsProps) {
  const navigate = useNavigate()
  const { notebooks } = useNotebookStore()

  if (loading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-4 rounded w-1/3 mb-2" style={{ background: 'var(--color-bg-tertiary)' }} />
            <div className="h-3 rounded w-full mb-1" style={{ background: 'var(--color-bg-tertiary)' }} />
            <div className="h-3 rounded w-2/3" style={{ background: 'var(--color-bg-tertiary)' }} />
          </div>
        ))}
      </div>
    )
  }

  if (results.length === 0 && query) {
    return <SearchEmptyState query={query} />
  }

  function highlightSnippet(snippet: string, keyword: string): React.ReactNode {
    if (!keyword) return snippet
    const parts = snippet.split(new RegExp(`(${escapeRegex(keyword)})`, 'gi'))
    return parts.map((part, i) =>
      part.toLowerCase() === keyword.toLowerCase() ? (
        <mark key={i} className="rounded px-0.5" style={{ background: 'var(--color-accent-light)', color: 'var(--color-accent)' }}>
          {part}
        </mark>
      ) : (
        part
      )
    )
  }

  return (
    <div className="space-y-2">
      {results.map((result, i) => (
        <button
          key={result.page_id}
          onClick={() => navigate(`/notebook/${result.notebook_id}/page/${result.page_id}`)}
          className="card w-full text-left animate-fade-in group transition-colors"
          style={{ animationDelay: `${i * 50}ms` }}
          onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-hover)' }}
          onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)' }}
        >
          <div className="flex items-center gap-2 mb-1.5">
            <FileText size={14} style={{ color: 'var(--color-accent)' }} />
            <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
              {result.page_title}
            </span>
          </div>
          <p className="text-xs leading-relaxed mb-2" style={{ color: 'var(--color-text-secondary)' }}>
            {highlightSnippet(result.snippet, query)}
          </p>
          <div className="flex items-center gap-2">
            <BookOpen size={12} style={{ color: 'var(--color-text-muted)' }} />
            <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
              {result.notebook_name}
            </span>
          </div>
        </button>
      ))}
    </div>
  )
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

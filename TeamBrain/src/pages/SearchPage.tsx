import { useState, useEffect } from 'react'
import { Search as SearchIcon } from 'lucide-react'
import { useSearchStore } from '@/stores/searchStore'
import { searchApi } from '@/api/endpoints'
import { SearchResults } from '@/components/search/SearchResults'
import { SearchFilters } from '@/components/search/SearchFilters'

export default function SearchPage() {
  const { query, setQuery, results, setResults, filters, loading, setLoading } = useSearchStore()
  const [localQuery, setLocalQuery] = useState(query)

  useEffect(() => {
    if (query) doSearch()
  }, [filters.notebook_id, filters.date_from, filters.date_to, filters.tag])

  async function doSearch() {
    if (!query.trim()) return
    setLoading(true)
    try {
      const data = await searchApi.search({
        q: query,
        notebook_id: filters.notebook_id || undefined,
        date_from: filters.date_from || undefined,
        date_to: filters.date_to || undefined,
        tag: filters.tag || undefined,
      })
      setResults(data)
    } catch {
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setQuery(localQuery)
    doSearch()
  }

  return (
    <div className="h-full flex flex-col">
      <div
        className="px-6 py-4"
        style={{ borderBottom: '1px solid var(--color-border)' }}
      >
        <h2
          className="text-xl font-semibold mb-4"
          style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}
        >
          搜索
        </h2>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div
            className="flex-1 flex items-center gap-2 px-4 py-2.5 rounded-lg"
            style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}
          >
            <SearchIcon size={18} style={{ color: 'var(--color-text-muted)' }} />
            <input
              type="text"
              value={localQuery}
              onChange={(e) => setLocalQuery(e.target.value)}
              placeholder="输入关键词搜索..."
              className="bg-transparent outline-none text-sm flex-1"
              style={{ color: 'var(--color-text-primary)' }}
            />
          </div>
          <button type="submit" className="btn-primary">
            搜索
          </button>
        </form>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="flex gap-6">
          <div className="flex-1">
            {query && (
              <p className="text-xs mb-3" style={{ color: 'var(--color-text-muted)' }}>
                找到 {results.length} 个结果
              </p>
            )}
            <SearchResults results={results} query={query} loading={loading} />
          </div>
          <div className="w-64 flex-shrink-0">
            <SearchFilters />
          </div>
        </div>
      </div>
    </div>
  )
}

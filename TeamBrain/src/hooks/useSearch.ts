import { useState, useEffect, useRef, useCallback } from 'react'
import { searchApi, type SearchResult } from '@/api/endpoints'

interface UseSearchOptions {
  debounceMs?: number
  minChars?: number
}

interface UseSearchReturn {
  query: string
  setQuery: (q: string) => void
  results: SearchResult[]
  loading: boolean
  error: string | null
  search: (q: string) => void
}

export function useSearch(options: UseSearchOptions = {}): UseSearchReturn {
  const { debounceMs = 300, minChars = 1 } = options
  const [query, setQueryState] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const timerRef = useRef<ReturnType<typeof setTimeout>>()

  const search = useCallback(async (q: string) => {
    if (q.length < minChars) {
      setResults([])
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await searchApi.search({ q })
      setResults(data)
    } catch (e: any) {
      setError(e.message || '搜索失败')
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [minChars])

  const setQuery = useCallback((q: string) => {
    setQueryState(q)
    if (timerRef.current) clearTimeout(timerRef.current)
    if (!q.trim()) {
      setResults([])
      setLoading(false)
      return
    }
    timerRef.current = setTimeout(() => search(q), debounceMs)
  }, [debounceMs, search])

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [])

  return { query, setQuery, results, loading, error, search }
}

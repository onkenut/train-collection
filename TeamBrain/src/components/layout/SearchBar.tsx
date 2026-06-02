import { useState, useEffect, useRef } from 'react'
import { Search, Command } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useSearchStore } from '@/stores/searchStore'
import { searchApi } from '@/api/endpoints'

export function SearchBar() {
  const { query, setQuery, setResults, setLoading } = useSearchStore()
  const [focused, setFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()
  let debounceTimer: ReturnType<typeof setTimeout>

  useEffect(() => {
    function handleKeydown(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }
    document.addEventListener('keydown', handleKeydown)
    return () => document.removeEventListener('keydown', handleKeydown)
  }, [])

  async function handleChange(value: string) {
    setQuery(value)
    if (debounceTimer) clearTimeout(debounceTimer)
    if (!value.trim()) {
      setResults([])
      return
    }
    debounceTimer = setTimeout(async () => {
      setLoading(true)
      try {
        const results = await searchApi.search({ q: value })
        setResults(results)
      } catch {
        setResults([])
      } finally {
        setLoading(false)
      }
    }, 300)
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && query.trim()) {
      navigate('/search')
    }
  }

  return (
    <div
      className="relative flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all"
      style={{
        background: focused ? 'var(--color-bg-tertiary)' : 'var(--color-bg-tertiary)',
        border: focused ? '1px solid var(--color-accent)' : '1px solid transparent',
        boxShadow: focused ? '0 0 0 2px var(--color-accent-light)' : 'none',
      }}
    >
      <Search size={14} style={{ color: 'var(--color-text-muted)', flexShrink: 0 }} />
      <input
        ref={inputRef}
        type="text"
        placeholder="搜索..."
        value={query}
        onChange={(e) => handleChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        onKeyDown={handleKeyDown}
        className="bg-transparent outline-none text-sm flex-1"
        style={{ color: 'var(--color-text-primary)' }}
      />
      <kbd
        className="hidden sm:flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-mono"
        style={{ background: 'var(--color-bg-secondary)', color: 'var(--color-text-muted)', border: '1px solid var(--color-border)' }}
      >
        <Command size={10} />K
      </kbd>
    </div>
  )
}

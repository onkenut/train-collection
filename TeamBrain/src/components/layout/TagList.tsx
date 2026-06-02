import { useEffect } from 'react'
import { Tag as TagIcon } from 'lucide-react'
import { useTagStore } from '@/stores/tagStore'
import { tagApi } from '@/api/endpoints'
import { useToast } from '@/components/common/Toast'
import { cn } from '@/lib/utils'

export function TagList() {
  const { tags, selectedTagId, setTags, setSelectedTag } = useTagStore()
  const toast = useToast()

  useEffect(() => {
    loadTags()
  }, [])

  async function loadTags() {
    try {
      const data = await tagApi.list()
      setTags(data)
    } catch {
      // silently fail on initial load
    }
  }

  if (tags.length === 0) return null

  return (
    <div>
      <div className="flex items-center gap-1.5 px-1 mb-2">
        <TagIcon size={12} style={{ color: 'var(--color-text-muted)' }} />
        <span className="text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
          标签
        </span>
      </div>
      <div className="flex flex-wrap gap-1.5 px-1">
        {tags.map((tag) => (
          <button
            key={tag.id}
            onClick={() => setSelectedTag(selectedTagId === tag.id ? null : tag.id)}
            className={cn(
              'px-2 py-0.5 rounded-full text-xs font-medium transition-colors',
              selectedTagId === tag.id && 'ring-1'
            )}
            style={{
              background: selectedTagId === tag.id ? `${tag.color}20` : 'var(--color-bg-tertiary)',
              color: selectedTagId === tag.id ? tag.color : 'var(--color-text-secondary)',
              borderColor: selectedTagId === tag.id ? tag.color : undefined,
              ...(selectedTagId === tag.id ? { ringColor: tag.color } : {}),
            }}
          >
            {tag.name}
          </button>
        ))}
      </div>
    </div>
  )
}

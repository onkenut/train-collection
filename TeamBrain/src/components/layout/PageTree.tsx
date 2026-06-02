import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, ChevronRight, ChevronDown, FileText } from 'lucide-react'
import { usePageStore } from '@/stores/pageStore'
import { pageApi } from '@/api/endpoints'
import { useContextMenu } from '@/components/common/ContextMenu'
import { useToast } from '@/components/common/Toast'
import { DragDropList, DragHandle } from '@/components/common/DragDropList'
import { cn } from '@/lib/utils'

interface PageTreeProps {
  notebookId: string
}

export function PageTree({ notebookId }: PageTreeProps) {
  const {
    pages, currentPageId, setCurrentPage, setPages,
    addPage, updatePage, removePage,
  } = usePageStore()
  const { handleContextMenu } = useContextMenu()
  const toast = useToast()
  const navigate = useNavigate()
  const [creating, setCreating] = useState(false)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  const rootPages = pages.filter((p) => p.parent_id === null)
  const getChildren = (parentId: string) => pages.filter((p) => p.parent_id === parentId)

  async function handleSelect(pageId: string) {
    setCurrentPage(pageId)
    navigate(`/notebook/${notebookId}/page/${pageId}`)
  }

  async function handleCreate(parentId: string | null = null) {
    setCreating(true)
    try {
      const page = await pageApi.create(notebookId, {
        title: '无标题页面',
        icon: '📄',
        parent_id: parentId,
      })
      addPage(page)
      setCurrentPage(page.id)
      navigate(`/notebook/${notebookId}/page/${page.id}`)
      toast.success('页面已创建')
    } catch {
      toast.error('创建页面失败')
    } finally {
      setCreating(false)
    }
  }

  async function handleRename(id: string) {
    const page = pages.find((p) => p.id === id)
    if (!page) return
    const title = prompt('重命名页面', page.title)
    if (!title || title === page.title) return
    try {
      await pageApi.update(id, { title })
      updatePage(id, { title })
      toast.success('已重命名')
    } catch {
      toast.error('重命名失败')
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('确定删除该页面？')) return
    try {
      await pageApi.delete(id)
      removePage(id)
      toast.success('已删除')
    } catch {
      toast.error('删除失败')
    }
  }

  async function handleReorder(ids: string[]) {
    try {
      const ordered = ids.map((id, i) => ({ id, sort_order: i }))
      await Promise.all(ordered.map((o) => pageApi.move(o.id, pages.find((p) => p.id === o.id)?.parent_id ?? null, o.sort_order)))
    } catch {
      toast.error('排序失败')
    }
  }

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const menuItems = [
    { label: '新建子页面', icon: '📄', action: 'create_child' },
    { label: '重命名', icon: '✏️', action: 'rename' },
    { label: '删除', icon: '🗑️', action: 'delete', danger: true, divider: true },
  ]

  const handlePageContextMenu = useCallback((e: React.MouseEvent, pageId: string) => {
    handleContextMenu(e, 'page', pageId, menuItems)
  }, [handleContextMenu])

  function renderPageItem(page: typeof pages[0], depth: number = 0) {
    const children = getChildren(page.id)
    const isExpanded = expandedIds.has(page.id)
    const isActive = currentPageId === page.id

    return (
      <div key={page.id}>
        <div
          className={cn('sidebar-item group', isActive && 'active')}
          style={{ paddingLeft: `${12 + depth * 16}px` }}
          onClick={() => handleSelect(page.id)}
          onContextMenu={(e) => handlePageContextMenu(e, page.id)}
        >
          {children.length > 0 ? (
            <button
              onClick={(e) => { e.stopPropagation(); toggleExpand(page.id) }}
              className="p-0.5 flex-shrink-0"
              style={{ color: 'var(--color-text-muted)' }}
            >
              {isExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            </button>
          ) : (
            <span className="w-4 flex-shrink-0" />
          )}
          <span className="text-sm flex-shrink-0">{page.icon}</span>
          <span className="truncate flex-1 text-sm">{page.title}</span>
        </div>
        {isExpanded && children.length > 0 && (
          <div>
            {children.map((child) => renderPageItem(child, depth + 1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between px-1 mb-1">
        <span className="text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
          页面
        </span>
        <button
          onClick={() => handleCreate()}
          disabled={creating}
          className="p-0.5 rounded transition-colors"
          style={{ color: 'var(--color-text-muted)' }}
          onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-bg-tertiary)' }}
          onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
        >
          <Plus size={14} />
        </button>
      </div>

      <DragDropList
        items={rootPages}
        getId={(p) => p.id}
        onReorder={handleReorder}
        renderItem={(page, dragHandleProps) => (
          <div className="group flex items-center">
            <DragHandle {...dragHandleProps} />
            {renderPageItem(page, 0)}
          </div>
        )}
      />

      {rootPages.length === 0 && (
        <div className="flex flex-col items-center py-4">
          <FileText size={20} style={{ color: 'var(--color-text-muted)' }} />
          <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>
            暂无页面
          </p>
        </div>
      )}
    </div>
  )
}

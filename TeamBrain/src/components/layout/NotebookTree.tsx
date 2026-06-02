import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, ChevronRight, ChevronDown } from 'lucide-react'
import { useNotebookStore } from '@/stores/notebookStore'
import { usePageStore } from '@/stores/pageStore'
import { notebookApi, pageApi } from '@/api/endpoints'
import { useContextMenu } from '@/components/common/ContextMenu'
import { useToast } from '@/components/common/Toast'
import { cn } from '@/lib/utils'

export function NotebookTree() {
  const {
    notebooks, currentNotebookId, expandedIds,
    setNotebooks, setCurrentNotebook, addNotebook,
    updateNotebook, removeNotebook, toggleExpand,
  } = useNotebookStore()
  const { setPages } = usePageStore()
  const { handleContextMenu } = useContextMenu()
  const toast = useToast()
  const navigate = useNavigate()
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    loadNotebooks()
  }, [])

  async function loadNotebooks() {
    try {
      const data = await notebookApi.list()
      setNotebooks(data)
    } catch (e: any) {
      toast.error('加载笔记本失败')
    }
  }

  async function handleSelect(id: string) {
    setCurrentNotebook(id)
    try {
      const pages = await pageApi.list(id)
      setPages(pages)
      navigate(`/notebook/${id}`)
    } catch {
      toast.error('加载页面失败')
    }
    if (!expandedIds.has(id)) toggleExpand(id)
  }

  async function handleCreate() {
    setCreating(true)
    try {
      const nb = await notebookApi.create({
        name: '新笔记本',
        icon: '📓',
        cover_color: '#10B981',
      })
      addNotebook(nb)
      setCurrentNotebook(nb.id)
      navigate(`/notebook/${nb.id}`)
      toast.success('笔记本已创建')
    } catch {
      toast.error('创建笔记本失败')
    } finally {
      setCreating(false)
    }
  }

  async function handleRename(id: string) {
    const nb = notebooks.find((n) => n.id === id)
    if (!nb) return
    const name = prompt('重命名笔记本', nb.name)
    if (!name || name === nb.name) return
    try {
      await notebookApi.update(id, { name })
      updateNotebook(id, { name })
      toast.success('已重命名')
    } catch {
      toast.error('重命名失败')
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('确定删除该笔记本及其所有页面？')) return
    try {
      await notebookApi.delete(id)
      removeNotebook(id)
      toast.success('已删除')
    } catch {
      toast.error('删除失败')
    }
  }

  const menuItems = [
    { label: '重命名', icon: '✏️', action: 'rename' },
    { label: '删除', icon: '🗑️', action: 'delete', danger: true, divider: true },
  ]

  return (
    <div>
      <div className="flex items-center justify-between px-1 mb-1">
        <span className="text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
          笔记本
        </span>
        <button
          onClick={handleCreate}
          disabled={creating}
          className="p-0.5 rounded transition-colors"
          style={{ color: 'var(--color-text-muted)' }}
          onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-bg-tertiary)' }}
          onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
        >
          <Plus size={14} />
        </button>
      </div>

      {notebooks.map((nb) => (
        <div
          key={nb.id}
          className={cn('sidebar-item group', currentNotebookId === nb.id && 'active')}
          onClick={() => handleSelect(nb.id)}
          onContextMenu={(e) => handleContextMenu(e, 'notebook', nb.id, menuItems)}
        >
          <button
            onClick={(e) => { e.stopPropagation(); toggleExpand(nb.id) }}
            className="p-0.5"
            style={{ color: 'var(--color-text-muted)' }}
          >
            {expandedIds.has(nb.id) ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          </button>
          <span className="text-base">{nb.icon}</span>
          <span className="truncate flex-1 text-sm">{nb.name}</span>
          <div
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{ background: nb.cover_color }}
          />
        </div>
      ))}

      {notebooks.length === 0 && (
        <p className="text-xs px-3 py-2" style={{ color: 'var(--color-text-muted)' }}>
          暂无笔记本，点击 + 创建
        </p>
      )}

      <ContextMenuActionHandler
        onRename={handleRename}
        onDelete={handleDelete}
      />
    </div>
  )
}

function ContextMenuActionHandler({
  onRename,
  onDelete,
}: {
  onRename: (id: string) => void
  onDelete: (id: string) => void
}) {
  const { contextMenu } = useContextMenu()
  useEffect(() => {
    if (!contextMenu || contextMenu.type !== 'notebook') return
    function handler(e: CustomEvent) {
      const { action, targetId } = e.detail
      if (action === 'rename') onRename(targetId)
      if (action === 'delete') onDelete(targetId)
    }
    window.addEventListener('notebook-action' as any, handler as any)
    return () => window.removeEventListener('notebook-action' as any, handler as any)
  }, [contextMenu, onRename, onDelete])
  return null
}

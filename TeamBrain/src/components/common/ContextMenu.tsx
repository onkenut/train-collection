import { useEffect, useRef } from 'react'
import { useUIStore, type ContextMenuItem } from '@/stores/uiStore'

interface ContextMenuProps {
  items: ContextMenuItem[]
  x: number
  y: number
  onAction: (action: string) => void
  onClose: () => void
}

export function ContextMenu({ items, x, y, onAction, onClose }: ContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose()
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [onClose])

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [onClose])

  const menuStyle: React.CSSProperties = {
    position: 'fixed',
    left: x,
    top: y,
    zIndex: 9999,
  }

  return (
    <div ref={menuRef} style={menuStyle} className="animate-fade-in">
      <div
        className="rounded-lg py-1 shadow-xl min-w-[160px]"
        style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}
      >
        {items.map((item, i) => (
          <div key={i}>
            {item.divider && i > 0 && (
              <div className="my-1" style={{ borderTop: '1px solid var(--color-border)' }} />
            )}
            <button
              className="w-full text-left px-3 py-1.5 text-sm flex items-center gap-2 transition-colors"
              style={{ color: item.danger ? 'var(--color-danger)' : 'var(--color-text-secondary)' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = item.danger ? 'rgba(239,68,68,0.1)' : 'var(--color-bg-tertiary)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
              }}
              onClick={() => { onAction(item.action); onClose() }}
            >
              {item.icon && <span className="text-base">{item.icon}</span>}
              <span>{item.label}</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export function useContextMenu() {
  const { contextMenu, showContextMenu, hideContextMenu } = useUIStore()

  const handleContextMenu = (
    e: React.MouseEvent,
    type: 'notebook' | 'page',
    targetId: string,
    items: ContextMenuItem[]
  ) => {
    e.preventDefault()
    e.stopPropagation()
    showContextMenu({ x: e.clientX, y: e.clientY, type, targetId, items })
  }

  return { contextMenu, handleContextMenu, hideContextMenu }
}

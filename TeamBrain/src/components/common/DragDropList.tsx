import { useState, useRef, useCallback } from 'react'
import { GripVertical } from 'lucide-react'

interface DragDropListProps<T> {
  items: T[]
  getId: (item: T) => string
  onReorder: (ids: string[]) => void
  renderItem: (item: T, dragHandleProps: React.HTMLAttributes<HTMLDivElement>) => React.ReactNode
  className?: string
}

export function DragDropList<T>({ items, getId, onReorder, renderItem, className }: DragDropListProps<T>) {
  const [dragIndex, setDragIndex] = useState<number | null>(null)
  const [overIndex, setOverIndex] = useState<number | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const handleDragStart = useCallback((e: React.DragEvent, index: number) => {
    setDragIndex(index)
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', String(index))
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent, index: number) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    if (dragIndex !== null && dragIndex !== index) {
      setOverIndex(index)
    }
  }, [dragIndex])

  const handleDrop = useCallback((e: React.DragEvent, index: number) => {
    e.preventDefault()
    if (dragIndex !== null && dragIndex !== index) {
      const newItems = [...items]
      const [moved] = newItems.splice(dragIndex, 1)
      newItems.splice(index, 0, moved)
      onReorder(newItems.map(getId))
    }
    setDragIndex(null)
    setOverIndex(null)
  }, [dragIndex, items, getId, onReorder])

  const handleDragEnd = useCallback(() => {
    setDragIndex(null)
    setOverIndex(null)
  }, [])

  return (
    <div ref={containerRef} className={className}>
      {items.map((item, index) => (
        <div
          key={getId(item)}
          draggable
          onDragStart={(e) => handleDragStart(e, index)}
          onDragOver={(e) => handleDragOver(e, index)}
          onDrop={(e) => handleDrop(e, index)}
          onDragEnd={handleDragEnd}
          className="relative"
          style={{
            opacity: dragIndex === index ? 0.5 : 1,
            transition: 'opacity 150ms ease',
          }}
        >
          {overIndex === index && dragIndex !== null && dragIndex < index && (
            <div
              className="h-0.5 rounded-full mb-0.5"
              style={{ background: 'var(--color-accent)' }}
            />
          )}
          {renderItem(item, {
            onMouseDown: (e) => e.stopPropagation(),
            className: 'cursor-grab active:cursor-grabbing',
          })}
          {overIndex === index && dragIndex !== null && dragIndex > index && (
            <div
              className="h-0.5 rounded-full mt-0.5"
              style={{ background: 'var(--color-accent)' }}
            />
          )}
        </div>
      ))}
    </div>
  )
}

export function DragHandle(props: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      {...props}
      className={`flex items-center opacity-0 group-hover:opacity-100 transition-opacity ${props.className || ''}`}
      style={{ color: 'var(--color-text-muted)', ...props.style }}
    >
      <GripVertical size={14} />
    </div>
  )
}

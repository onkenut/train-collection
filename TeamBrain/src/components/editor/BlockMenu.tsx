import { useState, useEffect, useRef } from 'react'
import {
  Heading1, Heading2, Heading3, List, ListOrdered, CheckSquare,
  Quote, Code, Table, Image, FileText, Minus, Type
} from 'lucide-react'

interface BlockMenuItem {
  icon: React.ReactNode
  label: string
  description: string
  type: string
}

const blockItems: BlockMenuItem[] = [
  { icon: <Type size={18} />, label: '正文', description: '普通文本段落', type: 'paragraph' },
  { icon: <Heading1 size={18} />, label: '标题1', description: '大标题', type: 'heading1' },
  { icon: <Heading2 size={18} />, label: '标题2', description: '中标题', type: 'heading2' },
  { icon: <Heading3 size={18} />, label: '标题3', description: '小标题', type: 'heading3' },
  { icon: <List size={18} />, label: '无序列表', description: '项目符号列表', type: 'bullet_list' },
  { icon: <ListOrdered size={18} />, label: '有序列表', description: '编号列表', type: 'ordered_list' },
  { icon: <CheckSquare size={18} />, label: '待办列表', description: '任务列表', type: 'task_list' },
  { icon: <Quote size={18} />, label: '引用', description: '引用块', type: 'blockquote' },
  { icon: <Minus size={18} />, label: '分隔线', description: '水平分隔线', type: 'divider' },
  { icon: <Code size={18} />, label: '代码块', description: '代码片段', type: 'code' },
  { icon: <Table size={18} />, label: '表格', description: '插入表格', type: 'table' },
  { icon: <Image size={18} />, label: '图片', description: '插入图片', type: 'image' },
  { icon: <FileText size={18} />, label: '文件', description: '附件', type: 'file' },
]

const shortcutMap: Record<string, string> = {
  paragraph: '',
  heading1: '# ',
  heading2: '## ',
  heading3: '### ',
  bullet_list: '- ',
  ordered_list: '1. ',
  task_list: '- [ ] ',
  blockquote: '> ',
  divider: '---',
  code: '```\n\n```',
  table: '| 列1 | 列2 | 列3 |\n| --- | --- | --- |\n|  |  |  |',
  image: '![alt](url)',
  file: '[文件名](url)',
}

export function BlockMenu() {
  const [open, setOpen] = useState(false)
  const [filter, setFilter] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const editor = document.querySelector('.milkdown .ProseMirror') as HTMLElement
      if (!editor) return

      if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
        const sel = window.getSelection()
        if (sel && sel.rangeCount > 0) {
          const range = sel.getRangeAt(0)
          const textBefore = range.startContainer.textContent?.slice(0, range.startOffset) || ''
          if (textBefore.endsWith('/') || textBefore === '/') {
            setOpen(true)
            setFilter('')
            setSelectedIndex(0)
          }
        }
      }
      if (e.key === 'Escape' && open) {
        setOpen(false)
      }
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [open])

  useEffect(() => {
    if (open) inputRef.current?.focus()
  }, [open])

  const filtered = blockItems.filter(
    (item) => item.label.includes(filter) || item.description.includes(filter)
  )

  function handleSelect(item: BlockMenuItem) {
    const shortcut = shortcutMap[item.type]
    if (shortcut) {
      const editor = document.querySelector('.milkdown .ProseMirror') as HTMLElement
      if (editor) {
        document.execCommand('insertText', false, shortcut)
      }
    }
    setOpen(false)
    setFilter('')
  }

  if (!open) return null

  return (
    <div
      className="absolute bottom-4 left-1/2 -translate-x-1/2 z-50 animate-fade-in"
      style={{ width: '320px' }}
    >
      <div
        className="rounded-xl shadow-2xl overflow-hidden"
        style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}
      >
        <div className="px-3 py-2" style={{ borderBottom: '1px solid var(--color-border)' }}>
          <input
            ref={inputRef}
            type="text"
            placeholder="搜索块类型..."
            value={filter}
            onChange={(e) => { setFilter(e.target.value); setSelectedIndex(0) }}
            className="bg-transparent outline-none text-sm w-full"
            style={{ color: 'var(--color-text-primary)' }}
            onKeyDown={(e) => {
              if (e.key === 'ArrowDown') {
                e.preventDefault()
                setSelectedIndex((i) => Math.min(i + 1, filtered.length - 1))
              } else if (e.key === 'ArrowUp') {
                e.preventDefault()
                setSelectedIndex((i) => Math.max(i - 1, 0))
              } else if (e.key === 'Enter' && filtered[selectedIndex]) {
                handleSelect(filtered[selectedIndex])
              }
            }}
          />
        </div>
        <div className="max-h-64 overflow-y-auto py-1">
          {filtered.map((item, i) => (
            <button
              key={item.type}
              onClick={() => handleSelect(item)}
              onMouseEnter={() => setSelectedIndex(i)}
              className="w-full flex items-center gap-3 px-3 py-2 text-left transition-colors"
              style={{
                background: i === selectedIndex ? 'var(--color-bg-tertiary)' : 'transparent',
                color: i === selectedIndex ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
              }}
            >
              <span style={{ color: 'var(--color-accent)' }}>{item.icon}</span>
              <div>
                <div className="text-sm font-medium">{item.label}</div>
                <div className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{item.description}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

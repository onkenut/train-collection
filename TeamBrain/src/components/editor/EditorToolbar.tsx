import { Bold, Italic, List, ListOrdered, Quote, Code, Heading1, Heading2, Heading3, SeparatorHorizontal, Save, Eye, Columns2, Edit3 } from 'lucide-react'
import { useEditorStore, type ViewMode } from '@/stores/editorStore'
import { cn } from '@/lib/utils'

interface EditorToolbarProps {
  onSave: () => void
}

export function EditorToolbar({ onSave }: EditorToolbarProps) {
  const { viewMode, setViewMode, isDirty, isSaving } = useEditorStore()

  const blockButtons = [
    { icon: Heading1, label: '标题1', action: () => insertMarkdown('# ') },
    { icon: Heading2, label: '标题2', action: () => insertMarkdown('## ') },
    { icon: Heading3, label: '标题3', action: () => insertMarkdown('### ') },
    { icon: Bold, label: '粗体', action: () => wrapSelection('**', '**') },
    { icon: Italic, label: '斜体', action: () => wrapSelection('*', '*') },
    { icon: List, label: '无序列表', action: () => insertMarkdown('- ') },
    { icon: ListOrdered, label: '有序列表', action: () => insertMarkdown('1. ') },
    { icon: Quote, label: '引用', action: () => insertMarkdown('> ') },
    { icon: Code, label: '代码', action: () => wrapSelection('`', '`') },
    { icon: SeparatorHorizontal, label: '分隔线', action: () => insertMarkdown('\n---\n') },
  ]

  const viewModes: { mode: ViewMode; icon: typeof Edit3; label: string }[] = [
    { mode: 'edit', icon: Edit3, label: '编辑' },
    { mode: 'split', icon: Columns2, label: '分屏' },
    { mode: 'preview', icon: Eye, label: '预览' },
  ]

  function insertMarkdown(prefix: string) {
    const editor = document.querySelector('.milkdown .ProseMirror') as HTMLElement
    if (editor) editor.focus()
  }

  function wrapSelection(before: string, after: string) {
    const editor = document.querySelector('.milkdown .ProseMirror') as HTMLElement
    if (editor) editor.focus()
  }

  return (
    <div
      className="flex items-center gap-1 px-4 py-2 border-b"
      style={{ background: 'var(--color-bg-secondary)', borderColor: 'var(--color-border)' }}
    >
      <div className="flex items-center gap-0.5">
        {blockButtons.map((btn, i) => (
          <button
            key={i}
            onClick={btn.action}
            title={btn.label}
            className="p-1.5 rounded-md transition-colors"
            style={{ color: 'var(--color-text-secondary)' }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-bg-tertiary)'; e.currentTarget.style.color = 'var(--color-text-primary)' }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--color-text-secondary)' }}
          >
            <btn.icon size={16} />
          </button>
        ))}
      </div>

      <div className="mx-2 h-5" style={{ borderLeft: '1px solid var(--color-border)' }} />

      <div className="flex items-center gap-0.5">
        {viewModes.map(({ mode, icon: Icon, label }) => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            title={label}
            className={cn('p-1.5 rounded-md transition-colors')}
            style={{
              color: viewMode === mode ? 'var(--color-accent)' : 'var(--color-text-muted)',
              background: viewMode === mode ? 'var(--color-accent-light)' : 'transparent',
            }}
          >
            <Icon size={16} />
          </button>
        ))}
      </div>

      <div className="flex-1" />

      <button
        onClick={onSave}
        disabled={isSaving || !isDirty}
        className="btn-primary text-xs px-3 py-1 flex items-center gap-1.5"
        style={{
          opacity: isSaving || !isDirty ? 0.5 : 1,
          cursor: isSaving || !isDirty ? 'not-allowed' : 'pointer',
        }}
      >
        <Save size={14} />
        {isSaving ? '保存中...' : '保存'}
      </button>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Sparkles, History } from 'lucide-react'
import { usePageStore } from '@/stores/pageStore'
import { useEditorStore } from '@/stores/editorStore'
import { useUIStore } from '@/stores/uiStore'
import { pageApi } from '@/api/endpoints'
import { MilkdownEditor } from '@/components/editor/MilkdownEditor'
import { useAutoSave } from '@/hooks/useAutoSave'
import { useToast } from '@/components/common/Toast'
import { EmptyState } from '@/components/common/EmptyState'

export default function EditorPage() {
  const { pageId, notebookId } = useParams<{ pageId: string; notebookId: string }>()
  const { currentPageId, setCurrentPage, setBlocks } = usePageStore()
  const { aiPanelOpen, versionPanelOpen } = useEditorStore()
  const { togglePanel } = useUIStore()
  const toast = useToast()
  const [content, setContent] = useState('')
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(true)

  useAutoSave({
    pageId: pageId || '',
    content,
    title,
  })

  useEffect(() => {
    if (pageId) loadPage()
  }, [pageId])

  async function loadPage() {
    if (!pageId) return
    setLoading(true)
    try {
      const data = await pageApi.get(pageId)
      setCurrentPage(pageId)
      setTitle(data.title)
      if (data.blocks) {
        setBlocks(data.blocks)
        setContent(blocksToMarkdown(data.blocks))
      }
    } catch {
      toast.error('加载页面失败')
    } finally {
      setLoading(false)
    }
  }

  function handleSave(markdown: string) {
    setContent(markdown)
    toast.success('已保存')
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-6 h-6 border-2 rounded-full animate-spin" style={{ borderColor: 'var(--color-accent)', borderTopColor: 'transparent' }} />
          <span className="text-sm" style={{ color: 'var(--color-text-muted)' }}>加载页面...</span>
        </div>
      </div>
    )
  }

  if (!pageId) {
    return (
      <EmptyState
        title="选择一个页面"
        description="从左侧页面列表选择或创建新页面"
      />
    )
  }

  return (
    <div className="h-full flex flex-col">
      <div
        className="flex items-center gap-3 px-6 py-3"
        style={{ borderBottom: '1px solid var(--color-border)' }}
      >
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="bg-transparent text-xl font-semibold outline-none flex-1"
          style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}
          placeholder="无标题页面"
        />
        <div className="flex items-center gap-1">
          <button
            onClick={() => togglePanel('ai')}
            className="p-2 rounded-lg transition-colors"
            style={{
              color: aiPanelOpen ? 'var(--color-ai-border)' : 'var(--color-text-muted)',
              background: aiPanelOpen ? 'var(--color-ai-bg)' : 'transparent',
            }}
            onMouseEnter={(e) => {
              if (!aiPanelOpen) e.currentTarget.style.background = 'var(--color-bg-tertiary)'
            }}
            onMouseLeave={(e) => {
              if (!aiPanelOpen) e.currentTarget.style.background = 'transparent'
            }}
            title="AI 助手"
          >
            <Sparkles size={18} />
          </button>
          <button
            onClick={() => togglePanel('version')}
            className="p-2 rounded-lg transition-colors"
            style={{
              color: versionPanelOpen ? 'var(--color-accent)' : 'var(--color-text-muted)',
              background: versionPanelOpen ? 'var(--color-accent-light)' : 'transparent',
            }}
            onMouseEnter={(e) => {
              if (!versionPanelOpen) e.currentTarget.style.background = 'var(--color-bg-tertiary)'
            }}
            onMouseLeave={(e) => {
              if (!versionPanelOpen) e.currentTarget.style.background = 'transparent'
            }}
            title="版本历史"
          >
            <History size={18} />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <MilkdownEditor
          content={content}
          pageId={pageId}
          onSave={handleSave}
        />
      </div>
    </div>
  )
}

function blocksToMarkdown(blocks: any[]): string {
  return blocks
    .sort((a, b) => a.sort_order - b.sort_order)
    .map((block) => {
      switch (block.type) {
        case 'heading1': return `# ${block.content}`
        case 'heading2': return `## ${block.content}`
        case 'heading3': return `### ${block.content}`
        case 'bullet_list': return `- ${block.content}`
        case 'ordered_list': return `1. ${block.content}`
        case 'task_list': return `- [ ] ${block.content}`
        case 'blockquote': return `> ${block.content}`
        case 'divider': return '---'
        case 'code': return `\`\`\`\n${block.content}\n\`\`\``
        default: return block.content
      }
    })
    .join('\n\n')
}

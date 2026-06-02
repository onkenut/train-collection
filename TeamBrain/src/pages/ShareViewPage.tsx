import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Lock } from 'lucide-react'
import { shareApi } from '@/api/endpoints'
import { usePageStore, type Page, type Block } from '@/stores/pageStore'
import { PreviewPane } from '@/components/editor/PreviewPane'
import { useToast } from '@/components/common/Toast'

export default function ShareViewPage() {
  const { shareId } = useParams<{ shareId: string }>()
  const [page, setPage] = useState<Page | null>(null)
  const [blocks, setBlocks] = useState<Block[]>([])
  const [loading, setLoading] = useState(true)
  const [needsPassword, setNeedsPassword] = useState(false)
  const [password, setPassword] = useState('')
  const toast = useToast()

  useEffect(() => {
    if (shareId) loadShare()
  }, [shareId])

  async function loadShare(pwd?: string) {
    if (!shareId) return
    setLoading(true)
    try {
      const data = await shareApi.getPublic(shareId, pwd)
      setPage(data)
      if (data.blocks) setBlocks(data.blocks)
      setNeedsPassword(false)
    } catch (e: any) {
      if (e.status === 401 || e.status === 403) {
        setNeedsPassword(true)
      } else {
        toast.error('该分享不存在或已过期')
      }
    } finally {
      setLoading(false)
    }
  }

  function handleSubmitPassword(e: React.FormEvent) {
    e.preventDefault()
    loadShare(password)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--color-bg-primary)' }}>
        <div className="w-6 h-6 border-2 rounded-full animate-spin" style={{ borderColor: 'var(--color-accent)', borderTopColor: 'transparent' }} />
      </div>
    )
  }

  if (needsPassword) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--color-bg-primary)' }}>
        <div className="card p-8 max-w-sm w-full mx-4">
          <div className="flex items-center justify-center mb-4">
            <Lock size={32} style={{ color: 'var(--color-accent)' }} />
          </div>
          <h2
            className="text-lg font-semibold text-center mb-2"
            style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}
          >
            需要密码访问
          </h2>
          <p className="text-sm text-center mb-4" style={{ color: 'var(--color-text-muted)' }}>
            该分享已设置访问密码
          </p>
          <form onSubmit={handleSubmitPassword}>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="输入访问密码"
              className="input-base mb-3"
            />
            <button type="submit" className="btn-primary w-full">
              访问
            </button>
          </form>
        </div>
      </div>
    )
  }

  if (!page) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--color-bg-primary)' }}>
        <p style={{ color: 'var(--color-text-muted)' }}>分享不存在或已过期</p>
      </div>
    )
  }

  const markdown = blocksToMarkdown(blocks)

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-bg-primary)' }}>
      <div className="max-w-3xl mx-auto px-6 py-12">
        <h1
          className="text-3xl font-bold mb-2"
          style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}
        >
          {page.icon} {page.title}
        </h1>
        <p className="text-xs mb-8" style={{ color: 'var(--color-text-muted)' }}>
          通过分享链接查看 · 只读模式
        </p>
        <PreviewPane content={markdown} />
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

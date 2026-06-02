import { useState } from 'react'
import { Sparkles, PenLine, FileText, Languages, BrainCircuit, RotateCcw } from 'lucide-react'
import { useAIStore, type AIAction } from '@/stores/aiStore'
import { useEditorStore } from '@/stores/editorStore'
import { aiApi } from '@/api/endpoints'
import { AIContentBlock } from '@/components/editor/AIContentBlock'
import { AIUsageBar } from './AIUsageBar'
import { useToast } from '@/components/common/Toast'

const actions: { type: AIAction; icon: typeof Sparkles; label: string; desc: string }[] = [
  { type: 'continue', icon: PenLine, label: '续写', desc: '基于上下文继续写作' },
  { type: 'summarize', icon: FileText, label: '摘要', desc: '生成内容摘要' },
  { type: 'rewrite', icon: RotateCcw, label: '改写', desc: '改写选中文本' },
  { type: 'translate', icon: Languages, label: '翻译', desc: '翻译为其他语言' },
  { type: 'brainstorm', icon: BrainCircuit, label: '头脑风暴', desc: '生成创意想法' },
]

export function AIPanel() {
  const { generating, generatedContent, setGenerating, setGeneratedContent, resetGenerated } = useAIStore()
  const { isDirty } = useEditorStore()
  const toast = useToast()
  const [selectedAction, setSelectedAction] = useState<AIAction | null>(null)
  const [context, setContext] = useState('')

  async function handleAction(action: AIAction) {
    setSelectedAction(action)
    setGenerating(true)
    setGeneratedContent(null)
    try {
      const response = await aiApi.generate({
        action,
        content: context || '当前页面内容',
      })
      setGeneratedContent(response.generated_text)
      toast.success(response.cached ? '结果来自缓存' : `已生成，消耗 ${response.tokens_used} tokens`)
    } catch (e: any) {
      toast.error(e.message || 'AI 生成失败')
    } finally {
      setGenerating(false)
    }
  }

  function handleAccept() {
    resetGenerated()
    toast.success('AI 内容已接受')
  }

  function handleDiscard() {
    resetGenerated()
    toast.info('AI 内容已丢弃')
  }

  return (
    <div className="p-4 flex flex-col gap-4">
      <AIUsageBar />

      <div>
        <label className="text-xs font-medium mb-1.5 block" style={{ color: 'var(--color-text-muted)' }}>
          上下文内容
        </label>
        <textarea
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="选中文本将自动填入，也可手动输入..."
          rows={3}
          className="input-base resize-none"
        />
      </div>

      <div>
        <label className="text-xs font-medium mb-2 block" style={{ color: 'var(--color-text-muted)' }}>
          AI 操作
        </label>
        <div className="grid grid-cols-1 gap-2">
          {actions.map(({ type, icon: Icon, label, desc }) => (
            <button
              key={type}
              onClick={() => handleAction(type)}
              disabled={generating}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors"
              style={{
                background: selectedAction === type ? 'var(--color-accent-light)' : 'var(--color-bg-tertiary)',
                opacity: generating ? 0.5 : 1,
                border: '1px solid transparent',
              }}
              onMouseEnter={(e) => {
                if (selectedAction !== type) e.currentTarget.style.borderColor = 'var(--color-border-hover)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'transparent'
              }}
            >
              <Icon size={18} style={{ color: selectedAction === type ? 'var(--color-accent)' : 'var(--color-text-secondary)' }} />
              <div>
                <div className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>{label}</div>
                <div className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{desc}</div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {(generatedContent || generating) && (
        <div>
          <label className="text-xs font-medium mb-1.5 block" style={{ color: 'var(--color-text-muted)' }}>
            生成结果
          </label>
          <AIContentBlock
            content={generatedContent || ''}
            generating={generating}
            onAccept={handleAccept}
            onDiscard={handleDiscard}
          />
        </div>
      )}
    </div>
  )
}

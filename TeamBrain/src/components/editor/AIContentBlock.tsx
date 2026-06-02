import { Check, X } from 'lucide-react'
import { useState } from 'react'

interface AIContentBlockProps {
  content: string
  onAccept: () => void
  onDiscard: () => void
  generating?: boolean
}

export function AIContentBlock({ content, onAccept, onDiscard, generating }: AIContentBlockProps) {
  const [accepted, setAccepted] = useState(false)

  function handleAccept() {
    setAccepted(true)
    onAccept()
  }

  function handleDiscard() {
    onDiscard()
  }

  return (
    <div className={`ai-content-block ${accepted ? 'accepted' : ''}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          {generating ? (
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ background: 'var(--color-ai-border)', animationDelay: '0ms' }} />
                <span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ background: 'var(--color-ai-border)', animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ background: 'var(--color-ai-border)', animationDelay: '300ms' }} />
              </div>
              <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>AI 生成中...</span>
            </div>
          ) : (
            <div className="text-sm whitespace-pre-wrap" style={{ color: 'var(--color-text-primary)' }}>
              {content}
            </div>
          )}
        </div>

        {!accepted && !generating && (
          <div className="flex items-center gap-1 flex-shrink-0">
            <button
              onClick={handleAccept}
              className="p-1.5 rounded-lg transition-colors"
              style={{ color: 'var(--color-accent)' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-accent-light)' }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
              title="接受"
            >
              <Check size={16} />
            </button>
            <button
              onClick={handleDiscard}
              className="p-1.5 rounded-lg transition-colors"
              style={{ color: 'var(--color-danger)' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(239,68,68,0.1)' }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
              title="丢弃"
            >
              <X size={16} />
            </button>
          </div>
        )}

        {accepted && (
          <span className="text-xs flex-shrink-0 px-2 py-0.5 rounded" style={{ color: 'var(--color-accent)', background: 'var(--color-accent-light)' }}>
            AI
          </span>
        )}
      </div>
    </div>
  )
}

import { useEffect, useRef, useCallback } from 'react'
import { Editor, rootCtx, defaultValueCtx } from '@milkdown/core'
import { commonmark } from '@milkdown/preset-commonmark'
import { gfm } from '@milkdown/preset-gfm'
import { nord } from '@milkdown/theme-nord'
import { Milkdown, MilkdownProvider, useEditor, useInstance } from '@milkdown/react'
import { listener, listenerCtx } from '@milkdown/plugin-listener'
import { clipboard } from '@milkdown/plugin-clipboard'
import { cursor } from '@milkdown/plugin-cursor'
import { prism } from '@milkdown/plugin-prism'
import { useEditorStore } from '@/stores/editorStore'
import { EditorToolbar } from './EditorToolbar'
import { BlockMenu } from './BlockMenu'
import { PreviewPane } from './PreviewPane'

import '@milkdown/theme-nord/style.css'

interface MilkdownEditorProps {
  content: string
  pageId: string
  onSave: (markdown: string) => void
  readOnly?: boolean
}

export function MilkdownEditor({ content, pageId, onSave, readOnly = false }: MilkdownEditorProps) {
  const { viewMode, setDirty } = useEditorStore()
  const contentRef = useRef(content)
  const lastSavedRef = useRef(content)

  const handleContentChange = useCallback((markdown: string) => {
    contentRef.current = markdown
    if (markdown !== lastSavedRef.current) {
      setDirty(true)
    }
  }, [setDirty])

  const handleSave = useCallback(() => {
    if (contentRef.current !== lastSavedRef.current) {
      onSave(contentRef.current)
      lastSavedRef.current = contentRef.current
      setDirty(false)
    }
  }, [onSave, setDirty])

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        handleSave()
      }
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleSave])

  if (viewMode === 'preview') {
    return (
      <div className="milkdown h-full">
        <PreviewPane content={content} />
      </div>
    )
  }

  return (
    <div className="milkdown h-full flex flex-col">
      {!readOnly && <EditorToolbar onSave={handleSave} />}
      <div className="flex-1 overflow-y-auto">
        {viewMode === 'split' ? (
          <div className="flex h-full">
            <div className="flex-1 overflow-y-auto border-r" style={{ borderColor: 'var(--color-border)' }}>
              <MilkdownProvider>
                <EditorInner content={content} onChange={handleContentChange} />
              </MilkdownProvider>
            </div>
            <div className="flex-1 overflow-y-auto p-6 milkdown">
              <PreviewPane content={contentRef.current} />
            </div>
          </div>
        ) : (
          <MilkdownProvider>
            <EditorInner content={content} onChange={handleContentChange} />
          </MilkdownProvider>
        )}
      </div>
      {!readOnly && <BlockMenu />}
    </div>
  )
}

function EditorInner({ content, onChange }: { content: string; onChange: (md: string) => void }) {
  const { loading } = useEditor((root) =>
    Editor.make()
      .config((ctx) => {
        ctx.set(rootCtx, root)
        ctx.set(defaultValueCtx, content)
        ctx.get(listenerCtx).markdownUpdated((_ctx, markdown) => {
          onChange(markdown)
        })
      })
      .config(nord)
      .use(commonmark)
      .use(gfm)
      .use(listener)
      .use(clipboard)
      .use(cursor)
      .use(prism)
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="w-5 h-5 border-2 rounded-full animate-spin" style={{ borderColor: 'var(--color-accent)', borderTopColor: 'transparent' }} />
      </div>
    )
  }

  return <Milkdown />
}

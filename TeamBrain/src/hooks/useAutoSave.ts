import { useEffect, useRef, useCallback } from 'react'
import { useEditorStore } from '@/stores/editorStore'
import { saveDraft, markDraftSynced } from '@/lib/dexie'
import { pageApi } from '@/api/endpoints'
import { useToast } from '@/components/common/Toast'

interface UseAutoSaveOptions {
  pageId: string
  content: string
  title?: string
  interval?: number
}

export function useAutoSave({ pageId, content, title = '', interval = 5000 }: UseAutoSaveOptions) {
  const { setDirty, setSaving, setLastSavedAt } = useEditorStore()
  const toast = useToast()
  const timerRef = useRef<ReturnType<typeof setTimeout>>()
  const lastSavedContentRef = useRef(content)

  const save = useCallback(async () => {
    if (!pageId || content === lastSavedContentRef.current) return

    setSaving(true)
    try {
      await saveDraft(pageId, title, content)
      await pageApi.save(pageId, content, title)
      await markDraftSynced(pageId)
      lastSavedContentRef.current = content
      setDirty(false)
      setLastSavedAt(new Date().toISOString())
    } catch {
      try {
        await saveDraft(pageId, title, content)
        setDirty(false)
      } catch {
        toast.error('自动保存失败')
      }
    } finally {
      setSaving(false)
    }
  }, [pageId, content, title, setDirty, setSaving, setLastSavedAt, toast])

  useEffect(() => {
    if (content === lastSavedContentRef.current) return
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(save, interval)
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [content, save, interval])

  useEffect(() => {
    function handleBlur() {
      if (content !== lastSavedContentRef.current) {
        save()
      }
    }
    window.addEventListener('blur', handleBlur)
    return () => window.removeEventListener('blur', handleBlur)
  }, [content, save])

  return { save }
}

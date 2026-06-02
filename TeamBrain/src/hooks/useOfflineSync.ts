import { useEffect, useState, useCallback, useRef } from 'react'
import { getUnsyncedDrafts, markDraftSynced } from '@/lib/dexie'
import { syncApi, type SyncPayload } from '@/api/endpoints'
import { useToast } from '@/components/common/Toast'

interface OfflineSyncState {
  isOnline: boolean
  hasUnsynced: boolean
  syncing: boolean
  lastSyncAt: string | null
}

export function useOfflineSync() {
  const [state, setState] = useState<OfflineSyncState>({
    isOnline: navigator.onLine,
    hasUnsynced: false,
    syncing: false,
    lastSyncAt: null,
  })
  const toast = useToast()
  const syncIntervalRef = useRef<ReturnType<typeof setInterval>>()

  const checkUnsynced = useCallback(async () => {
    try {
      const drafts = await getUnsyncedDrafts()
      setState((s) => ({ ...s, hasUnsynced: drafts.length > 0 }))
    } catch {
      // ignore
    }
  }, [])

  const sync = useCallback(async () => {
    if (!navigator.onLine || state.syncing) return

    const drafts = await getUnsyncedDrafts()
    if (drafts.length === 0) return

    setState((s) => ({ ...s, syncing: true }))
    try {
      const payload: SyncPayload = {
        pages: drafts.map((d) => ({
          id: d.page_id,
          title: d.title,
          blocks: [],
          updated_at: d.updated_at,
          checksum: '',
        })),
      }
      await syncApi.push(payload)
      for (const draft of drafts) {
        await markDraftSynced(draft.page_id)
      }
      setState((s) => ({
        ...s,
        syncing: false,
        hasUnsynced: false,
        lastSyncAt: new Date().toISOString(),
      }))
      toast.success(`已同步 ${drafts.length} 条离线修改`)
    } catch {
      setState((s) => ({ ...s, syncing: false }))
    }
  }, [state.syncing, toast])

  useEffect(() => {
    function handleOnline() {
      setState((s) => ({ ...s, isOnline: true }))
      sync()
    }
    function handleOffline() {
      setState((s) => ({ ...s, isOnline: false }))
    }
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [sync])

  useEffect(() => {
    checkUnsynced()
    syncIntervalRef.current = setInterval(checkUnsynced, 30000)
    return () => {
      if (syncIntervalRef.current) clearInterval(syncIntervalRef.current)
    }
  }, [checkUnsynced])

  return { ...state, sync, checkUnsynced }
}

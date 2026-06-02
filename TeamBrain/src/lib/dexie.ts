import Dexie, { type Table } from 'dexie'

export interface OfflinePageDraft {
  id: string
  page_id: string
  title: string
  content: string
  updated_at: string
  synced: boolean
}

class MindVaultDB extends Dexie {
  drafts!: Table<OfflinePageDraft, string>

  constructor() {
    super('mindvault')
    this.version(1).stores({
      drafts: 'id, page_id, synced, updated_at',
    })
  }
}

export const db = new MindVaultDB()

export async function saveDraft(pageId: string, title: string, content: string): Promise<void> {
  const id = `draft-${pageId}`
  await db.drafts.put({
    id,
    page_id: pageId,
    title,
    content,
    updated_at: new Date().toISOString(),
    synced: false,
  })
}

export async function getDraft(pageId: string): Promise<OfflinePageDraft | undefined> {
  return db.drafts.get(`draft-${pageId}`)
}

export async function markDraftSynced(pageId: string): Promise<void> {
  await db.drafts.update(`draft-${pageId}`, { synced: true })
}

export async function getUnsyncedDrafts(): Promise<OfflinePageDraft[]> {
  return db.drafts.where('synced').equals(0).toArray()
}

export async function deleteDraft(pageId: string): Promise<void> {
  await db.drafts.delete(`draft-${pageId}`)
}

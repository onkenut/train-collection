import api from './client'
import type { Notebook } from '@/stores/notebookStore'
import type { Page, Block } from '@/stores/pageStore'
import type { Tag } from '@/stores/tagStore'
import type { AIAction } from '@/stores/aiStore'

export interface PageVersion {
  id: string
  page_id: string
  snapshot: string
  char_count: number
  created_at: string
}

export interface SearchResult {
  page_id: string
  page_title: string
  notebook_id: string
  notebook_name: string
  snippet: string
  rank: number
}

export interface ShareLink {
  id: string
  page_id: string
  token: string
  password: string | null
  expires_at: string | null
  created_at: string
}

export interface AIRequest {
  action: AIAction
  content: string
  context?: string
  params?: {
    tone?: 'formal' | 'casual'
    rewrite_type?: 'polish' | 'simplify' | 'expand'
    target_lang?: string
  }
}

export interface AIResponse {
  id: string
  generated_text: string
  tokens_used: number
  cached: boolean
}

export interface AIUsageResponse {
  total_tokens: number
  budget_limit: number
  month: number
  year: number
}

export interface AIConfigResponse {
  api_key: string
  base_url: string
  model: string
  monthly_budget: number
}

export interface VersionDiff {
  additions: string[]
  deletions: string[]
}

export interface SyncPayload {
  pages: Array<{
    id: string
    title: string
    blocks: Block[]
    updated_at: string
    checksum: string
  }>
}

export const notebookApi = {
  list: () => api.get<Notebook[]>('/notebooks'),
  create: (data: Partial<Notebook>) => api.post<Notebook>('/notebooks', data),
  update: (id: string, data: Partial<Notebook>) => api.put<Notebook>(`/notebooks/${id}`, data),
  delete: (id: string) => api.delete<void>(`/notebooks/${id}`),
  reorder: (ids: string[]) => api.put<void>('/notebooks/reorder', { ids }),
}

export const pageApi = {
  list: (notebookId: string) => api.get<Page[]>(`/notebooks/${notebookId}/pages`),
  create: (notebookId: string, data: Partial<Page>) => api.post<Page>(`/notebooks/${notebookId}/pages`, data),
  get: (id: string) => api.get<Page & { blocks: Block[] }>(`/pages/${id}`),
  update: (id: string, data: Partial<Page>) => api.put<Page>(`/pages/${id}`, data),
  delete: (id: string) => api.delete<void>(`/pages/${id}`),
  move: (id: string, parentId: string | null, sortOrder: number) =>
    api.put<void>(`/pages/${id}/move`, { parent_id: parentId, sort_order: sortOrder }),
  save: (id: string, blocks: Block[]) => api.post<void>(`/pages/${id}/save`, { blocks }),
  fromTemplate: (templateId: string) => api.post<Page>(`/pages/from-template/${templateId}`),
}

export const blockApi = {
  list: (pageId: string) => api.get<Block[]>(`/pages/${pageId}/blocks`),
  create: (pageId: string, data: Partial<Block>) => api.post<Block>(`/pages/${pageId}/blocks`, data),
  update: (id: string, data: Partial<Block>) => api.put<Block>(`/blocks/${id}`, data),
  delete: (id: string) => api.delete<void>(`/blocks/${id}`),
  reorder: (pageId: string, blockIds: string[]) =>
    api.put<void>(`/pages/${pageId}/blocks/reorder`, { ids: blockIds }),
}

export const aiApi = {
  generate: (data: AIRequest) => api.post<AIResponse>('/ai/generate', data),
  getUsage: () => api.get<AIUsageResponse>('/ai/usage'),
  getConfig: () => api.get<AIConfigResponse>('/ai/config'),
  updateConfig: (data: Partial<AIConfigResponse>) => api.put<AIConfigResponse>('/ai/config', data),
}

export const versionApi = {
  list: (pageId: string) => api.get<PageVersion[]>(`/pages/${pageId}/versions`),
  get: (id: string) => api.get<PageVersion>(`/versions/${id}`),
  restore: (id: string) => api.post<Page>(`/versions/${id}/restore`),
  copy: (id: string) => api.post<Page>(`/versions/${id}/copy`),
  diff: (id: string, targetVersionId: string) =>
    api.get<VersionDiff>(`/versions/${id}/diff`, { target_version_id: targetVersionId }),
}

export const searchApi = {
  search: (params: {
    q: string
    notebook_id?: string
    date_from?: string
    date_to?: string
    tag?: string
  }) => api.get<SearchResult[]>('/search', params),
}

export const tagApi = {
  list: () => api.get<Tag[]>('/tags'),
  addPageTag: (pageId: string, tagId: string) => api.post<void>(`/pages/${pageId}/tags`, { tag_id: tagId }),
  removePageTag: (pageId: string, tagId: string) => api.delete<void>(`/pages/${pageId}/tags/${tagId}`),
  getTagPages: (tagId: string) => api.get<Page[]>(`/tags/${tagId}/pages`),
}

export const importExportApi = {
  importMarkdown: (files: File[]) => {
    const formData = new FormData()
    files.forEach((f) => formData.append('files', f))
    return api.upload<{ imported: number }>('/import/markdown', formData)
  },
  importNotion: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.upload<{ imported: number }>('/import/notion', formData)
  },
  exportPage: (id: string, format: 'markdown' | 'html' | 'pdf') =>
    api.get<{ task_id: string }>(`/pages/${id}/export`, { format }),
  exportNotebook: (id: string) => api.post<{ task_id: string }>(`/notebooks/${id}/export`),
  getExportStatus: (taskId: string) => api.get<{ status: string; progress: number }>(`/export/${taskId}/status`),
  downloadExport: (taskId: string) => `${import.meta.env.VITE_API_BASE_URL || '/api'}/export/${taskId}/download`,
}

export const shareApi = {
  create: (pageId: string, data?: { password?: string; expires_at?: string }) =>
    api.post<ShareLink>(`/pages/${pageId}/share`, data),
  list: () => api.get<ShareLink[]>('/shares'),
  revoke: (id: string) => api.delete<void>(`/shares/${id}`),
  getPublic: (token: string, password?: string) =>
    api.post<Page & { blocks: Block[] }>(`/share/${token}`, { password }),
}

export const syncApi = {
  push: (payload: SyncPayload) => api.post<void>('/sync', payload),
  pull: (since: string) => api.get<SyncPayload>('/sync/changes', { since }),
}

export const backupApi = {
  exportAll: () => api.post<{ task_id: string }>('/backup/export'),
  importBackup: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.upload<{ restored: number }>('/backup/import', formData)
  },
}

import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { BookOpen, Plus } from 'lucide-react'
import { useNotebookStore } from '@/stores/notebookStore'
import { usePageStore } from '@/stores/pageStore'
import { notebookApi, pageApi } from '@/api/endpoints'
import { EmptyState } from '@/components/common/EmptyState'
import { useToast } from '@/components/common/Toast'

export default function WorkspacePage() {
  const { notebookId } = useParams<{ notebookId?: string }>()
  const { notebooks, currentNotebookId, setCurrentNotebook, setNotebooks } = useNotebookStore()
  const { pages, setPages, addPage } = usePageStore()
  const navigate = useNavigate()
  const toast = useToast()

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    if (notebookId && notebookId !== currentNotebookId) {
      setCurrentNotebook(notebookId)
      loadPages(notebookId)
    }
  }, [notebookId])

  async function loadData() {
    try {
      const data = await notebookApi.list()
      setNotebooks(data)
      if (data.length > 0 && !notebookId) {
        setCurrentNotebook(data[0].id)
        loadPages(data[0].id)
      }
    } catch {
      toast.error('加载数据失败')
    }
  }

  async function loadPages(nbId: string) {
    try {
      const data = await pageApi.list(nbId)
      setPages(data)
    } catch {
      toast.error('加载页面列表失败')
    }
  }

  async function handleCreatePage() {
    if (!currentNotebookId) return
    try {
      const page = await pageApi.create(currentNotebookId, {
        title: '无标题页面',
        icon: '📄',
      })
      addPage(page)
      navigate(`/notebook/${currentNotebookId}/page/${page.id}`)
      toast.success('页面已创建')
    } catch {
      toast.error('创建页面失败')
    }
  }

  const notebook = notebooks.find((n) => n.id === (notebookId || currentNotebookId))

  return (
    <div className="h-full flex flex-col">
      {notebook ? (
        <>
          <div
            className="flex items-center justify-between px-6 py-4"
            style={{ borderBottom: '1px solid var(--color-border)' }}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{notebook.icon}</span>
              <div>
                <h2
                  className="text-lg font-semibold"
                  style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}
                >
                  {notebook.name}
                </h2>
                <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                  {pages.length} 个页面
                </p>
              </div>
            </div>
            <button onClick={handleCreatePage} className="btn-primary flex items-center gap-2">
              <Plus size={16} />
              新建页面
            </button>
          </div>

          {pages.length === 0 ? (
            <EmptyState
              icon={<BookOpen size={28} style={{ color: 'var(--color-text-muted)' }} />}
              title="暂无页面"
              description="点击上方按钮创建第一个页面"
              action={
                <button onClick={handleCreatePage} className="btn-primary flex items-center gap-2">
                  <Plus size={16} />
                  新建页面
                </button>
              }
            />
          ) : (
            <div className="flex-1 overflow-y-auto p-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {pages
                  .filter((p) => !p.parent_id)
                  .map((page) => (
                    <button
                      key={page.id}
                      onClick={() => navigate(`/notebook/${notebook.id}/page/${page.id}`)}
                      className="card text-left group transition-all"
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = 'var(--color-accent)'
                        e.currentTarget.style.transform = 'translateY(-2px)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = 'var(--color-border)'
                        e.currentTarget.style.transform = 'translateY(0)'
                      }}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span>{page.icon}</span>
                        <h3
                          className="text-sm font-medium truncate"
                          style={{ color: 'var(--color-text-primary)' }}
                        >
                          {page.title}
                        </h3>
                      </div>
                      <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                        {new Date(page.updated_at).toLocaleDateString('zh-CN')}
                      </p>
                    </button>
                  ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <EmptyState
          icon={<BookOpen size={28} style={{ color: 'var(--color-text-muted)' }} />}
          title="欢迎使用 MindVault"
          description="从左侧选择或创建一个笔记本开始"
        />
      )}
    </div>
  )
}

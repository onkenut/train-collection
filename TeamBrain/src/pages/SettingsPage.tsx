import { useState } from 'react'
import { Settings as SettingsIcon, Sparkles, Download, HardDrive, Share2 } from 'lucide-react'
import { AIConfigForm } from '@/components/ai/AIConfigForm'
import { AIUsageBar } from '@/components/ai/AIUsageBar'
import { importExportApi, shareApi, backupApi } from '@/api/endpoints'
import { useToast } from '@/components/common/Toast'

type SettingsTab = 'ai' | 'import-export' | 'backup' | 'shares'

const tabs: { id: SettingsTab; icon: typeof SettingsIcon; label: string }[] = [
  { id: 'ai', icon: Sparkles, label: 'AI 配置' },
  { id: 'import-export', icon: Download, label: '导入导出' },
  { id: 'backup', icon: HardDrive, label: '备份管理' },
  { id: 'shares', icon: Share2, label: '分享管理' },
]

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('ai')
  const toast = useToast()

  async function handleImportMarkdown(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files
    if (!files || files.length === 0) return
    try {
      const result = await importExportApi.importMarkdown(Array.from(files))
      toast.success(`已导入 ${result.imported} 个文件`)
    } catch {
      toast.error('导入失败')
    }
    e.target.value = ''
  }

  async function handleImportNotion(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const result = await importExportApi.importNotion(file)
      toast.success(`已导入 ${result.imported} 个页面`)
    } catch {
      toast.error('导入失败')
    }
    e.target.value = ''
  }

  async function handleExportBackup() {
    try {
      await backupApi.exportAll()
      toast.success('备份导出已开始')
    } catch {
      toast.error('导出备份失败')
    }
  }

  async function handleImportBackup(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const result = await backupApi.importBackup(file)
      toast.success(`已恢复 ${result.restored} 条数据`)
    } catch {
      toast.error('恢复备份失败')
    }
    e.target.value = ''
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-4xl mx-auto px-6 py-8">
        <h2
          className="text-2xl font-bold mb-6"
          style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}
        >
          <SettingsIcon size={24} className="inline mr-2" />
          设置
        </h2>

        <div className="flex gap-6">
          <nav className="w-48 flex-shrink-0">
            {tabs.map(({ id, icon: Icon, label }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-left transition-colors mb-1"
                style={{
                  color: activeTab === id ? 'var(--color-accent)' : 'var(--color-text-secondary)',
                  background: activeTab === id ? 'var(--color-accent-light)' : 'transparent',
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== id) e.currentTarget.style.background = 'var(--color-bg-tertiary)'
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== id) e.currentTarget.style.background = 'transparent'
                }}
              >
                <Icon size={16} />
                {label}
              </button>
            ))}
          </nav>

          <div className="flex-1 card p-6">
            {activeTab === 'ai' && (
              <div>
                <h3 className="text-lg font-semibold mb-4" style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}>
                  AI 配置
                </h3>
                <AIUsageBar />
                <div className="mt-6">
                  <AIConfigForm />
                </div>
              </div>
            )}

            {activeTab === 'import-export' && (
              <div>
                <h3 className="text-lg font-semibold mb-4" style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}>
                  导入导出
                </h3>

                <div className="space-y-6">
                  <div>
                    <h4 className="text-sm font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>
                      导入 Markdown
                    </h4>
                    <p className="text-xs mb-2" style={{ color: 'var(--color-text-muted)' }}>
                      批量导入 .md 文件，每个文件创建为一个页面
                    </p>
                    <label className="btn-secondary inline-flex items-center gap-2 cursor-pointer">
                      <Download size={16} />
                      选择 Markdown 文件
                      <input type="file" multiple accept=".md,.markdown" onChange={handleImportMarkdown} className="hidden" />
                    </label>
                  </div>

                  <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '1.5rem' }}>
                    <h4 className="text-sm font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>
                      导入 Notion
                    </h4>
                    <p className="text-xs mb-2" style={{ color: 'var(--color-text-muted)' }}>
                      导入 Notion 导出的 ZIP 文件
                    </p>
                    <label className="btn-secondary inline-flex items-center gap-2 cursor-pointer">
                      <Download size={16} />
                      选择 Notion 导出
                      <input type="file" accept=".zip" onChange={handleImportNotion} className="hidden" />
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'backup' && (
              <div>
                <h3 className="text-lg font-semibold mb-4" style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}>
                  备份管理
                </h3>
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>
                      导出备份
                    </h4>
                    <p className="text-xs mb-2" style={{ color: 'var(--color-text-muted)' }}>
                      导出完整数据库和附件
                    </p>
                    <button onClick={handleExportBackup} className="btn-primary flex items-center gap-2">
                      <HardDrive size={16} />
                      导出备份
                    </button>
                  </div>
                  <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
                    <h4 className="text-sm font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>
                      恢复备份
                    </h4>
                    <p className="text-xs mb-2" style={{ color: 'var(--color-text-muted)' }}>
                      从备份文件恢复数据（将覆盖当前数据）
                    </p>
                    <label className="btn-secondary inline-flex items-center gap-2 cursor-pointer">
                      <HardDrive size={16} />
                      选择备份文件
                      <input type="file" accept=".zip,.db" onChange={handleImportBackup} className="hidden" />
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'shares' && (
              <ShareManagement />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function ShareManagement() {
  const [shares, setShares] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const toast = useToast()

  useState(() => {
    loadShares()
  })

  async function loadShares() {
    try {
      const data = await shareApi.list()
      setShares(data)
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }

  async function handleRevoke(id: string) {
    if (!confirm('确定撤销该分享链接？')) return
    try {
      await shareApi.revoke(id)
      setShares(shares.filter((s) => s.id !== id))
      toast.success('已撤销分享')
    } catch {
      toast.error('撤销失败')
    }
  }

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4" style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}>
        分享管理
      </h3>
      {loading ? (
        <div className="text-sm" style={{ color: 'var(--color-text-muted)' }}>加载中...</div>
      ) : shares.length === 0 ? (
        <div className="text-sm" style={{ color: 'var(--color-text-muted)' }}>暂无活跃的分享链接</div>
      ) : (
        <div className="space-y-2">
          {shares.map((share) => (
            <div
              key={share.id}
              className="flex items-center justify-between p-3 rounded-lg"
              style={{ background: 'var(--color-bg-tertiary)' }}
            >
              <div>
                <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
                  {share.token}
                </p>
                <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                  创建于 {new Date(share.created_at).toLocaleDateString('zh-CN')}
                  {share.expires_at && ` · 过期于 ${new Date(share.expires_at).toLocaleDateString('zh-CN')}`}
                </p>
              </div>
              <button
                onClick={() => handleRevoke(share.id)}
                className="text-xs px-2 py-1 rounded transition-colors"
                style={{ color: 'var(--color-danger)' }}
                onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(239,68,68,0.1)' }}
                onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
              >
                撤销
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

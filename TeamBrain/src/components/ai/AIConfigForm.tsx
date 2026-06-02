import { useState, useEffect } from 'react'
import { Save } from 'lucide-react'
import { useAIStore } from '@/stores/aiStore'
import { aiApi } from '@/api/endpoints'
import { useToast } from '@/components/common/Toast'

export function AIConfigForm() {
  const { config, setConfig } = useAIStore()
  const toast = useToast()
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState(config)

  useEffect(() => {
    loadConfig()
  }, [])

  async function loadConfig() {
    try {
      const data = await aiApi.getConfig()
      setConfig(data)
      setForm(data)
    } catch {
      // use defaults
    }
  }

  async function handleSave() {
    setSaving(true)
    try {
      await aiApi.updateConfig(form)
      setConfig(form)
      toast.success('AI 配置已保存')
    } catch (e: any) {
      toast.error('保存配置失败')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium mb-1.5 block" style={{ color: 'var(--color-text-secondary)' }}>
          API Base URL
        </label>
        <input
          type="url"
          value={form.base_url}
          onChange={(e) => setForm((f) => ({ ...f, base_url: e.target.value }))}
          placeholder="https://api.openai.com/v1"
          className="input-base"
        />
      </div>

      <div>
        <label className="text-sm font-medium mb-1.5 block" style={{ color: 'var(--color-text-secondary)' }}>
          API Key
        </label>
        <input
          type="password"
          value={form.api_key}
          onChange={(e) => setForm((f) => ({ ...f, api_key: e.target.value }))}
          placeholder="sk-..."
          className="input-base"
        />
        <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>
          密钥仅存储在本地服务器，不会上传
        </p>
      </div>

      <div>
        <label className="text-sm font-medium mb-1.5 block" style={{ color: 'var(--color-text-secondary)' }}>
          模型
        </label>
        <input
          type="text"
          value={form.model}
          onChange={(e) => setForm((f) => ({ ...f, model: e.target.value }))}
          placeholder="gpt-3.5-turbo"
          className="input-base"
        />
        <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>
          支持所有 OpenAI 兼容 API，包括 Ollama 本地模型
        </p>
      </div>

      <div>
        <label className="text-sm font-medium mb-1.5 block" style={{ color: 'var(--color-text-secondary)' }}>
          月度 Token 预算
        </label>
        <input
          type="number"
          value={form.monthly_budget}
          onChange={(e) => setForm((f) => ({ ...f, monthly_budget: parseInt(e.target.value) || 0 }))}
          min={0}
          className="input-base"
        />
      </div>

      <button
        onClick={handleSave}
        disabled={saving}
        className="btn-primary flex items-center gap-2"
        style={{ opacity: saving ? 0.5 : 1 }}
      >
        <Save size={16} />
        {saving ? '保存中...' : '保存配置'}
      </button>
    </div>
  )
}

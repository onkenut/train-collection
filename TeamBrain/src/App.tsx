import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { ContextMenu } from '@/components/common/ContextMenu'
import { ToastContainer } from '@/components/common/Toast'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { useUIStore, type ContextMenuItem } from '@/stores/uiStore'
import WorkspacePage from '@/pages/WorkspacePage'
import EditorPage from '@/pages/EditorPage'
import SearchPage from '@/pages/SearchPage'
import SettingsPage from '@/pages/SettingsPage'
import ShareViewPage from '@/pages/ShareViewPage'

function ContextMenuWrapper() {
  const { contextMenu, hideContextMenu } = useUIStore()

  if (!contextMenu) return null

  const menuItems: ContextMenuItem[] = contextMenu.type === 'notebook'
    ? [
        { label: '重命名', icon: '✏️', action: 'rename' },
        { label: '删除', icon: '🗑️', action: 'delete', danger: true, divider: true },
      ]
    : [
        { label: '新建子页面', icon: '📄', action: 'create_child' },
        { label: '重命名', icon: '✏️', action: 'rename' },
        { label: '删除', icon: '🗑️', action: 'delete', danger: true, divider: true },
      ]

  return (
    <ContextMenu
      items={menuItems}
      x={contextMenu.x}
      y={contextMenu.y}
      onAction={(action) => {
        const event = new CustomEvent(`${contextMenu.type}-action`, {
          detail: { action, targetId: contextMenu.targetId },
        })
        window.dispatchEvent(event)
        hideContextMenu()
      }}
      onClose={hideContextMenu}
    />
  )
}

function ThemeInitializer() {
  const { theme } = useUIStore()
  if (typeof document !== 'undefined') {
    document.documentElement.classList.remove('dark', 'light')
    document.documentElement.classList.add(theme)
  }
  return null
}

export default function App() {
  return (
    <Router>
      <ThemeInitializer />
      <Routes>
        <Route path="/share/:shareId" element={<ShareViewPage />} />
        <Route
          path="*"
          element={
            <AppLayout>
              <Routes>
                <Route path="/" element={<WorkspacePage />} />
                <Route path="/notebook/:notebookId" element={<WorkspacePage />} />
                <Route path="/notebook/:notebookId/page/:pageId" element={<EditorPage />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </AppLayout>
          }
        />
      </Routes>
      <ContextMenuWrapper />
      <ToastContainer />
    </Router>
  )
}

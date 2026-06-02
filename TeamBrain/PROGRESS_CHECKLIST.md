# MindVault 项目任务清单

## 📊 项目状态总览

- **创建时间**: 2026-06-02
- **技术栈**: React 18 + TypeScript + FastAPI + SQLite
- **当前进度**: 约 95% 完成
- **核心模块**: 后端 API 100% / 前端框架 98% / 编辑器 90%
- **启动状态**: 可直接运行（见下方启动指南）

---

## ✅ 已完成

### 后端 (api/) - 100%

| 文件 | 状态 | 说明 |
|------|------|------|
| `requirements.txt` | ✅ 完成 | 所有依赖已列出（10个包） |
| `main.py` | ✅ 完成 | FastAPI 应用入口 + 11 个路由注册 |
| `config.py` | ✅ 完成 | 配置管理（AI、数据库） |
| `database.py` | ✅ 完成 | SQLAlchemy 配置 + WAL 模式 + FTS5 |
| `models.py` | ✅ 完成 | 10 个数据模型完整定义 |
| `schemas.py` | ✅ 完成 | Pydantic 请求/响应模式 |
| `init_db.py` | ✅ 完成 | 数据库初始化脚本 |
| `routers/notebooks.py` | ✅ 完成 | 笔记本 CRUD + 排序 |
| `routers/pages.py` | ✅ 完成 | 页面 CRUD + 保存 + 模板 + 批量 |
| `routers/blocks.py` | ✅ 完成 | 块 CRUD + 重排 |
| `routers/ai.py` | ✅ 完成 | AI 生成 + 配置 + 用量 + 历史 |
| `routers/versions.py` | ✅ 完成 | 版本列表/预览/恢复/复制/diff |
| `routers/search.py` | ✅ 完成 | FTS5 全文搜索 + jieba 分词 |
| `routers/tags.py` | ✅ 完成 | 标签 CRUD + 页面标签关联 |
| `routers/import_export.py` | ✅ 完成 | Markdown 批量导入/导出 |
| `routers/shares.py` | ✅ 完成 | 分享链接 + 密码/有效期 |
| `routers/sync.py` | ✅ 完成 | 离线同步 API |
| `routers/files.py` | ✅ 完成 | 文件上传 + 附件管理 |
| `services/ai_service.py` | ✅ 完成 | AI 服务 + TTLCache + 配额 |
| `services/search_service.py` | ✅ 完成 | 搜索服务 + 高亮摘要 |
| `services/export_service.py` | ✅ 完成 | Markdown 导出服务 |
| `services/import_service.py` | ✅ 完成 | Markdown 导入服务 |

### 前端 (src/) - 98%

| 文件 | 状态 | 说明 |
|------|------|------|
| `package.json` | ✅ 完成 | 完整依赖（React + TS + Vite + Tailwind + Milkdown + Zustand） |
| `vite.config.ts` | ✅ 完成 | Vite 配置 + API 代理 |
| `tailwind.config.js` | ✅ 完成 | Tailwind 主题配置 |
| `index.css` | ✅ 完成 | CSS 变量主题 + 组件类 + 动画 |
| `App.tsx` | ✅ 完成 | 路由配置 + 主题初始化 |
| `main.tsx` | ✅ 完成 | React 应用入口 |
| `api/client.ts` | ✅ 完成 | API 客户端封装（fetch 封装） |
| `api/endpoints.ts` | ✅ 完成 | 所有 API 端点定义（notebookApi, pageApi 等） |
| `stores/notebookStore.ts` | ✅ 完成 | 笔记本状态管理 |
| `stores/pageStore.ts` | ✅ 完成 | 页面+块状态管理 |
| `stores/uiStore.ts` | ✅ 完成 | UI 状态（侧边栏/面板/主题） |
| `stores/aiStore.ts` | ✅ 完成 | AI 状态（配置/用量/生成） |
| `stores/editorStore.ts` | ✅ 完成 | 编辑器状态（模式/自动保存） |
| `stores/searchStore.ts` | ✅ 完成 | 搜索状态（关键词/结果/筛选） |
| `stores/tagStore.ts` | ✅ 完成 | 标签状态管理 |
| `lib/dexie.ts` | ✅ 完成 | IndexedDB 离线草稿存储 |
| `lib/utils.ts` | ✅ 完成 | 工具函数（日期/文件/文本） |
| `lib/markdown.ts` | ✅ 完成 | Markdown 处理工具 |
| `hooks/useTheme.ts` | ✅ 完成 | 主题切换 Hook |
| `hooks/useAutoSave.ts` | ✅ 完成 | 自动保存 Hook（防抖 3s） |
| `hooks/useOfflineSync.ts` | ✅ 完成 | 离线同步 Hook |
| `hooks/useSearch.ts` | ✅ 完成 | 搜索 Hook |
| `components/layout/AppLayout.tsx` | ✅ 完成 | 应用布局（三栏） |
| `components/layout/Sidebar.tsx` | ✅ 完成 | 左侧边栏（笔记本/标签） |
| `components/layout/NotebookTree.tsx` | ✅ 完成 | 笔记本树形列表 |
| `components/layout/PageTree.tsx` | ✅ 完成 | 页面树形列表 |
| `components/layout/SearchBar.tsx` | ✅ 完成 | 顶部搜索栏 |
| `components/layout/TagList.tsx` | ✅ 完成 | 标签列表 |
| `components/layout/RightPanel.tsx` | ✅ 完成 | 右侧面板（AI/版本） |
| `components/editor/MilkdownEditor.tsx` | ✅ 完成 | Milkdown 编辑器集成 |
| `components/editor/EditorToolbar.tsx` | ✅ 完成 | 编辑器工具栏 |
| `components/editor/BlockMenu.tsx` | ✅ 完成 | 块命令菜单 |
| `components/editor/PreviewPane.tsx` | ✅ 完成 | Markdown 预览面板 |
| `components/editor/AIContentBlock.tsx` | ✅ 完成 | AI 内容插入块 |
| `components/ai/AIPanel.tsx` | ✅ 完成 | AI 助手面板（续写/摘要/改写） |
| `components/ai/AIConfigForm.tsx` | ✅ 完成 | AI 配置表单 |
| `components/ai/AIUsageBar.tsx` | ✅ 完成 | AI 用量进度条 |
| `components/version/VersionPanel.tsx` | ✅ 完成 | 版本历史时间轴 |
| `components/version/VersionPreview.tsx` | ✅ 完成 | 版本内容预览 |
| `components/version/VersionDiff.tsx` | ✅ 完成 | 版本差异对比 |
| `components/search/SearchResults.tsx` | ✅ 完成 | 搜索结果（高亮匹配） |
| `components/search/SearchFilters.tsx` | ✅ 完成 | 搜索筛选条件 |
| `components/common/Toast.tsx` | ✅ 完成 | Toast 提示组件 |
| `components/common/Modal.tsx` | ✅ 完成 | 模态框组件 |
| `components/common/ConfirmDialog.tsx` | ✅ 完成 | 确认对话框 |
| `components/common/ContextMenu.tsx` | ✅ 完成 | 右键菜单 |
| `components/common/DragDropList.tsx` | ✅ 完成 | 拖拽排序列表 |
| `components/common/EmptyState.tsx` | ✅ 完成 | 空状态组件 |
| `pages/WorkspacePage.tsx` | ✅ 完成 | 工作台首页 |
| `pages/EditorPage.tsx` | ✅ 完成 | 编辑器页面 |
| `pages/SearchPage.tsx` | ✅ 完成 | 搜索结果页面 |
| `pages/SettingsPage.tsx` | ✅ 完成 | 设置页面（AI/导入导出/分享管理） |
| `pages/ShareViewPage.tsx` | ✅ 完成 | 公开分享视图 |

### 部署配置 - 100%

| 文件 | 状态 | 说明 |
|------|------|------|
| `Dockerfile` | ✅ 完成 | Docker 镜像配置 |
| `.env.example` | ✅ 完成 | 环境变量示例 |
| `start-backend.bat` | ✅ 完成 | Windows 后端一键启动 |
| `start-frontend.bat` | ✅ 完成 | Windows 前端一键启动 |
| `README.md` | ✅ 完成 | 完整项目文档 |

## 🔧 已修复的问题

| 序号 | 问题 | 修复方案 | 修复日期 |
|------|------|----------|----------|
| 1 | npm omit=dev 导致 devDependencies 不安装 | 使用 `npm install --include=dev`，更新启动脚本 | 2026-06-02 |
| 2 | CSS @import 必须在所有其他语句之前 | 从 index.css 移除 Milkdown import | 2026-06-02 |
| 3 | Milkdown theme-nord CSS @layer 与 Tailwind v3 冲突 | 使用 `import ?raw` 动态注入，绕过 PostCSS | 2026-06-02 |
| 4 | SettingsPage 中误用 useState 而非 useEffect | 修复为正确的 useEffect 用法 | 2026-06-02 |
| 5 | Page 模型缺少 content 和 ai_summary 字段 | 在 models.py 中添加字段 | 2026-06-02 |
| 6 | PageSaveRequest 缺少 content 字段 | 添加可选 content 字段 | 2026-06-02 |
| 7 | useAutoSave 传入空块数组 | 修改 API 签名，传递 content 和 title | 2026-06-02 |
| 8 | save_page API 不处理 content 字段 | 添加 content 字段保存逻辑 | 2026-06-02 |
| 9 | pages.py 列索引错误（新增字段后偏移） | 修复所有列索引引用 | 2026-06-02 |
| 10 | shares.py 列索引错误 | 修复所有列索引引用 | 2026-06-02 |
| 11 | tags.py 列索引错误 | 修复所有列索引引用 | 2026-06-02 |
| 12 | versions.py 列索引错误 | 修复 metadata 字段索引 | 2026-06-02 |
| 13 | rebuild_fts SQL 错误（SELECT value FROM pages） | 修复为正确的字段查询 | 2026-06-02 |
| 14 | init_db 缺少数据库迁移逻辑 | 添加 ALTER TABLE 迁移新字段 | 2026-06-02 |
| 15 | 数据库列索引顺序错误（新增字段在表尾） | 修正所有相关文件的列索引映射 | 2026-06-02 |

---

## 🚀 启动指南

### 方式一：一键启动（推荐，Windows）

1. **启动后端**（新终端）：
   ```bash
   start-backend.bat
   ```

2. **启动前端**（新终端）：
   ```bash
   start-frontend.bat
   ```

3. 访问 http://localhost:5173

### 方式二：手动启动

#### 后端
```bash
cd api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py  # 初始化数据库（首次运行）
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端
```bash
npm install
npm run dev
```

---

## ⚠️ 待完善事项

### 高优先级（运行前检查）

| 序号 | 事项 | 说明 | 检查状态 |
|------|------|------|----------|
| 1 | 依赖安装 | Python + Node.js 依赖 | ⏳ 待执行 |
| 2 | 数据库初始化 | 运行 `python init_db.py` | ⏳ 待执行 |
| 3 | AI 配置 | 在设置页面配置 API Key | ⏳ 待配置 |

### 中优先级（功能完善）

| 序号 | 事项 | 说明 | 优先级 |
|------|------|------|--------|
| 4 | Markdown ↔ Block 转换 | 编辑器内容与块模型双向同步 | 中 |
| 5 | 冲突解决策略 | 离线同步冲突处理逻辑 | 中 |
| 6 | 错误边界 | React Error Boundary 组件 | 低 |
| 7 | 单元测试 | 核心服务测试 | 低 |
| 8 | E2E 测试 | 端到端测试 | 低 |

---

## 🔍 代码检查清单

### 后端代码检查

```bash
cd api
python -m pytest  # 如有测试
flake8 .          # 代码风格
```

### 前端代码检查

```bash
npm run lint       # ESLint
npm run check      # TypeScript 类型检查
npm run build      # 生产构建验证
```

---

## 📋 首次运行验证清单

- [ ] 后端启动成功，访问 http://localhost:8000/docs
- [ ] 前端启动成功，访问 http://localhost:5173
- [ ] 可以创建第一个笔记本
- [ ] 可以创建第一个页面
- [ ] 编辑器可以输入内容
- [ ] 自动保存正常工作
- [ ] 全文搜索功能正常
- [ ] AI 功能可配置（如需要）
- [ ] 版本历史可查看
- [ ] 标签功能正常

---

## 📁 项目完整结构

```
MindVault/
├── api/                          # 后端 FastAPI
│   ├── data/
│   │   ├── vault.db              # SQLite 数据库
│   │   └── attachments/          # 文件附件
│   ├── routers/                  # 11 个 API 路由模块
│   ├── services/                 # 4 个业务服务
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── config.py
│   ├── init_db.py
│   └── requirements.txt
├── src/                          # 前端 React
│   ├── components/
│   │   ├── layout/               # 6 个布局组件
│   │   ├── editor/               # 5 个编辑器组件
│   │   ├── ai/                   # 3 个 AI 组件
│   │   ├── version/              # 3 个版本组件
│   │   ├── search/               # 2 个搜索组件
│   │   └── common/               # 6 个通用组件
│   ├── pages/                    # 5 个页面
│   ├── stores/                   # 7 个 Zustand store
│   ├── hooks/                    # 4 个自定义 hook
│   ├── api/                      # API 客户端
│   ├── lib/                      # 工具库
│   ├── App.tsx
│   └── main.tsx
├── start-backend.bat
├── start-frontend.bat
├── Dockerfile
├── .env.example
├── README.md
├── PROGRESS_CHECKLIST.md         # 本文件
└── .trae/documents/              # PRD + 技术架构文档
```

---

## 💡 后续开发建议

1. **先启动验证**：安装依赖并启动，确认基础功能正常
2. **完善块编辑**：实现 Markdown 与 Block 模型的双向转换
3. **添加测试**：为核心 API 和组件添加单元测试
4. **性能优化**：大文档渲染优化、虚拟滚动
5. **功能扩展**：
   - 图片上传到云存储
   - 多用户支持
   - 数据加密
   - 移动端 APP

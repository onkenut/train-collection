# MindVault - 个人智能知识库系统

> 本地优先的个人智能知识库，集成块级 Markdown 编辑、AI 写作助手、全文搜索和版本管理。

## ✨ 功能特性

- 📓 **笔记本与页面管理**：无限层级嵌套，拖拽排序，树形展示
- 📝 **块级编辑器**：基于 Milkdown 的所见即所得 Markdown 编辑器
- 🤖 **AI 写作助手**：续写、摘要、改写、翻译、头脑风暴，支持缓存和配额管理
- 🔍 **全文搜索**：基于 SQLite FTS5，毫秒级响应，支持中文分词
- 📜 **版本历史**：自动快照，时间轴展示，支持恢复和差异对比
- 🏷️ **标签系统**：灵活的标签管理和筛选
- 📤 **导入导出**：Markdown 批量导入，单页面/笔记本导出
- 🔗 **分享功能**：生成公开分享链接，支持密码和有效期
- 💾 **离线编辑**：IndexedDB 离线存储，网络恢复自动同步
- 🎨 **响应式界面**：暗黑/浅色主题，桌面/移动端适配

## 🛠️ 技术栈

### 前端
- **React 18** + **TypeScript**
- **Vite** - 构建工具
- **Tailwind CSS 3** - 样式框架
- **Zustand** - 状态管理
- **Milkdown** - Markdown 编辑器
- **Dexie.js** - IndexedDB 封装
- **Lucide React** - 图标库

### 后端
- **FastAPI** - Web 框架
- **SQLAlchemy** - ORM
- **SQLite (WAL 模式)** - 数据库
- **SQLite FTS5** - 全文搜索
- **cachetools** - 内存缓存（TTL/LRU）
- **jieba** - 中文分词
- **httpx** - HTTP 客户端

## 🚀 快速开始

### 方式一：使用启动脚本（Windows）

1. **启动后端**：
   ```bash
   start-backend.bat
   ```

2. **启动前端**（新终端）：
   ```bash
   start-frontend.bat
   ```

### 方式二：手动启动

#### 后端
```bash
cd api
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（首次运行）
cd ..
python -m api.init_db

# 启动服务器
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
```

#### 前端
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 访问地址
- 前端界面：http://localhost:5173
- 后端 API：http://localhost:8080
- API 文档：http://localhost:8080/docs

## 🐳 Docker 部署

```bash
# 构建镜像
docker build -t mindvault .

# 运行容器
docker run -d \
  --name mindvault \
  -p 8000:8000 \
  -v $(pwd)/api/data:/app/data \
  -e AI_API_KEY=your_key \
  mindvault
```

## 📁 项目结构

```
MindVault/
├── api/                          # 后端 FastAPI
│   ├── data/                     # 数据库和附件
│   │   ├── vault.db              # SQLite 数据库
│   │   └── attachments/          # 文件附件
│   ├── routers/                  # API 路由
│   │   ├── notebooks.py          # 笔记本管理
│   │   ├── pages.py              # 页面管理
│   │   ├── blocks.py             # 块管理
│   │   ├── ai.py                 # AI 助手
│   │   ├── versions.py           # 版本历史
│   │   ├── search.py             # 全文搜索
│   │   ├── tags.py               # 标签管理
│   │   ├── import_export.py      # 导入导出
│   │   ├── shares.py             # 分享链接
│   │   ├── sync.py               # 离线同步
│   │   └── files.py              # 文件上传
│   ├── services/                 # 业务逻辑
│   │   ├── ai_service.py         # AI 服务（含缓存/配额）
│   │   ├── search_service.py     # 搜索服务（FTS5）
│   │   ├── import_service.py     # 导入服务
│   │   └── export_service.py     # 导出服务
│   ├── models.py                 # SQLAlchemy 模型
│   ├── schemas.py                # Pydantic 模式
│   ├── database.py               # 数据库配置
│   ├── config.py                 # 应用配置
│   ├── init_db.py                # 数据库初始化
│   ├── main.py                   # FastAPI 入口
│   └── requirements.txt          # Python 依赖
├── src/                          # 前端 React
│   ├── components/               # 组件
│   │   ├── layout/               # 布局组件
│   │   ├── editor/               # 编辑器组件
│   │   ├── ai/                   # AI 组件
│   │   ├── version/              # 版本组件
│   │   ├── search/               # 搜索组件
│   │   └── common/               # 通用组件
│   ├── pages/                    # 页面
│   ├── stores/                   # Zustand 状态
│   ├── hooks/                    # 自定义 hooks
│   ├── api/                      # API 客户端
│   ├── lib/                      # 工具库
│   └── main.tsx                  # 应用入口
├── Dockerfile
├── docker-compose.yml
├── start-backend.bat
├── start-frontend.bat
└── PROGRESS_CHECKLIST.md         # 项目进度清单
```

## 🔧 配置说明

### 环境变量
复制 `.env.example` 为 `.env` 并配置：

```env
# AI 配置
AI_API_KEY=your_api_key_here
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-3.5-turbo
AI_MONTHLY_BUDGET=1000000

# 数据库配置
DATA_DIR=./data
```

也可以在应用的「设置」页面配置 AI 参数。

### AI 配置
支持所有 OpenAI 兼容 API，包括：
- OpenAI (GPT-3.5/GPT-4)
- Azure OpenAI
- 本地模型（如 Ollama，配置 base_url 为 `http://localhost:11434/v1`）

## 📊 数据库设计

核心数据表：
- `notebooks` - 笔记本
- `pages` - 页面
- `blocks` - 内容块
- `page_versions` - 版本快照
- `tags` / `page_tags` - 标签系统
- `share_links` - 分享链接
- `ai_usage` / `ai_request_logs` - AI 用量统计
- `pages_fts` - FTS5 全文索引

## 🧪 开发

### 代码检查
```bash
npm run lint
npm run check  # TypeScript 类型检查
```

### 构建
```bash
# 前端构建
npm run build

# 生产启动
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📝 开发进度

详细开发进度请查看 [PROGRESS_CHECKLIST.md](PROGRESS_CHECKLIST.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

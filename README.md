# 企业资产与权限管理平台（AI 智能审计）

面向中型企业的 IT 资产全生命周期管理系统，集成三级 RBAC 权限控制与 AI 智能审计助手，帮助管理员高效掌控资产分布、权限合规与风险预警。

## 功能亮点

- 三级角色权限体系（admin / manager / viewer），接口级权限拦截
- JWT + bcrypt 无状态认证，密码加盐哈希存储
- AI 审计助手：自然语言提问，大模型自动分析资产状况并生成图表
- 管理员工作台：核心指标卡片 + 部门价值对比图 + 类别占比饼图
- 资产 CRUD + 多维搜索筛选（按名称/序列号/类别/状态）
- 操作审计日志，所有变更记录可追溯
- 种子数据一键生成 20 条真实感资产，覆盖 7 大类别、9 个部门

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python / FastAPI / SQLAlchemy (async) / SQLite |
| 认证 | JWT (PyJWT) / bcrypt |
| 前端 | React / Vite / TailwindCSS / Recharts |
| AI | 大模型 API（OpenAI 兼容协议） |

## 快速启动

### 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
pip install openai
```

配置 `.env`：

```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite+aiosqlite:///./assets.db
CORS_ORIGINS=http://localhost:5174

USE_MOCK_MODE=false
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://token.sensenova.cn/v1
MODEL_NAME=deepseek-v4-flash
```

启动：

```bash
set PYTHONPATH=%cd%          # Windows CMD
uvicorn main:app --reload    # 访问 http://localhost:8000
```

首次启动自动建表并写入种子数据。

### 前端

```bash
cd frontend
npm install
npm run dev                  # 访问 http://localhost:5174
```

### 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员（全部权限） |
| manager_zhang | manager123 | 部门经理（资产管理） |
| viewer_li | viewer123 | 查看者（只读） |

## 项目结构

```
enterprise/dashboard/
├── backend/
│   ├── main.py              # FastAPI 入口 + 启动种子数据
│   ├── database.py          # 异步数据库连接
│   ├── models.py            # User / Role / Asset / AuditLog 模型
│   ├── seed_data.py         # 种子数据（3用户 + 3角色 + 20资产）
│   ├── routers/
│   │   ├── auth.py          # 登录注册 / JWT 签发
│   │   ├── assets.py        # 资产 CRUD
│   │   └── audit.py         # AI 审计对话接口
│   └── services/
│       ├── auth_helper.py   # JWT 生成与验证
│       └── audit_assistant.py  # AI 审计（Mock/LLM 双模式）
├── frontend/
│   └── src/
│       ├── App.jsx          # 路由 + 登录态管理
│       ├── api.js           # axios 封装 + token 拦截器
│       └── pages/
│           ├── Login.jsx    # 登录/注册页
│           └── Dashboard.jsx # 主工作台（总览/资产/AI审计）
└── README.md
```

## 权限设计

| 角色 | 资产查看 | 资产编辑 | 用户管理 | AI 审计 |
|------|:--------:|:--------:|:--------:|:-------:|
| admin | ✓ | ✓ | ✓ | ✓ |
| manager | ✓ | ✓ | ✗ | ✓ |
| viewer | ✓ | ✗ | ✗ | ✓ |

## AI 审计助手示例

| 提问 | 回答 |
|------|------|
| 各部门资产分布 | 文字分析 + 柱状图 |
| 有哪些需要关注的异常 | 维护超期设备、许可证到期预警 |
| 资产总览 | 总数/总价值/类别/状态汇总 |

## 作者

陈科 | 独立开发 | 2026.06 - 2026.07

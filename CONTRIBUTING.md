# 贡献指南

感谢你对本项目的关注！以下是参与贡献的完整流程。

## 开发环境搭建

### 后端（Python 3.12+）

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

在 `backend/` 目录下创建 `.env` 文件，配置所需环境变量（参考 `.env.example`）。

### 前端（Node.js 20+）

```bash
cd frontend
npm install
```

## 本地运行

### 启动后端

```bash
cd backend
uvicorn main:app --reload --port 8000
```

后端默认监听 `http://localhost:8000`，API 文档地址：`http://localhost:8000/docs`

### 启动前端

```bash
cd frontend
npm run dev
```

前端开发服务器默认监听 `http://localhost:5173`，已配置对后端的代理。

## 代码规范

- 后端使用 **ruff** 进行代码检查和格式化
- 提交前请运行：
  ```bash
  ruff check backend/
  ruff format backend/
  ```
- 推荐安装 pre-commit 钩子以自动执行检查：
  ```bash
  pip install pre-commit
  pre-commit install
  ```

## 提交 PR 流程

1. Fork 本仓库并创建功能分支（命名建议：`feature/xxx` 或 `fix/xxx`）
2. 在功能分支上完成开发并提交
3. 确保 CI 检查全部通过（ruff lint + 前端构建）
4. 向 `main` 分支发起 Pull Request
5. 在 PR 描述中说明变更内容及关联的 Issue（如有）

## 测试角色说明

系统内置三种用户角色，测试时请覆盖各角色的权限边界：

| 角色 | 权限范围 |
|------|---------|
| **admin（管理员）** | 完整权限，包括用户管理、角色分配、系统配置 |
| **manager（管理者）** | 资产审批、审计报告查看、部门级数据管理 |
| **viewer（普通用户）** | 只读查看资产列表和基本信息 |

请在提交前分别以三种角色登录验证相关功能是否符合预期。

## 提交信息规范

建议使用约定式提交（Conventional Commits）格式：

- `feat: 新增 xxx 功能`
- `fix: 修复 xxx 问题`
- `docs: 更新文档`
- `refactor: 重构 xxx 模块`
- `test: 添加测试用例`

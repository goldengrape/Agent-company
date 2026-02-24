# Company 公司管理 (Company Runtime)

本文档对应当前实现：
- `nanobot/company/manager.py`
- `nanobot/company/loader.py`
- `nanobot/agent/subagent.py`
- `nanobot/agent/tools/document_flow.py`

## 核心职责

### CompanyManager
- 扫描 `workspace/tasks/TASK_*.md`
- 使用 `default_post` 分发任务
- 通过 `SubagentManager` 启动 worker
- 汇总结果并输出

### CompanyConfigLoader
- 解析公司配置目录（多公司/私有目录）
- 解析 `POSTS.md`、`DOCS_SCHEMA.md`、`WORKFLOWS.md`
- 读取 `SKILL.md` frontmatter（`default_post`、`default_task_template`、`skills_dir`）

### SubagentManager
- 为每个任务创建隔离 worker（独立 memory）
- 仅按岗位声明注册工具
- 空 `tools` 的岗位采用 fail-closed（不授予工具）

## 公司目录解析优先级

`CompanyConfigLoader._resolve_base_path()`：
1. `--path` 显式路径
2. `workspace/companies/<name>`
3. `workspace/companies/default`
4. 回退 `workspace/company`

## SKILL.md 支持字段

- `default_post`
- `default_task_template`
- `skills_dir`（顶层或 `components.skills_dir`）
- `components.posts`
- `components.docs_schema`
- `components.workflows`

## WORKFLOWS 现状

- `WORKFLOWS.md` 内容已加载到 `loader.workflows_content`。
- 当前运行时仍以 `default_post + TASK_*.md` 扫描分发为主，尚未实现完整工作流引擎编排。

## 文档流工具

`DocumentFlowTool` 现在会继承当前公司上下文（`company_name/company_path`），避免误读默认公司 schema。

## 审计与清理

运行结束后：
- 保留 `workspace/agent_resource/workers.json` 记录用于审计。
- 清理 worker 的隔离 memory 目录，避免运行态垃圾累积。

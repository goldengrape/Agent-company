# Nanobot Agent Company：当前实现导读

## 1. 系统定位

Nanobot Company 通过“岗位 + 文档 + 任务文件”组织多 Agent 协作：
- 岗位定义：`POSTS.md`
- 文档规范：`DOCS_SCHEMA.md`
- 工作流说明：`WORKFLOWS.md`（当前为内容加载，非完整编排执行）

## 2. 当前运行主链路

1. `nanobot company run` 启动管理器。
2. 扫描 `workspace/tasks/TASK_*.md`（或处理 `--task` 直接输入）。
3. 按 `default_post` 分发任务给 Subagent。
4. Subagent 在隔离上下文中执行并输出结果。
5. Manager 汇总结果并输出到终端/指定目录。

## 3. 多公司能力

支持两种选择方式：
- `--name <company_name>`：`workspace/companies/<name>`
- `--path <company_dir>`：显式指定配置目录（优先级最高）

## 4. 权限与隔离

- Worker 使用独立 memory 目录（按 task_id 隔离）。
- 文件路径权限采用规范路径边界判断，避免前缀绕过。
- 岗位工具策略为最小权限：
  - 明确声明 tools：仅授予声明工具
  - tools 为空：不授予工具（fail-closed）
  - 无岗位定义：兼容模式下授予默认工具集

## 5. 文档与代码的一致性结论

当前代码已经实现：
- 多公司路径解析
- 任务文件 `TASK_*.md` 扫描
- 公司上下文传递到 ContextBuilder/DocumentFlowTool
- 公司级 `skills_dir` 解析与运行时技能加载

当前仍未完成：
- 基于 `WORKFLOWS.md` 的完整运行时编排引擎

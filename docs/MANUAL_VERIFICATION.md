# Nanobot Company 人工验证方案 (Manual Verification)

本方案仅基于当前仓库实现，验证“任务分发-执行-审计”主链路。

## 0. 前置条件

- 在仓库根目录执行（当前项目目录）。
- 已安装 Python 及项目依赖。
- 可选：配置模型 API key（仅在需要真实 LLM 执行时）。

## 1. 初始化公司

```bash
nanobot company init --name demo
```

预期：
- 生成 `workspace/companies/demo/` 下四个基础文件。

## 2. 配置默认岗位

编辑 `workspace/companies/demo/SKILL.md`，设置：

```yaml
default_post: Post_Analyst
```

## 3. 放置任务文件并运行

创建任务文件：`workspace/tasks/TASK_DEMO_001.md`

然后运行：

```bash
nanobot company run --name demo
```

预期：
- 扫描到 `TASK_*.md`
- 任务被分配给 `default_post`
- 控制台输出汇总结果

## 4. 直接任务输入验证

```bash
nanobot company run --name demo --task "请写一份测试摘要"
```

预期：
- 不依赖任务文件扫描，直接处理输入任务。

## 5. 审计与清理验证

检查：
- `workspace/agent_resource/workers.json` 中保留 worker 记录（含状态与结果）。
- `workspace/memory/workers/<task_id>/` 在 run 结束后被清理。

## 6. 文档流工具公司上下文验证

在不同公司目录下分别执行 `DocumentFlowTool` 创建文档，确认 schema 解析来自对应公司目录，而不是默认公司。

## 7. 已知边界

- `WORKFLOWS.md` 当前已加载内容，但未作为完整运行时编排引擎执行。
- 运行时核心分发仍由 `default_post + TASK_*.md` 驱动。

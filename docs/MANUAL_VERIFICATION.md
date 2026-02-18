# Nanobot Company: 人工验证方案 (Manual Verification Plan)

本方案旨在验证 Nanobot Company 核心功能的端到端流程，包括公文创建、任务分发（模拟）和结果提交。

## 验证场景: 天气预报周报 (Weather Forecast Weekly)

我们将模拟一个简单的 PDCA 循环：
1.  **Plan**: 创建“天气查询”任务单。
2.  **Do**: 模拟气象分析师执行任务并生成报告。
3.  **Check/Act**: 提交报告并验证系统日志。

### 前置条件
- 确保已安装 `uv`。
- 确保位于项目根目录 `c:\Users\golde\code\nanobot-company`。

### 0. 配置 (可选但推荐)

本次验证主要侧重于“公文流转”机制（文件生成与移动），**不需要 LLM API Key**。
但如果您想运行完整的 Worker 智能体（涉及 `SubagentManager` 或 `AgentLoop`），请配置环境变量或 `~/.nanobot/config.json`：

```bash
# Windows PowerShell (仅在运行完整智能体时需要)
$env:OPENAI_API_KEY = "sk-..."
```

---

## 步骤 1: 创建任务 (Plan)

使用 `DocumentFlowTool` 创建一个符合 `Doc_Task_Weather` 规范的任务单。

**操作**: 运行以下 Python 脚本 (或通过 CLI 工具调用):

```bash
# Windows PowerShell
uv run python -c "import asyncio; from pathlib import Path; from nanobot.agent.tools.document_flow import DocumentFlowTool; tool = DocumentFlowTool(Path('.')); asyncio.run(tool.execute('create', doc_type='Doc_Task_Weather', title='Q3_Weather_Check', metadata={'Cities': 'Beijing, Shanghai'}))"
```

**预期结果**:
- 终端输出: `Document created successfully...`
- 文件检查: 检查 `workspace/tasks/` 目录下是否生成了 `TASK_WEATHER_<Date>.md`。
- 内容检查: 打开该文件，确认 `{ISO_Date}` 和 `{UUID}` 已被替换为实际值。

---

## 步骤 2: 模拟执行与报告 (Do)

假设 Worker 已经完成了查询，现在生成一份报告。我们将手动创建这份报告（或使用工具生成）。

**操作**: 运行以下命令生成报告:

```bash
uv run python -c "import asyncio; from pathlib import Path; from nanobot.agent.tools.document_flow import DocumentFlowTool; tool = DocumentFlowTool(Path('.')); asyncio.run(tool.execute('create', doc_type='Doc_Report_Weather', title='Weekly_Report', metadata={'Worker_ID': 'Post_Weather_Analyst'}))"
```

**预期结果**:
- 终端输出: `Document created successfully...`
- 文件检查: 检查 `workspace/reports/` 目录下是否生成了 `REPORT_WEATHER_<Date>.md`。

---

## 步骤 3: 提交公文 (Check/Act)

模拟 Worker 提交任务，触发公文流转（日志记录）。

**操作**:
1. 获取步骤 2 中生成的报告文件名 (例如 `REPORT_WEATHER_2023-10-27.md`)。
2. 运行提交命令 (替换 `<Filename>` 为实际文件名):

```bash
# 替换文件名
$filename = "REPORT_WEATHER_2026-02-17.md" # 请根据实际情况修改日期
uv run python -c "import asyncio; from pathlib import Path; from nanobot.agent.tools.document_flow import DocumentFlowTool; tool = DocumentFlowTool(Path('.')); asyncio.run(tool.execute('submit', file_path=f'workspace/reports/{$filename}'))"
```

**预期结果**:
- 终端输出: `Document ... submitted. System has logged this action.`
- 日志检查: 查看 `memory/EVENTS.jsonl` (注意: 位于根目录下的 memory 文件夹)，确认包含 `task_submitted` 事件。

---

## 补充检查: 核心组件状态

除了上述流程，建议检查以下组件是否正常加载：

1.  **Company Loader**: 确认 `POSTS.md` 被正确解析。
    ```bash
    uv run python -c "from pathlib import Path; from nanobot.company.loader import CompanyConfigLoader; loader = CompanyConfigLoader(Path('.')); loader.load_all(); print(f'Loaded Posts: {list(loader.posts.keys())}')"
    ```
    *预期*: 输出包含 `Post_Dev_Junior`, `Post_Weather_Analyst` 等。

2.  **Heartbeat**: 确认心跳服务能扫描到任务。
    *   在 `workspace/tasks/` 中保留一个 `TASK_...md` 文件，状态设为 `**Status**: Pending`。
    *   运行心跳检查 (模拟):
    ```bash
    uv run python -c "import asyncio; from pathlib import Path; from nanobot.heartbeat.service import HeartbeatService; svc = HeartbeatService(Path('.')); asyncio.run(svc._check_tasks())"
    ```
    *预期*: 查看控制台日志 (可能需要配置 loguru 输出) 或直接观察无报错。

---

## 遗留问题与建议 (Findings)

在代码审查中发现：
1.  `nanobot/company/loader.py` 中 `_load_workflows` 目前被注释掉 (`Placeholder`)。这意味着 `WORKFLOWS.md` 虽然存在但未被系统加载。建议在下一阶段实现此功能以支持更复杂的流程控制。

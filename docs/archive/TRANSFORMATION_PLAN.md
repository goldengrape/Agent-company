# 改造计划: Nanobot 到 Nanobot Company

本计划概述了修改 nanobot 核心以支持“Agent 公司”架构的步骤。

## 阶段 1: 核心数据结构与解析 (Core Data Structures & Parsing)
**目标**: 使 nanobot 能够理解公司定义（人、事、物）。

- [x] **1.1 实现 `CompanyConfigLoader`**
    - 创建 `nanobot/company/loader.py`。
    - 功能: 读取 `company/POSTS.md`, `company/WORKFLOWS.md`, `company/DOCS_SCHEMA.md`。
    - 产出: 岗位、流程、Schema 的结构化内存对象 (字典)。

- [x] **1.2 扩展 `ContextBuilder`**
    - 修改 `nanobot/context.py` (或等效文件)。
    - 增加逻辑以将“公司结构”注入到系统提示词 (System Prompt) 中。
    - 实现 `get_identity_for_post(post_id)`，根据 `POSTS.md` 动态生成 `IDENTITY`。

## 阶段 2: Manager 与 Worker 的生命周期 (Manager & Worker Lifecycle)
**目标**: 赋予 Manager 生成特定“员工”的权力。

- [x] **2.1 增强 `SubagentManager`**
    - 修改 `nanobot/manager.py` (或现有的 subagent 逻辑)。
    - 增加 `spawn_worker(post_id, task_context)` 方法。
    - 确保生成的 worker：
        - 继承正确的 Skills (如 `POSTS.md` 中定义)。
        - 拥有正确的 Tools (如 `POSTS.md` 中定义)。
        - 拥有正确的 System Prompt (Identity)。

- [x] **2.2 实现 `WorkerRegistry` (可选但推荐)**
    - 按 ID 和角色跟踪活跃的 worker。
    - 允许“返聘” (上下文恢复)，如果我们需要持久化 (高级功能)。

- [ ] **2.3 实施强制隔离 (Enforce Isolation)**
    - **独立 System Prompt**：
        - 确保 **每个 Agent** (无论是 Manager 还是 Worker) 都必须生成独立、专属的 `System Prompt`。
        - 严禁使用通用 `System Prompt`。Manager 的 Prompt 仅包含管理职责，Worker 的 Prompt 仅包含岗位技能。
    - **独立 Memory Store**：
        - 确保 `SubagentManager` 为每个 worker 初始化独立的 `MemoryStore` 实例，物理路径隔离。
        - 验证 Agent 无法访问其他 Agent 的 `MemoryStore` 实例。
    - **通信阻断**：
        - 移除或禁用任何允许 Agent 间直接共享变量的 Python 接口。

## 阶段 3: 公文流引擎 (Document Flow Engine - 官僚体系)
**目标**: 通过文件操作强制执行 PDCA 循环。

- [x] **3.1 创建 `DocumentFlowTool`**
    - 新工具 `nanobot/tools/document_flow.py`。
    - 方法: `create_task`, `submit_report`, `audit_report`。
    - 验证: 确保创建的文件符合 `DOCS_SCHEMA.md` 中的 Schema。

- [x] **3.2 修改 `AgentLoop` 以支持工作流**
    - 修改 `nanobot/agent.py`。
    - 增加“观察前”钩子 (Pre-observation hook): 检查是否有新的“收件箱”项目 (公文)。
    - 增加“行动后”钩子 (Post-action hook): 如果 `Task` 状态为 "Done"，触发“移交审计”动作 (或通知 Manager)。

## 阶段 4: 办公室管理 (Office Management - 服务层)
**目标**: 自动化与督办。

- [x] **4.1 增强 `HeartbeatService`**
    - 修改 `nanobot/heartbeat.py`。
    - 逻辑: 每 N 分钟扫描一次 `workspace/tasks/pending`。
    - 逻辑: 检查“陈旧”任务 (在 `Active` 状态停留过久的任务)。

- [x] **4.2 归档与日志 (Archive & Log)**
    - 确保 `MemoryStore` 捕获关键事件 (任务开始、任务结束)。

## 执行策略 (Execution Strategy)

1.  **准备工作**:
    - [x] 创建文档 (`docs/`, `company/`) - *已完成中文版*。
    - [x] 设置开发环境 (venv)。

2.  **实施**:
    - 从 **阶段 1** (加载器) 开始。
    - 然后是 **阶段 2** (Manager/Worker)。
    - 然后是 **阶段 3** (工具)。
    - 最后是 **阶段 4** (服务)。

3.  **验证**:
    - 创建一个测试场景: "实现功能 X"。
    - 手动触发流程。
    - 验证文件是否在 `workspace/` 中正确创建。

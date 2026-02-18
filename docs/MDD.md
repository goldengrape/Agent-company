# 模块设计文档 (MDD)
基于 nanobot 的极简核心，本系统划分为四个核心模块：

## 1. 组织管理模块 (Organizational Manager)
- **核心组件**：`SubagentManager`、`Posts.md` 解析器。
- **逻辑说明**：
  - Manager 定期通过 `HeartbeatService` 检查 `HEARTBEAT.md`。
  - 根据 `Posts.md` 定义的技能要求，通过 `spawn` 工具生成特定配置的子级 Worker。
  - Manager 负责在 Worker 启动时注入特定的“公文处理上下文”。

## 1.1 公司技能加载器 (Company Skill Loader)
- **输入**: `company/SKILL.md`
- **功能**:
  - 验证 Company Skill 的完整性 (Posts, Workflows, Docs)。
  - 解析 `POSTS.md` 并注册到 SubagentManager。
  - 解析 `WORKFLOWS.md` 并初始化 Cron 任务 (如果需要)。
- **Schema (SKILL.md)**:
  ```yaml
  name: "Company Name"
  description: "..."
  components:
    posts: "./POSTS.md"
    workflows: "./WORKFLOWS.md"
    docs_schema: "./DOCS_SCHEMA.md"
  skills_dir: "./skills"
  ```

## 2. 任务执行模块 (Task Execution Worker)
- **核心组件**：`AgentLoop`、`SkillsLoader`。
- **逻辑说明**：
  - Worker 加载对应的 `SKILL.md`（如 `github` 或 `summarize`）。
  - 仅限访问 `workspace` 中特定的公文目录（由 `restrictToWorkspace` 限制安全性）。
  - 任务完成后，调用 `write_file` 生成执行反馈文档。

## 3. 公文流转模块 (Document Flow Engine)
- **核心组件**：`filesystem` 增强工具（read/write/edit）、`CronService`。
- **流程实现**：
  - **P (Plan)**：Manager 写入任务公文。
  - **D (Do)**：Worker 修改公文状态并附加产出内容。
  - **C (Check)**：审计岗 Worker（由 Manager 重用生成的实例）调用 `grep` 检索 `HISTORY.md` 进行合规性检查。
  - **A (Act)**：Manager 根据审计公文关闭任务或重置循环。

## 4. 记忆与会话模块 (Persistence & Memory)
- **核心组件**：`MemoryStore` (Per-Agent Instance)、`SessionManager`。
- **逻辑说明**：
  - 每个 Agent 实例化自己的 `MemoryStore`，路径如 `workspace/memory/{agent_id}/`。
  - 公文历史记录在公文文件本身的元数据或 `HISTORY.md` 中，但 Agent 对事件的记忆是隔离的。
  - 关键共识（如项目决策）通过“通告”公文同步，而非直接修改对方记忆。

## 5. 约束与规范 (Constraints)
- **C1：轻量化**：核心代码必须保持在 nanobot 约 4000 行的量级，避免过度封装。
- **C2：标准化**：所有公文必须采用 Markdown 格式，且必须符合 `Docs.md` 中定义的 Schema。
- **C3：安全性**：Worker 严禁执行系统级危险命令（由 `ExecTool` 的 `deny_patterns` 过滤）。
- **C4：隔离性**：Worker 进程/线程之间无共享内存。所有输入必须来自 System Prompt 或 Read File；所有输出必须是 Write File 或 Tool Call。

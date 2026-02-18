# 用户需求文档 (URD): Nanobot 公司系统 (Nanobot Company System)

## 1. 项目概述
本项目旨在开发一个高度组织化的“Agent 公司”系统。该系统建立在 **nanobot** 轻量级框架之上，通过模拟现实世界的科层制/官僚体系，利用“公文流”控制多个 Agent 协作完成复杂任务。系统通过标准化的文档定义人（岗位）、事（流程）和物（公文格式）。

## 2. 角色定义
系统内存在两类核心 Agent 角色：

### 2.1 基层员工 (Worker)
- **职责**：负责执行具体的常规任务。
- **核心能力**：
  - **技能 (Skills)**：通过 `SkillsLoader` 动态加载特定领域的专业知识（如 GitHub 操作、数据汇总等）。
  - **工具调用 (Tool Execution)**：能够调用 nanobot 内置的文件操作、Shell 执行、网页搜索等工具。
  - **记忆能力 (Memory)**：利用 `MemoryStore` 维护两层记忆系统（`MEMORY.md` 记录事实，`HISTORY.md` 记录日志）。

### 2.2 管理者 (Manager)
- **职责**：负责 Worker 的生命周期管理及任务调度。
- **核心能力**：
  - **Agent 管理**：利用 nanobot 的 `SubagentManager` 能力生成、删除或重用 Worker 实例。
  - **任务分配**：为 Worker 提供必要的上下文（Context）并下发具体任务指令。
  - **记忆能力**：同样具备 `MemoryStore` 能力，记录公司层面的决策和各 Worker 的绩效。

### 2.3 隔离性原则 (Isolation Principles) - **新增核心规则**
- **独立 System Prompt**：每个 Agent (Worker/Manager) 必须拥有自己独立的 System Prompt，由 `ContextBuilder` 根据岗位定义 (`POSTS.md`) 动态生成。
- **独立 Memory**：每个 Agent 的记忆 (`MemoryStore`) 必须是物理隔离的。
  - **严禁共享**：不同 Agent 之间不能共享内存实例或直接访问对方的记忆文件。
  - **生命周期**：Worker 的记忆随其生命周期创建和销毁（或归档），Manager 的记忆持久化用于公司管理。
- **通信约束**：
  - **唯一渠道**：Agent 之间严禁通过共享内存或直接函数调用进行隐式通信。
  - **公文交互**：所有信息交换必须通过符合规范的“公文”（Markdown 文件）进行。Manager 通过发布“任务书”下达指令，Worker 通过提交“报告书”反馈结果。

## 3. 公司结构标准文档
公司的运作由三个核心 Markdown 配置文件定义，Agent 需通过 `read_file` 持续读取并遵守：

### 3.1 岗位描述文档 (Posts/People)
- **内容**：定义公司内设的所有工作岗位及其职能范围。
- **关键要素**：各岗位的职责说明、必须具备的技能组（Skills）、对应的工具调用权限。

### 3.2 流程管理文档 (Affairs/Workflows)
- **内容**：定义任务的科层传递机制和流转逻辑。
- **核心循环**：工作过程必须遵循 **PDCA (Plan-Do-Check-Act)** 循环。
  - **Plan**：任务初期的计划公文生成。
  - **Do**：Worker 执行阶段。
  - **Check**：生成审计/审查文档，进行合规性检查。
  - **Act**：根据检查结果调整，或将最终产出导向指定位置。


### 3.3 公文规范文档 (Document Specifications)
- **内容**：专门描述公文的形式与流向。
- **关键要素**：
  - **格式定义**：每类公文（如任务书、汇报书、审计单）的模板格式。
  - **流向控制**：明确定义该公文的上游（由谁生成）和下游（发往哪个岗位）。

### 3.4 公司技能定义 (Company Skill Definition)
- **内容**：将整个公司的运作逻辑封装为一个标准化的 Agent Skill。
- **元数据 (SKILL.md)**：
  - **Description**: 描述公司的业务领域（如“科技新闻简报公司”）。
  - **Components**: 显式声明包含的子模块（Posts, Workflows, Docs）。
  - **Sub-skills**: 包含特定于此公司的员工技能库。


## 4. 运行机制：公文流控制
- **传递媒介**：所有的工作指令、进度报告、审查意见均以“公文”（Markdown 文件）形式存储在 `workspace` 的特定目录中。
- **触发方式**：Agent 需监控特定目录或通过 `HeartbeatService` 定期轮询 `HEARTBEAT.md` 中的“公文待处理”任务。
- **解耦通信**：Agent 之间不直接对话，而是通过 `message` 工具或在 `workspace` 中修改/创建公文来完成协作。

## 5. 技术实现基础 (基于 nanobot 模块)
为实现上述需求，需重点利用或修改以下 nanobot 模块：
- **SubagentManager**：修改其逻辑，使其支持根据“岗位描述文档”生成特定配置的 Worker。
- **ContextBuilder**：用于在分配任务时，自动从三个核心文档中提取岗位、流程和格式要求，组装成 Worker 的系统提示词。
- **filesystem 工具组**：Worker 和 Manager 必须频繁使用 `write_file` 和 `edit_file` 来推动公文的生成与修改。
- **CronService**：用于设置 PDCA 循环中的“督办”任务，如定期检查某公文是否已超时未处理。

## 6. 预期目标
通过本系统，用户只需在 `workspace` 中放入初始的“任务申请公文”，Manager 即可自动拆解任务，生成对应岗位的 Worker，按照流程规范流转文件，并在完成 PDCA 闭环后产出符合格式规范的结果文档。

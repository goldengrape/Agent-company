# 公理设计文档 (ADD)
公理设计通过将**功能需求 (FRs)** 映射到**设计参数 (DPs)** 来确保设计的独立性与紧凑性。

## 1. 顶层映射 (Level 0)
- **FR0**：实现一个基于公文流控制、具备 PDCA 循环的多 Agent 协作体系。
- **DP0**：基于 nanobot 核心能力的“岗位-流程-公文”三位一体框架，封装为 **Company Skill**。

## 2. 一级分解 (Level 1)

| 功能需求 (FR) | 设计参数 (DP) | nanobot 对应模块/文件 |
| :--- | :--- | :--- |
| FR1：组织架构管理 (管理 Worker 生命周期) | DP1：管理者模块 (Manager) | SubagentManager & Posts.md |
| FR2：专业任务执行 (执行具体常规任务) | DP2：员工模块 (Worker) | AgentLoop, SkillsLoader & Posts.md |
| FR3：流程控制与审计 (PDCA 逻辑与公文流转) | DP3：公文流引擎 (Document Flow) | filesystem 工具组, CronService & Workflows.md |
| FR4：知识持久化 (存储事实与执行日志) | DP4：独立记忆层 (Isolated Memory Instances) | MemoryStore (Per Agent), SessionManager & Docs.md |
| FR5：公司定义封装 (多实例支持) | DP5：公司技能包 (Company Skill) | Loader, SKILL.md & companies/ |

## 3. 设计矩阵 (Design Matrix)

$$
\begin{bmatrix} FR1 \\ FR2 \\ FR3 \\ FR4 \end{bmatrix} = \begin{bmatrix} X & 0 & 0 & 0 \\ I & X & 0 & 0 \\ I & I & X & 0 \\ I & I & I & X \end{bmatrix} \begin{bmatrix} DP1 \\ DP2 \\ DP3 \\ DP4 \end{bmatrix}
$$

- **分析**：该设计为**准解耦设计 (Decoupled Design)**。
  - Worker (DP2) 依赖于 Manager (DP1) 分配上下文。
  - 公文流 (DP3) 依赖于前两者的执行产出。
  - 记忆层 (DP4) 记录所有模块的活动轨迹。
  - **独立性公理**：满足。通过 `Posts.md` 明确定义岗位界限，避免了功能耦合。
  - **隔离性公理**（新增）：满足。各 Agent 内存物理隔离，强制通过公文 (DP3) 交互，消除了隐藏耦合。

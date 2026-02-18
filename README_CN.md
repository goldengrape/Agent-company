<div align="center">
  <img src="nanobot_logo.png" alt="nanobot" width="500">
  <h1>Nanobot Company: 基于公文流的 Agent 协作框架</h1>
  <p>
    <a href="README.md">English</a> | <a href="README_CN.md">简体中文</a>
  </p>
  <p>
    <a href="https://pypi.org/project/nanobot-ai/"><img src="https://img.shields.io/pypi/v/nanobot-ai" alt="PyPI"></a>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </p>
</div>

🏢 **Nanobot Company** 是一个建立在 **nanobot** 轻量级框架之上的“Agent 公司”系统。

它通过模拟现实世界的科层制体系，利用**公文流 (Document Flow)** 控制多个 Agent 协作完成复杂任务。系统通过标准化的 Markdown 文档定义人（岗位）、事（流程）和物（公文格式），实现了高度组织化的 Agent 协作。

## 🌟 核心理念

我们认为大规模 Agent 协作的关键不在于增加单个 Agent 的智力，而在于建立**清晰的组织架构和标准化的作业流程**。

- **科层制 (Bureaucracy)**：通过岗位分工明确责任边界。
- **公文流 (Document Flow)**：以标准化的文档作为 Agent 间唯一的通信载体，实现解耦和可追溯。
- **PDCA 循环**：所有工作遵循 Plan-Do-Check-Act 闭环，确保交付质量。

## 👥 角色定义

系统内包含两类核心角色：

### 1. 管理者 (Manager)
- **职责**：负责 Worker 的生命周期管理及任务调度。
- **能力**：根据 `POSTS.md` 动态生成、复用或回收 Worker；解析 `WORKFLOWS.md` 定义的流程，分发任务；进行绩效评估。

### 2. 基层员工 (Worker)
- **职责**：执行具体的常规任务。
- **能力**：
  - **技能 (Skills)**：动态加载特定领域知识（如 GitHub 操作、数据分析）。
  - **工具 (Tools)**：调用文件操作、Shell、搜索等工具。
  - **记忆 (Memory)**：基于 `MEMORY.md` (事实) 和 `HISTORY.md` (日志) 的双层记忆。

## 📄 公司架构文档

公司的运作由 `company/` 目录下的三个核心配置文件定义：

| 文档 | 说明 | 对应概念 |
| :--- | :--- | :--- |
| **[`POSTS.md`](company/POSTS.md)** | **岗位描述**：定义所有岗位及其职责、所需技能和工具权限。 | **人 (People)** |
| **[`WORKFLOWS.md`](company/WORKFLOWS.md)** | **流程管理**：定义任务的流转逻辑和 PDCA 循环要求。 | **事 (Affairs)** |
| **[`DOCS_SCHEMA.md`](company/DOCS_SCHEMA.md)** | **公文规范**：定义各类公文（任务书、报告、审计单）的模板格式。 | **物 (Documents)** |

## 🚀 快速开始

### 1. 安装 nanobot

```bash
pip install nanobot-ai
# 或者使用 uv (推荐)
uv tool install nanobot-ai
```

### 2. 初始化公司

```bash
nanobot company init
```
*(注：此命令将自动创建 `company` 目录及示例配置)*

### 3. 定义岗位与流程

编辑 `company/POSTS.md` 添加你的第一个员工（例如“技术撰稿人”），并在 `company/WORKFLOWS.md` 中定义其工作流程。

### 4. 启动公司

```bash
nanobot company run
```

Manager 将自动启动，监控 `workspace` 中的任务申请，并根据配置调度 Worker 进行工作。

---

## 🛠️ 底层框架：nanobot

**Nanobot Company** 的底层是 **nanobot** —— 一个仅 ~4,000 行代码的超轻量级 Agent 框架。

如果你只需要一个简单的个人 AI 助手，nanobot 本身依然是极佳的选择。

### 主要特性
- **超轻量**：核心代码极其精简，易于理解和修改。
- **多模型支持**：支持 OpenAI, Anthropic, Gemini, DeepSeek, Local LLM (vLLM) 等。
- **扩展性强**：支持 MCP (Model Context Protocol) 协议，轻松连接外部工具。

### 个人助手模式

```bash
# 配置 API Key
nanobot config set providers.openai.apiKey sk-...

# 启动对话
nanobot agent
```

更多关于 nanobot 底层框架的详细文档，请参考 [原英文文档](docs/README_LEGACY.md) (如果有备份) 或查看源码。

## 🤝 参与贡献

欢迎提交 PR 或 Issue！让我们一起构建更高效的 AI 协作组织。

## 📄 许可证

MIT License

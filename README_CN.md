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

公司的运作由 `companies/<name>/` 目录下的三个核心配置文件定义：

| 文档 | 说明 | 对应概念 |
| :--- | :--- | :--- |
| **[`SKILL.md`](companies/default/SKILL.md)** | **公司定义**: 入口文件。可定义 `default_post` 自动处理所有任务。 | **身份 (Identity)** |
| **[`POSTS.md`](companies/default/POSTS.md)** | **岗位描述**：定义所有岗位及其职责、所需技能和工具权限。 | **人 (People)** |
| **[`WORKFLOWS.md`](companies/default/WORKFLOWS.md)** | **流程管理**：定义任务的流转逻辑和 PDCA 循环要求。 | **事 (Affairs)** |
| **[`DOCS_SCHEMA.md`](companies/default/DOCS_SCHEMA.md)** | **公文规范**：定义各类公文（任务书、报告、审计单）的模板格式。 | **物 (Documents)** |

## 🚀 快速开始

### 1. 安装 nanobot

```bash
pip install nanobot-ai
# 或者使用 uv (推荐)
uv tool install nanobot-ai
```

### 2. 初始化公司

```bash
```bash
nanobot company init --name <company_name>
```
*(注：此命令将自动创建 `companies/<company_name>` 目录及示例配置)*

### 3. 定义能力 (Capabilities)

公司通过配置而非代码来扩展能力。

1.  **定义岗位**: 在 `companies/<name>/POSTS.md` 中添加岗位描述。
2.  **配置分发**: 在 `companies/<name>/SKILL.md` 中增加 `default_post: <Post_ID>`。所有任务将自动分派给该岗位。

### 4. 委派任务 (Delegate Tasks)

在 `workspace/tasks` 目录下创建 Markdown 文件委派任务。

**示例**: 创建 `workspace/tasks/任意文件名.md`
*(Manager 将自动将其分派给默认岗位)*

```markdown
# TASK: 每日科技新闻
**ID**: NEWS_001

## 目标
搜索并总结今日最重要的 3条 AI 新闻。
```

### 5. 启动公司 (Run Company)

```bash
nanobot company run --name <company_name>
# 或运行默认公司
nanobot company run
# 或直接传入任务字符串
nanobot company run --name <company_name> --task "你的任务描述"
# 或指定任务文件
nanobot company run --name <company_name> --task ./path/to/task.md
# 或从自定义路径加载公司配置（private_companies/ 已被 .gitignore 排除）
nanobot company run --path ./private_companies/my_company
```

Manager 将自动启动，监控 `workspace/tasks`，根据文件名将任务分发给对应的 Agent，并生成报告到 `workspace/reports`。

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

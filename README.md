<div align="center">
  <img src="nanobot_logo.png" alt="nanobot" width="500">
  <h1>Nanobot Company: Document-Flow Based Agent Collaboration Framework</h1>
  <p>
    <a href="README.md">English</a> | <a href="README_CN.md">简体中文</a>
  </p>
  <p>
    <a href="https://pypi.org/project/nanobot-ai/"><img src="https://img.shields.io/pypi/v/nanobot-ai" alt="PyPI"></a>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </p>
</div>

🏢 **Nanobot Company** is an "Agent Company" system built on the ultra-lightweight **nanobot** framework.

It simulates a real-world bureaucratic system, using **Document Flow** to control multiple Agents collaborating on complex tasks. The system uses standardized Markdown documents to define People (Posts), Affairs (Workflows), and Objects (Document Schemas), achieving highly organized Agent collaboration.

## 🌟 Core Concepts

We believe the key to large-scale Agent collaboration is not increasing the intelligence of a single Agent, but establishing **clear organizational structures and standardized operating procedures**.

- **Bureaucracy**: Clarify responsibility boundaries through post division.
- **Document Flow**: Use standardized documents as the sole communication medium between Agents, achieving decoupling and traceability.
- **PDCA Cycle**: All work follows the Plan-Do-Check-Act loop to ensure delivery quality.

## 👥 Role Definitions

The system contains two core roles:

### 1. Manager
- **Responsibilities**: Manage Worker lifecycle and task scheduling.
- **Capabilities**: Dynamically spawn, reuse, or terminate Workers based on `POSTS.md`; parse workflows defined in `WORKFLOWS.md` and distribute tasks; conduct performance evaluations.

### 2. Worker
- **Responsibilities**: Execute specific routine tasks.
- **Capabilities**:
  - **Skills**: Dynamically load domain-specific knowledge (e.g., GitHub operations, data analysis).
  - **Tools**: Call file operations, Shell, search, and other tools.
  - **Memory**: Dual-layer memory based on `MEMORY.md` (Facts) and `HISTORY.md` (Logs).

## 📄 Company Architecture Documents

The company's operations are defined by three core configuration files in the `companies/<name>/` directory:

| Document | Description | Concept |
| :--- | :--- | :--- |
| **[`SKILL.md`](companies/default/SKILL.md)** | **Company Definition**: Entry point. Can define a `default_post` to handle all tasks automatically. | **Identity** |
| **[`POSTS.md`](companies/default/POSTS.md)** | **Job Descriptions**: Define all posts, their responsibilities, required skills, and tool permissions. | **People** |
| **[`WORKFLOWS.md`](companies/default/WORKFLOWS.md)** | **Workflow Management**: Define task flow logic and PDCA cycle requirements. | **Affairs** |
| **[`DOCS_SCHEMA.md`](companies/default/DOCS_SCHEMA.md)** | **Document Schemas**: Define template formats for various documents. | **Objects** |

## 🚀 Quick Start

### 1. Install nanobot

```bash
pip install nanobot-ai
# Or use uv (Recommended)
uv tool install nanobot-ai
```

### 2. Initialize Company

```bash
nanobot company init --name <company_name>
```
*(Note: This command will automatically create the `companies/<company_name>` directory and example configurations)*

### 3. Define Capabilities

Capabilities are extended through configuration, not code.

1.  **Define Post**: Add job descriptions in `companies/<name>/POSTS.md`.
2.    -   **Configure Dispatch**: In `companies/<name>/SKILL.md`, set `default_post: <Post_ID>`. All tasks will go to this post.

### 4. Delegate Tasks

Create Markdown files in `workspace/tasks` to delegate tasks.

**Example**: Create `workspace/tasks/ANY_NAME.md`
*(Manager will automatically assign it to the default post)*

```markdown
# TASK: Daily Tech News
**ID**: NEWS_001
## Goal
Search and summarize the top 3 AI news of the day.
```

### 5. Run Company

```bash
nanobot company run --name <company_name>
# or run default
nanobot company run
```

The Manager will automatically start, monitor task applications in `workspace`, and schedule Workers based on the configuration.

---

## 🛠️ Underlying Framework: nanobot

**Nanobot Company** is powered by **nanobot** — an ultra-lightweight Agent framework with only ~4,000 lines of code.

If you only need a simple personal AI assistant, nanobot itself is still an excellent choice.

### Key Features
- **Ultra-Lightweight**: Core code is extremely concise, easy to understand and modify.
- **Multi-Model Support**: Supports OpenAI, Anthropic, Gemini, DeepSeek, Local LLM (vLLM), etc.
- **High Extensibility**: Supports MCP (Model Context Protocol) to easily connect external tools.

### Personal Assistant Mode

```bash
# Set API Key
nanobot config set providers.openai.apiKey sk-...

# Start Chat
nanobot agent
```

For more detailed documentation on the nanobot underlying framework, please refer to the [Legacy Documentation](docs/README_LEGACY.md) (if available) or view the source code.

## 🤝 Contributing

PRs and Issues are welcome! Let's build a more efficient AI collaborative organization together.

## 📄 License

MIT License

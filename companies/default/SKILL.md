---
name: "Nanobot Company System"
description: "A data-driven, agentic company simulation where Managers and Workers collaborate via document flows."
behavior:
  - "Managers dispatch tasks based on WORKFLOWS.md"
  - "Workers execute tasks using defined Skills"
  - "Auditors verify outputs against DOCS_SCHEMA.md"
components:
  posts: "./POSTS.md"
  workflows: "./WORKFLOWS.md"
  docs_schema: "./DOCS_SCHEMA.md"
  skills_dir: "./skills"
---

# Nanobot Company Skill

## Overview
This skill defines the structure and operational logic of the "Nanobot Company". It encapsulates the organizational chart (Posts), operating procedures (Workflows), and document standards (Docs Schema).

## Components

### 1. 岗位 (Posts) - `POSTS.md`
Defines the "People" in the company.
- Roles (Manager, Worker, Auditor)
- Permissions & Tools
- Assigned Skills
- System Prompts (Context)

### 2. 公文 (Docs) - `DOCS_SCHEMA.md`
Defines the "Objects" (Information carriers).
- Task Orders (Input)
- Work Reports (Output)
- Audit Reports (Verification)
- Protocols (JSON/Markdown schemas)

### 3. 流程 (Workflows) - `WORKFLOWS.md`
Defines the "Things" (Processes).
- PDCA Cycles (Plan-Do-Check-Act)
- Task Routing
- State Transitions

## Usage
```bash
# 运行默认公司（从 workspace/tasks 读取任务）
nanobot company run

# 指定任务文件运行
nanobot company run --task ./my_task.md

# 传入任务字符串运行
nanobot company run --task "你的任务描述"
```


---
name: "公司名称"
description: "简要描述公司的业务领域和核心职能。"
behavior:
  - "Managers dispatch tasks based on WORKFLOWS.md"
  - "Workers execute tasks using defined Skills"
  - "Auditors verify outputs against DOCS_SCHEMA.md"
default_post: "Post_Default_Worker"
default_task_template: "请执行以下任务: {task}"
components:
  posts: "./POSTS.md"
  workflows: "./WORKFLOWS.md"
  docs_schema: "./DOCS_SCHEMA.md"
  skills_dir: "./skills"
---

# 公司名称 (Company Name)

## Overview
简要描述此公司的业务领域、定位和核心运作逻辑。

## Components

### 1. 岗位 (Posts) - `POSTS.md`
定义公司内的"人"——各工作岗位。
- 角色 (Manager, Worker, Auditor)
- 工具权限 & 文件访问权限
- 所需技能
- System Prompt (上下文指令)

### 2. 公文 (Docs) - `DOCS_SCHEMA.md`
定义公司内的"物"——信息载体。
- 任务单 (Input)
- 工作报告 (Output)
- 审计报告 (Verification)

### 3. 流程 (Workflows) - `WORKFLOWS.md`
定义公司内的"事"——工作流程。
- PDCA 循环 (Plan-Do-Check-Act)
- 任务路由
- 状态流转

## Usage
```bash
# 加载公司配置
nanobot company load --name <company_name>

# 运行公司循环
nanobot company run --name <company_name>
```

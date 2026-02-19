---
name: "Company Factory"
description: "元Agent公司。根据用户需求，自动生成新的Agent公司配置文件（SKILL.md、POSTS.md、DOCS_SCHEMA.md、WORKFLOWS.md）。"
behavior:
  - "Manager 接收用户对新公司的需求描述，协调各岗位协作"
  - "需求分析师将自然语言需求转化为结构化需求规格"
  - "架构师和工程师分工设计岗位、公文、流程"
  - "审计员确保所有配置文件内部一致且符合框架规范"
default_post: "Post_Company_Architect"
default_task_template: "请根据以下需求设计一个新的Agent公司: {task}"
components:
  posts: "./POSTS.md"
  workflows: "./WORKFLOWS.md"
  docs_schema: "./DOCS_SCHEMA.md"
---

# Company Factory — 元Agent公司

## Overview
Company Factory 是一个**元公司** (Meta-Company)：它本身是一个 Agent 公司，其业务是**创建其他 Agent 公司**。

用户只需提供对新公司的自然语言需求描述（业务领域、核心职能、预期工作流等），Company Factory 就会通过内部的 PDCA 循环，自动产出一套完整的公司配置文件。

## Components

### 1. 岗位 (Posts) - `POSTS.md`
定义元公司内的五个专业岗位：
- **需求分析师**: 解析用户需求，输出需求规格书
- **公司架构师**: 设计岗位结构和 SKILL.md
- **公文规范师**: 设计 DOCS_SCHEMA.md
- **流程工程师**: 设计 WORKFLOWS.md
- **集成审计员**: 验证全部配置的一致性

### 2. 公文 (Docs) - `DOCS_SCHEMA.md`
定义元公司专用公文：
- 新公司需求规格书 (Input)
- 新公司设计方案 (Intermediate)
- 配置文件交付包 (Output)
- 集成审计报告 (Verification)

### 3. 流程 (Workflows) - `WORKFLOWS.md`
定义"创建新公司"的标准流程：
- 需求调研 → 架构设计 → 配置编写 → 集成审计 → 交付

## Usage
```bash
# 运行元公司（从 workspace/tasks 读取任务）
nanobot company run --name company_factory

# 传入新公司需求描述运行
nanobot company run --name company_factory --task "创建一个数据分析公司，要求包含数据采集、清洗和可视化岗位"

# 通过文件传入需求
nanobot company run --name company_factory --task ./new_company_requirements.md
```


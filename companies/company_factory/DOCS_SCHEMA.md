# 公文规范文档 (物/文档) — Company Factory

本文档定义了元Agent公司内所有正式"公文"的 Schema (模板)。Agent **必须**遵守这些格式。

## 1. 任务单 (`Doc_Task_Order`)
**文件命名**: `TASK_{ID}_{Title}.md`
**位置**: `workspace/tasks/`

```markdown
# TASK ORDER: {标题}
**ID**: {UUID}
**Type**: {CompanyCreation | Revision}
**Status**: {Pending | Active | Done | Archived}
**Priority**: {High | Medium | Low}

## 1. 目标 (Objective)
{用户对新公司的需求描述}

## 2. 上下文与约束 (Context & Constraints)
{业务领域、技术约束、特殊要求}

## 3. 验收标准 (Success Criteria)
- [ ] 产出完整的 SKILL.md
- [ ] 产出完整的 POSTS.md
- [ ] 产出完整的 DOCS_SCHEMA.md
- [ ] 产出完整的 WORKFLOWS.md
- [ ] 通过集成审计

## 4. 指定岗位 (Assigned Post)
Post_Manager_Factory

## 5. 输入文件 (Input Files)
- {用户需求文档路径}

## 6. 预期产出 (Expected Output)
- workspace/deliverables/{company_name}/SKILL.md
- workspace/deliverables/{company_name}/POSTS.md
- workspace/deliverables/{company_name}/DOCS_SCHEMA.md
- workspace/deliverables/{company_name}/WORKFLOWS.md
```

## 2. 新公司需求规格书 (`Doc_Company_Requirements`)
**文件命名**: `REQ_{CompanyName}.md`
**位置**: `workspace/reports/`

```markdown
# 新公司需求规格书: {公司名称}
**Author**: Post_Requirements_Analyst
**Date**: {ISO_Date}
**Task Ref**: {指向任务单的链接}

## 1. 公司概述 (Company Overview)
- **名称**: {company_name}
- **业务领域**: {领域描述}
- **核心使命**: {一句话概括}

## 2. 岗位需求 (Required Posts)
| 序号 | 角色名称 | 角色类型 | 核心职责 | 需要的工具 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | {角色名} | {Manager/Worker/Auditor} | {职责} | {工具} |

## 3. 公文需求 (Required Documents)
| 序号 | 公文类型 | 用途 | 关联岗位 |
| :--- | :--- | :--- | :--- |
| 1 | {公文名} | {用途描述} | {产出/消费该公文的岗位} |

## 4. 工作流需求 (Required Workflows)
- **主要工作流**: {名称}
  - 触发条件: {何时启动}
  - 涉及岗位: {按顺序}
  - 预期产出: {最终交付物}

## 5. 特殊约束 (Special Constraints)
{安全、隐私、性能等特殊要求}

## 6. 待确认事项 (Open Questions)
- {用户需求中不明确的部分}
```

## 3. 新公司设计方案 (`Doc_Company_Design`)
**文件命名**: `DESIGN_{CompanyName}.md`
**位置**: `workspace/reports/`

```markdown
# 新公司设计方案: {公司名称}
**Author**: Post_Company_Architect
**Date**: {ISO_Date}
**Requirements Ref**: {指向需求规格书的链接}

## 1. 架构总览 (Architecture Overview)
{公司整体架构的文字描述}

## 2. 岗位矩阵 (Post Matrix)
| 岗位 Title | 角色类型 | 工具权限 | 输入公文 | 输出公文 |
| :--- | :--- | :--- | :--- | :--- |
| Post_XXX | Worker | read_file, write_file | Doc_Task | Doc_Report |

## 3. 技能映射 (Skills Mapping)
| 岗位 | 技能 | 说明 |
| :--- | :--- | :--- |
| Post_XXX | skill-name | 技能用途 |

## 4. 权限设计 (Permission Design)
| 岗位 | 可访问路径 | 模式 | 理由 |
| :--- | :--- | :--- | :--- |
| Post_XXX | workspace/reports/ | 读写 | 需要产出报告 |

## 5. 设计决策 (Design Decisions)
- {决策 1}: {理由}
```

## 4. 工作报告 (`Doc_Work_Report`)
**文件命名**: `REPORT_{TaskID}.md`
**位置**: `workspace/reports/`

```markdown
# WORK REPORT: {TaskID}
**Author**: {Worker_ID}
**Date**: {ISO_Date}
**Task Ref**: {指向任务单的链接}

## 1. 工作摘要 (Summary of Work)
{完成了什么}

## 2. 交付物 (Deliverables)
- [文件 1](path)

## 3. 自检 (Self-Check)
- [ ] 文件格式符合模板规范?
- [ ] 所有引用的岗位/公文/流程一致?

## 4. 问题/阻碍 (Issues / Blockers)
{遇到的任何问题}
```

## 5. 集成审计报告 (`Doc_Integration_Audit`)
**文件命名**: `AUDIT_INTEGRATION_{CompanyName}.md`
**位置**: `workspace/audits/`

```markdown
# 集成审计报告: {公司名称}
**Auditor**: Post_Integration_Auditor
**Date**: {ISO_Date}
**Target**: {指向配置文件目录的链接}

## 1. 审核清单 (Audit Checklist)
| 检查项 | 状态 | 详情 |
| :--- | :--- | :--- |
| SKILL.md frontmatter 完整 | {Pass/Fail} | ... |
| POSTS.md 格式合规 | {Pass/Fail} | ... |
| DOCS_SCHEMA.md 格式合规 | {Pass/Fail} | ... |
| WORKFLOWS.md 格式合规 | {Pass/Fail} | ... |
| 角色覆盖 (Manager/Worker/Auditor) | {Pass/Fail} | ... |
| 岗位-流程一致性 | {Pass/Fail} | ... |
| 公文-岗位一致性 | {Pass/Fail} | ... |
| 权限最小化 | {Pass/Fail} | ... |
| PDCA 闭环 | {Pass/Fail} | ... |

## 2. 详细发现 (Detailed Findings)
- {发现 1}

## 3. 结论 (Verdict)
**RESULT**: {PASS | FAIL}

## 4. 建议 (Recommendations)
{修改意见或后续步骤}
```

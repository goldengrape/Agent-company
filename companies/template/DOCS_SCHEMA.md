# 公文规范文档 (物/文档) — 模板

本文档定义了公司内所有正式"公文"的 Schema (模板)。Agent **必须**遵守这些格式。

<!--
  使用说明:
  1. 每种公文类型以 ## 标题定义，格式: ## N. 标题 (`Doc_类型ID`)
  2. 文件命名使用 `{ID}`, `{Title}`, `{Date}`, `{TaskID}` 等占位符
  3. 位置指定公文存放的相对路径 (相对于 workspace)
  4. 模板使用 markdown 代码块包裹
-->

## 1. 任务单 (`Doc_Task_Order`)
**文件命名**: `TASK_{ID}_{Title}.md`
**位置**: `workspace/tasks/`

```markdown
# TASK ORDER: {标题}
**ID**: {UUID}
**Type**: {Feature | Bugfix | Doc | Research}
**Status**: {Pending | Active | Done | Archived}
**Priority**: {High | Medium | Low}

## 1. 目标 (Objective)
{清晰描述需要达成什么}

## 2. 上下文与约束 (Context & Constraints)
{相关的背景信息、文件路径、约束条件}

## 3. 验收标准 (Success Criteria)
- [ ] {标准 1}
- [ ] {标准 2}

## 4. 指定岗位 (Assigned Post)
{Post_Title}

## 5. 输入文件 (Input Files)
- {Path/to/file1}

## 6. 预期产出 (Expected Output)
- {Path/to/deliverable}
```

## 2. 工作报告 (`Doc_Work_Report`)
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
- [ ] 所有测试通过? {Yes/No}
- [ ] 文档已更新? {Yes/No}

## 4. 问题/阻碍 (Issues / Blockers)
{遇到的任何问题}
```

## 3. 审计报告 (`Doc_Audit_Report`)
**文件命名**: `AUDIT_{TaskID}.md`
**位置**: `workspace/audits/`

```markdown
# AUDIT REPORT: {TaskID}
**Auditor**: {Worker_ID}
**Date**: {ISO_Date}
**Target**: {指向工作报告的链接}

## 1. 合规性检查 (Compliance Check)
| 项目 | 状态 | 备注 |
| :--- | :--- | :--- |
| 格式 | {Pass/Fail} | ... |
| 需求 | {Pass/Fail} | ... |
| 测试 | {Pass/Fail} | ... |

## 2. 详细发现 (Detailed Findings)
- {发现 1}

## 3. 结论 (Verdict)
**RESULT**: {PASS | FAIL}

## 4. 建议 (Recommendations)
{后续步骤}
```

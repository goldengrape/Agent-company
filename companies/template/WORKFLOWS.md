# 流程管理文档 (事/工作流) — 模板

本文档定义了公司内的标准操作程序 (SOP) 和公文流转。所有工作**必须**遵循 PDCA 循环。

## 1. 核心 PDCA 循环

### 阶段 1: 计划 (Plan)
- **执行者**: Manager (或用户)
- **动作**: 创建一份 **任务单** (`Doc_Task_Order`)。
- **产出**: `workspace/tasks/` 下的 Markdown 文件。
- **内容**: 使用 `Doc_Task_Order` 规范。定义功能、上下文和验收标准。

### 阶段 2: 执行 (Do)
- **执行者**: Worker (由 Manager 指派)
- **动作**:
  1. 从 `workspace/tasks/` 领取任务。
  2. 执行工作 (代码、文档等)。
  3. 生成 **工作报告** (`Doc_Work_Report`) 和任何交付物。
- **产出**:
  - 交付物存放在 `workspace/deliverables/`
  - 报告存放在 `workspace/reports/`

### 阶段 3: 检查 (Check)
- **执行者**: 审计员 (Auditor)
- **动作**:
  1. 阅读 `Doc_Work_Report` 和交付物。
  2. 对照 `Doc_Task_Order` 的要求验证完整性。
  3. 对照 `DOCS_SCHEMA.md` 验证合规性。
- **产出**: **审计报告** (`Doc_Audit_Report`) 存放在 `workspace/audits/`。
- **状态**: `PASS` (通过) 或 `FAIL` (失败)。

### 阶段 4: 处理 (Act)
- **执行者**: Manager
- **动作**:
  - 如果 `PASS`: 归档任务单和交付物。通知用户。
  - 如果 `FAIL`: 生成 **整改单** (新的 `Doc_Task_Order`) 并引用审计报告。
- **产出**: 系统状态更新或新任务。

## 2. 标准工作流

<!--
  使用说明:
  在此处定义你公司的具体业务工作流。
  每个工作流应该是 PDCA 循环的一个具体实例化。
  包含: 触发条件、涉及岗位、文档流向。
-->

### 2.1 示例工作流: 功能实现
1. **用户/Manager** 创建 `TASK_Feature_X.md`。
2. **Manager** 生成对应岗位的 Worker。
3. **Worker** 执行任务，创建 `REPORT_Feature_X.md`。
4. **Manager** 生成 `Post_Auditor`。
5. **Auditor** 检查产出，创建 `AUDIT_Feature_X.md`。
6. **Manager** 审查审计结果。
   - 如果通过: 归档。
   - 如果失败: 创建整改任务单。

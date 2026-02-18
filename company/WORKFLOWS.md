# 流程管理文档 (事/工作流)

本文档定义了公司内的标准操作程序 (SOP) 和公文流转。所有工作**必须**遵循 PDCA 循环。

## 1. 核心 PDCA 循环

### 阶段 1: 计划 (Plan)
- **执行者**: Manager (或用户)
- **动作**: 创建一份 **任务单** (`Doc_Task_Order`)。
- **产出**: `workspace/tasks/pending/` 下的 Markdown 文件 (例如 `TASK_001_P.md`)。
- **内容**: 使用 `Doc_Task_Order` 规范。定义功能、上下文和验收标准。

### 阶段 2: 执行 (Do)
- **执行者**: Worker (由 Manager 指派)
- **动作**:
  1. 从 `workspace/tasks/pending/` 领取任务。
  2. 将任务移动到 `workspace/tasks/active/`。
  3. 执行工作 (代码、文档等)。
  4. 生成 **工作报告** (`Doc_Work_Report`) 和任何交付物。
- **产出**:
  - 交付物存放在 `workspace/deliverables/`
  - 报告存放在 `workspace/reports/` (例如 `REPORT_001_D.md`)。

### 阶段 3: 检查 (Check)
- **执行者**: 审计员 (Auditor)
- **动作**:
  1. 阅读 `Doc_Work_Report` 和交付物。
  2. 对照 `Doc_Task_Order` 的要求验证完整性。
  3. 对照 `DOCS_SCHEMA.md` 验证合规性。
- **产出**: **审计报告** (`Doc_Audit_Report`) 存放在 `workspace/audits/` (例如 `AUDIT_001_C.md`)。
- **状态**: `PASS` (通过) 或 `FAIL` (失败)。

### 阶段 4: 处理 (Act)
- **执行者**: Manager
- **动作**:
  - 如果 `PASS`: 归档任务单和交付物。通知用户。
  - 如果 `FAIL`: 生成 **整改单** (新的 `Doc_Task_Order`) 并引用审计报告。
- **产出**: 系统状态更新或新任务。

## 2. 标准工作流

### 2.1 功能实现流程
1. **用户/Manager** 创建 `Task_Feature_X.md`。
2. **Manager** 生成 `Post_Dev_Junior`。
3. **Dev** 编写代码 + 测试。创建 `Report_Feature_X.md`。
4. **Manager** 生成 `Post_Auditor`。
5. **Auditor** 检查测试是否通过及代码风格。创建 `Audit_Feature_X.md`。
6. **Manager** 审查审计结果。
   - 如果通过: 合并代码。
   - 如果失败: 创建 `Task_Fix_Feature_X.md`。

### 2.2 文档编写流程
1. **用户/Manager** 创建 `Task_Write_Docs.md`。
2. **Manager** 生成 `Post_Writer_Tech`。
3. **Writer** 编写文档。创建 `Report_Docs.md`。
4. **Manager** 生成 `Post_Auditor`。
5. **Auditor** 检查链接、语法和规范。创建 `Audit_Docs.md`。
6. **Manager** 发布或要求修改。

### 2.3 天气预报生成流程
1. **用户** 创建 `Task_Weather_Global.md` (包含目标城市列表)。
2. **Manager** 生成 `Post_Weather_Analyst`。
3. **Analyst** 查询北京、上海、San Diego 的天气。
4. **Analyst** 生成 `Report_Weather_Weekly.md`。
5. **Manager** 生成 `Post_Auditor`。
6. **Auditor** 检查是否包含所有指定城市，以及格式是否正确。
7. **Manager** 将报告发送给用户 (归档)。

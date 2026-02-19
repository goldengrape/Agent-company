# 流程管理文档 (事/工作流) — Company Factory

本文档定义了元Agent公司内的标准操作程序 (SOP) 和公文流转。所有工作**必须**遵循 PDCA 循环。

## 1. 核心 PDCA 循环

### 阶段 1: 计划 (Plan)
- **执行者**: Manager (`Post_Manager_Factory`) 或用户
- **动作**: 接收用户对新公司的需求描述，创建一份 **任务单** (`Doc_Task_Order`)。
- **产出**: `workspace/tasks/` 下的 Markdown 文件。
- **内容**: 使用 `Doc_Task_Order` 规范。明确新公司的业务领域和核心需求。

### 阶段 2: 执行 (Do)
- **执行者**: 依次由 Manager 生成的各 Worker
- **动作**: 分四个子阶段执行：
  1. **需求分析** → `Post_Requirements_Analyst`
  2. **架构设计** → `Post_Company_Architect`
  3. **公文设计** → `Post_Schema_Designer`
  4. **流程设计** → `Post_Workflow_Engineer`
- **产出**:
  - 需求规格书存放在 `workspace/reports/`
  - 配置文件存放在 `workspace/deliverables/<company_name>/`

### 阶段 3: 检查 (Check)
- **执行者**: 集成审计员 (`Post_Integration_Auditor`)
- **动作**:
  1. 读取 `workspace/deliverables/<company_name>/` 下的全部配置文件。
  2. 对照 `companies/template/` 验证格式合规性。
  3. 交叉检查岗位-公文-流程的一致性。
- **产出**: **集成审计报告** (`Doc_Integration_Audit`) 存放在 `workspace/audits/`。
- **状态**: `PASS` (通过) 或 `FAIL` (失败)。

### 阶段 4: 处理 (Act)
- **执行者**: Manager (`Post_Manager_Factory`)
- **动作**:
  - 如果 `PASS`: 将配置文件从 `workspace/deliverables/` 部署到 `companies/<company_name>/`。通知用户。
  - 如果 `FAIL`: 根据审计报告生成 **整改任务单**，引用审计发现，指派对应岗位修复。
- **产出**: 最终部署的公司配置或新的整改任务。

## 2. 标准工作流

### 2.1 新公司创建流程
这是 Company Factory 的核心工作流，将"创建新公司"分解为串行的四步。

1. **用户/Manager** 创建 `TASK_Create_<CompanyName>.md`，包含新公司的需求描述。
2. **Manager** 生成 `Post_Requirements_Analyst`。
3. **Analyst** 分析需求，产出 `REQ_<CompanyName>.md`（需求规格书）。
4. **Manager** 生成 `Post_Company_Architect`。
5. **Architect** 设计架构，产出 `SKILL.md` 和 `POSTS.md`，存放在 `workspace/deliverables/<company_name>/`。
6. **Manager** 生成 `Post_Schema_Designer`。
7. **Designer** 设计公文规范，产出 `DOCS_SCHEMA.md`，存放在 `workspace/deliverables/<company_name>/`。
8. **Manager** 生成 `Post_Workflow_Engineer`。
9. **Engineer** 设计工作流，产出 `WORKFLOWS.md`，存放在 `workspace/deliverables/<company_name>/`。
10. **Manager** 生成 `Post_Integration_Auditor`。
11. **Auditor** 审核全部配置文件，产出 `AUDIT_INTEGRATION_<CompanyName>.md`。
12. **Manager** 审查审计结果：
    - 如果通过: 部署配置文件到 `companies/<company_name>/`，归档任务。
    - 如果失败: 针对失败项创建整改任务单，指派对应 Worker 修复。

### 2.2 公司修订流程
当已有公司需要调整岗位、公文或流程时使用此工作流。

1. **用户/Manager** 创建 `TASK_Revise_<CompanyName>.md`，包含修改需求。
2. **Manager** 根据修改范围，选择性地生成对应岗位：
   - 修改岗位 → `Post_Company_Architect`
   - 修改公文 → `Post_Schema_Designer`
   - 修改流程 → `Post_Workflow_Engineer`
3. **Worker** 在现有配置基础上进行修改。
4. **Manager** 生成 `Post_Integration_Auditor` 重新审核。
5. **Manager** 根据审核结果归档或继续整改。

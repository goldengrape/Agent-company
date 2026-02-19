# 流程管理文档 (事/工作流) — Tech News Filter

本文档定义了科技新闻筛选公司内的标准操作程序 (SOP) 和公文流转。所有工作**必须**遵循 PDCA 循环。

## 1. 核心 PDCA 循环

### 阶段 1: 计划 (Plan)
- **执行者**: Manager (`Post_Manager_NewsOps`) 或定时触发器
- **动作**: 每日创建一份 **采集任务单** (`Doc_Task_Order`)。
- **产出**: `workspace/tasks/` 下的 `TASK_DailyCollect_{YYYY-MM-DD}.md`。
- **内容**: 使用 `Doc_Task_Order` 规范，指定当日RSS采集范围和时间窗口。

### 阶段 2: 执行 (Do)
- **执行者**: 依次由 Manager 生成的各 Worker
- **动作**: 分三个子阶段执行：
  1. **RSS采集与翻译** → `Post_RSS_Collector`
  2. **情报筛选** → `Post_Intelligence_Filter`
  3. **报告合成** → `Post_Report_Synthesizer`
- **产出**:
  - 原始新闻清单存放在 `workspace/raw_feeds/`
  - 筛选后清单存放在 `workspace/filtered/`
  - 每日报告存放在 `workspace/reports/`

### 阶段 3: 检查 (Check)
- **执行者**: 质量审计员 (`Post_Quality_Auditor`)
- **动作**:
  1. 读取 `workspace/reports/` 下的每日报告。
  2. 抽检过滤准确性和遗漏情况。
  3. 验证写作风格和格式合规性。
- **产出**: **质量审计报告** (`Doc_Quality_Audit`) 存放在 `workspace/audits/`。
- **状态**: `PASS` (通过) 或 `FAIL` (失败)。

### 阶段 4: 处理 (Act)
- **执行者**: Manager (`Post_Manager_NewsOps`)
- **动作**:
  - 如果 `PASS`: 归档当日报告，标记任务完成。
  - 如果 `FAIL`: 根据审计报告生成 **整改任务单**，指派对应岗位修复。
- **产出**: 最终归档的每日报告或新的整改任务。

## 2. 标准工作流

### 2.1 每日新闻筛选流程
这是 Tech News Filter 的核心工作流，每日定时触发。

1. **Manager/定时任务** 创建 `TASK_DailyCollect_{YYYY-MM-DD}.md`，包含当日采集指令。
2. **Manager** 生成 `Post_RSS_Collector`。
3. **RSS采集翻译员** 抓取所有RSS源，翻译标题和摘要，产出 `RAW_{YYYY-MM-DD}.md`。
4. **Manager** 生成 `Post_Intelligence_Filter`。
5. **首席情报筛选官** 执行 PASS/BLOCK/RESOLUTION 三层过滤，产出 `FILTERED_{YYYY-MM-DD}.md`。
6. **Manager** 生成 `Post_Report_Synthesizer`。
7. **情报合成员** 将筛选结果编译为学术化报告，产出 `REPORT_DailyBrief_{YYYY-MM-DD}.md`。
8. **Manager** 生成 `Post_Quality_Auditor`。
9. **质量审计员** 抽检报告质量，产出 `AUDIT_DailyBrief_{YYYY-MM-DD}.md`。
10. **Manager** 审查审计结果：
    - 如果通过: 归档报告，标记任务完成。
    - 如果失败: 针对失败项创建整改任务单，指派对应 Worker 修复。

### 2.2 手动补充采集流程
当用户需要对特定主题进行深度追踪时使用此工作流。

1. **用户/Manager** 创建 `TASK_DeepDive_{Topic}.md`，包含特定主题和追踪的媒体源。
2. **Manager** 生成 `Post_RSS_Collector`，限定从特定源采集特定主题。
3. **RSS采集翻译员** 采集并翻译，产出原始清单。
4. **Manager** 生成 `Post_Intelligence_Filter`，使用标准过滤逻辑。
5. **首席情报筛选官** 筛选，产出筛选清单。
6. **Manager** 生成 `Post_Report_Synthesizer`，合成为专题报告。
7. （可选）**Manager** 生成 `Post_Quality_Auditor` 进行审核。

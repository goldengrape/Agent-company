# 公文规范文档 (物/文档) — Tech News Filter

本文档定义了科技新闻筛选公司内所有正式"公文"的 Schema (模板)。Agent **必须**遵守这些格式。

## 1. 每日采集任务单 (`Doc_Task_Order`)
**文件命名**: `TASK_DailyCollect_{YYYY-MM-DD}.md`
**位置**: `workspace/tasks/`

```markdown
# TASK ORDER: 每日新闻采集 — {YYYY-MM-DD}
**ID**: {UUID}
**Type**: Research
**Status**: {Pending | Active | Done | Archived}
**Priority**: High

## 1. 目标 (Objective)
从指定RSS源采集当日最新科技新闻，翻译标题和摘要为简体中文。

## 2. 上下文与约束 (Context & Constraints)
- 数据源: TechCrunch, Wired, Nature, IEEE Spectrum, Ars Technica, The Verge, MIT Technology Review
- 时间范围: 过去24小时内发布的新闻
- 翻译要求: 专业术语保留英文原文

## 3. 验收标准 (Success Criteria)
- [ ] 所有指定RSS源均已抓取
- [ ] 标题和摘要已翻译为简体中文
- [ ] 输出文件格式符合 Doc_Raw_Feed 规范

## 4. 指定岗位 (Assigned Post)
Post_RSS_Collector

## 5. 输入文件 (Input Files)
- workspace/config/rss_sources.md (如有)

## 6. 预期产出 (Expected Output)
- workspace/raw_feeds/RAW_{YYYY-MM-DD}.md
```

## 2. 原始新闻清单 (`Doc_Raw_Feed`)
**文件命名**: `RAW_{YYYY-MM-DD}.md`
**位置**: `workspace/raw_feeds/`

```markdown
# 原始新闻清单 — {YYYY-MM-DD}
**采集时间**: {ISO_Timestamp}
**采集员**: Post_RSS_Collector
**条目总数**: {N}

---

## 条目 1
- **title_en**: {英文原标题}
- **title_zh**: {简体中文翻译标题}
- **summary_en**: {英文原摘要}
- **summary_zh**: {简体中文翻译摘要}
- **link**: {原文URL}
- **source**: {媒体名称}
- **pub_date**: {发布时间}

---
(重复以上格式)
```

## 3. 筛选后新闻清单 (`Doc_Filtered_Feed`)
**文件命名**: `FILTERED_{YYYY-MM-DD}.md`
**位置**: `workspace/filtered/`

```markdown
# 筛选后新闻清单 — {YYYY-MM-DD}
**筛选时间**: {ISO_Timestamp}
**筛选官**: Post_Intelligence_Filter
**原始条目数**: {M}
**通过条目数**: {N} (不超过20)

---

## 通过条目 1
- **title_zh**: {简体中文标题}
- **summary_zh**: {简体中文摘要}
- **link**: {原文URL}
- **source**: {媒体名称}
- **filter_result**: {PASS | PARTIAL}
- **filter_reason**: {一句话过滤理由}
- **category**: {技术架构 | 供应链 | 科学发现 | 实用工具}

---
(重复以上格式)

## 被拦截条目摘要
| # | 标题 | 来源 | 拦截原因 |
|---|------|------|----------|
| 1 | {标题} | {来源} | {BLOCK_GATE编号及简述} |
```

## 4. 每日新闻报告 (`Doc_Daily_Brief`)
**文件命名**: `REPORT_DailyBrief_{YYYY-MM-DD}.md`
**位置**: `workspace/reports/`

```markdown
# 每日科技情报 — {YYYY-MM-DD}

## 概览
本日共筛选 {N} 条情报，覆盖领域: {领域列表}。

---

### 1. {中文标题}
**来源**: {媒体名} | **时间**: {发布时间}

{2-3句摘要，冷峻学术风格，无形容词，直接呈现数据和逻辑链}

[原文链接]({URL})

---
(重复以上格式，最多20条)
```

## 5. 质量审计报告 (`Doc_Quality_Audit`)
**文件命名**: `AUDIT_DailyBrief_{YYYY-MM-DD}.md`
**位置**: `workspace/audits/`

```markdown
# 质量审计报告 — {YYYY-MM-DD}
**审计员**: Post_Quality_Auditor
**审计时间**: {ISO_Timestamp}
**审计对象**: REPORT_DailyBrief_{YYYY-MM-DD}.md

## 1. 过滤准确性抽检
| # | 条目标题 | 判定 | 是否符合PASS_GATES | 备注 |
|---|----------|------|---------------------|------|
| 1 | {标题}   | PASS | {Yes/No}            | ...  |

## 2. 遗漏检查抽检
| # | 被拦截标题 | 原判定 | 是否应被拦截 | 备注 |
|---|------------|--------|--------------|------|
| 1 | {标题}     | BLOCK  | {Yes/No}     | ...  |

## 3. 风格合规检查
- 是否存在形容词: {Yes/No}
- 是否存在公关语言: {Yes/No}
- 是否使用第三人称: {Yes/No}

## 4. 格式完整性
- 每条包含标题: {Yes/No}
- 每条包含摘要: {Yes/No}
- 每条包含原文链接: {Yes/No}
- 总条目数不超过20: {Yes/No}

## 5. 结论 (Verdict)
**RESULT**: {PASS | FAIL}

## 6. 问题与建议
{具体问题描述和改进建议}
```

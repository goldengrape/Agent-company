---
name: "Tech News Filter"
description: "科技新闻筛选公司。聚合顶级科技媒体RSS新闻源，执行底层技术情报过滤，翻译为简体中文，生成每日硬核科技新闻报告。"
behavior:
  - "采集员从RSS源抓取原始新闻数据"
  - "情报筛选官执行多层过滤逻辑，剔除噪音"
  - "情报合成员撰写学术化每日报告"
  - "审计员验证报告质量和过滤准确性"
default_post: "Post_RSS_Collector"
default_task_template: "请执行每日新闻采集与筛选任务。\n\n任务文件: {filename}\n\n任务内容:\n{content}"
components:
  posts: "./POSTS.md"
  workflows: "./WORKFLOWS.md"
  docs_schema: "./DOCS_SCHEMA.md"
---

# Tech News Filter — 科技新闻筛选公司

## Overview
Tech News Filter 是一个底层技术情报分析公司。其核心使命是从海量科技新闻中提取具有架构级、机制级价值的硬核信息，过滤一切公关噪音、政治化叙事和碎片化内容，为高密度信息消费者提供每日精炼情报。

## Components

### 1. 岗位 (Posts) - `POSTS.md`
定义公司内的四个专业岗位：
- **RSS采集翻译员**: 从指定媒体源抓取并翻译新闻
- **首席情报筛选官**: 执行核心 PASS/BLOCK 过滤逻辑
- **情报合成员**: 撰写冷峻学术化的每日报告
- **质量审计员**: 验证过滤准确性和报告质量

### 2. 公文 (Docs) - `DOCS_SCHEMA.md`
定义公司专用公文：
- 每日采集任务单 (Input)
- 原始新闻清单 (Intermediate)
- 筛选后新闻清单 (Intermediate)
- 每日新闻报告 (Output)
- 质量审计报告 (Verification)

### 3. 流程 (Workflows) - `WORKFLOWS.md`
定义"每日新闻筛选"的标准流程：
- 采集翻译 → 情报筛选 → 报告合成 → 质量审计 → 归档发布

## Usage
```bash
# 加载公司配置
nanobot company load --name tech_news_filter

# 运行每日新闻筛选
nanobot company run --name tech_news_filter
```

# Docs Index and Status

本索引用于说明 `docs/` 下文档的用途与维护状态。

## 1. 核心规范

| File | Purpose | Status |
| --- | --- | --- |
| `URD.md` | 需求定义 | Active |
| `MDD.md` | 模块设计 | Active |
| `ADD.md` | 设计映射 | Active |

## 2. 组件文档

| File | Purpose | Status |
| --- | --- | --- |
| `COMPONENTS.md` | 组件总览 | Active |
| `components/AGENT.md` | Agent 运行机制 | Active |
| `components/BUS.md` | 消息总线 | Active |
| `components/COMPANY.md` | 公司运行时 | Active |
| `components/CONFIG.md` | 配置模型 | Active |
| `components/CLI.md` | CLI 行为 | Active |
| `components/CHANNELS.md` | 渠道集成 | Active |
| `components/CRON.md` | 定时任务 | Active |
| `components/HEARTBEAT.md` | 心跳服务 | Active |
| `components/PROVIDERS.md` | Provider 体系 | Active |
| `components/SESSION.md` | 会话持久化 | Active |
| `components/SKILLS.md` | 技能加载机制 | Active |
| `components/UTILS.md` | 通用工具函数 | Active |

## 3. 指南与评审

| File | Purpose | Status |
| --- | --- | --- |
| `introduction.md` | 实现导读 | Active |
| `MANUAL_VERIFICATION.md` | 人工验证步骤 | Active |
| `CODE_REVIEW_REPORT_2026-02-24.md` | 评审报告（英文） | Active |
| `CODE_REVIEW_REPORT_2026-02-24_ZH.md` | 评审报告（中文） | Active |

## 4. 归档文档

历史阶段性文档已移动至 `docs/archive/`：
- `TRANSFORMATION_PLAN.md`
- `MANAGER_HIERARCHY_ANALYSIS.md`
- `VERIFICATION_REPORT.md`

## 5. 维护规则

1. 代码行为变更应同步更新组件文档。
2. 涉及路径、配置键名时，以代码为准并回查：
   - `nanobot/config/schema.py`
   - `nanobot/config/loader.py`
   - `nanobot/cli/company.py`
   - `nanobot/session/manager.py`
   - `nanobot/company/loader.py`
3. 阶段性分析文档完成后应归档，避免与现状混淆。

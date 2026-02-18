# Nanobot 组件目录

本文档是 `nanobot` 系统组件的高层目录。

## 核心组件 (Core Components)

### [Agent (代理核心)](components/AGENT.md)
Nanobot 代理的核心逻辑。
- **关键文件**: `loop.py`, `context.py`, `memory.py`, `subagent.py`, `worker_registry.py`
- **职责**: 负责代理循环执行、上下文管理、记忆处理及子代理（Worker）管理。

### [Company (公司管理)](components/COMPANY.md)
涉及“公司”抽象的相关组件，管理工作流和员工。
- **关键文件**: `manager.py`, `loader.py`
- **职责**: 加载公司配置，管理公司生命周期。

### [Config (配置管理)](components/CONFIG.md)
系统的配置管理模块。
- **关键文件**: `loader.py`, `schema.py`
- **职责**: 加载和验证配置文件。

## 通信与交互 (Communication & Interaction)

### [Bus (消息总线)](components/BUS.md)
用于内部通信的事件总线。
- **关键文件**: `events.py`, `queue.py`
- **职责**: 处理系统内部的事件分发和消息队列。

### [Channels (通信渠道)](nanobot/channels)
与外部通信平台的集成。
- **支持平台**: 钉钉 (DingTalk), Discord, Email, 飞书 (Feishu), 微信 (MoChat), QQ, Slack, Telegram, WhatsApp。
- **职责**: 负责从外部渠道接收消息并发送回复。

### [CLI (命令行接口)](components/CLI.md)
用于与 Nanobot 交互的命令行工具。
- **关键文件**: `commands.py`, `company.py`
- **职责**: 为用户提供控制系统的命令行指令。

## 服务与基础设施 (Services & Infrastructure)

### [Cron (定时任务)](components/CRON.md)
周期性任务的调度器。
- **关键文件**: `service.py`, `types.py`
- **职责**: 在预定时间间隔执行任务。

### [Heartbeat (心跳服务)](components/HEARTBEAT.md)
系统监控和健康检查。
- **关键文件**: `service.py`
- **职责**: 监控系统运行状态和健康状况。

### [Providers (模型供应商)](nanobot/providers)
LLM（大语言模型）供应商集成。
- **关键文件**: `litellm_provider.py`, `openai_codex_provider.py`
- **职责**: 负责与 AI 模型接口交互，进行文本和代码生成。

### [Session (会话管理)](components/SESSION.md)
用户会话管理。
- **关键文件**: `manager.py`
- **职责**: 管理用户会话状态和上下文。

## 资源 (Resources)

### [Skills (技能库)](nanobot/skills)
代理可用的能力和工具。
- **职责**: 提供具体的功能实现，如天气查询、GitHub 交互等。

### [Utils (工具集)](nanobot/utils)
通用工具函数。
- **关键文件**: `helpers.py`
- **职责**: 提供系统通用的辅助函数。

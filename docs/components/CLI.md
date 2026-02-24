# CLI 命令行接口 (CLI)

本文档对应当前实现：`nanobot/cli/commands.py` 与 `nanobot/cli/company.py`。

## 命令结构

```text
nanobot
├── onboard
├── agent
├── gateway
├── status
├── company
│   ├── init
│   └── run
├── channels
│   ├── status
│   └── login
├── cron
│   ├── list
│   ├── add
│   ├── remove
│   ├── enable
│   └── run
└── provider
    └── login
```

## 关键命令行为

### `nanobot onboard`
- 初始化配置文件（优先当前目录 `config.json`，否则 `~/.nanobot/config.json`）。
- 初始化工作区（默认 `~/.nanobot/workspace`）。
- 生成引导文件（`AGENTS.md`、`SOUL.md`、`USER.md`）和内存目录。

### `nanobot agent`
- 支持一次性消息：`-m/--message`。
- 支持交互模式（`prompt_toolkit` 历史与编辑）。
- 支持 `--session` 指定会话键（默认 `cli:direct`）。
- `--markdown/--no-markdown` 控制渲染。

### `nanobot gateway`
- 启动 Message Bus、AgentLoop、ChannelManager、CronService、HeartbeatService。
- 默认端口 `18790`。

### `nanobot company init --name <name>`
- 在 `workspace/companies/<name>/` 创建：
  - `SKILL.md`
  - `POSTS.md`
  - `WORKFLOWS.md`
  - `DOCS_SCHEMA.md`

### `nanobot company run`
- 默认扫描 `workspace/tasks/TASK_*.md`。
- 可用 `--task` 直接输入任务文本或任务文件路径。
- 可用 `--name` 或 `--path` 选择公司配置。
- 可用 `--output` 指定产出目录（会传递到 worker 指令模板）。

## 渠道与定时

### `nanobot channels status`
- 读取配置并输出各渠道启用状态。

### `nanobot channels login`
- 启动 bridge（主要用于扫码接入场景，如 WhatsApp）。

### `nanobot cron *`
- 提供 `list/add/remove/enable/run` 完整生命周期管理。

## Provider 登录

### `nanobot provider login openai-codex`
- 走 OAuth 流程，不依赖 API key 字段。

## 配置格式

当前仅使用 JSON 配置，不使用 `config.yaml`。
- 本地优先：`./config.json`
- 默认：`~/.nanobot/config.json`

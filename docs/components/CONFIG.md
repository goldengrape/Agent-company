# Config 配置管理 (Configuration)

`nanobot/config` 组件负责整个系统的配置加载、验证和管理。它基于 Pydantic 构建，确保配置数据的类型安全和完整性。

## 1. 配置文件位置

系统按以下优先级查找配置文件 `config.json`：

1.  **当前工作目录**: `./config.json`
2.  **用户主目录**: `~/.nanobot/config.json`

如果未找到配置文件，系统将使用默认配置启动。

## 2. 配置结构 (Schema)

配置主要分为以下几个部分：

### 2.1 Agents (`agents`)
定义 Agent 的默认行为。
- `workspace`: 工作区路径 (默认为 `~/.nanobot/workspace`)
- `model`: 默认使用的 LLM 模型
- `max_tokens`: 生成的最大 token 数
- `temperature`: 随机性设置
- `memory_window`: 短期记忆（上下文）保留的消息数量

### 2.2 Channels (`channels`)
配置外部通信渠道的接入。
支持的渠道包括：
- **IM**: WhatsApp, Telegram, Discord, Feishu (飞书), DingTalk (钉钉), Slack, QQ, WeChat (MoChat)
- **Email**: SMTP/IMAP 邮件收发

每个渠道通常包含 `enabled` (开关), `allow_from` (白名单), 以及各自的鉴权信息的配置（如 token, secret）。

### 2.3 Providers (`providers`)
配置 LLM 供应商。支持多供应商并存。
- **配置项**: `api_key`, `api_base`, `extra_headers`
- **支持列表**: OpenAI, Anthropic, DeepSeek, OpenRouter, Google Gemini, Azure, Local (vLLM) 等。
- **自动匹配**: 系统会根据 `model` 名称自动选择对应的 Provider 配置。

### 2.4 Tools (`tools`)
工具的全局配置。
- `web`: 搜索工具配置 (Brave Search API Key)
- `exec`: Shell 执行工具的超时设置
- `restrict_to_workspace`: 安全开关，是否限制文件操作仅在工作区内
- `mcp_servers`: Model Context Protocol (MCP) 服务器配置

## 3. 环境变量覆盖

支持使用环境变量覆盖配置，前缀为 `NANOBOT_`，使用双下划线 `__` 分隔层级。

例如：
- 覆盖默认模型: `NANOBOT_AGENTS__DEFAULTS__MODEL=gpt-4`
- 设置 OpenAI Key: `NANOBOT_PROVIDERS__OPENAI__API_KEY=sk-...`

## 4. 代码用法

### 加载配置

```python
from nanobot.config.loader import load_config

# 自动查找并加载
config = load_config()

# 访问配置
print(f"Workspace: {config.workspace_path}")
print(f"Default Model: {config.agents.defaults.model}")
```

### 获取 Provider

```python
# 获取特定模型的配置 (API Key, Base URL)
provider_config = config.get_provider("deepseek-chat")
api_key = provider_config.api_key
```

## 5. 键名转换

配置文件 (`config.json`) 使用 **camelCase** (小驼峰) 命名规范（如 `apiKey`），而 Python 代码中使用 **snake_case** (蛇形) 命名（如 `api_key`）。`loader.py` 会在加载和保存时自动处理这种转换。
